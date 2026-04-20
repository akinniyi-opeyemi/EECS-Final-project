"""Build CLI for the faculty site generator.

Usage:
    python build.py <persona_id> <template_name>
    python build.py --all
    python build.py --persona <persona_id>
    python build.py --template <template_name>
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
# Support both capitalizations for the personas folder.
PERSONAS_DIR = REPO_ROOT / "Personas"
if not PERSONAS_DIR.exists():
    PERSONAS_DIR = REPO_ROOT / "personas"
SITES_DIR = REPO_ROOT / "sites"
TEMPLATES_DIR = REPO_ROOT / "templates"


def discover_personas() -> list[str]:
    return sorted(p.stem for p in PERSONAS_DIR.glob("*.json"))


def discover_templates() -> list[str]:
    return sorted(
        p.stem for p in TEMPLATES_DIR.glob("*.py")
        if p.stem != "__init__"
    )


def load_persona(persona_id: str) -> dict:
    path = PERSONAS_DIR / f"{persona_id}.json"
    if not path.exists():
        raise SystemExit(f"persona not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_template(template_name: str):
    try:
        return importlib.import_module(f"templates.{template_name}")
    except ModuleNotFoundError as e:
        raise SystemExit(f"template not found: {template_name} ({e})")


def build_one(persona_id: str, template_name: str) -> Path:
    persona = load_persona(persona_id)
    module = load_template(template_name)
    if not hasattr(module, "render"):
        raise SystemExit(f"template {template_name} has no render() function")
    out_dir = SITES_DIR / f"{persona_id}__{template_name}"
    if out_dir.exists():
        # Deterministic overwrite: remove stale files first so the old output
        # doesn't leak through when a template no longer produces them.
        for child in out_dir.rglob("*"):
            if child.is_file():
                child.unlink()
    module.render(persona, out_dir)
    return out_dir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build faculty sites.")
    parser.add_argument("persona_id", nargs="?", help="Persona id (e.g., halvern_cs_001)")
    parser.add_argument("template_name", nargs="?", help="Template name (e.g., jekyll_alfolio)")
    parser.add_argument("--all", action="store_true", help="Build every (persona, template) pair")
    parser.add_argument("--persona", help="Build all templates for this persona")
    parser.add_argument("--template", help="Build all personas for this template")
    args = parser.parse_args(argv)

    personas = discover_personas()
    templates = discover_templates()

    pairs: list[tuple[str, str]] = []
    if args.all:
        pairs = [(p, t) for p in personas for t in templates]
    elif args.persona and args.template:
        pairs = [(args.persona, args.template)]
    elif args.persona:
        pairs = [(args.persona, t) for t in templates]
    elif args.template:
        pairs = [(p, args.template) for p in personas]
    elif args.persona_id and args.template_name:
        pairs = [(args.persona_id, args.template_name)]
    else:
        parser.print_help()
        return 2

    for pid, tname in pairs:
        out = build_one(pid, tname)
        print(f"built: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
