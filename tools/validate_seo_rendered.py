"""Before-deploy checks for changed articles; editorial signals remain warnings.

Never rewrite articles, approve a review, or treat snippet length as a ranking rule.
The reviewer remains responsible for language, evidence and content quality.
"""
import argparse,json,re,subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from publication_gate import GateError,page_fingerprint
from seo_verification import fingerprint


def changed_articles(paths):
    result=set()
    for path in paths:
        m=re.fullmatch(r'content/posts/([a-z0-9-]+)\.md|layouts/partials/schema-([a-z0-9-]+)\.html',path)
        if m:result.add(next(x for x in m.groups() if x))
    return sorted(result)


def check_article(root,rendered,slug):
    if not re.fullmatch('[a-z0-9-]+',slug):raise GateError('Invalid SEO article slug')
    raw=(rendered/'posts'/slug/'index.html').read_text()
    if (root/'quality/url-migrations'/f'{slug}.json').exists():
        page_fingerprint(root,slug,raw)
        return {'slug':slug,'status':'reviewed_redirect','warnings':[]}
    proof=fingerprint(raw,'/posts/'+slug+'/')
    tokens={x.strip().lower() for x in proof['robots'].split(',')}
    if tokens & {'noindex','nofollow','none'}:
        raise GateError('Changed published article unexpectedly prevents indexing or link following: '+slug)
    warnings=[]
    if len(proof['description'])<100:warnings.append('short_description_review_context_not_length')
    soup=BeautifulSoup(raw,'html.parser');body=soup.select_one('.post-content')
    if body is None:raise GateError('Changed article body missing')
    for code in body.select('pre,code'):code.decompose()
    visible=body.get_text(' ',strip=True)
    hangul=len(re.findall('[가-힣]',visible));latin=len(re.findall('[A-Za-z]',visible))
    if hangul>=100 and hangul/max(1,hangul+latin)>=.05:
        warnings.append('review_visible_prose_language_for_english_audience')
    if re.search('[가-힣]',proof['description']):warnings.append('review_description_language')
    return {'slug':slug,'status':'pass','description_length':len(proof['description']),
            'warnings':warnings,'body_language_signal':{'hangul_characters':hangul,'latin_characters':latin},
            'language_signal_is_not_a_classifier':True}


def validate(root,rendered,paths):
    return {'status':'pass','articles':[check_article(root,rendered,s) for s in changed_articles(paths)],
            'length_and_language_policy':'advisory; independent editorial review required',
            'source_scope':'changed article/schema paths only; existing warnings do not block unrelated publications'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('seo-render-validation.json'))
    args=parser.parse_args();root=Path.cwd();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    paths=subprocess.check_output(['git','diff','--name-only',commit+'^',commit,'--'],text=True).splitlines()
    result=validate(root,root/'public',paths);result['source_commit']=commit
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
