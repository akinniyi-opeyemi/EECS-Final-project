"""Raw HTML 1998 pastiche template.

Renders a persona as a late-1990s academic homepage: HTML 4.01 Transitional
doctype, iso-8859-1 charset, table-based layout, <font> tags, presentational
attributes on <body> and <img>, obfuscated email, no nav, no CSS classes,
no <div>, no HTML5 semantic tags. Intentionally anachronistic — the whole
point is that a visual inspector should immediately say "this looks wrong
for 2026."
"""

from __future__ import annotations

import shutil
from pathlib import Path


# ---------- entity encoding ----------

# Latin-1 named character references (HTML 4.01). Used so that non-ASCII
# characters like ö render as &ouml; — the period-accurate way to include
# diacritics on an iso-8859-1 page.
_NAMED_ENTITIES = {
    0xA0: "nbsp", 0xA1: "iexcl", 0xA2: "cent", 0xA3: "pound", 0xA4: "curren",
    0xA5: "yen", 0xA6: "brvbar", 0xA7: "sect", 0xA8: "uml", 0xA9: "copy",
    0xAA: "ordf", 0xAB: "laquo", 0xAC: "not", 0xAD: "shy", 0xAE: "reg",
    0xAF: "macr", 0xB0: "deg", 0xB1: "plusmn", 0xB2: "sup2", 0xB3: "sup3",
    0xB4: "acute", 0xB5: "micro", 0xB6: "para", 0xB7: "middot", 0xB8: "cedil",
    0xB9: "sup1", 0xBA: "ordm", 0xBB: "raquo", 0xBC: "frac14", 0xBD: "frac12",
    0xBE: "frac34", 0xBF: "iquest",
    0xC0: "Agrave", 0xC1: "Aacute", 0xC2: "Acirc", 0xC3: "Atilde", 0xC4: "Auml",
    0xC5: "Aring", 0xC6: "AElig", 0xC7: "Ccedil", 0xC8: "Egrave", 0xC9: "Eacute",
    0xCA: "Ecirc", 0xCB: "Euml", 0xCC: "Igrave", 0xCD: "Iacute", 0xCE: "Icirc",
    0xCF: "Iuml", 0xD0: "ETH", 0xD1: "Ntilde", 0xD2: "Ograve", 0xD3: "Oacute",
    0xD4: "Ocirc", 0xD5: "Otilde", 0xD6: "Ouml", 0xD7: "times", 0xD8: "Oslash",
    0xD9: "Ugrave", 0xDA: "Uacute", 0xDB: "Ucirc", 0xDC: "Uuml", 0xDD: "Yacute",
    0xDE: "THORN", 0xDF: "szlig",
    0xE0: "agrave", 0xE1: "aacute", 0xE2: "acirc", 0xE3: "atilde", 0xE4: "auml",
    0xE5: "aring", 0xE6: "aelig", 0xE7: "ccedil", 0xE8: "egrave", 0xE9: "eacute",
    0xEA: "ecirc", 0xEB: "euml", 0xEC: "igrave", 0xED: "iacute", 0xEE: "icirc",
    0xEF: "iuml", 0xF0: "eth", 0xF1: "ntilde", 0xF2: "ograve", 0xF3: "oacute",
    0xF4: "ocirc", 0xF5: "otilde", 0xF6: "ouml", 0xF7: "divide", 0xF8: "oslash",
    0xF9: "ugrave", 0xFA: "uacute", 0xFB: "ucirc", 0xFC: "uuml", 0xFD: "yacute",
    0xFE: "thorn", 0xFF: "yuml",
}


def _enc(value) -> str:
    """HTML-escape + transliterate non-ASCII to Latin-1 named entities.

    Period-accurate: the iso-8859-1 pages of the era wrote V&ouml;ssing, not
    the raw Unicode character."""
    if value is None:
        return ""
    s = str(value)
    out = []
    for ch in s:
        code = ord(ch)
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch == '"':
            out.append("&quot;")
        elif code < 128:
            out.append(ch)
        elif code in _NAMED_ENTITIES:
            out.append(f"&{_NAMED_ENTITIES[code]};")
        else:
            out.append(f"&#{code};")
    return "".join(out)


# ---------- misc helpers ----------

_MONTHS = ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]


def _format_last_updated(iso: str) -> str:
    """'2021-03-14' -> 'March 14, 2021.'"""
    try:
        y, m, d = [int(p) for p in iso.split("-")]
        return f"{_MONTHS[m]} {d}, {y}."
    except Exception:
        return iso or ""


def _obfuscate_email(email: str) -> str:
    """'vossing@econ.halvern.edu' -> 'vossing (at) econ (dot) halvern (dot) edu'"""
    if not email or "@" not in email:
        return _enc(email)
    local, _, domain = email.partition("@")
    domain_parts = domain.split(".")
    return _enc(local) + " (at) " + " (dot) ".join(_enc(p) for p in domain_parts)


def _strip_country_code(phone: str) -> str:
    """NOTE: this is the one template where we deliberately transform a
    persona field. 1998 phone numbers were rarely written with a +1.
    '+1 (419) 555-0164' -> '(419) 555-0164'."""
    if not phone:
        return ""
    s = phone.strip()
    if s.startswith("+1 "):
        return s[3:]
    if s.startswith("+1-"):
        return s[3:]
    if s.startswith("+1"):
        return s[2:].lstrip(" -")
    return s


def _sem_sort_key(sem: str) -> tuple:
    year = 0
    for tok in (sem or "").split():
        if tok.isdigit():
            year = int(tok)
            break
    order = {"Winter": -1, "Spring": 0, "Summer": 1, "Fall": 2}
    season = 0
    for k, v in order.items():
        if k in (sem or ""):
            season = v
            break
    return (year, season)


def _author_name_to_last_first(author: str) -> str:
    """'G. V\u00f6ssing' -> 'V\u00f6ssing, G.'  /  'H. Sonnenschein' -> 'Sonnenschein, H.'"""
    toks = author.strip().split()
    if len(toks) < 2:
        return author
    last = toks[-1]
    initials = " ".join(toks[:-1])
    return f"{last}, {initials}"


def _author_list(authors: list[str]) -> str:
    return ", ".join(_enc(_author_name_to_last_first(a)) for a in authors)


def _format_pub(pub: dict) -> str:
    """Format one publication as a single <li> entry in 1998-econ style.

    Example (article):
      V&ouml;ssing, G. "On the Existence of Equilibrium...," <i>Econometrica</i>,
      87(4), 2019, pp. 1201-1238.
    """
    ptype = pub.get("type", "article")
    authors_raw = pub.get("authors") or []
    authors = _author_list(authors_raw)
    title = _enc(pub.get("title", ""))
    year = pub.get("year")
    parts = []

    if ptype == "book":
        # book: Author. <i>Title</i>. Publisher, year.
        # Authors list already ends in "." from the trailing initial.
        if authors:
            parts.append(authors)
        parts.append(f"<i>{title}</i>.")
        trail = []
        if pub.get("publisher"):
            trail.append(_enc(pub["publisher"]))
        if year:
            trail.append(str(year))
        if trail:
            parts.append(", ".join(trail) + ".")
        if pub.get("note"):
            parts.append(f"({_enc(pub['note'])}).")
    elif ptype == "chapter":
        # chapter: Author. "Title," in <i>Book</i>, ed. Editors, Publisher, year, pp. pages.
        if authors:
            parts.append(authors)
        parts.append(f'"{title},"')
        book = pub.get("book") or pub.get("book_title") or ""
        parts.append(f"in <i>{_enc(book)}</i>," if book else "")
        if pub.get("editors"):
            parts.append("ed. " + ", ".join(_enc(e) for e in pub["editors"]) + ",")
        if pub.get("publisher"):
            parts.append(_enc(pub["publisher"]) + ",")
        if year:
            parts.append(f"{year}" + (", " if pub.get("pages") else "."))
        if pub.get("pages"):
            parts.append(f"pp. {_enc(pub['pages'])}.")
    elif ptype == "review":
        # review: Author. "Title," Review of <i>Venue</i>, year.
        if authors:
            parts.append(authors)
        parts.append(f'"{title},"')
        if pub.get("venue"):
            parts.append(f"<i>{_enc(pub['venue'])}</i>,")
        if year:
            parts.append(f"{year}.")
    else:
        # article (default)
        if authors:
            parts.append(authors)
        parts.append(f'"{title},"')
        if pub.get("venue"):
            parts.append(f"<i>{_enc(pub['venue'])}</i>,")
        tail = []
        if pub.get("volume"):
            v = str(pub["volume"])
            if pub.get("issue"):
                v = f"{v}({pub['issue']})"
            tail.append(v)
        if year:
            tail.append(str(year))
        if pub.get("pages"):
            tail.append(f"pp. {_enc(pub['pages'])}")
        if tail:
            parts.append(", ".join(tail) + ".")
        if pub.get("note"):
            parts.append(f"({_enc(pub['note'])}).")

    # Glue without introducing extra spaces
    out = " ".join(p for p in parts if p)
    return out


# ---------- page assembly ----------

def _heading_block(persona: dict) -> str:
    name = persona.get("name", {}) or {}
    dept = persona.get("department", {}) or {}
    uni = persona.get("university", {}) or {}
    return (
        f'<h1 align="center">{_enc(name.get("full", ""))}</h1>\n'
        f'<h3 align="center">{_enc(name.get("title", ""))}</h3>\n'
        f'<p align="center">\n'
        f'{_enc(dept.get("name", ""))}<br>\n'
        f'{_enc(uni.get("name", ""))}\n'
        f'</p>'
    )


def _bio_block(persona: dict, photo_filename: str | None) -> str:
    bio = (persona.get("research") or {}).get("long_bio") or ""
    img = ""
    if photo_filename:
        alt = (persona.get("assets") or {}).get("photo_alt") or "Photograph"
        img = (
            f'<img src="{_enc(photo_filename)}" alt="{_enc(alt)}" '
            'align="left" hspace="10" vspace="5" width="150" border="0">'
        )
    if not bio:
        return img + '<br clear="all">' if img else ""
    return (
        f'<p>{img}\n{_enc(bio)}</p>\n'
        '<br clear="all">'
    )


def _contact_block(persona: dict) -> str:
    office = persona.get("office") or {}
    contact = persona.get("contact") or {}
    m = office.get("mailing_address") or {}

    addr_lines = []
    for key in ("line1", "line2", "street", "building_line"):
        if m.get(key):
            addr_lines.append(_enc(m[key]))
    csz_bits = []
    city_state = ", ".join(s for s in [m.get("city", ""), m.get("state", "")] if s).strip(", ")
    csz_line = " ".join(s for s in [city_state, m.get("zip", "")] if s).strip()
    if csz_line:
        addr_lines.append(_enc(csz_line))
    if m.get("country"):
        addr_lines.append(_enc(m["country"]))
    address_html = "<br>\n".join(addr_lines)

    lines = [f'<font size="+1"><b>Contact Information</b></font>', "<p>"]
    if address_html:
        lines.append(address_html + "<br>")
        lines.append("&nbsp;<br>")  # blank line

    if contact.get("phone_office"):
        lines.append(f'Phone: {_enc(_strip_country_code(contact["phone_office"]))}<br>')
    if contact.get("phone_lab"):
        lines.append(f'Lab: {_enc(_strip_country_code(contact["phone_lab"]))}<br>')
    if contact.get("fax"):
        lines.append(f'Fax: {_enc(_strip_country_code(contact["fax"]))}<br>')
    if contact.get("email"):
        lines.append(f"Email: {_obfuscate_email(contact['email'])}<br>")
    if contact.get("email_secondary"):
        lines.append(f"Also: {_obfuscate_email(contact['email_secondary'])}<br>")
    if office.get("hours"):
        lines.append("&nbsp;<br>")
        lines.append(f'Office hours: {_enc(office["hours"])}<br>')

    lines.append("</p>")
    return "\n".join(lines)


def _research_interests_block(persona: dict) -> str:
    areas = (persona.get("research") or {}).get("areas") or []
    if not areas:
        return ""
    items = "\n".join(f"<li>{_enc(a)}</li>" for a in areas)
    return (
        '<font size="+1"><b>Research Interests</b></font>\n'
        f'<ul>\n{items}\n</ul>'
    )


def _publications_block(persona: dict) -> str:
    pubs = sorted(persona.get("publications") or [], key=lambda p: p.get("year", 0), reverse=True)
    if not pubs:
        return ""
    items = "\n".join(f"<li>{_format_pub(p)}</li>" for p in pubs)
    return (
        '<font size="+1"><b>Publications</b></font>\n'
        f'<ol>\n{items}\n</ol>'
    )


def _teaching_block(persona: dict) -> str:
    teaching = persona.get("teaching") or []
    if not teaching:
        return ""
    by_sem: dict[str, list[dict]] = {}
    for c in teaching:
        by_sem.setdefault(c.get("semester") or "Other", []).append(c)
    ordered = sorted(by_sem.keys(), key=_sem_sort_key, reverse=True)

    chunks = ['<font size="+1"><b>Teaching</b></font>']
    for sem in ordered:
        chunks.append(f'<p><b>{_enc(sem)}:</b><br>')
        lines = []
        for c in by_sem[sem]:
            code = _enc(c.get("code", ""))
            title = _enc(c.get("title", ""))
            meta = []
            if c.get("room"):
                meta.append(_enc(c["room"]))
            if c.get("days"):
                meta.append(_enc(c["days"]))
            if c.get("level"):
                meta.append(_enc(c["level"]))
            meta_str = ", ".join(meta)
            meta_html = f'<br><small>&nbsp;&nbsp;{meta_str}</small>' if meta_str else ""
            note = c.get("note")
            note_html = f'<br><small>&nbsp;&nbsp;<i>{_enc(note)}</i></small>' if note else ""
            lines.append(f'{code} &#151; {title}{meta_html}{note_html}')
        chunks.append("<br>\n".join(lines))
        chunks.append("</p>")
    return "\n".join(chunks)


def _students_block(persona: dict) -> str:
    group = persona.get("group") or {}
    phds = group.get("current_phd_students") or []
    ms = group.get("current_masters_students") or []
    advisees = group.get("advisees") or []
    alumni = group.get("alumni") or []
    if not (phds or ms or advisees or alumni):
        return ""

    out = ['<font size="+1"><b>Students</b></font>']

    if phds:
        items = []
        for s in phds:
            topic = f" ({_enc(s['topic'])})" if s.get("topic") else ""
            yr = f", started {s['year_started']}" if s.get("year_started") else ""
            items.append(f'<li>{_enc(s.get("name",""))}{yr}{topic}</li>')
        out.append("<p><b>Current Ph.D. students:</b></p>")
        out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
    if ms:
        items = []
        for s in ms:
            topic = f" ({_enc(s['topic'])})" if s.get("topic") else ""
            items.append(f'<li>{_enc(s.get("name",""))}{topic}</li>')
        out.append("<p><b>Current Masters students:</b></p>")
        out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
    if advisees:
        items = []
        for a in advisees:
            year = f" ({_enc(a['year'])})" if a.get("year") else ""
            topic = f" &#151; {_enc(a['topic'])}" if a.get("topic") else ""
            items.append(f'<li>{_enc(a.get("name",""))}{year}{topic}</li>')
        out.append("<p><b>Undergraduate advisees:</b></p>")
        out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
    if alumni:
        items = []
        for a in alumni:
            year = f" ({a['graduated']})" if a.get("graduated") else ""
            pos = f" &#151; {_enc(a['first_position'])}" if a.get("first_position") else ""
            items.append(f'<li>{_enc(a.get("name",""))}{year}{pos}</li>')
        out.append("<p><b>Former students:</b></p>")
        out.append("<ul>\n" + "\n".join(items) + "\n</ul>")

    return "\n".join(out)


def _prospective_block(persona: dict) -> str:
    ps = persona.get("prospective_students") or {}
    if ps.get("accepting") is None:
        return ""
    note = ps.get("note") or ""
    if not note:
        return ""
    # Plain italic paragraph, no callout.
    return f"<p><i>{_enc(note)}</i></p>"


def _footer_block(persona: dict) -> str:
    last = (persona.get("site_meta") or {}).get("last_updated") or ""
    if not last:
        return ""
    return f'<font size="-1">Last updated: {_enc(_format_last_updated(last))}</font>'


def _hr() -> str:
    return '<hr width="80%" size="2">'


# ---------- page ----------

def _page_html(persona: dict, photo_filename: str | None) -> str:
    name = persona.get("name", {}) or {}
    uni = persona.get("university", {}) or {}

    title_text = f"{name.get('full', '')} - {uni.get('name', '')}"

    sections = [
        _heading_block(persona),
        _hr(),
        _bio_block(persona, photo_filename),
        _hr(),
        _contact_block(persona),
        _hr(),
        _research_interests_block(persona),
        _hr(),
        _publications_block(persona),
        _hr(),
        _teaching_block(persona),
        _hr(),
        _students_block(persona),
        _prospective_block(persona),
        _hr(),
        _footer_block(persona),
    ]
    body = "\n".join(s for s in sections if s)

    return (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n'
        '  "http://www.w3.org/TR/html4/loose.dtd">\n'
        '<html>\n'
        '<head>\n'
        '<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">\n'
        f'<title>{_enc(title_text)}</title>\n'
        '</head>\n'
        '<body bgcolor="#FFFFFF" text="#000000" link="#0000EE" vlink="#551A8B" alink="#FF0000"\n'
        '      leftmargin="20" topmargin="20" marginwidth="20" marginheight="20">\n'
        f"{body}\n"
        '</body>\n'
        '</html>\n'
    )


# ---------- public entrypoint ----------

def _resolve_personas_root(rel_path: str) -> Path | None:
    candidates = [Path.cwd() / "Personas", Path.cwd() / "personas"]
    here = Path(__file__).resolve().parent.parent
    candidates.extend([here / "Personas", here / "personas"])
    for c in candidates:
        if (c / rel_path).exists():
            return c
    return None


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
            # Use plain 'photo.jpg' — less modern than 'headshot.jpg'.
            photo_filename = "photo.jpg"
            shutil.copyfile(src, out_dir / photo_filename)

    # Write the HTML as Latin-1 bytes to match the declared iso-8859-1 charset.
    # All non-ASCII chars are already encoded as &entity;/&#NNN; so latin-1
    # encoding succeeds without loss.
    page = _page_html(persona, photo_filename)
    (out_dir / "index.html").write_bytes(page.encode("iso-8859-1"))
