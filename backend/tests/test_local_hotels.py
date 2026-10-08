import sqlite3

import pytest
from fastapi.testclient import TestClient
from backend.app.main import create_app, _connect


def payload(id=' Exact/Provider?ID ', zip='02108'):
    return {'hotel': {'place_id': id, 'name': None, 'address': None, 'latitude': 42.3, 'longitude': -71.1},
            'center': {'postcode': zip, 'country_code': 'us', 'latitude': 42.36, 'longitude': -71.06, 'locality': 'Boston'}}


@pytest.fixture
def setup(tmp_path):
    db = tmp_path / 'local.db'
    return db, TestClient(create_app(db))


def test_save_repeat_edit_restart_and_remove(setup):
    db, client = setup
    with _connect(db) as c:
        old = {t: list(map(tuple, c.execute(f'SELECT * FROM {t}'))) for t in ['hotels','trips','users','bookings','id_sequences']}
    assert client.get('/api/local-hotels?postcode=02108').json()['hotels'] == []
    assert client.post('/api/local-hotels', json=payload()).status_code == 200
    with _connect(db) as c:
        c.execute('UPDATE demo_hotel_nights SET nightly_rate_cents=500, rooms_available=10 WHERE stay_date=?', ('2026-10-10',))
    client.post('/api/local-hotels', json=payload())
    client.post('/api/local-hotels', json=payload(zip='02109'))
    client.post('/api/local-hotels', json=payload('unrelated'))
    restarted = TestClient(create_app(db))
    body = restarted.get('/api/local-hotels?postcode=02109').json()
    assert body['center'] == payload(zip='02109')['center']
    hotel = body['hotels'][0]
    assert hotel['place_id'] == payload()['hotel']['place_id']
    assert len(hotel['demo_nights']) == 5
    assert [n['stay_date'] for n in hotel['demo_nights']] == [f'2026-10-{d}' for d in range(10,15)]
    assert hotel['demo_nights'][0]['nightly_rate_cents'] == 500
    assert hotel['demo_nights'][0]['rooms_available'] == 10
    assert hotel['demo_nights'][1]['nightly_rate_cents'] == 10000
    assert hotel['demo_nights'][1]['rooms_available'] == 20
    assert restarted.post('/api/local-hotels/status', json={'place_ids':[hotel['place_id'], 'absent']}).json() == {'saved_ids':[hotel['place_id']]}
    assert restarted.delete('/api/local-hotels', params={'hotel_id':hotel['place_id']}).status_code == 204
    assert restarted.get('/api/local-hotels?postcode=02109').json()['hotels'] == []
    assert len(restarted.get('/api/local-hotels?postcode=02108').json()['hotels']) == 1
    with _connect(db) as c:
        assert not c.execute('SELECT 1 FROM demo_hotel_nights WHERE hotel_id=?',(hotel['place_id'],)).fetchall()
        assert not c.execute('SELECT 1 FROM saved_hotel_zips WHERE hotel_id=?',(hotel['place_id'],)).fetchall()
        assert not c.execute('PRAGMA foreign_key_check').fetchall()
        assert old == {t: list(map(tuple, c.execute(f'SELECT * FROM {t}'))) for t in old}


def test_failed_delete_rolls_back_all_related_rows(setup):
    db, client = setup
    client.post('/api/local-hotels', json=payload('id'))
    with _connect(db) as c:
        c.execute("CREATE TRIGGER fail_delete BEFORE DELETE ON saved_hotels BEGIN SELECT RAISE(ABORT, 'test'); END")
    assert client.delete('/api/local-hotels', params={'hotel_id':'id'}).status_code == 503
    with _connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM demo_hotel_nights').fetchone()[0] == 5
        assert c.execute('SELECT COUNT(*) FROM saved_hotel_zips').fetchone()[0] == 1
        assert c.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0] == 1


def test_failed_save_rolls_back_and_read_failure_is_not_empty(setup):
    db, client = setup
    with _connect(db) as c:
        c.execute("CREATE TRIGGER fail_night BEFORE INSERT ON demo_hotel_nights BEGIN SELECT RAISE(ABORT, 'test'); END")
    assert client.post('/api/local-hotels', json=payload()).status_code == 503
    with _connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0] == 0
        assert c.execute('SELECT COUNT(*) FROM saved_hotel_zips').fetchone()[0] == 0
        c.execute('DROP TABLE saved_hotel_zips')
    assert client.get('/api/local-hotels?postcode=02108').status_code == 503


@pytest.mark.parametrize('key,value', [('place_id',''), ('latitude',91), ('longitude',-181)])
def test_invalid_hotel_rejected(setup,key,value):
    _, client = setup
    body=payload();body['hotel'][key]=value
    assert client.post('/api/local-hotels',json=body).status_code == 422


def test_invalid_zip_and_country_rejected(setup):
    _, client = setup
    assert client.get('/api/local-hotels?postcode=1234').status_code == 422
    body=payload();body['center']['country_code']='ca'
    assert client.post('/api/local-hotels',json=body).status_code == 422
