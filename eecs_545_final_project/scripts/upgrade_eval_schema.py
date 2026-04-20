# scripts/upgrade_eval_schema.py
# Upgrades all four website task JSONs to the three-tier
# evaluation schema standard.

import json
from pathlib import Path

# ============================================================
# CONFIGURATION: paths to each website's task file
# ============================================================
TASK_FILES = {
    "house_renting":      Path("house-renting-eval/tasks.json"),
    "job_application":    Path("job_application/tasks.json"),
    "course_registration": Path("course_registration/tasks.json"),
    "personal_website":   Path("Personal Website/tasks/test.raw.json"),
}

OUTPUT_FILES = {
    "house_renting":      Path("house-renting-eval/tasks_v2.json"),
    "job_application":    Path("job_application/tasks_v2.json"),
    "course_registration": Path("course_registration/tasks_v2.json"),
    "personal_website":   Path("Personal Website/tasks/test_v2.json"),
}

# ============================================================
# HELPER: build three-tier eval from a simple target string
# ============================================================
def build_three_tier(target, interaction=None):
    """
    Given a simple target string, build a three-tier
    evaluation block.

    Rules:
    - exact_match: use if target is a precise value
                   (price, date, code, email, short string)
    - must_include: extract key fragments that must appear
    - fuzzy_match:  paraphrase variants of the answer
    """
    if not target:
        return {
            "exact_match": None,
            "must_include": [],
            "fuzzy_match": []
        }

    target = target.strip()

    # determine if this is a precise value
    # (prices, dates, emails, short codes, yes/no)
    is_precise = (
        target.startswith("$") or        # price
        any(m in target for m in [
            "January", "February", "March", "April",
            "May", "June", "July", "August", "September",
            "October", "November", "December"
        ]) or                             # date
        "@" in target or                  # email
        len(target) <= 20 or             # short value
        target in ["Available",
                   "Not Available",
                   "N/A", "OPEN",
                   "CLOSED"]             # status
    )

    exact_match = target if is_precise else None

    # must_include: extract key fragments
    must_include = build_must_include(target)

    # fuzzy_match: paraphrase the answer
    fuzzy_match = build_fuzzy_match(target)

    return {
        "exact_match": exact_match,
        "must_include": must_include,
        "fuzzy_match": fuzzy_match
    }


def build_must_include(target):
    """Extract key fragments that must appear in any valid answer."""
    if not target:
        return []

    fragments = []

    # for prices: extract the number
    if target.startswith("$"):
        fragments.append(target)           # full price
        # also add without dollar sign
        stripped = target.replace("$", "").replace(",", "")
        if stripped not in fragments:
            fragments.append(target.split("/")[0])

    # for dates: include month and year
    elif any(m in target for m in [
        "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October",
        "November", "December"
    ]):
        fragments.append(target)
        # also add year alone as backup
        for part in target.split():
            if part.isdigit() and len(part) == 4:
                fragments.append(part)

    # for emails: include full email
    elif "@" in target:
        fragments.append(target)

    # for availability status
    elif target in ["Available", "Not Available"]:
        fragments.append(target)

    # for N/A
    elif target == "N/A":
        fragments.append("N/A")

    # for numeric values (bedrooms, fees)
    elif target.isdigit() or target in ["Studio", "1", "2", "3", "4"]:
        fragments.append(target)

    # for longer text: use the full target
    else:
        fragments.append(target)

    return fragments


def build_fuzzy_match(target):
    """Build paraphrase variants of the answer."""
    if not target:
        return []

    fuzzy = [target]  # always include original

    # price variants
    if target.startswith("$") and "/month" in target:
        price = target.replace("/month", "").strip()
        fuzzy.append(f"The monthly rent is {price}")
        fuzzy.append(f"rent of {target}")
        fuzzy.append(target.replace("/month", " per month"))

    # availability variants
    elif target == "Available":
        fuzzy.extend([
            "currently available",
            "is available for rent",
            "available for rent",
            "yes, available"
        ])
    elif target == "Not Available":
        fuzzy.extend([
            "not currently available",
            "is not available",
            "unavailable",
            "no longer available"
        ])

    # N/A variants
    elif target == "N/A":
        fuzzy.extend([
            "not applicable",
            "no deadline",
            "no application deadline",
            "not listed"
        ])

    # bedroom variants
    elif target == "Studio":
        fuzzy.extend([
            "studio apartment",
            "studio unit",
            "0 bedrooms"
        ])
    elif target.isdigit():
        num = int(target)
        words = ["zero", "one", "two", "three", "four",
                 "five", "six", "seven", "eight", "nine"]
        if num < len(words):
            fuzzy.append(f"{words[num]} bedroom")
            fuzzy.append(f"{words[num]} bedrooms")

    return fuzzy


# ============================================================
# UPGRADER 1: house_renting
# ============================================================
def upgrade_house_renting(tasks):
    """
    Input schema:
    {
      "task_id": "C_01_T01",
      "template": "classic",
      "env_id": "...",
      "start_url": "http://localhost:8000/...",
      "instruction": "...",
      "interaction": "none",
      "evaluation": {
        "type": "string_match",
        "target": "$1,450/month"
      }
    }
    """
    upgraded = []
    for task in tasks:
        target = task.get("evaluation", {}).get("target", "")
        interaction = task.get("interaction", "none")

        # determine perturbation type from interaction
        perturbation_type = classify_perturbation(interaction)

        new_task = {
            "task_id":          task["task_id"],
            "website":          "house_renting",
            "template":         task["template"],
            "env_id":           task["env_id"],
            "start_url":        task["start_url"],
            "instruction":      task["instruction"],
            "interaction":      interaction,
            "perturbation_type": perturbation_type,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": build_three_tier(target, interaction),
                "reference_answer_raw_annotation": target
            }
        }
        upgraded.append(new_task)
    return upgraded


def classify_perturbation(interaction):
    """Map interaction type to perturbation category for RQ I."""
    mapping = {
        "none":                        "visible",
        "click_show_details_button":   "click_to_reveal",
        "click_apply_tab":             "tab_navigation",
        "click_contact_tab":           "tab_navigation",
        "click_details_tab":           "tab_navigation",
        "click_details_tab_then_toggle": "tab_then_expand",
        "click_details_tab_then_fees_toggle": "tab_then_expand",
        "use_sidebar_city_filter":     "filter_navigation",
    }
    return mapping.get(interaction, "unknown")


# ============================================================
# UPGRADER 2: job_application
# ============================================================
def upgrade_job_application(tasks):
    """
    Input schema:
    {
      "task_id": "J01_classic",
      "env_id": "job_site_classic",
      "instruction": "...",
      "evaluation": {
        "type": "string_match",
        "target": "most recent"
      }
    }
    """
    # template name mapping
    template_map = {
        "job_site_classic": "classic",
        "job_site_modern":  "modern",
        "job_site_notion":  "notion"
    }

    # start_url mapping
    url_map = {
        "job_site_classic": "http://localhost:8002/templates/job_site_1_classic.html",
        "job_site_modern":  "http://localhost:8002/templates/job_site_2_modern.html",
        "job_site_notion":  "http://localhost:8002/templates/job_site_3_notion.html"
    }

    upgraded = []
    for task in tasks:
        env_id = task.get("env_id", "")
        target = task.get("evaluation", {}).get("target", "")
        eval_type = task.get("evaluation", {}).get("type", "string_match")

        # extract task type from task_id (J01, J02 etc)
        task_base = task["task_id"].split("_")[0]

        new_task = {
            "task_id":    task["task_id"],
            "website":    "job_application",
            "template":   template_map.get(env_id, env_id),
            "env_id":     env_id,
            "start_url":  url_map.get(env_id, ""),
            "instruction": task["instruction"],
            "interaction": "none",
            "perturbation_type": "layout_style",
            "eval": {
                "eval_types": [eval_type],
                "reference_answers": build_three_tier(target),
                "reference_answer_raw_annotation": target
            }
        }
        upgraded.append(new_task)
    return upgraded


# ============================================================
# UPGRADER 3: course_registration
# ============================================================
def upgrade_course_registration(tasks):
    """
    Input schema:
    {
      "id": "find_cs310",
      "category": "course_lookup",
      "prompt": "Find CS 310..."
    }
    No evaluation targets exist. We add placeholders
    with verified=false so they can be filled manually.
    """
    # template url mapping
    url_map = {
        "2000s":  "http://localhost:8001/2000s/index.html",
        "2010s":  "http://localhost:8001/2010s/index.html",
        "modern": "http://localhost:8001/modern/index.html",
    }

    templates = ["2000s", "2010s", "modern"]
    upgraded = []

    for task in tasks["tasks"]:
        for template in templates:
            new_task = {
                "task_id":    f"{task['id']}_{template}",
                "website":    "course_registration",
                "template":   template,
                "env_id":     f"course_{template}",
                "start_url":  url_map[template],
                "instruction": task["prompt"],
                "category":   task["category"],
                "interaction": "varies",
                "perturbation_type": "era_style",
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": {
                        "exact_match":  None,
                        "must_include": [],
                        "fuzzy_match":  []
                    },
                    "reference_answer_raw_annotation": "",
                    "verified": False,
                    "note": "Ground truth not yet annotated. Fill manually."
                }
            }
            upgraded.append(new_task)
    return upgraded


# ============================================================
# UPGRADER 4: personal_website
# ============================================================
def upgrade_personal_website(tasks):
    """
    Already has good schema. Standardize field names
    and add perturbation_type + website fields.
    Also normalize eval block to match our standard.
    """
    template_complexity = {
        "jekyll_alfolio":  "modern_academic",
        "raw_html_1998":   "retro_minimal",
        "notion":          "structured_blocks",
        "hugo_papermod":   "blog_style"
    }

    upgraded = []
    for task in tasks:
        template = task.get("template", "")

        # standardize eval block
        existing_eval = task.get("eval", {})
        ref_answers = existing_eval.get("reference_answers", {})

       # ensure all three tiers exist and are correct types
        if not ref_answers.get("exact_match"):
            ref_answers["exact_match"] = None
        if not ref_answers.get("must_include"):
            ref_answers["must_include"] = []
        if not ref_answers.get("fuzzy_match"):
            ref_answers["fuzzy_match"] = []

        new_task = {
            "task_id":          task["task_id"],
            "website":          "personal_website",
            "template":         template,
            "template_style":   template_complexity.get(template, "unknown"),
            "persona_id":       task.get("persona_id", ""),
            "env_id":           task.get("sites", [template])[0],
            "start_url":        task.get("start_url", ""),
            "instruction":      task.get("intent", ""),
            "task_type":        task.get("task_type", ""),
            "interaction":      "navigation",
            "perturbation_type": "framework_style",
            "viewport_size":    task.get("viewport_size",
                                        {"width": 1280, "height": 720}),
            "eval": {
                "eval_types": existing_eval.get("eval_types", ["string_match"]),
                "reference_answers": ref_answers,
                "reference_answer_raw_annotation":
                    existing_eval.get("reference_answer_raw_annotation", "")
            }
        }
        upgraded.append(new_task)
    return upgraded


# ============================================================
# MAIN: run all upgrades
# ============================================================
print("Upgrading evaluation schemas to three-tier standard...\n")

results = {}

# house_renting
print("1. house_renting...")
with open(TASK_FILES["house_renting"]) as f:
    tasks = json.load(f)
upgraded = upgrade_house_renting(tasks)
with open(OUTPUT_FILES["house_renting"], "w") as f:
    json.dump(upgraded, f, indent=2)
results["house_renting"] = len(upgraded)
print(f"   {len(upgraded)} tasks upgraded")

# job_application
print("2. job_application...")
with open(TASK_FILES["job_application"]) as f:
    tasks = json.load(f)
upgraded = upgrade_job_application(tasks)
with open(OUTPUT_FILES["job_application"], "w") as f:
    json.dump(upgraded, f, indent=2)
results["job_application"] = len(upgraded)
print(f"   {len(upgraded)} tasks upgraded")

# course_registration
print("3. course_registration...")
with open(TASK_FILES["course_registration"]) as f:
    tasks = json.load(f)
upgraded = upgrade_course_registration(tasks)
with open(OUTPUT_FILES["course_registration"], "w") as f:
    json.dump(upgraded, f, indent=2)
results["course_registration"] = len(upgraded)
print(f"   {len(upgraded)} tasks upgraded")
print(f"   NOTE: {len(upgraded)} tasks need manual ground truth annotation")

# personal_website
print("4. personal_website...")
with open(TASK_FILES["personal_website"]) as f:
    tasks = json.load(f)
upgraded = upgrade_personal_website(tasks)
with open(OUTPUT_FILES["personal_website"], "w") as f:
    json.dump(upgraded, f, indent=2)
results["personal_website"] = len(upgraded)
print(f"   {len(upgraded)} tasks upgraded")

# summary
print(f"\n{'='*45}")
print(f"Upgrade complete")
print(f"{'='*45}")
for site, count in results.items():
    print(f"  {site:<25} {count} tasks")
print(f"  {'TOTAL':<25} {sum(results.values())} tasks")
print(f"\nUpgraded files saved as *_v2.json")
print(f"Review before replacing originals.")