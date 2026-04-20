# scripts/infer_rq2.py
# RQ II: Test-time intervention strategies
# Runs memory and CoT agents on failed tasks from vanilla
# Usage:
#   python scripts/infer_rq2.py --website house_renting --mode vision_only --strategy memory
#   python scripts/infer_rq2.py --website house_renting --mode vision_only --strategy cot
#   python scripts/infer_rq2.py --website house_renting --mode vision_only --strategy all

import json, os, time, argparse, base64
from pathlib import Path
from openai import OpenAI
from playwright.sync_api import sync_playwright
from interventions import memory_agent, cot_agent

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument("--website", required=True,
    choices=["house_renting", "personal_website"])
parser.add_argument("--mode", required=True,
    choices=["text_only", "multimodal", "vision_only"])
parser.add_argument("--strategy", required=True,
    choices=["memory", "cot", "all"])
parser.add_argument("--test", action="store_true",
    help="Run only first 5 failed tasks")
args = parser.parse_args()

# ============================================================
# MODEL
# ============================================================
if args.mode == "text_only":
    MODEL  = "openai/gpt-oss-120b"
    client = OpenAI(
        base_url=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"]
    )
else:
    MODEL  = "Qwen/Qwen3-VL-30B-A3B-Instruct"
    client = OpenAI(
        base_url=os.environ["QWEN_BASE_URL"],
        api_key=os.environ["QWEN_API_KEY"]
    )

TEMPERATURE = 0.0
MAX_TOKENS  = 600
PAUSE       = 1.5

# ============================================================
# WEBSITE CONFIG
# ============================================================
TASK_FILES = {
    "house_renting":   Path("house-renting-eval/tasks.json"),
    "personal_website": Path("Personal Website/tasks/test.raw.json")
}

SYSTEM_PROMPTS = {
    "house_renting": {
        "text_only": "You are a web agent evaluating rental property listings. Return ONLY the answer.",
        "vision":    "You are a web agent evaluating rental property listings. Return ONLY the answer."
    },
    "personal_website": {
        "text_only": "You are a web agent evaluating academic personal websites. Return ONLY the answer.",
        "vision":    "You are a web agent evaluating academic personal websites. Return ONLY the answer."
    }
}

# ============================================================
# LOAD FAILED TASKS FROM VANILLA RUN
# ============================================================
def load_failed_tasks(website, mode):
    """Load tasks that vanilla agent failed on."""
    metrics_path = Path(f"results/metrics/{website}/{mode}/per_task_results.json")
    if not metrics_path.exists():
        print(f"No vanilla results found at {metrics_path}")
        print(f"Run vanilla inference first: python scripts/infer.py --website {website} --mode {mode}")
        exit(1)

    with open(metrics_path) as f:
        results = json.load(f)

    failed_ids = {r["task_id"] for r in results if not r["success"]}
    print(f"Found {len(failed_ids)} failed tasks from vanilla {mode}")

    with open(TASK_FILES[website]) as f:
        all_tasks = json.load(f)

    failed_tasks = [t for t in all_tasks
                    if str(t["task_id"]) in failed_ids]
    print(f"Matched {len(failed_tasks)} tasks")
    return failed_tasks


# ============================================================
# PLAYWRIGHT HELPERS
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
                    el => el.remove());
                return clone.innerText.trim();
            }""")
        except Exception as e:
            text = f"ERROR: {e}"
        finally:
            browser.close()
    return text


def get_screenshot_b64(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            screenshot_bytes = page.screenshot(full_page=False)
        except Exception as e:
            screenshot_bytes = None
        finally:
            browser.close()
    if screenshot_bytes:
        return base64.b64encode(screenshot_bytes).decode()
    return None


# ============================================================
# RUN ONE STRATEGY ON ONE TASK
# ============================================================
def run_strategy(task, strategy_name, output_dir):
    task_id     = str(task["task_id"])
    url         = task.get("start_url", "")
    instruction = task.get("instruction") or task.get("intent", "")
    interaction = task.get("interaction", "none")

    output_path = output_dir / f"{task_id}.json"
    if output_path.exists():
        return None, "skipped"

    interaction_hints = {
        "click_show_details_button": "\nNote: Info may be behind 'Show Details' button.",
        "click_apply_tab":           "\nNote: Info may be under 'Apply' tab.",
        "click_contact_tab":         "\nNote: Contact info may be under 'Contact' tab.",
        "click_details_tab":         "\nNote: Info may be under 'Details' tab.",
        "click_details_tab_then_toggle": "\nNote: Info may be under 'Details' tab in expandable section.",
        "use_sidebar_city_filter":   "\nNote: Use city filter in sidebar.",
    }
    hint = interaction_hints.get(interaction, "")

    # get page content
    page_text      = None
    screenshot_b64 = None

    if args.mode in ["text_only", "multimodal"]:
        page_text = get_page_text(url)

    if args.mode in ["multimodal", "vision_only"]:
        screenshot_b64 = get_screenshot_b64(url)

    # select agent
    agent = memory_agent if strategy_name == "memory" else cot_agent

    # build content
    sys_key = "text_only" if args.mode == "text_only" else "vision"
    system_prompt = SYSTEM_PROMPTS[args.website][sys_key]

    if args.mode == "text_only":
        content = agent.build_prompt(page_text, instruction, hint)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": content}
        ]
    else:
        content = agent.build_vision_content(
            screenshot_b64, instruction, hint, page_text
        )
        content_with_system = [{"type": "text", "text": system_prompt}] + content
        messages = [{"role": "user", "content": content_with_system}]

    # run inference
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        raw_output = response.choices[0].message.content.strip()

        # parse CoT output
        if strategy_name == "cot":
            raw_output = cot_agent.parse_cot_output(raw_output)

        error = None
    except Exception as e:
        raw_output = None
        error = str(e)

    result = {
        "task_id":           task_id,
        "website":           args.website,
        "template":          task.get("template", ""),
        "instruction":       instruction,
        "interaction":       interaction,
        "perturbation_type": task.get("perturbation_type", ""),
        "start_url":         url,
        "raw_output":        raw_output,
        "error":             error,
        "model":             MODEL,
        "mode":              args.mode,
        "strategy":          strategy_name
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result, "done"


# ============================================================
# MAIN
# ============================================================
strategies = (["memory", "cot"]
              if args.strategy == "all"
              else [args.strategy])

failed_tasks = load_failed_tasks(args.website, args.mode)

if args.test:
    failed_tasks = failed_tasks[:5]
    print(f"TEST MODE: running first 5 failed tasks")

print(f"Website:   {args.website}")
print(f"Mode:      {args.mode}")
print(f"Strategy:  {args.strategy}")
print(f"Model:     {MODEL}")
print(f"Tasks:     {len(failed_tasks)} failed tasks to retry")
print()

for strategy_name in strategies:
    output_dir = Path(
        f"results/raw_outputs/{args.website}/rq2_{strategy_name}_{args.mode}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*45}")
    print(f"Running strategy: {strategy_name}")
    print(f"Output: {output_dir}")
    print(f"{'='*45}\n")

    stats = {"done": 0, "skipped": 0, "error": 0}

    for i, task in enumerate(failed_tasks):
        task_id  = str(task["task_id"])
        template = task.get("template", "")

        print(f"[{i+1}/{len(failed_tasks)}] {task_id} ({template})...",
              end=" ", flush=True)

        result, status = run_strategy(task, strategy_name, output_dir)

        if status == "skipped":
            print("skipped")
            stats["skipped"] += 1
        elif result and result.get("error"):
            print(f"ERROR: {result['error'][:50]}")
            stats["error"] += 1
        else:
            out = result['raw_output'][:50] if result and result['raw_output'] else 'None'
            print(f"done → {out}")
            stats["done"] += 1

        time.sleep(PAUSE)

    print(f"\nStrategy {strategy_name} complete:")
    print(f"  Done: {stats['done']}, Skipped: {stats['skipped']}, Errors: {stats['error']}")