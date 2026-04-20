#!/usr/bin/env python3
"""
run_eval.py
===========
Evaluation runner for the HomeNest Rentals WebArena-compatible testbed.

Usage
-----
# Dry run (no agent called, just validates setup)
python run_eval.py --dry-run

# Run all tasks with GPT-4V
python run_eval.py --agent gpt4v

# Run only classic template tasks
python run_eval.py --agent gpt4v --template classic

# Run a single task
python run_eval.py --agent gpt4v --task-id C_01_T01

# Run and save results to a custom file
python run_eval.py --agent gpt4v --output results_gpt4v.json

Dependencies
------------
pip install openai playwright Pillow
playwright install chromium
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime


# ── Browser automation ─────────────────────────────────────────────────────────
def take_screenshot(url, interaction_type, instruction="", screenshot_path="screenshot.png"):
    """
    Open a headless browser, navigate to url, perform any required
    interactions based on interaction_type, then take a screenshot.

    interaction_type values and what they do:
      none                         : just load the page and screenshot
      click_show_details_button    : click all expandable + sections (modern)
      click_details_tab            : click the Details tab (hidden)
      click_contact_tab            : click the Contact tab (hidden)
      click_apply_tab              : click the Apply tab (hidden)
      click_details_tab_then_toggle: click Details tab then expand Pet Policy toggle
      click_details_tab_then_fees_toggle: click Details tab then expand Fees toggle
      use_sidebar_city_filter      : select city from sidebar dropdown (hidden index)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page(viewport={"width": 1280, "height": 900})

        # Navigate and wait for JS to finish rendering
        page.goto(url, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1000)

        # ── Perform interactions ──────────────────────────────────────────────
        if interaction_type == "none":
            pass

        elif interaction_type == "click_show_details_button":
            # Modern detail page: click all expandable section headers to reveal
            # property details and contact info
            headers = page.query_selector_all(".section-header")
            for header in headers:
                try:
                    header.click()
                    page.wait_for_timeout(400)
                except Exception:
                    pass

        elif interaction_type == "click_details_tab":
            # Hidden detail page: click the Details tab
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
            except Exception:
                pass

        elif interaction_type == "click_contact_tab":
            # Hidden detail page: click the Contact tab
            try:
                page.click("button:has-text('Contact')")
                page.wait_for_timeout(400)
            except Exception:
                pass

        elif interaction_type == "click_apply_tab":
            # Hidden detail page: click the Apply tab
            try:
                page.click("button:has-text('Apply')")
                page.wait_for_timeout(400)
            except Exception:
                pass

        elif interaction_type == "click_details_tab_then_toggle":
            # Hidden detail page: click Details tab then expand the Pet Policy toggle
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
                toggle_headers = page.query_selector_all(".toggle-hdr")
                for toggle in toggle_headers:
                    if "Pet" in toggle.inner_text():
                        toggle.click()
                        page.wait_for_timeout(400)
                        break
            except Exception:
                pass

        elif interaction_type == "click_details_tab_then_fees_toggle":
            # Hidden detail page: click Details tab then expand the Fees & Deadlines toggle
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
                toggle_headers = page.query_selector_all(".toggle-hdr")
                for toggle in toggle_headers:
                    if "Fee" in toggle.inner_text():
                        toggle.click()
                        page.wait_for_timeout(400)
                        break
            except Exception:
                pass

        elif interaction_type == "use_sidebar_city_filter":
            # Hidden index page: extract city name from instruction and select
            # it in the city dropdown filter
            # Instruction format: "Use the city filter to find listings in {city}..."
            city_match = re.search(r"listings in ([A-Za-z\s]+?) and", instruction)
            if city_match:
                city = city_match.group(1).strip()
                try:
                    page.select_option("#f-city", city)
                    page.wait_for_timeout(600)
                except Exception:
                    pass

        # Take screenshot
        page.screenshot(path=screenshot_path, full_page=False)
        browser.close()

    return screenshot_path


def image_to_base64(path):
    """Read an image file and return base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_page_text(url, interaction_type, instruction=""):
    """
    Open a headless browser, navigate to url, perform any required
    interactions, then extract and return the visible text of the page.
    Used for text-only models that do not support image inputs.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1000)

        if interaction_type == "none":
            pass
        elif interaction_type == "click_show_details_button":
            for header in page.query_selector_all(".section-header"):
                try:
                    header.click()
                    page.wait_for_timeout(400)
                except Exception:
                    pass
        elif interaction_type == "click_details_tab":
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
            except Exception:
                pass
        elif interaction_type == "click_contact_tab":
            try:
                page.click("button:has-text('Contact')")
                page.wait_for_timeout(400)
            except Exception:
                pass
        elif interaction_type == "click_apply_tab":
            try:
                page.click("button:has-text('Apply')")
                page.wait_for_timeout(400)
            except Exception:
                pass
        elif interaction_type == "click_details_tab_then_toggle":
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
                for toggle in page.query_selector_all(".toggle-hdr"):
                    if "Pet" in toggle.inner_text():
                        toggle.click()
                        page.wait_for_timeout(400)
                        break
            except Exception:
                pass
        elif interaction_type == "click_details_tab_then_fees_toggle":
            try:
                page.click("button:has-text('Details')")
                page.wait_for_timeout(400)
                for toggle in page.query_selector_all(".toggle-hdr"):
                    if "Fee" in toggle.inner_text():
                        toggle.click()
                        page.wait_for_timeout(400)
                        break
            except Exception:
                pass
        elif interaction_type == "use_sidebar_city_filter":
            city_match = re.search(r"listings in ([A-Za-z ]+?) and", instruction)
            if city_match:
                try:
                    page.select_option("#f-city", city_match.group(1).strip())
                    page.wait_for_timeout(600)
                except Exception:
                    pass

        text = page.inner_text("body")
        browser.close()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT CONFIGURATION
# This is the ONLY section you need to edit to add or configure agents.
# For each agent, set:
#   base_url : the OpenAI-compatible server URL
#   api_key  : your API key for that server
#   model    : the model identifier string
#
# To activate a placeholder agent, just fill in its base_url, api_key, and model.
# All three modes (text, vision, multi) will work automatically.
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_CONFIGS = {
    "gpt4v": {
        "base_url" : "http://promaxgb10-d473.eecs.umich.edu:8000/v1",
        "api_key"  : "api_IcLlffdxoWOSgBPWW3X3zS15YSBHim5a",        # ← replace with your actual key
        "model"    : "openai/gpt-oss-120b",
    },
    "qwen3_vl_30b": {
        "base_url" : "http://your-server/v1", # ← update when available
        "api_key"  : "your_key_here",
        "model"    : "Qwen/Qwen3-VL-30B-Instruct",
    },
    "uitars_7b": {
        "base_url" : "http://your-server/v1",
        "api_key"  : "your_key_here",
        "model"    : "bytedance-research/UI-TARS-7B",
    },
    "cogagent_9b": {
        "base_url" : "http://your-server/v1",
        "api_key"  : "your_key_here",
        "model"    : "THUDM/cogagent-9b",
    },
    "qwen2_vl_7b": {
        "base_url" : "http://your-server/v1",
        "api_key"  : "your_key_here",
        "model"    : "Qwen/Qwen2-VL-7B-Instruct",
    },
    "gemini": {
        "base_url" : "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key"  : "your_key_here",        # ← GOOGLE_API_KEY
        "model"    : "gemini-2.1-pro",
    },
    # ── Add new agents below ──────────────────────────────────────────────────
    # "my_agent": {
    #     "base_url" : "http://your-server/v1",
    #     "api_key"  : "your_key_here",
    #     "model"    : "my-org/my-model",
    # },
}

# ── Generic model call (works for ALL agents and ALL three modes) ──────────────
def call_model(url, instruction, interaction_type="none", mode="text", config=None):
    """
    Generic VLM call that works for any OpenAI-compatible server.

    All agents share this function. The only difference between agents
    is the config dict passed in (base_url, api_key, model).

    mode options:
      text   : extract page text, send as plain text (works for text-only models)
      vision : take screenshot, send as image (requires vision-capable model)
      multi  : send both screenshot and page text (most capable, requires vision)
    """
    if config is None:
        raise ValueError("config must be provided. Check AGENT_CONFIGS.")

    base_url = config["base_url"]
    api_key  = config["api_key"]
    model    = config["model"]

    if "your_key_here" in api_key or "your-server" in base_url:
        raise NotImplementedError(
            "Agent not configured yet. "
            "Update base_url and api_key in AGENT_CONFIGS at the top of this file."
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    client = OpenAI(base_url=base_url, api_key=api_key)

    # ── Mode: text-only ───────────────────────────────────────────────────────
    if mode == "text":
        page_text = extract_page_text(url, interaction_type, instruction=instruction)
        system_prompt = (
            "You are a precise information extraction agent. "
            "You will be given the raw text content of a house rental website page "
            "and a specific question. "
            "Find the exact answer in the text and return ONLY that value. "
            "Do not include any explanation or extra words. "
            "Return the value exactly as it appears on the page. "
            "If the answer is not in the text, return: NOT FOUND"
        )
        user_prompt = (
            "Here is the text content of a house rental website page:\n\n"
            + page_text
            + "\n\n---\n\n"
            "Question: " + instruction + "\n\n"
            "Return only the exact value as it appears on the page, nothing else."
        )
        response = client.chat.completions.create(
            model=model, max_tokens=100,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    # ── Mode: vision-only ─────────────────────────────────────────────────────
    elif mode == "vision":
        screenshot_path = "screenshot_eval.png"
        take_screenshot(url, interaction_type, instruction=instruction, screenshot_path=screenshot_path)
        image_b64 = image_to_base64(screenshot_path)
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        system_prompt = (
            "You are a precise information extraction agent. "
            "You will be shown a screenshot of a house rental website and given a question. "
            "Find the exact answer visible on the page and return ONLY that value. "
            "Do not include any explanation or extra words. "
            "Return the value exactly as it appears on the page. "
            "If the answer is not visible, return: NOT FOUND"
        )
        user_prompt = (
            "Look at this screenshot of a house rental website.\n\n"
            "Question: " + instruction + "\n\n"
            "Return only the exact value as it appears on the page, nothing else."
        )
        response = client.chat.completions.create(
            model=model, max_tokens=100,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64," + image_b64,
                                "detail": "high"
                            }
                        },
                        {"type": "text", "text": user_prompt}
                    ]
                }
            ]
        )
        return response.choices[0].message.content.strip()

    # ── Mode: multimodal (text + vision) ──────────────────────────────────────
    elif mode == "multi":
        page_text = extract_page_text(url, interaction_type, instruction=instruction)
        screenshot_path = "screenshot_eval.png"
        take_screenshot(url, interaction_type, instruction=instruction, screenshot_path=screenshot_path)
        image_b64 = image_to_base64(screenshot_path)
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        system_prompt = (
            "You are a precise information extraction agent. "
            "You will be shown both a screenshot and the text content of a house rental website. "
            "Use both to find the exact answer and return ONLY that value. "
            "Do not include any explanation or extra words. "
            "Return the value exactly as it appears on the page. "
            "If the answer is not found, return: NOT FOUND"
        )
        user_prompt = (
            "Here is the text content of the page:\n\n"
            + page_text
            + "\n\n---\n\n"
            "Question: " + instruction + "\n\n"
            "The screenshot is also attached. "
            "Return only the exact value as it appears on the page, nothing else."
        )
        response = client.chat.completions.create(
            model=model, max_tokens=100,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64," + image_b64,
                                "detail": "high"
                            }
                        },
                        {"type": "text", "text": user_prompt}
                    ]
                }
            ]
        )
        return response.choices[0].message.content.strip()

    else:
        raise ValueError("Invalid mode: " + mode + ". Choose from: text, vision, multi")


# ── Agent Registry ─────────────────────────────────────────────────────────────
# Do NOT edit this section to configure agents.
# Edit AGENT_CONFIGS above instead.

AGENTS = {
    "gpt4v": {
        "name"     : "GPT-OSS-120B (UMich)",
        "model_id" : AGENT_CONFIGS["gpt4v"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["gpt4v"]),
        "notes"    : "UMich class server. Set api_key in AGENT_CONFIGS above."
    },
    "qwen3_vl_30b": {
        "name"     : "Qwen3-VL-30B-Instruct",
        "model_id" : AGENT_CONFIGS["qwen3_vl_30b"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["qwen3_vl_30b"]),
        "notes"    : "Large Qwen3 VL model. Set base_url and api_key in AGENT_CONFIGS above."
    },
    "uitars_7b": {
        "name"     : "UI-TARS-7B",
        "model_id" : AGENT_CONFIGS["uitars_7b"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["uitars_7b"]),
        "notes"    : "UI-TARS from ByteDance. Set base_url and api_key in AGENT_CONFIGS above."
    },
    "cogagent_9b": {
        "name"     : "CogAgent-9B",
        "model_id" : AGENT_CONFIGS["cogagent_9b"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["cogagent_9b"]),
        "notes"    : "CogAgent from Tsinghua. Set base_url and api_key in AGENT_CONFIGS above."
    },
    "qwen2_vl_7b": {
        "name"     : "Qwen2-VL-7B",
        "model_id" : AGENT_CONFIGS["qwen2_vl_7b"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["qwen2_vl_7b"]),
        "notes"    : "Qwen2-VL 7B. Set base_url and api_key in AGENT_CONFIGS above."
    },
    "gemini": {
        "name"     : "Gemini-2.1-Pro",
        "model_id" : AGENT_CONFIGS["gemini"]["model"],
        "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["gemini"]),
        "notes"    : "Gemini 2.1 Pro. Set api_key (GOOGLE_API_KEY) in AGENT_CONFIGS above."
    },
    # ── Add new agents below ──────────────────────────────────────────────────
    # Step 1: Add config to AGENT_CONFIGS above
    # Step 2: Add entry here following the same pattern
    # "my_agent": {
    #     "name"     : "My Agent",
    #     "model_id" : AGENT_CONFIGS["my_agent"]["model"],
    #     "call"     : lambda url, instr, interaction, mode="text": call_model(url, instr, interaction, mode, AGENT_CONFIGS["my_agent"]),
    #     "notes"    : "My agent description."
    # },
}


# ── Evaluation helpers ─────────────────────────────────────────────────────────
def evaluate(prediction, ground_truth):
    """String match evaluation. Returns True if prediction matches ground truth."""
    return prediction.strip().lower() == ground_truth.strip().lower()

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print("Results saved to: " + path)


# ── Dry run ────────────────────────────────────────────────────────────────────
def dry_run(tasks, envs, template_filter=None, task_id_filter=None):
    """
    Validates setup without calling any agent.
    Checks that every task has a matching env_id in envs.json.
    Prints a summary of what would be run.
    """
    print("=" * 60)
    print("DRY RUN MODE - No agent will be called")
    print("=" * 60)

    env_ids  = {e["env_id"] for e in envs}
    filtered = [t for t in tasks if
        (template_filter is None or t["template"] == template_filter) and
        (task_id_filter  is None or t["task_id"]  == task_id_filter)
    ]

    errors = []
    for t in filtered:
        if t["env_id"] not in env_ids:
            errors.append(
                "MISSING ENV: task " + t["task_id"] +
                " references env_id '" + t["env_id"] +
                "' which does not exist in envs.json"
            )

    print("")
    print("Tasks to run  : " + str(len(filtered)))
    print("Templates     : " + str(sorted(set(t["template"] for t in filtered))))
    print("")

    for tmpl in ["classic", "modern", "hidden"]:
        count = len([t for t in filtered if t["template"] == tmpl])
        if count:
            print("  " + tmpl.capitalize() + " tasks : " + str(count))

    print("")

    if errors:
        print("ERRORS FOUND (" + str(len(errors)) + "):")
        for e in errors:
            print("  [ERROR] " + e)
    else:
        print("Validation passed. No errors found.")

    print("")
    print("Sample tasks (first 5):")
    for t in filtered[:5]:
        print("  [" + t["task_id"] + "] " + t["instruction"])
        print("    URL         : " + t["start_url"])
        print("    Expected    : " + t["evaluation"]["target"])
        print("    Interaction : " + t["interaction"])
        print("")

    print("Dry run complete. Run without --dry-run to execute evaluation.")
    return len(errors) == 0


# ── Main evaluation loop ───────────────────────────────────────────────────────
def run_evaluation(agent_key, tasks, envs, template_filter=None, task_id_filter=None, output_path="results.json", mode="text"):
    if agent_key not in AGENTS:
        print("Unknown agent: " + agent_key)
        print("Available agents: " + str(list(AGENTS.keys())))
        sys.exit(1)

    agent = AGENTS[agent_key]
    print("=" * 60)
    print("HomeNest Rentals Evaluation Runner")
    print("=" * 60)
    print("Agent    : " + agent["name"])
    print("Model ID : " + agent["model_id"])
    print("Mode     : " + mode)
    print("Started  : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    filtered = [t for t in tasks if
        (template_filter is None or t["template"] == template_filter) and
        (task_id_filter  is None or t["task_id"]  == task_id_filter)
    ]

    print("Running " + str(len(filtered)) + " tasks...")
    print("")

    results = []
    passed  = 0
    failed  = 0
    errors  = 0

    for i, task in enumerate(filtered):
        print("[" + str(i+1) + "/" + str(len(filtered)) + "] " + task["task_id"])
        try:
            start      = time.time()
            # Pass url, instruction, AND interaction type to agent
            prediction = agent["call"](
                task["start_url"],
                task["instruction"],
                task["interaction"],
                mode
            )
            elapsed = round(time.time() - start, 2)
            success = evaluate(prediction, task["evaluation"]["target"])
            status  = "PASS" if success else "FAIL"
            if success: passed += 1
            else:       failed += 1
            print("  Status      : " + status)
            print("  Predicted   : " + prediction)
            print("  Expected    : " + task["evaluation"]["target"])
            print("  Interaction : " + task["interaction"])
            print("  Time        : " + str(elapsed) + "s")
            results.append({
                "task_id"    : task["task_id"],
                "template"   : task["template"],
                "agent"      : agent["name"],
                "mode"       : mode,
                "instruction": task["instruction"],
                "start_url"  : task["start_url"],
                "interaction": task["interaction"],
                "expected"   : task["evaluation"]["target"],
                "predicted"  : prediction,
                "status"     : status,
                "elapsed_s"  : elapsed
            })
        except NotImplementedError as e:
            print("  [SKIP] " + str(e))
            errors += 1
            results.append({
                "task_id"    : task["task_id"],
                "template"   : task["template"],
                "agent"      : agent["name"],
                "mode"       : mode,
                "instruction": task["instruction"],
                "start_url"  : task["start_url"],
                "interaction": task["interaction"],
                "expected"   : task["evaluation"]["target"],
                "predicted"  : None,
                "status"     : "SKIP",
                "elapsed_s"  : 0
            })
        except Exception as e:
            print("  [ERROR] " + str(e))
            errors += 1
            results.append({
                "task_id"    : task["task_id"],
                "template"   : task["template"],
                "agent"      : agent["name"],
                "mode"       : mode,
                "instruction": task["instruction"],
                "start_url"  : task["start_url"],
                "interaction": task["interaction"],
                "expected"   : task["evaluation"]["target"],
                "predicted"  : None,
                "status"     : "ERROR",
                "elapsed_s"  : 0
            })
        print("")

    # ── Summary ───────────────────────────────────────────────────────────────
    total      = len(filtered)
    completed  = passed + failed
    sr_overall = round(passed / completed, 4) if completed > 0 else 0

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Total tasks : " + str(total))
    print("Passed      : " + str(passed))
    print("Failed      : " + str(failed))
    print("Skipped/Err : " + str(errors))
    print("Overall SR  : " + str(round(sr_overall * 100, 1)) + "%")
    print("")

    # SR per template
    sr_by_template = {}
    for tmpl in ["classic", "modern", "hidden"]:
        tmpl_results = [r for r in results if r["template"] == tmpl and r["status"] in ("PASS","FAIL")]
        tmpl_passed  = len([r for r in tmpl_results if r["status"] == "PASS"])
        tmpl_total   = len(tmpl_results)
        sr = round(tmpl_passed / tmpl_total, 4) if tmpl_total > 0 else 0
        sr_by_template[tmpl] = sr
        print(tmpl.capitalize() + " SR : " + str(round(sr * 100, 1)) + "% (" + str(tmpl_passed) + "/" + str(tmpl_total) + ")")

    print("")
    print("Robustness Drop (Delta):")
    delta_cm = round((sr_by_template.get("classic",0) - sr_by_template.get("modern",0)) * 100, 1)
    delta_mh = round((sr_by_template.get("modern",0)  - sr_by_template.get("hidden",0))  * 100, 1)
    delta_ch = round((sr_by_template.get("classic",0) - sr_by_template.get("hidden",0))  * 100, 1)
    print("  Classic vs Modern : " + str(delta_cm) + "%")
    print("  Modern  vs Hidden : " + str(delta_mh) + "%")
    print("  Classic vs Hidden : " + str(delta_ch) + "% (overall robustness drop)")
    print("")

    # SR per task type
    print("SR per task type:")
    for t_num in range(1, 11):
        t_key     = "T" + str(t_num).zfill(2)
        t_results = [r for r in results if t_key in r["task_id"] and r["status"] in ("PASS","FAIL")]
        t_passed  = len([r for r in t_results if r["status"] == "PASS"])
        t_total   = len(t_results)
        sr = round(t_passed / t_total * 100, 1) if t_total > 0 else 0
        print("  " + t_key + " : " + str(sr) + "% (" + str(t_passed) + "/" + str(t_total) + ")")

    print("")

    # SR per house
    print("SR per house:")
    for hid in [str(i).zfill(2) for i in range(1, 13)]:
        h_results = [r for r in results if ("_" + hid + "_") in r["task_id"] and r["status"] in ("PASS","FAIL")]
        h_passed  = len([r for r in h_results if r["status"] == "PASS"])
        h_total   = len(h_results)
        sr = round(h_passed / h_total * 100, 1) if h_total > 0 else 0
        print("  House " + hid + " : " + str(sr) + "% (" + str(h_passed) + "/" + str(h_total) + ")")

    print("")
    print("=" * 60)

    # ── Save results ──────────────────────────────────────────────────────────
    output = {
        "meta": {
            "agent"          : agent["name"],
            "model_id"       : agent["model_id"],
            "mode"           : mode,
            "timestamp"      : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tasks"    : total,
            "passed"         : passed,
            "failed"         : failed,
            "skipped"        : errors,
            "sr_overall"     : sr_overall,
            "sr_by_template" : sr_by_template,
            "robustness_drop": {
                "classic_vs_modern" : delta_cm,
                "modern_vs_hidden"  : delta_mh,
                "classic_vs_hidden" : delta_ch
            }
        },
        "results": results
    }
    save_json(output, output_path)
    return output


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="HomeNest Rentals WebArena Evaluation Runner")
    parser.add_argument("--agent",       type=str, help="Agent key. Options: " + str(list(AGENTS.keys())))
    parser.add_argument("--template",    type=str, help="Filter by template: classic, modern, or hidden")
    parser.add_argument("--task-id",     type=str, help="Run a single task by ID e.g. C_01_T01")
    parser.add_argument("--output",      type=str, default=None, help="Output file. Default: results_{agent}_{template}_{mode}.json")
    parser.add_argument("--tasks",       type=str, default="tasks.json",   help="Path to tasks.json")
    parser.add_argument("--envs",        type=str, default="envs.json",    help="Path to envs.json")
    parser.add_argument("--mode",        type=str, default="text", choices=["text","vision","multi"], help="Input mode: text (default), vision, or multi")
    parser.add_argument("--dry-run",     action="store_true", help="Validate setup without calling any agent")
    parser.add_argument("--list-agents", action="store_true", help="List all available agents and exit")
    args = parser.parse_args()

    if args.list_agents:
        print("Available agents:")
        for key, ag in AGENTS.items():
            print("  " + key + " -> " + ag["name"] + " (" + ag["model_id"] + ")")
            print("    " + ag["notes"])
        sys.exit(0)

    if not os.path.exists(args.tasks):
        print("tasks.json not found at: " + args.tasks)
        sys.exit(1)
    if not os.path.exists(args.envs):
        print("envs.json not found at: " + args.envs)
        sys.exit(1)

    tasks = load_json(args.tasks)
    envs  = load_json(args.envs)

    if args.dry_run:
        ok = dry_run(tasks, envs, template_filter=args.template, task_id_filter=args.task_id)
        sys.exit(0 if ok else 1)

    if not args.agent:
        print("Please specify an agent with --agent. Use --list-agents to see options.")
        sys.exit(1)

    # Auto-generate output filename if not specified
    # Format: results_{agent}_{template}_{mode}.json
    if args.output:
        output_path = args.output
    else:
        tmpl_label  = args.template if args.template else "all"
        output_path = "results_" + args.agent + "_" + tmpl_label + "_" + args.mode + ".json"

    run_evaluation(
        agent_key       = args.agent,
        tasks           = tasks,
        envs            = envs,
        template_filter = args.template,
        task_id_filter  = args.task_id,
        output_path     = output_path,
        mode            = args.mode
    )

if __name__ == "__main__":
    main()
