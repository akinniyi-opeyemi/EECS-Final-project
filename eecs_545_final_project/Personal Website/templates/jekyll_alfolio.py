"""Jekyll al-folio pastiche template.

Renders a persona as a multi-page static site mimicking the al-folio Jekyll
theme: narrow reading column, serif display type, top-right nav, bolded
author-name in publication lists, small-caps section headings.
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path


# ---------- small helpers ----------

def _esc(value) -> str:
    """HTML-escape, returning '' for None."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _paragraphs(text: str) -> str:
    if not text:
        return ""
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n".join(f"      <p>{_esc(p)}</p>" for p in parts)


def _author_list_html(authors: list[str], last_name: str) -> str:
    """Render an author list, bolding any entry whose last token matches last_name."""
    rendered = []
    target = last_name.lower()
    for a in authors:
        tokens = a.replace(",", "").split()
        last = tokens[-1].lower() if tokens else ""
        if last == target:
            rendered.append(f"<strong>{_esc(a)}</strong>")
        else:
            rendered.append(_esc(a))
    return ", ".join(rendered)


def _pub_venue_line(pub: dict) -> str:
    """Italicized venue/year line; varies by type."""
    ptype = pub.get("type", "article")
    year = pub.get("year")
    if ptype == "book":
        publisher = pub.get("publisher") or pub.get("venue") or ""
        bits = [publisher, str(year) if year else ""]
    elif ptype == "chapter":
        book_title = pub.get("book_title") or pub.get("venue") or ""
        publisher = pub.get("publisher") or ""
        bits = [f"In <em>{_esc(book_title)}</em>" if book_title else "", publisher, str(year) if year else ""]
        joined = ", ".join(b for b in bits if b)
        return f"<div class=\"pub-venue\"><em>{joined}</em></div>" if joined else ""
    else:
        venue = pub.get("venue") or ""
        bits = [venue, str(year) if year else ""]
    joined = " ".join(b for b in bits if b)
    return f"<div class=\"pub-venue\"><em>{_esc(joined)}</em></div>" if joined else ""


def _pub_buttons(pub: dict) -> str:
    buttons = [f'<a class="pub-btn" href="#abs-{_esc(pub.get("id",""))}">abs</a>']
    if pub.get("pdf_source"):
        buttons.append(f'<a class="pub-btn" href="{_esc(pub["pdf_source"])}">pdf</a>')
    if pub.get("bibtex_source"):
        buttons.append(f'<a class="pub-btn" href="{_esc(pub["bibtex_source"])}">bib</a>')
    if pub.get("code_url"):
        buttons.append(f'<a class="pub-btn" href="{_esc(pub["code_url"])}">code</a>')
    return '<div class="pub-btns">' + " ".join(buttons) + "</div>"


def _pub_entry_html(pub: dict, last_name: str) -> str:
    title = _esc(pub.get("title", ""))
    authors = _author_list_html(pub.get("authors", []), last_name)
    venue_line = _pub_venue_line(pub)
    btns = _pub_buttons(pub)
    note = pub.get("note")
    note_html = f'<div class="pub-note">{_esc(note)}</div>' if note else ""
    return (
        '<article class="pub">\n'
        f'  <div class="pub-title"><strong>{title}</strong></div>\n'
        f'  <div class="pub-authors">{authors}</div>\n'
        f'  {venue_line}\n'
        f'  {note_html}\n'
        f'  {btns}\n'
        '</article>'
    )


def _nav_html(cv_present: bool, brand: str, current: str) -> str:
    items = [
        ("About", "index.html", "about"),
        ("Publications", "publications.html", "publications"),
        ("Teaching", "teaching.html", "teaching"),
    ]
    if cv_present:
        items.append(("CV", "cv.html", "cv"))
    links = []
    for label, href, key in items:
        cls = "nav-link active" if key == current else "nav-link"
        links.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return (
        '<nav class="topnav">\n'
        f'  <a class="brand" href="index.html">{_esc(brand)}</a>\n'
        '  <div class="nav-links">\n    ' + "\n    ".join(links) + '\n  </div>\n'
        '</nav>'
    )


def _news_items(persona: dict) -> list[tuple[int, str]]:
    """Synthesize up to 3 dated news items, deterministically, sorted desc by year."""
    items: list[tuple[int, str]] = []

    awards = persona.get("awards") or []
    if awards:
        # awards are already ordered newest-first in the persona; be explicit anyway.
        a = max(awards, key=lambda x: x.get("year", 0))
        if a.get("year") and a.get("name"):
            items.append((a["year"], f"Received {a['name']}"))

    pubs = persona.get("publications") or []
    if pubs:
        p = max(pubs, key=lambda x: x.get("year", 0))
        title = p.get("title") or ""
        if len(title) > 60:
            title = title[:57].rstrip() + "…"
        venue = p.get("venue") or ""
        suffix = f" accepted to {venue}" if venue else ""
        if p.get("year"):
            items.append((p["year"], f"New paper “{title}”{suffix}"))

    positions = persona.get("positions") or []
    recent_pos = [pos for pos in positions if pos.get("start") and pos["start"] >= 2023]
    if recent_pos:
        pos = max(recent_pos, key=lambda x: x["start"])
        role = pos.get("role", "")
        inst = pos.get("institution", "")
        items.append((pos["start"], f"Joined {inst} as {role}"))

    items.sort(key=lambda x: x[0], reverse=True)
    return items[:3]


def _format_news_date(year: int) -> str:
    return f"{year}"


def _socials_html(social: dict) -> str:
    order = [
        ("google_scholar", "scholar"),
        ("semantic_scholar", "semantic scholar"),
        ("github", "github"),
        ("dblp", "dblp"),
        ("orcid", "orcid"),
        ("twitter", "twitter"),
        ("bluesky", "bluesky"),
        ("linkedin", "linkedin"),
        ("personal_blog", "blog"),
    ]
    out = []
    for key, label in order:
        val = social.get(key)
        if not val:
            continue
        if key == "orcid":
            href = f"https://orcid.org/{val}"
        else:
            href = val
        out.append(f'<a class="social" href="{_esc(href)}">{label}</a>')
    if not out:
        return ""
    return '<div class="socials">' + " · ".join(out) + "</div>"


def _contact_block(persona: dict) -> str:
    office = persona.get("office") or {}
    contact = persona.get("contact") or {}
    rows = []
    if contact.get("email"):
        rows.append(f'<div class="contact-row"><span class="ico">📧</span> <a href="mailto:{_esc(contact["email"])}">{_esc(contact["email"])}</a></div>')
    if contact.get("email_secondary"):
        rows.append(f'<div class="contact-row"><span class="ico">📧</span> also <a href="mailto:{_esc(contact["email_secondary"])}">{_esc(contact["email_secondary"])}</a></div>')
    if office.get("building") or office.get("room"):
        parts = []
        if office.get("building"):
            parts.append(office["building"])
        if office.get("room"):
            parts.append(f"Room {office['room']}")
        rows.append(f'<div class="contact-row"><span class="ico">📍</span> {_esc(", ".join(parts))}</div>')
    if contact.get("phone_office"):
        rows.append(f'<div class="contact-row"><span class="ico">📞</span> {_esc(contact["phone_office"])}</div>')
    if contact.get("phone_lab"):
        rows.append(f'<div class="contact-row"><span class="ico">📞</span> Lab: {_esc(contact["phone_lab"])}</div>')
    if contact.get("fax"):
        rows.append(f'<div class="contact-row"><span class="ico">📠</span> Fax: {_esc(contact["fax"])}</div>')
    if office.get("hours"):
        rows.append(f'<div class="contact-row"><span class="ico">🕑</span> Office hours: {_esc(office["hours"])}</div>')
    if not rows:
        return ""
    return '<div class="contact-block">\n  ' + "\n  ".join(rows) + "\n</div>"


def _mailing_address_html(office: dict) -> str:
    m = office.get("mailing_address") if office else None
    if not m:
        return ""
    lines = []
    for key in ("line1", "line2", "building_line", "street"):
        if m.get(key):
            lines.append(_esc(m[key]))
    city_state = ", ".join(s for s in [m.get("city", ""), m.get("state", "")] if s).strip(", ")
    csz = " ".join(s for s in [city_state, m.get("zip", "")] if s).strip()
    if csz:
        lines.append(_esc(csz))
    if m.get("country"):
        lines.append(_esc(m["country"]))
    if not lines:
        return ""
    return '<address class="mailing">\n  ' + "<br>\n  ".join(lines) + "\n</address>"


def _students_block(persona: dict) -> str:
    group = persona.get("group") or {}
    blocks = []
    if group.get("name"):
        phds = group.get("current_phd_students") or []
        ms = group.get("current_masters_students") or []
        if phds or ms:
            rows = []
            for s in phds:
                topic = f" — {_esc(s['topic'])}" if s.get("topic") else ""
                yr = f" (since {s['year_started']})" if s.get("year_started") else ""
                rows.append(f'<li><strong>{_esc(s.get("name",""))}</strong>{yr}{topic}</li>')
            for s in ms:
                rows.append(f'<li>{_esc(s.get("name",""))} <span class="muted">(M.S.)</span></li>')
            blocks.append(
                f'<div class="group-label">{_esc(group["name"])}</div>\n'
                '<ul class="student-list">\n  ' + "\n  ".join(rows) + "\n</ul>"
            )
    advisees = group.get("advisees") or []
    if advisees:
        rows = []
        for a in advisees:
            name = _esc(a.get("name", ""))
            level = f' <span class="muted">({_esc(a["level"])})</span>' if a.get("level") else ""
            topic = f" — {_esc(a['topic'])}" if a.get("topic") else ""
            rows.append(f"<li>{name}{level}{topic}</li>")
        blocks.append('<ul class="student-list">\n  ' + "\n  ".join(rows) + "\n</ul>")
    if not blocks:
        return ""
    return (
        '<section class="students">\n'
        '  <h2 class="section-heading">students</h2>\n  '
        + "\n  ".join(blocks) + "\n</section>"
    )


def _prospective_block(persona: dict) -> str:
    ps = persona.get("prospective_students") or {}
    if ps.get("accepting") is None:
        return ""
    note = ps.get("note") or ""
    cls = "prospective accepting" if ps.get("accepting") else "prospective not-accepting"
    label = "Prospective Students" if ps.get("accepting") else "Not Accepting Students"
    return (
        f'<aside class="{cls}">\n'
        f'  <div class="prospective-label">{label}</div>\n'
        f'  <div class="prospective-note">{_esc(note)}</div>\n'
        '</aside>'
    )


# ---------- CSS ----------

CSS = """\
/* jekyll_alfolio pastiche */
:root {
  --background:    #ffffff;
  --text-primary:  #212529;
  --text-muted:    #6c757d;
  --accent:        #0076df;
  --accent-hover:  #0056b3;
  --border-light:  #e9ecef;
  --code-bg:       #f8f9fa;
  --font-serif-display: Georgia, "Times New Roman", serif;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--background);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.6;
}

a {
  color: var(--accent);
  text-decoration: none;
}
a:hover { color: var(--accent-hover); text-decoration: underline; }

.page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px 48px 24px;
}

/* top nav */
.topnav {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 20px 0 24px 0;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 32px;
}
.brand {
  font-family: var(--font-serif-display);
  font-size: 1.15rem;
  color: var(--text-primary);
}
.brand:hover { text-decoration: none; }
.nav-links .nav-link {
  margin-left: 18px;
  color: var(--text-primary);
  font-size: 0.95rem;
}
.nav-links .nav-link.active {
  color: var(--accent);
}

/* hero */
.hero {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin-bottom: 24px;
}
.hero-text { flex: 1 1 auto; }
.hero-photo {
  flex: 0 0 auto;
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid var(--border-light);
}
.hero h1 {
  font-family: var(--font-serif-display);
  font-weight: 400;
  font-size: 2.5rem;
  margin: 0 0 4px 0;
  line-height: 1.15;
}
.hero .title-line {
  color: var(--text-primary);
  font-size: 1.05rem;
  margin-bottom: 2px;
}
.hero .affiliation {
  color: var(--text-muted);
  font-size: 0.98rem;
  margin-bottom: 14px;
}
.hero .pronouns {
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* bio */
.bio p { margin: 0 0 14px 0; }

/* section headings */
.section-heading {
  text-transform: lowercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 4px;
  margin: 36px 0 16px 0;
}

/* contact block */
.contact-block {
  margin: 20px 0 4px 0;
  font-size: 0.95rem;
}
.contact-row { margin-bottom: 4px; }
.contact-row .ico { display: inline-block; width: 1.4em; }

/* socials */
.socials {
  margin-top: 10px;
  font-size: 0.9rem;
  color: var(--text-muted);
}
.socials .social {
  color: var(--accent);
}

/* news */
.news-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.news-list li {
  display: flex;
  gap: 14px;
  margin-bottom: 6px;
  font-size: 0.95rem;
}
.news-date {
  flex: 0 0 auto;
  width: 60px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.news-text { flex: 1 1 auto; }

/* publications */
.pub {
  border-left: 3px solid var(--accent);
  padding: 6px 0 6px 14px;
  margin-bottom: 18px;
}
.pub-title { font-size: 1rem; margin-bottom: 2px; }
.pub-authors { font-size: 0.93rem; color: var(--text-primary); margin-bottom: 2px; }
.pub-venue { font-size: 0.93rem; color: var(--text-muted); margin-bottom: 6px; }
.pub-note { font-size: 0.85rem; color: var(--accent); margin-bottom: 6px; }
.pub-btns { font-family: var(--font-mono); font-size: 0.8rem; }
.pub-btn {
  display: inline-block;
  padding: 1px 6px;
  margin-right: 4px;
  border: 1px solid var(--border-light);
  border-radius: 3px;
  color: var(--text-muted);
  background: var(--code-bg);
}
.pub-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
  text-decoration: none;
}

/* year headings on /publications */
.year-heading {
  font-family: var(--font-serif-display);
  font-weight: 400;
  font-size: 1.6rem;
  margin: 28px 0 12px 0;
  color: var(--text-primary);
}

/* students */
.group-label {
  font-style: italic;
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 6px;
}
.student-list { padding-left: 20px; margin: 6px 0 14px 0; }
.student-list li { margin-bottom: 3px; font-size: 0.95rem; }
.muted { color: var(--text-muted); }

/* prospective students block */
.prospective {
  border: 1px solid var(--border-light);
  border-left: 4px solid var(--accent);
  background: var(--code-bg);
  padding: 14px 18px;
  margin: 28px 0;
  font-size: 0.95rem;
}
.prospective.not-accepting { border-left-color: var(--text-muted); }
.prospective-label {
  font-weight: 600;
  margin-bottom: 6px;
  text-transform: lowercase;
  letter-spacing: 0.08em;
  color: var(--accent);
}
.prospective.not-accepting .prospective-label { color: var(--text-muted); }

/* teaching */
.course-card {
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--accent);
  padding: 14px 18px;
  margin-bottom: 14px;
}
.course-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}
.course-code {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: var(--text-muted);
}
.course-title {
  font-family: var(--font-serif-display);
  font-size: 1.15rem;
  margin: 0;
}
.course-meta {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 4px;
}
.course-meta .sep { margin: 0 6px; }

/* mailing / footer */
.mailing {
  font-style: normal;
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.5;
  margin-top: 14px;
}
footer.site-footer {
  border-top: 1px solid var(--border-light);
  margin-top: 40px;
  padding-top: 16px;
  color: var(--text-muted);
  font-size: 0.85rem;
}
.last-updated { margin-top: 6px; }

@media (max-width: 600px) {
  .hero { flex-direction: column-reverse; }
  .hero-photo { width: 140px; height: 140px; }
  .topnav { flex-direction: column; align-items: flex-start; gap: 8px; }
  .nav-links .nav-link { margin-left: 0; margin-right: 14px; }
}
"""


# ---------- page builders ----------

def _page_shell(title: str, nav: str, body: str, footer: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{_esc(title)}</title>\n"
        '  <link rel="stylesheet" href="style.css">\n'
        "</head>\n"
        "<body>\n"
        '  <div class="page">\n'
        f"{nav}\n"
        f"{body}\n"
        f"{footer}\n"
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )


def _footer_html(persona: dict, include_address: bool = False) -> str:
    meta = persona.get("site_meta") or {}
    copyright_line = meta.get("copyright_line") or ""
    last = meta.get("last_updated") or ""
    addr = _mailing_address_html(persona.get("office") or {}) if include_address else ""
    last_html = f'<div class="last-updated">Last updated: {_esc(last)}</div>' if last else ""
    copy_html = f"<div>{_esc(copyright_line)}</div>" if copyright_line else ""
    return (
        '<footer class="site-footer">\n'
        f"  {addr}\n"
        f"  {copy_html}\n"
        f"  {last_html}\n"
        "</footer>"
    )


def _index_html(persona: dict, photo_filename: str | None) -> str:
    name = persona["name"]
    dept = persona.get("department", {}) or {}
    uni = persona.get("university", {}) or {}
    research = persona.get("research", {}) or {}
    social = persona.get("social", {}) or {}
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""

    nav = _nav_html(cv_present=bool((persona.get("assets") or {}).get("cv_source")),
                    brand=brand, current="about")

    pronouns = name.get("pronouns")
    pronouns_html = f'<div class="pronouns">{_esc(pronouns)}</div>' if pronouns else ""

    affiliation_parts = []
    if dept.get("name"):
        affiliation_parts.append(_esc(dept["name"]))
    if uni.get("name"):
        affiliation_parts.append(_esc(uni["name"]))
    affiliation = " · ".join(affiliation_parts)

    photo_html = ""
    if photo_filename:
        alt = (persona.get("assets") or {}).get("photo_alt") or f"Headshot of {name.get('full','')}"
        photo_html = f'<img class="hero-photo" src="{_esc(photo_filename)}" alt="{_esc(alt)}">'

    hero = (
        '<section class="hero">\n'
        '  <div class="hero-text">\n'
        f'    <h1>{_esc(name.get("full",""))}</h1>\n'
        f'    <div class="title-line">{_esc(name.get("title",""))}</div>\n'
        f'    <div class="affiliation">{affiliation}</div>\n'
        f'    {pronouns_html}\n'
        '  </div>\n'
        f"  {photo_html}\n"
        '</section>'
    )

    bio_html = f'<section class="bio">\n{_paragraphs(research.get("long_bio",""))}\n</section>' if research.get("long_bio") else ""

    contact_html = _contact_block(persona)
    socials_html = _socials_html(social)

    # News
    news = _news_items(persona)
    news_html = ""
    if news:
        rows = "".join(
            f'    <li><span class="news-date">{_format_news_date(y)}</span>'
            f'<span class="news-text">{_esc(text)}</span></li>\n'
            for y, text in news
        )
        news_html = (
            '<section class="news">\n'
            '  <h2 class="section-heading">news</h2>\n'
            f'  <ul class="news-list">\n{rows}  </ul>\n'
            '</section>'
        )

    # Selected pubs (3 most recent)
    pubs = sorted(persona.get("publications") or [], key=lambda p: p.get("year", 0), reverse=True)[:3]
    selected_html = ""
    if pubs:
        entries = "\n".join(_pub_entry_html(p, name.get("last", "")) for p in pubs)
        selected_html = (
            '<section class="selected-pubs">\n'
            '  <h2 class="section-heading">selected publications</h2>\n'
            f"{entries}\n"
            f'  <p class="more-link"><a href="publications.html">see all publications →</a></p>\n'
            '</section>'
        )

    students_html = _students_block(persona)
    prospective_html = _prospective_block(persona)

    body = "\n".join(b for b in [hero, bio_html, contact_html, socials_html,
                                 news_html, selected_html, students_html,
                                 prospective_html] if b)

    footer = _footer_html(persona, include_address=True)
    title = f"{name.get('full','')} · {uni.get('short_name') or uni.get('name','')}"
    return _page_shell(title, nav, body, footer)


def _publications_html(persona: dict) -> str:
    name = persona["name"]
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""
    nav = _nav_html(cv_present=bool((persona.get("assets") or {}).get("cv_source")),
                    brand=brand, current="publications")

    pubs = sorted(persona.get("publications") or [], key=lambda p: p.get("year", 0), reverse=True)
    by_year: dict[int, list[dict]] = {}
    for p in pubs:
        by_year.setdefault(p.get("year", 0), []).append(p)

    sections = []
    for year in sorted(by_year.keys(), reverse=True):
        entries = "\n".join(_pub_entry_html(p, name.get("last", "")) for p in by_year[year])
        sections.append(
            f'<h2 class="year-heading">{_esc(year)}</h2>\n{entries}'
        )

    header = (
        '<section class="hero">\n'
        '  <div class="hero-text">\n'
        f'    <h1>Publications</h1>\n'
        f'    <div class="affiliation">{_esc(name.get("full",""))}</div>\n'
        '  </div>\n'
        '</section>'
    )

    body = header + "\n" + "\n".join(sections) if sections else header
    footer = _footer_html(persona, include_address=True)
    return _page_shell(f"Publications · {name.get('full','')}", nav, body, footer)


def _teaching_html(persona: dict) -> str:
    name = persona["name"]
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""
    nav = _nav_html(cv_present=bool((persona.get("assets") or {}).get("cv_source")),
                    brand=brand, current="teaching")

    # Semester ordering: try to put most-recent-looking semesters first, based on year in string.
    def semester_sort_key(course: dict) -> tuple:
        sem = course.get("semester", "")
        year = 0
        for tok in sem.split():
            if tok.isdigit():
                year = int(tok)
                break
        season_order = {"Fall": 2, "Summer": 1, "Spring": 0, "Winter": -1}
        season = 0
        for k, v in season_order.items():
            if k in sem:
                season = v
                break
        return (year, season)

    courses = sorted(persona.get("teaching") or [], key=semester_sort_key, reverse=True)

    cards = []
    for c in courses:
        meta_bits = []
        if c.get("semester"):
            meta_bits.append(_esc(c["semester"]))
        if c.get("room"):
            meta_bits.append(_esc(c["room"]))
        if c.get("days"):
            meta_bits.append(_esc(c["days"]))
        if c.get("level"):
            meta_bits.append(_esc(c["level"]))
        meta = '<span class="sep">·</span>'.join(meta_bits)
        cards.append(
            '<article class="course-card">\n'
            '  <div class="course-header">\n'
            f'    <h3 class="course-title">{_esc(c.get("title",""))}</h3>\n'
            f'    <span class="course-code">{_esc(c.get("code",""))}</span>\n'
            '  </div>\n'
            f'  <div class="course-meta">{meta}</div>\n'
            '</article>'
        )

    header = (
        '<section class="hero">\n'
        '  <div class="hero-text">\n'
        f'    <h1>Teaching</h1>\n'
        f'    <div class="affiliation">{_esc(name.get("full",""))}</div>\n'
        '  </div>\n'
        '</section>'
    )

    body = header + "\n" + "\n".join(cards) if cards else header
    footer = _footer_html(persona, include_address=False)
    return _page_shell(f"Teaching · {name.get('full','')}", nav, body, footer)


# ---------- public entrypoint ----------

def render(persona: dict, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy headshot if present.
    photo_filename = None
    assets = persona.get("assets") or {}
    photo_source = assets.get("photo_source")
    if photo_source:
        # photo_source is relative to the personas folder. Resolve via module-level constant
        # supplied by build.py; fall back to searching common locations.
        personas_root = _resolve_personas_root(photo_source)
        src = personas_root / photo_source if personas_root else Path(photo_source)
        if src.exists():
            ext = src.suffix.lower() or ".jpg"
            photo_filename = f"headshot{ext}"
            shutil.copyfile(src, out_dir / photo_filename)

    # Copy group photo if present.
    group = persona.get("group") or {}
    if group.get("group_photo_source"):
        gp = group["group_photo_source"]
        personas_root = _resolve_personas_root(gp)
        src = personas_root / gp if personas_root else Path(gp)
        if src.exists():
            shutil.copyfile(src, out_dir / Path(gp).name)

    (out_dir / "style.css").write_text(CSS, encoding="utf-8")
    (out_dir / "index.html").write_text(_index_html(persona, photo_filename), encoding="utf-8")
    (out_dir / "publications.html").write_text(_publications_html(persona), encoding="utf-8")
    (out_dir / "teaching.html").write_text(_teaching_html(persona), encoding="utf-8")


def _resolve_personas_root(rel_path: str) -> Path | None:
    """Walk up from cwd to find a folder that contains rel_path under a 'personas' or 'Personas' dir."""
    candidates = [Path.cwd() / "Personas", Path.cwd() / "personas"]
    # Also try repo root based on this file's location.
    here = Path(__file__).resolve().parent.parent
    candidates.extend([here / "Personas", here / "personas"])
    for c in candidates:
        if (c / rel_path).exists():
            return c
    return None
