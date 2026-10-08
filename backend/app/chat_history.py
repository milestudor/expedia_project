"""Application-owned conversation writes, separate from model SQL retrieval."""
import json
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class HistoryError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.status = status


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def _connect(database: Path):
    c = sqlite3.connect(database, timeout=5)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


@contextmanager
def connect(database):
    c = _connect(database)
    try:
        with c:
            yield c
    finally:
        c.close()


def append(database, conversation_id, turn_id, role, stage, content, prompt_version):
    if not isinstance(content, str):
        content = json.dumps(content)
    with connect(database) as c:
        c.execute('''INSERT INTO chat_messages
            (message_id, conversation_id, turn_id, timestamp, role, stage, content, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (str(uuid4()), conversation_id, turn_id, timestamp(), role, stage, content, prompt_version))


def start_turn(database, question, conversation_id, prompt_version):
    cid = conversation_id or str(uuid4())
    tid = str(uuid4())
    c = _connect(database)
    try:
        c.execute('BEGIN IMMEDIATE')
        row = c.execute('SELECT * FROM chat_conversations WHERE conversation_id=?', (cid,)).fetchone()
        if conversation_id and row is None:
            raise HistoryError('Conversation not found. Start a new conversation.', 404)
        if row and c.execute("SELECT 1 FROM chat_turns WHERE conversation_id=? AND status='pending'", (cid,)).fetchone():
            raise HistoryError('This conversation already has a request in progress.', 409)
        now = timestamp()
        if row is None:
            c.execute('INSERT INTO chat_conversations VALUES (?, ?, ?, ?)', (cid, question[:120], now, now))
        else:
            c.execute('UPDATE chat_conversations SET updated_at=? WHERE conversation_id=?', (now, cid))
        c.execute('INSERT INTO chat_turns VALUES (?, ?, ?, ?, ?, NULL)', (tid, cid, now, 'pending', prompt_version))
        c.execute('''INSERT INTO chat_messages
            (message_id, conversation_id, turn_id, timestamp, role, stage, content, prompt_version)
            VALUES (?, ?, ?, ?, 'user', 'user_message', ?, ?)''',
            (str(uuid4()), cid, tid, now, question, prompt_version))
        c.commit()
        # Only successful previous exchanges inform follow-ups; failed attempts remain in the trace.
        history = [dict(r) for r in c.execute('''SELECT m.role, m.content FROM chat_messages m
            JOIN chat_turns t ON t.turn_id=m.turn_id WHERE m.conversation_id=?
            AND t.status='succeeded' AND m.stage IN ('user_message', 'assistant_answer')
            ORDER BY m.sequence DESC LIMIT 12''', (cid,))][::-1]
        latest = c.execute('''SELECT result_json FROM chat_turns WHERE conversation_id=? AND
            status='succeeded' AND result_json IS NOT NULL ORDER BY timestamp DESC LIMIT 1''', (cid,)).fetchone()
        previous = json.loads(latest[0]) if latest else None
        context = {'messages': [r | {'content': r['content'][:2000]} for r in history], 'previous_stay': previous.get('stay') if previous else None,
                   'previous_question': previous.get('question') if previous else None}
        return cid, tid, context
    finally:
        c.close()


def finish_turn(database, conversation_id, turn_id, result=None, error=None, prompt_version=''):
    with connect(database) as c:
        now = timestamp()
        role, stage = ('tool', 'error') if error else ('assistant', 'assistant_answer')
        content = str(error) if error else result['answer']
        c.execute('''INSERT INTO chat_messages
            (message_id, conversation_id, turn_id, timestamp, role, stage, content, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (str(uuid4()), conversation_id, turn_id, now, role, stage, content, prompt_version))
        c.execute('UPDATE chat_turns SET status=?, result_json=? WHERE turn_id=?',
                  ('failed' if error else 'succeeded', json.dumps(result) if result else None, turn_id))
        c.execute('UPDATE chat_conversations SET updated_at=? WHERE conversation_id=?', (now, conversation_id))


def recover_pending(connection):
    """At backend startup, retain unfinished traces and identify interrupted turns."""
    rows = connection.execute("SELECT * FROM chat_turns WHERE status='pending'").fetchall()
    for row in rows:
        connection.execute('''INSERT INTO chat_messages
            (message_id, conversation_id, turn_id, timestamp, role, stage, content, prompt_version)
            VALUES (?, ?, ?, ?, 'tool', 'error', ?, ?)''',
            (str(uuid4()), row['conversation_id'], row['turn_id'], timestamp(),
             'Request interrupted by backend restart. No successful answer was completed.', row['prompt_version']))
        connection.execute("UPDATE chat_turns SET status='interrupted' WHERE turn_id=?", (row['turn_id'],))


def list_conversations(database):
    with connect(database) as c:
        return [dict(r) for r in c.execute('''SELECT * FROM chat_conversations
            ORDER BY updated_at DESC LIMIT 20''')]


def load_conversation(database, conversation_id):
    with connect(database) as c:
        conversation = c.execute('SELECT * FROM chat_conversations WHERE conversation_id=?', (conversation_id,)).fetchone()
        if conversation is None:
            raise HistoryError('Conversation not found.', 404)
        rows = [dict(r) for r in c.execute('''SELECT * FROM chat_messages WHERE conversation_id=?
            ORDER BY sequence DESC LIMIT 201''', (conversation_id,))]
        latest = c.execute('''SELECT result_json FROM chat_turns WHERE conversation_id=?
            ORDER BY timestamp DESC LIMIT 1''', (conversation_id,)).fetchone()
        return {'conversation': dict(conversation), 'messages': rows[:200][::-1],
                'truncated': len(rows) > 200,
                'latest_result': json.loads(latest[0]) if latest and latest[0] else None}
