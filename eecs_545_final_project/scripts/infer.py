# scripts/infer.py
# Runs text-only inference on house-renting-eval tasks
# using gpt-oss-120B via the class server.
# Saves raw outputs to results/raw_outputs/

import json, os, time
from pathlib import Path
from openai import OpenAI
from playwright.sync_api import sync_playwright

# ============================================================
# CONFIGURATION
# ============================================================
# TASK_FILE   = Path("house-renting-eval/tasks.json")
TASK_FILE   = Path("house-renting-eval/tasks_test.json")
OUTPUT_DIR  = Path("results/raw_outputs/house_renting")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL       = "openai/gpt-oss-120b"
TEMPERATURE = 0.0
MAX_TOKENS  = 500
PAUSE       = 1.0    # seconds between requests

client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"]
)

# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are a web agent evaluating rental property listings.
You are given the text content of a web page and a task.
Your job is to find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- If the information requires clicking a button or navigating to a tab,
  say what action is needed and what the answer would be
- If information is not visible on the page, say 'Not visible'
- Be precise: return exact values like '$1,450/month' not 'fourteen fifty'
"""

# ============================================================
# FUNCTION 1: Extract page text using Playwright
# ============================================================
def get_page_text(url):
    """Load a page and extract its visible text content."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            # get all visible text
            text = page.evaluate("""() => {
                // remove script and style tags
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
# FUNCTION 2: Build prompt for text-only mode
# ============================================================
def build_prompt(page_text, instruction, interaction):
    """Build the user prompt for text-only mode."""

    # truncate page text if too long
    if len(page_text) > 6000:
        page_text = page_text[:6000] + "\n...[truncated]"

    # add interaction hint if needed
    interaction_hint = ""
    if interaction and interaction != "none":
        hints = {
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
                "\nNote: Fee information may be under a 'Details' tab inside a 'Fees' expandable section.",
            "use_sidebar_city_filter":
                "\nNote: You may need to use a city filter in the sidebar to find this listing.",
        }
        interaction_hint = hints.get(interaction, "")

    prompt = f"""Page content:
{page_text}
{interaction_hint}

Task: {instruction}

Answer:"""

    return prompt


# ============================================================
# FUNCTION 3: Run inference for one task
# ============================================================
def run_task(task):
    """Run inference for a single task. Returns result dict."""
    task_id    = task["task_id"]
    url        = task["start_url"]
    instruction = task["instruction"]
    interaction = task.get("interaction", "none")

    output_path = OUTPUT_DIR / f"{task_id}.json"

    # skip if already done
    if output_path.exists():
        return None, "skipped"

    # get page text
    try:
        page_text = get_page_text(url)
    except Exception as e:
        page_text = f"ERROR: {e}"

    # build prompt
    prompt = build_prompt(page_text, instruction, interaction)

    # run inference
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

    # save result
    result = {
        "task_id":    task_id,
        "website":    task.get("website", "house_renting"),
        "template":   task["template"],
        "instruction": instruction,
        "interaction": interaction,
        "perturbation_type": task.get("perturbation_type", ""),
        "start_url":  url,
        "raw_output": raw_output,
        "error":      error,
        "model":      MODEL,
        "mode":       "text_only"
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result, "done"


# ============================================================
# MAIN
# ============================================================
print("Loading tasks...")
with open(TASK_FILE) as f:
    tasks = json.load(f)

print(f"Found {len(tasks)} tasks")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Model: {MODEL}")
print(f"Mode: text-only\n")

stats = {"done": 0, "skipped": 0, "error": 0}

for i, task in enumerate(tasks):
    task_id  = task["task_id"]
    template = task["template"]

    print(f"[{i+1}/{len(tasks)}] {task_id} ({template})...", end=" ", flush=True)

    result, status = run_task(task)

    if status == "skipped":
        print("skipped")
        stats["skipped"] += 1
    elif result and result["error"]:
        print(f"ERROR: {result['error'][:50]}")
        stats["error"] += 1
    else:
        print(f"done → {result['raw_output'][:50] if result['raw_output'] else 'None'}")
        stats["done"] += 1

    time.sleep(PAUSE)

# summary
print(f"\n{'='*45}")
print(f"Inference complete")
print(f"{'='*45}")
print(f"Done:    {stats['done']}")
print(f"Skipped: {stats['skipped']}")
print(f"Errors:  {stats['error']}")
print(f"\nResults saved to: {OUTPUT_DIR}")