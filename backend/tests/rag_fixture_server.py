"""MOCK MODEL server: isolated SQLite, no provider calls. Never a production fallback.

Run with --database /private/tmp/expedia-rag-browser.db for restart checks.
"""
import argparse
import json
import tempfile
from pathlib import Path

import uvicorn
from backend.app import main, hotel_chat
from backend.tests.test_local_hotels import payload
from fastapi.testclient import TestClient

FIXTURE = json.loads((Path(__file__).resolve().parents[2] /
    'docs/assignment-2-part-2/chat-fixture.json').read_text())


def mocked_model(system, body):
    if system == hotel_chat.QUERY_RULES:
        question = body['question']
        if question.lower().strip() in ('hi', 'hello'):
            return json.dumps({'mode':'chat', 'answer':'MOCK MODEL: Hello! I can compare saved hotels using simulated course data.'})
        values = dict(FIXTURE['proposal'])
        values['parameters'] = dict(values['parameters'])
        if '00000' in question:
            values['parameters']['postcode'] = '00000'
        elif '16803' in question or ('What about' in question and '16803' in (body.get('history', {}).get('previous_question') or '')):
            values['parameters']['postcode'] = '16803'
        if 'What about October 12' in question:
            values.update(check_in='2026-10-12',check_out='2026-10-13')
        elif 'night of October 11' in question:
            values.update(check_in='2026-10-11',check_out='2026-10-12')
        if '250' not in question and '250' not in (body.get('history', {}).get('previous_question') or ''):
            values['sql'] = values['sql'].replace(' AND SUM(n.nightly_rate_cents)*:rooms<:budget', '')
            values['parameters'].pop('budget', None)
        if 'delete' in question.lower():
            values['sql'] = 'DELETE FROM saved_hotels'
        return json.dumps(values)
    if not body['records']:
        return 'MOCK MODEL: No matching local records were retrieved. Rates and availability are simulated course data.'
    record = body['records'][0]
    if record['check_in']=='2026-10-10' and record['check_out']=='2026-10-12':
        return 'MOCK MODEL DEMONSTRATION\n' + FIXTURE['answer']
    return (f"MOCK MODEL: {record['name']} has {record['recorded_nights']}/{record['expected_nights']} nights recorded "
            f"for {record['check_in']} to {record['check_out']} (checkout excluded). "
            f"Total ${(record['total_cost_cents'] or 0)/100:.2f} for {record['rooms_requested']} room(s). "
            'Rates and rooms are simulated course data.')


def fixture_app(database):
    hotel_chat.model_request = mocked_model
    hotel_chat.MODEL_SOURCE = 'MOCK MODEL — fixed fixtures, real isolated SQLite retrieval'
    hotel_chat.get_openai_model = lambda: 'fixture; no remote model'
    app = main.create_app(database)
    client = TestClient(app)
    for postcode in ['16802','16803']:
        fixture_hotel = payload('fixture-hotel', postcode)
        fixture_hotel['center'].update(locality='State College', latitude=40.8, longitude=-77.86)
        client.post('/api/local-hotels', json=fixture_hotel)
    with main._connect(database) as c:
        c.execute("UPDATE saved_hotels SET name='Fixture Inn' WHERE hotel_id='fixture-hotel'")
        c.execute("UPDATE demo_hotel_nights SET nightly_rate_cents=500 WHERE stay_date='2026-10-10'")
    return app


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--database', type=Path)
    args=parser.parse_args()
    if args.database and args.database.resolve()==main.DEFAULT_DATABASE.resolve():
        parser.error('Fixture server cannot use the normal project database.')
    with tempfile.TemporaryDirectory(prefix='expedia-rag-fixture-') as folder:
        db=args.database or Path(folder)/'fixture.db'
        print('MOCK MODEL SERVER: isolated database, fixture proposals/answers, no live provider.')
        uvicorn.run(fixture_app(db), host='127.0.0.1', port=8001)
