"""Check ad eligibility in real Hugo output, including empty and opted-out posts."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


@unittest.skipUnless(os.environ.get("HUGO_RENDER_TEST") == "1", "Requires pinned Hugo")
class RenderedAdPlacementTests(unittest.TestCase):
    def test_article_ads_and_site_verification_have_different_scopes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content/posts").mkdir(parents=True)
            (root / "layouts/_default").mkdir(parents=True)
            (root / "layouts/partials").mkdir()
            source = Path(__file__).resolve().parents[2] / "layouts/partials/extend_head.html"
            shutil.copyfile(source, root / "layouts/partials/extend_head.html")
            (root / "hugo.toml").write_text('baseURL = "https://example.invalid/"\n')
            layout = '<html><head>{{ partial "extend_head.html" . }}</head><body>{{ .Content }}</body></html>'
            for name in ("_default/single.html", "_default/list.html", "404.html"):
                (root / "layouts" / name).write_text(layout)
            (root / "content/posts/full.md").write_text('---\ntitle: Article\ntags: [example]\n---\nUseful article content.\n')
            (root / "content/posts/empty.md").write_text('---\ntitle: Empty\n---\n')
            (root / "content/posts/no-ads.md").write_text('---\ntitle: No ads\nnoAds: true\n---\nUseful article content.\n')
            (root / "content/search.md").write_text('---\ntitle: Search\nlayout: search\n---\nSearch interface.\n')
            (root / "content/about.md").write_text('---\ntitle: About\n---\nSite information.\n')
            subprocess.run(["hugo", "--source", str(root), "--quiet"], check=True, capture_output=True)
            for name in ("index.html", "posts/index.html", "posts/full/index.html",
                         "posts/empty/index.html", "posts/no-ads/index.html",
                         "search/index.html", "about/index.html", "tags/index.html",
                         "tags/example/index.html", "404.html"):
                with self.subTest(page=name):
                    soup = BeautifulSoup((root / "public" / name).read_text(), "html.parser")
                    ads = soup.select('script[src*="pagead2.googlesyndication.com"]')
                    self.assertEqual(bool(ads), name == "posts/full/index.html")
                    self.assertIsNotNone(soup.select_one('meta[name="google-adsense-account"]'))


if __name__ == "__main__":
    unittest.main()
