"""Two-call SQL RAG service. Models never receive database access or credentials."""
import hashlib
import math
import json
import os
import re
import sqlite3
from datetime import date
from uuid import UUID
from pathlib import Path
from time import monotonic

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from . import chat_history
from .config import get_openai_key, get_openai_model


class ChatError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status
        self.conversation_id = None


class ChatQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=1500)
    conversation_id: UUID | None = None


class Proposal(BaseModel):
    model_config = ConfigDict(extra='forbid')
    sql: str = Field(min_length=1, max_length=4000)
    check_in: date
    check_out: date
    rooms: int = Field(ge=1, le=20)
    parameters: dict = Field(default_factory=dict, max_length=10)


MODEL_SOURCE = 'live-model'
PROMPT_FILE = Path(__file__).resolve().parents[2] / 'prompts' / 'hotel-assistant.md'


def load_assistant_prompt():
    global QUERY_RULES, ANSWER_RULES, PROMPT_VERSION
    text = PROMPT_FILE.read_text(encoding='utf-8')
    common, rest = text.split('## Query stage', 1)
    query, answer = rest.split('## Answer stage', 1)
    if not all(part.strip() for part in (common, query, answer)):
        raise RuntimeError('Hotel assistant prompt needs purpose, query, and answer sections.')
    QUERY_RULES = common + '\nQuery stage\n' + query
    ANSWER_RULES = common + '\nAnswer stage\n' + answer
    PROMPT_VERSION = hashlib.sha256(text.encode()).hexdigest()


load_assistant_prompt()


def model_request(system, payload):
    key, model = get_openai_key(), get_openai_model()
    if not key:
        raise ChatError('OpenAI is not configured. Add OPEN_AI privately to the backend .env and restart.', 503)
    try:
        response = httpx.post('https://api.openai.com/v1/responses',
            headers={'Authorization': f'Bearer {key}'},
            json={'model': model, 'instructions': system,
                'input': [{'role': 'user', 'content': json.dumps(payload)}],
                'service_tier': 'default', 'reasoning': {'effort': 'medium'},
                'text': {'format': {'type': 'text'}, 'verbosity': 'medium'},
                'max_output_tokens': 4000, 'store': False}, timeout=60)
        if response.status_code in (402, 429):
            raise ChatError('Model quota or rate limit reached. Check API credit or wait before retrying.', 429)
        if response.status_code in (401, 403):
            raise ChatError('Model credentials were rejected. Check backend configuration.', 503)
        response.raise_for_status()
        body = response.json()
        if body.get('status') != 'completed':
            raise ValueError('incomplete or failed response')
        content = ''.join(part['text'] for item in body.get('output', [])
            if item.get('type') == 'message' for part in item.get('content', [])
            if part.get('type') == 'output_text')
        if not content.strip() or len(content) > 20000:
            raise ValueError('empty or oversized content')
        return content.strip()
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise ChatError('OpenAI request failed or returned an invalid response. Please try again later.') from None


def parse_proposal(content):
    try:
        # Accept a single JSON fence, but never execute reasoning or surrounding prose.
        if content.startswith('```json\n') and content.endswith('\n```'):
            content = content[8:-4]
        values = json.loads(content)
        if isinstance(values, dict) and ('clarification' in values or values.get('mode') == 'chat'):
            return values
        proposal = Proposal.model_validate(values)
        nights = (proposal.check_out - proposal.check_in).days
        if not 1 <= nights <= 30:
            raise ChatError('Choose a stay between 1 and 30 nights.', 422)
        for name, value in proposal.parameters.items():
            if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,40}', name):
                raise ValueError('invalid parameter name')
            if value is not None and type(value) not in (str, int, float):
                raise ValueError('invalid parameter value')
            if isinstance(value, str) and len(value) > 200:
                raise ValueError('oversized parameter')
            if isinstance(value, (int, float)) and (not math.isfinite(value) or abs(value) > 10**12):
                raise ValueError('invalid numeric parameter')
        return proposal
    except (ValueError, ValidationError):
        raise ChatError('Model returned an invalid query proposal; nothing was executed.') from None


def retrieve(database: Path, proposal: Proposal):
    nights = (proposal.check_out - proposal.check_in).days
    if not 1 <= nights <= 30:
        raise ChatError('Choose a stay between 1 and 30 nights.', 422)
    sql = proposal.sql.strip()
    if not re.match(r'^SELECT\s', sql, re.I) or any(s in sql for s in (';', '--', '/*', '\x00')):
        raise ChatError('Proposed query rejected: only one allowed SELECT is permitted.', 422)
    # Read-only URI provides a second boundary even if SQL validation has a defect.
    connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    nights = (proposal.check_out - proposal.check_in).days
    try:
        connection.execute('BEGIN')  # Consistent snapshot across selection and nightly evidence.
        connection.execute(f'''CREATE TEMP VIEW hotel_stay_options AS
            SELECT h.hotel_id, h.name, h.address, z.postcode, c.locality,
                COUNT(n.stay_date) AS recorded_nights, {nights} AS expected_nights,
                CASE WHEN COUNT(n.stay_date)={nights}
                     THEN SUM(n.nightly_rate_cents)*{proposal.rooms} END AS total_cost_cents,
                MIN(n.rooms_available) AS minimum_rooms,
                CASE WHEN COUNT(n.stay_date)={nights} AND MIN(n.rooms_available)>={proposal.rooms}
                     THEN 1 ELSE 0 END AS available
            FROM saved_hotels h JOIN saved_hotel_zips z ON z.hotel_id=h.hotel_id
            JOIN saved_zip_contexts c ON c.postcode=z.postcode
            LEFT JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id
                AND n.stay_date>='{proposal.check_in.isoformat()}'
                AND n.stay_date<'{proposal.check_out.isoformat()}'
            GROUP BY h.hotel_id, z.postcode''')
        connection.execute('PRAGMA query_only=ON')
        functions = {'count', 'sum', 'min', 'max', 'lower', 'upper', 'like', 'coalesce', 'round', 'abs', 'length'}
        tables = {'saved_hotels', 'saved_hotel_zips', 'saved_zip_contexts', 'demo_hotel_nights'}

        def authorize(action, arg1, arg2, _db, source):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and (arg1 == 'hotel_stay_options' or arg1 in tables):
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and arg2 in functions:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        deadline = monotonic() + 2
        steps = 0

        def progress():
            nonlocal steps
            steps += 1
            return int(steps > 2000 or monotonic() > deadline)

        connection.set_progress_handler(progress, 1000)
        connection.set_authorizer(authorize)
        executed_sql = f'SELECT DISTINCT hotel_id FROM ({sql}) LIMIT 21'
        try:
            parameters = proposal.parameters | {'check_in': proposal.check_in.isoformat(),
                'check_out': proposal.check_out.isoformat(), 'nights': nights, 'rooms': proposal.rooms}
            selected = connection.execute(executed_sql, parameters).fetchall()
        except sqlite3.Error:
            raise ChatError('Proposed query rejected: invalid, disallowed, or too expensive. No records changed.', 422) from None
        finally:
            connection.set_authorizer(None)
        records = []
        for row in selected[:20]:
            # Canonical totals and nights replace any arithmetic or fabricated columns from the model.
            details = connection.execute('SELECT * FROM hotel_stay_options WHERE hotel_id=? ORDER BY postcode',
                                         (row['hotel_id'],)).fetchall()
            if not details:
                raise ChatError('Proposed query returned an unknown hotel ID; answer generation stopped.', 422)
            preferred = proposal.parameters.get('postcode')
            record = dict(next((r for r in details if r['postcode'] == preferred), details[0]))
            record['postcodes'] = [r['postcode'] for r in details]
            record['check_in'] = proposal.check_in.isoformat()
            record['check_out'] = proposal.check_out.isoformat()
            record['rooms_requested'] = proposal.rooms
            record['simulated_course_data'] = True
            record['nightly_records'] = [dict(n) for n in connection.execute('''SELECT stay_date,
                nightly_rate_cents, rooms_available FROM demo_hotel_nights
                WHERE hotel_id=? AND stay_date>=? AND stay_date<? ORDER BY stay_date''',
                (row['hotel_id'], record['check_in'], record['check_out']))]
            records.append(record)
        return records, len(selected) > 20, executed_sql
    finally:
        connection.close()


def answer_question(database, question, conversation_id=None):
    cid, tid, context = chat_history.start_turn(database, question, conversation_id, PROMPT_VERSION)
    def record(role, stage, content):
        chat_history.append(database, cid, tid, role, stage, content, PROMPT_VERSION)
    try:
        record('system', 'prompt_snapshot', {'version': PROMPT_VERSION, 'query_prompt': QUERY_RULES,
            'answer_prompt': ANSWER_RULES, 'model': get_openai_model()})
        query_input = {'question': question, 'history': context}
        record('tool', 'query_request', query_input)
        raw = model_request(QUERY_RULES, query_input)
        record('assistant', 'proposed_sql', raw)
        proposal = parse_proposal(raw)
        if isinstance(proposal, dict):
            if 'clarification' in proposal:
                answer = proposal['clarification']
                mode = 'clarification'
            else:
                if not re.fullmatch(r'\s*(hi|hello|hey|thanks|thank you|help|what can you do)[!?.\s]*', question, re.I):
                    raise ChatError('A hotel question requires checked retrieval; an unsupported direct answer was rejected.', 422)
                answer = proposal.get('answer')
                mode = 'chat'
            if not isinstance(answer, str) or not 1 <= len(answer) <= 1000:
                raise ChatError('Invalid model clarification or greeting.', 502)
            result = {'mode': mode, 'question': question, 'answer': answer, 'records': [],
                      'stay': None, 'model': get_openai_model(), 'source': MODEL_SOURCE}
        else:
            record('tool', 'validated_proposal', proposal.model_dump(mode='json'))
            records, truncated, executed_sql = retrieve(database, proposal)
            parameters = proposal.parameters | {'check_in': proposal.check_in.isoformat(),
                'check_out': proposal.check_out.isoformat(), 'nights': (proposal.check_out-proposal.check_in).days,
                'rooms': proposal.rooms}
            record('tool', 'executed_sql', {'sql': executed_sql, 'parameters': parameters})
            record('tool', 'retrieval_result', {'records': records, 'truncated': truncated})
            with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as inventory:
                saved_hotel_count = inventory.execute('SELECT COUNT(*) FROM saved_hotels').fetchone()[0]
            answer_input = {'question': question, 'history': context, 'records': records,
                'saved_hotel_count': saved_hotel_count,
                'truncated': truncated, 'check_in': proposal.check_in.isoformat(),
                'check_out': proposal.check_out.isoformat(), 'rooms_requested': proposal.rooms}
            record('tool', 'answer_request', {'instructions': ANSWER_RULES, 'payload': answer_input})
            answer = model_request(ANSWER_RULES, answer_input)
            result = {'mode': 'rag', 'question': question, 'proposed_sql': proposal.sql,
                'executed_sql': executed_sql, 'parameters': parameters,
                'stay': {'check_in': proposal.check_in.isoformat(), 'check_out': proposal.check_out.isoformat(),
                         'rooms': proposal.rooms}, 'records': records, 'truncated': truncated,
                'answer': answer, 'model': get_openai_model(), 'source': MODEL_SOURCE,
                'saved_hotel_count': saved_hotel_count}
        result.update(conversation_id=cid, turn_id=tid, prompt_version=PROMPT_VERSION, simulated_course_data=True)
        chat_history.finish_turn(database, cid, tid, result=result, prompt_version=PROMPT_VERSION)
        return result
    except ChatError as error:
        chat_history.finish_turn(database, cid, tid, error=error, prompt_version=PROMPT_VERSION)
        error.conversation_id = cid
        raise
    except sqlite3.Error:
        error = ChatError('Local chat storage or retrieval is unavailable. No successful answer was completed.', 503)
        error.conversation_id = cid
        try:
            chat_history.finish_turn(database, cid, tid, error=error, prompt_version=PROMPT_VERSION)
        except sqlite3.Error:
            pass
        raise error from None
