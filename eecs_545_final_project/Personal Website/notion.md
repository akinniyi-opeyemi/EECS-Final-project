# Template spec: `notion`

## What we're mimicking

A [Notion](https://www.notion.so/) public page, specifically the kind that
early-career academics in the humanities and DH (digital humanities) sometimes
use instead of a traditional website. Notion public pages have a very
distinctive visual identity that is instantly recognizable:

- **Ultra-narrow reading column** (around 700px), left-aligned with a huge
  left margin on wide screens (Notion's default is ~900px total content
  width including whitespace)
- **A "cover image" band** at the top — often abstract art, a gradient, or a
  photo — spanning the full page width, maybe 30% of viewport height
- **A large emoji "page icon"** overlapping the bottom edge of the cover,
  left-aligned with the content column
- **Page title as a massive bold sans-serif heading** right under the icon,
  no subtitle styling — just black H1 text
- **Notion-specific font stack**: Notion uses a custom sans-serif very
  similar to `"Inter"`, and a system font stack for fallback. Their actual
  stack is something like:
  ```
  ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI Variable Display",
  "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif
  ```
- **Everything is "blocks"**: headings, paragraphs, bullet lists, toggle
  lists, callouts, dividers, inline database tables. There is very little
  visual hierarchy beyond spacing and font weight — no cards, no background
  colors (except for callouts), minimal borders
- **Headings use emoji prefixes as a convention**: `📚 Publications`,
  `🎓 Teaching`, `📬 Contact`, `👥 Advisees`
- **Callouts**: a rounded grey box with a colored emoji icon on the left and
  text on the right. Notion's default callout has a subtle border, no
  shadow, and a specific padding
- **Toggle blocks**: sections that can be expanded/collapsed with a triangle
  disclosure icon (▶ / ▼). We'll implement these with `<details>`/`<summary>`
  HTML which degrades gracefully without JavaScript
- **"Inline database" tables** for publications: a simple borderless
  table with thin horizontal dividers between rows, column headers in small
  grey text, rows in black. Notion databases have a specific look — we're
  not trying to be pixel-perfect but we're capturing the "spreadsheet-but-not"
  feel
- **No traditional nav bar**. Notion public pages have no nav; navigation
  is entirely by scrolling and clicking linked blocks. This is the single
  biggest structural difference from al-folio and Hugo
- **A small "shared publicly" indicator** in the top-right (the tiny Notion
  watermark / share status) — we'll mimic this with a minimal "Published via
  Notion" text badge

## Why this is a good template for the experiment

Notion public pages deliberately have:
- No traditional navigation (so the agent can't use a "Contact" link)
- Toggle blocks that hide content behind clicks (so important info can be
  collapsed by default, testing whether agents click to expand)
- Inline databases instead of free-text lists (so publication data is
  tabular, which is structurally different from al-folio's prose-like list)
- Information in callouts (so "contact info" might be in a colored box
  rather than a section heading)

These properties make it a good stress test for agents trained mostly on
traditional HTML layouts. Keep this in mind when deciding where to put
task-target fields — the whole point is that they're harder to find than on
a conventional page, not impossible.

## Color palette

Notion's default is extremely restrained. Mostly true-black text on white,
with only a few accent colors (used for callout backgrounds, tags, and
links).

```
--background:      #ffffff
--text-primary:    #37352f    (Notion's signature dark brown-grey)
--text-secondary:  #9b9a97    (for subtle labels)
--text-tertiary:   #b9b8b5    (for dividers, placeholder text)
--divider:         #ededec
--callout-bg:      #f7f6f3    (default grey callout)
--callout-bg-blue: #e7f3f8    (info callout)
--callout-bg-red:  #fbe4e4    (warning callout)
--callout-bg-green:#ddedea    (success callout)
--callout-bg-yellow:#fbf3db   (note callout)
--link-color:      #37352f    (links are just black with underline)
--tag-bg:          #ededeb
--tag-text:        #37352f
```

Crucially, **Notion text is NOT pure black (`#000000`)**. It's `#37352f`,
a warm dark brown-grey. Using pure black is one of the fastest ways to make
a Notion pastiche look fake.

## Typography

```
--font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont,
             "Segoe UI Variable Display", "Segoe UI", Helvetica,
             "Apple Color Emoji", Arial, sans-serif;
--font-mono: "SFMono-Regular", Menlo, Consolas, "PT Mono",
             "Liberation Mono", Courier, monospace;
```

- Page title (`name.full`): 40px, bold (700), -0.02em letter-spacing
- H1 section headers: 30px, bold, with ~30px top margin
- H2 subsection headers: 24px, bold
- H3 sub-subsection headers: 20px, bold
- Body text: 16px, normal weight, line-height 1.5
- Small labels: 14px, color `var(--text-secondary)`

## Layout

```
┌────────────────────────────────────────────────────────┐
│                                                         │
│           [ cover image band, full width ]              │
│           [ subtle gradient or abstract art ]           │
│                                                         │
├────────────────────────────────────────────────────────┤
│    [empty large left margin]      [empty right margin] │
│                                                         │
│        📖   <- large emoji icon, overlapping cover     │
│                                                         │
│        Yuki Abernathy                                   │
│                                                         │
│        Assistant Professor · Program in Literature,     │
│        Science, and Technology · Merrow Institute of    │
│        Technology                                       │
│                                                         │
│        ───────────────────────────────────────────     │
│                                                         │
│        > "I read novels like software and software     │
│        >  like novels."                                 │
│                                                         │
│        ───                                              │
│                                                         │
│        💡  Currently working on Compiled Fictions,     │
│            a book on postwar American fiction and      │
│            early programming cultures. Expected         │
│            Fall 2025 from Stanford University Press.   │
│                                                         │
│        ## 👤 About                                      │
│        [full bio as flowing text]                      │
│                                                         │
│        ## 📬 Contact                                    │
│                                                         │
│        📧  abernathy@merrow.edu                         │
│        🏢  Hale Building, Office 3N-17                 │
│        📞  +1 (650) 555-0133                            │
│        🕐  Mondays 3:00–5:00 PM (in person)             │
│            Thursdays 11:00 AM–12:00 PM (virtual)        │
│                                                         │
│        ▶ Mailing address                                │
│          [toggle block — click to expand]              │
│                                                         │
│        ## 📚 Publications                               │
│                                                         │
│        [inline database table]                          │
│                                                         │
│        ## 🎓 Teaching                                   │
│                                                         │
│        ▶ Fall 2025                                      │
│          [toggle expanded by default]                  │
│          - LIT 21.014 · Introduction to Fiction         │
│          - LIT 21.S02 · Literature and the Computer    │
│                                                         │
│        ▶ Spring 2026                                    │
│          [toggle collapsed by default]                 │
│                                                         │
│        ## 👥 Advisees                                   │
│        [bullet list]                                   │
│                                                         │
│        ## 🔗 Links                                      │
│        [bullet list of social links]                   │
│                                                         │
│        ───                                              │
│                                                         │
│        Last edited: Sep 10, 2025                        │
│                                                         │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Pages to generate

**Just `index.html`**. Notion public pages are single-page by convention;
everything lives on the main page, expansion happens via toggle blocks.
Do not generate `publications.html` or `teaching.html` — the full lists
should be on the main page, possibly inside toggle blocks.

This is a key structural difference from the other templates and is a
genuine source of task difficulty: the agent has to find information
without leaving the page, but also without seeing it all at once.

## No nav

There is no `<nav>` element. Instead, we add a minimal "breadcrumb" at the
very top left (above the cover image) that just shows the person's name,
styled like Notion's breadcrumb text: small, grey, no underline. This is
what Notion does for shared pages and is a recognizable visual signature.

## Field placement

| Persona field                  | Where rendered / how                    |
|--------------------------------|------------------------------------------|
| `name.full`                    | Page title H1, after the icon           |
| `name.title`, `department.name`, `university.name` | Subtitle line with `·` separators |
| `research.one_liner`           | Blockquote near the top, italic         |
| `research.long_bio`            | Under the `👤 About` heading, flowing text |
| `assets.photo_source`          | **Used as the page icon** — circular-cropped, ~100px, overlapping the cover image. This is unusual for Notion (page icons are usually emoji) but is how some humanities academics personalize their pages. If you prefer, use an emoji (📖) as the icon and place the headshot as a smaller inline image inside the About section. Your choice — document whichever you pick in a comment. |
| `contact.email`                | Under `📬 Contact`, with 📧 prefix       |
| `contact.phone_office`         | Under `📬 Contact`, with 📞 prefix, if non-null |
| `office.building` + `office.room` | Under `📬 Contact`, with 🏢 prefix    |
| `office.hours`                 | Under `📬 Contact`, with 🕐 prefix       |
| `office.mailing_address` (full) | **Inside a toggle block** labeled "Mailing address" — this is a deliberate UI-variance choice that tests whether the agent clicks to expand content |
| `social.*`                     | Under `🔗 Links` section as bullet list |
| `publications`                 | Inside an **inline database table** under `📚 Publications`. Columns: Year, Title, Venue, Type. All entries visible; no pagination. Sort by year descending. |
| `teaching`                     | Grouped by semester, each semester inside a toggle block. Current semester expanded by default, others collapsed. |
| `group.advisees`               | Under `👥 Advisees` as a bullet list    |
| `group.current_phd_students`   | Same section, labeled differently if `group.name` is non-null |
| `prospective_students.note`    | Inside a `💡` callout block near the top (if `accepting` is true) or a `⚠️` callout (if `accepting` is false). If `accepting` is null, skip. |

## Critical implementation details

### The toggle blocks

Use native HTML `<details>`/`<summary>` elements. No JavaScript needed; they
work out of the box and the VWA agent can interact with them via click.
Style them to look like Notion toggles:

```css
details > summary {
  list-style: none;
  cursor: pointer;
  padding: 4px 0;
}
details > summary::before {
  content: "▶";
  display: inline-block;
  margin-right: 8px;
  font-size: 10px;
  color: var(--text-secondary);
  transition: transform 0.15s ease;
}
details[open] > summary::before {
  transform: rotate(90deg);
}
```

**Important**: the mailing address is inside a toggle, which means the agent
must click to reveal it. The agent's initial observation via SoM may or may
not see the collapsed content, depending on how `<details>` elements are
handled. This is a deliberate source of task difficulty — one of the
hypotheses your experiment tests.

However, since ground-truth tasks include "find the full mailing address",
we want the agent to *be able to* find it — just to have to work for it. So
`<details>` is correct; do not hide it with `display: none` or put it
behind JavaScript.

### The callout blocks

```html
<div class="callout callout-blue">
  <span class="callout-icon">💡</span>
  <div class="callout-content">...text...</div>
</div>
```

With styling:

```css
.callout {
  display: flex;
  gap: 10px;
  padding: 16px;
  margin: 4px 0;
  border-radius: 4px;
  background: var(--callout-bg);
  border: 1px solid transparent;
}
.callout-blue { background: var(--callout-bg-blue); }
.callout-icon { font-size: 18px; flex-shrink: 0; }
```

### The inline database table

```html
<table class="notion-db">
  <thead>
    <tr>
      <th>Year</th>
      <th>Title</th>
      <th>Venue</th>
      <th>Type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025</td>
      <td><strong>Compiled Fictions: American Literature...</strong></td>
      <td>Stanford University Press</td>
      <td><span class="tag">book</span></td>
    </tr>
    ...
  </tbody>
</table>
```

With styling that gives thin horizontal dividers, no vertical borders,
small grey column headers, and hover highlighting on rows:

```css
.notion-db {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.notion-db th {
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: none;
  padding: 8px 10px;
  border-bottom: 1px solid var(--divider);
}
.notion-db td {
  padding: 10px;
  border-bottom: 1px solid var(--divider);
  vertical-align: top;
}
.notion-db tr:hover td {
  background: #f7f6f3;
}
.tag {
  background: var(--tag-bg);
  color: var(--tag-text);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}
```

### The cover image

Use a simple CSS gradient as the cover, since we don't have real cover
images. Generate a pleasing deterministic gradient from the persona's name
(e.g., hash the name, map to two hues, use `linear-gradient`). A warm
sunset gradient for Abernathy would look like `linear-gradient(135deg,
#f6d365 0%, #fda085 100%)`. Any two-color gradient the function produces is
fine; the requirement is determinism.

Height: 30vh, or 200px minimum.

## Things that are authentically Notion

- The warm brown-grey text color `#37352f`
- The Notion font stack
- Emoji-prefixed section headings
- Toggle blocks with the rotating triangle
- Callouts with colored backgrounds and emoji icons
- Inline database tables with small grey headers and thin row dividers
- The cover image + page icon combo
- No traditional nav
- The "Last edited: [date]" line at the bottom
- The "`>`" blockquote for the one-liner

## Things that would make it NOT look like Notion

- Any top nav bar
- Card-based layouts with shadows
- Serif fonts
- Bright accent colors anywhere except callouts
- Tag clouds or pill rows (those are Hugo PaperMod)
- Multi-column footer (Notion has no footer, just an inline "Last edited")
- Centered content (Notion content is left-aligned with a large left margin)
- Any blue/purple links (Notion links are black with underline by default)

## Smoke test checklist

After rendering Abernathy, verify:

- [ ] Cover band at top with a gradient
- [ ] Large page icon overlapping cover (emoji or headshot)
- [ ] Name rendered as massive bold H1
- [ ] One-liner appears as a blockquote, italic
- [ ] No traditional nav bar anywhere
- [ ] Email `abernathy@merrow.edu` visible in Contact section
- [ ] Office `Hale Building, Office 3N-17` visible in Contact section
- [ ] Office hours visible in Contact section
- [ ] Mailing address is inside a `<details>` toggle block (click to expand)
- [ ] Publications are in an inline database table, not a prose list
- [ ] Publications table has 6 rows, sorted by year descending, including the
      forthcoming book "Compiled Fictions" at the top
- [ ] Teaching grouped by semester inside toggle blocks
- [ ] Fall 2025 toggle is open by default, Spring 2026 is closed
- [ ] Advisees section has 2 entries (Robin, Anh)
- [ ] Prospective students callout visible (accepting = true for Abernathy)
- [ ] Links section has github, bluesky, personal blog
- [ ] Text color is warm brown-grey `#37352f`, NOT pure black
- [ ] Content column is narrow (~700px) with large left/right margins
- [ ] "Last edited: ..." line at the bottom using `site_meta.last_updated`
- [ ] No `null` text anywhere
