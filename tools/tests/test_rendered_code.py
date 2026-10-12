"""Exercise real Hugo output after the pinned executable has been installed."""
import os,subprocess,tempfile,unittest
from pathlib import Path
from bs4 import BeautifulSoup


@unittest.skipUnless(os.environ.get('HUGO_RENDER_TEST')=='1','Run after verified Hugo setup')
class RenderedCodeTests(unittest.TestCase):
    def test_plain_and_typed_code_remain_copyable_and_only_explicit_goat_is_svg(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'content').mkdir();(root/'layouts').mkdir()
            (root/'hugo.toml').write_text('baseURL = "https://example.invalid/"\n')
            (root/'layouts/single.html').write_text('{{ .Content }}')
            plain='curl -H "Authorization: Bearer $TOKEN" https://example.invalid\n'
            typed='print("safe <code> & symbols")\n'
            (root/'content/test.md').write_text('---\ntitle: fixture\n---\n\n```\n'+plain+'```\n\n```python\n'+typed+'```\n\n```goat\n+---+\n| A |\n+---+\n```\n')
            subprocess.run(['hugo','--source',str(root),'--quiet'],check=True,capture_output=True)
            html=BeautifulSoup((root/'public/test/index.html').read_text(),'html.parser')
            blocks=html.select('pre code')
            self.assertEqual([x.get_text() for x in blocks],[plain,typed])
            self.assertEqual(len(html.select('svg')),1)


if __name__=='__main__':unittest.main()
