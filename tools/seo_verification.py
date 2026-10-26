"""Exact rendered/public comparisons for explicitly selected non-article URLs.

Length is not a pass criterion. Main HTML (including links and images), title,
canonical, robots, description and Open Graph/Twitter metadata are compared.
"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from publication_gate import GateError, SITE


def checked_path(value):
    if not isinstance(value, str) or not value.startswith('/') or not value.endswith('/'):
        raise GateError('SEO URL must be an absolute site path ending in /')
    parsed = urlsplit(value)
    decoded = unquote(value)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or
            decoded != value or '\\' in value or '//' in value or
            any(p in ('.', '..') for p in value.split('/')) or
            not re.fullmatch(r'/[a-zA-Z0-9_./-]*', value)):
        raise GateError('Unsafe SEO verification path')
    return value


def rendered_file(rendered, path):
    path = checked_path(path)
    root = Path(rendered).resolve()
    target = (root / path.lstrip('/') / 'index.html').resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise GateError('SEO rendered file missing or escaped root')
    return target


def fingerprint(raw, path):
    checked_path(path)
    soup = BeautifulSoup(raw, 'html.parser')
    selectors = {'title': 'head title', 'description': 'head meta[name="description"]',
                 'robots': 'head meta[name="robots"]', 'canonical': 'head link[rel="canonical"]'}
    result = {}
    for name, selector in selectors.items():
        nodes = soup.select(selector)
        if len(nodes) != 1:
            raise GateError('SEO metadata must occur exactly once: ' + name)
        value = (nodes[0].get_text() if name == 'title' else
                 nodes[0].get('href' if name == 'canonical' else 'content', ''))
        if not value.strip():
            raise GateError('Empty SEO metadata: ' + name)
        result[name] = value
    if result['canonical'] != SITE + path:
        raise GateError('Unexpected SEO canonical')
    if soup.select('meta[http-equiv="refresh"]'):
        raise GateError('SEO verification does not permit redirects')
    main = soup.select('main')
    if len(main) != 1:
        raise GateError('Expected one main body')
    result['main_sha256'] = hashlib.sha256(str(main[0]).encode()).hexdigest()
    result['social'] = sorted((m.get('property', m.get('name', '')), m.get('content', ''))
        for m in soup.select('head meta')
        if m.get('property', '').startswith('og:') or m.get('name', '').startswith('twitter:'))
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GateError('SEO live redirect rejected')


def fetch_live(path, commit):
    path = checked_path(path)
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise GateError('Invalid source commit')
    request = urllib.request.Request(SITE + path + '?verify=' + commit[:12], headers={
        'Cache-Control': 'no-cache', 'User-Agent': 'RockB-seo-verification/1.0',
        'Accept-Encoding': 'identity'})
    opener = urllib.request.build_opener(NoRedirect())
    started = time.monotonic()
    with opener.open(request, timeout=20) as response:
        if response.status != 200:
            raise GateError('SEO URL unavailable')
        size = 0; parts = []
        while True:
            part = response.read1(65536)
            if not part:
                break
            size += len(part)
            if size > 8_000_000 or time.monotonic() - started > 30:
                raise GateError('SEO response exceeded bounds')
            parts.append(part)
        return b''.join(parts).decode('utf-8')


def selected_paths(root, rendered, changes):
    """Stable site pages plus explicit representative/changed taxonomy pages."""
    root = Path(root); rendered = Path(rendered)
    config = json.loads((root / 'quality/seo-verification.json').read_text())
    if config.get('version') != 1:
        raise GateError('Unsupported SEO verification configuration')
    paths = set(config['paths'])
    tree = ET.parse(rendered / 'sitemap-pages.xml')
    for loc in tree.findall('.//{*}loc'):
        value = urlsplit(loc.text)
        if value.scheme != 'https' or value.netloc != urlsplit(SITE).netloc or value.query or value.fragment:
            raise GateError('Non-site URL in pages sitemap')
        paths.add(checked_path(value.path))
    for change in changes:
        match = re.fullmatch(r'content/(tags|categories)/([a-zA-Z0-9_-]+)/_index\.md', change)
        if match:
            paths.add('/' + match[1] + '/' + match[2] + '/')
    if len(paths) > 50:
        raise GateError('SEO URL selection requires explicit review above 50 URLs')
    for path in paths:
        rendered_file(rendered, path)
    return sorted(paths)


def verify_paths(rendered, paths, commit):
    evidence = []
    for path in paths:
        expected = fingerprint(rendered_file(rendered, path).read_text(), path)
        actual = fingerprint(fetch_live(path, commit), path)
        if expected != actual:
            fields = sorted(k for k in expected if expected[k] != actual[k])
            raise GateError('SEO public mismatch: ' + path + ' fields=' + ','.join(fields))
        evidence.append({'url': SITE + path, 'fingerprint': expected,
                         'description_length': len(actual['description']),
                         'length_policy': 'informational_only'})
    return evidence
