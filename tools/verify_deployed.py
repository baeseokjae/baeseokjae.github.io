"""Wait for the exact Pages commit and compare public articles with this build."""
import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from publication_gate import page_fingerprint, GateError, SITE
from seo_verification import selected_paths, verify_paths

PROTECTED = ['best-ai-agent-memory-frameworks-2026','agent-memory-architecture-guide-2026',
             'vibe-coding-tools-comparison-2026']


def gh(path):
    return json.loads(subprocess.check_output(['gh','api',path],text=True,stderr=subprocess.PIPE,timeout=30))


def verify_once(repo, commit, rendered, slugs, paths=()):
    main=gh('repos/'+repo+'/git/ref/heads/main')['object']['sha']
    if main != commit: raise RuntimeError('Superseded source; do not verify or notify')
    pages=gh('repos/'+repo+'/pages/builds/latest')
    if pages.get('status')!='built':raise GateError('Pages is not built')
    current=gh('repos/'+repo+'/git/ref/heads/gh-pages')['object']['sha']
    if pages['commit']!=current:raise GateError('Pages branch not live yet')
    message=gh('repos/'+repo+'/commits/'+current)['commit']['message']
    if commit not in message:raise GateError('Pages belongs to another source commit')
    verified=[]
    for slug in slugs:
        expected=page_fingerprint(rendered.parent,slug,(rendered/'posts'/slug/'index.html').read_text())
        url=SITE+'/posts/'+slug+'/'
        request=urllib.request.Request(url+'?verify='+commit[:12],headers={'Cache-Control':'no-cache','User-Agent':'RockB-publication-verification/2.0'})
        with urllib.request.urlopen(request,timeout=20) as response:
            if response.status!=200:raise GateError('Article unavailable')
            actual=page_fingerprint(rendered.parent,slug,response.read().decode())
        if actual!=expected:raise GateError('Public content differs: '+slug)
        verified.append(slug)
    seo = verify_paths(rendered, paths, commit)
    return {'status':'verified','source_commit':commit,'pages_commit':current,'slugs':verified,'seo_pages':seo}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--rendered',type=Path,default=Path('public'));p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    changes=subprocess.check_output(['git','diff','--name-only',args.commit+'^',args.commit],text=True).splitlines()
    slugs=set(PROTECTED)|{'oodle','opus-4'}
    for path in changes:
        if path.startswith('content/posts/') and path.endswith('.md'):slugs.add(Path(path).stem)
        if path.startswith('layouts/partials/schema-') and path.endswith('.html'):slugs.add(Path(path).stem.removeprefix('schema-'))
        if path.startswith('quality/url-migrations/') and path.endswith('.json'):slugs.add(Path(path).stem)
    if set(changes)&{'.hugo-build.json','.github/workflows/deploy.yml','hugo.toml','assets/css/extended/code-blocks.css'}:
        slugs.add('toolreplay-agent-tool-call-audit-2026')
    paths=selected_paths(args.rendered.parent, args.rendered, changes)
    deadline=time.monotonic()+600
    while True:
        try:
            result=verify_once(args.repo,args.commit,args.rendered,sorted(slugs),paths);break
        except (GateError,OSError,subprocess.SubprocessError) as exc:
            if time.monotonic()>deadline:raise SystemExit('Public verification deadline reached: '+str(exc))
            time.sleep(15)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
