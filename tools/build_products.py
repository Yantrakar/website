#!/usr/bin/env python3
"""Fill the Products section of the site from GitHub.

Public repos in the org that carry the topic set in products.json are picked
up automatically: description, homepage and latest release. Entries in
products.json add or override fields, and can list products that are not
public repos (yet). An entry with "tagline_from" takes its text from that
live site (meta description, og:description, or its lead paragraph), so the
tile always says what the product's own site says. The tiles are written between these markers:

    <!-- products:start -->  ...  <!-- products:end -->

Stdlib only. Uses GITHUB_TOKEN when set (GitHub Actions), anonymous otherwise.
If GitHub cannot be reached the page is left as it is, so a deploy never
publishes an empty Products section.
"""
from __future__ import annotations

import html
import json
from html.parser import HTMLParser
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "products.json"
TARGETS = [ROOT / "index.html"]
START, END = "<!-- products:start -->", "<!-- products:end -->"
API = "https://api.github.com"


def gh(path: str):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "yantrakar-site-products",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


class _Tagline(HTMLParser):
    """Pick a site's own one-liner: meta description, og:description, then
    the lead paragraph (p.lead, or the first <p> after the first <h1>)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang, self.meta, self.og, self.lead = "", "", "", ""
        self._h1_seen, self._in_p, self._buf, self._lead_is_class = False, False, [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key == "description" and not self.meta:
                self.meta = a.get("content", "")
            elif key == "og:description" and not self.og:
                self.og = a.get("content", "")
        elif tag == "h1":
            self._h1_seen = True
        elif tag == "p" and not self.lead:
            is_lead = "lead" in (a.get("class") or "").split()
            if is_lead or self._h1_seen:
                self._in_p, self._buf, self._lead_is_class = True, [], is_lead

    def handle_data(self, data):
        if self._in_p:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self._in_p:
            self._in_p = False
            self.lead = " ".join("".join(self._buf).split())

    def best(self) -> str:
        return " ".join((self.meta or self.og or self.lead).split())


def site_tagline(url: str) -> tuple[str, str] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "yantrakar-site-products"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            page = r.read(512_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception as exc:
        print(f"products: could not read tagline from {url} ({exc}); using products.json text", file=sys.stderr)
        return None
    parser = _Tagline()
    parser.feed(page)
    text = parser.best()
    return (text, parser.lang) if text else None


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def tagged_repos(org: str, topic: str) -> dict[str, dict]:
    repos, page = {}, 1
    while True:
        batch = gh(f"/orgs/{org}/repos?type=public&per_page=100&page={page}") or []
        for r in batch:
            if topic in (r.get("topics") or []) and not r.get("archived"):
                rel = gh(f"/repos/{org}/{r['name']}/releases/latest")
                r["_release"] = rel
                repos[r["name"]] = r
        if len(batch) < 100:
            return repos
        page += 1


def merge(cfg: dict, repos: dict[str, dict]) -> list[dict]:
    items, used = [], set()
    auto = sorted(repos.values(), key=lambda r: r.get("pushed_at") or "", reverse=True)
    for entry in cfg.get("products", []):
        repo = repos.get(entry.get("repo", ""))
        if entry.get("repo"):
            used.add(entry["repo"])
        items.append(fill(dict(entry), repo))
    for r in auto:
        if r["name"] not in used:
            items.append(fill({"repo": r["name"], "name": r["name"], "tag": "OPEN SOURCE"}, r))
    return items


def fill(entry: dict, repo: dict | None) -> dict:
    if repo:
        entry.setdefault("text", repo.get("description") or "")
        if "links" not in entry:
            links = []
            if repo.get("homepage"):
                host = re.sub(r"^https?://", "", repo["homepage"]).rstrip("/")
                links.append({"label": host, "url": repo["homepage"]})
            links.append({"label": "GitHub", "url": repo["html_url"]})
            entry["links"] = links
        rel = repo.get("_release")
        if rel and rel.get("tag_name") and entry.get("show_release", True):
            entry["release"] = {"label": rel["tag_name"], "url": rel["html_url"]}
    if entry.get("tagline_from"):
        got = site_tagline(entry["tagline_from"])
        if got:
            entry["text"], entry["lang"] = got
    entry.setdefault("id", slug(entry.get("repo") or entry["name"]))
    return entry


def render(items: list[dict]) -> str:
    e = lambda s: html.escape(str(s), quote=True)
    cols = "tiles tiles-2" if len(items) in (2, 4) else "tiles"
    out = [f'<div class="{cols}">']
    for it in items:
        out.append(f'<div class="panel tile" id="{e(it["id"])}">')
        if it.get("tag"):
            out.append(f'<span class="tag tag-accent">{e(it["tag"])}</span>')
        out.append(f'<h3>{e(it["name"])}</h3>')
        if it.get("text"):
            lang = f' lang="{e(it["lang"])}"' if it.get("lang") else ""
            out.append(f'<p{lang}>{e(it["text"])}</p>')
        out.append('<div class="tile-foot">')
        if it.get("install"):
            out.append(f'<p class="term"><code><span class="prompt">$</span> {e(it["install"])}</code></p>')
        links = list(it.get("links", []))
        if it.get("release"):
            links.append({"label": f'Release {it["release"]["label"]}', "url": it["release"]["url"]})
        if links:
            a = " ".join(f'<a href="{e(l["url"])}" rel="noopener">{e(l["label"])} →</a>' for l in links)
            out.append(f'<p class="tile-links">{a}</p>')
        out.append("</div>")
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        repos = tagged_repos(cfg["org"], cfg["topic"])
    except Exception as exc:  # network, rate limit, ...
        print(f"products: GitHub not reachable ({exc}); leaving pages unchanged", file=sys.stderr)
        return 0
    block = render(merge(cfg, repos))
    for path in TARGETS:
        page = path.read_text(encoding="utf-8")
        pat = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        if not pat.search(page):
            print(f"products: markers missing in {path}", file=sys.stderr)
            return 1
        new = pat.sub(lambda _: f"{START}\n{block}\n{END}", page)
        if new != page:
            path.write_text(new, encoding="utf-8")
            print(f"products: updated {path.relative_to(ROOT)} ({len(repos)} tagged repos)")
        else:
            print(f"products: {path.relative_to(ROOT)} already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
