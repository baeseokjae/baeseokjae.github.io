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
    if not (root / "content/posts" / f"{slug}.md").exists():
        return check_migration(root, slug)
    path, text, meta, body = read_post(root, slug)
    exception_path = root / "quality/publication-exceptions" / f"{slug}.json"
    if exception_path.exists():
        exception = json.loads(exception_path.read_text())
        require(exception.get("version") == 1 and exception.get("slug") == slug, "Invalid publication exception identity")
        require(exception.get("authorization") == "explicit_site_owner_instruction", "Publication exception needs site-owner authorization")
        require(bool(exception.get("reason")), "Publication exception needs a reason")
        reviewed_date(exception.get("authorized_at"), "authorized_at")
        require(exception.get("article_sha256") == digest(path.read_bytes()), "REVIEW_REQUIRED: article changed after owner exception")
        schema = root / "layouts/partials" / f"schema-{slug}.html"
        require(meta.get("draft") is False and meta.get("schema") == f"schema-{slug}", "Invalid publication metadata")
        require(schema.is_file() and exception.get("schema_sha256") == digest(schema.read_bytes()), "REVIEW_REQUIRED: schema changed after owner exception")
        cover = (meta.get("cover") or {}).get("image")
        require(isinstance(cover, str) and cover.startswith("/images/"), "Publication exception requires a pinned local cover")
        require(exception.get("cover_sha256") == digest(local_file(root, "static" + cover).read_bytes()), "REVIEW_REQUIRED: cover changed after owner exception")
        return {"slug": slug, "status": "pass", "review_basis": "site_owner_exception",
                "article_sha256": exception["article_sha256"], "exception_sha256": digest(exception_path.read_bytes())}
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


def check_migration(root, slug):
    """Accept only an owner-authorized, recoverable consolidation with an alias.

    This is a URL migration review, not a factual approval of the destination.
    The surviving article must independently pass the normal publication gate.
    """
    require(bool(SLUG.fullmatch(slug)), "Invalid migration slug")
    require(not (root / "content/posts" / f"{slug}.md").exists(), "Migration source is still an article")
    path = root / "quality/url-migrations" / f"{slug}.json"
    require(path.is_file(), f"Deleted article requires a separate migration review: {slug}")
    record = json.loads(path.read_text())
    require(record.get("version") == 1 and record.get("slug") == slug, "Invalid migration identity")
    require(record.get("authorization") == "explicit_site_owner_instruction", "Migration needs site-owner authorization")
    reviewed_date(record.get("authorized_at"), "migration authorized_at")
    require(bool(record.get("reason")), "Migration needs a reason")
    target = record.get("destination_slug", "")
    require(isinstance(target, str) and bool(SLUG.fullmatch(target)) and target != slug, "Invalid migration destination")
    require((root / "content/posts" / f"{target}.md").is_file(), "Migration destination must be a surviving article, not a redirect chain")
    _, _, meta, _ = read_post(root, target)
    require(meta.get("draft") is False and not meta.get("robotsNoIndex"), "Migration destination must remain published and indexable")
    aliases = meta.get("aliases", [])
    require(isinstance(aliases, list) and f"/posts/{slug}/" in aliases, "Migration alias is missing from destination")
    require(not meta.get("url") and not meta.get("canonicalURL"), "Migration destination must use its own post URL")
    commit = record.get("source_commit", "")
    require(isinstance(commit, str) and bool(re.fullmatch(r"[a-f0-9]{40}", commit)), "Invalid migration source commit")
    subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root, check=True, capture_output=True)
    def historical_article(name):
        return subprocess.check_output(["git", "show", f"{commit}:content/posts/{name}.md"], cwd=root)
    source = historical_article(slug)
    destination = historical_article(target)
    require(digest(source) == record.get("source_article_sha256"), "Migration source hash differs from recorded history")
    require(digest(destination) == record.get("destination_before_sha256"), "Migration destination history hash mismatch")
    body = lambda data: " ".join(data.decode().split("---\n", 2)[2].split())
    if record.get("kind") == "exact_duplicate":
        require(body(source) == body(destination), "Migration source was not an exact duplicate")
    elif record.get("kind") == "unfinished_placeholder":
        require("placeholder post" in body(source).lower() and len(body(source).split()) < 100,
                "Migration source was not the reviewed unfinished placeholder")
    else:
        raise GateError("Unsupported migration kind")
    check(root, target)
    return {"slug": slug, "status": "pass", "review_basis": "site_owner_url_migration",
            "destination_slug": target, "migration_sha256": digest(path.read_bytes())}


def changed_slugs(root, base, head="HEAD"):
    # Compare with the last pre-gate baseline, not HEAD^: a cancelled/failed
    # earlier push must not bypass review on a later unrelated successful push.
    paths = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", base, head, "--"], cwd=root, text=True).splitlines()
    slugs = set()
    for p in paths:
        m = re.fullmatch(r"content/posts/(.+)\.md|layouts/partials/schema-(.+)\.html|quality/reviews/(.+)\.json|quality/publication-exceptions/(.+)\.json|quality/url-migrations/(.+)\.json", p)
        if m:
            slugs.add(next(x for x in m.groups() if x))
        if p.startswith("static/images/"):
            image = "/" + p.removeprefix("static/")
            for post in (root / "content/posts").glob("*.md"):
                if image in post.read_text():
                    slugs.add(post.stem)
    for slug in slugs:
        if not (root / "content/posts" / f"{slug}.md").exists():
            check_migration(root, slug)
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


def page_fingerprint(root, slug, raw):
    """Validate the expected URL semantics for articles and reviewed redirects."""
    migration_path = root / "quality/url-migrations" / f"{slug}.json"
    if not migration_path.exists():
        result = html_fingerprint(raw)
        require(result["canonical"] == f"{SITE}/posts/{slug}/", "Unexpected canonical URL")
        return result
    migration = check_migration(root, slug)
    target = f"{SITE}/posts/{migration['destination_slug']}/"
    soup = BeautifulSoup(raw, "html.parser")
    canonical = soup.select_one('link[rel="canonical"]')
    refresh = soup.find("meta", attrs={"http-equiv": re.compile(r"^refresh$", re.I)})
    require(canonical is not None and canonical.get("href") == target, "Redirect canonical differs from reviewed destination")
    require(refresh is not None and re.fullmatch(r"0\s*;\s*url\s*=\s*" + re.escape(target), refresh.get("content", ""), re.I),
            "Redirect must immediately refresh to the reviewed destination")
    require(soup.select_one(".post-content") is None, "Redirect still publishes duplicate article content")
    require(not soup.find_all("script"), "Redirect must not load scripts (ads, tracking, or article schema)")
    require(soup.find("a", href=target) is not None, "Redirect needs a fallback destination link")
    return {"kind": "redirect", "canonical": target, "refresh": refresh["content"],
            "body": digest(" ".join(soup.get_text(" ", strip=True).split())),
            "links": sorted(a.get("href") for a in soup.select("a[href]"))}


def verify_live(root, slug, rendered, commit):
    validation = check(root, slug)
    is_migration = validation.get("review_basis") == "site_owner_url_migration"
    rel = f"quality/url-migrations/{slug}.json" if is_migration else f"content/posts/{slug}.md"
    committed = subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=root)
    require(digest(committed) == digest((root / rel).read_bytes()), "Local article or migration differs from intended commit")
    expected = page_fingerprint(root, slug, (rendered / "posts" / slug / "index.html").read_text())
    url = f"{SITE}/posts/{slug}/"
    req = urllib.request.Request(url + "?verify=" + commit[:12], headers={"Cache-Control": "no-cache", "User-Agent": "RockB-publication-verification/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        require(response.status == 200, "Live URL is not HTTP 200")
        actual = page_fingerprint(root, slug, response.read().decode())
    for field in expected:
        require(actual[field] == expected[field], f"LIVE_MISMATCH: {field} differs from reviewed build for {slug}")
    result = {"slug": slug, "status": "pass", "url": url, "commit": commit,
            "artifact_sha256": digest((root / rel).read_bytes()), "body_sha256": actual["body"],
            "kind": "redirect" if is_migration else "article", "checked_at": datetime.now(timezone.utc).isoformat()}
    result["migration_sha256" if is_migration else "article_sha256"] = result["artifact_sha256"]
    return result


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
