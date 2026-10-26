import tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from validate_seo_rendered import validate,changed_articles
from publication_gate import GateError,SITE

class RenderedSeoTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.public=self.root/'public'
  self.file=self.public/'posts/example/index.html';self.file.parent.mkdir(parents=True)
  self.html=f'<head><title>Title</title><meta name="description" content="Concise useful summary"><meta name="robots" content="index, follow"><link rel="canonical" href="{SITE}/posts/example/"></head><main><div class="post-content">English article</div></main>'
  self.file.write_text(self.html)
 def test_changed_scope_excludes_other_pages_and_deduplicates(self):
  self.assertEqual(changed_articles(['content/posts/example.md','layouts/partials/schema-example.html','content/tags/example/_index.md','content/about.md']),['example'])
 def test_short_description_passes_with_advisory(self):
  result=validate(self.root,self.public,['content/posts/example.md']);self.assertEqual(result['status'],'pass');self.assertIn('short_description_review_context_not_length',result['articles'][0]['warnings'])
 def test_missing_duplicate_metadata_or_noindex_fails_before_deploy(self):
  for raw in [self.html.replace('index, follow','noindex, follow'),self.html.replace('index, follow','none'),self.html.replace('<title>Title</title>',''),self.html.replace('</head>','<meta name="description" content="Duplicate"></head>')]:
   self.file.write_text(raw)
   with self.assertRaises(GateError):validate(self.root,self.public,['content/posts/example.md'])
 def test_korean_prose_warns_but_code_alone_does_not(self):
  self.file.write_text(self.html.replace('English article','한글 본문 '*80));r=validate(self.root,self.public,['content/posts/example.md']);self.assertIn('review_visible_prose_language_for_english_audience',r['articles'][0]['warnings'])
  self.file.write_text(self.html.replace('English article','English article <pre><code>'+'한글 '*100+'</code></pre>'));r=validate(self.root,self.public,['content/posts/example.md']);self.assertNotIn('review_visible_prose_language_for_english_audience',r['articles'][0]['warnings'])
 def test_unrelated_change_does_not_validate_old_backlog(self):
  self.file.unlink();self.assertEqual(validate(self.root,self.public,['tools/example.py'])['articles'],[])

if __name__=='__main__':unittest.main()
