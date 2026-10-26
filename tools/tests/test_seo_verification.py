import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import seo_verification as seo
import verify_deployed as deployed
from publication_gate import GateError, SITE


def html(path='/', description='Short but accurate', robots='index, follow', body='Text'):
    return (f'<html><head><title>RockB</title><meta name="description" content="{description}">'
            f'<meta name="robots" content="{robots}"><link rel="canonical" href="{SITE}{path}">'
            '<meta property="og:title" content="RockB"></head>'
            f'<body><main><h1>Title</h1><p>{body}</p><a href="/posts/">Posts</a></main></body></html>')


class SEOTests(unittest.TestCase):
    def test_home_tag_article_and_static_and_short_text(self):
        for p in ['/', '/tags/ssrf/', '/posts/example/', '/about/']:
            self.assertEqual(seo.fingerprint(html(p), p)['description'], 'Short but accurate')

    def test_missing_duplicate_or_blank_metadata(self):
        base = html()
        for raw in [base.replace('<title>RockB</title>', ''),
                    base.replace('</head>', '<meta name="description" content="duplicate"></head>'),
                    base.replace('Short but accurate', ''),
                    base.replace('</head>', '<meta name="robots" content="noindex"></head>')]:
            with self.subTest(raw=raw), self.assertRaises(GateError):seo.fingerprint(raw, '/')

    def test_wrong_canonical_and_meta_refresh(self):
        for raw in [html().replace(SITE, 'https://evil.example'),
                    html().replace('</head>', '<meta http-equiv="refresh" content="0;url=/"></head>')]:
            with self.assertRaises(GateError):seo.fingerprint(raw, '/')

    def test_path_injection_and_traversal(self):
        for path in ['https://evil.test/', '//evil.test/', '/../../', '/a/../', '/%2e%2e/', '/a/?x=1',
                     '/a/#b', '/a\\b/', '/a//b/', 'relative/', '/a']:
            with self.subTest(path=path), self.assertRaises(GateError):seo.checked_path(path)

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            Path(b,'index.html').write_text(html())
            Path(a,'escape').symlink_to(b, target_is_directory=True)
            with self.assertRaises(GateError):seo.rendered_file(a, '/escape/')

    def test_redirect_rejected(self):
        with self.assertRaises(GateError):seo.NoRedirect().redirect_request(None,None,302,'',{},'https://evil.test/')

    def test_exact_public_match_and_meaningful_mismatches(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);(root/'index.html').write_text(html())
            with patch.object(seo,'fetch_live',return_value=html()):
                self.assertEqual(len(seo.verify_paths(root,['/'],'a'*40)),1)
            for raw in [html(description='different'),html(robots='noindex, follow'),html(body='Other'),
                        html().replace('href="/posts/"','href="/other/"'),html().replace('content="RockB"','content="Other"')]:
                with patch.object(seo,'fetch_live',return_value=raw), self.assertRaises(GateError):
                    seo.verify_paths(root,['/'],'a'*40)

    def test_unavailable_public_page(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'index.html').write_text(html())
            with patch.object(seo,'fetch_live',side_effect=OSError('404')), self.assertRaises(OSError):
                seo.verify_paths(Path(temp),['/'],'a'*40)

    def test_pages_identity_before_network_verification(self):
        commit='a'*40;page='b'*40
        cases=[([{'object':{'sha':'c'*40}}],RuntimeError),
               ([{'object':{'sha':commit}},{'status':'building'}],GateError),
               ([{'object':{'sha':commit}},{'status':'built','commit':page},{'object':{'sha':'c'*40}}],GateError),
               ([{'object':{'sha':commit}},{'status':'built','commit':page},{'object':{'sha':page}},
                 {'commit':{'message':'other source'}}],GateError)]
        for values,error in cases:
            with patch.object(deployed,'gh',side_effect=values), patch.object(deployed,'verify_paths') as verify, self.assertRaises(error):
                deployed.verify_once('x/y',commit,Path('public'),[],['/'])
            verify.assert_not_called()

    def test_correct_pages_identity_calls_generic_check(self):
        commit='a'*40;page='b'*40
        with patch.object(deployed,'gh',side_effect=[{'object':{'sha':commit}}, {'status':'built','commit':page},
                    {'object':{'sha':page}},{'commit':{'message':'deploy '+commit}}]), \
                patch.object(deployed,'verify_paths',return_value=[{'url':SITE+'/'}]) as verify:
            result=deployed.verify_once('x/y',commit,Path('public'),[],['/'])
            self.assertEqual(result['source_commit'],commit);verify.assert_called_once()

    def test_site_pages_and_changed_taxonomy_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'quality').mkdir();public=root/'public';public.mkdir()
            (root/'quality/seo-verification.json').write_text(json.dumps({'version':1,'paths':['/']}))
            (public/'sitemap-pages.xml').write_text(f'<urlset><url><loc>{SITE}/about/</loc></url></urlset>')
            for path in ['/','/about/','/tags/example/']:
                p=public/path.strip('/')/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html(path))
            self.assertEqual(seo.selected_paths(root,public,['content/tags/example/_index.md']),['/','/about/','/tags/example/'])

if __name__=='__main__':unittest.main()
