#!/usr/bin/env python3
"""Build an article page from its Markdown.

The Markdown file is the source, and it is also published as it is, for
readers and machines (llms.txt points to it). Its figures are Mermaid
diagrams; on the page each one is drawn as an inline SVG instead, taken from
tools/article_figs/<slug>/figNN.svg (a wide and a narrow variant, each with
<title> and <desc>). The page keeps its own header, contact form and footer;
the article is written between these markers, and the head metadata is filled
from the front matter:

    <!-- article:start -->  ...  <!-- article:end -->

The Markdown is a small subset: front matter, one # title and a lead
paragraph, ## sections, paragraphs, - and 1. lists, **bold**, [links](url),
one table, and figures. A figure is a caption paragraph that starts with
"**Fig. NN · Title.**" followed by a mermaid block, or "**Table · Title.**"
followed by a table and a "Source:" paragraph. A bold table row is
highlighted.

    python3 tools/build_article.py          write the pages
    python3 tools/build_article.py --check  fail if a page is out of date

Stdlib only.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "tools" / "article_figs"
SITE = "https://yantrakar.com/"
START, END = "<!-- article:start -->", "<!-- article:end -->"

ARTICLES = [{
    "slug": "running-ai-inside-your-network",
    "eyebrow": "FIELD NOTES · PRIVATE AI",
    "place": "Stavanger",
    # One entry per ## section, in order: (id, label in the page index).
    "sections": [("short", "In short"), ("why", "Why"), ("models", "Models"), ("limits", "Limits"),
                 ("start", "Start"), ("comments", "Comments"), ("consider", "Steps")],
}, {
    "slug": "self-replication-network-boundary",
    "eyebrow": "FIELD NOTES · AI SAFETY",
    "place": "Stavanger",
    "full_title": True,  # <title> keeps the whole headline, not only the part before the colon
    "sections": [("measured", "Research"), ("slow", "Speed"), ("chain", "Controls"), ("steps", "Steps")],
}]

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
FIG_RE = re.compile(r"^\*\*Fig\. (\d\d) · (.+?)\.\*\* (.+)$")
TABLE_RE = re.compile(r"^\*\*Table · (.+?)\.\*\* (.+)$")


class BuildError(Exception):
    pass


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise BuildError("no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        meta[k.strip()] = json.loads(v) if v.startswith('"') else v
    return meta, text[m.end():]


def blocks(body: str) -> list[tuple[str, object]]:
    """Split the body into (kind, data) blocks."""
    out, lines, i = [], body.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            lang, i, code = line[3:].strip(), i + 1, []
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append(("code", (lang, "\n".join(code))))
            i += 1
        elif line.startswith("# "):
            out.append(("h1", line[2:]))
            i += 1
        elif line.startswith("## "):
            out.append(("h2", line[3:]))
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(("table", rows))
        elif re.match(r"(- |\d+\. )", line):
            kind = "ul" if line.startswith("- ") else "ol"
            items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            out.append((kind, items))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|```|\||- |\d+\. )", lines[i]):
                para.append(lines[i])
                i += 1
            out.append(("p", " ".join(para)))
    return out


def inline(text: str) -> str:
    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(SITE):
            href = url[len(SITE):]
            # A link to the page itself becomes a link to the anchor.
            href = re.sub(r"^[\w-]+\.html(?=#)", lambda h: "" if h.group(0) == PAGE else h.group(0), href)
            return f'<a href="{href}">{label}</a>'
        return f'<a href="{url}" rel="noopener">{label}</a>'
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
    return t


def plain(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text.replace("**", ""))


def figure_svg(slug: str, no: str, ids: set) -> str:
    path = FIGS / slug / f"fig{no}.svg"
    if not path.exists():
        raise BuildError(f"Fig. {no}: {path.relative_to(ROOT)} is missing")
    svg = path.read_text().strip()
    for variant in ("wv", "nv"):
        if not re.search(rf'<svg class="{variant} sw"[^>]*role="img"', svg):
            raise BuildError(f"Fig. {no}: no {variant} variant with role=img")
    if svg.count("<title") != 2 or svg.count("<desc") != 2:
        raise BuildError(f"Fig. {no}: each variant needs one <title> and one <desc>")
    for i in re.findall(r'\bid="([^"]+)"', svg):
        if i in ids:
            raise BuildError(f"Fig. {no}: id {i} is used twice on the page")
        ids.add(i)
    return svg


def render(art: dict, meta: dict, bl: list) -> tuple[str, str]:
    """Return (article html, description) for the page."""
    slug, ids, parts, sections = art["slug"], set(), [], list(art["sections"])
    if [k for k, _ in bl[:2]] != ["h1", "p"]:
        raise BuildError("the body must start with the # title and a lead paragraph")
    if sum(k == "h2" for k, _ in bl) != len(sections):
        raise BuildError("the number of ## sections differs from ARTICLES[...]['sections']")
    if bl[0][1] != meta["title"]:
        raise BuildError("the # title differs from the front matter title")
    y, m, d = meta["date"][:10].split("-")
    index = " ".join(
        f'<span class="pi"><a href="#{sid}">{n:02d} {html.escape(label)}</a>'
        + (' <span aria-hidden="true">·</span>' if n < len(sections) else "") + "</span>"
        for n, (sid, label) in enumerate(sections, 1))
    parts.append(f'''<section class="hero" aria-labelledby="hero-h">
<div class="wrap">
<div class="hero-text">
<p class="eyebrow">{art["eyebrow"]}</p>
<h1 id="hero-h">{inline(meta["title"])}</h1>
<p class="lead">{inline(bl[1][1])}</p>
<p class="mono-line">{html.escape(meta["author"])} · {art["place"]} · <time datetime="{meta["date"]}">{int(d)} {MONTHS[int(m) - 1]} {y}</time></p>
<nav class="page-index" aria-label="On this page">{index}</nav>
</div>
</div>
</section>''')
    i, open_sec = 2, False
    while i < len(bl):
        kind, data = bl[i]
        if kind == "h2":
            if open_sec:
                parts.append("</div>\n</section>")
            sid, _ = sections.pop(0)
            parts.append(f'<section class="sec" id="{sid}" aria-labelledby="{sid}-h">\n'
                         f'<div class="wrap stack art">\n<h2 id="{sid}-h">{inline(data)}</h2>')
            open_sec = True
        elif kind == "p" and FIG_RE.match(data):
            no, title, caption = FIG_RE.match(data).groups()
            if i + 1 >= len(bl) or bl[i + 1][0] != "code" or bl[i + 1][1][0] != "mermaid":
                raise BuildError(f"Fig. {no}: a mermaid block must follow the caption")
            parts.append(f'<figure class="fig">\n<div class="fig-head"><span class="fig-no">FIG. {no}</span>'
                         f'<span class="fig-title">{html.escape(title.upper())}</span></div>\n'
                         f'<div class="fig-body cq">\n{figure_svg(slug, no, ids)}\n'
                         f'<figcaption>{inline(caption)}</figcaption>\n</div>\n</figure>')
            i += 1
        elif kind == "p" and TABLE_RE.match(data):
            title, caption = TABLE_RE.match(data).groups()
            if i + 2 >= len(bl) or bl[i + 1][0] != "table" or not str(bl[i + 2][1]).startswith("Source: "):
                raise BuildError("a table and a 'Source:' paragraph must follow the table caption")
            head, *rows = bl[i + 1][1]
            trs = []
            for row in rows:
                hl = all(c.startswith("**") and c.endswith("**") for c in row)
                tds = "".join(f'<td data-label="{html.escape(plain(h))}">{inline(c[2:-2] if hl else c)}</td>'
                              for h, c in zip(head, row))
                cls = ' class="hl"' if hl else ""
                trs.append(f"<tr{cls}>{tds}</tr>")
            ths = "".join(f'<th scope="col">{inline(h)}</th>' for h in head)
            parts.append(f'<figure class="fig">\n<div class="fig-head"><span class="fig-no">TABLE</span>'
                         f'<span class="fig-title">{html.escape(title.upper())}</span></div>\n'
                         f'<div class="fig-body">\n<table class="dtable">\n'
                         f'<caption class="sr-only">{inline(caption)}</caption>\n'
                         f'<thead><tr>{ths}</tr></thead>\n<tbody>\n' + "\n".join(trs) + '\n</tbody>\n</table>\n'
                         f'<p class="footnote">{inline(bl[i + 2][1])}</p>\n</div>\n</figure>')
            i += 2
        elif kind == "p":
            parts.append(f'<p class="prose">{inline(data)}</p>')
        elif kind == "ul":
            parts.append('<ul class="art-list">\n' + "\n".join(f"<li>{inline(x)}</li>" for x in data) + "\n</ul>")
        elif kind == "ol":
            parts.append('<ol class="steps">\n' + "\n".join(f"<li><div>{inline(x)}</div></li>" for x in data) + "\n</ol>")
        else:
            raise BuildError(f"unexpected {kind} block: {str(data)[:60]}")
        i += 1
    parts.append("</div>\n</section>")
    for sid, _ in art["sections"]:
        ids.update({sid, f"{sid}-h"})
    return "\n\n".join(parts), meta["description"]


def head(page: str, meta: dict, art: dict) -> str:
    title = f'{meta["title"] if art.get("full_title") else meta["title"].split(":")[0]} · Yantrakar'
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
          "description": meta["description"], "datePublished": meta["date"],
          "dateModified": meta.get("updated", meta["date"]),
          "author": {"@type": "Person", "@id": f"{SITE}about.html#sandeep", "name": meta["author"],
                     "url": f"{SITE}about.html", "sameAs": [meta["author_url"]]},
          "publisher": {"@type": "Organization", "@id": f"{SITE}#org", "name": meta["publisher"], "url": SITE},
          "image": meta["image"], "mainEntityOfPage": meta["url"]}
    a = lambda s: html.escape(s, quote=True)
    subs = [
        (r"<title>.*?</title>", f"<title>{html.escape(title)}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{a(meta["description"])}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{a(title)}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{a(meta["description"])}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{meta["url"]}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{meta["url"]}">'),
        (r'<meta property="article:published_time" content="[^"]*">', f'<meta property="article:published_time" content="{meta["date"]}">'),
        (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{meta["image"]}">'),
        (r'<script type="application/ld\+json">.*?</script>',
         f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'),
    ]
    for pat, new in subs:
        page, n = re.subn(pat, lambda _m: new, page, count=1, flags=re.S)
        if n != 1:
            raise BuildError(f"head: no match for {pat}")
    return page


def build(art: dict) -> tuple[Path, str, str]:
    global PAGE
    PAGE = art["slug"] + ".html"
    md, page_path = ROOT / (art["slug"] + ".md"), ROOT / PAGE
    meta, body = front_matter(md.read_text())
    article, _ = render(art, meta, blocks(body))
    page = page_path.read_text()
    if page.count(START) != 1 or page.count(END) != 1:
        raise BuildError(f"{PAGE}: needs one {START} and one {END}")
    a, b = page.index(START) + len(START), page.index(END)
    new = head(page[:a] + "\n" + article + "\n" + page[b:], meta, art)
    return page_path, page, new


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale = []
    for art in ARTICLES:
        try:
            path, old, new = build(art)
        except BuildError as e:
            print(f"{art['slug']}: {e}", file=sys.stderr)
            return 2
        if old != new:
            stale.append(path.name)
            if not check:
                path.write_text(new)
    if check and stale:
        print("out of date, run tools/build_article.py: " + ", ".join(stale), file=sys.stderr)
        return 1
    print(("up to date: " if check or not stale else "wrote: ") + ", ".join(stale or [a["slug"] + ".html" for a in ARTICLES]))
    return 0


PAGE = ""

if __name__ == "__main__":
    sys.exit(main())
