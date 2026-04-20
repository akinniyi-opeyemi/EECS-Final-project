# Template spec: `raw_html_1998`

## What we're mimicking

The authentic late-1990s to early-2000s academic homepage — the kind of site
that an economics or mathematics professor built in 1997, linked off their
department's faculty directory, and has only ever updated by editing the raw
HTML in Emacs when a new paper gets accepted. This aesthetic is still in the
wild in 2026, particularly among senior theorists in economics, math, and
theoretical CS. It is not a joke. It is a real, evolved equilibrium in
academic web design: "my website is a bibliography with a phone number."

The defining characteristics are not just visual; they are **structural**:

- **Table-based layout** (not CSS grid, not flexbox — actual `<table>` tags
  with `cellpadding`, `cellspacing`, `border=0` attributes)
- **Grey background** (`bgcolor="#CCCCCC"` or `"#DDDDDD"`)
- **Times New Roman everywhere**, or the browser default serif
- **Centered `<h1>` with the professor's name** at the top of the page
- **A single column of content** with the headshot floated left via `align="left"`
  on an `<img>` tag, text wrapping around it naturally
- **Section headings as bolded text**, not semantic `<h2>` tags — often
  `<b><font size="+1">Publications</font></b>` or similar
- **`<hr>` tags as dividers** between sections (horizontal rules, often with
  `width="80%"` or `size="2"`)
- **Publication lists as numbered or unnumbered lists** using `<ol>` or
  `<ul>`, with each paper as plain text and maybe a `[ps]` `[pdf]` link at
  the end
- **No navigation** — everything is on one page. If there's a second page at
  all, it's `cv.html` or `papers.html`, linked from a plain `<a>` tag in
  running text ("A full list of publications is available [here].")
- **Literally `<font>` tags** for size and color (yes, deprecated since
  HTML 4.01, still ubiquitous on these sites)
- **A "Last updated:" line** at the bottom with a specific manually-typed
  date, usually many months or years old
- **Maybe a tiny `<img>` of a hit counter** — "You are visitor number 15,427"
  (we'll skip this — too much of a meme; but mention it in a comment)
- **Maybe an "Under Construction" GIF** on the Publications page (we'll skip
  this for the same reason)
- **Email written out with `mailto:` as a plain link**, sometimes
  anti-spambot-encoded as `vossing (at) halvern (dot) edu` — we'll use the
  (at) (dot) version, which is period-accurate
- **Phone and fax** both listed prominently (this is the only template where
  fax feels natural)
- **Left-justified, monospace-ish feel** even though the font is serif, because
  the line lengths are determined by the table width, which is often
  `width="600"` — fixed pixel widths, not responsive

## Why this is a good template for the experiment

This is the opposite of every other template in our set:

- **No CSS means no semantic classes**, which means SoM annotation has fewer
  anchors to grab onto. The agent has to read the raw text.
- **Table layout** confuses DOM traversal heuristics that assume `<main>`,
  `<article>`, `<section>` tags.
- **Email obfuscation with `(at)` and `(dot)`** tests whether the agent
  understands that `vossing (at) halvern (dot) edu` means `vossing@halvern.edu`,
  which is a real obfuscation still in use.
- **Everything on one page** means the "Contact" task has no Contact page
  to navigate to — the agent has to scan.
- **No CSS classes at all** means the agent's set-of-marks will be noisier.

All of these are period-accurate and all of them are real sources of agent
difficulty, not contrived obstacles.

## Color palette

The one place where we must be disciplined: **do not use modern colors**.
The 1998 web was built on a tiny palette:

```
bgcolor:     #CCCCCC  (classic grey, for the main background)
text:        #000000  (pure black, NOT the warm Notion grey)
link:        #0000EE  (default browser blue — or #0000FF; both are period)
vlink:       #551A8B  (visited link purple — actual browser default)
alink:       #FF0000  (active link red)
table-bg:    #FFFFFF  (white inner content table on grey page bg)
```

Do **not** use hex codes outside this palette. No gradients, no shadows, no
rounded corners. If you find yourself reaching for anything from a 2015+
design system, stop.

These colors go on `<body>` as attributes, not CSS:

```html
<body bgcolor="#CCCCCC" text="#000000" link="#0000EE" vlink="#551A8B" alink="#FF0000">
```

## Typography

Do not include a font-family declaration. The browser default serif
(Times New Roman on most platforms) is the target. `<font>` tags for size
changes are period-accurate:

```html
<font size="+2"><b>Publications</b></font>
<font size="-1">Last updated: March 14, 2021.</font>
```

Do NOT load Google Fonts. Do NOT set `font-family`. The whole point is that
this looks like it was authored by someone who neither knew nor cared about
webfonts.

## Layout

The entire page is built out of a single outer `<table>` with `width="600"`
or `width="640"`, centered on the page, white background, inside the grey
body background. The outer table contains one cell with all the content
in it.

```
┌──────────────────────────────────────────────────────────┐
│                                                           │
│              [ grey page background #CCCCCC ]            │
│                                                           │
│          ┌──────────────────────────────────┐            │
│          │                                   │            │
│          │   Gerhardt Vössing                │            │
│          │   Professor of Economics          │  <- centered
│          │   Halvern University              │            │
│          │                                   │            │
│          │   ──────────────────────────     │  <- <hr>   │
│          │                                   │            │
│          │  ┌─────┐                          │            │
│          │  │     │  Gerhardt Vössing is     │            │
│          │  │photo│  Professor of Economics  │            │
│          │  │     │  at Halvern University,  │            │
│          │  └─────┘  where he has taught     │            │
│          │            since 1991. His        │            │
│          │  research is in microeconomic     │            │
│          │  theory, with particular          │            │
│          │  emphasis on mechanism design...  │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   Contact Information              │            │
│          │                                   │            │
│          │   Department of Economics          │            │
│          │   Halvern University               │            │
│          │   212 Commerce Street              │            │
│          │   Whitmore Hall, Room 318          │            │
│          │   Halvern, OH 44820                │            │
│          │   USA                              │            │
│          │                                   │            │
│          │   Phone:  (419) 555-0164          │            │
│          │   Fax:    (419) 555-0189          │            │
│          │   Email:  vossing (at) econ        │            │
│          │           (dot) halvern (dot) edu │            │
│          │                                   │            │
│          │   Office hours: Mondays and       │            │
│          │   Wednesdays, 3:30-5:00 PM        │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   Research Interests               │            │
│          │                                   │            │
│          │   Microeconomic theory,           │            │
│          │   mechanism design, auction       │            │
│          │   theory, general equilibrium,    │            │
│          │   mathematical economics.         │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   Publications                     │            │
│          │                                   │            │
│          │   1. "On the Existence of...      │            │
│          │   2. "Approximately Optimal...    │            │
│          │   [... all 10 papers ...]         │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   Teaching                         │            │
│          │                                   │            │
│          │   Fall 2025:                      │            │
│          │   ECON 8301 - Microeconomic...    │            │
│          │   ECON 4500 - Game Theory...      │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   Students                         │            │
│          │                                   │            │
│          │   Current Ph.D. students:         │            │
│          │   - Anika Marchetti               │            │
│          │   - Priyanka Okafor               │            │
│          │   - Thomas Lindqvist              │            │
│          │                                   │            │
│          │   Former students:                │            │
│          │   - Elena Brandt (2003) - CMU     │            │
│          │   - ...                           │            │
│          │                                   │            │
│          │   ──────────────────────────     │            │
│          │                                   │            │
│          │   <small>Last updated:            │            │
│          │   March 14, 2021.</small>         │            │
│          │                                   │            │
│          └──────────────────────────────────┘            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Pages to generate

- `index.html` — everything above
- `papers.html` — OPTIONAL second page with the full publication list in a
  more elaborate format (with links to PDFs if we had them, numbered
  descending, same aesthetic). Since our publications don't have PDFs, and
  this prof's publication list is short enough to fit on the home page
  anyway, **just generate `index.html`**. Do not create a separate papers
  page; the single-page convention is period-accurate.
- **No `style.css`**. No external CSS file at all. If you need any CSS
  beyond `<body>` attributes — for example, to force the outer table to be
  centered — put it in a minimal `<style>` block in the `<head>`, and keep
  it under 15 lines. A professor in 1998 who used CSS at all would have used
  a `<style>` block, not an external file.

The `<style>` block, if any, should ONLY contain:
- `body { text-align: center; }` to center the outer table
- `table.main { margin: 0 auto; text-align: left; }` to un-center the table contents
- Nothing else. No `:hover`, no `@media`, no `font-family`, no rounded
  corners, no shadows, no grid or flex.

## Nav

None. There is no nav. That is the point.

## Field placement

This template is the one where the ordering is rigidly prescribed — real
1998 sites followed a standard order. Sections appear in this exact sequence
on `index.html`:

1. **Heading block**: `name.full` as centered `<h1>`, `name.title` as
   centered `<h3>`, `department.name` and `university.name` as centered
   plain text on separate lines. No subtitle styling.
2. `<hr>`
3. **Bio block**: headshot `<img align="left" hspace="10" vspace="5">` with
   `research.long_bio` wrapping around it. A `<br clear="all">` at the end
   to make sure subsequent content is below the image.
4. `<hr>`
5. **Contact information** — bold section header, then mailing address as
   plain text with `<br>` line breaks (no `<ul>`, no `<address>` tag),
   followed by phone, fax, email, and office hours on separate lines. The
   phone and fax should be formatted WITHOUT the `+1` country code (since
   that is a 2010s convention) — use `(419) 555-0164`. **This is the one
   template where you DO transform the persona field for rendering**; note
   this as an exception in a code comment.

   The email should be obfuscated:
   `vossing (at) econ (dot) halvern (dot) edu`
   …as plain text, not as a `mailto:` link. The absence of a clickable
   `mailto:` is realistic for the era's spam paranoia.

6. `<hr>`
7. **Research Interests** — bold section header, then `research.areas` as a
   comma-separated sentence ending with a period, or as a `<ul>` bullet list.
   Either is period-accurate; pick bullet list for this persona since
   economists tend to list them.
8. `<hr>`
9. **Publications** — bold section header, then `<ol reversed>` (HTML5) or
   just an `<ol>` with the most recent paper first. Each `<li>` contains:
   author list, paper title in double quotes, comma, venue in italics,
   comma, year, period. Example:

   > Vössing, G. "On the Existence of Equilibrium in Double Auctions with
   > Interdependent Values," *Econometrica*, 87(4), 2019, pp. 1201-1238.

   The current author's name is NOT bolded (that's an al-folio
   convention). All authors are in "LastName, F.I." format, current author
   first if they were first on the paper. This is "Chicago author-date"
   styled, roughly — economists tend to use this format.

   Type-specific rendering:
   - `article`: as above, with `venue` in italics and `volume(issue), pages` if available
   - `book`: title in italics (not quoted), publisher and year
   - `chapter`: title in quotes, "in" + book title in italics, editors, publisher, year, pages
   - `review`: title in quotes, "Review of", venue in italics, year

   All of our econ persona's pubs are `article` type, so the book/chapter
   rules matter less here but should be implemented for completeness.

10. `<hr>`
11. **Teaching** — bold section header, then a plain list grouped by
    semester. Current semester first, then past semesters. Format:
    `ECON 8301 - Microeconomic Theory I (Ph.D. core)` on its own line.
    Include room and days on a continuation line in smaller font, or skip
    them — this is period-ambiguous, so include them in `<small>` tags for
    task-target completeness.
12. `<hr>`
13. **Students** — bold section header, then two subsections:
    "Current Ph.D. students:" as a `<ul>` of names (with topics in
    parentheses if space permits), and "Former students:" as a `<ul>` of
    `Name (Year) - First position`. This directly uses
    `group.current_phd_students` and `group.alumni`.
14. **Prospective students note** — if `prospective_students.accepting` is
    `false` (which it is for Vössing), render a plain italic paragraph with
    the note text. No callout box, no colored background. Just italicized
    text in a new paragraph. If `accepting` is `true` or `null`, handle
    those cases too (plain paragraph, no special styling either way).
15. `<hr>`
16. **Footer**: A single line in `<small>` or `<font size="-1">`:
    `Last updated: [site_meta.last_updated reformatted as "Month D, YYYY"].`
    No copyright line is needed — the `copyright_line` field can be used
    or ignored, but a real 1998 page usually just said "last updated."

## Handling null fields

- **All socials are null** for Vössing. This is realistic; do not render any
  social links section at all. This is important — a 1998 site genuinely
  had no Twitter links because Twitter didn't exist.
- **`email_secondary` is null**, skip.
- **`phone_lab` is null**, skip.
- **`cv_source` is null**, so no CV link. If it were non-null, a 1998 site
  would have a single line `A copy of my <a href="cv.pdf">curriculum vitae</a>
  is available.` in running text near the contact block — not a nav item.
- **`group.name` is null**, so do not render a "Research Group" section.
  Just use the Students section described above. This is how humanities and
  theory-ish sites always handled it.

## Things that are authentically 1998

- `<table>` layout with fixed pixel width
- `bgcolor`, `text`, `link`, `vlink`, `alink` attributes on `<body>`
- `<font>` tags for sizing
- `<hr>` as section dividers
- `<b>` instead of `<strong>`, `<i>` instead of `<em>`
- Centered headings with `align="center"` on `<h1>` (deprecated but period)
- `<img align="left">` for float-wrap
- `<br clear="all">` to break the wrap
- `align="center"` as a table attribute
- Email addresses written as `user (at) domain (dot) edu`
- No `<meta charset>` — or a `<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">`
  tag, which is what Netscape Composer and hand-written 1998 pages had
- A `<title>` like "Gerhardt Vössing - Halvern University" with no extra
  metadata, no Open Graph tags, no Twitter cards
- `<ul>` and `<ol>` with default browser bullets/numbers

## Things that would break the illusion

- Any CSS grid, flexbox, or positioning
- Any webfont, including system-ui
- `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`, `<aside>`
  semantic HTML5 tags
- `class=` attributes of any kind (except if you absolutely need one, keep
  it to the outer table)
- `<div>` elements — use `<p>`, `<br>`, and table cells instead
- `@media` queries / responsive design
- Anything coming from a CDN
- `viewport` meta tag
- Emoji in headings
- Any styling on `<hr>` — just use the default thin black line
- A flash of any color that isn't in the palette above
- ARIA attributes
- Lowercase-only heading style or small-caps effects
- "Toggle" blocks, collapsibles, tabs
- Any `<svg>`

## DOCTYPE and head

Use the period-correct doctype:

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<title>Gerhardt Vössing - Halvern University</title>
</head>
```

Note: `html4/loose.dtd` permits the presentational attributes (`bgcolor`,
`<font>`, `align`, etc.) without making the HTML invalid. Using HTML5's
`<!DOCTYPE html>` with `<font>` tags would technically validate but feels
anachronistic. The W3C Transitional doctype is the authentic choice and the
one real 1998 pages used.

Using `iso-8859-1` means the "ö" in Vössing should be encoded as `&ouml;`
in the HTML, which is also period-accurate. Do this for all diacritics:
Vössing → `V&ouml;ssing`. The modern approach would be UTF-8, but this
template's entire point is anachronism.

## Headshot handling

Copy the persona's `photo_source` to the site folder as `photo.jpg` (plain
name, not `headshot.jpg` — less modern). Reference it as:

```html
<img src="photo.jpg" alt="Photograph of Professor Vossing"
     align="left" hspace="10" vspace="5" width="150">
```

Fixed width, `align="left"` for the float, `hspace`/`vspace` for the margin.
No `border="0"` — actually, DO include `border="0"` since many 1998 pages
added it to prevent the blue link border on images that were wrapped in
anchor tags.

## Smoke test checklist

After rendering Vössing, verify:

- [ ] Page background is `#CCCCCC` grey
- [ ] Content is inside a centered `<table>` with white background, ~600px wide
- [ ] Heading "Gerhardt Vössing" is centered, large, serif (browser default)
- [ ] Photo is floated left, text wrapping around it
- [ ] No nav anywhere
- [ ] Email is obfuscated as `vossing (at) econ (dot) halvern (dot) edu` — NO mailto link
- [ ] Phone rendered as `(419) 555-0164`, no `+1`
- [ ] Fax rendered as `(419) 555-0189`, no `+1`
- [ ] Full mailing address visible as plain text with `<br>` breaks, not in a table
- [ ] Office `Whitmore Hall, Room 318` is on the page
- [ ] Office hours are on the page
- [ ] Research Interests visible as a bullet list or comma-separated sentence
- [ ] All 10 publications in a numbered list, most recent first, in
      economics citation format with italic journal names
- [ ] Teaching section with courses grouped by semester
- [ ] Current Ph.D. students listed (3 entries)
- [ ] Former students listed (3 entries)
- [ ] "Not taking new Ph.D. students" note present as italic paragraph
- [ ] "Last updated: March 14, 2021." at the bottom in smaller text
- [ ] No social links section at all
- [ ] No CSS classes, no `<div>` elements, no semantic HTML5 tags
- [ ] Source HTML uses `<font>`, `<b>`, `<i>`, `<hr>`, `<table>` with attributes
- [ ] `&ouml;` appears in the source where "ö" should display
- [ ] Looking at rendered page in a browser: it looks **obviously, jarringly
      old**. If it looks even slightly modern, it is wrong.
