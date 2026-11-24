from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from pilot.storage import Store,ORDERS
from pilot.content import GAMES
from test_protocol import age_filler
APP=Path(__file__).resolve().parents[1]/'app.py'

@pytest.mark.parametrize('order,language',[(ORDERS[0],'English'),(ORDERS[1],'简体中文')])
def test_complete_bilingual_sessions_and_reruns(tmp_path,monkeypatch,order,language):
    db=tmp_path/'app.sqlite3';monkeypatch.setenv('PILOT_DB_PATH',str(db));monkeypatch.setenv('PILOT_MODE','preview');monkeypatch.setenv('PILOT_TEST_ORDER',','.join(order))
    a=AppTest.from_file(str(APP)).run()
    a.radio[0].set_value(language).run();a.button[0].click().run()
    assert not a.exception
    store=Store(db);pid=a.session_state['participant_id'];token=a.session_state['resume_token']
    a.run();assert a.session_state['participant_id']==pid
    assert (store.participant(pid)['first_game'],store.participant(pid)['second_game'])==order
    visited=[]
    for _ in range(20):
        assert not a.exception
        p=store.participant(pid);stage=store.stage(p);visited.append(stage)
        if stage=='complete':break
        kind,_,gid=stage.partition(':')
        if kind in ('trial','quiz'):
            qs=GAMES[gid]['trials' if kind=='trial' else 'quiz']
            # First try a missing required response, which must not advance.
            a.button[0].click().run();assert store.stage(store.participant(pid))==stage
            for q in qs: a.radio(key=q['code']).set_value(q['answer'])
        elif stage=='filler':
            age_filler(store,pid)
            for code,value in [('FILL1','4'),('FILL2','3'),('FILL3','5')]:a.radio(key=code).set_value(value)
            a.run()
        a.button[0].click().run()
    assert visited[-1]=='complete'
    assert store.participant(pid)['status']=='completed'
    assert len(store.rows('comprehension_responses',True))==10
    assert all(r['correct']==1 for r in store.rows('comprehension_responses',True))
    # A new Streamlit session resumes from the opaque capability after browser refresh.
    b=AppTest.from_file(str(APP));b.query_params['resume']=token;b.run()
    assert not b.exception and b.session_state['participant_id']==pid
    assert 'complete'==store.stage(store.participant(pid))

def test_missing_asset_has_readable_fallback(tmp_path,monkeypatch):
    monkeypatch.setenv('PILOT_DB_PATH',str(tmp_path/'missing.sqlite3'));monkeypatch.setenv('PILOT_TEST_ORDER',','.join(ORDERS[0]))
    monkeypatch.setitem(GAMES['dragon_castle'],'hero_asset','not-present.svg')
    a=AppTest.from_file(str(APP)).run();a.radio[0].set_value('English').run();a.button[0].click().run()
    assert not a.exception and any('Illustration unavailable' in x.value for x in a.info)

def test_admin_is_protected(tmp_path,monkeypatch):
    monkeypatch.setenv('PILOT_DB_PATH',str(tmp_path/'admin.sqlite3'));monkeypatch.setenv('PILOT_ADMIN_PASSWORD','test-only-password')
    a=AppTest.from_file(str(APP));a.query_params['researcher']='1';a.run()
    assert not a.exception and not a.metric
    a.text_input[0].set_value('wrong');a.button[0].click().run()
    assert a.error and not a.metric
    a.text_input[0].set_value('test-only-password');a.button[0].click().run()
    assert not a.exception and a.metric
