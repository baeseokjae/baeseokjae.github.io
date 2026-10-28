"""Real Hugo pages must preserve collection membership and each page canonical."""
import os,shutil,subprocess,tempfile,unittest
from pathlib import Path
from bs4 import BeautifulSoup

@unittest.skipUnless(os.environ.get('HUGO_RENDER_TEST')=='1','Requires pinned Hugo')
class PaginationTests(unittest.TestCase):
 def test_filtered_lists_have_distinct_canonicals_without_changing_membership(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'content/posts').mkdir(parents=True);(root/'layouts/partials').mkdir(parents=True)
   source=Path(__file__).resolve().parents[2]/'layouts/partials/canonical-url.html';shutil.copyfile(source,root/'layouts/partials/canonical-url.html')
   (root/'hugo.toml').write_text('baseURL = "https://example.invalid/"\n[pagination]\npagerSize = 2\n[params]\nmainSections = ["posts"]\n')
   head='<head><link rel="canonical" href="{{ partial "canonical-url.html" . }}"></head>'
   listing=head+'''{{ $pages := union .RegularPages .Sections }}{{ if .IsHome }}{{ $pages = where site.RegularPages "Type" "in" site.Params.mainSections }}{{ $pages = where $pages "Params.hiddenInHomeList" "!=" "true" }}{{ end }}{{ $p := .Paginate $pages }}{{ range $p.Pages }}<a class="entry" href="{{ .RelPermalink }}">{{ .Title }}</a>{{ end }}'''
   (root/'layouts/list.html').write_text(listing);(root/'layouts/single.html').write_text(head+'{{ .Content }}');(root/'layouts/terms.html').write_text(head)
   for n in range(6):
    (root/f'content/posts/p{n}.md').write_text('---\ntitle: Post '+str(n)+'\ndate: 2026-01-0'+str(n+1)+'\ntags: [topic]\nhiddenInHomeList: "'+('true' if n==5 else 'false')+'"\n---\nBody\n')
   (root/'content/posts/custom.md').write_text('---\ntitle: External canonical\ncanonicalURL: https://example.org/source/\nhiddenInHomeList: "true"\n---\nBody\n')
   subprocess.run(['hugo','--source',str(root),'--quiet'],check=True,capture_output=True)
   for rel,expected in [('index.html','/'),('page/2/index.html','/page/2/'),('posts/page/2/index.html','/posts/page/2/'),('tags/topic/page/2/index.html','/tags/topic/page/2/'),('posts/p0/index.html','/posts/p0/')]:
    with self.subTest(rel=rel):
     soup=BeautifulSoup((root/'public'/rel).read_text(),'html.parser');self.assertEqual(soup.select_one('link[rel=canonical]')['href'],'https://example.invalid'+expected)
   home_entries=[]
   for f in [root/'public/index.html',root/'public/page/2/index.html',root/'public/page/3/index.html']:
    home_entries.extend(x['href'] for x in BeautifulSoup(f.read_text(),'html.parser').select('a.entry'))
   self.assertEqual(home_entries,[f'/posts/p{n}/' for n in [4,3,2,1,0]])
   custom=BeautifulSoup((root/'public/posts/custom/index.html').read_text(),'html.parser');self.assertEqual(custom.select_one('link[rel=canonical]')['href'],'https://example.org/source/')
