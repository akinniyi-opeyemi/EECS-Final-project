"""Hugo PaperMod / Wowchemy pastiche template.

Renders a persona as a card-heavy, warm, tinted-hero academic site typical
of the Hugo-flavored humanities/social-science pages circa 2022–2025.
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path


# ---------- small helpers ----------

def _esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _paragraphs(text: str) -> str:
    if not text:
        return ""
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n".join(f"      <p>{_esc(p)}</p>" for p in parts)


def _resolve_personas_root(rel_path: str) -> Path | None:
    candidates = [Path.cwd() / "Personas", Path.cwd() / "personas"]
    here = Path(__file__).resolve().parent.parent
    candidates.extend([here / "Personas", here / "personas"])
    for c in candidates:
        if (c / rel_path).exists():
            return c
    return None


# ---------- nav ----------

def _nav_html(brand: str) -> str:
    return (
        '<nav class="topnav">\n'
        '  <div class="nav-inner">\n'
        f'    <a class="brand" href="index.html">{_esc(brand)}</a>\n'
        '    <div class="nav-links">\n'
        '      <a class="nav-link" href="index.html">Home</a>\n'
        '      <a class="nav-link" href="publications.html">Publications</a>\n'
        '      <a class="nav-link" href="teaching.html">Teaching</a>\n'
        '      <a class="nav-link" href="index.html#contact">Contact</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</nav>'
    )


# ---------- hero ----------

def _hero_html(persona: dict, photo_filename: str | None) -> str:
    name = persona.get("name", {}) or {}
    dept = persona.get("department", {}) or {}
    uni = persona.get("university", {}) or {}
    research = persona.get("research", {}) or {}
    social = persona.get("social", {}) or {}

    photo_html = ""
    if photo_filename:
        alt = (persona.get("assets") or {}).get("photo_alt") or f"Portrait of {name.get('full','')}"
        photo_html = f'<img class="hero-photo" src="{_esc(photo_filename)}" alt="{_esc(alt)}">'

    areas = research.get("areas") or []
    pills_html = ""
    if areas:
        pills = "".join(f'<span class="pill">{_esc(a)}</span>' for a in areas[:5])
        pills_html = f'<div class="pills">{pills}</div>'

    socials_html = _hero_socials(social)

    title_line = name.get("title") or ""
    dept_line = dept.get("name") or ""
    uni_line = uni.get("name") or ""

    return (
        '<section class="hero-band">\n'
        '  <div class="hero-inner">\n'
        f'    {photo_html}\n'
        f'    <h1 class="hero-name">{_esc(name.get("full",""))}</h1>\n'
        f'    <div class="hero-title">{_esc(title_line)}{(" · " + _esc(dept_line)) if dept_line else ""}</div>\n'
        f'    <div class="hero-uni">{_esc(uni_line)}</div>\n'
        f'    {pills_html}\n'
        f'    {socials_html}\n'
        '  </div>\n'
        '</section>'
    )


def _hero_socials(social: dict) -> str:
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
    chips = []
    for key, label in order:
        val = social.get(key)
        if not val:
            continue
        href = f"https://orcid.org/{val}" if key == "orcid" else val
        chips.append(f'<a class="social-chip" href="{_esc(href)}">{label}</a>')
    if not chips:
        return ""
    return '<div class="hero-socials">' + "".join(chips) + "</div>"


# ---------- bio card ----------

def _bio_card(persona: dict) -> str:
    research = persona.get("research", {}) or {}
    one_liner = research.get("one_liner") or ""
    long_bio = research.get("long_bio") or ""
    if not (one_liner or long_bio):
        return ""
    quote_html = f'<blockquote class="pullquote">{_esc(one_liner)}</blockquote>' if one_liner else ""
    prose = _paragraphs(long_bio)
    return (
        '<section class="card bio-card">\n'
        '  <h2 class="card-heading"><span class="emoji">📖</span> Biography</h2>\n'
        f'  {quote_html}\n'
        f'{prose}\n'
        '</section>'
    )


# ---------- contact card ----------

def _mailing_address_lines(office: dict) -> list[str]:
    m = (office or {}).get("mailing_address") or {}
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
    return lines


def _contact_card(persona: dict) -> str:
    contact = persona.get("contact") or {}
    office = persona.get("office") or {}
    rows = []
    if contact.get("email"):
        rows.append(f'<div class="c-row"><span class="ico">✉</span> <a href="mailto:{_esc(contact["email"])}">{_esc(contact["email"])}</a></div>')
    if contact.get("email_secondary"):
        rows.append(f'<div class="c-row"><span class="ico">✉</span> also <a href="mailto:{_esc(contact["email_secondary"])}">{_esc(contact["email_secondary"])}</a></div>')
    if office.get("building") or office.get("room"):
        parts = []
        if office.get("building"):
            parts.append(office["building"])
        if office.get("room"):
            parts.append(f"Room {office['room']}")
        rows.append(f'<div class="c-row"><span class="ico">📍</span> {_esc(", ".join(parts))}</div>')
    if contact.get("phone_office"):
        rows.append(f'<div class="c-row"><span class="ico">☎</span> {_esc(contact["phone_office"])}</div>')
    if contact.get("phone_lab"):
        rows.append(f'<div class="c-row"><span class="ico">☎</span> Lab: {_esc(contact["phone_lab"])}</div>')
    if contact.get("fax"):
        rows.append(f'<div class="c-row"><span class="ico">🖷</span> Fax: {_esc(contact["fax"])}</div>')
    if office.get("hours"):
        rows.append(f'<div class="c-row"><span class="ico">🕑</span> <strong>Office hours:</strong> {_esc(office["hours"])}</div>')

    addr_lines = _mailing_address_lines(office)
    addr_html = ""
    if addr_lines:
        addr_html = (
            '<div class="c-mailing"><div class="c-mailing-label">Mailing address</div>\n'
            '<address>' + "<br>".join(addr_lines) + "</address></div>"
        )

    if not rows and not addr_html:
        return ""
    return (
        '<section id="contact" class="card contact-card">\n'
        '  <h2 class="card-heading"><span class="emoji">✉</span> Contact</h2>\n'
        '  ' + "\n  ".join(rows) + "\n"
        f'  {addr_html}\n'
        '</section>'
    )


# ---------- publications ----------

TYPE_COLORS = {
    "article": "#2a6f6f",
    "book": "#8b4513",
    "chapter": "#b8860b",
    "review": "#6b7280",
}

TYPE_LABEL = {
    "article": "article",
    "book": "book",
    "chapter": "chapter",
    "review": "review",
}


def _pub_card(pub: dict) -> str:
    ptype = pub.get("type", "article")
    color = TYPE_COLORS.get(ptype, "#2a6f6f")
    year = pub.get("year")
    year_short = f"{year % 100:02d}" if isinstance(year, int) else ""

    title = _esc(pub.get("title", ""))
    authors_raw = pub.get("authors") or []
    # For chapters with no authors, fall back to editors with an "ed." prefix.
    if not authors_raw and pub.get("type") == "chapter" and pub.get("editors"):
        authors_line = "Edited by " + ", ".join(_esc(e) for e in pub["editors"])
        authors_html = f'<div class="pub-authors">{authors_line}</div>'
    elif authors_raw:
        authors_html = '<div class="pub-authors">' + ", ".join(_esc(a) for a in authors_raw) + "</div>"
    else:
        authors_html = ""

    # venue/meta line
    meta_bits = []
    if ptype == "book":
        if pub.get("publisher"):
            meta_bits.append(_esc(pub["publisher"]))
        if year:
            meta_bits.append(str(year))
        if pub.get("isbn"):
            meta_bits.append(f"ISBN {_esc(pub['isbn'])}")
    elif ptype == "chapter":
        book = pub.get("book") or pub.get("book_title")
        if book:
            meta_bits.append(f"In <em>{_esc(book)}</em>")
        if pub.get("editors"):
            meta_bits.append("ed. " + ", ".join(_esc(e) for e in pub["editors"]))
        if pub.get("publisher"):
            meta_bits.append(_esc(pub["publisher"]))
        if year:
            meta_bits.append(str(year))
        if pub.get("pages"):
            meta_bits.append(f"pp. {_esc(pub['pages'])}")
    else:
        if pub.get("venue"):
            meta_bits.append(_esc(pub["venue"]))
        if year:
            meta_bits.append(str(year))
        if pub.get("volume"):
            vol = pub["volume"]
            if pub.get("issue"):
                vol = f"{vol}({pub['issue']})"
            meta_bits.append(_esc(vol))
        if pub.get("pages"):
            meta_bits.append(_esc(pub["pages"]))
    meta_line = " · ".join(meta_bits)

    # button row
    btns = [f'<span class="type-pill type-{ptype}">{TYPE_LABEL.get(ptype, ptype)}</span>']
    if pub.get("pdf_source"):
        btns.append(f'<a class="pub-btn" href="{_esc(pub["pdf_source"])}">pdf</a>')
    if pub.get("bibtex_source"):
        btns.append(f'<a class="pub-btn" href="{_esc(pub["bibtex_source"])}">bib</a>')
    if pub.get("code_url"):
        btns.append(f'<a class="pub-btn" href="{_esc(pub["code_url"])}">code</a>')

    note_html = ""
    if pub.get("note"):
        note_html = f'<div class="pub-note">{_esc(pub["note"])}</div>'

    return (
        '<article class="pub-card">\n'
        f'  <div class="pub-thumb" style="background:{color};">{year_short}</div>\n'
        '  <div class="pub-body">\n'
        f'    <div class="pub-title">{title}</div>\n'
        f'    {authors_html}\n'
        f'    <div class="pub-meta">{meta_line}</div>\n'
        f'    {note_html}\n'
        f'    <div class="pub-btns">{" ".join(btns)}</div>\n'
        '  </div>\n'
        '</article>'
    )


def _recent_pubs_card(persona: dict) -> str:
    pubs = sorted(persona.get("publications") or [], key=lambda p: p.get("year", 0), reverse=True)[:3]
    if not pubs:
        return ""
    cards = "\n".join(_pub_card(p) for p in pubs)
    return (
        '<section class="card pubs-card">\n'
        '  <h2 class="card-heading"><span class="emoji">📚</span> Recent Publications</h2>\n'
        f'  {cards}\n'
        '  <p class="see-all"><a href="publications.html">See all publications →</a></p>\n'
        '</section>'
    )


# ---------- teaching ----------

def _semester_sort_key(course: dict) -> tuple:
    sem = course.get("semester", "") or ""
    year = 0
    for tok in sem.split():
        if tok.isdigit():
            year = int(tok)
            break
    season_order = {"Winter": -1, "Spring": 0, "Summer": 1, "Fall": 2}
    season = 0
    for k, v in season_order.items():
        if k in sem:
            season = v
            break
    return (year, season)


def _course_card(c: dict) -> str:
    meta_bits = []
    if c.get("semester"):
        meta_bits.append(_esc(c["semester"]))
    if c.get("room"):
        meta_bits.append(_esc(c["room"]))
    if c.get("days"):
        meta_bits.append(_esc(c["days"]))
    if c.get("level"):
        meta_bits.append(_esc(c["level"]))
    meta = " · ".join(meta_bits)
    return (
        '<article class="course-card">\n'
        f'  <div class="course-code">{_esc(c.get("code",""))}</div>\n'
        f'  <div class="course-title">{_esc(c.get("title",""))}</div>\n'
        f'  <div class="course-meta">{meta}</div>\n'
        '</article>'
    )


def _teaching_home_card(persona: dict) -> str:
    courses = sorted(persona.get("teaching") or [], key=_semester_sort_key, reverse=True)
    if not courses:
        return ""
    shown = courses[:4]
    cards = "\n".join(_course_card(c) for c in shown)
    see_all = ""
    if len(courses) > len(shown):
        see_all = '<p class="see-all"><a href="teaching.html">See all teaching →</a></p>'
    else:
        see_all = '<p class="see-all"><a href="teaching.html">Full teaching history →</a></p>'
    return (
        '<section class="card teaching-card">\n'
        '  <h2 class="card-heading"><span class="emoji">🎓</span> Teaching</h2>\n'
        '  <div class="course-grid">\n'
        f'  {cards}\n'
        '  </div>\n'
        f'  {see_all}\n'
        '</section>'
    )


# ---------- students / advisees ----------

def _students_card(persona: dict) -> str:
    group = persona.get("group") or {}
    group_name = group.get("name")
    advisees = group.get("advisees") or []
    alumni = group.get("alumni") or []
    phds = group.get("current_phd_students") or []
    ms = group.get("current_masters_students") or []

    if group_name:
        if not (phds or ms or alumni):
            return ""
        sections = []

        # optional group photo
        photo_html = ""
        gp = group.get("group_photo_source")
        if gp:
            # build.render copies the photo to the output dir using its basename
            photo_html = f'<img class="group-photo" src="{_esc(Path(gp).name)}" alt="{_esc(group.get("group_photo_caption") or group_name)}">'

        if phds:
            rows = []
            for s in phds:
                topic = f" — {_esc(s['topic'])}" if s.get("topic") else ""
                yr = f" <span class=\"muted\">(since {s['year_started']})</span>" if s.get("year_started") else ""
                rows.append(f'<li><strong>{_esc(s.get("name",""))}</strong>{yr}{topic}</li>')
            sections.append('<h3 class="sub-heading">Doctoral students</h3>\n<ul class="student-list">' + "".join(rows) + "</ul>")
        if ms:
            rows = []
            for s in ms:
                topic = f" — {_esc(s['topic'])}" if s.get("topic") else ""
                rows.append(f'<li>{_esc(s.get("name",""))}{topic}</li>')
            sections.append('<h3 class="sub-heading">Masters students</h3>\n<ul class="student-list">' + "".join(rows) + "</ul>")
        if alumni:
            sections.append('<h3 class="sub-heading">Former Students</h3>\n' + _alumni_list(alumni))

        return (
            '<section class="card students-card">\n'
            f'  <h2 class="card-heading"><span class="emoji">👥</span> {_esc(group_name)}</h2>\n'
            f'  {photo_html}\n'
            '  ' + "\n  ".join(sections) + "\n"
            '</section>'
        )

    # No group.name → humanities-style Current Advisees card
    blocks = []
    if advisees:
        rows = []
        for a in advisees:
            name = _esc(a.get("name", ""))
            year = f' <span class="muted">({_esc(a["year"])})</span>' if a.get("year") else ""
            level = f' <span class="muted">({_esc(a["level"])})</span>' if a.get("level") else ""
            topic = f" — {_esc(a['topic'])}" if a.get("topic") else ""
            rows.append(f"<li>{name}{year}{level}{topic}</li>")
        blocks.append('<ul class="student-list">' + "".join(rows) + "</ul>")
    if alumni:
        blocks.append('<h3 class="sub-heading">Former Students</h3>\n' + _alumni_list(alumni))

    if not blocks:
        return ""
    return (
        '<section class="card students-card">\n'
        '  <h2 class="card-heading"><span class="emoji">👥</span> Current Advisees</h2>\n'
        '  ' + "\n  ".join(blocks) + "\n"
        '</section>'
    )


def _alumni_list(alumni: list[dict]) -> str:
    rows = []
    for a in alumni:
        name = _esc(a.get("name", ""))
        deg = f' <span class="muted">({_esc(a["degree"])}, {_esc(a["graduated"])})</span>' if a.get("degree") or a.get("graduated") else ""
        pos = f" — now {_esc(a['first_position'])}" if a.get("first_position") else ""
        thesis = f'<div class="muted thesis">“{_esc(a["thesis"])}”</div>' if a.get("thesis") else ""
        rows.append(f"<li>{name}{deg}{pos}{thesis}</li>")
    return '<ul class="student-list alumni">' + "".join(rows) + "</ul>"


# ---------- prospective students ----------

def _prospective_card(persona: dict) -> str:
    ps = persona.get("prospective_students") or {}
    if ps.get("accepting") is None:
        return ""
    note = ps.get("note") or ""
    accepting = bool(ps.get("accepting"))
    cls = "prospective-card accepting" if accepting else "prospective-card not-accepting"
    label = "Prospective Students" if accepting else "Not Accepting Students"
    emoji = "🎓" if accepting else "⏸"
    return (
        f'<section class="card {cls}">\n'
        f'  <h2 class="card-heading"><span class="emoji">{emoji}</span> {label}</h2>\n'
        f'  <p>{_esc(note)}</p>\n'
        '</section>'
    )


# ---------- footer ----------

def _footer_html(persona: dict) -> str:
    uni = persona.get("university", {}) or {}
    office = persona.get("office") or {}
    social = persona.get("social") or {}
    meta = persona.get("site_meta") or {}
    name = persona.get("name", {}) or {}

    research = persona.get("research", {}) or {}
    about_blurb = research.get("one_liner") or ""

    addr_lines = _mailing_address_lines(office)
    addr_html = "<br>".join(addr_lines)

    social_order = [
        ("google_scholar", "Google Scholar"),
        ("semantic_scholar", "Semantic Scholar"),
        ("github", "GitHub"),
        ("dblp", "DBLP"),
        ("orcid", "ORCID"),
        ("twitter", "Twitter"),
        ("bluesky", "Bluesky"),
        ("linkedin", "LinkedIn"),
        ("personal_blog", "Blog"),
    ]
    social_items = []
    for key, label in social_order:
        val = social.get(key)
        if not val:
            continue
        href = f"https://orcid.org/{val}" if key == "orcid" else val
        social_items.append(f'<li><a href="{_esc(href)}">{label}</a></li>')
    social_html = "<ul class=\"foot-list\">" + "".join(social_items) + "</ul>" if social_items else ""

    copyright_line = meta.get("copyright_line") or ""
    last = meta.get("last_updated") or ""
    last_html = f'<span class="muted"> · Last updated {_esc(last)}</span>' if last else ""

    return (
        '<footer class="site-footer">\n'
        '  <div class="footer-cols">\n'
        '    <div class="foot-col">\n'
        '      <div class="foot-heading">About</div>\n'
        f'      <p class="foot-about">{_esc(about_blurb)}</p>\n'
        f'      <p class="foot-about muted">{_esc(name.get("full",""))} · {_esc(uni.get("name",""))}</p>\n'
        '    </div>\n'
        '    <div class="foot-col">\n'
        '      <div class="foot-heading">Contact</div>\n'
        f'      <address>{addr_html}</address>\n'
        '    </div>\n'
        '    <div class="foot-col">\n'
        '      <div class="foot-heading">Elsewhere</div>\n'
        f'      {social_html}\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="foot-copy">\n'
        f'    <span>{_esc(copyright_line)}</span>\n'
        f'    {last_html}\n'
        '  </div>\n'
        '</footer>'
    )


# ---------- CSS ----------

CSS = """\
/* hugo_papermod pastiche */
:root {
  --background:      #fafaf7;
  --surface:         #ffffff;
  --surface-alt:     #f0eee8;
  --text-primary:    #1f2937;
  --text-secondary:  #4b5563;
  --text-muted:      #9ca3af;
  --accent:          #2a6f6f;
  --accent-dark:     #1f5757;
  --accent-soft:     #d4e6e6;
  --border:          #e5e7eb;
  --shadow:          0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-strong:   0 4px 16px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.05);
  --font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-serif: Georgia, "Times New Roman", serif;
  --radius: 10px;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--background);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.65;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-dark); }

/* top nav */
.topnav {
  position: sticky;
  top: 0;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(6px);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}
.nav-inner {
  max-width: 1080px;
  margin: 0 auto;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}
.nav-links .nav-link {
  color: var(--text-secondary);
  margin-left: 22px;
  font-size: 0.95rem;
  font-weight: 500;
}
.nav-links .nav-link:hover {
  color: var(--accent);
}

/* hero band */
.hero-band {
  background: var(--surface-alt);
  border-bottom: 1px solid var(--border);
  padding: 56px 24px 48px 24px;
}
.hero-inner {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}
.hero-photo {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--surface);
  box-shadow: var(--shadow-strong);
  margin-bottom: 18px;
}
.hero-name {
  font-size: 2.1rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.01em;
}
.hero-title {
  color: var(--text-secondary);
  font-size: 1.05rem;
  margin-bottom: 4px;
}
.hero-uni {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-bottom: 18px;
}

/* research pill tags */
.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin: 14px 0 18px 0;
}
.pill {
  display: inline-block;
  padding: 4px 12px;
  background: var(--accent-soft);
  color: var(--accent-dark);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 500;
}

/* hero socials */
.hero-socials {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}
.social-chip {
  display: inline-block;
  padding: 5px 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.social-chip:hover {
  color: var(--accent);
  border-color: var(--accent);
}

/* main content */
main.content, .content {
  max-width: 960px;
  margin: 32px auto;
  padding: 0 24px;
}

/* cards */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px 28px;
  margin-bottom: 20px;
}
.card-heading {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 14px 0;
  letter-spacing: -0.005em;
}
.card-heading .emoji {
  margin-right: 6px;
}
.sub-heading {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 16px 0 6px 0;
}

/* bio */
.bio-card .pullquote {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 1.15rem;
  color: var(--accent-dark);
  border-left: 3px solid var(--accent);
  margin: 0 0 16px 0;
  padding: 6px 14px;
  background: var(--accent-soft);
  border-radius: 4px;
}
.bio-card p {
  margin: 0 0 12px 0;
}

/* two-column row for bio + contact */
.row-two {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 20px;
}
.row-two > .card { margin-bottom: 0; }

/* contact card */
.contact-card .c-row {
  margin-bottom: 6px;
  font-size: 0.95rem;
}
.contact-card .c-row .ico {
  display: inline-block;
  width: 1.4em;
  color: var(--accent);
}
.c-mailing {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.c-mailing-label {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.c-mailing address {
  font-style: normal;
  line-height: 1.55;
}

/* publications */
.pub-card {
  display: flex;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  align-items: flex-start;
}
.pub-card:last-child { border-bottom: none; }
.pub-thumb {
  flex: 0 0 auto;
  width: 64px;
  height: 64px;
  border-radius: 8px;
  color: #fff;
  font-weight: 700;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.pub-body { flex: 1 1 auto; min-width: 0; }
.pub-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 2px;
  line-height: 1.35;
}
.pub-authors {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 2px;
}
.pub-meta {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.pub-note {
  font-size: 0.85rem;
  color: var(--accent);
  margin-bottom: 6px;
}
.pub-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.type-pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  color: #fff;
  text-transform: lowercase;
  letter-spacing: 0.02em;
}
.type-article { background: #2a6f6f; }
.type-book    { background: #8b4513; }
.type-chapter { background: #b8860b; }
.type-review  { background: #6b7280; }
.pub-btn {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}
.pub-btn:hover { color: var(--accent); border-color: var(--accent); }

.see-all {
  margin: 14px 0 0 0;
  font-size: 0.9rem;
}

/* year/type group heading on publications page */
.pub-group-heading {
  font-size: 1rem;
  font-weight: 700;
  margin: 24px 0 8px 0;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.pub-group-heading:first-of-type { margin-top: 0; }

/* teaching */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}
.course-card {
  background: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
}
.course-code {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.course-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 6px;
  line-height: 1.3;
}
.course-meta {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* students / advisees */
.student-list {
  margin: 6px 0 4px 0;
  padding-left: 20px;
}
.student-list li {
  margin-bottom: 4px;
  font-size: 0.95rem;
}
.student-list.alumni li { color: var(--text-secondary); }
.thesis { font-style: italic; font-size: 0.85rem; }
.muted { color: var(--text-muted); font-weight: normal; }
.group-photo {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 12px;
}

/* prospective students */
.prospective-card.accepting {
  border-left: 4px solid var(--accent);
  background: linear-gradient(to right, var(--accent-soft) 0%, var(--surface) 40%);
}
.prospective-card.not-accepting {
  border-left: 4px solid var(--text-muted);
  background: var(--surface-alt);
}

/* page hero on subpages */
.page-hero {
  background: var(--surface-alt);
  border-bottom: 1px solid var(--border);
  padding: 32px 24px;
  text-align: center;
}
.page-hero h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
}
.page-hero .sub {
  color: var(--text-muted);
  margin-top: 4px;
  font-size: 0.95rem;
}

/* footer */
.site-footer {
  background: var(--surface-alt);
  border-top: 1px solid var(--border);
  margin-top: 48px;
  padding: 36px 24px 20px 24px;
}
.footer-cols {
  max-width: 960px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1.2fr 1fr;
  gap: 36px;
}
.foot-heading {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.foot-about { font-size: 0.9rem; color: var(--text-secondary); margin: 0 0 6px 0; }
.foot-col address { font-style: normal; font-size: 0.88rem; color: var(--text-secondary); line-height: 1.55; }
.foot-list { list-style: none; padding: 0; margin: 0; }
.foot-list li { font-size: 0.88rem; margin-bottom: 4px; }
.foot-copy {
  max-width: 960px;
  margin: 24px auto 0 auto;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  font-size: 0.82rem;
  color: var(--text-muted);
}

@media (max-width: 720px) {
  .row-two { grid-template-columns: 1fr; }
  .footer-cols { grid-template-columns: 1fr; gap: 20px; }
  .nav-links .nav-link { margin-left: 14px; }
  .hero-name { font-size: 1.7rem; }
}
"""


# ---------- page shells ----------

def _page_shell(title: str, nav_and_body: str) -> str:
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
        f"{nav_and_body}\n"
        "</body>\n"
        "</html>\n"
    )


def _index_html(persona: dict, photo_filename: str | None) -> str:
    name = persona.get("name", {}) or {}
    uni = persona.get("university", {}) or {}
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""

    nav = _nav_html(brand)
    hero = _hero_html(persona, photo_filename)

    bio = _bio_card(persona)
    contact = _contact_card(persona)
    # Row: bio + contact side by side when both present
    row_two = ""
    if bio and contact:
        row_two = f'<div class="row-two">\n{bio}\n{contact}\n</div>'
    else:
        row_two = bio + contact

    pubs_card = _recent_pubs_card(persona)
    teaching_card = _teaching_home_card(persona)
    students_card = _students_card(persona)
    prospective_card = _prospective_card(persona)

    body = (
        '<main class="content">\n'
        + "\n".join(b for b in [row_two, pubs_card, teaching_card, students_card, prospective_card] if b)
        + "\n</main>"
    )

    footer = _footer_html(persona)
    title = f"{name.get('full','')} — {uni.get('short_name') or uni.get('name','')}"
    return _page_shell(title, f"{nav}\n{hero}\n{body}\n{footer}")


def _publications_html(persona: dict) -> str:
    name = persona.get("name", {}) or {}
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""
    nav = _nav_html(brand)

    page_hero = (
        '<section class="page-hero">\n'
        '  <h1>Publications</h1>\n'
        f'  <div class="sub">{_esc(name.get("full",""))}</div>\n'
        '</section>'
    )

    pubs = persona.get("publications") or []
    group_order = [
        ("book", "Books"),
        ("article", "Articles"),
        ("chapter", "Chapters"),
        ("review", "Reviews"),
    ]
    grouped: dict[str, list[dict]] = {}
    for p in pubs:
        grouped.setdefault(p.get("type", "article"), []).append(p)
    for k in grouped:
        grouped[k].sort(key=lambda p: p.get("year", 0), reverse=True)

    groups_html = []
    for key, label in group_order:
        items = grouped.get(key) or []
        if not items:
            continue
        cards = "\n".join(_pub_card(p) for p in items)
        groups_html.append(
            f'<h2 class="pub-group-heading">{_esc(label)}</h2>\n'
            + '<section class="card">\n' + cards + "\n</section>"
        )

    # catch any unexpected types
    seen = {k for k, _ in group_order}
    for other_type, items in grouped.items():
        if other_type in seen or not items:
            continue
        cards = "\n".join(_pub_card(p) for p in items)
        groups_html.append(
            f'<h2 class="pub-group-heading">{_esc(other_type.title())}</h2>\n'
            + '<section class="card">\n' + cards + "\n</section>"
        )

    body = (
        '<main class="content">\n'
        + ("\n".join(groups_html) if groups_html else '<section class="card">No publications.</section>')
        + "\n</main>"
    )
    footer = _footer_html(persona)
    return _page_shell(f"Publications — {name.get('full','')}", f"{nav}\n{page_hero}\n{body}\n{footer}")


def _teaching_html(persona: dict) -> str:
    name = persona.get("name", {}) or {}
    brand = name.get("preferred") or name.get("last") or name.get("full") or ""
    nav = _nav_html(brand)

    page_hero = (
        '<section class="page-hero">\n'
        '  <h1>Teaching</h1>\n'
        f'  <div class="sub">{_esc(name.get("full",""))}</div>\n'
        '</section>'
    )

    courses = sorted(persona.get("teaching") or [], key=_semester_sort_key, reverse=True)
    if courses:
        cards = "\n".join(_course_card(c) for c in courses)
        body_inner = (
            '<section class="card">\n'
            '  <div class="course-grid">\n'
            f'{cards}\n'
            '  </div>\n'
            '</section>'
        )
    else:
        body_inner = '<section class="card">No courses listed.</section>'

    body = f'<main class="content">\n{body_inner}\n</main>'
    footer = _footer_html(persona)
    return _page_shell(f"Teaching — {name.get('full','')}", f"{nav}\n{page_hero}\n{body}\n{footer}")


# ---------- public entrypoint ----------

def render(persona: dict, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # copy headshot
    photo_filename = None
    assets = persona.get("assets") or {}
    photo_source = assets.get("photo_source")
    if photo_source:
        root = _resolve_personas_root(photo_source)
        src = root / photo_source if root else Path(photo_source)
        if src.exists():
            ext = src.suffix.lower() or ".jpg"
            photo_filename = f"headshot{ext}"
            shutil.copyfile(src, out_dir / photo_filename)

    # copy group photo
    group = persona.get("group") or {}
    if group.get("group_photo_source"):
        gp = group["group_photo_source"]
        root = _resolve_personas_root(gp)
        src = root / gp if root else Path(gp)
        if src.exists():
            shutil.copyfile(src, out_dir / Path(gp).name)

    (out_dir / "style.css").write_text(CSS, encoding="utf-8")
    (out_dir / "index.html").write_text(_index_html(persona, photo_filename), encoding="utf-8")
    (out_dir / "publications.html").write_text(_publications_html(persona), encoding="utf-8")
    (out_dir / "teaching.html").write_text(_teaching_html(persona), encoding="utf-8")
