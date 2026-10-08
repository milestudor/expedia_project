import sqlite3

import pytest

from backend.app.main import _connect, initialize_database
from backend.app.migrations import migrate_saved_hotels


@pytest.fixture
def connection(tmp_path):
    database = tmp_path / 'fresh.db'
    initialize_database(database)
    connection = _connect(database)
    yield connection
    connection.close()


def test_repeatable_migration_preserves_existing_database(connection):
    tables = ['hotels', 'trips', 'users', 'bookings', 'id_sequences']
    before = {t: [tuple(r) for r in connection.execute(f'SELECT * FROM {t}')] for t in tables}
    # Emulate the pre-migration database, then upgrade it twice.
    connection.execute('DROP TABLE demo_hotel_nights')
    connection.execute('DROP TABLE saved_hotels')
    migrate_saved_hotels(connection)
    provider_id = '  00AbC-provider-ID  '
    connection.execute('INSERT INTO saved_hotels VALUES (?, NULL, NULL, 90, -180)', (provider_id,))
    connection.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)',
                       (provider_id, '2026-10-10'))
    migrate_saved_hotels(connection)
    assert tuple(connection.execute('SELECT * FROM saved_hotels').fetchone()) == (provider_id, None, None, 90, -180)
    assert tuple(connection.execute('SELECT * FROM demo_hotel_nights').fetchone()) == (provider_id, '2026-10-10', 10000, 20)
    assert before == {t: [tuple(r) for r in connection.execute(f'SELECT * FROM {t}')] for t in tables}
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute('INSERT INTO saved_hotels VALUES (?, NULL, NULL, 0, 0)', (provider_id,))
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)',
                           (provider_id, '2026-10-10'))


@pytest.mark.parametrize('latitude,longitude', [(None, 0), (0, None), (91, 0), (0, -181),
                                               ('bad', 0), (0, 'bad'), (float('inf'), 0)])
def test_invalid_coordinates_rejected(connection, latitude, longitude):
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute('INSERT INTO saved_hotels VALUES (?, NULL, NULL, ?, ?)', ('id', latitude, longitude))


@pytest.mark.parametrize('stay_date', ['2026-2-01', '2026-02-29', '2026-04-31', '2026-13-01',
                                      '2026-00-01', '2026-01-00', '0000-01-01', 'bad', None,
                                      '2026-10-10T00:00:00'])
def test_invalid_dates_rejected(connection, stay_date):
    connection.execute("INSERT INTO saved_hotels VALUES ('id', NULL, NULL, 0, 0)")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)', ('id', stay_date))


@pytest.mark.parametrize('rate,rooms', [(-1, 20), (10000, -1), (1.5, 20), (10000, 1.5),
                                       ('bad', 20), (10000, 'bad'), (None, 20), (10000, None)])
def test_invalid_daily_values_rejected(connection, rate, rooms):
    connection.execute("INSERT INTO saved_hotels VALUES ('id', NULL, NULL, 0, 0)")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute('INSERT INTO demo_hotel_nights VALUES (?, ?, ?, ?)', ('id', '2026-10-10', rate, rooms))


def test_foreign_key_and_valid_nights(connection):
    assert connection.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES ('missing', '2026-10-10')")
    connection.execute("INSERT INTO saved_hotels VALUES ('id', NULL, NULL, -90, 180)")
    connection.execute("INSERT INTO demo_hotel_nights VALUES ('id', '2028-02-29', 0, 0)")
    connection.execute("INSERT INTO demo_hotel_nights VALUES ('id', '2028-03-01', 12345, 3)")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("DELETE FROM saved_hotels WHERE hotel_id='id'")
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()


def test_migration_requires_foreign_keys():
    with sqlite3.connect(':memory:') as connection:
        with pytest.raises(RuntimeError, match='foreign keys'):
            migrate_saved_hotels(connection)
