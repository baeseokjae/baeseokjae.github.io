"""Notify only a verified new publication; persist send intent before the request.

An uncertain send is never retried automatically. The ledger contains only
publication identifiers and delivery state, never chat credentials or contents.
"""
import html
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
import yaml


def github(repo,path,method='GET',body=None):
    token=os.environ['GH_TOKEN']
    req=urllib.request.Request('https://api.github.com/repos/'+repo+'/'+path,method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=25) as res:return json.load(res)


def notify(repo,commit,verification,posts,send=None):
    if verification.get('status')!='verified' or verification.get('source_commit')!=commit:
        raise ValueError('Notification requires exact public verification')
    if not posts:return {'status':'not_required'}
    ref='tags/rockb-notify-'+commit
    try:
        existing=github(repo,'git/ref/'+ref)
    except urllib.error.HTTPError as exc:
        if exc.code!=404:raise
        existing=None
    if existing:
        tag=github(repo,'git/tags/'+existing['object']['sha']);receipt=json.loads(tag['message'])
        if receipt.get('source_commit')!=commit:raise ValueError('Notification ledger identity differs')
        return {'status':receipt['status'],'reused':True}
    receipt={'version':1,'source_commit':commit,'status':'delivery_unknown','at':datetime.now(timezone.utc).isoformat()}
    def tag_for(value):
        return github(repo,'git/tags','POST',{'tag':'rockb-notify-'+commit,'message':json.dumps(value),
                    'object':commit,'type':'commit'})['sha']
    intent=tag_for(receipt)
    # If this POST loses its response, stop; retry reads the durable ref first.
    github(repo,'git/refs','POST',{'ref':'refs/'+ref,'sha':intent})
    title=html.escape(posts[0]['title'])
    text=('📝 <b>New post published</b>\n'+title if len(posts)==1 else
          f'📝 <b>{len(posts)} new posts published</b>\n'+title+f' (and {len(posts)-1} more)')
    text+='\n\n🔗 https://baeseokjae.github.io/'
    if send is None:
        def send(text):
            body=urllib.parse.urlencode({'chat_id':os.environ['TELEGRAM_CHAT_ID'],'text':text,'parse_mode':'HTML'}).encode()
            req=urllib.request.Request('https://api.telegram.org/bot'+os.environ['TELEGRAM_BOT_TOKEN']+'/sendMessage',data=body)
            with urllib.request.urlopen(req,timeout=25) as response:return json.load(response)
    response=send(text)
    if not response.get('ok'):raise ValueError('Telegram rejected notification; inspect delivery ledger')
    sent={**receipt,'status':'sent','at':datetime.now(timezone.utc).isoformat()}
    tag=tag_for(sent);github(repo,'git/refs/'+ref,'PATCH',{'sha':tag,'force':True})
    return {'status':'sent','message_id':response.get('result',{}).get('message_id')}


if __name__=='__main__':
    try:
        commit=os.environ['GITHUB_SHA'];repo=os.environ['GITHUB_REPOSITORY']
        paths=subprocess.check_output(['git','diff',commit+'^',commit,'--name-only','--diff-filter=A','--','content/posts'],text=True).splitlines()
        posts=[]
        for path in paths:
            if path.endswith('.md'):
                meta=yaml.safe_load(Path(path).read_text().split('---\n',2)[1])
                posts.append({'title':str(meta['title'])})
        result=notify(repo,commit,json.loads(Path('live-verification.json').read_text()),posts)
        Path('notification-receipt.json').write_text(json.dumps(result)+'\n')
        print(json.dumps(result))
        if result['status']=='delivery_unknown':raise SystemExit(1)
    except Exception as exc:
        # Exceptions from an HTTP client can contain credentials in the URL.
        Path('notification-receipt.json').write_text(json.dumps({'status':'delivery_unknown','error_type':type(exc).__name__})+'\n')
        raise SystemExit('Notification delivery needs reconciliation: '+type(exc).__name__)
