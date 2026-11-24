"""Descriptive task diagnostics and analysis-ready exports, never hypothesis tests."""
import csv
import io
import json
import zipfile
from datetime import datetime, timezone
import pandas as pd
from scipy.stats import t
from .storage import TABLES,seconds
from .content import GAMES,APP_VERSION

def frame(store,table,include_tests=False,completed_only=False):
    rows=store.rows(table,include_tests,completed_only)
    with store.connect() as db: cols=[r[1] for r in db.execute(f'PRAGMA table_info({table})') if r[1]!='resume_hash']
    return pd.DataFrame(rows,columns=cols)

def csv_bytes(df): return df.to_csv(index=False,lineterminator='\n').encode('utf-8-sig')

def paired_diagnostic(sessions,column,bound):
    if sessions.empty: return dict(measure=column,n_pairs=0,mean_azul_minus_dragon=None,ci95_low=None,ci95_high=None,proposed_bound=bound)
    wide=sessions.pivot(index='participant_id',columns='game_id',values=column)
    if not {'azul','dragon_castle'}.issubset(wide.columns): return paired_diagnostic(pd.DataFrame(),column,bound)
    dif=(wide.azul-wide.dragon_castle).dropna(); n=len(dif); mean=float(dif.mean()) if n else None
    margin=float(t.ppf(.975,n-1)*dif.std(ddof=1)/(n**.5)) if n>=2 else None
    return dict(measure=column,n_pairs=n,mean_azul_minus_dragon=mean,ci95_low=mean-margin if margin is not None else None,ci95_high=mean+margin if margin is not None else None,proposed_bound=bound)

def report(store,include_tests=False):
    p=frame(store,'participants',include_tests); a=frame(store,'assignments',include_tests)
    g=frame(store,'game_sessions',include_tests,True); q=frame(store,'comprehension_responses',include_tests,True)
    statuses=p.status.value_counts().to_dict() if not p.empty else {}
    durations=[seconds(r.started_at,r.completed_at) for r in p.itertuples() if r.status=='completed']
    missing=[]
    for r in p.itertuples():
        if r.status=='withdrawn': continue
        for game in GAMES:
            for table,expected in [('trial_responses',3),('comprehension_responses',5)]:
                rows=store.rows(table,include_tests)
                n=sum(x['participant_id']==r.participant_id and x['game_id']==game for x in rows)
                if n<expected: missing.append(dict(participant_id=r.participant_id,status=r.status,game_id=game,table=table,missing_items=expected-n))
    return dict(label='Stimulus-validation, comprehension and website-usability diagnostics',app_version=APP_VERSION,includes_tests=include_tests,
       participants_started=len(p),status_counts=statuses,order_counts=a.order_code.value_counts().to_dict() if not a.empty else {},
       mean_completion_seconds=sum(durations)/len(durations) if durations else None,
       timing_note='Elapsed time includes external questionnaires and inactive tabs.',
       quiz_by_game=q.groupby('game_id').correct.agg(['count','mean']).reset_index().to_dict('records') if not q.empty else [],
       quiz_by_item=q.groupby(['game_id','item_code']).correct.agg(['count','mean']).reset_index().to_dict('records') if not q.empty else [],
       missing=missing,paired_diagnostics=[paired_diagnostic(g,x,.10) for x in ['quiz_accuracy','trial_accuracy']],
       bounds_note='±0.10 accuracy is a proposed absolute difference bound requiring prerecruitment approval. A non-significant difference never establishes equivalence.',
       external_note='Culture recognition, prior exposure, ratings, background and usability answers are collected externally and are not present in website records. Survey return is participant-reported, not independently verified.')

def export_zip(store,include_tests=False,completed_only=True):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for table in TABLES: z.writestr(table+'.csv',csv_bytes(frame(store,table,include_tests,completed_only)))
        z.writestr('manifest.json',json.dumps(dict(generated_at=datetime.now(timezone.utc).isoformat(),app_version=APP_VERSION,includes_tests=include_tests,completed_only=completed_only,join_keys=['participant_id','game_id'],excluded_fields=['resume_hash'],questionnaire_location='external platform',note='Do not use website completion as evidence of verified questionnaire completion.'),indent=2))
    return out.getvalue()

SCALES={'CF':list(range(1,7)),'PN':list(range(1,4)),'PI':list(range(1,6)),'PCD':list(range(1,6)),'PQ':list(range(1,6)),'GC':list(range(1,5)),'VIS':[1],'THEME':[1],'PRICE':[1]}
REVERSED={'CF3','CF4','CF5','CF6','PRICE1'}
def merge_external(store,path,include_tests=False):
    """Join an external *game-level* CSV. Reject duplicates and invalid scale values."""
    ext=pd.read_csv(path,dtype={'participant_id':str,'game_id':str})
    if not {'participant_id','game_id'}.issubset(ext.columns): raise ValueError('External CSV requires participant_id and game_id.')
    if ext.duplicated(['participant_id','game_id']).any(): raise ValueError('Duplicate participant/game rows in external CSV.')
    allowed={'participant_id','game_id','culture_recognition','prior_exposure'}|{g+str(i) for g,items in SCALES.items() for i in items}
    unknown=set(ext.columns)-allowed
    if unknown: raise ValueError('Unexpected fields: use a de-identified game-level export containing only documented columns: '+', '.join(sorted(unknown)))
    for g,items in SCALES.items():
        cols=[g+str(i) for i in items]
        for c in set(cols)&set(ext.columns):
            ext[c]=pd.to_numeric(ext[c],errors='raise')
            if ((ext[c].dropna()<1)|(ext[c].dropna()>7)|(ext[c].dropna()%1!=0)).any(): raise ValueError(f'{c} must be an integer 1–7 or missing.')
        if set(cols).issubset(ext.columns):
            coded=pd.DataFrame({c:(8-ext[c] if c in REVERSED else ext[c]) for c in cols})
            ext[g+'_score']=coded.mean(axis=1).where(coded.notna().all(axis=1))
    site=frame(store,'game_sessions',include_tests,True)
    merged=site.merge(ext,on=['participant_id','game_id'],how='left',validate='one_to_one',indicator='external_match')
    return merged

def external_report(store,path,include_tests=False):
    """Optional local diagnostics for external ratings; no survey UI is added."""
    merged=merge_external(store,path,include_tests)
    result={'label':'External stimulus-validation diagnostics; not final hypothesis tests','rows':len(merged),'unmatched_website_rows':int((merged.external_match!='both').sum()),'scales':{},'paired_diagnostics':[],'item_distributions':{},'recognition':[],'prior_exposure_counts':[]}
    for group,items in SCALES.items():
        score=group+'_score'
        if score in merged.columns:
            result['scales'][group]=merged.groupby('game_id')[score].agg(['count','mean','std']).reset_index().where(pd.notna, None).to_dict('records')
            result['paired_diagnostics'].append(paired_diagnostic(merged,score,.5))
        for i in items:
            c=group+str(i)
            if c in merged.columns:
                result['item_distributions'][c]=merged.groupby('game_id')[c].value_counts(dropna=False).rename('count').reset_index().to_dict('records')
    if 'culture_recognition' in merged.columns:
        for game,rows in merged.groupby('game_id'):
            values=rows.culture_recognition.dropna().astype(str).str.lower()
            result['recognition'].append(dict(game_id=game,n_answered=len(values),accuracy=float(values.isin(GAMES[game]['recognition']).mean()) if len(values) else None,counts=values.value_counts().to_dict()))
    if 'prior_exposure' in merged.columns:
        result['prior_exposure_counts']=merged.groupby('game_id').prior_exposure.value_counts(dropna=False).rename('count').reset_index().to_dict('records')
    result['note']='Proposed ±0.5 seven-point rating bounds require approval. Confidence intervals describe paired differences; no automatic equivalence declaration, hypothesis test, item deletion or participant exclusion is performed. Culture-recognition codes must follow the documented mapping.'
    return result
