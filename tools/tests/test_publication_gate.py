import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("publication_gate", Path(__file__).parents[1] / "publication_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for p in ["content/posts", "layouts/partials", "quality/reviews", "static/images"]:
            (self.root / p).mkdir(parents=True)
        self.slug = "fixture-model"
        self.post = self.root / "content/posts/fixture-model.md"
        self.schema = self.root / "layouts/partials/schema-fixture-model.html"
        self.review = self.root / "quality/reviews/fixture-model.json"
        self.post.write_text('---\ntitle: Model 2026\ndescription: A reviewed model guide\ndraft: false\nschema: schema-fixture-model\n---\n\nThe model has 8B parameters. [Model card](https://vendor.example/model).\n')
        self.schema.write_text('<script type="application/ld+json">'+json.dumps({"@type": "Article", "headline": "Model 2026", "description": "A reviewed model guide"})+'</script>')
        now = datetime.now(timezone.utc).isoformat()
        self.receipt = {"version": 1, "slug": self.slug, "status": "approved", "reviewer": "fixture-review",
                        "reviewed_at": now, "schema_sha256": gate.digest(self.schema.read_bytes()),
                        "checks": {k: {"status": "pass", "note": "Checked fixture source"} for k in gate.CHECKS},
                        "sources": [{"id": "S1", "url": "https://vendor.example/model", "type": "primary", "checked_at": now}],
                        "commercial": {"paid": False}}
        self.cover_claims()

    def save(self):
        self.receipt["article_sha256"] = gate.digest(self.post.read_bytes())
        self.review.write_text(json.dumps(self.receipt))

    def cover_claims(self):
        _, _, meta, body = gate.read_post(self.root, self.slug)
        self.receipt["claims"] = [{"sha256": b["sha256"], "kind": "source", "source_ids": ["S1"], "note": "Checked against the primary model card"} for b in gate.risk_blocks(meta, body)]
        self.save()

    def check(self):
        return gate.check(self.root, self.slug)

    def test_reviewed_article_passes(self):
        self.assertEqual(self.check()["status"], "pass")

    def test_missing_review_blocks(self):
        self.review.unlink()
        with self.assertRaisesRegex(gate.GateError, "missing"):
            self.check()

    def test_changed_article_invalidates_approval(self):
        self.post.write_text(self.post.read_text() + "\nA new claim.\n")
        with self.assertRaisesRegex(gate.GateError, "article changed"):
            self.check()

    def test_unreviewed_model_id_cannot_pass_by_updating_document_hash(self):
        self.post.write_text(self.post.read_text() + "\nRun nonexistent-model:99b for 95% success.\n")
        self.save()
        with self.assertRaisesRegex(gate.GateError, "uncovered claim"):
            self.check()

    def test_unsupported_statistic_blocks(self):
        self.receipt["claims"][-1]["source_ids"] = []
        self.save()
        with self.assertRaisesRegex(gate.GateError, "primary source"):
            self.check()

    def test_unresolved_price_review_blocks(self):
        self.receipt["checks"]["pricing"]["status"] = "unverified"
        self.save()
        with self.assertRaisesRegex(gate.GateError, "pricing"):
            self.check()

    def test_test_claim_requires_raw_record(self):
        self.post.write_text(self.post.read_text()+"\nWe tested 50 tasks on our GPU.\n")
        self.cover_claims()
        with self.assertRaisesRegex(gate.GateError, "original run evidence"):
            self.check()
        self.receipt["claims"][-1].update(kind="first_party_test", run={"path": "missing.json", "sha256": "bad", "methodology": "fixed tasks"})
        self.save()
        with self.assertRaisesRegex(gate.GateError, "Evidence file missing"):
            self.check()

    def test_actual_test_record_passes_and_tampering_fails(self):
        self.post.write_text(self.post.read_text()+"\nWe tested 50 tasks on our GPU.\n")
        self.cover_claims()
        record=self.root/"run.json";record.write_text('{"completed":50}')
        self.receipt["claims"][-1].update(kind="first_party_test", run={"path":"run.json", "sha256":gate.digest(record.read_bytes()), "methodology":"fixed task set and runtime"})
        self.save();self.check()
        record.write_text('{"completed":1}')
        with self.assertRaisesRegex(gate.GateError, "hash mismatch"):
            self.check()

    def test_schema_mismatch_blocks(self):
        self.schema.write_text(self.schema.read_text().replace("Model 2026", "Wrong Model"))
        self.receipt["schema_sha256"] = gate.digest(self.schema.read_bytes());self.save()
        with self.assertRaisesRegex(gate.GateError, "title mismatch"):
            self.check()

    def test_cover_change_invalidates_review(self):
        self.post.write_text(self.post.read_text().replace("draft: false", "draft: false\ncover:\n  image: /images/cover.png"))
        cover=self.root/"static/images/cover.png";cover.write_bytes(b"first image")
        self.receipt["cover_sha256"]=gate.digest(cover.read_bytes());self.save();self.check()
        cover.write_bytes(b"unreviewed claim in cover")
        with self.assertRaisesRegex(gate.GateError, "cover changed"):
            self.check()

    def test_paid_placement_requires_disclosure_and_link_attributes(self):
        self.receipt["commercial"]={"paid": True, "disclosure_text":"Paid placement.", "links":["https://sponsor.example/"]};self.save()
        with self.assertRaisesRegex(gate.GateError, "disclosure"):
            self.check()
        self.post.write_text(self.post.read_text()+'\nPaid placement. <a href="https://sponsor.example/">Sponsor</a>\n');self.save()
        with self.assertRaisesRegex(gate.GateError, "sponsored/nofollow"):
            self.check()
        self.post.write_text(self.post.read_text().replace('href="https://sponsor.example/"', 'rel="sponsored" href="https://sponsor.example/"'));self.save();self.check()

    def test_future_review_date_blocks(self):
        self.receipt["reviewed_at"]="2999-01-01T00:00:00Z";self.save()
        with self.assertRaisesRegex(gate.GateError, "future"):
            self.check()

    def test_evidence_path_cannot_escape_repository(self):
        with self.assertRaisesRegex(gate.GateError, "leaves repository"):
            gate.local_file(self.root, "../outside.json")

    def test_baseline_catches_article_from_previous_failed_push(self):
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL).strip()
        git("init");git("config","user.email","fixture@example.invalid");git("config","user.name","Fixture")
        git("add",".");git("commit","-m","baseline");base=git("rev-parse","HEAD")
        p=self.root/"content/posts/unreviewed.md";p.write_text(self.post.read_text())
        git("add",".");git("commit","-m","unreviewed article")
        (self.root/"unrelated.txt").write_text("later unrelated change")
        git("add",".");git("commit","-m","unrelated followup")
        self.assertIn("unreviewed",gate.changed_slugs(self.root,base))
        with self.assertRaisesRegex(gate.GateError,"missing"):
            gate.check(self.root,"unreviewed")

    def test_http_200_with_old_article_is_not_publication_success(self):
        def html(body):
            return '<html><head><link rel="canonical" href="https://baeseokjae.github.io/posts/fixture-model/"><meta name="description" content="A guide"></head><h1>A model</h1><div class="post-content">'+body+'</div></html>'
        rendered=self.root/"public";p=rendered/"posts/fixture-model/index.html";p.parent.mkdir(parents=True);p.write_text(html("Corrected body"))
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return html("Old false claim").encode()
        with patch.object(gate.subprocess,"check_output",return_value=self.post.read_bytes()),patch.object(gate.urllib.request,"urlopen",return_value=Response()):
            with self.assertRaisesRegex(gate.GateError,"LIVE_MISMATCH"):
                gate.verify_live(self.root,self.slug,rendered,"a"*40)


if __name__ == "__main__":
    unittest.main()
