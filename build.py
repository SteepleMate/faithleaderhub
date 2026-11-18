"""Builds the Faith Leader Hub static site (faithleaderhub.com) from content/ into docs/ (GitHub Pages serves docs/).
  python build.py
Content: content/*.md articles (front matter: title, slug, date, summary), content/about.md, content/feeds.json.
No dependencies. Re-run after editing content, then commit content/ and docs/ together.
"""
import datetime, html, json, os, re
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(ROOT, 'content'), os.path.join(ROOT, 'docs')
SITE = 'https://faithleaderhub.com'
SM = 'https://get.steeplemate.com/?utm_source=faithleaderhub&utm_medium=site'
NAME = 'Faith Leader Hub'
TAG = 'Practical help for the people who keep the church running'


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    def link(m):
        url = m.group(2).replace('&amp;', '&')
        if 'steeplemate.com' in url and 'utm_' not in url:
            url = SM
        ext = '' if url.startswith('/') else ' rel="noopener"'
        return f'<a href="{html.escape(url)}"{ext}>{m.group(1)}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, t)


def md(text):
    out, para, lst = [], [], None
    def flush():
        nonlocal lst
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
        if lst: out.append(f'<{lst[0]}>' + ''.join(f'<li>{inline(i)}</li>' for i in lst[1]) + f'</{lst[0]}>'); lst = None
    for ln in text.splitlines():
        m = re.match(r'(#{2,4}) (.*)', ln)
        if m: flush(); lv = len(m.group(1)); out.append(f'<h{lv}>{inline(m.group(2))}</h{lv}>'); continue
        b = re.match(r'\s*[-*] (.*)', ln); n = re.match(r'\s*\d+[.)] (.*)', ln)
        if b or n:
            kind = 'ul' if b else 'ol'
            if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
            if not lst or lst[0] != kind: flush(); lst = (kind, [])
            lst[1].append((b or n).group(1)); continue
        if lst and ln.startswith('  ') and ln.strip(): lst[1][-1] += ' ' + ln.strip(); continue
        if not ln.strip(): flush(); continue
        if lst: flush()
        para.append(ln.strip())
    flush()
    return '\n'.join(out)


def parse(path):
    t = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n(.*)', t.replace('\r\n', '\n'), re.S)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', m.group(1), re.M))
    return meta, m.group(2).strip()


CSS = """:root{--bg:#FBF8F3;--surface:#FFFFFF;--ink:#14202B;--ink-2:#4B5661;--ink-3:#7A848C;--line:#E6DFD3;--accent:#1F3A55;--accent-2:#A7762A;--soft:#F4ECDF}
@media (prefers-color-scheme: dark){:root{--bg:#141A1D;--surface:#1B2327;--ink:#ECE7DF;--ink-2:#B9C2C5;--ink-3:#8C979B;--line:#2C373C;--accent:#9DB9D6;--accent-2:#D9A957;--soft:#20292D}}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--ink);font:17px/1.65 Georgia,"Iowan Old Style","Palatino Linotype",serif;padding:0 16px}
a{color:var(--accent)}a:hover{color:var(--accent-2)}
.wrap{max-width:760px;margin:0 auto}
header{display:flex;flex-wrap:wrap;align-items:center;gap:10px 22px;padding:22px 0 16px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font:800 22px/1.1 system-ui,"Segoe UI",sans-serif;color:var(--ink);text-decoration:none;letter-spacing:.01em}
.brand img{width:44px;height:44px;border-radius:9px}
@media (prefers-color-scheme: dark){.brand img{background:#FBF8F3;padding:3px}}
.brand span span{color:var(--accent-2)}
nav{display:flex;flex-wrap:wrap;gap:16px;font:500 14px system-ui,"Segoe UI",sans-serif;margin-left:auto}
nav a{text-decoration:none;color:var(--ink-2)}nav a:hover{color:var(--accent)}
.hero{padding:42px 0 18px}.hero h1{font:700 34px/1.2 system-ui,"Segoe UI",sans-serif;margin:0 0 10px}.hero p{color:var(--ink-2);margin:0;font-size:19px}
.cards{display:grid;gap:16px;margin:26px 0}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.card h2{font:600 20px/1.3 system-ui,"Segoe UI",sans-serif;margin:0 0 6px}.card h2 a{text-decoration:none;color:var(--ink)}.card h2 a:hover{color:var(--accent)}
.card p{margin:0;color:var(--ink-2)}.meta{font:13px system-ui,"Segoe UI",sans-serif;color:var(--ink-3);margin-top:8px}
article{padding:30px 0}article h1{font:700 32px/1.2 system-ui,"Segoe UI",sans-serif;margin:0 0 8px}
article h2,article h3{font-family:system-ui,"Segoe UI",sans-serif;line-height:1.3;margin:30px 0 8px}article h2{font-size:23px}article h3{font-size:19px}
article li{margin:4px 0}
.callout{background:var(--soft);border-left:4px solid var(--accent-2);border-radius:8px;padding:16px 20px;margin:30px 0}
.callout strong{font-family:system-ui,"Segoe UI",sans-serif}
.feeds{list-style:none;padding:0}.feeds li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:12px 0}
.feeds .links{font:14px system-ui,"Segoe UI",sans-serif;margin-top:6px;display:flex;gap:16px}
footer{border-top:1px solid var(--line);margin:40px 0 0;padding:20px 0 40px;font:14px system-ui,"Segoe UI",sans-serif;color:var(--ink-3)}
footer a{color:var(--ink-2)}
@media (max-width:600px){body{font-size:16px}.hero h1{font-size:27px}article h1{font-size:26px}nav{margin-left:0}}"""


def page(title, body, desc, path):
    canon = SITE + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/feed.xml">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<link rel="icon" href="/favicon.png" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta property="og:image" content="{SITE}/logo.png">
<link rel="stylesheet" href="/style.css">
</head>
<body><div class="wrap">
<header><a class="brand" href="/"><img src="/logo.png" alt="" width="44" height="44"><span>Faith Leader <span>Hub</span></span></a>
<nav><a href="/">Articles</a><a href="/resources.html">Resources</a><a href="/about.html">About</a><a href="/feed.xml">RSS</a><a href="{SM}">SteepleMate</a></nav></header>
{body}
<footer>Faith Leader Hub is published by Pentesoft, the team behind <a href="{SM}">SteepleMate</a> church management software.
Articles are free to read and share with credit. <a href="/feed.xml">RSS feed</a> · <a href="/privacy.html">Privacy</a> · <a href="/about.html">About</a></footer>
</div></body></html>
"""


def callout():
    return (f'<div class="callout"><strong>Want one place for your people, groups, check-in and calendar?</strong> '
            f'<a href="{SM}">SteepleMate</a> is church management software for churches of every size, from new plants to large congregations. '
            f'Try it free for 30 days.</div>')


def main():
    os.makedirs(os.path.join(OUT, 'articles'), exist_ok=True)
    arts = []
    for f in sorted(os.listdir(SRC)):
        if f.endswith('.md') and f != 'about.md':
            meta, body = parse(os.path.join(SRC, f)); arts.append((meta, body))
    arts.sort(key=lambda a: (a[0]['date'], a[0]['title']), reverse=True)
    for meta, body in arts:
        more = ''.join(f'<li><a href="/articles/{m["slug"]}.html">{html.escape(m["title"])}</a></li>' for m, _ in arts if m['slug'] != meta['slug'])
        d = datetime.date.fromisoformat(meta['date']).strftime('%B %-d, %Y') if os.name != 'nt' else datetime.date.fromisoformat(meta['date']).strftime('%B %d, %Y').replace(' 0', ' ')
        content = (f'<article><h1>{html.escape(meta["title"])}</h1><div class="meta">{d}</div>{md(body)}{callout()}'
                   f'<h3>More from Faith Leader Hub</h3><ul>{more}</ul></article>')
        open(os.path.join(OUT, 'articles', meta['slug'] + '.html'), 'w', encoding='utf-8').write(page(f'{meta["title"]} | {NAME}', content, meta['summary'], f'/articles/{meta["slug"]}.html'))
    cards = ''.join(f'<div class="card"><h2><a href="/articles/{m["slug"]}.html">{html.escape(m["title"])}</a></h2><p>{html.escape(m["summary"])}</p></div>' for m, _ in arts)
    home = (f'<section class="hero"><h1>{TAG}.</h1><p>Short, practical articles for pastors, church administrators and volunteers '
            f'at churches of every size. Free to read and share.</p></section><div class="cards">{cards}</div>'
            f'<div class="callout"><strong>Stay current.</strong> Follow our <a href="/feed.xml">RSS feed</a>, or see '
            f'<a href="/resources.html">trusted church-leadership feeds</a> we read ourselves.</div>{callout()}')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page(f'{NAME}: {TAG}', home, TAG + '.', '/'))
    am, ab = parse(os.path.join(SRC, 'about.md'))
    open(os.path.join(OUT, 'about.html'), 'w', encoding='utf-8').write(page(f'About | {NAME}', f'<article><h1>{html.escape(am["title"])}</h1>{md(ab)}{callout()}</article>', 'About Faith Leader Hub.', '/about.html'))
    feeds = [{'name': NAME, 'site': SITE + '/', 'feed': SITE + '/feed.xml',
              'description': 'Our own practical articles for pastors, church administrators and volunteers. New articles appear here first.'}]
    feeds += json.load(open(os.path.join(SRC, 'feeds.json'), encoding='utf-8'))
    items = ''.join(f'<li><strong>{html.escape(x["name"])}</strong><div>{html.escape(x["description"])}</div><div class="links">'
                    f'<a href="{html.escape(x["site"])}" rel="noopener">Website</a><a href="{html.escape(x["feed"])}" rel="noopener">RSS feed</a></div></li>' for x in feeds)
    res = (f'<article><h1>Resources: church-leadership feeds</h1><p>Trusted sources we read for church research, news and leadership ideas. '
           f'Add any of these RSS feeds to your feed reader, starting with our own. Links after the first go to their publishers; '
           f'Faith Leader Hub is not affiliated with them.</p><ul class="feeds">{items}</ul></article>')
    open(os.path.join(OUT, 'resources.html'), 'w', encoding='utf-8').write(page(f'Resources | {NAME}', res, 'RSS feeds from trusted church-leadership publishers.', '/resources.html'))
    priv = ('<article><h1>Privacy</h1><p>This site does not use cookies, analytics or tracking scripts, and it has no forms.</p>'
            '<p>Faith Leader Hub is also the address SteepleMate uses to introduce itself to churches, using the church office email '
            'address a church publishes on its own website. If you received one of those emails and would rather not hear from us, '
            'reply with the word "unsubscribe" and we will not email that address again. You can also write to '
            '<a href="mailto:hello@faithleaderhub.com?subject=unsubscribe">hello@faithleaderhub.com</a>.</p></article>')
    open(os.path.join(OUT, 'privacy.html'), 'w', encoding='utf-8').write(page(f'Privacy | {NAME}', priv, 'Privacy at Faith Leader Hub.', '/privacy.html'))
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(page(f'Not found | {NAME}', '<article><h1>Page not found</h1><p><a href="/">Back to the articles</a>.</p></article>', 'Not found.', '/404.html'))
    open(os.path.join(OUT, 'style.css'), 'w', encoding='utf-8').write(CSS)
    import shutil
    for src, dst in (('logo-icon-256.png', 'logo.png'), ('favicon-64.png', 'favicon.png'), ('apple-touch-icon.png', 'apple-touch-icon.png')):
        shutil.copyfile(os.path.join(ROOT, 'assets', src), os.path.join(OUT, dst))
    if os.path.exists(os.path.join(OUT, 'favicon.svg')): os.remove(os.path.join(OUT, 'favicon.svg'))
    rss_items = ''.join(f'<item><title>{html.escape(m["title"])}</title><link>{SITE}/articles/{m["slug"]}.html</link><guid>{SITE}/articles/{m["slug"]}.html</guid>'
                        f'<pubDate>{format_datetime(datetime.datetime.fromisoformat(m["date"] + "T09:00:00-06:00"))}</pubDate><description>{html.escape(m["summary"])}</description></item>' for m, _ in arts)
    open(os.path.join(OUT, 'feed.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}/</link>'
        f'<description>{html.escape(TAG)}.</description><language>en-us</language>{rss_items}</channel></rss>\n')
    urls = ['/', '/about.html', '/resources.html', '/privacy.html'] + [f'/articles/{m["slug"]}.html' for m, _ in arts]
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                                                        + ''.join(f'<url><loc>{SITE}{u}</loc></url>' for u in urls) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    open(os.path.join(OUT, 'CNAME'), 'w').write('faithleaderhub.com\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print(f'built {len(arts)} articles into docs/')


if __name__ == '__main__':
    main()
