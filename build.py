#!/usr/bin/env python3
"""Static site builder for The Market Journal.

Usage:  python3 build.py
Reads:  config.json, posts/*.md, src/style.css
Writes: docs/  (GitHub Pages serves this folder)

No third-party packages required.
"""
import html, json, re, shutil, sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
CFG = json.loads((ROOT / "config.json").read_text())
SITE = CFG["site_url"].rstrip("/")
BASE = urlparse(SITE).path.rstrip("/")          # "" on a custom domain
PER_PAGE = 12
TODAY = datetime.now(timezone(timedelta(hours=-6))).date()


# ---------- tiny markdown ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               r'<a href="\2" rel="noopener" target="_blank">\1</a>', t)
    t = re.sub(r"\[([^\]]+)\]\((/[^)]*)\)", lambda m: f'<a href="{BASE}{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    return t


def md(text):
    out, para, items, kind = [], [], [], None

    def flush_p():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_l():
        nonlocal kind
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
            items.clear()
            kind = None

    for line in text.strip().splitlines():
        s = line.strip()
        if not s:
            flush_p(); flush_l(); continue
        m = re.match(r"^(#{2,3})\s+(.*)", s)
        if m:
            flush_p(); flush_l()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
        m = re.match(r"^[-*]\s+(.*)", s)
        if m:
            flush_p()
            if kind not in (None, "ul"): flush_l()
            kind = "ul"; items.append(m.group(1)); continue
        m = re.match(r"^\d+\.\s+(.*)", s)
        if m:
            flush_p()
            if kind not in (None, "ol"): flush_l()
            kind = "ol"; items.append(m.group(1)); continue
        if s.startswith(">"):
            flush_p(); flush_l()
            out.append(f"<blockquote>{inline(s.lstrip('> '))}</blockquote>"); continue
        flush_l(); para.append(s)
    flush_p(); flush_l()
    return "\n".join(out)


# ---------- posts ----------
def parse_post(path):
    raw = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front matter")
    meta = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    for need in ("title", "date", "category", "summary"):
        if need not in meta:
            sys.exit(f"{path.name}: front matter missing '{need}'")
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    body = m.group(2)
    return {
        **meta, "slug": slug, "body_md": body, "html": md(body),
        "d": date.fromisoformat(meta["date"]),
        "mins": max(1, round(len(re.sub(r"[#*\[\]()-]", " ", body).split()) / 220)),
    }


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fmt(d):
    return f"{d.strftime('%B')} {d.day}, {d.year}"


# ---------- templates ----------
ORG = {
    "@type": "RealEstateAgent", "name": "The Market Real Estate Co.",
    "url": SITE + "/", "telephone": "+1-225-953-8889",
    "address": {"@type": "PostalAddress", "streetAddress": "4983 Bluebonnet Boulevard, Suite A",
                "addressLocality": "Baton Rouge", "addressRegion": "LA", "postalCode": "70809", "addressCountry": "US"},
    "sameAs": CFG.get("same_as", []),
}


def page(title, desc, path, body, ld=None, og_type="website"):
    url = f"{SITE}{path}"
    ld_json = f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:type" content="{og_type}"><meta property="og:url" content="{url}">
<meta property="og:site_name" content="The Market Journal">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="The Market Journal" href="{BASE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE}/assets/style.css">
{ld_json}
</head><body>
<header><div class="nav">
<a class="brand" href="{BASE}/">The Market Journal<small>Team Smith · The Market Real Estate Co.</small></a>
<nav><a href="{BASE}/">Home</a><a href="{BASE}/about/">About</a><a href="{BASE}/contact/">Contact</a></nav>
</div></header>
<main class="wrap">{body}</main>
<footer><div class="in">
<p><strong>Team Smith | Experience Results</strong></p>
<p>The Market Real Estate Co. · Licensed in Louisiana and Alabama<br>
Baton Rouge: 4983 Bluebonnet Boulevard, Suite A, Baton Rouge, LA 70809<br>
Alabama: 21036 State Highway 181, Suite 102C, Fairhope, AL 36532<br>
Office: (225) 953-8889</p>
<p>Content is general information, not legal, tax, or financial advice. Every market is different, so talk with a licensed professional about your situation. Equal Housing Opportunity.</p>
</div></footer>
</body></html>"""


CTA = """<div class="cta"><h3>Questions about buying, selling, or joining the team?</h3>
<p>Call or text Steven Smith: (225) 413-3376</p>
<p class="dim">The Market Real Estate Co. office: (225) 953-8889</p>
<p style="margin-top:10px">Team Smith | Experience Results</p></div>"""


def card(p):
    return f"""<a class="card" href="{BASE}/posts/{p['slug']}/">
<span class="tag">{html.escape(p['category'])}</span><h2>{html.escape(p['title'])}</h2>
<p>{html.escape(p['summary'])}</p>
<div class="meta">{fmt(p['d'])} · {p['mins']} min read</div></a>"""


def write(rel, content):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)


def listing(posts, cats, active, path_prefix, title, desc, hero):
    pages = [posts[i:i + PER_PAGE] for i in range(0, len(posts), PER_PAGE)] or [[]]
    chips = f'<a class="chip {"on" if active is None else ""}" href="{BASE}/">All</a>' + "".join(
        f'<a class="chip {"on" if c == active else ""}" href="{BASE}/category/{slugify(c)}/">{html.escape(c)}</a>' for c in cats)
    for n, chunk in enumerate(pages, 1):
        rel = path_prefix + ("" if n == 1 else f"page/{n}/")
        nav = ""
        if len(pages) > 1:
            prev = f'<a href="{BASE}/{path_prefix}{"" if n == 2 else f"page/{n-1}/"}">← Newer</a>' if n > 1 else "<span></span>"
            nxt = f'<a href="{BASE}/{path_prefix}page/{n+1}/">Older →</a>' if n < len(pages) else "<span></span>"
            nav = f'<div class="pager">{prev}<span>Page {n} of {len(pages)}</span>{nxt}</div>'
        body = f"{hero}<div class='chips'>{chips}</div>{''.join(card(p) for p in chunk)}{nav}{CTA}"
        ld = {"@context": "https://schema.org", "@type": "Blog", "name": "The Market Journal",
              "url": SITE + "/", "publisher": ORG}
        write(rel + "index.html", page(title, desc, "/" + rel, body, ld))


def main():
    posts = []
    for f in sorted((ROOT / "posts").glob("*.md")):
        p = parse_post(f)
        if p["d"] <= TODAY:
            posts.append(p)
    posts.sort(key=lambda p: p["d"], reverse=True)
    cats = sorted({p["category"] for p in posts})

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "src" / "style.css", OUT / "assets" / "style.css")
    write(".nojekyll", "")
    if CFG.get("custom_domain"):
        write("CNAME", CFG["custom_domain"])

    hero = """<section class="hero"><div class="eyebrow">The Market Journal</div>
<h1>Straight talk on real estate, from a team that closes.</h1>
<p>Practical advice for buyers, sellers, and agents, from Steven Smith and Team Smith at The Market Real Estate Co.</p></section>"""
    listing(posts, cats, None, "", "The Market Journal | Team Smith | Experience Results",
            "Real estate insights from Steven Smith and Team Smith at The Market Real Estate Co. Straight talk for buyers, sellers, and agents.", hero)
    for c in cats:
        cp = [p for p in posts if p["category"] == c]
        h = f'<section class="hero"><div class="eyebrow">Category</div><h1>{html.escape(c)}</h1></section>'
        listing(cp, cats, c, f"category/{slugify(c)}/", f"{c} | The Market Journal",
                f"{c} articles from Team Smith at The Market Real Estate Co.", h)

    for p in posts:
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
              "description": p["summary"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
              "author": {"@type": "Person", "name": "Steven Smith", "worksFor": ORG},
              "publisher": ORG, "mainEntityOfPage": f"{SITE}/posts/{p['slug']}/",
              "articleSection": p["category"]}
        body = f"""<a class="back" href="{BASE}/">← All posts</a>
<article><span class="tag">{html.escape(p['category'])}</span><h1>{html.escape(p['title'])}</h1>
<div class="meta">By Steven Smith · {fmt(p['d'])} · {p['mins']} min read</div>
{p['html']}</article>{CTA}"""
        write(f"posts/{p['slug']}/index.html",
              page(f"{p['title']} | The Market Journal", p["summary"], f"/posts/{p['slug']}/", body, ld, "article"))

    about = """<a class="back" href="{b}/">← All posts</a><article><h1>About The Market Journal</h1>
<p>The Market Journal is where Steven Smith and Team Smith share what we've learned in more than 22 years of real estate. Steven is the broker/owner of The Market Real Estate Co., an independent boutique brokerage serving Greater Baton Rouge, the Alabama Gulf Coast, and Greater Huntsville, and is licensed in Louisiana and Alabama.</p>
<p>Team Smith is a large, high-producing team. Our RealTrends Verified 2025 production was 322 sides and $109.14 million, and we've earned 600+ five-star Zillow reviews and 150+ five-star Google reviews. Each year we also run the Christmas Give, a charity Steven and Laura started in 2008 to help neighbors in need.</p></article>{cta}""".format(b=BASE, cta=CTA)
    write("about/index.html", page("About | The Market Journal", "About Steven Smith, Team Smith, and The Market Real Estate Co.", "/about/", about, {"@context": "https://schema.org", **ORG}))
    contact = """<a class="back" href="{b}/">← All posts</a><article><h1>Contact</h1>
<p>Call or text Steven Smith: (225) 413-3376</p><p>The Market Real Estate Co. office: (225) 953-8889</p>
<p>Baton Rouge: 4983 Bluebonnet Boulevard, Suite A, Baton Rouge, LA 70809<br>Alabama: 21036 State Highway 181, Suite 102C, Fairhope, AL 36532</p></article>""".format(b=BASE)
    write("contact/index.html", page("Contact | The Market Journal", "Contact Steven Smith and Team Smith at The Market Real Estate Co.", "/contact/", contact))
    write("404.html", page("Page not found | The Market Journal", "Page not found", "/404.html",
          f'<article><h1>That page moved or doesn\'t exist.</h1><p><a href="{BASE}/">Back to The Market Journal</a></p></article>'))

    # sitemap / rss / robots / llms.txt
    urls = [("/", max([p["d"] for p in posts], default=TODAY))] + [("/about/", TODAY), ("/contact/", TODAY)] + \
           [(f"/category/{slugify(c)}/", max(p["d"] for p in posts if p["category"] == c)) for c in cats] + \
           [(f"/posts/{p['slug']}/", p["d"]) for p in posts]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{SITE}/posts/{p['slug']}/</link>"
                    f"<guid>{SITE}/posts/{p['slug']}/</guid><pubDate>{datetime(p['d'].year, p['d'].month, p['d'].day, 12, tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>"
                    f"<description>{html.escape(p['summary'])}</description></item>" for p in posts[:30])
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>The Market Journal</title><link>{SITE}/</link>'
          f"<description>Real estate insights from Team Smith at The Market Real Estate Co.</description>{items}</channel></rss>")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("llms.txt", "# The Market Journal\n\n> Real estate insights from Steven Smith and Team Smith at The Market Real Estate Co. "
          "(Baton Rouge, LA; licensed in Louisiana and Alabama).\n\n## Posts\n\n" +
          "".join(f"- [{p['title']}]({SITE}/posts/{p['slug']}/): {p['summary']}\n" for p in posts))
    print(f"Built {len(posts)} posts into docs/ ({SITE})")


if __name__ == "__main__":
    main()
