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
├── course_registration/         # Website 3: 60 tasks, 3 templates
├── job_application/             # Website 4: 15 tasks (supplementary)
├── scripts/
│   ├── infer.py                 # Main inference script (--agent, --mode, --website)
│   ├── evaluate.py              # Evaluation with three-tier metrics
│   ├── evaluate_rq2.py          # RQ II intervention evaluation
│   ├── infer_rq2.py             # RQ II intervention inference
│   ├── config.py                # Environment auto-detection (Mac, Great Lakes, Bridges-2)
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
| course_registration | 2000s, 2010s, modern | 60 | era_style | Yes |
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
| uitars | bytedance-research/UI-TARS-7B-DPO | 7B | GUI-specialized | Great Lakes / Bridges-2 |
| qwen25 | Qwen/Qwen2.5-VL-7B-Instruct | 7B | general vision | Great Lakes / Bridges-2 |
| internvl | OpenGVLab/InternVL2-8B | 8B | general vision | Great Lakes / Bridges-2 |

### Input Modes

| Mode | Description | Model |
|---|---|---|
| text_only | DOM text extraction only | gpt-oss-120B |
| multimodal | Screenshot + DOM text | Qwen3-VL-30B / local models |
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

# request GPU node
srun --partition=spgpu --gres=gpu:1 --mem=40G --time=4:00:00 --pty bash
```

### Bridges-2 (NSF ACCESS)

```bash
# login
ssh <your_username>@bridges2.psc.edu

# setup
source /ocean/projects/<allocation_id>/<your_username>/miniconda3/etc/profile.d/conda.sh
conda activate eecs545_b2
module load cuda
pip install vllm openai playwright rapidfuzz sentence-transformers
playwright install chromium

# request GPU node
srun --partition=GPU-shared --gres=gpu:v100-32:1 --mem=16G --time=10:00:00 --pty bash
```

### Environment Variables

```bash
export OPENAI_BASE_URL="http://promaxgb10-d473.eecs.umich.edu:8000/v1"
export OPENAI_API_KEY="your_key"
export QWEN_BASE_URL="http://promaxgb10-d668.eecs.umich.edu:8000/v1"
export QWEN_API_KEY="your_key"
export UITARS_BASE_URL="http://localhost:9002/v1"
export UITARS_API_KEY="local"
export QWEN25_BASE_URL="http://localhost:9003/v1"
export QWEN25_API_KEY="local"
export INTERNVL_BASE_URL="http://localhost:9004/v1"
export INTERNVL_API_KEY="local"
```

Note: `config.py` auto-detects the environment (Mac, Great Lakes, Bridges-2) and sets correct model paths and ports automatically.

---

## Serving Models on Great Lakes / Bridges-2

```bash
# UI-TARS-7B on port 9002 (Bridges-2)
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/models/UI-TARS-7B-DPO \
    --port 9002 --host 0.0.0.0 \
    --max-model-len 4096 --dtype half

# Qwen2.5-VL-7B on port 9003 (Bridges-2)
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/models/Qwen2.5-VL-7B-Instruct \
    --port 9003 --host 0.0.0.0 \
    --max-model-len 4096 --dtype half

# InternVL2-8B on port 9004 (Bridges-2, requires --trust-remote-code)
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/models/InternVL2-8B \
    --port 9004 --host 0.0.0.0 \
    --max-model-len 4096 --dtype half \
    --trust-remote-code

# Note: use --dtype half instead of bfloat16 on V100 nodes
```

---

## Running Inference

```bash
# start website server (Mac)
cd house-renting-eval && python -m http.server 8888

# start course_registration server (Mac)
python -m http.server 8001 --directory course_registration &

# run inference
python scripts/infer.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars

# all combinations
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
# run memory and CoT on failed tasks
python scripts/infer_rq2.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars \
    --strategy memory

python scripts/infer_rq2.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars \
    --strategy cot

# evaluate interventions
python scripts/evaluate_rq2.py \
    --website house_renting \
    --mode vision_only \
    --agent uitars
```

---

## Generating Visualizations

```bash
# per-website dashboard
python scripts/visualize.py --website house_renting
python scripts/visualize.py --website personal_website

# cross-mode comparison
python scripts/visualize.py --website all

# comprehensive dashboard (3 websites, all modes)
python scripts/visualize_comprehensive.py

# cross-agent comparison
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

### RQ I: Temporal Degradation by Input Mode (personal_website)

| Mode | raw_html_1998 | hugo_papermod | notion | jekyll_alfolio | TRS |
|---|---|---|---|---|---|
| text_only (gpt-oss-120B) | 95.0% | 95.0% | 90.0% | 80.0% | 0.842 |
| multimodal (Qwen3-VL-30B) | 75.0% | 85.0% | 80.0% | 65.0% | 0.867 |
| vision_only (Qwen3-VL-30B) | 60.0% | 40.0% | 30.0% | 60.0% | 0.500 |

### RQ I: Temporal Degradation by Input Mode (course_registration)

| Mode | 2000s | 2010s | modern | TRS |
|---|---|---|---|---|
| text_only (gpt-oss-120B) | 85.0% | 90.0% | 90.0% | 1.059* |
| multimodal (Qwen3-VL-30B) | 65.0% | 90.0% | 90.0% | 1.385* |
| vision_only (Qwen3-VL-30B) | 45.0% | 60.0% | 30.0% | 0.667 |

*TRS > 1.0 indicates that the 2000s template is harder than later templates, reversing the expected degradation direction. See Finding 9.

---

### RQ I: Cross-Agent Comparison (vision_only, house_renting)

| Agent | Params | Type | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|---|---|
| gpt-oss-120B | 120B | text-only | 100.0% | 98.8% | 100.0% | 0.988 |
| Qwen3-VL-30B | 30B | general vision | 60.0% | 22.6% | 14.2% | 0.236 |
| UI-TARS-7B | 7B | GUI-specialized | 58.3% | 27.4% | 24.2% | **0.414** |
| Qwen2.5-VL-7B | 7B | general vision | 60.0% | 23.8% | 15.0% | 0.250 |
| InternVL2-8B | 8B | general vision | 53.3% | 27.4% | 12.5% | 0.234 |

**Key finding 1:** UI-TARS-7B (TRS=0.414) is the most robust vision agent despite being 4x smaller than Qwen3-VL-30B (TRS=0.236). GUI specialization matters more than model size for temporal robustness.

**Key finding 2:** Qwen2.5-VL-7B (TRS=0.250) matches Qwen3-VL-30B (TRS=0.236) despite being 4x smaller. Scaling within the same model family yields minimal robustness gains.

**Key finding 3:** click_to_reveal and tab_navigation achieve 0% success rate across ALL vision agents, confirming these represent fundamental interaction barriers that no vision agent can overcome without actual browser interaction.

### RQ I: Cross-Agent Comparison (multimodal, house_renting)

| Agent | Params | Type | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|---|---|
| Qwen3-VL-30B | 30B | general vision | 93.3% | 73.8% | 97.5% | 0.791 |
| UI-TARS-7B | 7B | GUI-specialized | 98.3% | 96.4% | 96.7% | **0.981** |
| Qwen2.5-VL-7B | 7B | general vision | 93.3% | 78.6% | 94.2% | 0.842 |
| InternVL2-8B | 8B | general vision | 93.3% | 92.9% | 87.5% | 0.938 |

**Key finding:** UI-TARS-7B achieves TRS=0.981 in multimodal mode, nearly matching text-only performance (TRS=0.988). InternVL2-8B also performs strongly (TRS=0.938), suggesting multimodal mode significantly benefits all agents by resolving interaction barriers via DOM text extraction.

### RQ I: Cross-Agent Comparison (vision_only, personal_website)

| Agent | raw_html_1998 | hugo_papermod | notion | jekyll_alfolio | TRS |
|---|---|---|---|---|---|
| Qwen3-VL-30B | 60.0% | 40.0% | 30.0% | 60.0% | 0.500 |
| UI-TARS-7B | 60.0% | 40.0% | 25.0% | 60.0% | 0.417 |
| Qwen2.5-VL-7B | 60.0% | 40.0% | 30.0% | 60.0% | 0.500 |
| InternVL2-8B | 60.0% | 40.0% | 25.0% | 60.0% | 0.417 |

**Key finding:** All vision agents converge to similar TRS (0.417-0.500) on personal_website. Framework style perturbations affect all agents equally because failures are dominated by navigation limitations rather than visual complexity. GUI specialization provides no advantage here.

### RQ I: Cross-Agent Comparison (multimodal, personal_website)

| Agent | raw_html_1998 | hugo_papermod | notion | jekyll_alfolio | TRS |
|---|---|---|---|---|---|
| Qwen3-VL-30B | 75.0% | 85.0% | 80.0% | 65.0% | 0.867 |
| UI-TARS-7B | 80.0% | 85.0% | 70.0% | 70.0% | 0.875 |
| Qwen2.5-VL-7B | 70.0% | 70.0% | 80.0% | 65.0% | **0.929** |
| InternVL2-8B | 75.0% | 70.0% | 80.0% | 60.0% | 0.800 |

**Key finding:** Qwen2.5-VL-7B achieves the highest TRS on personal_website multimodal (0.929), outperforming UI-TARS (0.875). This suggests Qwen2.5 handles academic text-heavy content better than GUI-specialized models when DOM text is available.

### RQ I: Cross-Agent Comparison (vision_only, course_registration)

| Agent | 2000s | 2010s | modern | TRS |
|---|---|---|---|---|
| gpt-oss-120B | 85.0% | 90.0% | 90.0% | 1.059* |
| Qwen3-VL-30B | 45.0% | 60.0% | 30.0% | 0.667 |
| UI-TARS-7B | 55.0% | 50.0% | 10.0% | 0.182 |
| Qwen2.5-VL-7B | TBD | TBD | TBD | TBD |
| InternVL2-8B | TBD | TBD | TBD | TBD |

### RQ I: Cross-Agent Comparison (multimodal, course_registration)

| Agent | 2000s | 2010s | modern | TRS |
|---|---|---|---|---|
| gpt-oss-120B | 85.0% | 90.0% | 90.0% | 1.059* |
| Qwen3-VL-30B | 65.0% | 90.0% | 90.0% | 1.385* |
| UI-TARS-7B | 90.0% | 65.0% | 75.0% | 0.722 |
| Qwen2.5-VL-7B | TBD | TBD | TBD | TBD |
| InternVL2-8B | TBD | TBD | TBD | TBD |

*TRS > 1.0 due to inverse degradation pattern. See Finding 9.

---

### RQ II: Test-Time Interventions (house_renting, vision_only)

| Agent | Memory Recovered | Memory Rate | Memory Hallucinated | CoT Recovered | CoT Rate | CoT Hallucinated |
|---|---|---|---|---|---|---|
| Qwen3-VL-30B | 69 | 35.9% | 23 | 12 | 6.2% | 29 |
| UI-TARS-7B | 41 | 23.2% | 104 | 7 | 4.0% | 65 |
| Qwen2.5-VL-7B | 99 | **52.1%** | 60 | 8 | 4.2% | 10 |
| InternVL2-8B | 81 | 41.8% | 107 | 22 | 11.3% | 44 |

**Key finding:** Memory intervention effectiveness varies significantly by agent. Qwen2.5-VL-7B achieves the highest memory recovery rate (52.1%) with the lowest hallucination rate among recovering agents. UI-TARS-7B has the lowest memory recovery (23.2%) despite being the most robust vision agent, suggesting GUI specialization does not transfer to memory-augmented interventions. CoT is consistently weak across all agents (4-11%).

### RQ II: Test-Time Interventions (personal_website, vision_only)

| Agent | Memory Recovered | Memory Rate | Memory Hallucinated | CoT Recovered | CoT Rate | CoT Hallucinated |
|---|---|---|---|---|---|---|
| Qwen3-VL-30B | 0 | 0.0% | 31 | 1 | 2.4% | 8 |
| UI-TARS-7B | 3 | 7.1% | 28 | 3 | 7.1% | 23 |
| Qwen2.5-VL-7B | 2 | 4.8% | 40 | 3 | 7.1% | 23 |
| InternVL2-8B | 4 | 9.5% | 38 | 3 | 7.1% | 23 |

**Key finding:** All agents show minimal recovery on personal_website (0-9.5%), confirming that navigation-type failures are irreducible regardless of agent architecture or intervention strategy. High hallucination rates indicate interventions cause agents to fabricate answers rather than admit information is unavailable.

### RQ II: Test-Time Interventions (course_registration, vision_only)

| Agent | Memory Recovered | Memory Rate | Memory Hallucinated | CoT Recovered | CoT Rate | CoT Hallucinated |
|---|---|---|---|---|---|---|
| Qwen3-VL-30B | 1 | 3.0% | 31 | 5 | **15.2%** | 21 |
| UI-TARS-7B | 8 | **21.6%** | 28 | 5 | 13.5% | 28 |
| Qwen2.5-VL-7B | TBD | TBD | TBD | TBD | TBD | TBD |
| InternVL2-8B | TBD | TBD | TBD | TBD | TBD | TBD |

**Key finding:** Course_registration is the only website where CoT outperforms memory for Qwen3-VL-30B (15.2% vs 3.0%). This suggests CoT reasoning is more effective when failures are caused by interface complexity rather than information unavailability.

### RQ II: Memory Recovery Rate by Perturbation Type (house_renting, vision_only)

| Perturbation | Qwen3-VL | UI-TARS | Qwen2.5 | InternVL |
|---|---|---|---|---|
| visible | 60% | 23% | 70% | 60% |
| tab_navigation | 23% | 10% | 38% | 25% |
| tab_then_expand | 17% | 50% | 29% | 29% |
| filter_navigation | 14% | 0% | 100% | 0% |
| click_to_reveal | 0% | 33% | 25% | 33% |

---

### RQ III: Failure Mode Taxonomy (vision_only, house_renting)

| Category | Count | % of failures | Description |
|---|---|---|---|
| Viewport limitation | 24 | 12.5% | Information below 720px fold, requires scrolling |
| Interaction limitation | 144 | 75.0% | Content behind buttons, tabs, or toggles |
| Navigation limitation | 7 | 3.6% | Requires sidebar filter interaction |
| Wrong content retrieved | 17 | 8.9% | Agent found content but wrong answer |

### RQ III: Failure Mode Taxonomy (vision_only, personal_website)

| Category | Count | % of failures | Description |
|---|---|---|---|
| Navigation (multi-page) | 28 | 66.7% | Information on teaching.html or publications.html |
| Visual reading failure | 8 | 19.0% | Text too small or below fold |
| Wrong content retrieved | 6 | 14.3% | Agent found wrong course or publication |

---

## Summary of Key Findings

### Finding 1: Input modality is the primary driver of robustness

| Mode | TRS (house_renting) | TRS (personal_website) |
|---|---|---|
| text_only | 0.988 | 0.842 |
| multimodal | 0.791 | 0.867 |
| vision_only | 0.236 | 0.500 |

Text-only agents bypass UI complexity entirely via DOM extraction, achieving near-perfect robustness. Vision-only agents degrade severely because interactive elements are invisible barriers.

### Finding 2: GUI specialization outperforms scale in vision-only mode

| Agent | Size | Type | TRS (house_renting) |
|---|---|---|---|
| UI-TARS-7B | 7B | GUI-specialized | **0.414** |
| Qwen2.5-VL-7B | 7B | general vision | 0.250 |
| Qwen3-VL-30B | 30B | general vision | 0.236 |
| InternVL2-8B | 8B | general vision | 0.234 |

A 7B GUI-specialized model outperforms a 30B general vision model by 76% in TRS. Domain specialization is more important than parameter count for temporal robustness.

### Finding 3: UI-TARS multimodal is the optimal configuration for interaction-heavy websites

| Agent | Mode | TRS (house_renting) |
|---|---|---|
| gpt-oss-120B | text_only | 0.988 |
| UI-TARS-7B | multimodal | **0.981** |
| InternVL2-8B | multimodal | 0.938 |
| Qwen2.5-VL-7B | multimodal | 0.842 |
| Qwen3-VL-30B | multimodal | 0.791 |

UI-TARS in multimodal mode nearly matches text-only performance (TRS=0.981 vs 0.988) while using a 17x smaller model.

### Finding 4: click_to_reveal and tab_navigation are irreducible barriers in vision-only mode

All five vision agents score 0% on click_to_reveal and tab_navigation perturbations. These represent fundamental limitations of static screenshot evaluation that cannot be overcome without actual browser interaction. Multimodal agents resolve these barriers via DOM text extraction.

### Finding 5: Memory intervention effectiveness depends on both failure mode type and agent architecture

| Agent | Website | Memory Rate | Notes |
|---|---|---|---|
| Qwen2.5-VL-7B | house_renting | **52.1%** | best memory recovery |
| InternVL2-8B | house_renting | 41.8% | strong recovery |
| Qwen3-VL-30B | house_renting | 35.9% | moderate recovery |
| UI-TARS-7B | house_renting | 23.2% | weakest recovery |
| all agents | personal_website | 0-9.5% | navigation failures irreducible |

Memory intervention is beneficial when information exists on the page. It is actively harmful when failures are navigation-based. Surprisingly, GUI specialization (UI-TARS) does not help memory recovery.

### Finding 6: Agent ranking differs by website and mode

On house_renting, UI-TARS dominates in both vision_only (TRS=0.414) and multimodal (TRS=0.981) modes. On personal_website multimodal, Qwen2.5-VL-7B outperforms all agents including UI-TARS (TRS=0.929 vs 0.875). GUI specialization is most valuable for interaction-heavy websites but less critical for text-heavy academic content.

### Finding 7: Vision agents converge on navigation-dominated websites

On personal_website vision_only, all agents cluster at TRS=0.417-0.500 regardless of size or specialization. When the primary failure mode is navigation, neither GUI specialization nor model scale provides an advantage. Failure mode type is a stronger predictor of robustness than model architecture.

### Finding 8: CoT is consistently ineffective across all agents

CoT recovery rates range from 4.0-11.3% on house_renting and 2.4-7.1% on personal_website, with high hallucination rates across all agents. Chain-of-thought reasoning does not reliably improve GUI agent performance on static screenshot evaluation tasks. Exception: course_registration shows higher CoT effectiveness (15.2% for Qwen3-VL) due to different failure mode characteristics.

### Finding 9: Era-style perturbations show inverse degradation on course_registration

For course_registration, text_only and multimodal agents perform better on 2010s and modern templates than on the 2000s baseline, producing TRS > 1.0. This reveals that 2000s-era table-based HTML is harder for agents to parse than semantic HTML, reversing the expected degradation direction. Vision-only agents show the expected degradation pattern (modern is hardest at 10-30%) due to the modern template's progressive disclosure UI hiding course details behind interactive panels.

---

## Failure Analysis

**Category 1: Viewport limitation (12.5% of house_renting failures)**
Information exists on the page but is below the 720px viewport. Agent cannot scroll. Fixable with full-page screenshots.

**Category 2: Interaction limitation (75.0% of house_renting failures)**
Content hidden behind interactive elements (buttons, tabs, toggles). Agent can see the element visually but cannot click it. Fundamental barrier for static screenshot evaluation.

**Category 3: Navigation limitation (3.6% of house_renting failures)**
Information requires sidebar filter or multi-page navigation. Agent cannot interact with filters or navigate to linked pages.

**Category 4: Navigation multi-page (66.7% of personal_website failures)**
Information lives on a linked page (teaching.html, publications.html). Agent only sees the homepage and cannot follow links in static evaluation mode.

---

## Citation

```
@misc{eecs545_gui_robustness_2026,
  title  = {GUI Agent Temporal Robustness Benchmark},
  author = {Zuchen Li, Opeyemi Akinniyi, Carol Kang, Hao Yin, Xiangnong Wu},
  year   = {2026},
  note   = {EECS 545 Final Project, University of Michigan}
}
```

---

## Acknowledgments

Class API access provided by EECS 545 course staff, University of Michigan.
Compute provided by University of Michigan Advanced Research Computing (ARC) and NSF ACCESS Bridges-2.