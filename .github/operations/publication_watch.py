"""Verify declared publication against GitHub and the public page, independently."""
import hashlib,json,re,urllib.request
from datetime import datetime
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

SHA=re.compile(r'[0-9a-f]{40}')
URL=re.compile(r'https://baeseokjae\.github\.io/posts/[a-z0-9-]+/')
ALERTS={'external_publication_unverified','external_publication_evidence_unavailable',
        'external_publication_missed','external_publication_state_unknown'}


class Article(HTMLParser):
    def __init__(self):
        super().__init__();self.stack=[];self.level=None;self.parts=[];self.canonical=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link' and 'canonical' in a.get('rel','').split():self.canonical=a.get('href')
        if tag in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:return
        self.stack.append(tag)
        if self.level is None and 'post-content' in a.get('class','').split():self.level=len(self.stack)
    def handle_endtag(self,tag):
        if tag in self.stack:
            index=len(self.stack)-1-self.stack[::-1].index(tag)
            if self.level is not None and index<self.level:self.level=None
            self.stack=self.stack[:index]
    def handle_data(self,data):
        if self.level is not None and not {'script','style'}.intersection(self.stack) and data.strip():self.parts.append(data.strip())
    def fingerprint(self):return hashlib.sha256(' '.join(' '.join(self.parts).split()).encode()).hexdigest()


def page(url):
    request=urllib.request.Request(url,headers={'User-Agent':'RockB-Independent-Publication-Watch/1','Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=20) as response:
        if response.status!=200 or response.geturl().split('?')[0]!=url.split('?')[0]:raise ValueError('Page identity differs')
        raw=response.read(2*1024**2)
        if len(raw)>=2*1024**2:raise ValueError('Unbounded page')
        return raw.decode()


def verify(signal,repo,at,api,fetch=page):
    if signal is None:return {'status':'legacy_signal','alerts':[]}
    try:
        deadline=datetime.fromisoformat(signal['deadline_at'])
        if signal.get('version')!=1 or type(signal.get('expected')) is not bool or deadline.tzinfo is None:raise ValueError('Invalid signal')
        local=at.astimezone(ZoneInfo('Asia/Seoul'))
        if signal['day']!=local.date().isoformat() or deadline!=local.replace(hour=9,minute=20,second=0,microsecond=0):raise ValueError('Stale schedule identity')
        if signal.get('status')=='unknown':return {'status':'unknown','alerts':['external_publication_state_unknown']}
        if not signal['expected']:return {'status':'not_expected','alerts':[]}
        proof=signal.get('proof')
        if not proof:
            if signal.get('status')=='verified':raise ValueError('Success without evidence')
            return {'status':'pending' if at<deadline else 'missed','alerts':[] if at<deadline else ['external_publication_missed']}
        commit,public_url,pages=proof['commit'],proof['url'],proof['pages_commit']
        if not SHA.fullmatch(commit) or not SHA.fullmatch(pages) or not URL.fullmatch(public_url):raise ValueError('Invalid proof identity')
        if not re.fullmatch('[0-9a-f]{64}',proof.get('body_sha256','')):raise ValueError('Missing body hash')
        runs=api(repo,'actions/runs?head_sha='+commit+'&per_page=30')['workflow_runs']
        matches=[r for r in runs if r.get('name')=='Deploy Hugo' and r.get('head_sha')==commit]
        if not matches or matches[0].get('conclusion')!='success':raise ValueError('CI evidence missing')
        page_commit=api(repo,'commits/'+pages)
        if page_commit.get('sha')!=pages or commit not in page_commit.get('commit',{}).get('message',''):raise ValueError('Pages source mismatch')
        live=Article();live.feed(fetch(public_url+'?opsverify='+commit[:12]))
        if live.canonical!=public_url or live.fingerprint()!=proof['body_sha256']:raise ValueError('Live body or canonical differs')
        name='rockb-notify-'+commit;ref=api(repo,'git/ref/tags/'+name)
        if ref.get('ref')!='refs/tags/'+name or ref.get('object',{}).get('type')!='tag':raise ValueError('Notification ref mismatch')
        tag=api(repo,'git/tags/'+ref['object']['sha']);receipt=json.loads(tag['message'])
        if (tag.get('sha')!=ref['object']['sha'] or tag.get('tag')!=name or tag.get('object',{}).get('type')!='commit' or tag.get('object',{}).get('sha')!=commit
            or receipt.get('version')!=1 or receipt.get('source_commit')!=commit or receipt.get('status')!='sent'):raise ValueError('Notification evidence unverified')
        return {'status':'verified','alerts':[],'day':signal['day'],'source_commit':commit,'body_sha256':live.fingerprint()}
    except (ValueError,KeyError,TypeError,AttributeError):return {'status':'mismatch','alerts':['external_publication_unverified']}
    except Exception:return {'status':'unavailable','alerts':['external_publication_evidence_unavailable']}
