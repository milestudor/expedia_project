"""Additive, repeatable migrations for local API hotel storage."""

import sqlite3


def migrate_saved_hotels(connection: sqlite3.Connection) -> None:
    """Create empty storage tables; caller supplies a foreign-key-enabled connection.

    API hotels[].place_id maps verbatim to hotel_id. name, address, latitude,
    and longitude map directly to their namesakes. No provider prices exist;
    the daily defaults below are fictional classroom data.
    """
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise RuntimeError("Saved hotel migration requires foreign keys enabled")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS saved_hotels (
            hotel_id TEXT NOT NULL PRIMARY KEY,
            name TEXT,
            address TEXT,
            latitude REAL NOT NULL CHECK (
                typeof(latitude) IN ('integer', 'real') AND latitude BETWEEN -90 AND 90
            ),
            longitude REAL NOT NULL CHECK (
                typeof(longitude) IN ('integer', 'real') AND longitude BETWEEN -180 AND 180
            )
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS demo_hotel_nights (
            hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
            stay_date TEXT NOT NULL CHECK (
                stay_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                AND substr(stay_date, 1, 4) BETWEEN '0001' AND '9999'
                AND date(stay_date, '+0 days') IS NOT NULL
                AND date(stay_date, '+0 days') = stay_date
            ),
            nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK (
                typeof(nightly_rate_cents) = 'integer' AND nightly_rate_cents >= 0
            ),
            rooms_available INTEGER NOT NULL DEFAULT 20 CHECK (
                typeof(rooms_available) = 'integer' AND rooms_available >= 0
            ),
            PRIMARY KEY (hotel_id, stay_date)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS saved_zip_contexts (
            postcode TEXT NOT NULL PRIMARY KEY CHECK (
                postcode GLOB '[0-9][0-9][0-9][0-9][0-9]'
            ),
            country_code TEXT NOT NULL CHECK (country_code = 'us'),
            latitude REAL NOT NULL CHECK (latitude BETWEEN -90 AND 90),
            longitude REAL NOT NULL CHECK (longitude BETWEEN -180 AND 180),
            locality TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS saved_hotel_zips (
            hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
            postcode TEXT NOT NULL REFERENCES saved_zip_contexts(postcode),
            PRIMARY KEY (hotel_id, postcode)
        )
    """)


def migrate_chat_history(connection: sqlite3.Connection) -> None:
    """Add chat-only storage; never modify original or saved-hotel tables."""
    connection.execute('''CREATE TABLE IF NOT EXISTS chat_conversations (
        conversation_id TEXT PRIMARY KEY, title TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS chat_turns (
        turn_id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES chat_conversations(conversation_id),
        timestamp TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','succeeded','failed','interrupted')),
        prompt_version TEXT NOT NULL, result_json TEXT)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        sequence INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT UNIQUE NOT NULL,
        conversation_id TEXT NOT NULL REFERENCES chat_conversations(conversation_id),
        turn_id TEXT NOT NULL REFERENCES chat_turns(turn_id), timestamp TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('system','user','assistant','tool')),
        stage TEXT NOT NULL, content TEXT NOT NULL, prompt_version TEXT NOT NULL)''')
    connection.execute('CREATE INDEX IF NOT EXISTS chat_messages_conversation ON chat_messages(conversation_id, sequence)')
    connection.execute('CREATE INDEX IF NOT EXISTS chat_turns_conversation ON chat_turns(conversation_id, timestamp)')
