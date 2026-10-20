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

    def owner_exception(self):
        self.post.write_text(self.post.read_text().replace("draft: false", "draft: false\ncover:\n  image: /images/cover.png"))
        self.cover = self.root / "static/images/cover.png"
        self.cover.write_bytes(b"approved cover")
        self.review.unlink()
        target = self.root / "quality/publication-exceptions" / f"{self.slug}.json"
        target.parent.mkdir()
        target.write_text(json.dumps({"version": 1, "slug": self.slug,
            "authorization": "explicit_site_owner_instruction",
            "authorized_at": datetime.now(timezone.utc).isoformat(),
            "reason": "Owner explicitly authorized this exact existing-article publication.",
            "article_sha256": gate.digest(self.post.read_bytes()),
            "schema_sha256": gate.digest(self.schema.read_bytes()),
            "cover_sha256": gate.digest(self.cover.read_bytes())}))
        return target

    def test_owner_exception_is_distinct_from_review_approval(self):
        self.owner_exception()
        result = self.check()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["review_basis"], "site_owner_exception")

    def test_owner_exception_rejects_changed_artifacts(self):
        self.owner_exception()
        for artifact in (self.post, self.schema, self.cover):
            with self.subTest(artifact=artifact):
                original = artifact.read_bytes()
                artifact.write_bytes(original + b"\nchanged")
                with self.assertRaisesRegex(gate.GateError, "changed after owner exception"):
                    self.check()
                artifact.write_bytes(original)

    def test_owner_exception_requires_explicit_authorization(self):
        target = self.owner_exception()
        data = json.loads(target.read_text())
        data["authorization"] = "assumed"
        target.write_text(json.dumps(data))
        with self.assertRaisesRegex(gate.GateError, "site-owner authorization"):
            self.check()

    def test_owner_exception_cannot_be_reused_for_another_article(self):
        target = self.owner_exception()
        data = json.loads(target.read_text())
        data["slug"] = "another-article"
        target.write_text(json.dumps(data))
        with self.assertRaisesRegex(gate.GateError, "exception identity"):
            self.check()

    def test_owner_exception_does_not_allow_future_authorization(self):
        target = self.owner_exception()
        data = json.loads(target.read_text())
        data["authorized_at"] = "2999-01-01T00:00:00Z"
        target.write_text(json.dumps(data))
        with self.assertRaisesRegex(gate.GateError, "future"):
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

    def migration_fixture(self, kind="exact_duplicate", different=False):
        exception = self.owner_exception()
        old = self.root / "content/posts/old-model.md"
        original = self.post.read_bytes()
        if kind == "unfinished_placeholder":
            old.write_text("---\ntitle: Unfinished\n---\nThis is a placeholder post.\n")
        else:
            old.write_bytes(original + (b"\nDifferent material.\n" if different else b""))
        source = old.read_bytes()
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL).strip()
        git("init");git("config","user.email","fixture@example.invalid");git("config","user.name","Fixture")
        git("add",".");git("commit","-m","historical articles");base=git("rev-parse","HEAD")
        old.unlink()
        self.post.write_text(self.post.read_text().replace("draft: false", "draft: false\naliases: ['/posts/old-model/']"))
        data=json.loads(exception.read_text());data['article_sha256']=gate.digest(self.post.read_bytes());exception.write_text(json.dumps(data))
        migration=self.root/'quality/url-migrations/old-model.json';migration.parent.mkdir()
        record={'version':1,'slug':'old-model','destination_slug':self.slug,'kind':kind,
                'authorization':'explicit_site_owner_instruction','authorized_at':datetime.now(timezone.utc).isoformat(),
                'reason':'Owner requested consolidation preserving the old entry URL.',
                'source_commit':base,'source_article_sha256':gate.digest(source),'destination_before_sha256':gate.digest(original)}
        migration.write_text(json.dumps(record))
        return migration,exception,git,base

    def test_duplicate_migration_preserves_verified_destination_and_old_url(self):
        _,_,git,base=self.migration_fixture()
        result=gate.check(self.root,'old-model')
        self.assertEqual(result['destination_slug'],self.slug)
        self.assertEqual(result['review_basis'],'site_owner_url_migration')
        git('add','.');git('commit','-m','consolidate')
        self.assertIn('old-model',gate.changed_slugs(self.root,base))

    def test_unreviewed_deletion_still_blocks(self):
        migration,_,_,_=self.migration_fixture();migration.unlink()
        with self.assertRaisesRegex(gate.GateError,'separate migration review'):
            gate.check(self.root,'old-model')

    def test_placeholder_migration_requires_an_actual_short_placeholder(self):
        self.migration_fixture(kind='unfinished_placeholder')
        self.assertEqual(gate.check(self.root,'old-model')['status'],'pass')
        migration=self.root/'quality/url-migrations/old-model.json';data=json.loads(migration.read_text())
        data['kind']='exact_duplicate';migration.write_text(json.dumps(data))
        with self.assertRaisesRegex(gate.GateError,'not an exact duplicate'):
            gate.check(self.root,'old-model')

    def test_nonduplicate_cannot_use_duplicate_migration(self):
        self.migration_fixture(different=True)
        with self.assertRaisesRegex(gate.GateError,'not an exact duplicate'):
            gate.check(self.root,'old-model')

    def test_migration_rejects_missing_authority_and_tampered_history(self):
        migration,_,_,_=self.migration_fixture();original=json.loads(migration.read_text())
        for key,value,expected in [('authorization','assumed','site-owner'),('source_article_sha256','wrong','source hash'),('destination_before_sha256','wrong','history hash'),('source_commit','HEAD','source commit'),('authorized_at','2999-01-01T00:00:00Z','future')]:
            with self.subTest(key=key):
                data=dict(original);data[key]=value;migration.write_text(json.dumps(data))
                with self.assertRaisesRegex(gate.GateError,expected):gate.check(self.root,'old-model')
        migration.write_text(json.dumps(original))

    def test_migration_cannot_drop_alias_or_bypass_destination_review(self):
        self.migration_fixture();original=self.post.read_text()
        self.post.write_text(original.replace("aliases: ['/posts/old-model/']",'aliases: []'))
        with self.assertRaisesRegex(gate.GateError,'alias is missing'):gate.check(self.root,'old-model')
        self.post.write_text(original+'\nAn unreviewed new claim.\n')
        with self.assertRaisesRegex(gate.GateError,'changed after owner exception'):gate.check(self.root,'old-model')
        self.post.unlink()
        with self.assertRaisesRegex(gate.GateError,'surviving article'):gate.check(self.root,'old-model')

    def test_redirect_verification_rejects_wrong_destination_old_body_and_ads(self):
        self.migration_fixture();target=gate.SITE+'/posts/'+self.slug+'/'
        html=f'<html><head><link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}"></head><body><a href="{target}">Continue</a></body></html>'
        self.assertEqual(gate.page_fingerprint(self.root,'old-model',html)['kind'],'redirect')
        for bad,expected in [(html.replace(target,gate.SITE+'/posts/wrong/'),'canonical'),(html.replace('0; url=','3; url='),'immediately'),(html.replace('</body>','<div class="post-content">Old duplicate</div></body>'),'duplicate'),(html.replace('</body>','<script src="ads.js"></script></body>'),'scripts'),(html.replace('<a href=', '<span data-href=').replace('</a>','</span>'),'fallback')]:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(gate.GateError,expected):gate.page_fingerprint(self.root,'old-model',bad)

    def test_http_200_old_duplicate_fails_live_migration_verification(self):
        _,_,git,_=self.migration_fixture();git('add','.');git('commit','-m','consolidate');commit=git('rev-parse','HEAD')
        target=gate.SITE+'/posts/'+self.slug+'/'
        rendered=self.root/'public';p=rendered/'posts/old-model/index.html';p.parent.mkdir(parents=True)
        p.write_text(f'<link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}"><a href="{target}">Continue</a>')
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return b'<link rel="canonical" href="https://baeseokjae.github.io/posts/old-model/"><div class="post-content">Old article</div>'
        with patch.object(gate.urllib.request,'urlopen',return_value=Response()):
            with self.assertRaisesRegex(gate.GateError,'Redirect canonical'):
                gate.verify_live(self.root,'old-model',rendered,commit)


if __name__ == "__main__":
    unittest.main()
