"""Versioned material loading and external questionnaire links."""
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
ROOT=Path(__file__).resolve().parents[1]
GAMES=json.loads((ROOT/'config/games.json').read_text())
APP_VERSION='pilot-1.1.0'
PROTOCOL_VERSION='external-survey-per-game-1'

def reload_materials():
    """Refresh config on reruns while preserving shared references in storage/scoring."""
    fresh=json.loads((ROOT/'config/games.json').read_text())
    if set(fresh)!={'dragon_castle','azul'}: raise ValueError('Both game configurations are required.')
    GAMES.clear();GAMES.update(fresh)


def text(value,lang='en'):
    return value.get(lang,value.get('en','')) if isinstance(value,dict) else value

def pages(order):
    result=[]
    for i,g in enumerate(order):
        result.extend(f'{s}:{g}' for s in ('product','learn','trial','quiz','handoff'))
        if i==0: result.append('filler')
    return result+['finish','complete']

def score_answers(game,kind,answers):
    qs=GAMES[game][kind]
    if set(answers)!={q['code'] for q in qs}: raise ValueError('Every task item requires a response.')
    scored=[]
    for q in qs:
        a=str(answers[q['code']])
        if a not in {o['id'] for o in q['options']}: raise ValueError('Invalid answer option.')
        scored.append((q['code'],a,int(a==q['answer']),q['rule_ref']))
    return scored

def questionnaire_url(base,pid,game,position,order,language,return_url,questionnaire_version="external-unconfigured"):
    parsed=urlsplit(base)
    if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('External questionnaire URL must be HTTPS without embedded credentials.')
    reserved={'participant_id','game_id','game_position','assigned_order','language','return_url','stimulus_version','rules_version','protocol_version','questionnaire_version'}
    pairs=[(k,v) for k,v in parse_qsl(parsed.query,keep_blank_values=True) if k not in reserved]
    pairs += list(dict(participant_id=pid,game_id=game,game_position=position,assigned_order=','.join(order),language=language,return_url=return_url,stimulus_version=GAMES[game]['stimulus_version'],rules_version=GAMES[game]['rules_version'],protocol_version=PROTOCOL_VERSION,questionnaire_version=questionnaire_version).items())
    return urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(pairs),parsed.fragment))
