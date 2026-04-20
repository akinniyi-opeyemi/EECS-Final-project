"""Generate WebArena / VisualWebArena task JSON files from personas + sites.

For every built site folder under `sites/<persona_id>__<template>/`, emits
5 task-JSONs covering the 5 evaluation tasks:

  T1. Title of most recent publication
  T2. Office hours this semester
  T3. Current-semester course + location
  T4. Accepting prospective graduate students?
  T5. Twitter account

Output layout:

    tasks/
      config.json                  # shared generator config (as_of_date, base_url)
      test.raw.json                # flat array of every task (WebArena-ingestible)
      config_files/NNN.json        # one file per task, WebArena convention
      index/                       # cross-reference indexes for humans
        by_persona.json
        by_template.json
        by_task_type.json

Ground-truth values are derived directly from the persona JSON — no hand-
maintained answer key. Regenerate after persona edits.

Usage:
    python make_tasks.py
    python make_tasks.py --base-url http://localhost:8000
    python make_tasks.py --as-of 2025-10-15
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PERSONAS_DIR = REPO_ROOT / "Personas"
if not PERSONAS_DIR.exists():
    PERSONAS_DIR = REPO_ROOT / "personas"
SITES_DIR = REPO_ROOT / "sites"
TASKS_DIR = REPO_ROOT / "tasks"

DEFAULT_AS_OF = date(2025, 10, 15)
DEFAULT_BASE_URL = "http://localhost:8000"


# ---------- persona + site discovery ----------

def load_personas() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted(PERSONAS_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            p = json.load(f)
        out[p["persona_id"]] = p
    return out


def discover_built_sites() -> list[tuple[str, str]]:
    """Return [(persona_id, template_name), ...] for every folder under sites/."""
    if not SITES_DIR.exists():
        return []
    pairs: list[tuple[str, str]] = []
    for d in sorted(SITES_DIR.iterdir()):
        if not d.is_dir():
            continue
        if "__" not in d.name:
            continue
        persona_id, template = d.name.split("__", 1)
        pairs.append((persona_id, template))
    return pairs


# ---------- semester logic ----------

def _semester_bounds(sem: str) -> tuple[date, date] | None:
    if not sem:
        return None
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
    return None


def current_semester_courses(persona: dict, as_of: date) -> list[dict]:
    courses = []
    for c in persona.get("teaching") or []:
        b = _semester_bounds(c.get("semester") or "")
        if b and b[0] <= as_of <= b[1]:
            courses.append(c)
    return courses


def most_recent_publication(persona: dict) -> dict | None:
    pubs = persona.get("publications") or []
    if not pubs:
        return None
    # Stable: max year, break ties by first appearance (Python's max is stable).
    return max(pubs, key=lambda p: p.get("year", 0))


# ---------- task builders ----------

def task_t1_pub_title(persona: dict) -> tuple[str, dict]:
    pub = most_recent_publication(persona)
    name = persona["name"]["full"]
    intent = f"Find the title of the most recent publication of {name}."
    if not pub:
        return intent, _eval_fuzzy(f"{name} has no listed publications.")
    return intent, _eval_string_match(must_include=[pub["title"]],
                                      raw_annotation=pub["title"])


def task_t2_office_hours(persona: dict) -> tuple[str, dict]:
    name = persona["name"]["preferred"] or persona["name"]["full"]
    hours = (persona.get("office") or {}).get("hours") or ""
    intent = f"When does {name} hold office hours this semester?"
    if not hours:
        return intent, _eval_fuzzy(f"{name} does not list office hours on the page.")
    # Use both: a forgiving must_include anchor (day name) and a fuzzy full reference.
    day_anchors = [tok for tok in ("Monday", "Tuesday", "Wednesday", "Thursday",
                                   "Friday", "Saturday", "Sunday",
                                   "Mondays", "Tuesdays", "Wednesdays",
                                   "Thursdays", "Fridays")
                   if tok in hours]
    ev = _eval_string_match(must_include=day_anchors[:1],
                            fuzzy_match=[hours],
                            raw_annotation=hours)
    return intent, ev


def task_t3_current_course(persona: dict, as_of: date) -> tuple[str, dict]:
    name = persona["name"]["full"]
    courses = current_semester_courses(persona, as_of)
    intent = f"What course is {name} teaching this semester, and where does it take place?"
    if not courses:
        return intent, _eval_fuzzy(f"{name} is not teaching a course this semester.")
    ref_parts = []
    for c in courses:
        piece = f"{c.get('code','')} — {c.get('title','')}"
        if c.get("room"):
            piece += f", in {c['room']}"
        ref_parts.append(piece.strip())
    ref = "; ".join(ref_parts)
    # must_include at least the first course's code, for a cheap offline check.
    must = [courses[0].get("code", "")]
    if courses[0].get("room"):
        must.append(courses[0]["room"])
    ev = _eval_string_match(must_include=[m for m in must if m],
                            fuzzy_match=[ref],
                            raw_annotation=ref)
    return intent, ev


def task_t4_accepting(persona: dict) -> tuple[str, dict]:
    name = persona["name"]["full"]
    ps = persona.get("prospective_students") or {}
    accepting = ps.get("accepting")
    note = ps.get("note") or ""
    intent = f"Is {name} taking prospective graduate students in the upcoming academic year?"
    if accepting is True:
        ref = f"Yes, {name} is accepting prospective graduate students. Note: {note}".strip()
    elif accepting is False:
        ref = f"No, {name} is not accepting new graduate students. Note: {note}".strip()
    else:
        # null — typically undergrad-only institution or N/A
        ref = (
            f"Not applicable — the institution is undergraduate-only, or "
            f"the page does not list a graduate-student policy. Note: {note}"
        ).strip()
    return intent, _eval_fuzzy(ref)


def task_t5_twitter(persona: dict) -> tuple[str, dict]:
    name = persona["name"]["full"]
    twitter = (persona.get("social") or {}).get("twitter")
    intent = f"Find {name}'s Twitter account."
    if twitter:
        ev = _eval_string_match(must_include=[twitter], raw_annotation=twitter)
    else:
        ev = _eval_fuzzy(
            f"The page does not list a Twitter account for {name}."
        )
    return intent, ev


TASK_BUILDERS = [
    ("T1_recent_pub",       task_t1_pub_title),
    ("T2_office_hours",     task_t2_office_hours),
    ("T3_current_course",   task_t3_current_course),
    ("T4_accepting",        task_t4_accepting),
    ("T5_twitter",          task_t5_twitter),
]


# ---------- eval helpers ----------

def _eval_string_match(must_include: list[str] | None = None,
                       exact_match: str | None = None,
                       fuzzy_match: list[str] | None = None,
                       raw_annotation: str = "") -> dict:
    return {
        "eval_types": ["string_match"],
        "reference_answers": {
            "exact_match": exact_match,
            "must_include": must_include or None,
            "fuzzy_match": fuzzy_match or None,
        },
        "reference_url": "",
        "program_html": [],
        "string_note": "",
        "reference_answer_raw_annotation": raw_annotation,
    }


def _eval_fuzzy(reference: str) -> dict:
    return {
        "eval_types": ["string_match"],
        "reference_answers": {
            "exact_match": None,
            "must_include": None,
            "fuzzy_match": [reference],
        },
        "reference_url": "",
        "program_html": [],
        "string_note": "",
        "reference_answer_raw_annotation": reference,
    }


# ---------- task assembly ----------

def build_task(task_id: int,
               task_type: str,
               builder,
               persona: dict,
               template: str,
               base_url: str,
               as_of: date) -> dict:
    persona_id = persona["persona_id"]
    site_slug = f"{persona_id}__{template}"
    start_url = f"{base_url.rstrip('/')}/{site_slug}/"

    if builder is task_t3_current_course:
        intent, eval_block = builder(persona, as_of)
    else:
        intent, eval_block = builder(persona)

    return {
        "task_id": task_id,
        "task_type": task_type,
        "persona_id": persona_id,
        "template": template,
        "sites": [site_slug],
        "start_url": start_url,
        "geolocation": None,
        "require_login": False,
        "storage_state": None,
        "intent_template": _intent_template_for(task_type),
        "intent_template_id": _intent_template_id_for(task_type),
        "instantiation_dict": {"name": persona["name"]["full"]},
        "intent": intent,
        "require_reset": False,
        "viewport_size": {"width": 1280, "height": 720},
        "eval": eval_block,
    }


_INTENT_TEMPLATES = {
    "T1_recent_pub":     (1, "Find the title of the most recent publication of {name}."),
    "T2_office_hours":   (2, "When does {name} hold office hours this semester?"),
    "T3_current_course": (3, "What course is {name} teaching this semester, and where does it take place?"),
    "T4_accepting":      (4, "Is {name} taking prospective graduate students in the upcoming academic year?"),
    "T5_twitter":        (5, "Find {name}'s Twitter account."),
}


def _intent_template_for(task_type: str) -> str:
    return _INTENT_TEMPLATES[task_type][1]


def _intent_template_id_for(task_type: str) -> int:
    return _INTENT_TEMPLATES[task_type][0]


# ---------- writer ----------

def write_outputs(tasks: list[dict], as_of: date, base_url: str) -> None:
    TASKS_DIR.mkdir(exist_ok=True)
    (TASKS_DIR / "config_files").mkdir(exist_ok=True)
    (TASKS_DIR / "index").mkdir(exist_ok=True)

    # Per-task files
    existing = list((TASKS_DIR / "config_files").glob("*.json"))
    for f in existing:
        f.unlink()
    for t in tasks:
        with (TASKS_DIR / "config_files" / f"{t['task_id']}.json").open("w", encoding="utf-8") as f:
            json.dump(t, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # Flat aggregate
    with (TASKS_DIR / "test.raw.json").open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Indexes
    by_persona: dict[str, list[int]] = {}
    by_template: dict[str, list[int]] = {}
    by_task_type: dict[str, list[int]] = {}
    for t in tasks:
        by_persona.setdefault(t["persona_id"], []).append(t["task_id"])
        by_template.setdefault(t["template"], []).append(t["task_id"])
        by_task_type.setdefault(t["task_type"], []).append(t["task_id"])

    for name, data in [
        ("by_persona.json", by_persona),
        ("by_template.json", by_template),
        ("by_task_type.json", by_task_type),
    ]:
        with (TASKS_DIR / "index" / name).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    # Shared config
    config = {
        "as_of_date": as_of.isoformat(),
        "base_url": base_url,
        "task_count": len(tasks),
        "task_types": [
            {"id": tid, "key": key, "intent_template": tmpl}
            for key, (tid, tmpl) in _INTENT_TEMPLATES.items()
        ],
    }
    with (TASKS_DIR / "config.json").open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


# ---------- main ----------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="Base URL where the sites/ folder will be served.")
    ap.add_argument("--as-of", default=DEFAULT_AS_OF.isoformat(),
                    help="Fixed 'today' for determining current semester (YYYY-MM-DD).")
    args = ap.parse_args(argv)

    as_of = date.fromisoformat(args.as_of)
    personas = load_personas()
    pairs = discover_built_sites()
    if not pairs:
        raise SystemExit("No built sites found under sites/. Run build.py first.")

    tasks: list[dict] = []
    task_id = 0
    for persona_id, template in pairs:
        persona = personas.get(persona_id)
        if persona is None:
            print(f"warn: no persona for built site {persona_id}; skipping")
            continue
        for task_type, builder in TASK_BUILDERS:
            t = build_task(task_id, task_type, builder, persona, template,
                           args.base_url, as_of)
            tasks.append(t)
            task_id += 1

    write_outputs(tasks, as_of, args.base_url)
    print(f"wrote {len(tasks)} tasks for {len(pairs)} sites to tasks/")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
