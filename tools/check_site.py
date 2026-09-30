"""Check current website/docs links, exact path case, anchors and media data.

Uses only the standard library. Frozen experimental trees are read-only targets;
their historical preparation prose is not treated as current navigation.
This is an offline check, not a claim that third-party servers are reachable.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import argparse
import json
import posixpath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://roboplanner.github.io/atg-repair-planning/'
GH = 'https://github.com/RoboPlanner/atg-repair-planning/'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.duplicates, self.images_without_alt = [], set(), [], 0
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.duplicates.append(attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'img' and 'alt' not in attrs:
            self.images_without_alt += 1
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.links.append(attrs[key])


def check():
    issues, checked, external = [], [], set()
    pages = {p.relative_to(ROOT).as_posix(): Page(p.read_text('utf-8'))
             for p in (ROOT / 'docs').glob('*.html')}

    def issue(source, url, reason):
        issues.append({'source': source, 'target': url, 'reason': reason})

    def link(source, url):
        u = urlparse(url)
        if u.scheme in ('mailto', 'data', 'javascript'):
            return
        target = None
        fragment = unquote(u.fragment)
        if url.startswith(SITE):
            target = 'docs/' + unquote(u.path.removeprefix('/atg-repair-planning/'))
        elif url.startswith(GH + 'blob/main/') or url.startswith(GH + 'tree/main/'):
            target = unquote(re.sub(r'^/RoboPlanner/atg-repair-planning/(blob|tree)/main/', '', u.path))
        elif u.scheme or u.netloc:
            if u.hostname in ('localhost', '127.0.0.1', '::1'):
                issue(source, url, 'loopback URL used as a public link')
            else:
                external.add(url)
            return
        else:
            target = posixpath.join(posixpath.dirname(source), unquote(u.path)) if u.path else source
        target = posixpath.normpath(target)
        if target.startswith('../') or target.startswith('/'):
            issue(source, url, 'link escapes the repository')
            return
        actual = ROOT
        for part in target.split('/'):
            if not actual.is_dir() or part not in {p.name for p in actual.iterdir()}:
                issue(source, url, 'missing target or wrong path case')
                return
            actual = actual / part
        if actual.is_dir() and (actual / 'index.html').is_file():
            actual = actual / 'index.html'
            target += '/index.html'
        if fragment and actual.suffix == '.html':
            doc = pages.get(target) or Page(actual.read_text('utf-8'))
            if fragment not in doc.ids:
                issue(source, url, 'missing HTML anchor')
        if fragment and actual.suffix == '.md':
            headings = re.findall(r'^#{1,6}\s+(.+)$', actual.read_text('utf-8'), re.M)
            slugs = {re.sub(r'[^\w\- ]', '', h.strip().lower()).replace(' ', '-') for h in headings}
            if fragment not in slugs:
                issue(source, url, 'missing Markdown heading anchor')
        checked.append(target)

    for name, page in pages.items():
        for href in page.links:
            link(name, href)
        for repeated in page.duplicates:
            issue(name, '#' + repeated, 'duplicate HTML id')
        if page.images_without_alt:
            issue(name, '', 'image missing alternative text')
        if any('/papers/' in h for h in page.links):
            issue(name, '', 'paper navigation is temporarily disabled')

    markdown = list(ROOT.glob('*.md')) + list((ROOT / 'documentation').glob('*.md')) + list((ROOT / 'docs/assets/downloads').glob('*.md')) + list((ROOT / 'translations/en').rglob('*.md'))
    for p in markdown:
        name = p.relative_to(ROOT).as_posix()
        text = p.read_text('utf-8')
        # Exclude code examples: loopback addresses are legitimate preview instructions.
        prose = re.sub(r'```.*?```', '', text, flags=re.S)
        for demo in re.findall(r'https?://(?:127\.0\.0\.1|localhost)(?::\d+)?/#[\w-]+', prose):
            issue(name, demo, 'demo navigation must use the public project address')
        for href in re.findall(r'\]\(([^\n)]+)\)', prose):
            link(name, href)
            if '/papers/' in href:
                issue(name, href, 'paper navigation is temporarily disabled')

    for p in (ROOT / 'docs/assets').glob('*.css'):
        for href in re.findall(r'url\([\s\"\']*([^\)\"\']+)', p.read_text('utf-8')):
            link(p.relative_to(ROOT).as_posix(), href.strip())

    # Dynamic player media paths are resolved from index.html, not from the JSON folder.
    def media(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k in ('src', 'poster', 'svg') and isinstance(v, str) and v.startswith('assets/'):
                    link('docs/index.html', v)
                else:
                    media(v)
        elif isinstance(value, list):
            for v in value:
                media(v)
    for p in (ROOT / 'docs/assets/data').glob('*.json'):
        media(json.loads(p.read_text('utf-8')))
    for n in range(1, 5):
        link('docs/index.html', f'assets/images/figure{n}.png')
    mapping = json.loads((ROOT / 'docs/assets/data/manuscript-map.json').read_text('utf-8'))
    for row in mapping['tables']:
        link('README.md', row['source'])
    for row in mapping['figures']:
        link('docs/index.html', row['asset'])
    return {'checked_references': len(checked), 'unique_targets': len(set(checked)),
            'html_pages': len(pages), 'markdown_files': len(markdown),
            'external_urls_not_network_checked': sorted(external), 'issues': issues}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='Optionally save the detailed report')
    args = parser.parse_args()
    report = check()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if report['issues']:
        print(json.dumps(report['issues'], ensure_ascii=False, indent=2))
        sys.exit(1)
    print(f"PASS: {report['checked_references']} references, {report['unique_targets']} targets; "
          f"{report['html_pages']} HTML pages and {report['markdown_files']} Markdown files. "
          'Third-party HTTP availability is not checked by this offline command.')
