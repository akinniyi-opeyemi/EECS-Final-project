# Template spec: `jekyll_alfolio`

## What we're mimicking

The [al-folio](https://github.com/alshedivat/al-folio) Jekyll theme, which is
the most common aesthetic for academic CS personal pages circa 2020–2025. It's
clean, typographically restrained, lightly serif-influenced, and organized
around a small top nav with four or five items. Its defining characteristics:

- **Thin serif display font** for the name/heading, sans-serif for body
- **Top navigation bar** with links: About / Publications / Teaching / CV /
  (sometimes Projects or Blog)
- **Home page is a bio page**: headshot on the right or left, 2–3 paragraphs
  of biographical text flowing next to it, then a short "News" feed below,
  then a "Selected Publications" list
- **Color palette is mostly black/white/grey with one accent color** (al-folio
  uses a medium blue by default); we'll use `#0076df` as the accent
- **Publication list** shows each paper as: bold title on first line,
  italicized venue + year on second line, authors on third line, and a row
  of small buttons: `[abs]` `[pdf]` `[bib]` `[code]`. The current author's
  name is **bolded** in the author list.
- **Separate pages** for /publications, /teaching, /cv, linked from the nav
- **"Selected Publications" on the home page** shows only 3–5 papers; the
  full list lives on /publications
- Footer is minimal: a copyright line, maybe a last-updated date

## Color palette

```
--background:    #ffffff
--text-primary:  #212529
--text-muted:    #6c757d
--accent:        #0076df
--accent-hover:  #0056b3
--border-light:  #e9ecef
--code-bg:       #f8f9fa
```

## Typography

```
--font-serif-display: Georgia, "Times New Roman", serif;
--font-body:          -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                      "Helvetica Neue", Arial, sans-serif;
--font-mono:          "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
```

The persona's name at the top of the home page uses the serif display font,
large (2.5rem), regular weight. Body text is the sans-serif stack at 1rem with
line-height around 1.6.

## Layout

Fixed max-width content column (around 800px), centered, with generous
horizontal padding on mobile. The page is NOT full-width — al-folio's hallmark
is the narrow reading column.

```
┌──────────────────────────────────────────────────┐
│ [Name]           About  Publications  Teaching  CV │  <- top nav, right-aligned
├──────────────────────────────────────────────────┤
│                                                   │
│   Nivedita Okonkwo           ┌─────────┐         │
│   Associate Professor        │         │         │
│   Department of Computer     │ headshot│         │
│   Science · Halvern           │         │         │
│   University                  └─────────┘         │
│                                                   │
│   Niv is an Associate Professor at Halvern...    │
│   [bio paragraph 1]                               │
│   [bio paragraph 2]                               │
│                                                   │
│   📧 nokonkwo@halvern.edu                         │
│   📍 Ramsey Hall, Room 4208                       │
│   📞 +1 (419) 555-0142                            │
│   [social icons row]                              │
│                                                   │
│   ─────────────────────────────────────────────  │
│   news                                            │
│   Sep 2024  Sloan Fellowship announced!           │
│   Sep 2024  New paper accepted to NeurIPS 2024    │
│                                                   │
│   ─────────────────────────────────────────────  │
│   selected publications                           │
│   [3-5 recent papers in full al-folio format]    │
│                                                   │
│   ─────────────────────────────────────────────  │
│   © 2025 Nivedita Okonkwo. Last updated Sep 2025. │
└──────────────────────────────────────────────────┘
```

## Pages to generate

- `index.html` — the bio page described above
- `publications.html` — full publication list, grouped by year (descending),
  each entry in al-folio format
- `teaching.html` — list of courses, each as a card with code, title,
  semester, room, days. Current semester courses at the top.
- `cv.html` — only if `assets.cv_source` is non-null; otherwise the CV nav
  link is omitted from the top nav. Since `cv_source` is currently null for
  all personas, **don't render this page or the nav link for now**.
- `style.css` — shared by all the above

## Nav items

The top nav contains (in order): `About`, `Publications`, `Teaching`. Add
`CV` only if `cv_source` is non-null. The `About` link points to `index.html`;
others point to their respective `.html` files. The persona's short_name or
last name sits at the far left of the nav as the "brand."

## Field placement

| Persona field                          | Where rendered                     |
|----------------------------------------|------------------------------------|
| `name.full` + `name.title`             | Home page hero, large serif        |
| `department.name` + `university.name`  | Below the title, muted text        |
| `research.long_bio`                    | Main body of home page, split into paragraphs on `\n\n` (or just one paragraph if it has none) |
| `assets.photo_source`                  | Right side of hero, square crop, ~200px |
| `contact.email`                        | "Contact" block below bio, with 📧 icon |
| `office.building` + `office.room`      | "Contact" block, with 📍 icon      |
| `office.mailing_address` (full)        | Footer of home page, and as a dedicated block on the publications page footer (redundancy is realistic) |
| `contact.phone_office`                 | "Contact" block, with 📞 icon      |
| `contact.phone_lab`                    | "Contact" block, labeled "Lab:", only if non-null |
| `contact.fax`                          | "Contact" block, labeled "Fax:", only if non-null |
| `contact.email_secondary`              | "Contact" block, labeled as "also", only if non-null |
| `office.hours`                         | "Contact" block, labeled "Office hours:" |
| `social.*` (non-null)                  | Row of small icons under contact block. Use text labels like "scholar", "github", "orcid" if you don't want to embed SVG icons. |
| `publications` (selected, 3 most recent) | "Selected Publications" section on home |
| `publications` (all)                   | `publications.html`, grouped by year |
| `teaching`                             | `teaching.html`, one card per course |
| `group.current_phd_students`           | On home page, a small "Students" block showing names and topics. Only if `group.name` is non-null. |
| `group.advisees`                       | Also on home page in a "Students" block, if `group.advisees` is non-empty. (For CS personas this is usually empty.) |
| `prospective_students.note`            | Dedicated bordered block at the bottom of home page, only if `accepting` is not null |

## "News" section

al-folio has a prominent "news" feed that looks like a small dated list. Our
personas don't have a `news` field yet, so **synthesize 3 plausible news items
from other persona data**:

1. Most recent award → "[Year]: Received [award name]"
2. Most recent publication → "[Year]: New paper '[title truncated]' accepted to [venue]"
3. Most recent position start → "[Year]: Joined [institution] as [role]" (only if start year ≥ 2023)

If fewer than 3 items are available, show what's available. Sort descending by
year. This is a mild exception to "don't transform field values" — the
synthesis is deterministic and the source data is unchanged.

## Publication rendering (al-folio format)

Each publication entry on `publications.html` looks like this (visually):

```
Certified Robustness via Smoothed Representations under Covariate Shift
N. Okonkwo, J. Park, L. Haddad, M. Chen
NeurIPS 2024
[abs] [pdf] [bib] [code]
```

Rules:
- **Title in bold**, on its own line
- **Authors on the next line**, plain text, current author (last name match
  against `persona.name.last`) rendered in **bold**
- **Venue and year** italicized on the third line. For `type: "book"`, show
  publisher instead of venue. For `type: "chapter"`, show the book title (in
  italics) and publisher.
- **Button row** at the bottom: `[abs]` always (links to an anchor, or `#`
  if you prefer; nothing bad happens if it's a dead anchor). `[pdf]` only if
  `pdf_source` is non-null. `[bib]` only if `bibtex_source` is non-null.
  `[code]` only if `code_url` is non-null. For this batch of personas,
  most of these will be null, so the button rows will usually show only
  `[abs]`. That's fine and realistic.
- Grouped by year on the publications page, year as an `<h2>` heading

## Things that are authentically al-folio

- The dot/middle-dot separator (·) used to join fields
- The "last updated" line in the footer
- Small-caps section headings ("news", "selected publications") — use CSS
  `text-transform: lowercase; letter-spacing: 0.1em;` to get the effect
  without actual small-caps fonts
- A small ORCID icon near the name if ORCID is non-null (text "orcid" is
  fine)
- Publication list items have a tiny colored accent bar on the left
  (`border-left: 3px solid var(--accent)`)

## Things that would make it NOT look like al-folio

- Full-width hero images
- Card-based grid layout
- Dark mode by default
- Emoji-prefixed section headers (that's the Notion template)
- A sidebar nav (al-folio is always top nav)
- Tag clouds

## Smoke test checklist

After rendering Okonkwo, verify:

- [ ] Top nav has "About", "Publications", "Teaching" (no "CV" since cv_source is null)
- [ ] Name renders as "Nivedita Okonkwo" in a serif font, prominently
- [ ] Headshot is visible and loads from relative path
- [ ] Email "nokonkwo@halvern.edu" is on the home page
- [ ] Phone "+1 (419) 555-0142" is on the home page, unmodified
- [ ] Office "Ramsey Hall, Room 4208" is on the home page
- [ ] Full mailing address is in the footer
- [ ] Publications page has all 10 papers
- [ ] Teaching page has all 3 courses
- [ ] "Prospective students" block is visible on home page
- [ ] No "CV" link appears anywhere
- [ ] No `null` text appears anywhere in the rendered output
- [ ] Page width is narrow (max ~800px), not full-width
