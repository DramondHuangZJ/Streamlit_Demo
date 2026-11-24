"""Transactional local SQLite storage; no questionnaire or personal identifiers."""
import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .content import GAMES, APP_VERSION, PROTOCOL_VERSION, pages, score_answers

ORDERS=(('dragon_castle','azul'),('azul','dragon_castle'))
TABLES=('participants','assignments','page_timings','trial_responses','comprehension_responses','game_sessions','survey_handoffs','events')

def now(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def seconds(start,end=None): return max(0,(datetime.fromisoformat((end or now()).replace('Z','+00:00'))-datetime.fromisoformat(start.replace('Z','+00:00'))).total_seconds())
def digest(token): return hashlib.sha256(token.encode()).hexdigest()
class StaleStep(ValueError): pass

class Store:
    def __init__(self,path):
        self.path=Path(path).expanduser().resolve(); self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
            CREATE TABLE IF NOT EXISTS participants(
              participant_id TEXT PRIMARY KEY, resume_hash TEXT UNIQUE NOT NULL,
              started_at TEXT NOT NULL, completed_at TEXT, status TEXT NOT NULL,
              is_test INTEGER NOT NULL, language TEXT NOT NULL, page_index INTEGER NOT NULL,
              page_entered_at TEXT NOT NULL, app_version TEXT NOT NULL, protocol_version TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS assignments(
              participant_id TEXT PRIMARY KEY REFERENCES participants(participant_id),
              order_code TEXT NOT NULL, first_game TEXT NOT NULL, second_game TEXT NOT NULL,
              assigned_at TEXT NOT NULL, algorithm TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS page_timings(
              participant_id TEXT REFERENCES participants(participant_id), page_id TEXT,
              entered_at TEXT NOT NULL, exited_at TEXT NOT NULL, duration_seconds REAL NOT NULL,
              PRIMARY KEY(participant_id,page_id));
            CREATE TABLE IF NOT EXISTS trial_responses(
              participant_id TEXT REFERENCES participants(participant_id), game_id TEXT,
              item_code TEXT, response TEXT NOT NULL, correct INTEGER NOT NULL,
              rule_ref TEXT NOT NULL, recorded_at TEXT NOT NULL,
              PRIMARY KEY(participant_id,game_id,item_code));
            CREATE TABLE IF NOT EXISTS comprehension_responses(
              participant_id TEXT REFERENCES participants(participant_id), game_id TEXT,
              item_code TEXT, response TEXT NOT NULL, correct INTEGER NOT NULL,
              rule_ref TEXT NOT NULL, recorded_at TEXT NOT NULL,
              PRIMARY KEY(participant_id,game_id,item_code));
            CREATE TABLE IF NOT EXISTS game_sessions(
              participant_id TEXT REFERENCES participants(participant_id), game_id TEXT,
              game_position INTEGER NOT NULL, stimulus_version TEXT NOT NULL,
              rules_version TEXT NOT NULL, quiz_accuracy REAL, trial_accuracy REAL,
              PRIMARY KEY(participant_id,game_id));
            CREATE TABLE IF NOT EXISTS survey_handoffs(
              participant_id TEXT REFERENCES participants(participant_id), game_id TEXT,
              generated_at TEXT NOT NULL, returned_at TEXT, confirmation_method TEXT,
              configured INTEGER NOT NULL, PRIMARY KEY(participant_id,game_id));
            CREATE TABLE IF NOT EXISTS events(
              event_id INTEGER PRIMARY KEY AUTOINCREMENT,
              participant_id TEXT REFERENCES participants(participant_id),
              event_type TEXT NOT NULL, recorded_at TEXT NOT NULL, details TEXT NOT NULL);
            ''')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=30,isolation_level=None); db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON'); db.execute('PRAGMA busy_timeout=30000')
        try: yield db
        finally: db.close()
    @contextmanager
    def transaction(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try: yield db; db.execute('COMMIT')
            except Exception: db.execute('ROLLBACK'); raise
    def start(self,language='en',is_test=True,forced_order=None):
        if language not in ('en','zh'): raise ValueError('Unknown language.')
        if forced_order is not None and not is_test: raise ValueError('Forced order is only allowed for test records.')
        if forced_order is not None and tuple(forced_order) not in ORDERS: raise ValueError('Invalid order.')
        token=secrets.token_urlsafe(32); pid='P-'+secrets.token_hex(8); stamp=now()
        with self.transaction() as db:
            counts={r['order_code']:r['n'] for r in db.execute('SELECT a.order_code,COUNT(*) n FROM assignments a JOIN participants p USING(participant_id) WHERE p.is_test=? GROUP BY a.order_code',(int(is_test),))}
            choices=[o for o in ORDERS if counts.get('>'.join(o),0)==min(counts.get('>'.join(x),0) for x in ORDERS)]
            order=tuple(forced_order) if forced_order else secrets.choice(choices)
            db.execute('INSERT INTO participants VALUES(?,?,?,NULL,?,?,?,?,?,?,?)',(pid,digest(token),stamp,'in_progress',int(is_test),language,0,stamp,APP_VERSION,PROTOCOL_VERSION))
            db.execute('INSERT INTO assignments VALUES(?,?,?,?,?,?)',(pid,'>'.join(order),*order,stamp,'balanced-random-tie-v1' if forced_order is None else 'test-forced'))
            for i,g in enumerate(order,1):
                db.execute('INSERT INTO game_sessions VALUES(?,?,?,?,?,NULL,NULL)',(pid,g,i,GAMES[g]['stimulus_version'],GAMES[g]['rules_version']))
            db.execute('INSERT INTO events(participant_id,event_type,recorded_at,details) VALUES(?,?,?,?)',(pid,'start',stamp,json.dumps({'screening':'external_platform','test':is_test})))
        return pid,token
    def participant(self,pid):
        with self.connect() as db:
            row=db.execute('SELECT p.*,a.first_game,a.second_game,a.order_code FROM participants p JOIN assignments a USING(participant_id) WHERE participant_id=?',(pid,)).fetchone()
            return dict(row) if row else None
    def resume(self,token):
        if not token or len(token)>200: return None
        with self.connect() as db:
            row=db.execute('SELECT participant_id FROM participants WHERE resume_hash=?',(digest(token),)).fetchone()
            return self.participant(row[0]) if row else None
    def stage(self,p): return pages((p['first_game'],p['second_game']))[p['page_index']]
    def prepare_handoff(self,pid,game,configured):
        p=self.participant(pid)
        if p is None or self.stage(p)!=f'handoff:{game}' or p['status']!='in_progress': raise StaleStep('Not on the questionnaire handoff.')
        with self.transaction() as db:
            db.execute('INSERT OR IGNORE INTO survey_handoffs VALUES(?,?,?,NULL,NULL,?)',(pid,game,now(),int(configured)))
    def advance(self,pid,expected,answers=None):
        answers=answers or {}; stamp=now()
        with self.transaction() as db:
            row=db.execute('SELECT p.*,a.first_game,a.second_game FROM participants p JOIN assignments a USING(participant_id) WHERE participant_id=?',(pid,)).fetchone()
            if not row: raise ValueError('Unknown participant.')
            p=dict(row); order=(p['first_game'],p['second_game']); stage=pages(order)[p['page_index']]
            if p['status']!='in_progress' or stage!=expected: raise StaleStep('This step was already saved. Refresh to continue.')
            kind,_,game=stage.partition(':')
            if kind in ('trial','quiz'):
                scores=score_answers(game,'trials' if kind=='trial' else 'quiz',answers)
                table='trial_responses' if kind=='trial' else 'comprehension_responses'
                for code,response,correct,ref in scores:
                    db.execute(f'INSERT INTO {table} VALUES(?,?,?,?,?,?,?)',(pid,game,code,response,correct,ref,stamp))
                column='trial_accuracy' if kind=='trial' else 'quiz_accuracy'
                db.execute(f'UPDATE game_sessions SET {column}=? WHERE participant_id=? AND game_id=?',(sum(x[2] for x in scores)/len(scores),pid,game))
            elif kind=='handoff':
                handoff=db.execute('SELECT * FROM survey_handoffs WHERE participant_id=? AND game_id=?',(pid,game)).fetchone()
                if not handoff: raise ValueError('Generate the questionnaire handoff first.')
                method='participant_reported' if handoff['configured'] else 'preview_no_survey'
                if not handoff['configured'] and not p['is_test']: raise ValueError('Real sessions require a configured questionnaire.')
                db.execute('UPDATE survey_handoffs SET returned_at=?,confirmation_method=? WHERE participant_id=? AND game_id=?',(stamp,method,pid,game))
            elif stage=='filler':
                if seconds(p['page_entered_at'],stamp)<90: raise ValueError('Please complete the 90-second break.')
                if set(answers)!={'FILL1','FILL2','FILL3'} or any(str(v) not in ('3','4','5','6') for v in answers.values()): raise ValueError('Respond to all three shape-count activities.')
                db.execute('INSERT INTO events(participant_id,event_type,recorded_at,details) VALUES(?,?,?,?)',(pid,'filler',stamp,json.dumps(answers)))
            elif stage=='finish':
                for table,expected_n in [('trial_responses',6),('comprehension_responses',10)]:
                    if db.execute(f'SELECT COUNT(*) FROM {table} WHERE participant_id=?',(pid,)).fetchone()[0]!=expected_n: raise ValueError('Both games must be completed first.')
                if db.execute('SELECT COUNT(*) FROM survey_handoffs WHERE participant_id=? AND returned_at IS NOT NULL',(pid,)).fetchone()[0]!=2: raise ValueError('Both handoffs must be completed first.')
                db.execute("UPDATE participants SET status='completed',completed_at=? WHERE participant_id=?",(stamp,pid))
            db.execute('INSERT INTO page_timings VALUES(?,?,?,?,?)',(pid,stage,p['page_entered_at'],stamp,seconds(p['page_entered_at'],stamp)))
            db.execute('UPDATE participants SET page_index=page_index+1,page_entered_at=? WHERE participant_id=?',(stamp,pid))
    def withdraw(self,pid):
        with self.transaction() as db:
            row=db.execute('SELECT status FROM participants WHERE participant_id=?',(pid,)).fetchone()
            if not row or row[0]!='in_progress': raise ValueError('Only unfinished sessions can be withdrawn here.')
            for table in TABLES[1:]: db.execute(f'DELETE FROM {table} WHERE participant_id=?',(pid,))
            # Retain only an anonymous administrative withdrawal count.
            db.execute("UPDATE participants SET status='withdrawn',resume_hash=?,language='',completed_at=NULL WHERE participant_id=?",(digest(secrets.token_urlsafe(32)),pid))
    def rows(self,table,include_tests=False,completed_only=False):
        if table not in TABLES: raise ValueError('Unknown table.')
        where=[]; params=[]
        if not include_tests: where.append('p.is_test=0')
        if completed_only: where.append("p.status='completed'")
        sql=f'SELECT t.* FROM {table} t JOIN participants p ON p.participant_id=t.participant_id' if table!='participants' else 'SELECT p.* FROM participants p'
        if where: sql+=' WHERE '+' AND '.join(where)
        with self.connect() as db:
            result=[dict(r) for r in db.execute(sql,params)]
        # Resume credentials never leave the storage boundary.
        for r in result: r.pop('resume_hash',None)
        return result
