# Faculty Site Generator — CLAUDE.md

## What this project is

This project generates static "personal websites" for fictional faculty members
for use in evaluating a visual web GUI agent (VisualWebArena / VWA). The
research question: **how robust are VLM agents when the same information is
presented in different UI styles?**

Each fictional faculty member is defined by a persona JSON file. We render each
persona using multiple UI *templates* (different visual styles). The agent is
later asked to find specific information (contact info, office address,
publication counts, etc.) on these rendered sites. If the agent succeeds on one
template but fails on another for the same persona, that is a measurable UI
effect.

**This means the rendered sites are data, not products.** The visual
distinctiveness of each template, and the faithful round-tripping of every
persona field to the rendered HTML, matter more than code cleverness.

## Critical constraints (read before writing any code)

1. **Pastiche, not authentic.** We are NOT installing Hugo, Jekyll, Ruby,
   Node, or any static-site generator toolchain. Every template produces
   hand-authored HTML + CSS that *visually and structurally mimics* the target
   style (al-folio, Hugo PaperMod, Notion public page). Do not suggest
   installing Hugo or Jekyll. Do not use Jinja2 if a plain f-string will do
   (Jinja2 is fine if you want it, but don't add it as a dependency if the
   templates are simple enough without it).

2. **Deterministic build.** The same persona + same template must always
   produce byte-identical output. This rules out calling an LLM at build time,
   using random ordering, or including timestamps-of-generation in the HTML.
   The `site_meta.last_updated` field from the persona is allowed; anything
   from `datetime.now()` is not.

3. **Every "task-target" field must be findable on the rendered site.**
   Specifically, the agent will be asked about: name, title, department,
   office building + room, full mailing address, email, office phone, office
   hours, courses (code + title + room), most recent publication, number of
   publications per year, advisees / students, Google Scholar URL, and whether
   the persona is accepting students. If a field is non-null in the persona
   JSON, it MUST be present somewhere on the rendered site. Templates can
   differ in *where* and *how prominently*, but not in *whether*. If a field
   is null in the persona, the template should omit the corresponding UI
   element entirely (not render an empty row or a broken link).

4. **Self-contained output.** Each generated site folder must be openable by
   double-clicking `index.html` or serving with `python -m http.server`, with
   no external CSS or JS dependencies. Inline CSS, or a single `style.css`
   next to `index.html`, is preferred. Do not load Tailwind, Bootstrap, or
   any CDN at runtime — if you want Tailwind-like utility classes, hand-write
   the CSS. (The VWA agent should not see a flash of unstyled content or fail
   because a CDN is blocked.)

5. **Static files only.** No JavaScript frameworks. A tiny amount of vanilla
   JS is fine for things like "expand/collapse sections" (Notion-style toggles)
   or mobile nav, but the page must be fully legible with JS disabled — all
   task-target fields must be in the initial HTML, not rendered by JS at
   runtime. This matters because the VWA agent parses the DOM after load and
   we don't want tasks to accidentally depend on JS execution.

6. **Image paths are relative and short.** When copying a persona's
   `photo_source` into a site folder, place it at `./headshot.jpg` (or
   `./assets/headshot.jpg` if the template has an `assets/` convention) and
   reference it with a relative path. Do not use absolute filesystem paths or
   `file://` URLs.

## Repository layout

```
project-root/
├── CLAUDE.md                      # This file
├── personas/                      # Source of truth for persona data
│   ├── halvern_cs_001.json
│   ├── thornfield_anth_001.json
│   ├── merrow_lit_001.json
│   └── images/
│       ├── halvern_cs_001_headshot.jpg
│       ├── thornfield_anth_001_headshot.jpg
│       └── merrow_lit_001_headshot.jpg
├── templates/                     # One Python module per UI template
│   ├── __init__.py
│   ├── specs/                     # Markdown specs describing each template
│   │   ├── jekyll_alfolio.md
│   │   ├── hugo_papermod.md
│   │   └── notion.md
│   ├── jekyll_alfolio.py          # def render(persona: dict, out_dir: Path) -> None
│   ├── hugo_papermod.py
│   └── notion.py
├── build.py                       # CLI: python build.py <persona_id> <template>
└── sites/                         # Generated output (gitignored)
    └── <persona_id>__<template>/
        ├── index.html
        ├── style.css
        ├── headshot.jpg
        └── (subpages as needed)
```

## The persona schema (v0.2)

Personas are JSON. The important contract:

- **Any field ending in `_source`** is a path *relative to the `personas/`
  folder*, pointing to a file on disk that must be copied into the rendered
  site. Examples: `assets.photo_source`, `group.group_photo_source`. A
  `_source` field of `null` means "no such file; skip rendering."
- **Any field ending in `_url`** is a real external URL (e.g.,
  `social.google_scholar`). Render as a link. A `_url` field of `null` means
  "don't render this link at all."
- **`null` always means "omit from rendering"**, never "render as empty."
  This is how we avoid broken sections and dangling links.
- **`group.name` being null** signals a humanities-style persona (no lab).
  Render the "Students / Advisees" section from `group.advisees` instead of
  `group.current_phd_students`. For CS-style personas where `group.name` is
  non-null, render a proper "Lab" section with PhD students, masters
  students, and alumni.
- **`prospective_students.accepting`** is three-valued: `true` (render a
  "Prospective Students" note, positive framing), `false` (render a "not
  accepting students this cycle" note), `null` (do not render any
  prospective-students section; typical for undergrad-only institutions). In
  all three cases, `prospective_students.note` holds the natural-language
  text to show if the section is rendered.
- **`publications[*].type`** is one of `"article"`, `"book"`, `"chapter"`,
  `"review"`. Templates may render different types differently (e.g., books
  with a cover thumbnail, articles as one-line entries), but all publications
  must appear somewhere.

See `personas/halvern_cs_001.json` for a fully populated example.

## What "render" means

For each template, the `render(persona, out_dir)` function must:

1. Create `out_dir` if it doesn't exist.
2. Copy the persona's headshot from `personas/<photo_source>` to
   `out_dir/headshot.jpg` (or the template's chosen filename). If
   `photo_source` is null, skip the headshot element in HTML.
3. If `group.group_photo_source` is non-null, copy that too.
4. Write `index.html` and any CSS/subpages the template needs.
5. Not print anything to stdout unless there's an error. Build output is
   handled by `build.py`.

The `render` function is pure in intent: same input → same output. No
randomness, no network, no time-dependent behavior.

## The build CLI

`build.py` is a thin dispatcher:

```
python build.py <persona_id> <template_name>
python build.py --all                              # build every (persona, template) pair
python build.py --persona halvern_cs_001           # all templates for one persona
python build.py --template jekyll_alfolio          # all personas for one template
```

Output goes to `sites/<persona_id>__<template_name>/`. Existing output folders
are overwritten (since the build is deterministic, this is safe).

## Workflow for adding a template

When asked to implement a new template:

1. Read the template's spec file in `templates/specs/<name>.md` first. The
   spec is authoritative for visual style, layout, field placement, and the
   "what should this look like" decisions.
2. Read `personas/halvern_cs_001.json` and at least one humanities persona
   (Thornfield or Merrow) so you understand how nulls and branching fields
   behave across persona types.
3. Write `templates/<name>.py` with a single `render(persona, out_dir)`
   function. Use plain Python string formatting or f-strings. Jinja2 is fine
   if you prefer, but add it to a requirements file if you do.
4. **Smoke test**: after writing the template, actually run it on all three
   personas and open the output in a browser. Verify visually that:
   - The page looks like the target style (not generic)
   - All task-target fields are visibly present
   - Null fields are silently omitted, not rendered as empty rows
   - The headshot is displayed and loads from a relative path
   - Humanities personas don't have a "Lab" section with zero members
5. Report back with: which persona you tested, a one-line summary of what
   the page looks like, and any fields you weren't sure where to place.

## What NOT to do

- Do not install Hugo, Jekyll, or any static-site generator.
- Do not fetch anything from the network at build time.
- Do not use `datetime.now()`, `random`, or anything non-deterministic.
- Do not create a shared "base template" that all three inherit from. The
  whole point is that the three templates should produce structurally
  different HTML. A shared base would make them look more similar than we
  want. Each template is its own self-contained file.
- Do not minify HTML or CSS. Readable output is easier to debug and the VWA
  agent doesn't care.
- Do not add a favicon, robots.txt, or sitemap.xml unless asked.
- Do not add analytics, tracking pixels, or any third-party embeds.
- Do not write unit tests for the templates. Visual inspection is the test.
  (A smoke test that each template runs without crashing on each persona is
  fine if you want it.)

## Ground truth for the experiment

Every task-target field's ground-truth value is literally the persona JSON.
Evaluation will be done by comparing the agent's answer to the persona field
directly. This means: do not transform field values before rendering them.
Render "Ramsey Hall" as "Ramsey Hall", not "Hall, Ramsey" or "ramsey hall".
Render the phone as "+1 (419) 555-0142", not as "(419) 555-0142" or
"419-555-0142". If a template's aesthetic calls for a transformation (e.g., a
minimalist template might want to drop the "+1" country code), discuss it
with the user first — it's a research-design decision, not a style decision.
