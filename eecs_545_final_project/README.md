# GUI Agent Temporal Robustness Benchmark

**EECS 545 Final Project — University of Michigan, Winter 2026**

A controlled benchmark for evaluating how VLM-based GUI agents degrade under temporal interface changes, and whether lightweight test-time interventions can recover lost performance.

---

## Research Questions

| RQ | Question |
|---|---|
| RQ I | How much do VLM-based GUI agents degrade under controlled interface perturbations, and which perturbation types hurt most? |
| RQ II | Can lightweight test-time interventions (experience memory, chain-of-thought reasoning) recover lost performance without retraining? |
| RQ III | What failure modes characterize non-robust GUI agents? |

---

## Project Structure

```
eecs_545_final_project/
├── house-renting-eval/          # Website 1: 264 tasks, 3 templates
├── Personal Website/            # Website 2: 80 tasks, 4 templates
├── course_registration/         # Website 3: 144 tasks, 3 templates (pending annotation)
├── job_application/             # Website 4: 15 tasks (supplementary)
├── scripts/
│   ├── infer.py                 # Main inference script (--agent, --mode, --website)
│   ├── evaluate.py              # Evaluation with three-tier metrics
│   ├── evaluate_rq2.py          # RQ II intervention evaluation
│   ├── infer_rq2.py             # RQ II intervention inference
│   ├── visualize.py             # Per-website visualizations
│   ├── visualize_comprehensive.py  # Full dashboard
│   ├── visualize_agents.py      # Cross-agent comparison
│   ├── visualize_rq2.py         # RQ II visualizations
│   └── interventions/
│       ├── vanilla.py           # Strategy A: no intervention
│       ├── memory_agent.py      # Strategy B: few-shot memory
│       └── cot_agent.py         # Strategy C: chain-of-thought
├── results/
│   ├── raw_outputs/             # Per-task model predictions
│   ├── metrics/                 # Evaluation summaries
│   └── visualizations/          # All generated charts
└── environment.yml
```

---

## Benchmark Design

### Websites

All websites use a controlled design: same content across templates, only the UI framework changes.

| Website | Templates | Tasks | Perturbation Types | Controlled |
|---|---|---|---|---|
| house_renting | classic, modern, hidden | 264 | visible, click_to_reveal, tab_navigation, tab_then_expand, filter_navigation | Yes |
| personal_website | raw_html_1998, hugo_papermod, notion, jekyll_alfolio | 80 | framework_style | Yes |
| course_registration | 2000s, 2010s, modern | 144 | framework_style | Yes (pending annotation) |
| job_application | classic, modern, notion | 15 | framework_style | No (supplementary) |

### Evaluation: Three-Tier Schema

Each task has three levels of reference answers:

```
Tier 1: exact_match    → precise value ("$1,450/month")
Tier 2: must_include   → required keywords (["$1,450", "month"])
Tier 3: fuzzy_match    → paraphrases + semantic similarity
```

### Metrics

**Success Rate (SR):**
```
SR(template) = successful tasks / total tasks
```

**Temporal Degradation:**
```
Δ(baseline, later) = SR(baseline) - SR(later)
```

**Temporal Robustness Score (TRS):**
```
TRS = 1 - (max degradation / SR_baseline)
TRS = 1.0  → perfect robustness
TRS = 0.0  → complete failure
```

---

## Agents

| Agent | Model | Size | Type | Endpoint |
|---|---|---|---|---|
| gpt_oss | openai/gpt-oss-120b | 120B | text-only | class server |
| qwen_vl | Qwen/Qwen3-VL-30B-A3B-Instruct | 30B | general vision | class server |
| uitars | bytedance-research/UI-TARS-7B-DPO | 7B | GUI-specialized | Great Lakes |
| qwen25 | Qwen/Qwen2.5-VL-7B-Instruct | 7B | general vision | Great Lakes |
| internvl | OpenGVLab/InternVL2-8B | 8B | general vision | Great Lakes |

### Input Modes

| Mode | Description | Model |
|---|---|---|
| text_only | DOM text extraction only | gpt-oss-120B |
| multimodal | Screenshot + DOM text | Qwen3-VL-30B |
| vision_only | Screenshot only | Qwen3-VL-30B / local models |

---

## Setup

### Local (Mac)

```bash
conda create -n eecs545 python=3.11
conda activate eecs545
pip install -r requirements.txt
playwright install chromium
```

### Great Lakes

```bash
module load cuda
module load python3.11-anaconda/2024.02
conda activate eecs545_gl
pip install vllm openai playwright rapidfuzz sentence-transformers
playwright install chromium
```

### Environment Variables

```bash
export OPENAI_BASE_URL="http://promaxgb10-d473.eecs.umich.edu:8000/v1"
export OPENAI_API_KEY="your_key"
export QWEN_BASE_URL="http://promaxgb10-d668.eecs.umich.edu:8000/v1"
export QWEN_API_KEY="your_key"
export UITARS_BASE_URL="http://gl1501:8001/v1"
export UITARS_API_KEY="local"
export QWEN25_BASE_URL="http://gl1501:8002/v1"
export QWEN25_API_KEY="local"
export INTERNVL_BASE_URL="http://gl1501:8003/v1"
export INTERNVL_API_KEY="local"
```

---

## Serving Models on Great Lakes

```bash
# UI-TARS-7B on port 8001
python -m vllm.entrypoints.openai.api_server \
    --model /scratch/.../models/UI-TARS-7B-DPO \
    --port 8001 --host 0.0.0.0 \
    --max-model-len 4096 --dtype bfloat16

# Qwen2.5-VL-7B on port 8002
python -m vllm.entrypoints.openai.api_server \
    --model /scratch/.../models/Qwen2.5-VL-7B-Instruct \
    --port 8002 --host 0.0.0.0 \
    --max-model-len 4096 --dtype bfloat16

# InternVL2-8B on port 8003
python -m vllm.entrypoints.openai.api_server \
    --model /scratch/.../models/InternVL2-8B \
    --port 8003 --host 0.0.0.0 \
    --max-model-len 4096 --dtype bfloat16
```

---

## Running Inference

```bash
# Start website server
cd house-renting-eval && python -m http.server 8888

# Run inference
python scripts/infer.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars

# All combinations
for agent in gpt_oss qwen_vl uitars qwen25 internvl; do
    python scripts/infer.py --website house_renting --mode vision_only --agent $agent
done
```

---

## Running Evaluation

```bash
python scripts/evaluate.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars
```

---

## Running RQ II Interventions

```bash
# Run memory and CoT on failed tasks
python scripts/infer_rq2.py \
    --website house_renting \
    --mode vision_only \
    --strategy memory

python scripts/infer_rq2.py \
    --website house_renting \
    --mode vision_only \
    --strategy cot

# Evaluate interventions
python scripts/evaluate_rq2.py \
    --website house_renting \
    --mode vision_only
```

---

## Generating Visualizations

```bash
# Per-website dashboard
python scripts/visualize.py --website house_renting
python scripts/visualize.py --website personal_website

# Cross-mode comparison
python scripts/visualize.py --website all

# Comprehensive dashboard (3 websites, all modes)
python scripts/visualize_comprehensive.py

# Cross-agent comparison
python scripts/visualize_agents.py

# RQ II intervention results
python scripts/visualize_rq2.py --website house_renting --mode vision_only
```

---

## Key Results

### RQ I: Temporal Degradation by Input Mode (house_renting)

| Mode | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|
| text_only (gpt-oss-120B) | 100.0% | 98.8% | 100.0% | 0.988 |
| multimodal (Qwen3-VL-30B) | 93.3% | 73.8% | 97.5% | 0.791 |
| vision_only (Qwen3-VL-30B) | 60.0% | 22.6% | 14.2% | 0.236 |

### RQ I: Temporal Degradation by Agent (vision_only, house_renting)

| Agent | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|
| gpt-oss-120B (text-only) | 100.0% | 98.8% | 100.0% | 0.988 |
| Qwen3-VL-30B | 60.0% | 22.6% | 14.2% | 0.236 |
| UI-TARS-7B | 58.3% | 27.4% | 24.2% | 0.414 |
| Qwen2.5-VL-7B | 60.0% | 23.8% | 15.0% | 0.250 |
| InternVL2-8B | TBD | TBD | TBD | TBD |

### RQ II: Test-Time Interventions (house_renting, vision_only)

| Strategy | Recovered | Rate | Hallucinated | Net |
|---|---|---|---|---|
| vanilla | 0 | 0.0% | 0 | 0.0% |
| memory | 69 | 35.9% | 23 | +24.0% |
| CoT | 12 | 6.2% | 29 | -8.8% |

### RQ III: Failure Mode Taxonomy (vision_only)

| Category | Count | Description |
|---|---|---|
| Viewport limitation | 24 | Information exists but below 720px fold |
| Interaction limitation | 144 | Content hidden behind buttons or tabs |
| Navigation limitation | 7 | Requires sidebar filter interaction |
| Navigation (multi-page) | 28 | Information on a different page entirely |

---

## Failure Analysis

Three distinct failure categories identified:

**Category 1: Viewport limitation (9.1% of failures)**
Information exists on the page but is below the 720px viewport. Agent cannot scroll. Fixable with full-page screenshots.

**Category 2: Interaction limitation (72.7% of failures)**
Content hidden behind interactive elements (buttons, tabs, toggles). Agent can see the element visually but cannot click it. Fundamental barrier for static screenshot evaluation.

**Category 3: Navigation limitation (3.6% of failures)**
Information requires sidebar filter or multi-page navigation. Agent cannot interact with filters or navigate to linked pages.

---

## Citation

If you use this benchmark, please cite:

```
@misc{eecs545_gui_robustness_2026,
  title  = {GUI Agent Temporal Robustness Benchmark},
  author = {group members},
  year   = {2026},
  note   = {EECS 545 Final Project, University of Michigan}
}
```

---

## Acknowledgments

Class API access provided by EECS 545 course staff, University of Michigan.
Compute provided by University of Michigan Advanced Research Computing (ARC).