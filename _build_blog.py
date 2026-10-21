#!/usr/bin/env python3
"""Build blog/index.html and blog/<slug>.html from _posts.py, and refresh sitemap.xml.
Run from the repo root: python3 _build_blog.py
"""
import html as H, json, os, re, datetime
from _posts import POSTS

SITE = "https://www.hirehybryd.com"
BOOK = "https://api.leadconnectorhq.com/widget/booking/mN3F1LEz2Q5n6eoMMfK2"
os.makedirs("blog", exist_ok=True)

src = open("our-story.html", encoding="utf-8").read()
body = src[src.find("<body"):]
nav = re.search(r"<body>(<div data-animation.*?</nav><div class=\"menu-button w-nav-button\"><div class=\"icon[^\"]*w-icon-nav-menu\"></div></div></div></div></div>)", body, re.S).group(1)
nav = nav.replace(' aria-current="page"', "").replace(" w--current", "")
nav = re.sub(r'<li><a href="/our-story"([^>]*)>OUR STORY</a></li>',
             r'<li class="nav-spacing"><a href="/our-story"\1>OUR STORY</a></li><li><a href="/blog" aria-current="page" class="nav-link copy-dark w--current">BLOG</a></li>', nav)
assert 'href="/blog"' in nav
fi = body.find('<section class="section-footer"'); fe = body.find("</section>", fi) + 10
footer = body[fi:fe]
tail = body[fe:].replace("</body></html>", "")
cta = f'<div class="cta dark padding-24px centered"><a href="{BOOK}" target="_blank" class="link-block-5 w-inline-block"><div class="w-layout-blockcontainer container-xxlarge w-container"><div class="div-block-15"><h5 class="copy-white copy-eyebrow margin-bottom-16px">Wonder if Hybryd is a good fit for you?</h5><div class="div-block-20"><h3 class="copy-white copy-regular">Book a call</h3><img loading="lazy" src="/images/arrow-right-white.svg" alt=""/></div></div></div></a></div>'

def head(title, desc, path, ld, extra=""):
    url = SITE + path
    t = H.escape(title); d = H.escape(desc, quote=True)
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><title>{t}</title><meta content="{d}" name="description"/><meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta property="og:type" content="{'article' if path.startswith('/blog/') else 'website'}"/><meta property="og:site_name" content="Hybryd"/><meta property="og:locale" content="en_US"/><meta property="og:url" content="{url}"/><meta property="og:title" content="{t}"/><meta property="og:description" content="{d}"/><meta property="og:image" content="{SITE}/images/og-image.png"/><meta property="og:image:width" content="1200"/><meta property="og:image:height" content="630"/><meta name="twitter:card" content="summary_large_image"/><meta name="twitter:title" content="{t}"/><meta name="twitter:description" content="{d}"/><meta name="twitter:image" content="{SITE}/images/og-image.png"/>{extra}
<link rel="canonical" href="{url}"/><link href="/css/site.css" rel="stylesheet" type="text/css"/><link href="https://fonts.googleapis.com" rel="preconnect"/><link href="https://fonts.gstatic.com" rel="preconnect" crossorigin="anonymous"/><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet"><script type="text/javascript">!function(o,c){{var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}}(window,document);</script><link href="/images/group-119.png" rel="shortcut icon" type="image/x-icon"/><link href="/images/logo-group-120.png" rel="apple-touch-icon"/>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>'''

ORG = {"@type": "Organization", "@id": SITE + "/#organization", "name": "Hybryd", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/images/logo-group-120.png"}}

def nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")

def words(htmltext):
    return len(re.sub(r"<[^>]+>", " ", htmltext).split())

# ---- posts
for p in POSTS:
    path = f"/blog/{p['slug']}"
    faq_html = ""
    faq_ld = None
    if p.get("faq"):
        faq_html = '<h2>Questions we get about this</h2>' + "".join(f'<h3>{H.escape(q)}</h3><p>{H.escape(a)}</p>' for q, a in p["faq"])
        faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    article_ld = {"@type": "BlogPosting", "@id": SITE + path + "#post", "headline": p["title"], "description": p["description"], "url": SITE + path,
                  "datePublished": p["date"], "dateModified": p.get("updated", p["date"]), "image": SITE + "/images/og-image.png",
                  "author": {"@type": "Organization", "name": "Hybryd", "@id": SITE + "/#organization"}, "publisher": {"@id": SITE + "/#organization"},
                  "mainEntityOfPage": SITE + path, "wordCount": words(p["body"]), "inLanguage": "en-US", "articleSection": p["eyebrow"]}
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": p["title"], "item": SITE + path}]}
    graph = [ORG, article_ld, crumbs] + ([faq_ld] if faq_ld else [])
    ld = {"@context": "https://schema.org", "@graph": graph}
    extra = f'<meta property="article:published_time" content="{p["date"]}"/><meta property="article:section" content="{H.escape(p["eyebrow"])}"/>'
    others = [o for o in POSTS if o["slug"] != p["slug"]][:3]
    more = "".join(f'<li><a href="/blog/{o["slug"]}">{H.escape(o["title"])}</a></li>' for o in others)
    page = head(p["title"] + " | Hybryd Blog", p["description"], path, ld, extra) + f'''<body>{nav}
<section class="hero-our-story post-hero"><div class="w-layout-blockcontainer container-large centered w-container"><div class="post-meta"><a href="/blog" class="copy-eyebrow">Blog</a><span class="copy-eyebrow">{H.escape(p["eyebrow"])}</span><span class="copy-eyebrow post-date">{nice_date(p["date"])}</span></div><h1 class="copy-centered margin-bottom-24px">{H.escape(p["title"])}</h1><p class="post-lede copy-centered">{H.escape(p["description"])}</p></div></section>
<section class="section-100 post-section"><div class="w-layout-blockcontainer container-large w-container"><article class="post">{p["body"]}{faq_html}</article>
<aside class="post-more"><h5 class="copy-eyebrow">More from the Hybryd blog</h5><ul>{more}</ul></aside></div></section>
{cta}{footer}{tail}</body></html>'''
    open(f"blog/{p['slug']}.html", "w", encoding="utf-8").write(page)

# ---- index
posts_sorted = sorted(POSTS, key=lambda x: x["date"], reverse=True)
cards = "".join(f'''<a href="/blog/{p["slug"]}" class="post-card"><span class="copy-eyebrow">{H.escape(p["eyebrow"])}</span><h3>{H.escape(p["title"])}</h3><p>{H.escape(p["description"])}</p><span class="post-card-date">{nice_date(p["date"])}</span></a>''' for p in posts_sorted)
blog_ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "Blog", "@id": SITE + "/blog#blog", "url": SITE + "/blog", "name": "Hybryd Blog", "publisher": {"@id": SITE + "/#organization"},
            "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": SITE + "/blog/" + p["slug"], "datePublished": p["date"]} for p in posts_sorted]},
           {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog"}]}]}
index = head("Blog | Remote Staffing Advice for Small Business | Hybryd",
             "Straight answers on hiring and keeping full-time remote office staff from the Philippines, Latin America, and Africa: cost, onboarding, retention, and which roles to fill first.",
             "/blog", blog_ld) + f'''<body>{nav}
<section class="hero-our-story post-hero"><div class="w-layout-blockcontainer container-large centered w-container"><h1 class="copy-centered margin-bottom-24px">The Hybryd blog</h1><p class="post-lede copy-centered">Straight answers for owners thinking about remote office staff. No fluff, no jargon, written by people who do this every day.</p></div></section>
<section class="section-100 post-section"><div class="w-layout-blockcontainer container-large w-container"><div class="post-grid">{cards}</div></div></section>
{cta}{footer}{tail}</body></html>'''
open("blog/index.html", "w", encoding="utf-8").write(index)

# ---- sitemap
today = datetime.date.today().isoformat()
sm = open("sitemap.xml").read()
sm = re.sub(r"\s*<url><loc>https://www\.hirehybryd\.com/blog.*?</url>", "", sm, flags=re.S)
entries = f'  <url><loc>{SITE}/blog</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
entries += "".join(f'  <url><loc>{SITE}/blog/{p["slug"]}</loc><lastmod>{p.get("updated", p["date"])}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n' for p in posts_sorted)
sm = sm.replace("</urlset>", entries + "</urlset>")
open("sitemap.xml", "w").write(sm)
print(f"built {len(POSTS)} posts + index; sitemap updated")
