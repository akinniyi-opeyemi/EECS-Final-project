# scripts/infer.py
# Configurable inference script for all four websites.
# Usage:
#   python scripts/infer.py --website house_renting
#   python scripts/infer.py --website personal_website
#   python scripts/infer.py --website job_application
#   python scripts/infer.py --website course_registration
#   python scripts/infer.py --website house_renting --test
#   (--test runs only first 3 tasks)

import json, os, time, argparse
from pathlib import Path
from openai import OpenAI
from playwright.sync_api import sync_playwright

# ============================================================
# WEBSITE CONFIGURATIONS
# ============================================================
CONFIGS = {
    "house_renting": {
        "task_file":  Path("house-renting-eval/tasks.json"),
        "output_dir": Path("results/raw_outputs/house_renting"),
        "system_prompt": """You are a web agent evaluating rental property listings.
You are given the text content of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- Be precise: return exact values like '$1,450/month' not 'fourteen fifty'
- If information is not visible, say 'Not visible'
"""
    },
    "personal_website": {
        "task_file":  Path("Personal Website/tasks/test.raw.json"),
        "output_dir": Path("results/raw_outputs/personal_website"),
        "system_prompt": """You are a web agent evaluating academic personal websites.
You are given the text content of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- If information is not on this page, it may be on a linked page
  like publications or teaching
- If information is not found anywhere, say 'Not found'
- Be precise with names, titles, and dates
"""
    },
    "job_application": {
        "task_file":  Path("job_application/tasks.json"),
        "output_dir": Path("results/raw_outputs/job_application"),
        "system_prompt": """You are a web agent evaluating job application websites.
You are given the text content of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- If information requires clicking a button, note that
- Be precise with job titles, dates, and requirements
"""
    },
    "course_registration": {
        "task_file":  Path("course_registration/tasks_v2.json"),
        "output_dir": Path("results/raw_outputs/course_registration"),
        "system_prompt": """You are a web agent evaluating a course registration system.
You are given the text content of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- Course codes, instructor names, and times must be exact
- If a filter or search is needed, describe what you would do
"""
    }
}

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--website",
    required=True,
    choices=list(CONFIGS.keys()),
    help="Which website to run inference on"
)
parser.add_argument(
    "--test",
    action="store_true",
    help="Run only first 3 tasks for testing"
)
args = parser.parse_args()

config     = CONFIGS[args.website]
TASK_FILE  = config["task_file"]
OUTPUT_DIR = config["output_dir"]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SYSTEM_PROMPT = config["system_prompt"]

# ============================================================
# MODEL CONFIGURATION
# ============================================================
MODEL       = "openai/gpt-oss-120b"
TEMPERATURE = 0.0
MAX_TOKENS  = 500
PAUSE       = 1.0

client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"]
)

# ============================================================
# FUNCTION 1: Extract page text
# ============================================================
def get_page_text(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            text = page.evaluate("""() => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, noscript').forEach(
                    el => el.remove()
                );
                return clone.innerText.trim();
            }""")
        except Exception as e:
            text = f"ERROR loading page: {e}"
        finally:
            browser.close()
    return text


# ============================================================
# FUNCTION 2: Build prompt
# ============================================================
def build_prompt(page_text, instruction, interaction="none"):
    if len(page_text) > 6000:
        page_text = page_text[:6000] + "\n...[truncated]"

    interaction_hints = {
        "click_show_details_button":
            "\nNote: Some information may be hidden behind a 'Show Details' button.",
        "click_apply_tab":
            "\nNote: Some information may be under an 'Apply' tab.",
        "click_contact_tab":
            "\nNote: Contact information may be under a 'Contact' tab.",
        "click_details_tab":
            "\nNote: Some information may be under a 'Details' tab.",
        "click_details_tab_then_toggle":
            "\nNote: Some information may be under a 'Details' tab inside an expandable section.",
        "click_details_tab_then_fees_toggle":
            "\nNote: Fee information may be under a 'Details' tab inside a 'Fees' section.",
        "use_sidebar_city_filter":
            "\nNote: You may need to use a city filter in the sidebar.",
    }
    hint = interaction_hints.get(interaction, "")

    return f"""Page content:
{page_text}
{hint}

Task: {instruction}

Answer:"""


# ============================================================
# FUNCTION 3: Run one task
# ============================================================
def run_task(task):
    task_id     = task["task_id"]
    url         = task.get("start_url", "")
    instruction = task.get("instruction") or task.get("intent", "")
    interaction = task.get("interaction", "none")

    output_path = OUTPUT_DIR / f"{task_id}.json"

    if output_path.exists():
        return None, "skipped"

    try:
        page_text = get_page_text(url)
    except Exception as e:
        page_text = f"ERROR: {e}"

    prompt = build_prompt(page_text, instruction, interaction)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        raw_output = response.choices[0].message.content.strip()
        error = None
    except Exception as e:
        raw_output = None
        error = str(e)

    result = {
        "task_id":           str(task_id),
        "website":           args.website,
        "template":          task.get("template", ""),
        "instruction":       instruction,
        "interaction":       interaction,
        "perturbation_type": task.get("perturbation_type", ""),
        "start_url":         url,
        "raw_output":        raw_output,
        "error":             error,
        "model":             MODEL,
        "mode":              "text_only"
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result, "done"


# ============================================================
# MAIN
# ============================================================
print(f"Website:  {args.website}")
print(f"Tasks:    {TASK_FILE}")
print(f"Output:   {OUTPUT_DIR}")
print(f"Model:    {MODEL}")
print(f"Mode:     text-only")
if args.test:
    print(f"Mode:     TEST (first 3 tasks only)")
print()

with open(TASK_FILE) as f:
    tasks = json.load(f)

if args.test:
    tasks = tasks[:3]

print(f"Loaded {len(tasks)} tasks\n")

stats = {"done": 0, "skipped": 0, "error": 0}

for i, task in enumerate(tasks):
    task_id  = str(task["task_id"])
    template = task.get("template", "")

    print(f"[{i+1}/{len(tasks)}] {task_id} ({template})...",
          end=" ", flush=True)

    result, status = run_task(task)

    if status == "skipped":
        print("skipped")
        stats["skipped"] += 1
    elif result and result["error"]:
        print(f"ERROR: {result['error'][:50]}")
        stats["error"] += 1
    else:
        out = result['raw_output'][:50] if result and result['raw_output'] else 'None'
        print(f"done → {out}")
        stats["done"] += 1

    time.sleep(PAUSE)

print(f"\n{'='*45}")
print(f"Inference complete")
print(f"{'='*45}")
print(f"Done:    {stats['done']}")
print(f"Skipped: {stats['skipped']}")
print(f"Errors:  {stats['error']}")
print(f"\nResults saved to: {OUTPUT_DIR}")