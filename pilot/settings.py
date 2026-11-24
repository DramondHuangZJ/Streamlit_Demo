import json,os
from urllib.parse import urlsplit
from .content import ROOT,GAMES
STUDY=json.loads((ROOT/'config/study.json').read_text())

def truth(value): return str(value).strip().lower() in ('1','true','yes')
def collection_blockers(settings):
    if settings.get('PILOT_MODE','preview')!='collection': return []
    missing=[]
    for key in ('PILOT_APPROVALS_CONFIRMED','PILOT_STORAGE_APPROVED'):
        if not truth(settings.get(key,'')): missing.append(key)
    for key in ('research_contact','institution','ethics_reference','retention_policy','materials_approved','translation_approved','prices_approved','external_screening_approved'):
        if not STUDY.get(key): missing.append('config/study.json: '+key)
    for key in ('PILOT_SURVEY_URL_1','PILOT_SURVEY_URL_2','PILOT_PUBLIC_URL'):
        value=settings.get(key,'');p=urlsplit(value)
        if p.scheme!='https' or not p.netloc or p.username or p.password: missing.append(key+' (HTTPS URL required)')
    return missing
