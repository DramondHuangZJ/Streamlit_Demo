from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import io,json,zipfile
import pandas as pd
import pytest
from pilot.storage import Store,ORDERS,StaleStep
from pilot.content import GAMES,pages,score_answers,questionnaire_url
from pilot.analysis import export_zip,report,merge_external
from pilot.settings import collection_blockers

@pytest.fixture
def store(tmp_path): return Store(tmp_path/'study.sqlite3')
def age_filler(store,pid):
    with store.transaction() as db:
        db.execute('UPDATE participants SET page_entered_at=? WHERE participant_id=?',((datetime.now(timezone.utc)-timedelta(seconds=91)).isoformat(),pid))
def complete(store,order=ORDERS[0],is_test=True):
    pid,token=store.start('en',is_test,order if is_test else None)
    for stage in pages((store.participant(pid)['first_game'],store.participant(pid)['second_game']))[:-1]:
        kind,_,gid=stage.partition(':');answers=None
        if kind in ('quiz','trial'): answers={q['code']:q['answer'] for q in GAMES[gid]['quiz' if kind=='quiz' else 'trials']}
        if kind=='handoff': store.prepare_handoff(pid,gid,True)
        if kind=='filler': age_filler(store,pid);answers={'FILL1':'4','FILL2':'3','FILL3':'5'}
        store.advance(pid,stage,answers)
    return pid,token

def test_assignment_balanced_concurrent_and_stable(store):
    with ThreadPoolExecutor(max_workers=4) as ex: sessions=list(ex.map(lambda _:store.start(),range(20)))
    orders=[store.participant(pid)['order_code'] for pid,_ in sessions]
    assert orders.count('dragon_castle>azul')==orders.count('azul>dragon_castle')==10
    for pid,token in sessions:
        p=Store(store.path).resume(token)
        assert p['participant_id']==pid and p['page_index']==0
        assert p['order_code']==store.participant(pid)['order_code']
    assert store.resume('not-a-token') is None
    with pytest.raises(ValueError): store.start(is_test=False,forced_order=ORDERS[0])

@pytest.mark.parametrize('order',ORDERS)
def test_full_protocol_finalization_and_export(store,order):
    pid,token=complete(store,order)
    assert store.participant(pid)['status']=='completed'
    assert len(store.rows('page_timings',True))==12
    assert len(store.rows('trial_responses',True))==6
    assert len(store.rows('comprehension_responses',True))==10
    assert all(r['correct']==1 for r in store.rows('comprehension_responses',True))
    with pytest.raises(StaleStep): store.advance(pid,'finish')
    assert len(store.rows('page_timings',True))==12
    assert not store.rows('participants') # tests are excluded by default
    z=zipfile.ZipFile(io.BytesIO(export_zip(store,True)))
    p=pd.read_csv(z.open('participants.csv'));q=pd.read_csv(z.open('comprehension_responses.csv'))
    assert len(p)==1 and len(q)==10 and q.correct.sum()==10
    assert 'resume_hash' not in p.columns and token.encode() not in z.read('participants.csv')
    assert not report(store)['participants_started']
    assert report(store,True)['participants_started']==1

def test_validation_is_atomic_and_no_answer_changes_after_save(store):
    pid,_=store.start(forced_order=ORDERS[0])
    store.advance(pid,'product:dragon_castle');store.advance(pid,'learn:dragon_castle')
    for invalid in ({},{'D_T1':'0'},{'D_T1':'9','D_T2':'1','D_T3':'2'}):
        with pytest.raises(ValueError):store.advance(pid,'trial:dragon_castle',invalid)
    assert not store.rows('trial_responses',True)
    wrong={q['code']:next(o['id'] for o in q['options'] if o['id']!=q['answer']) for q in GAMES['dragon_castle']['trials']}
    store.advance(pid,'trial:dragon_castle',wrong)
    assert sum(r['correct'] for r in store.rows('trial_responses',True))==0
    with pytest.raises(StaleStep):store.advance(pid,'trial:dragon_castle',wrong)
    assert len(store.rows('trial_responses',True))==3

def test_filler_is_enforced_by_server(store):
    pid,_=store.start(forced_order=ORDERS[0])
    for s in pages(ORDERS[0])[:5]:
        k,_,g=s.partition(':')
        if k=='handoff':store.prepare_handoff(pid,g,False)
        answers={q['code']:q['answer'] for q in GAMES[g]['trials' if k=='trial' else 'quiz']} if k in ('trial','quiz') else None
        store.advance(pid,s,answers)
    with pytest.raises(ValueError):store.advance(pid,'filler',{'FILL1':'4','FILL2':'3','FILL3':'5'})
    age_filler(store,pid)
    with pytest.raises(ValueError):store.advance(pid,'filler',{'FILL1':'4'})
    store.advance(pid,'filler',{'FILL1':'4','FILL2':'3','FILL3':'5'})
    assert store.stage(store.participant(pid))=='product:azul'

def test_withdrawal_deletes_answers_and_invalidates_resume(store):
    pid,token=store.start();stage=store.stage(store.participant(pid));store.advance(pid,stage)
    store.withdraw(pid)
    assert store.resume(token) is None
    assert store.rows('participants',True)[0]['status']=='withdrawn'
    for table in ['assignments','page_timings','game_sessions','events']:assert not store.rows(table,True)

def test_collection_record_cannot_bypass_missing_questionnaire(store):
    pid,_=store.start(is_test=False)
    with store.transaction() as db:db.execute('UPDATE participants SET page_index=4 WHERE participant_id=?',(pid,))
    gid=store.participant(pid)['first_game'];store.prepare_handoff(pid,gid,False)
    with pytest.raises(ValueError):store.advance(pid,'handoff:'+gid)

def test_link_contract_and_reserved_parameter_integrity():
    url=questionnaire_url('https://survey.example/entry?participant_id=spoof&custom=yes','P-1','azul',2,ORDERS[0],'zh','https://site.example/?resume=abc')
    from urllib.parse import urlsplit,parse_qs
    q=parse_qs(urlsplit(url).query)
    assert q['participant_id']==['P-1'] and q['custom']==['yes']
    assert q['return_url']==['https://site.example/?resume=abc']
    for bad in ['http://survey.example','javascript:alert(1)','https://user:pass@example.com']:
        with pytest.raises(ValueError):questionnaire_url(bad,'P','azul',1,ORDERS[0],'en','https://site.example')

def test_collection_requires_review_and_durable_storage():
    assert collection_blockers({'PILOT_MODE':'collection'})
    assert not collection_blockers({'PILOT_MODE':'preview'})

def test_external_merge_reversal_missing_items_and_validation(store,tmp_path):
    pid,_=complete(store)
    rows=[]
    for g in GAMES:
        rows.append(dict(participant_id=pid,game_id=g,CF1=7,CF2=7,CF3=1,CF4=1,CF5=1,CF6=1,PRICE1=1))
    p=tmp_path/'external.csv';pd.DataFrame(rows).to_csv(p,index=False)
    m=merge_external(store,p,True)
    assert list(m.CF_score)==[7,7] and list(m.PRICE_score)==[7,7]
    rows[0]['CF6']=None;pd.DataFrame(rows).to_csv(p,index=False)
    assert merge_external(store,p,True).CF_score.isna().sum()==1
    rows[0]['CF6']=8;pd.DataFrame(rows).to_csv(p,index=False)
    with pytest.raises(ValueError):merge_external(store,p,True)
    pd.DataFrame([rows[1],rows[1]]).to_csv(p,index=False)
    with pytest.raises(ValueError):merge_external(store,p,True)

def test_export_keeps_empty_headers_and_excludes_tests(store):
    z=zipfile.ZipFile(io.BytesIO(export_zip(store)))
    assert pd.read_csv(z.open('comprehension_responses.csv')).empty
    assert 'item_code' in pd.read_csv(z.open('comprehension_responses.csv')).columns
    assert json.loads(z.read('manifest.json'))['includes_tests'] is False

def test_material_change_cannot_silently_mix_versions(store):
    pid,_=store.start()
    assert store.materials_match(pid)
    with store.transaction() as db: db.execute("UPDATE game_sessions SET stimulus_version='obsolete' WHERE participant_id=?",(pid,))
    assert not store.materials_match(pid)

def test_questionnaire_version_recorded_on_handoff(store):
    pid,_=store.start()
    with store.transaction() as db:db.execute('UPDATE participants SET page_index=4 WHERE participant_id=?',(pid,))
    game=store.participant(pid)['first_game'];store.prepare_handoff(pid,game,True,'external-pilot-v3')
    assert store.rows('survey_handoffs',True)[0]['questionnaire_version']=='external-pilot-v3'

def test_external_descriptive_report(store,tmp_path):
    from pilot.analysis import external_report
    pid,_=complete(store)
    p=tmp_path/'ratings.csv'
    rows=[dict(participant_id=pid,game_id=g,PCD1=3,PCD2=4,PCD3=5,PCD4=4,PCD5=4,culture_recognition='china' if g=='dragon_castle' else 'portugal',prior_exposure='no') for g in GAMES]
    pd.DataFrame(rows).to_csv(p,index=False)
    r=external_report(store,p,True)
    assert all(x['accuracy']==1 for x in r['recognition'])
    assert r['paired_diagnostics'][0]['n_pairs']==1
    assert r['paired_diagnostics'][0]['ci95_low'] is None
    assert r['scales']['PCD'][0]['mean']==4
    json.dumps(r,allow_nan=False)
