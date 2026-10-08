"""Labeled mocked model checks; all retrieval runs against real temporary SQLite."""
import json
import sqlite3
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from backend.app import hotel_chat as chat
from backend.app.main import create_app, _connect
from backend.tests.test_local_hotels import payload

FIXTURE = Path(__file__).resolve().parents[2] / 'docs/assignment-2-part-2/chat-fixture.json'


@pytest.fixture
def setup(tmp_path):
    db = tmp_path / 'chat.db'
    client = TestClient(create_app(db))
    fixture_hotel = payload('fixture-hotel', '16802')
    fixture_hotel['center'].update(locality='State College', latitude=40.8, longitude=-77.86)
    client.post('/api/local-hotels', json=fixture_hotel)
    with _connect(db) as c:
        c.execute("UPDATE saved_hotels SET name='Fixture Inn' WHERE hotel_id='fixture-hotel'")
        c.execute("UPDATE demo_hotel_nights SET nightly_rate_cents=500 WHERE stay_date='2026-10-10'")
    return db, client


def proposal(sql='SELECT hotel_id FROM hotel_stay_options WHERE available=1 ORDER BY total_cost_cents', end='2026-10-12', rooms=1):
    return chat.Proposal(sql=sql, check_in='2026-10-10', check_out=end, rooms=rooms)


def test_two_requests_and_grounded_payload(setup, monkeypatch):
    db, client = setup
    fixture = json.loads(FIXTURE.read_text())
    calls = []
    def model(system, body):
        calls.append((system, body))
        return json.dumps(fixture['proposal']) if len(calls) == 1 else fixture['answer']
    monkeypatch.setattr(chat, 'model_request', model)
    result = client.post('/api/hotel-chat', json={'question': fixture['question']})
    assert result.status_code == 200, result.text
    body = result.json()
    assert len(calls) == 2
    assert 'Actual local schema' in calls[0][0]
    assert calls[1][1]['question'] == fixture['question']
    assert calls[1][1]['records'] == body['records']
    record = body['records'][0]
    assert record['total_cost_cents'] == 10500
    assert [n['stay_date'] for n in record['nightly_records']] == ['2026-10-10', '2026-10-11']
    assert record['available'] == 1
    assert body['answer'] == fixture['answer']


def test_missing_nights_and_room_minimum(setup):
    db, _ = setup
    records, _, _ = chat.retrieve(db, proposal(end='2026-10-16', sql='SELECT hotel_id FROM hotel_stay_options'))
    assert records[0]['recorded_nights'] == 5
    assert records[0]['expected_nights'] == 6
    assert records[0]['available'] == 0
    assert records[0]['total_cost_cents'] is None
    with _connect(db) as c:
        c.execute("UPDATE demo_hotel_nights SET rooms_available=1 WHERE stay_date='2026-10-11'")
    records, _, _ = chat.retrieve(db, proposal(rooms=2, sql='SELECT hotel_id FROM hotel_stay_options'))
    assert records[0]['available'] == 0
    assert records[0]['total_cost_cents'] == 21000
    assert records[0]['minimum_rooms'] == 1


def test_no_matches_still_uses_second_request(setup, monkeypatch):
    _, client = setup
    calls = []
    def model(_system, body):
        calls.append(body)
        return json.dumps(proposal(sql="SELECT hotel_id FROM hotel_stay_options WHERE postcode='00000'").model_dump(mode='json')) if len(calls) == 1 else 'No matching local records. Simulated course data.'
    monkeypatch.setattr(chat, 'model_request', model)
    result = client.post('/api/hotel-chat', json={'question': 'Hotels in 00000 October 10 to 12, 2026?'})
    assert result.status_code == 200
    assert result.json()['records'] == []
    assert calls[1]['records'] == []


@pytest.mark.parametrize('sql', [
    'DELETE FROM saved_hotels',
    'SELECT hotel_id FROM hotel_stay_options; DELETE FROM saved_hotels',
    'SELECT content AS hotel_id FROM chat_messages',
    'SELECT email AS hotel_id FROM users',
    'SELECT name AS hotel_id FROM sqlite_master',
    "SELECT load_extension('bad') AS hotel_id",
    "SELECT * FROM pragma_table_info('users')",
    'PRAGMA query_only=OFF',
    "ATTACH DATABASE 'bad' AS bad",
    'SELECT hotel_id FROM hotel_stay_options -- bypass',
    "SELECT 'invented' AS hotel_id",
    'SELECT hotel_id FROM missing_table',
])
def test_rejected_queries_cannot_modify_or_read_private_tables(setup, sql):
    db, _ = setup
    before = db.read_bytes()
    with pytest.raises(chat.ChatError):
        chat.retrieve(db, proposal(sql=sql))
    assert db.read_bytes() == before


def test_bounded_results_and_canonical_values(setup):
    db, client = setup
    for i in range(22):
        client.post('/api/local-hotels', json=payload(f'fixture-{i}', '16802'))
    records, truncated, _ = chat.retrieve(db, proposal(sql='SELECT hotel_id, 0 AS total_cost_cents FROM hotel_stay_options ORDER BY hotel_id'))
    assert len(records) == 20
    assert truncated
    assert all(r['total_cost_cents'] == 20000 for r in records)


def test_invalid_proposal_and_dates():
    for value in ['nonsense', '{"sql":"SELECT 1"}', json.dumps(proposal().model_dump(mode='json') | {'check_out': '2026-10-10'}), json.dumps(proposal().model_dump(mode='json') | {'check_out': '2026-12-01'})]:
        with pytest.raises(chat.ChatError):
            chat.parse_proposal(value)


def test_rejected_query_stops_answer_call(setup, monkeypatch):
    _, client = setup
    model = lambda *_: json.dumps(proposal(sql='DELETE FROM saved_hotels').model_dump(mode='json'))
    monkeypatch.setattr(chat, 'model_request', model)
    assert client.post('/api/hotel-chat', json={'question': 'Delete saved hotels October 10 to 12, 2026'}).status_code == 422


@pytest.mark.parametrize('status, expected', [(429, 429), (402, 429), (401, 503), (503, 502)])
def test_mock_provider_failures(monkeypatch, status, expected):
    monkeypatch.setenv('OPEN_AI', 'fixture-secret')
    monkeypatch.setenv('OPENAI_MODEL', 'gpt-5.6-luna')
    monkeypatch.setattr(chat.httpx, 'post', lambda *a, **kw: httpx.Response(status, request=httpx.Request('POST', 'https://fixture.invalid')))
    with pytest.raises(chat.ChatError) as caught:
        chat.model_request('test', {})
    assert caught.value.status == expected
    assert 'fixture-secret' not in str(caught.value)


def test_missing_configuration(setup, monkeypatch):
    _, client = setup
    monkeypatch.delenv('OPEN_AI', raising=False)
    assert client.post('/api/hotel-chat', json={'question': 'Hotels October 10 to 12, 2026?'}).status_code == 503


def test_http_mock_exercises_both_provider_requests(setup, monkeypatch):
    _, client = setup
    fixture = json.loads(FIXTURE.read_text())
    monkeypatch.setenv('OPEN_AI', 'fixture-secret')
    monkeypatch.setenv('OPENAI_MODEL', 'gpt-5.6-luna')
    requests = []
    def post(url, **kwargs):
        requests.append(kwargs['json'])
        content = json.dumps(fixture['proposal']) if len(requests) == 1 else fixture['answer']
        return httpx.Response(200, json={'status':'completed', 'output':[{'type':'message','content':[{'type':'output_text','text':content}]}]}, request=httpx.Request('POST', url))
    monkeypatch.setattr(chat.httpx, 'post', post)
    result = client.post('/api/hotel-chat', json={'question': fixture['question']})
    assert result.status_code == 200
    assert len(requests) == 2
    assert requests[0]['instructions'] == chat.QUERY_RULES
    assert json.loads(requests[1]['input'][0]['content'])['records'][0]['total_cost_cents'] == 10500
    assert 'fixture-secret' not in result.text


def test_unknown_function_rejected(setup):
    db, _ = setup
    with pytest.raises(chat.ChatError):
        chat.retrieve(db, proposal(sql='SELECT randomblob(1000000000) AS hotel_id'))


def test_expensive_query_interrupted(setup):
    db, _ = setup
    # The single hotel's five demo dates produce one view row, so add distinct fixture IDs.
    with _connect(db) as c:
        for i in range(15):
            c.execute('INSERT INTO saved_hotels VALUES (?, NULL, NULL, 0, 0)', (f'expensive-{i}',))
            c.execute('INSERT INTO saved_hotel_zips VALUES (?, ?)', (f'expensive-{i}', '16802'))
    sql = '''SELECT a.hotel_id FROM hotel_stay_options a CROSS JOIN hotel_stay_options b
             CROSS JOIN hotel_stay_options c CROSS JOIN hotel_stay_options d
             CROSS JOIN hotel_stay_options e CROSS JOIN hotel_stay_options f
             ORDER BY length(a.hotel_id || b.hotel_id || c.hotel_id || d.hotel_id || e.hotel_id || f.hotel_id)'''
    with pytest.raises(chat.ChatError, match='too expensive'):
        chat.retrieve(db, proposal(sql=sql))


def test_preflight_outputs_no_credentials(monkeypatch):
    from backend.app import model_preflight
    monkeypatch.setenv('OPEN_AI', 'fixture-secret')
    monkeypatch.setenv('OPENAI_MODEL', 'gpt-5.6-luna')
    def get(url, **_kwargs):
        assert url == 'https://api.openai.com/v1/models/gpt-5.6-luna'
        return httpx.Response(200, json={'id':'gpt-5.6-luna'}, request=httpx.Request('GET', url))
    monkeypatch.setattr(model_preflight.httpx, 'get', get)
    result = model_preflight.check()
    assert result['accessible']
    assert 'fixture-secret' not in json.dumps(result)


def test_parameterized_join_and_history_persist_after_restart(setup, monkeypatch):
    db, client = setup
    fixture = json.loads(FIXTURE.read_text())
    calls=[]
    def model(system, body):
        calls.append(body)
        return json.dumps(fixture['proposal']) if system == chat.QUERY_RULES else fixture['answer']
    monkeypatch.setattr(chat, 'model_request', model)
    before = {}
    with _connect(db) as c:
        for table in ['saved_hotels','saved_hotel_zips','demo_hotel_nights','hotels','trips','users','bookings']:
            before[table] = list(map(tuple, c.execute(f'SELECT * FROM {table}')))
    body=client.post('/api/hotel-chat',json={'question':fixture['question']}).json()
    cid=body['conversation_id']
    restarted=TestClient(create_app(db))
    history=restarted.get(f'/api/hotel-chat/conversations/{cid}').json()
    stages=[m['stage'] for m in history['messages']]
    assert stages == ['user_message','prompt_snapshot','query_request','proposed_sql','validated_proposal','executed_sql','retrieval_result','answer_request','assistant_answer']
    assert all(m['conversation_id']==cid and m['message_id'] and m['timestamp'] and m['prompt_version'] for m in history['messages'])
    assert history['latest_result']['parameters']['postcode']=='16802'
    assert history['latest_result']['records'][0]['total_cost_cents']==10500
    assert 'JOIN saved_hotel_zips' in body['proposed_sql']
    assert 'JOIN demo_hotel_nights' in body['proposed_sql']
    assert calls[1]['records']==history['latest_result']['records']
    assert restarted.get('/api/hotel-chat/conversations').json()['conversations'][0]['conversation_id']==cid
    with _connect(db) as c:
        assert before=={t:list(map(tuple,c.execute(f'SELECT * FROM {t}'))) for t in before}


def test_follow_up_receives_previous_successful_context(setup,monkeypatch):
    _,client=setup
    fixture=json.loads(FIXTURE.read_text())
    requests=[]
    def model(system,body):
        requests.append((system,body))
        if system==chat.ANSWER_RULES: return 'MOCK answer from retrieved records.'
        values=dict(fixture['proposal'])
        if 'What about' in body['question']:
            values.update(check_in='2026-10-12',check_out='2026-10-13')
        return json.dumps(values)
    monkeypatch.setattr(chat,'model_request',model)
    first=client.post('/api/hotel-chat',json={'question':fixture['question']}).json()
    second=client.post('/api/hotel-chat',json={'question':'What about October 12?','conversation_id':first['conversation_id']}).json()
    context=requests[2][1]['history']
    assert context['previous_stay']['check_in']=='2026-10-10'
    assert [m['role'] for m in context['messages']]==['user','assistant']
    assert second['records'][0]['nightly_records'][0]['stay_date']=='2026-10-12'
    assert second['records'][0]['total_cost_cents']==10000


def test_failed_proposal_and_second_request_failures_saved(setup,monkeypatch):
    db,client=setup
    monkeypatch.setattr(chat,'model_request',lambda *_:json.dumps(proposal(sql='DELETE FROM saved_hotels').model_dump(mode='json')))
    rejected=client.post('/api/hotel-chat',json={'question':'Delete hotels October 10 to 12, 2026'}).json()
    history=client.get('/api/hotel-chat/conversations/'+rejected['conversation_id']).json()
    assert history['messages'][-1]['stage']=='error'
    assert not any(m['stage']=='assistant_answer' for m in history['messages'])
    assert history['latest_result'] is None
    with _connect(db) as c: assert c.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0]==1
    calls=[]
    def fail_answer(system,body):
        calls.append(body)
        if system==chat.QUERY_RULES: return json.dumps(proposal().model_dump(mode='json'))
        raise chat.ChatError('MOCK rate limit',429)
    monkeypatch.setattr(chat,'model_request',fail_answer)
    failed=client.post('/api/hotel-chat',json={'question':'Hotels October 10 to 12, 2026?'}).json()
    history=client.get('/api/hotel-chat/conversations/'+failed['conversation_id']).json()
    assert any(m['stage']=='retrieval_result' for m in history['messages'])
    assert history['messages'][-1]['content']=='MOCK rate limit'
    assert not any(m['stage']=='assistant_answer' for m in history['messages'])


def test_greeting_and_clarification_are_saved_without_retrieval(setup,monkeypatch):
    _,client=setup
    monkeypatch.setattr(chat,'model_request',lambda *_:json.dumps({'mode':'chat','answer':'Hello! I can compare saved hotels using simulated course data.'}))
    result=client.post('/api/hotel-chat',json={'question':'Hi'}).json()
    assert result['mode']=='chat'
    cid=result['conversation_id']
    monkeypatch.setattr(chat,'model_request',lambda *_:json.dumps({'clarification':'Which dates and ZIP should I use?'}))
    result=client.post('/api/hotel-chat',json={'question':'Find a hotel','conversation_id':cid}).json()
    assert result['mode']=='clarification'
    history=client.get('/api/hotel-chat/conversations/'+cid).json()
    assert len([m for m in history['messages'] if m['stage']=='assistant_answer'])==2
    assert not any(m['stage']=='retrieval_result' for m in history['messages'])


def test_chat_mode_cannot_bypass_hotel_retrieval(setup,monkeypatch):
    _,client=setup
    monkeypatch.setattr(chat,'model_request',lambda *_:json.dumps({'mode':'chat','answer':'Invented hotel deal'}))
    assert client.post('/api/hotel-chat',json={'question':'Which hotel is cheapest October 11, 2026?'}).status_code==422


def test_interrupted_turn_recovered_and_pending_turn_rejected(setup):
    db,client=setup
    from backend.app import chat_history
    cid,tid,_=chat_history.start_turn(db,'Hotels October 11, 2026?',None,chat.PROMPT_VERSION)
    busy=client.post('/api/hotel-chat',json={'question':'Follow up now','conversation_id':cid})
    assert busy.status_code==409
    application=create_app(db)
    with _connect(db) as c:
        assert c.execute('SELECT status FROM chat_turns WHERE turn_id=?',(tid,)).fetchone()[0]=='pending'
    with TestClient(application) as restarted:
        history=restarted.get('/api/hotel-chat/conversations/'+cid).json()
    assert history['messages'][-1]['stage']=='error'
    assert 'interrupted' in history['messages'][-1]['content']
    assert history['latest_result'] is None
    with _connect(db) as c: assert c.execute('SELECT status FROM chat_turns WHERE turn_id=?',(tid,)).fetchone()[0]=='interrupted'


def test_unknown_conversation_does_not_start_model_request(setup,monkeypatch):
    _,client=setup
    monkeypatch.setattr(chat,'model_request',lambda *_:pytest.fail('unknown conversation sent to model'))
    assert client.post('/api/hotel-chat',json={'question':'Hello','conversation_id':'00000000-0000-0000-0000-000000000000'}).status_code==404


def test_prompt_loaded_on_app_start_and_version_changes(tmp_path,monkeypatch):
    original=chat.PROMPT_FILE.read_text()
    custom=tmp_path/'hotel-assistant.md';custom.write_text(original+'\nTest version.\n')
    old_version=chat.PROMPT_VERSION
    monkeypatch.setattr(chat,'PROMPT_FILE',custom)
    create_app(tmp_path/'prompt.db')
    assert chat.PROMPT_VERSION!=old_version
    assert 'Test version.' in chat.ANSWER_RULES


def test_cheapest_three_excludes_missing_and_unavailable_nights(setup):
    db,client=setup
    for name,rate in [('cheap',2000),('expensive',15000),('unavailable',100),('missing',100),('middle',7000)]:
        client.post('/api/local-hotels',json=payload(name,'16802'))
        with _connect(db) as c:
            c.execute('UPDATE demo_hotel_nights SET nightly_rate_cents=? WHERE hotel_id=?',(rate,name))
    with _connect(db) as c:
        c.execute("UPDATE demo_hotel_nights SET rooms_available=0 WHERE hotel_id='unavailable' AND stay_date='2026-10-11'")
        c.execute("DELETE FROM demo_hotel_nights WHERE hotel_id='missing' AND stay_date='2026-10-11'")
    fixture=json.loads(FIXTURE.read_text())
    fixture['proposal']['parameters'].update(check_in='2026-10-13',check_out='2026-10-14',nights=1,rooms=20)
    records,_,_=chat.retrieve(db,chat.parse_proposal(json.dumps(fixture['proposal'])))
    assert [r['hotel_id'] for r in records]==['cheap','fixture-hotel','middle']
    assert [r['total_cost_cents'] for r in records]==[4000,10500,14000]
    assert all(r['expected_nights']==2 and r['rooms_requested']==1 and r['available']==1 for r in records)


def test_responses_parser_ignores_reasoning_and_rejects_incomplete_output(monkeypatch):
    monkeypatch.setenv('OPEN_AI','fixture-secret')
    payload={'status':'completed','output':[{'type':'reasoning','summary':[]},
        {'type':'message','content':[{'type':'output_text','text':'Supported reply.'}]}]}
    def post(url,**kwargs):
        assert url=='https://api.openai.com/v1/responses'
        assert kwargs['json']['store'] is False
        assert kwargs['json']['input'][0]['content']=='{"question": "Hi"}'
        return httpx.Response(200,json=payload,request=httpx.Request('POST',url))
    monkeypatch.setattr(chat.httpx,'post',post)
    assert chat.model_request('fixture prompt',{'question':'Hi'})=='Supported reply.'
    payload['status']='incomplete'
    with pytest.raises(chat.ChatError):chat.model_request('fixture prompt',{'question':'Hi'})


def test_empty_inventory_reported_to_answer_model(tmp_path, monkeypatch):
    db = tmp_path / 'empty.db'
    client = TestClient(create_app(db))
    calls = []
    def model(system, body):
        calls.append(body)
        return proposal().model_dump_json() if len(calls) == 1 else 'No hotels saved; use Add to Local.'
    monkeypatch.setattr(chat, 'model_request', model)
    response = client.post('/api/hotel-chat', json={'question': 'Hotels October 10 to 12, 2026?'})
    assert response.status_code == 200
    assert response.json()['saved_hotel_count'] == 0
    assert calls[1]['saved_hotel_count'] == 0
    assert calls[1]['records'] == []
    with _connect(db) as c:
        assert c.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0] == 0
