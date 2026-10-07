#!/usr/bin/env python3
"""Require evidence tied to the exact article before publication.

This checks evidence completeness and content identity, not the truth of a
source. A separate source review remains necessary. No command creates an
approved review, publishes a page, or changes a task's status.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://baeseokjae.github.io"
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
CHECKS = {"numbers", "model_ids", "pricing", "dates_versions", "benchmarks", "sponsorship", "cover"}
KINDS = {"source", "calculation", "procedure", "correction", "scope", "first_party_test"}
FIRST_PARTY = re.compile(r"\b(?:we\s+(?:tested|benchmarked|measured)|our\s+(?:tests|benchmarks|measurements))\b", re.I)
RISK = re.compile(r"\d|[$€£%]|\b(?:SOC\s*2|HIPAA|GDPR|tested|benchmark|guarantee)\b", re.I)


class GateError(ValueError):
    pass


def digest(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise GateError(message)


def read_post(root, slug):
    require(bool(SLUG.fullmatch(slug)), "Invalid slug")
    path = root / "content/posts" / f"{slug}.md"
    text = path.read_text()
    require(text.startswith("---\n"), "Missing YAML front matter")
    _, front, body = text.split("---\n", 2)
    meta = yaml.safe_load(front)
    require(isinstance(meta, dict), "Invalid front matter")
    return path, text, meta, body


def risk_blocks(meta, body):
    blocks = [f"TITLE: {meta.get('title', '')}\nDESCRIPTION: {meta.get('description', '')}"]
    blocks += [x.strip() for x in re.split(r"\n\s*\n", body.strip()) if x.strip()]
    result = []
    for block in blocks:
        without_urls = re.sub(r"https?://[^\s)<>]+", "", block)
        if block == blocks[0] or RISK.search(without_urls) or FIRST_PARTY.search(block):
            result.append({"sha256": digest(block), "text": block})
    return result


def local_file(root, rel):
    require(isinstance(rel, str) and rel, "Missing evidence path")
    p = (root / rel).resolve()
    require(p.is_relative_to(root.resolve()), "Evidence path leaves repository")
    require(p.is_file(), f"Evidence file missing: {rel}")
    return p


def reviewed_date(value, label):
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(d.tzinfo is not None, f"{label} needs a timezone")
        require(d <= datetime.now(timezone.utc), f"{label} is in the future")
    except (TypeError, AttributeError, ValueError) as exc:
        raise GateError(f"Invalid {label}: {exc}") from exc


def check(root, slug):
    path, text, meta, body = read_post(root, slug)
    receipt_path = root / "quality/reviews" / f"{slug}.json"
    require(receipt_path.exists(), f"REVIEW_REQUIRED: missing {receipt_path.relative_to(root)}")
    receipt = json.loads(receipt_path.read_text())
    require(receipt.get("version") == 1 and receipt.get("slug") == slug, "Invalid receipt identity")
    require(receipt.get("status") == "approved", "REVIEW_REQUIRED: review is not approved")
    require(bool(receipt.get("reviewer")), "Missing reviewer")
    require(receipt.get("article_sha256") == digest(path.read_bytes()), "REVIEW_REQUIRED: article changed after review")
    reviewed_date(receipt.get("reviewed_at"), "reviewed_at")
    require(meta.get("draft") is False, "Draft must explicitly be false")
    require(meta.get("schema") == f"schema-{slug}", "Missing expected schema reference")
    schema = root / "layouts/partials" / f"schema-{slug}.html"
    require(schema.is_file(), "Missing schema")
    require(receipt.get("schema_sha256") == digest(schema.read_bytes()), "REVIEW_REQUIRED: schema changed after review")
    entries = [json.loads(x) for x in re.findall(r'<script[^>]*>(.*?)</script>', schema.read_text(), re.S)]
    articles = [x for x in entries if x.get("@type") in ("Article", "BlogPosting")]
    require(bool(articles), "No Article schema")
    for article in articles:
        require(article.get("headline") == meta.get("title"), "Schema title mismatch")
        require(article.get("description") == meta.get("description"), "Schema description mismatch")
    cover = (meta.get("cover") or {}).get("image")
    if cover:
        require(cover.startswith("/images/"), "Review expects a local cover")
        cover_path = local_file(root, "static" + cover)
        require(receipt.get("cover_sha256") == digest(cover_path.read_bytes()), "REVIEW_REQUIRED: cover changed after review")
    checks = receipt.get("checks", {})
    require(CHECKS <= checks.keys(), "Missing required review checks")
    for name in CHECKS:
        item = checks[name]
        require(item.get("status") in ("pass", "not_applicable") and bool(item.get("note")), f"Unresolved check: {name}")
    sources = receipt.get("sources", [])
    require(bool(sources), "Missing primary sources")
    ids = set()
    for source in sources:
        require(source.get("id") and source["id"] not in ids, "Duplicate or empty source ID")
        ids.add(source["id"])
        url = source.get("url", "")
        require(urlsplit(url).scheme == "https" and bool(urlsplit(url).hostname), "Source needs HTTPS URL")
        require(url in body, f"Source is not linked in article: {url}")
        require(source.get("type") == "primary", "Primary source review required")
        reviewed_date(source.get("checked_at"), "source checked_at")
    reviewed = {x.get("sha256"): x for x in receipt.get("claims", [])}
    for block in risk_blocks(meta, body):
        item = reviewed.get(block["sha256"])
        require(item is not None, f"REVIEW_REQUIRED: uncovered claim block {block['sha256'][:12]}: {block['text'][:90]}")
        kind = item.get("kind")
        require(kind in KINDS and len(item.get("note", "").strip()) >= 12, "Claim needs a review classification and rationale")
        references = item.get("source_ids", [])
        require(all(x in ids for x in references), "Claim refers to unknown source")
        if kind == "source":
            require(bool(references), "Factual claim needs a primary source")
        if FIRST_PARTY.search(block["text"]) and kind not in ("correction", "scope"):
            require(kind == "first_party_test", "First-party test claim needs original run evidence")
        if kind == "first_party_test":
            run = item.get("run", {})
            evidence = local_file(root, run.get("path"))
            require(digest(evidence.read_bytes()) == run.get("sha256"), "Run evidence hash mismatch")
            require(bool(run.get("methodology")), "Run evidence needs methodology")
    commercial = receipt.get("commercial")
    require(isinstance(commercial, dict) and isinstance(commercial.get("paid"), bool), "Explicit commercial review required")
    if commercial["paid"]:
        disclosure = commercial.get("disclosure_text", "")
        require(disclosure and disclosure in body, "Paid placement disclosure missing from body")
        links = commercial.get("links", [])
        require(bool(links), "Paid placement destinations missing")
        soup = BeautifulSoup(body, "html.parser")
        for url in links:
            anchors = soup.find_all("a", href=url)
            require(anchors and all(set(x.get("rel", [])) & {"sponsored", "nofollow"} for x in anchors), "Paid link requires sponsored/nofollow HTML attribute")
    return {"slug": slug, "status": "pass", "claim_blocks": len(risk_blocks(meta, body)), "article_sha256": receipt["article_sha256"]}


def changed_slugs(root, base, head="HEAD"):
    # Compare with the last pre-gate baseline, not HEAD^: a cancelled/failed
    # earlier push must not bypass review on a later unrelated successful push.
    paths = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", base, head, "--"], cwd=root, text=True).splitlines()
    slugs = set()
    for p in paths:
        m = re.fullmatch(r"content/posts/(.+)\.md|layouts/partials/schema-(.+)\.html|quality/reviews/(.+)\.json", p)
        if m:
            slugs.add(next(x for x in m.groups() if x))
        if p.startswith("static/images/"):
            image = "/" + p.removeprefix("static/")
            for post in (root / "content/posts").glob("*.md"):
                if image in post.read_text():
                    slugs.add(post.stem)
    for slug in slugs:
        require((root / "content/posts" / f"{slug}.md").exists(), f"Deleted article requires a separate migration review: {slug}")
    return sorted(slugs)


def html_fingerprint(raw):
    soup = BeautifulSoup(raw, "html.parser")
    content = soup.select_one(".post-content")
    require(content is not None, "Live article body missing")
    canonical = soup.select_one('link[rel="canonical"]')
    title = soup.select_one("h1")
    description = soup.select_one('meta[name="description"]')
    require(canonical is not None and title is not None and description is not None, "Live metadata missing")
    schemas = [json.loads(s.string or s.get_text()) for s in soup.select('script[type="application/ld+json"]')]
    return {"canonical": canonical["href"], "title": title.get_text(" ", strip=True),
            "description": description["content"],
            "body": digest(" ".join(content.get_text(" ", strip=True).split())),
            "links": sorted((a.get("href"), tuple(a.get("rel", []))) for a in content.select("a[href]")),
            "schemas": digest(json.dumps(schemas, sort_keys=True, ensure_ascii=False)),
            "image": str(soup.select_one('meta[property="og:image"]'))}


def verify_live(root, slug, rendered, commit):
    check(root, slug)
    post, text, _, _ = read_post(root, slug)
    committed = subprocess.check_output(["git", "show", f"{commit}:content/posts/{slug}.md"], cwd=root)
    require(digest(committed) == digest(post.read_bytes()), "Local article differs from intended commit")
    expected = html_fingerprint((rendered / "posts" / slug / "index.html").read_text())
    url = f"{SITE}/posts/{slug}/"
    req = urllib.request.Request(url + "?verify=" + commit[:12], headers={"Cache-Control": "no-cache", "User-Agent": "RockB-publication-verification/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        require(response.status == 200, "Live URL is not HTTP 200")
        actual = html_fingerprint(response.read().decode())
    require(actual["canonical"] == url, "Unexpected canonical URL")
    for field in expected:
        require(actual[field] == expected[field], f"LIVE_MISMATCH: {field} differs from reviewed build for {slug}")
    return {"slug": slug, "status": "pass", "url": url, "commit": commit, "article_sha256": digest(post.read_bytes()), "body_sha256": actual["body"], "checked_at": datetime.now(timezone.utc).isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inventory", "check", "changed", "verify-live"])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--slug")
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--rendered", type=Path)
    parser.add_argument("--commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "changed":
            policy = json.loads((args.root / "quality/policy.json").read_text())
            slugs = changed_slugs(args.root, args.base or policy["baseline_commit"], args.head)
            result = [check(args.root, s) for s in slugs]
        else:
            require(bool(args.slug), "--slug is required")
            if args.command == "inventory":
                _, _, meta, body = read_post(args.root, args.slug)
                result = {"slug": args.slug, "status": "review_required", "claim_blocks": risk_blocks(meta, body)}
            elif args.command == "check":
                result = check(args.root, args.slug)
            else:
                require(args.rendered is not None and bool(args.commit), "--rendered and --commit are required")
                result = verify_live(args.root, args.slug, args.rendered, args.commit)
        output = json.dumps({"status": "pass", "result": result}, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output)
        print(output)
    except (GateError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "review_required", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
