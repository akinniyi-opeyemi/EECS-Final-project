"""Notion public-page pastiche template.

Renders a persona as a single long-scroll page mimicking a Notion public
document: cover band with deterministic gradient, large page icon
(headshot, circular) overlapping the bottom of the cover, left-aligned
narrow reading column, emoji-prefixed section headings, `<details>` toggle
blocks for the mailing address and teaching semesters, and an inline
database-style table for publications.

Design choice for the page icon: we use the persona's headshot (circular,
~100px) as the icon, overlapping the cover. The spec allows either emoji
or headshot; since every persona has a real photo, the headshot feels more
personal and matches what humanities academics often do on Notion.
"""

from __future__ import annotations

import hashlib
import html
import shutil
from datetime import date
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
    return "\n".join(f"  <p>{_esc(p)}</p>" for p in parts)


def _resolve_personas_root(rel_path: str) -> Path | None:
    candidates = [Path.cwd() / "Personas", Path.cwd() / "personas"]
    here = Path(__file__).resolve().parent.parent
    candidates.extend([here / "Personas", here / "personas"])
    for c in candidates:
        if (c / rel_path).exists():
            return c
    return None


# ---------- deterministic gradient ----------

def _name_gradient(full_name: str) -> str:
    """Pick two pastel-ish hues from a stable hash of the name."""
    h = hashlib.md5(full_name.encode("utf-8")).digest()
    hue_a = h[0] * 360 // 255
    hue_b = (hue_a + 40 + (h[1] % 60)) % 360
    sat = 65
    light_a = 72
    light_b = 62
    angle = 100 + (h[2] % 80)
    color_a = f"hsl({hue_a}, {sat}%, {light_a}%)"
    color_b = f"hsl({hue_b}, {sat}%, {light_b}%)"
    return f"linear-gradient({angle}deg, {color_a} 0%, {color_b} 100%)"


# ---------- semester logic ----------

def _semester_bounds(sem: str) -> tuple[date, date] | None:
    year = None
    for tok in sem.split():
        if tok.isdigit() and len(tok) == 4:
            year = int(tok)
            break
    if year is None:
        return None
    if "Spring" in sem:
        return date(year, 1, 15), date(year, 5, 20)
    if "Summer" in sem:
        return date(year, 5, 21), date(year, 8, 15)
    if "Fall" in sem:
        return date(year, 8, 16), date(year, 12, 20)
    if "Winter" in sem:
        return date(year, 12, 21), date(year + 1, 1, 14)
    return date(year, 1, 1), date(year, 12, 31)


def _parse_last_updated(meta: dict) -> date | None:
    s = (meta or {}).get("last_updated")
    if not s:
        return None
    try:
        parts = [int(p) for p in s.split("-")]
        return date(parts[0], parts[1], parts[2])
    except Exception:
        return None


def _current_semester(persona: dict) -> str | None:
    """Determine the 'current' semester deterministically from site_meta.last_updated.

    If last_updated falls inside a semester that appears in teaching, return it.
    Otherwise return the next upcoming semester after last_updated. If no
    last_updated, return the semester with the most courses.
    """
    teaching = persona.get("teaching") or []
    semesters = [c.get("semester") for c in teaching if c.get("semester")]
    if not semesters:
        return None
    ref = _parse_last_updated(persona.get("site_meta") or {})
    if ref is None:
        # fallback: semester with the most courses, then first by sort order
        counts: dict[str, int] = {}
        for s in semesters:
            counts[s] = counts.get(s, 0) + 1
        return max(counts.keys(), key=lambda s: (counts[s], _sem_sort_key(s)))

    # containing semester wins
    for s in semesters:
        b = _semester_bounds(s)
        if b and b[0] <= ref <= b[1]:
            return s

    # else earliest upcoming
    upcoming = [(s, _semester_bounds(s)) for s in semesters if _semester_bounds(s)]
    upcoming = [(s, b) for s, b in upcoming if b[0] > ref]
    if upcoming:
        upcoming.sort(key=lambda x: x[1][0])
        return upcoming[0][0]
    # else most recent past
    past = [(s, _semester_bounds(s)) for s in semesters if _semester_bounds(s)]
    past.sort(key=lambda x: x[1][0], reverse=True)
    return past[0][0] if past else None


def _sem_sort_key(sem: str) -> tuple:
    year = 0
    for tok in sem.split():
        if tok.isdigit():
            year = int(tok)
            break
    order = {"Winter": -1, "Spring": 0, "Summer": 1, "Fall": 2}
    season = 0
    for k, v in order.items():
        if k in sem:
            season = v
            break
    return (year, season)


# ---------- blocks ----------

def _breadcrumb(name_full: str) -> str:
    return f'<div class="breadcrumb">📄  {_esc(name_full)}</div>'


def _cover_and_icon(persona: dict, photo_filename: str | None) -> str:
    name = persona.get("name", {}) or {}
    grad = _name_gradient(name.get("full", "Unknown"))
    if photo_filename:
        alt = (persona.get("assets") or {}).get("photo_alt") or f"Portrait of {name.get('full','')}"
        icon_html = f'<img class="page-icon" src="{_esc(photo_filename)}" alt="{_esc(alt)}">'
    else:
        icon_html = '<div class="page-icon page-icon-emoji">📖</div>'
    return (
        f'<div class="cover" style="background: {grad};"></div>\n'
        f'<div class="page-icon-wrap">{icon_html}</div>'
    )


def _title_block(persona: dict) -> str:
    name = persona.get("name", {}) or {}
    dept = persona.get("department", {}) or {}
    uni = persona.get("university", {}) or {}
    sub_parts = []
    if name.get("title"):
        sub_parts.append(_esc(name["title"]))
    if dept.get("name"):
        sub_parts.append(_esc(dept["name"]))
    if uni.get("name"):
        sub_parts.append(_esc(uni["name"]))
    sub = " · ".join(sub_parts)
    pronouns = name.get("pronouns")
    pronouns_html = f' <span class="pronouns">({_esc(pronouns)})</span>' if pronouns else ""
    return (
        f'<h1 class="page-title">{_esc(name.get("full",""))}{pronouns_html}</h1>\n'
        f'<div class="page-subtitle">{sub}</div>'
    )


def _one_liner_quote(persona: dict) -> str:
    one = ((persona.get("research") or {}).get("one_liner")) or ""
    if not one:
        return ""
    return f'<blockquote class="pullquote">{_esc(one)}</blockquote>'


def _forthcoming_callout(persona: dict) -> str:
    pubs = persona.get("publications") or []
    ref = _parse_last_updated(persona.get("site_meta") or {})
    ref_year = ref.year if ref else None
    for p in pubs:
        note = (p.get("note") or "").lower()
        is_forthcoming = "forthcoming" in note
        if not is_forthcoming and ref_year and p.get("year") and p["year"] > ref_year:
            is_forthcoming = True
        if is_forthcoming:
            bits = []
            title = p.get("title") or ""
            publisher = p.get("publisher") or p.get("venue") or ""
            year = p.get("year")
            msg = f"Currently working on <em>{_esc(title)}</em>"
            if publisher:
                msg += f", forthcoming from {_esc(publisher)}"
            if year:
                msg += f" ({year})"
            msg += "."
            return (
                '<div class="callout callout-yellow">\n'
                '  <span class="callout-icon">📘</span>\n'
                f'  <div class="callout-content">{msg}</div>\n'
                '</div>'
            )
    return ""


def _prospective_callout(persona: dict) -> str:
    ps = persona.get("prospective_students") or {}
    if ps.get("accepting") is None:
        return ""
    note = ps.get("note") or ""
    if ps.get("accepting"):
        return (
            '<div class="callout callout-blue">\n'
            '  <span class="callout-icon">💡</span>\n'
            f'  <div class="callout-content"><strong>Prospective students:</strong> {_esc(note)}</div>\n'
            '</div>'
        )
    return (
        '<div class="callout callout-red">\n'
        '  <span class="callout-icon">⚠️</span>\n'
        f'  <div class="callout-content"><strong>Not accepting new students:</strong> {_esc(note)}</div>\n'
        '</div>'
    )


def _about_section(persona: dict) -> str:
    long_bio = ((persona.get("research") or {}).get("long_bio")) or ""
    if not long_bio:
        return ""
    return (
        '<h2 class="section-heading">👤 About</h2>\n'
        + _paragraphs(long_bio)
    )


def _mailing_address_toggle(office: dict) -> str:
    m = (office or {}).get("mailing_address") or {}
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
    return (
        '<details class="toggle">\n'
        '  <summary>Mailing address</summary>\n'
        '  <div class="toggle-body">\n'
        '    <address>' + "<br>".join(lines) + "</address>\n"
        '  </div>\n'
        '</details>'
    )


def _contact_section(persona: dict) -> str:
    office = persona.get("office") or {}
    contact = persona.get("contact") or {}
    rows = []
    if contact.get("email"):
        rows.append(f'<div class="kv"><span class="kv-ico">📧</span> <a href="mailto:{_esc(contact["email"])}">{_esc(contact["email"])}</a></div>')
    if contact.get("email_secondary"):
        rows.append(f'<div class="kv"><span class="kv-ico">📧</span> also <a href="mailto:{_esc(contact["email_secondary"])}">{_esc(contact["email_secondary"])}</a></div>')
    if office.get("building") or office.get("room"):
        parts = []
        if office.get("building"):
            parts.append(office["building"])
        if office.get("room"):
            parts.append(f"Office {office['room']}")
        rows.append(f'<div class="kv"><span class="kv-ico">🏢</span> {_esc(", ".join(parts))}</div>')
    if contact.get("phone_office"):
        rows.append(f'<div class="kv"><span class="kv-ico">📞</span> {_esc(contact["phone_office"])}</div>')
    if contact.get("phone_lab"):
        rows.append(f'<div class="kv"><span class="kv-ico">📞</span> Lab: {_esc(contact["phone_lab"])}</div>')
    if contact.get("fax"):
        rows.append(f'<div class="kv"><span class="kv-ico">📠</span> Fax: {_esc(contact["fax"])}</div>')
    if office.get("hours"):
        rows.append(f'<div class="kv"><span class="kv-ico">🕐</span> {_esc(office["hours"])}</div>')

    addr_toggle = _mailing_address_toggle(office)

    if not rows and not addr_toggle:
        return ""
    return (
        '<h2 class="section-heading">📬 Contact</h2>\n'
        + "\n".join(rows)
        + ("\n" + addr_toggle if addr_toggle else "")
    )


def _publications_db(persona: dict) -> str:
    pubs = sorted(persona.get("publications") or [], key=lambda p: p.get("year", 0), reverse=True)
    if not pubs:
        return ""
    rows = []
    for p in pubs:
        year = p.get("year", "")
        title = _esc(p.get("title", ""))
        ptype = p.get("type", "article")
        if ptype == "book":
            venue = _esc(p.get("publisher") or "")
        elif ptype == "chapter":
            book = p.get("book") or p.get("book_title") or ""
            publisher = p.get("publisher") or ""
            venue_bits = [f"<em>{_esc(book)}</em>" if book else "", _esc(publisher)]
            venue = ", ".join(b for b in venue_bits if b)
        else:
            venue = _esc(p.get("venue") or "")
            if p.get("volume"):
                v = p["volume"]
                if p.get("issue"):
                    v = f"{v}({p['issue']})"
                venue += f" {v}"
        note_html = f'<div class="db-note">{_esc(p["note"])}</div>' if p.get("note") else ""
        rows.append(
            "<tr>\n"
            f"  <td class=\"col-year\">{_esc(year)}</td>\n"
            f"  <td class=\"col-title\"><strong>{title}</strong>{note_html}</td>\n"
            f"  <td class=\"col-venue\">{venue}</td>\n"
            f"  <td class=\"col-type\"><span class=\"tag\">{_esc(ptype)}</span></td>\n"
            "</tr>"
        )

    return (
        '<h2 class="section-heading">📚 Publications</h2>\n'
        '<table class="notion-db">\n'
        '  <thead>\n'
        '    <tr><th>Year</th><th>Title</th><th>Venue</th><th>Type</th></tr>\n'
        '  </thead>\n'
        '  <tbody>\n'
        + "\n".join(rows) + "\n"
        '  </tbody>\n'
        '</table>'
    )


def _teaching_section(persona: dict) -> str:
    teaching = persona.get("teaching") or []
    if not teaching:
        return ""
    by_sem: dict[str, list[dict]] = {}
    for c in teaching:
        by_sem.setdefault(c.get("semester") or "Other", []).append(c)
    ordered_semesters = sorted(by_sem.keys(), key=_sem_sort_key, reverse=True)
    current = _current_semester(persona)

    blocks = []
    for sem in ordered_semesters:
        open_attr = " open" if sem == current else ""
        items = []
        for c in by_sem[sem]:
            meta = []
            if c.get("room"):
                meta.append(_esc(c["room"]))
            if c.get("days"):
                meta.append(_esc(c["days"]))
            if c.get("level"):
                meta.append(_esc(c["level"]))
            meta_str = " · ".join(meta)
            note = c.get("note")
            note_html = f'<div class="teach-note">{_esc(note)}</div>' if note else ""
            items.append(
                '<li class="teach-item">\n'
                f'  <span class="teach-code">{_esc(c.get("code",""))}</span> · '
                f'<span class="teach-title">{_esc(c.get("title",""))}</span>\n'
                f'  <div class="teach-meta">{meta_str}</div>\n'
                f'  {note_html}\n'
                '</li>'
            )
        blocks.append(
            f'<details class="toggle"{open_attr}>\n'
            f'  <summary>{_esc(sem)}</summary>\n'
            '  <div class="toggle-body">\n'
            '    <ul class="teach-list">\n'
            + "\n".join(items) + "\n"
            '    </ul>\n'
            '  </div>\n'
            '</details>'
        )
    return (
        '<h2 class="section-heading">🎓 Teaching</h2>\n'
        + "\n".join(blocks)
    )


def _advisees_section(persona: dict) -> str:
    group = persona.get("group") or {}
    phds = group.get("current_phd_students") or []
    ms = group.get("current_masters_students") or []
    advisees = group.get("advisees") or []
    alumni = group.get("alumni") or []
    if not (phds or ms or advisees or alumni):
        return ""

    heading = "👥 Advisees"
    if group.get("name"):
        heading = f"👥 {group['name']}"

    blocks = []
    if phds:
        items = []
        for s in phds:
            yr = f" <span class=\"muted\">(since {s['year_started']})</span>" if s.get("year_started") else ""
            topic = f" — {_esc(s['topic'])}" if s.get("topic") else ""
            items.append(f'<li><strong>{_esc(s.get("name",""))}</strong>{yr}{topic}</li>')
        blocks.append(
            '<h3 class="subsection">Doctoral students</h3>\n'
            '<ul class="bullets">' + "".join(items) + "</ul>"
        )
    if ms:
        items = []
        for s in ms:
            topic = f" — {_esc(s['topic'])}" if s.get("topic") else ""
            items.append(f'<li>{_esc(s.get("name",""))}{topic}</li>')
        blocks.append(
            '<h3 class="subsection">Masters students</h3>\n'
            '<ul class="bullets">' + "".join(items) + "</ul>"
        )
    if advisees:
        items = []
        for a in advisees:
            year = f' <span class="muted">({_esc(a["year"])})</span>' if a.get("year") else ""
            level = f' <span class="muted">({_esc(a["level"])})</span>' if a.get("level") else ""
            topic = f" — {_esc(a['topic'])}" if a.get("topic") else ""
            items.append(f'<li>{_esc(a.get("name",""))}{year}{level}{topic}</li>')
        if group.get("name") or phds or ms:
            blocks.append(
                '<h3 class="subsection">Undergraduate advisees</h3>\n'
                '<ul class="bullets">' + "".join(items) + "</ul>"
            )
        else:
            blocks.append('<ul class="bullets">' + "".join(items) + "</ul>")
    if alumni:
        items = []
        for a in alumni:
            deg = f' <span class="muted">({_esc(a["degree"])}, {_esc(a["graduated"])})</span>' if a.get("degree") or a.get("graduated") else ""
            pos = f" — {_esc(a['first_position'])}" if a.get("first_position") else ""
            items.append(f'<li>{_esc(a.get("name",""))}{deg}{pos}</li>')
        blocks.append(
            '<h3 class="subsection">Alumni</h3>\n'
            '<ul class="bullets">' + "".join(items) + "</ul>"
        )
    return f'<h2 class="section-heading">{heading}</h2>\n' + "\n".join(blocks)


def _links_section(persona: dict) -> str:
    social = persona.get("social") or {}
    order = [
        ("google_scholar", "Google Scholar"),
        ("semantic_scholar", "Semantic Scholar"),
        ("github", "GitHub"),
        ("dblp", "DBLP"),
        ("orcid", "ORCID"),
        ("twitter", "Twitter"),
        ("bluesky", "Bluesky"),
        ("linkedin", "LinkedIn"),
        ("personal_blog", "Personal blog"),
    ]
    items = []
    for key, label in order:
        val = social.get(key)
        if not val:
            continue
        href = f"https://orcid.org/{val}" if key == "orcid" else val
        items.append(f'<li>{label}: <a href="{_esc(href)}">{_esc(href)}</a></li>')
    if not items:
        return ""
    return (
        '<h2 class="section-heading">🔗 Links</h2>\n'
        '<ul class="bullets">' + "".join(items) + "</ul>"
    )


def _last_edited(persona: dict) -> str:
    meta = persona.get("site_meta") or {}
    last = meta.get("last_updated")
    copyright_line = meta.get("copyright_line") or ""
    bits = []
    if last:
        bits.append(f"Last edited: {_esc(last)}")
    if copyright_line:
        bits.append(_esc(copyright_line))
    if not bits:
        return ""
    return (
        '<hr class="thin-rule">\n'
        '<div class="last-edited">' + " · ".join(bits) + "</div>"
    )


# ---------- CSS ----------

CSS = """\
/* notion pastiche */
:root {
  --background:        #ffffff;
  --text-primary:      #37352f;
  --text-secondary:    #9b9a97;
  --text-tertiary:     #b9b8b5;
  --divider:           #ededec;
  --callout-bg:        #f7f6f3;
  --callout-bg-blue:   #e7f3f8;
  --callout-bg-red:    #fbe4e4;
  --callout-bg-green:  #ddedea;
  --callout-bg-yellow: #fbf3db;
  --tag-bg:            #ededeb;
  --tag-text:          #37352f;
  --font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont,
               "Segoe UI Variable Display", "Segoe UI", Helvetica,
               "Apple Color Emoji", Arial, sans-serif;
  --font-mono: "SFMono-Regular", Menlo, Consolas, "PT Mono",
               "Liberation Mono", Courier, monospace;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--background);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.5;
}

a {
  color: var(--text-primary);
  text-decoration: underline;
  text-decoration-color: var(--text-tertiary);
  text-underline-offset: 2px;
}
a:hover {
  text-decoration-color: var(--text-primary);
}

/* breadcrumb */
.breadcrumb {
  max-width: 900px;
  margin: 0 auto;
  padding: 10px 96px;
  font-size: 13px;
  color: var(--text-secondary);
}

/* share badge */
.share-badge {
  position: absolute;
  top: 14px;
  right: 20px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* cover */
.cover {
  width: 100%;
  height: 30vh;
  min-height: 200px;
}

/* page icon overlapping cover */
.page-icon-wrap {
  max-width: 900px;
  margin: -52px auto 0 auto;
  padding: 0 96px;
  position: relative;
}
.page-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
  border: 4px solid var(--background);
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  background: var(--background);
}
.page-icon-emoji {
  width: 78px;
  height: 78px;
  border-radius: 8px;
  font-size: 72px;
  line-height: 78px;
  text-align: center;
  border: none;
  box-shadow: none;
  background: transparent;
}

/* page body (narrow reading column) */
.page-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 96px 120px 96px;
}

/* title */
.page-title {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin: 18px 0 6px 0;
}
.page-title .pronouns {
  font-size: 16px;
  font-weight: 400;
  color: var(--text-secondary);
  letter-spacing: 0;
  vertical-align: middle;
}
.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* section headings */
.section-heading {
  font-size: 30px;
  font-weight: 700;
  margin: 36px 0 8px 0;
  letter-spacing: -0.01em;
}
h3.subsection {
  font-size: 20px;
  font-weight: 700;
  margin: 20px 0 6px 0;
}

/* body paragraphs */
p {
  margin: 0 0 8px 0;
}

/* blockquote (one-liner pullquote) */
.pullquote {
  border-left: 3px solid var(--text-primary);
  margin: 18px 0;
  padding: 4px 14px;
  font-style: italic;
  font-size: 18px;
  color: var(--text-primary);
}

hr.thin-rule {
  border: none;
  border-top: 1px solid var(--divider);
  margin: 36px 0 18px 0;
}

/* callouts */
.callout {
  display: flex;
  gap: 10px;
  padding: 16px;
  margin: 12px 0;
  border-radius: 4px;
  background: var(--callout-bg);
  border: 1px solid transparent;
}
.callout-blue   { background: var(--callout-bg-blue); }
.callout-red    { background: var(--callout-bg-red); }
.callout-green  { background: var(--callout-bg-green); }
.callout-yellow { background: var(--callout-bg-yellow); }
.callout-icon { font-size: 18px; flex-shrink: 0; line-height: 1.4; }
.callout-content { flex: 1 1 auto; }

/* contact key/value rows */
.kv {
  margin: 4px 0;
  font-size: 16px;
}
.kv-ico {
  display: inline-block;
  width: 1.5em;
}

/* toggle blocks */
details.toggle {
  margin: 4px 0;
  padding: 2px 0;
}
details.toggle > summary {
  list-style: none;
  cursor: pointer;
  padding: 4px 0;
  font-size: 16px;
}
details.toggle > summary::-webkit-details-marker { display: none; }
details.toggle > summary::before {
  content: "▶";
  display: inline-block;
  margin-right: 8px;
  font-size: 10px;
  color: var(--text-secondary);
  transition: transform 0.15s ease;
}
details.toggle[open] > summary::before {
  transform: rotate(90deg);
}
.toggle-body {
  padding: 4px 0 8px 22px;
  color: var(--text-primary);
}
.toggle-body address {
  font-style: normal;
  line-height: 1.55;
  color: var(--text-primary);
}

/* inline database table */
.notion-db {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  margin: 6px 0 18px 0;
}
.notion-db th {
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 8px 10px;
  border-bottom: 1px solid var(--divider);
  border-top: 1px solid var(--divider);
}
.notion-db td {
  padding: 10px;
  border-bottom: 1px solid var(--divider);
  vertical-align: top;
}
.notion-db tr:hover td {
  background: #f7f6f3;
}
.notion-db .col-year {
  width: 60px;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}
.notion-db .col-type { width: 80px; }
.notion-db .db-note {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.tag {
  display: inline-block;
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  text-transform: lowercase;
}

/* teaching */
.teach-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.teach-item {
  margin-bottom: 10px;
}
.teach-code {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-secondary);
}
.teach-title {
  font-weight: 600;
}
.teach-meta {
  font-size: 13px;
  color: var(--text-secondary);
  margin-left: 14px;
}
.teach-note {
  font-size: 13px;
  color: var(--text-secondary);
  margin-left: 14px;
  font-style: italic;
}

/* bullets */
.bullets {
  padding-left: 24px;
  margin: 6px 0;
}
.bullets li {
  margin-bottom: 4px;
  font-size: 16px;
}

.muted { color: var(--text-secondary); font-weight: normal; }

/* last-edited */
.last-edited {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 760px) {
  .breadcrumb, .page-body, .page-icon-wrap { padding-left: 24px; padding-right: 24px; }
  .page-title { font-size: 32px; }
  .section-heading { font-size: 24px; }
}
"""


# ---------- page assembly ----------

def _page_html(persona: dict, photo_filename: str | None) -> str:
    name_full = (persona.get("name") or {}).get("full") or ""
    body_parts = [
        _title_block(persona),
        _one_liner_quote(persona),
        _forthcoming_callout(persona),
        _prospective_callout(persona),
        _about_section(persona),
        _contact_section(persona),
        _publications_db(persona),
        _teaching_section(persona),
        _advisees_section(persona),
        _links_section(persona),
        _last_edited(persona),
    ]
    body = "\n".join(b for b in body_parts if b)

    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{_esc(name_full)}</title>\n"
        '  <link rel="stylesheet" href="style.css">\n'
        "</head>\n"
        "<body>\n"
        '<div class="share-badge">Published via Notion</div>\n'
        f"{_breadcrumb(name_full)}\n"
        f"{_cover_and_icon(persona, photo_filename)}\n"
        '<main class="page-body">\n'
        f"{body}\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


# ---------- public entrypoint ----------

def render(persona: dict, out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    photo_filename = None
    assets = persona.get("assets") or {}
    photo_source = assets.get("photo_source")
    if photo_source:
        root = _resolve_personas_root(photo_source)
        src = root / photo_source if root else Path(photo_source)
        if src.exists():
            ext = src.suffix.lower() or ".jpg"
            photo_filename = f"icon{ext}"
            shutil.copyfile(src, out_dir / photo_filename)

    (out_dir / "style.css").write_text(CSS, encoding="utf-8")
    (out_dir / "index.html").write_text(_page_html(persona, photo_filename), encoding="utf-8")
