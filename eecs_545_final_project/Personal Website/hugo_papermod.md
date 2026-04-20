# Template spec: `hugo_papermod`

## What we're mimicking

A blend of [Hugo PaperMod](https://github.com/adityatelange/hugo-PaperMod)
and [Wowchemy](https://wowchemy.com/) (now Hugo Blox), which together
represent the Hugo-flavored academic aesthetic you see on a lot of humanities
and social-science faculty pages circa 2022–2025. The look is card-heavy,
subtly warmer than al-folio, and places more emphasis on visual hierarchy
through color blocks and thumbnails rather than pure typography.

Defining characteristics:

- **Hero section at the top**: large headshot (often circular), name, title,
  and a row of social icons, all centered or left-aligned on a soft-tinted
  background band
- **Cards everywhere**: bio, publications, projects are each in their own
  rounded-corner card with subtle shadow
- **A sidebar navigation OR a sticky top nav** — we'll use a sticky top nav
  for consistency
- **Tag/keyword pills** for research areas under the hero
- **"Recent Publications" on the home page** with visual hierarchy:
  cover-thumbnail placeholders, title, authors, venue, sometimes an abstract
  snippet
- **A "Bio" card** with a longer, more formal biographical statement
- Color palette uses a warm accent (often teal, burnt orange, or deep blue);
  we'll use a deep teal `#2a6f6f`
- Corner radius is prominent (8–12px on cards, full circle on headshot)
- Icons are inline SVG or simple Unicode symbols
- Footer has multiple columns (about, contact, social) — wider than al-folio's
  minimal footer

## Color palette

```
--background:      #fafaf7    (warm off-white)
--surface:         #ffffff    (card background)
--surface-alt:     #f0eee8    (hero band background)
--text-primary:    #1f2937
--text-secondary:  #4b5563
--text-muted:      #9ca3af
--accent:          #2a6f6f    (deep teal)
--accent-soft:     #d4e6e6    (for tag pill backgrounds)
--border:          #e5e7eb
--shadow:          0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)
```

## Typography

```
--font-display: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-body:    "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-serif:   Georgia, "Times New Roman", serif;   /* for pull quotes / one-liners */
```

Everything is sans-serif except the `research.one_liner` pull quote which
gets italic serif treatment for emphasis. This is a Wowchemy convention.

## Layout

Wider than al-folio — max-width around 1000–1100px for cards, with the hero
band stretching full-width.

```
┌────────────────────────────────────────────────────────┐
│ [brand]     Home  Publications  Teaching  Contact      │  <- sticky nav
├────────────────────────────────────────────────────────┤
│                                                         │
│         [hero band, full width, soft tinted bg]        │
│                                                         │
│                      ⬤  <- circular headshot          │
│                                                         │
│                Malcolm Reyes-Whittaker                  │
│                Professor of Anthropology                │
│                    Thornfield College                   │
│                                                         │
│            [ cultural anthropology ] [ oral history ]  │
│            [ ethnography of labor ]                    │
│                                                         │
│            [scholar] [bsky] [blog] [orcid]             │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────┐  ┌────────────────────┐  │
│  │  📖 Biography            │  │  ✉  Contact        │  │
│  │                          │  │                    │  │
│  │  "I write about how     │  │  mreyeswhittaker   │  │
│  │   communities make      │  │    @thornfield.edu │  │
│  │   meaning after the     │  │                    │  │
│  │   factories close."     │  │  Ashwood Hall 214  │  │
│  │                          │  │  +1 (802) 555-0187 │  │
│  │  Malcolm Reyes-Whittaker │  │                    │  │
│  │  is a cultural...        │  │  Office hours:     │  │
│  │  [full bio prose]        │  │  Wed 1-3pm,        │  │
│  │                          │  │  Fri 10-11:30am    │  │
│  └─────────────────────────┘  └────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  📚 Recent Publications                           │  │
│  │                                                    │  │
│  │  ┌───┐  The Mill Was a Person: Personhood...     │  │
│  │  │pub│  M. Reyes-Whittaker                       │  │
│  │  │ 24│  American Ethnologist · 2024              │  │
│  │  └───┘                                            │  │
│  │                                                    │  │
│  │  [... 2 more recent entries ...]                 │  │
│  │                                                    │  │
│  │  [ See all publications → ]                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  🎓 Teaching                                      │  │
│  │  [teaching card grid or list]                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  👥 Current Advisees                              │  │
│  │  [advisee list]                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
├────────────────────────────────────────────────────────┤
│  About              Contact            Elsewhere        │
│  [about blurb]      [mailing address]  [social links]  │
│                                                         │
│  © 2025 Malcolm Reyes-Whittaker · Thornfield College   │
└────────────────────────────────────────────────────────┘
```

## Pages to generate

- `index.html` — everything described above, long scrolling page
- `publications.html` — full publication list as cards, grouped by type
  (Books, Articles, Chapters, Reviews), sorted by year descending within
  each group
- `teaching.html` — full teaching history as cards
- `style.css`

Hugo PaperMod sites often put everything on the home page and link to
"archive" pages only for the full lists. We follow that convention: the
index has abbreviated sections with "See all →" links, and the subpages have
the full enumeration.

Notice there is no separate "About" or "Bio" page — the bio lives in a card
on the home page. This is distinct from al-folio's convention.

## Nav items

Sticky top nav (sticks to top on scroll). Items: `Home`, `Publications`,
`Teaching`, `Contact`. The brand (persona's `preferred` name or `name.last`)
is far left; nav items float right. Use a thin bottom border or subtle
shadow when scrolled.

The `Contact` nav item is a same-page anchor (`#contact`) that jumps to the
contact card on the home page, NOT a separate page. This is a Wowchemy
convention and is distinct from al-folio.

## Field placement

| Persona field                        | Where rendered                        |
|--------------------------------------|---------------------------------------|
| `name.full`                          | Hero, large                           |
| `name.title` + `department.name`     | Hero, below name, smaller             |
| `university.name`                    | Hero, below department                |
| `research.areas`                     | Hero, as pill tags (max 4-5 shown)    |
| `research.one_liner`                 | Bio card, italic serif pull quote at the top |
| `research.long_bio`                  | Bio card, main prose                  |
| `assets.photo_source`                | Hero, circular, ~160px diameter       |
| `contact.email`                      | Contact card, with icon               |
| `contact.phone_office`               | Contact card, with icon, if non-null  |
| `contact.phone_lab`                  | Contact card, labeled "Lab:", if non-null |
| `contact.fax`                        | Contact card, labeled "Fax:", if non-null |
| `office.building` + `office.room`    | Contact card                          |
| `office.hours`                       | Contact card, labeled "Office hours:" |
| `office.mailing_address` (full)      | Contact card AND in the footer left column |
| `social.*`                           | Hero row of icons; footer right column |
| `publications` (3 most recent)       | "Recent Publications" card on home    |
| `publications` (all)                 | `publications.html`, grouped by type  |
| `teaching` (current + next semester) | "Teaching" card on home               |
| `teaching` (all)                     | `teaching.html`                       |
| `group.current_phd_students`         | "Students" card, if `group.name` is non-null |
| `group.current_masters_students`     | Also in "Students" card               |
| `group.advisees`                     | "Current Advisees" card, if non-empty (for humanities personas) |
| `group.alumni`                       | "Former Students" subsection within the students card, if non-empty |
| `prospective_students.note`          | Dedicated card near the bottom of home page, if `accepting` is not null |

## Publication rendering (Hugo PaperMod/Wowchemy format)

Each publication on `publications.html` is a horizontally-oriented card:

```
┌─────────────────────────────────────────────────┐
│  ┌──┐                                            │
│  │24│  The Mill Was a Person: Personhood, Loss,  │
│  │  │  and the Ethics of Closure in a Vermont    │
│  └──┘  Paper Town                                │
│        M. Reyes-Whittaker                        │
│        American Ethnologist · 2024 · 51(3)       │
│        [article]                                  │
└─────────────────────────────────────────────────┘
```

The left "thumbnail" box is a simple colored square with the 2-digit year in
it (e.g., "24" for 2024). Different type uses different background colors:

- `article`: accent teal `#2a6f6f`
- `book`: warm brown `#8b4513`
- `chapter`: muted gold `#b8860b`
- `review`: grey `#6b7280`

This is a clean visual hierarchy trick Wowchemy uses to let readers skim by
type. Text on the thumbnail is white, centered.

The button row at the bottom shows the publication type as a pill ("article",
"book", "chapter", "review"), and any of `[pdf]` / `[code]` if the
corresponding `_source` or `_url` is non-null.

## Handling humanities-specific fields

Since the anthropology persona has `group.name = null` (no lab), the
template must branch:

- **If `group.name` is null**: render a "Current Advisees" card showing
  `group.advisees` as a simple list of `{name, year, topic}` entries. Show
  `group.alumni` as a smaller "Former Students" subsection. Do not render
  the word "Lab" anywhere.
- **If `group.name` is non-null**: render a "Research Group" card titled
  with `group.name`, showing PhD students and masters students as separate
  subsections, alumni as a third subsection. Include `group.group_photo_source`
  at the top of the card if non-null.

This template will primarily be used for humanities personas, but must handle
both cases cleanly — the research design may eventually render a CS persona
with this template as a within-subject comparison.

## Things that are authentically Hugo PaperMod/Wowchemy

- Circular headshot
- Hero band with tinted background
- Pill tags for research areas
- Card-based layout with rounded corners and subtle shadows
- Emoji section headers (📖 Biography, 📚 Publications, 🎓 Teaching)
- "See all →" links that go to subpages
- Multi-column footer
- Visible publication type as a pill

## Things that would make it NOT look like this

- Narrow reading column (that's al-folio)
- Pure black and white (too austere; Hugo themes have warmth)
- Top-right nav with serif brand (too al-folio)
- Full horizontal rule dividers between sections (use cards instead)
- Hover underlines on nav (use color change instead)

## Smoke test checklist

After rendering Reyes-Whittaker, verify:

- [ ] Hero has circular headshot, name, title, department, university
- [ ] Research areas render as pill tags under the hero
- [ ] Bio card has the italic serif one-liner at the top, prose below
- [ ] Contact card shows email, office, phone, hours, mailing address
- [ ] "Prospective Students" section is NOT rendered (because `accepting` is null for Thornfield)
- [ ] Publications page has all 7 entries grouped by type: 1 Book, 5 Articles, 1 Chapter, 1 Review
- [ ] Advisees card shows 3 current advisees (Juniper, Dev, Sam)
- [ ] Former Students subsection shows 2 alumni (Ingrid, Marco)
- [ ] No "Lab" or "Research Group" heading appears
- [ ] Social icons in hero include bluesky and personal blog, but NOT twitter/linkedin/github (which are null)
- [ ] Footer has multi-column layout with mailing address
- [ ] No `null` text anywhere
- [ ] Full-bleed hero band; main content is slightly narrower
