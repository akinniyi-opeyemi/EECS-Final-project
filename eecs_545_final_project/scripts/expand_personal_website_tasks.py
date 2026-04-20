# scripts/expand_personal_website_tasks.py
# Expands personal website tasks from 4 (one per persona)
# to 80 (all persona x template combinations x 5 tasks)

import json
from pathlib import Path

TASK_FILE   = Path("Personal Website/tasks/test.raw.json")
OUTPUT_FILE = Path("Personal Website/tasks/test.raw.json")
BACKUP_FILE = Path("Personal Website/tasks/test.raw.backup.json")

# all personas and templates
PERSONAS = [
    "halvern_cs_001",
    "halvern_econ_001",
    "merrow_lit_001",
    "thornfield_anth_001"
]

TEMPLATES = [
    "jekyll_alfolio",
    "raw_html_1998",
    "notion",
    "hugo_papermod"
]

TEMPLATE_STYLE = {
    "jekyll_alfolio":  "modern_academic",
    "raw_html_1998":   "retro_minimal",
    "notion":          "structured_blocks",
    "hugo_papermod":   "blog_style"
}

# load existing tasks
print("Loading existing tasks...")
with open(TASK_FILE) as f:
    existing_tasks = json.load(f)

print(f"Found {len(existing_tasks)} existing tasks")

# backup original
with open(BACKUP_FILE, "w") as f:
    json.dump(existing_tasks, f, indent=2)
print(f"Backup saved to {BACKUP_FILE}")

# build a lookup of task types per persona
# so we can copy the eval block for each task type
# key: (persona_id, task_type) -> task
task_lookup = {}
for task in existing_tasks:
    key = (task["persona_id"], task["task_type"])
    task_lookup[key] = task

print(f"Task types found: {sorted(set(t['task_type'] for t in existing_tasks))}")

# generate all 80 tasks
new_tasks = []
task_id_counter = 0

for persona_id in PERSONAS:
    for template in TEMPLATES:
        # get the 5 task types for this persona
        # use existing persona tasks as source for eval blocks
        persona_tasks = [t for t in existing_tasks
                        if t["persona_id"] == persona_id]

        if not persona_tasks:
            print(f"WARNING: no tasks found for persona {persona_id}")
            continue

        for source_task in persona_tasks:
            task_type = source_task["task_type"]

            # build the new task
            new_task = {
                "task_id": task_id_counter,
                "task_type": task_type,
                "persona_id": persona_id,
                "template": template,
                "template_style": TEMPLATE_STYLE.get(template, "unknown"),
                "sites": [f"{persona_id}__{template}"],
                "start_url": f"http://localhost:8003/{persona_id}__{template}/",
                "geolocation": None,
                "require_login": False,
                "storage_state": None,
                "intent_template": source_task.get("intent_template", ""),
                "intent_template_id": source_task.get("intent_template_id"),
                "instantiation_dict": source_task.get("instantiation_dict", {}),
                "intent": source_task.get("intent", ""),
                "instruction": source_task.get("instruction",
                               source_task.get("intent", "")),
                "interaction": "navigation",
                "perturbation_type": "framework_style",
                "require_reset": False,
                "viewport_size": source_task.get("viewport_size",
                                {"width": 1280, "height": 720}),
                "website": "personal_website",
                "eval": source_task.get("eval", {})
            }

            new_tasks.append(new_task)
            task_id_counter += 1

# save expanded tasks
with open(OUTPUT_FILE, "w") as f:
    json.dump(new_tasks, f, indent=2)

# summary
print(f"\n{'='*45}")
print(f"Expansion complete")
print(f"{'='*45}")
print(f"Original tasks:  {len(existing_tasks)}")
print(f"Expanded tasks:  {len(new_tasks)}")
print(f"Personas:        {len(PERSONAS)}")
print(f"Templates:       {len(TEMPLATES)}")
print(f"Tasks per combo: {len(new_tasks) // (len(PERSONAS) * len(TEMPLATES))}")
print(f"\nBreakdown:")
for persona in PERSONAS:
    count = sum(1 for t in new_tasks if t["persona_id"] == persona)
    print(f"  {persona:<30} {count} tasks")
print(f"\nBy template:")
for template in TEMPLATES:
    count = sum(1 for t in new_tasks if t["template"] == template)
    print(f"  {template:<20} {count} tasks")
print(f"\nSaved to: {OUTPUT_FILE}")
print(f"Backup at: {BACKUP_FILE}")