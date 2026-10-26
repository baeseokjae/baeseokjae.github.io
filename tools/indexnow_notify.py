"""Independent post-deployment IndexNow notification with a durable intent ledger.

Only actually changed, verified, indexable article URLs are admitted in v1.
Non-article edits/deletions need a separately reviewed URL manifest; no bulk fallback.
The public ownership key is separate from all private Webmaster credentials.
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from notify_publication import github
from publication_gate import SITE
from seo_verification import NoRedirect

ENDPOINT='https://api.indexnow.org/indexnow'


def select_urls(changes, verification, root):
    slugs=set()
    for path in changes:
        m=re.fullmatch(r'content/posts/([a-z0-9-]+)\.md|layouts/partials/schema-([a-z0-9-]+)\.html',path)
        if m:slugs.add(next(x for x in m.groups() if x))
    verified=set(verification.get('slugs',[]));urls=[]
    for slug in sorted(slugs):
        if slug not in verified:raise ValueError('Changed URL lacks exact public verification')
        file=Path(root)/'public/posts'/slug/'index.html'
        if not file.is_file():raise ValueError('Deletion not supported by article notification v1')
        soup=BeautifulSoup(file.read_text(),'html.parser')
        canonical=soup.select('link[rel="canonical"]');robots=soup.select('meta[name="robots"]')
        url=SITE+'/posts/'+slug+'/'
        if len(canonical)!=1 or canonical[0].get('href')!=url:raise ValueError('Changed URL not self canonical')
        if len(robots)!=1 or 'noindex' in robots[0].get('content','').lower():
            raise ValueError('Changed URL not indexable')
        urls.append(url)
    return urls


def ownership(key):
    opener=urllib.request.build_opener(NoRedirect())
    req=urllib.request.Request(SITE+'/'+key+'.txt',headers={'Accept-Encoding':'identity'})
    with opener.open(req,timeout=10) as res:
        if res.status!=200 or res.read(256).decode('utf-8').strip()!=key:
            raise ValueError('Public ownership key mismatch')


def post(payload):
    opener=urllib.request.build_opener(NoRedirect())
    request=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
    try:
        with opener.open(request,timeout=15) as res:return res.status,dict(res.headers)
    except urllib.error.HTTPError as exc:return exc.code,dict(exc.headers)


def notify(repo,commit,config,verification,changes,root,check_key=ownership,send=post,sleep=time.sleep):
    if config.get('enabled') is not True:return {'status':'off'}
    if config.get('version')!=1 or not re.fullmatch('[0-9a-f]{40}',commit):raise ValueError('Invalid notification configuration')
    if verification.get('status')!='verified' or verification.get('source_commit')!=commit or not verification.get('pages_commit'):
        raise ValueError('Exact source and Pages verification required')
    urls=select_urls(changes,verification,root)
    if not urls:return {'status':'not_required','reason':'no_changed_verified_article_urls'}
    if len(urls)>2:raise ValueError('Unexpected batch size; inspect ordinary publication limits')
    key=config.get('key','')
    if not re.fullmatch('[a-f0-9]{32}',key):raise ValueError('Invalid ownership key')
    if (Path(root)/'static'/f'{key}.txt').read_text().strip()!=key:raise ValueError('Local ownership key mismatch')
    ref='tags/rockb-indexnow-'+commit
    try:existing=github(repo,'git/ref/'+ref)
    except urllib.error.HTTPError as exc:
        if exc.code!=404:raise
        existing=None
    if existing:
        tag=github(repo,'git/tags/'+existing['object']['sha']);old=json.loads(tag['message'])
        if old.get('source_commit')!=commit or old.get('urls')!=urls:raise ValueError('Ledger identity mismatch')
        return {**old,'reused':True}
    check_key(key)
    receipt={'version':1,'source_commit':commit,'urls':urls,'status':'unknown','at':datetime.now(timezone.utc).isoformat()}
    def tag_for(value):
        return github(repo,'git/tags','POST',{'tag':'rockb-indexnow-'+commit,'message':json.dumps(value),'object':commit,'type':'commit'})['sha']
    # Atomic ref creation wins once; response loss stops before external submission.
    intent=tag_for(receipt)
    github(repo,'git/refs','POST',{'ref':'refs/'+ref,'sha':intent})
    payload={'host':'baeseokjae.github.io','key':key,'keyLocation':SITE+'/'+key+'.txt','urlList':urls}
    try:
        code,headers=send(payload)
        if code==429:
            delay=headers.get('Retry-After') or headers.get('retry-after')
            if isinstance(delay,str) and delay.isdigit() and 0<int(delay)<=5:
                sleep(int(delay));code,headers=send(payload)
        status={200:'submitted',202:'validation_pending',429:'rate_limited'}.get(code,'rejected' if 400<=code<500 else 'unknown')
        receipt.update(status=status,http_status=code,at=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        receipt.update(status='unknown',error_type=type(exc).__name__)
    tag=tag_for(receipt);github(repo,'git/refs/'+ref,'PATCH',{'sha':tag,'force':True})
    return receipt


def main():
    output=Path('indexnow-receipt.json')
    try:
        config=json.loads(Path('quality/indexnow.json').read_text())
        if config.get('enabled') is not True:result={'status':'off'}
        else:
            commit=os.environ['GITHUB_SHA']
            changes=subprocess.check_output(['git','diff','--name-only',commit+'^',commit,'--'],text=True).splitlines()
            result=notify(os.environ['GITHUB_REPOSITORY'],commit,config,json.loads(Path('live-verification.json').read_text()),changes,Path('.'))
    except Exception as exc:result={'status':'needs_reconciliation','error_type':type(exc).__name__}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'url_count':len(result.get('urls',[]))}))
    # This observer cannot change publication or Telegram success.

if __name__=='__main__':main()
