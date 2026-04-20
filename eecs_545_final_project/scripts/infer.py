# scripts/infer.py
# Configurable inference script for all four websites.
# Supports text-only, multimodal, and vision-only modes.
# Supports multiple agents via --agent flag.
# Usage:
#   python scripts/infer.py --website house_renting --mode vision_only --agent qwen_vl
#   python scripts/infer.py --website house_renting --mode vision_only --agent uitars
#   python scripts/infer.py --website house_renting --mode vision_only --agent qwen25
#   python scripts/infer.py --website house_renting --mode vision_only --agent internvl
#   python scripts/infer.py --website house_renting --mode text_only --agent gpt_oss
#   python scripts/infer.py --website house_renting --mode vision_only --agent uitars --test

import json, os, time, argparse, base64
from pathlib import Path
from openai import OpenAI
from playwright.sync_api import sync_playwright

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--website",
    required=True,
    choices=["house_renting", "personal_website",
             "job_application", "course_registration"],
)
parser.add_argument(
    "--mode",
    required=True,
    choices=["text_only", "multimodal", "vision_only"],
)
parser.add_argument(
    "--agent",
    required=True,
    choices=["gpt_oss", "qwen_vl", "uitars", "qwen25", "internvl"],
    help="Which agent to use"
)
parser.add_argument(
    "--test",
    action="store_true",
    help="Run only first 3 tasks for testing"
)
args = parser.parse_args()

# ============================================================
# AGENT CONFIGURATIONS
# ============================================================
AGENT_CONFIGS = {
    "gpt_oss": {
        "model":    "openai/gpt-oss-120b",
        "base_url": os.environ.get("OPENAI_BASE_URL", ""),
        "api_key":  os.environ.get("OPENAI_API_KEY", ""),
        "vision":   False,
    },
    "qwen_vl": {
        "model":    "Qwen/Qwen3-VL-30B-A3B-Instruct",
        "base_url": os.environ.get("QWEN_BASE_URL", ""),
        "api_key":  os.environ.get("QWEN_API_KEY", ""),
        "vision":   True,
    },
    "uitars": {
        "model":    "/scratch/eecs545w26_class_root/eecs545w26_class/akinniyi/models/UI-TARS-7B-DPO",
        "base_url": os.environ.get("UITARS_BASE_URL", "http://localhost:8001/v1"),
        "api_key":  os.environ.get("UITARS_API_KEY", "local"),
        "vision":   True,
    },
    "qwen25": {
        "model":    "/scratch/eecs545w26_class_root/eecs545w26_class/akinniyi/models/Qwen2.5-VL-7B-Instruct",
        "base_url": os.environ.get("QWEN25_BASE_URL", "http://localhost:8002/v1"),
        "api_key":  os.environ.get("QWEN25_API_KEY", "local"),
        "vision":   True,
    },
    "internvl": {
        "model":    "/scratch/eecs545w26_class_root/eecs545w26_class/akinniyi/models/InternVL2-8B",
        "base_url": os.environ.get("INTERNVL_BASE_URL", "http://localhost:8003/v1"),
        "api_key":  os.environ.get("INTERNVL_API_KEY", "local"),
        "vision":   True,
    }
}

agent_config = AGENT_CONFIGS[args.agent]
MODEL        = agent_config["model"]
AGENT_VISION = agent_config["vision"]

# validate mode vs agent
if args.mode != "text_only" and not AGENT_VISION:
    print(f"WARNING: agent {args.agent} does not support vision.")
    print(f"Only text_only mode is supported for this agent.")
    if args.mode != "text_only":
        print("Switching to text_only mode.")
        args.mode = "text_only"

client = OpenAI(
    base_url=agent_config["base_url"],
    api_key=agent_config["api_key"]
)

TEMPERATURE = 0.0
MAX_TOKENS  = 500
PAUSE       = 1.5

# ============================================================
# WEBSITE CONFIGURATIONS
# ============================================================
CONFIGS = {
    "house_renting": {
        "task_file":  Path("house-renting-eval/tasks.json"),
        "output_dir": Path(f"results/raw_outputs/house_renting/{args.mode}/{args.agent}"),
        "system_prompt_text": """You are a web agent evaluating rental property listings.
You are given the text content of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- Be precise: return exact values like '$1,450/month' not 'fourteen fifty'
- If information is not visible, say 'Not visible'
""",
        "system_prompt_vision": """You are a web agent evaluating rental property listings.
You are given a screenshot of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- Be precise: return exact values like '$1,450/month'
- If information requires clicking or expanding something, say what you would do
- If information is not visible in the screenshot, say 'Not visible'
"""
    },
    "personal_website": {
        "task_file":  Path("Personal Website/tasks/test.raw.json"),
        "output_dir": Path(f"results/raw_outputs/personal_website/{args.mode}/{args.agent}"),
        "system_prompt_text": """You are a web agent evaluating academic personal websites.
You are given the text content of a single web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- You can only see the text of the current page
- If the information is not on this page, say 'Not found'
- Be precise with names, titles, and dates
""",
        "system_prompt_vision": """You are a web agent evaluating academic personal websites.
You are given a screenshot of a web page and a task.
Find the specific information requested and return it concisely.

Rules:
- Return ONLY the answer, no explanation
- Look carefully at all text visible in the screenshot
- If information is not visible, say 'Not found'
- Be precise with names, titles, and dates
"""
    },
    "job_application": {
        "task_file":  Path("job_application/tasks.json"),
        "output_dir": Path(f"results/raw_outputs/job_application/{args.mode}/{args.agent}"),
        "system_prompt_text": """You are a web agent evaluating job application websites.
Find the specific information requested and return it concisely.
Return ONLY the answer, no explanation.
""",
        "system_prompt_vision": """You are a web agent evaluating job application websites.
You are given a screenshot of the page.
Find the specific information requested and return it concisely.
Return ONLY the answer, no explanation.
"""
    },
    "course_registration": {
        "task_file":  Path("course_registration/tasks.json"),
        "output_dir": Path(f"results/raw_outputs/course_registration/{args.mode}/{args.agent}"),
        "system_prompt_text": """You are a web agent evaluating a course registration system.
Find the specific information requested and return it concisely.
Return ONLY the answer, no explanation.
""",
        "system_prompt_vision": """You are a web agent evaluating a course registration system.
You are given a screenshot of the page.
Find the specific information requested and return it concisely.
Return ONLY the answer, no explanation.
"""
    }
}

config        = CONFIGS[args.website]
TASK_FILE     = config["task_file"]
OUTPUT_DIR    = config["output_dir"]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = (
    config["system_prompt_text"]
    if args.mode == "text_only"
    else config["system_prompt_vision"]
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
# FUNCTION 2: Capture screenshot
# ============================================================
def get_screenshot_b64(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            screenshot_bytes = page.screenshot(full_page=False)
        except Exception as e:
            print(f"\n  screenshot error: {type(e).__name__}: {e}", end=" ")
            screenshot_bytes = None
        finally:
            browser.close()
    if screenshot_bytes:
        return base64.b64encode(screenshot_bytes).decode()
    return None


# ============================================================
# FUNCTION 3: Build prompt content
# ============================================================
def build_content(page_text, screenshot_b64,
                  instruction, interaction="none"):

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

    if args.mode == "text_only":
        text = page_text or ""
        if len(text) > 6000:
            text = text[:6000] + "\n...[truncated]"
        return f"Page content:\n{text}\n{hint}\n\nTask: {instruction}\n\nAnswer:"

    elif args.mode == "vision_only":
        if not screenshot_b64:
            return None
        return [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}
            },
            {
                "type": "text",
                "text": f"{hint}\n\nTask: {instruction}\n\nAnswer:"
            }
        ]

    else:  # multimodal
        text = page_text or ""
        if len(text) > 5000:
            text = text[:5000] + "\n...[truncated]"
        content = []
        if screenshot_b64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}
            })
        content.append({
            "type": "text",
            "text": f"Page text:\n{text}\n{hint}\n\nTask: {instruction}\n\nAnswer:"
        })
        return content


# ============================================================
# FUNCTION 4: Run one task
# ============================================================
def run_task(task):
    task_id     = str(task["task_id"])
    url         = task.get("start_url", "")
    instruction = task.get("instruction") or task.get("intent", "")
    interaction = task.get("interaction", "none")

    output_path = OUTPUT_DIR / f"{task_id}.json"
    if output_path.exists():
        return None, "skipped"

    page_text      = None
    screenshot_b64 = None

    if args.mode in ["text_only", "multimodal"]:
        try:
            page_text = get_page_text(url)
        except Exception as e:
            page_text = f"ERROR: {e}"

    if args.mode in ["multimodal", "vision_only"]:
        try:
            screenshot_b64 = get_screenshot_b64(url)
        except Exception as e:
            screenshot_b64 = None

    content = build_content(page_text, screenshot_b64, instruction, interaction)

    if content is None:
        result = {
            "task_id":           task_id,
            "website":           args.website,
            "template":          task.get("template", ""),
            "instruction":       instruction,
            "interaction":       interaction,
            "perturbation_type": task.get("perturbation_type", ""),
            "start_url":         url,
            "raw_output":        None,
            "error":             "screenshot capture failed",
            "model":             MODEL,
            "agent":             args.agent,
            "mode":              args.mode
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result, "error"

    if isinstance(content, str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": content}
        ]
    else:
        content_with_system = [{"type": "text", "text": SYSTEM_PROMPT}] + content
        messages = [{"role": "user", "content": content_with_system}]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        raw_output = response.choices[0].message.content.strip()
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
        "agent":             args.agent,
        "mode":              args.mode
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result, "done"


# ============================================================
# MAIN
# ============================================================
print(f"Website:  {args.website}")
print(f"Mode:     {args.mode}")
print(f"Agent:    {args.agent}")
print(f"Model:    {MODEL}")
print(f"Tasks:    {TASK_FILE}")
print(f"Output:   {OUTPUT_DIR}")
if args.test:
    print(f"          TEST MODE (first 3 tasks only)")
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
    elif status == "error" or (result and result.get("error")):
        err = result["error"][:60] if result and result.get("error") else "unknown"
        print(f"ERROR: {err}")
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