"""Bilingual task website; questionnaires are administered on an external platform."""
import hmac
import math
import os
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st
from pilot.content import GAMES,ROOT,APP_VERSION,text,pages,questionnaire_url
from pilot.storage import Store,StaleStep,seconds
from pilot.analysis import report,export_zip,frame
from pilot.settings import STUDY,collection_blockers

st.set_page_config(page_title='Board Game Learning Study | 桌游学习研究',page_icon='◈',layout='centered',initial_sidebar_state='collapsed')

def setting(key,default=''):
    if key in os.environ: return os.environ[key]
    try: return str(st.secrets.get(key,default))
    except (FileNotFoundError,KeyError): return default

LANG=st.session_state.get('language','zh')
def tr(en,zh): return zh if LANG=='zh' else en

def asset(name,caption):
    p=ROOT/'assets'/name
    if p.is_file(): st.image(str(p),width='stretch')
    else:
        st.info(tr('Illustration unavailable. Please use the complete text description below.','图示暂不可用，请阅读下方完整文字说明。'))
    st.caption(caption)

def advance(expected,answers=None):
    try:
        STORE.advance(st.session_state.participant_id,expected,answers)
    except (ValueError,StaleStep) as e:
        st.session_state['validation_error']=str(e) if LANG=='en' else '请完成所有项目并满足页面所需时间；若该步骤已保存，请刷新后继续。'
        return

def next_button(stage,label=None):
    st.button(label or tr('Continue','继续'),type='primary',width='stretch',on_click=advance,args=(stage,))

def submit_task(stage,codes):
    answers={c:st.session_state.get(c) for c in codes}
    if any(v is None for v in answers.values()):
        st.session_state['validation_error']=tr('Please answer every item before continuing.','请回答全部题目后继续。')
        return
    advance(stage,answers)

def admin():
    st.title('Researcher dashboard')
    configured=setting('PILOT_ADMIN_PASSWORD')
    if not configured:
        st.info('Set PILOT_ADMIN_PASSWORD in your environment or Streamlit secrets to enable this protected page. Local CLI: python admin.py summary')
        return
    if not st.session_state.get('admin_authenticated'):
        with st.form('admin_login'):
            password=st.text_input('Researcher password',type='password')
            submitted=st.form_submit_button('Sign in')
        if submitted:
            if hmac.compare_digest(password.encode(),configured.encode()):
                st.session_state.admin_authenticated=True; st.rerun()
            else: st.error('Incorrect password.')
        return
    if st.button('Sign out'):
        st.session_state.pop('admin_authenticated',None);st.rerun()
    include=st.checkbox('Include test records',value=False)
    r=report(STORE,include)
    st.caption(r['label'])
    st.metric('Participants started',r['participants_started'])
    c1,c2=st.columns(2);c1.metric('Completed',r['status_counts'].get('completed',0));c2.metric('In progress',r['status_counts'].get('in_progress',0))
    st.write('Status counts',r['status_counts']);st.write('Assigned orders',r['order_counts'])
    if r['mean_completion_seconds'] is not None: st.metric('Mean elapsed minutes',round(r['mean_completion_seconds']/60,1))
    st.caption(r['timing_note'])
    for title,key in [('Comprehension by game','quiz_by_game'),('Comprehension by item','quiz_by_item'),('Missing task responses','missing'),('Paired task diagnostics','paired_diagnostics')]:
        st.subheader(title);st.dataframe(r[key],width='stretch')
    st.info(r['bounds_note']);st.info(r['external_note'])
    st.subheader('Exports')
    incomplete=st.checkbox('Include unfinished sessions in export',value=False)
    st.download_button('Download normalized CSV bundle',export_zip(STORE,include,not incomplete),file_name='pilot_task_export.zip',mime='application/zip',type='primary')
    st.caption('Task records contain no scale ratings. Join the external game-level questionnaire export by participant_id and game_id using admin.py merge-external.')
    st.json({'app_version':APP_VERSION,'mode':MODE,'collection_blockers':collection_blockers(SETTINGS) if MODE=='collection' else ['Preview mode: test records only.']})

SETTINGS={k:setting(k) for k in ['PILOT_MODE','PILOT_APPROVALS_CONFIRMED','PILOT_STORAGE_APPROVED','PILOT_SURVEY_URL_1','PILOT_SURVEY_URL_2','PILOT_PUBLIC_URL']}
MODE=setting('PILOT_MODE','preview')
if MODE not in ('preview','collection'): st.error('PILOT_MODE must be preview or collection.');st.stop()
DB_PATH=Path(setting('PILOT_DB_PATH',str(ROOT/'data/pilot.sqlite3')))
if not DB_PATH.is_absolute(): DB_PATH=ROOT/DB_PATH
STORE=Store(DB_PATH)
if st.query_params.get('researcher')=='1': admin();st.stop()

st.markdown('''<style>
.block-container{max-width:880px;padding-top:2rem;padding-bottom:3rem}
h1{font-size:2.2rem!important;line-height:1.2!important;letter-spacing:-.03em}
h2{font-size:1.5rem!important;margin-top:1.2rem!important}
p,li{line-height:1.75} [data-testid="stMetricValue"]{font-size:1.7rem}
.stButton>button,.stLinkButton>a{min-height:48px;border-radius:10px}
[data-testid="stRadio"] label{padding:5px 0} [data-testid="stCaptionContainer"]{line-height:1.6}
@media(max-width:600px){.block-container{padding:1rem 1rem 2rem}h1{font-size:1.8rem!important}}
</style>''',unsafe_allow_html=True)

if st.session_state.get('validation_error'): st.error(st.session_state.pop('validation_error'))
if MODE=='preview': st.caption(tr('RESEARCH PREVIEW · test sessions only · Chinese translation pending review','研究预览 · 仅供测试 · 中文译文待审校'))
blockers=collection_blockers(SETTINGS)
if blockers:
    st.error('Recruitment is not enabled: complete the researcher checklist first.');st.json(blockers);st.stop()

# A random resume capability, rather than a participant identifier, restores a session.
token=st.query_params.get('resume') or st.session_state.get('resume_token')
p=STORE.resume(token) if token else None
if token and p is None:
    st.error(tr('This session link is invalid or was withdrawn. Open the original study link to start again.','此会话链接无效或已撤回。请从原始研究链接重新进入。'));st.stop()
if p:
    st.session_state.participant_id=p['participant_id'];st.session_state.resume_token=token
    st.session_state.language=p['language'];LANG=p['language']

if not p:
    language=st.radio('Language / 语言',['简体中文','English'],horizontal=True,index=0,key='language_choice')
    LANG='zh' if language=='简体中文' else 'en';st.session_state.language=LANG
    st.caption(tr('A short introduction to two board games','两款桌游的简短体验'))
    st.title(text(STUDY['study_title'],LANG))
    st.write(tr('Explore two board games, learn their basic rules and try a short activity for each. There are no purchases to make.','您将了解两款桌游、学习基本规则，并分别完成简短活动。您无需购买任何产品。'))
    st.write(tr('Allow about 15–20 minutes for this website, plus time for the external questionnaires.','本网站约需15–20分钟，另需预留外部问卷填写时间。'))
    with st.container(border=True):
        st.subheader(tr('Before starting','开始之前'))
        st.write(tr('Eligibility, adult confirmation, informed consent and all questionnaires are handled by your external study platform. Begin here only after that platform has confirmed your eligibility and consent. If you are under 18 or do not agree to participate, please close this page.','资格筛查、年满18岁确认、知情同意及所有问卷均由外部研究平台处理。仅在该平台已确认您的资格与同意后，才开始此处活动。若未满18岁或不同意参与，请关闭本页面。'))
        st.write(tr('Participation is voluntary. This site saves anonymous task responses and elapsed page times as you proceed. It does not ask for your name or email. You may leave before finishing, or use “Withdraw” to delete saved website answers before final submission. External-platform withdrawal follows that platform’s study information.','参与完全自愿。本网站会逐步保存匿名任务回答和页面经过时间，不询问姓名或邮箱。您可在完成前离开，或在最终提交前使用“撤回”删除已保存的网站回答。外部平台的撤回按其研究说明处理。'))
    contact=STUDY['research_contact'] or tr('[Research contact pending confirmation]','[研究联系信息待确认]')
    st.caption(contact)
    st.caption(tr('Preview uses original schematic illustrations and an experimental price placeholder. These materials are not approved for recruitment yet.','预览使用原创示意图和暂定实验价格；材料尚未获准用于正式招募。'))
    if st.button(tr('Start preview' if MODE=='preview' else 'Start the game activities','开始预览' if MODE=='preview' else '开始游戏活动'),type='primary',width='stretch'):
        forced=None
        if MODE=='preview' and setting('PILOT_TEST_ORDER'):
            forced=tuple(setting('PILOT_TEST_ORDER').split(','))
        pid,resume=STORE.start(LANG,MODE=='preview',forced)
        st.session_state.participant_id=pid;st.session_state.resume_token=resume
        st.query_params['resume']=resume;st.rerun()
    st.stop()

stage=STORE.stage(p);order=(p['first_game'],p['second_game']);sequence=pages(order)
st.progress(min(p['page_index']/(len(sequence)-1),1),text=tr(f'Step {p["page_index"]+1} of {len(sequence)}',f'第{p["page_index"]+1}步，共{len(sequence)}步'))
st.caption(tr('Your anonymous matching code: ','您的匿名匹配码：')+p['participant_id'])
with st.sidebar:
    st.caption(tr('Language','语言')+': '+('English' if LANG=='en' else '简体中文'))
    if p['status']=='in_progress':
        with st.expander(tr('Leave this study','退出研究')):
            st.write(tr('Withdraw deletes your saved website answers. This does not delete answers on the external questionnaire platform.','撤回会删除已保存的网站回答，不会删除外部问卷平台的回答。'))
            if st.checkbox(tr('I want to withdraw and delete my website answers.','我要撤回并删除我的网站回答。')):
                if st.button(tr('Withdraw','撤回')):
                    STORE.withdraw(p['participant_id']);st.query_params.clear();st.session_state.clear();st.success(tr('Your website answers were deleted. You may close this page.','您的网站回答已删除，可以关闭本页。'));st.stop()

kind,_,gid=stage.partition(':')
if gid:
    game=GAMES[gid];position=order.index(gid)+1
    st.caption(tr(f'GAME {position} OF 2',f'游戏{position}／2'))
    st.title(game['title'])

with st.empty().container():
    if kind=='product':
        st.write(text(game['culture'],LANG))
        asset(game['hero_asset'],tr('Temporary original research schematic; not commercial game artwork.','暂用原创研究示意图，并非商业游戏美术素材。'))
        st.write(text(game['description'],LANG))
        c1,c2,c3=st.columns(3)
        c1.metric(tr('Players','玩家人数'),game['players']);c2.metric(tr('Minutes (full game)','分钟（完整游戏）'),game['minutes']);c3.metric(tr('Price scenario','价格情境'),'CNY 299')
        st.caption(text(game['price'],LANG))
        st.subheader(tr('Your objective','游戏目标'));st.write(text(game['objective'],LANG))
        st.subheader(tr('In the box','组件概览'));st.write(text(game['components'],LANG))
        next_button(stage,tr('Learn the rules','学习规则'))
    elif kind=='learn':
        st.write(tr('Read the six short sections and two examples. You can keep this page open until you are ready.','请阅读以下6个简短部分和2个示例。准备好后再继续。'))
        for sec in game['sections']:
            st.subheader(text(sec['title'],LANG));st.write(text(sec['text'],LANG))
        for example in game['examples']:
            st.subheader(text(example['title'],LANG));asset(example['asset'],tr('Original explanatory schematic','原创说明示意图'));st.write(text(example['text'],LANG))
        st.subheader(tr('Quick questions','简短答疑'))
        for faq in game['faq']:
            with st.expander(text(faq['question'],LANG)): st.write(text(faq['answer'],LANG))
        next_button(stage,tr('Try a short activity','开始简短活动'))
    elif kind in ('trial','quiz'):
        st.subheader(tr('Try one short turn','试做一个简短回合') if kind=='trial' else tr('Check your understanding','检查您的理解'))
        if kind=='trial': asset(game['examples'][0]['asset'],tr('Use this position for decision 1; decisions 2 and 3 describe the next steps.','第1项决策使用此图；第2和第3项描述后续步骤。'))
        st.write(tr('Choose one answer for each item. Answers will be available after the full pilot is complete.','请每题选择一个答案。完整试做结束后可查看答案。'))
        qs=game['trials' if kind=='trial' else 'quiz'];answers={}
        with st.form('game_task'):
            for q in qs:
                options={o['id']:text(o['text'],LANG) for o in q['options']}
                answers[q['code']]=st.radio(text(q['prompt'],LANG),list(options),format_func=lambda v,op=options:op[v],index=None,key=q['code'])
            st.form_submit_button(tr('Save and continue','保存并继续'),type='primary',width='stretch',on_click=submit_task,args=(stage,[q['code'] for q in qs]))
    elif kind=='handoff':
        st.subheader(tr('Your questionnaire','您的问卷'))
        st.write(tr('Please answer the questionnaire about the game you have just experienced, then return to this page. Keep this tab open.','请填写关于刚体验游戏的问卷，然后回到本页面。请保留本标签页。'))
        base=setting(f'PILOT_SURVEY_URL_{position}')
        STORE.prepare_handoff(p['participant_id'],gid,bool(base))
        public=setting('PILOT_PUBLIC_URL','http://localhost:8502').rstrip('/')
        return_url=public+'/?'+urlencode({'resume':st.session_state.resume_token})
        if base:
            try:
                url=questionnaire_url(base,p['participant_id'],gid,position,order,LANG,return_url)
                st.link_button(tr('Open questionnaire in a new tab','在新标签页打开问卷'),url,type='primary',width='stretch')
            except ValueError as e: st.error(str(e));st.stop()
            st.code(p['participant_id'],language=None)
            st.caption(tr('Matching code and game information are included in the link. If asked, use the code above.','链接已包含匹配码和游戏信息。如问卷要求，请使用上方代码。'))
            next_button(stage,tr('I completed the questionnaire — continue','我已完成问卷——继续'))
            st.caption(tr('This button records your return; questionnaire completion is checked separately by the researcher.','该按钮记录您的返回；问卷完成情况由研究者另外核对。'))
        else:
            st.info(tr('Preview: external questionnaire link is not configured. No questionnaire is collected here.','预览：尚未配置外部问卷链接。本网站不收集问卷。'))
            next_button(stage,tr('Continue preview without a questionnaire','不填写问卷，继续预览'))
    elif stage=='filler':
        st.title(tr('A short pause','短暂休息'))
        st.write(tr('Spend at least 90 seconds on this neutral shape-counting activity before continuing. Count the circles on each line.','继续前，请花至少90秒完成这个中性的数图形活动。数一数每行有几个圆形。'))
        answers={}
        for code,shapes in [('FILL1','● ▲ ● ■ ● ◆ ● ▲'),('FILL2','■ ● ◆ ● ▲ ● ■ ◆'),('FILL3','● ■ ● ▲ ● ◆ ● ■ ●')]:
            st.markdown(f'### {shapes}')
            answers[code]=st.radio(tr('How many circles?','有几个圆形？'),['3','4','5','6'],index=None,horizontal=True,key=code)
        remain=max(0,math.ceil(90-seconds(p['page_entered_at'])))
        st.caption(tr(f'{remain} seconds remaining. The timer continues while you look at the shapes.','剩余'+str(remain)+'秒。您观察图形时计时会继续。'))
        st.button(tr('Continue to the next game','继续下一款游戏'),type='primary',width='stretch',on_click=submit_task,args=(stage,['FILL1','FILL2','FILL3']))
    elif stage=='finish':
        st.title(tr('You have explored both games','您已体验两款游戏'))
        st.write(tr('Your game activities and questionnaire return steps are saved. Use the button below to finalize the website portion.','您的游戏活动和问卷返回步骤已保存。请点击下方按钮，最终提交网站部分。'))
        st.caption(tr('Your external platform manages any additional questions, payment and study completion code.','其他问题、报酬和研究完成代码由外部平台管理。'))
        next_button(stage,tr('Finish and view the debrief','完成并查看研究说明'))
    elif stage=='complete':
        st.title(tr('Thank you for taking part','感谢参与'))
        st.success(tr('Your website session is complete.','您的网站体验已完成。'))
        st.write(tr('This pilot compares two culturally different board-game stimuli and checks whether their instructions, activities and presentation are suitable for a later study. It does not establish that either culture or game is superior.','本试做比较两款呈现不同文化的桌游，检查说明、活动和呈现方式是否适合后续研究。它并不证明任何文化或游戏更优越。'))
        st.write(tr('Please follow your external platform’s instructions to finish the study and claim any participation payment.','请按照外部平台的说明完成研究并领取可能的参与报酬。'))
        with st.expander(tr('Activity answers and official rule sources','活动答案与官方规则来源')):
            for g in order:
                st.subheader(GAMES[g]['title'])
                for q in GAMES[g]['trials']+GAMES[g]['quiz']:
                    answer=next(o['text'] for o in q['options'] if o['id']==q['answer'])
                    st.write(text(q['prompt'],LANG)+' → '+text(answer,LANG))
                    st.caption(q['rule_ref'])
                st.link_button(tr('Official English rulebook','官方英文规则书'),GAMES[g]['rules_url'])
