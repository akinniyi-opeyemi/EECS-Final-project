# Synthetic House Renting Website Templates (WebArena Compatible)

## Overview

This project provides a **WebArena-compatible testbed** for evaluating the robustness of visual language model (VLM) GUI agents under UI and workflow changes. Three versions of the same house rental website are built, each with a different visual style and interaction complexity. An agent is given identical tasks across all three templates. Performance gaps between templates measure UI robustness.

**Research question:** How does a VLM agent's ability to find information degrade as the UI becomes more complex and content becomes progressively hidden?

---

## Templates

| Template | Landing Page Style | Detail Page Style | Change Type |
| -------- | ------------------ | ----------------- | ----------- |
| `classic/` | Paginated grid, 4 per page | Flat tables, all fields visible | Baseline |
| `modern/` | Card-based grid with hero banner | Expandable sections, click to reveal | Layout + interaction shift |
| `hidden/` | Sidebar filter + vertical list | 4 tabs + collapsible toggles | Workflow + visibility shift |

All three templates display the **exact same 12 house listings** with identical data. Only the layout, visual style, and interaction model differ.

---

## Task Complexity Model

Tasks are structured as subsets, with each template inheriting previous tasks and adding new interaction-specific ones:

```
Classic tasks (T01-T05)
  subset of Modern tasks (T01-T07, adds button interaction)
    subset of Hidden tasks (T01-T10, adds filter + tab + toggle interaction)
```

This means the same base tasks run on all three templates, and harder interaction tasks are added progressively. A robustness drop on inherited tasks signals pure UI sensitivity, while failures on new tasks measure interaction cost.

---

## Repository Layout

```
house-renting-eval/
├── dashboard.html                 # Interactive results dashboard (standalone HTML)
├── run_eval.py                    # Evaluation runner with agent registry and dry run
├── tasks.json                     # 264 task definitions across all three templates
├── envs.json                      # 45 environment configs (15 per template)
├── README.md                      # This file
│
├── assets/
│   ├── house_01.jpg
│   ├── house_02.jpg
│   └── ... house_12.jpg          # Shared images used by all three templates
│
└── templates/
    ├── classic/                   # Template 1: flat, everything visible
    │   ├── index.html             # Landing page: 4-per-page paginated grid
    │   ├── about.html
    │   ├── contact.html
    │   ├── house_01.html
    │   └── ... house_12.html
    │
    ├── modern/                    # Template 2: card-based, content behind buttons
    │   ├── index.html             # Landing page: card grid with hero banner
    │   ├── about.html
    │   ├── contact.html
    │   ├── house_01.html
    │   └── ... house_12.html
    │
    └── hidden/                    # Template 3: sidebar filters, tabs, toggles
        ├── index.html             # Landing page: sidebar filter + vertical list
        ├── about.html
        ├── contact.html
        ├── house_01.html
        └── ... house_12.html
```

---

## House Listings

All 12 listings are fictional but realistic, with unique data across all fields. 8 are currently available and 4 are marked not available.

| House | City | Rent | Beds | Status |
| ----- | ---- | ---- | ---- | ------ |
| 01 Maplewood Apartments | Austin, TX | $1,450/mo | 2 | Available |
| 02 Sunset Ridge Home | Denver, CO | $2,200/mo | 3 | Available |
| 03 Lakeside Condo | Chicago, IL | $1,800/mo | 1 | Not Available |
| 04 The Elmwood | Boston, MA | $2,600/mo | 2 | Available |
| 05 Riverfront Studio | Portland, OR | $1,100/mo | Studio | Available |
| 06 Oak Hill House | Nashville, TN | $1,750/mo | 3 | Not Available |
| 07 Parkview Terrace | Seattle, WA | $2,400/mo | 2 | Available |
| 08 Cedar Grove Flat | Atlanta, GA | $1,350/mo | 1 | Available |
| 09 Hillcrest Manor | San Diego, CA | $3,100/mo | 4 | Not Available |
| 10 Pinewood Cottage | Raleigh, NC | $1,550/mo | 2 | Available |
| 11 Downtown Loft | Miami, FL | $2,050/mo | 1 | Not Available |
| 12 Birchwood Place | Minneapolis, MN | $1,650/mo | 2 | Available |

---

## Task Definitions (tasks.json)

264 tasks total across three templates. Each task targets a specific field on a specific house listing.

| Template | Task IDs | Tasks per house | Total | Required interaction |
| -------- | -------- | --------------- | ----- | -------------------- |
| Classic | T01-T05 | 5 | 60 | None, all fields visible |
| Modern | T01-T07 | 7 | 84 | Click expandable section for T06-T07 |
| Hidden | T01-T10 | 10 | 120 | Sidebar filter (T08), tab navigation (T09), toggle expand (T10) |

### Task field mapping

| Task | Field | Templates |
| ---- | ----- | --------- |
| T01 | Monthly rent | All |
| T02 | Number of bedrooms | All |
| T03 | Application deadline | All |
| T04 | Contact email | All |
| T05 | Availability status | All |
| T06 | Pet policy | Modern, Hidden |
| T07 | Parking details | Modern, Hidden |
| T08 | Find listing via city filter | Hidden only |
| T09 | Lease duration (Details tab) | Hidden only |
| T10 | Application fee (Details tab, Fees toggle) | Hidden only |

### Task ID format

```
C_01_T03   means Classic template, House 01, Task 03
M_07_T06   means Modern template, House 07, Task 06
H_12_T10   means Hidden template, House 12, Task 10
```

---

## Environment Configs (envs.json)

45 environments, 15 per template. Each environment maps to a single HTML page with metadata describing the required interaction type.

| Interaction type | Description |
| ---------------- | ----------- |
| `none` | All content visible, no clicks needed |
| `click_to_reveal` | Content hidden behind expandable sections |
| `sidebar_filter` | Agent must use city, bedroom, availability, or price filters |
| `tabs_and_toggles` | Content split across 4 tabs with nested toggle sections |
| `form_submission` | Contact form with mailto submission |

---

## Supported VLM Agents

The following agents are registered in `run_eval.py`. Each has a placeholder call function that must be replaced with real inference code before running evaluations.

| Key | Agent | Notes |
| --- | ----- | ----- |
| `gpt4v` | GPT-OSS-120B (UMich) | Currently configured for UMich class server |
| `qwen3_vl_30b` | Qwen3-VL-30B-Instruct | Large model, high GPU requirement |
| `uitars_7b` | UI-TARS-7B | UI-focused, strong on interactive elements |
| `cogagent_9b` | CogAgent-9B | Good at DOM navigation |
| `qwen2_vl_7b` | Qwen2-VL-7B | Good speed and accuracy balance |
| `gemini` | Gemini-2.1-Pro | Requires Google API key |

### Configuring agents

All agent credentials are in one place at the top of `run_eval.py` in the `AGENT_CONFIGS` dictionary. To activate any agent, just fill in its `base_url`, `api_key`, and `model`:

```python
AGENT_CONFIGS = {
    "gpt4v": {
        "base_url" : "http://your-server/v1",
        "api_key"  : "your_key_here",   # only thing you need to change
        "model"    : "openai/gpt-oss-120b",
    },
    ...
}
```

To add a brand new agent, add its config to `AGENT_CONFIGS` and copy one entry in the registry section below it. No other changes needed.

---

## 1. Serving the Websites

Serve from the project root so all three templates can access the shared `assets/` folder:

```bash
cd house-renting-eval
python -m http.server 8000
```

Access each template:

```
http://localhost:8000/templates/classic/index.html
http://localhost:8000/templates/modern/index.html
http://localhost:8000/templates/hidden/index.html
```

---

## 2. Running Evaluations

### Dry run (validate setup, no agent called)

```bash
python run_eval.py --dry-run
python run_eval.py --dry-run --template classic
python run_eval.py --dry-run --task-id C_01_T01
```

### List available agents

```bash
python run_eval.py --list-agents
```

### Input modes

Every evaluation run supports three input modes that control what the agent receives as input:

| Mode | What the agent receives | Best for |
| ---- | ----------------------- | -------- |
| `text` | Raw page text extracted from the DOM | Text-only models |
| `vision` | Screenshot of the page | Vision-capable models |
| `multi` | Both screenshot and page text | Multimodal models (most capable) |

The default mode is `text`. Specify a mode with the `--mode` flag.

### Run a full evaluation

```bash
# Text mode (default)
python run_eval.py --agent gpt4v --mode text --output results_gpt4v_text.json

# Vision mode
python run_eval.py --agent gpt4v --mode vision --output results_gpt4v_vision.json

# Multimodal mode
python run_eval.py --agent gpt4v --mode multi --output results_gpt4v_multi.json

# Specific template only
python run_eval.py --agent gpt4v --mode text --template classic
```

### Run a single task

```bash
python run_eval.py --agent gpt4v --mode text --task-id C_01_T01
```

### Output file naming

Output filenames are generated automatically in the format `results_{agent}_{template}_{mode}.json`. You do not need to specify `--output` unless you want a custom name.

```bash
# These commands auto-generate the filenames shown in the comments
python run_eval.py --agent gpt4v --mode text              # results_gpt4v_all_text.json
python run_eval.py --agent gpt4v --mode vision            # results_gpt4v_all_vision.json
python run_eval.py --agent gpt4v --mode multi             # results_gpt4v_all_multi.json
python run_eval.py --agent gpt4v --mode text --template classic   # results_gpt4v_classic_text.json
python run_eval.py --agent qwen2_vl_7b --mode text        # results_qwen2_vl_7b_all_text.json
```

Use `--output` only when you want a custom filename:

```bash
python run_eval.py --agent gpt4v --mode text --output my_custom_name.json
```

---

## 3. Measuring Robustness

### Success Rate

```
SR = successful_tasks / total_tasks
```

### Robustness Drop

```
Delta = SR(classic) - SR(hidden)
```

`run_eval.py` automatically computes and prints after each run:

- Overall SR across all tasks
- SR per template (classic, modern, hidden)
- SR per task type (T01 to T10)
- SR per house (01 to 12)
- Robustness drop for all three template pairs (classic vs modern, modern vs hidden, classic vs hidden)

---

## 4. Evaluation Dashboard

`dashboard.html` is a standalone interactive HTML file. Open it in any browser by double-clicking it or serving it locally.

```bash
python -m http.server 8000
# then open http://localhost:8000/dashboard.html
```

### Dashboard features

- Agent selector chips to show one or all agents, charts update instantly
- Input mode filter chips (Text Only, Vision Only, Multimodal) to compare across modes
- Summary cards showing average SR, best agent, baseline SR, and max robustness drop
- SR by template: grouped horizontal bar chart per agent
- Robustness drop panel: visual gradient bars comparing all agents
- SR by task type: SVG line chart across T01 to T10 with zone shading
- SR by house: color-coded heatmap with agents as rows and houses as columns
- Agent comparison summary table with all SR and delta values

### Loading real results

The dashboard opens with mock data for demonstration. To replace it with real results:

1. Run evaluations with `run_eval.py` and save named output files
2. Open `dashboard.html` in your browser
3. Click "Load results.json" in the top right corner
4. Select one or more results files at once using the file picker
5. All mock data is wiped automatically on first load
6. Only real agent results are shown, with no mock data mixed in

If you only have results for 3 agents, only those 3 agents will appear. There is no mixing of mock and real data once the first file is loaded.

To compare across input modes, load all three mode result files at once:

```bash
# Select all three files in the file picker at the same time
results_gpt4v_all_text.json
results_gpt4v_all_vision.json
results_gpt4v_all_multi.json
```

Then use the mode filter chips on the dashboard to toggle between them.

---

## 5. WebArena Compatibility

### Supported

- Static HTML pages
- DOM-based interaction
- Click, scroll, text extraction
- Button-triggered content (JavaScript works)
- Tab navigation and toggle expansion
- Sidebar filter interaction

### Limitations

- No backend or database
- No real login or authentication flows
- No dynamic network requests or live listings

---

## 6. Critical Constraints

1. **Self-contained output.** Each HTML file must be openable by double-clicking or serving with `python -m http.server`. No external CSS or JS CDN dependencies.

2. **Static files only.** All task-target fields must be present in the initial HTML, not rendered by JavaScript at runtime. All pages are fully readable with JS disabled.

3. **Same data across all templates.** Field values are identical across classic, modern, and hidden. Only layout and interaction differ.

4. **Unavailable fields handled cleanly.** Unavailable houses show N/A for date fields and display a clear notice. No empty rows or broken elements.

5. **Relative image paths.** All house photos reference `../assets/house_XX.jpg`. Always serve from the project root, not from inside a template folder.

6. **No randomness.** Same input always produces the same page. No `datetime.now()` or non-deterministic values anywhere.

---

## 7. Debug Tips

If the agent fails to find a field:

- Classic: the field should be visible immediately in a table row with no interaction needed
- Modern: check whether the field is inside an expandable section that requires a click
- Hidden: check which tab the field lives in and whether it is inside a toggle that must be expanded first

To inspect the DOM:

```
Right click the page in browser, then Inspect, then Elements
```

To check for JavaScript errors:

```
Right click, then Inspect, then Console
```

---

## 8. Extending the Project

### Adding more house listings

Duplicate an existing `house_XX.html` in all three template folders, update the data, add the listing to the JavaScript array in each `index.html`, and add corresponding tasks and environments to `tasks.json` and `envs.json`.

### Adding a new UI template

Create a new folder following the same 15-file structure (index, about, contact, 12 detail pages). Ensure all task-target fields are present in the HTML. Register the new environments in `envs.json` and add corresponding tasks to `tasks.json`.

### Adding a new agent

Open `run_eval.py`, find the agent registry section, and add a new entry following the commented template. Implement the call function with your actual model inference code.

---

## 9. Summary

This project provides a minimal but complete WebArena-compatible testbed for studying:

- **Layout robustness** (flat tables vs. card-based UI vs. filtered list)
- **Interaction robustness** (visible vs. hidden behind clicks, tabs, and toggles)
- **Filter robustness** (finding a listing through a sidebar search vs. browsing directly)
- **Generalisation across UI changes** for identical underlying property data

The progressive task subset model (Classic subset of Modern subset of Hidden) allows precise attribution of performance drops to specific interaction types rather than just overall template difficulty.

---

## Quick Start

```bash
# 1. Install dependencies
pip install openai playwright Pillow
playwright install chromium

# 2. Configure your agent in run_eval.py
# Open run_eval.py and update AGENT_CONFIGS with your api_key and base_url

# 3. Serve the project from the root folder
cd house-renting-eval
python -m http.server 8000

# 4. Validate setup with a dry run (in a second terminal)
python run_eval.py --dry-run

# 5. Test a single task first
python run_eval.py --agent gpt4v --mode text --task-id C_01_T01

# 6. Run full evaluation across all three modes
# Output files are named automatically: results_gpt4v_all_{mode}.json
python run_eval.py --agent gpt4v --mode text
python run_eval.py --agent gpt4v --mode vision
python run_eval.py --agent gpt4v --mode multi

# 7. View results in the dashboard
# Open http://localhost:8000/dashboard.html
# Click Load results.json and select all three results files at once
```
