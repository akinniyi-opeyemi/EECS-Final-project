# GUI Agent Temporal Robustness Benchmark

**EECS 545 Final Project — University of Michigan, Winter 2026**

A controlled benchmark for evaluating how VLM-based GUI agents degrade under temporal interface changes, and whether lightweight test-time interventions can recover lost performance.

---

## Research Questions

| RQ | Question |
|---|---|
| RQ I | How much do VLM-based GUI agents degrade under controlled interface perturbations, and which perturbation types hurt most? |
| RQ II | Can lightweight test-time interventions (experience memory, chain-of-thought reasoning) recover lost performance without retraining? |

---

## Project Structure

```
eecs_545_final_project/
├── house-renting-eval/          # Website 1: 264 tasks, 3 templates
├── Personal Website/            # Website 2: 80 tasks, 4 templates
├── course_registration/         # Website 3: 60 tasks, 3 templates
├── job_application/             # Website 4: templates exist, inference not run
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
│   ├── visualize_agent_dashboard.py    # Agent dashboard (single figure)
│   ├── visualize_agent_dashboard_v2.py # Agent dashboard v2 (5-row × 3-col)
│   ├── visualize_agent_dashboard_rows.py # Paper-ready row PNGs (5 files)
│   ├── visualize_agent_hallucinations.py # Hallucination + net-improvement charts
│   ├── visualize_pipeline.py    # Pipeline diagram (preliminary vs. controlled)
│   └── interventions/
│       ├── vanilla.py           # Strategy A: no intervention
│       ├── memory_agent.py      # Strategy B: few-shot memory
│       └── cot_agent.py         # Strategy C: chain-of-thought
├── results/
│   ├── raw_outputs/             # Per-task model predictions
│   ├── metrics/                 # Evaluation summaries
│   └── visualizations/          # All generated charts
├── results.tex                  # LaTeX result tables (SR by template, per-agent SR)
├── task_inventory_table.tex     # LaTeX benchmark task inventory table
└── environment.yml
```

---

## Benchmark Design

### Websites

| Website | Templates | Tasks | Perturbation Types | Controlled |
|---|---|---|---|---|
| house_renting | classic, modern, hidden | 264 | visible, click_to_reveal, tab_navigation, tab_then_expand, filter_navigation | Yes |
| personal_website | raw_html_1998, hugo_papermod, notion, jekyll_alfolio | 80 | framework_style | Yes |
| course_registration | 2000s, 2010s, modern | 60 | era_style | Yes |
| job_application | classic, modern, notion | 15 | framework_style | No (not evaluated) |

### Evaluation: Three-Tier Schema

```
Tier 1: exact_match    → precise value ("$1,450/month")
Tier 2: must_include   → required keywords (["$1,450", "month"])
Tier 3: fuzzy_match    → paraphrases + semantic similarity
```

### Metrics

```
SR(template) = successful tasks / total tasks
Δ(baseline, later) = SR(baseline) - SR(later)
TRS = 1 - (max degradation / SR_baseline)
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

| Mode | Description |
|---|---|
| text_only | DOM text extraction only (gpt-oss-120B) |
| multimodal | Screenshot + DOM text (Qwen3-VL-30B / local models) |
| vision_only | Screenshot only (Qwen3-VL-30B / local models) |

---

## Setup

### Local (Mac)

```bash
conda create -n eecs545 python=3.11
conda activate eecs545
pip install -r requirements.txt
playwright install chromium
```

### Bridges-2 (NSF ACCESS)

```bash
ssh <your_username>@bridges2.psc.edu
source /ocean/projects/<allocation_id>/<your_username>/miniconda3/etc/profile.d/conda.sh
conda activate eecs545_b2
srun --partition=GPU-shared --gres=gpu:v100-32:1 --mem=16G --time=10:00:00 --pty bash
```

Note: `config.py` auto-detects the environment and sets correct model paths and ports.

---

## Key Results

### RQ I: Temporal Degradation by Input Mode (house_renting)

| Mode | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|
| text_only (gpt-oss-120B) | 100.0% | 98.8% | 100.0% | 0.988 |
| multimodal (Qwen3-VL-30B) | 93.3% | 73.8% | 97.5% | 0.791 |
| vision_only (Qwen3-VL-30B) | 60.0% | 22.6% | 14.2% | 0.236 |

### RQ I: Temporal Degradation by Input Mode (personal_website)

| Mode | raw_html | hugo | notion | jekyll | TRS |
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

*TRS > 1.0 indicates inverse degradation. See Finding 9.

---

### RQ I: Cross-Agent Comparison (vision_only, house_renting)

| Agent | Type | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | text-only | 100.0% | 98.8% | 100.0% | 0.988 |
| UI-TARS-7B | GUI-specialized | 58.3% | 27.4% | 24.2% | **0.414** |
| Qwen2.5-VL-7B | general vision | 60.0% | 23.8% | 15.0% | 0.250 |
| Qwen3-VL-30B | general vision | 60.0% | 22.6% | 14.2% | 0.236 |
| InternVL2-8B | general vision | 53.3% | 27.4% | 12.5% | 0.234 |

### RQ I: Cross-Agent Comparison (multimodal, house_renting)

| Agent | Type | Classic | Modern | Hidden | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | text-only | 100.0% | 98.8% | 100.0% | 0.988 |
| UI-TARS-7B | GUI-specialized | 98.3% | 96.4% | 96.7% | **0.981** |
| InternVL2-8B | general vision | 93.3% | 92.9% | 87.5% | 0.938 |
| Qwen2.5-VL-7B | general vision | 93.3% | 78.6% | 94.2% | 0.842 |
| Qwen3-VL-30B | general vision | 93.3% | 73.8% | 97.5% | 0.791 |

### RQ I: Cross-Agent Comparison (vision_only, personal_website)

| Agent | raw_html | hugo | notion | jekyll | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | 95.0% | 95.0% | 90.0% | 80.0% | 0.842 |
| Qwen3-VL-30B | 60.0% | 40.0% | 30.0% | 60.0% | 0.500 |
| Qwen2.5-VL-7B | 60.0% | 40.0% | 30.0% | 60.0% | 0.500 |
| UI-TARS-7B | 60.0% | 40.0% | 25.0% | 60.0% | 0.417 |
| InternVL2-8B | 60.0% | 40.0% | 25.0% | 60.0% | 0.417 |

### RQ I: Cross-Agent Comparison (multimodal, personal_website)

| Agent | raw_html | hugo | notion | jekyll | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | 95.0% | 95.0% | 90.0% | 80.0% | 0.842 |
| Qwen2.5-VL-7B | 70.0% | 70.0% | 80.0% | 65.0% | **0.929** |
| UI-TARS-7B | 80.0% | 85.0% | 70.0% | 70.0% | 0.875 |
| Qwen3-VL-30B | 75.0% | 85.0% | 80.0% | 65.0% | 0.867 |
| InternVL2-8B | 75.0% | 70.0% | 80.0% | 60.0% | 0.800 |

### RQ I: Cross-Agent Comparison (vision_only, course_registration)

| Agent | Type | 2000s | 2010s | modern | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | text-only | 85.0% | 90.0% | 90.0% | 1.059* |
| InternVL2-8B | general vision | 40.0% | 40.0% | 35.0% | **0.875** |
| Qwen3-VL-30B | general vision | 45.0% | 60.0% | 30.0% | 0.667 |
| Qwen2.5-VL-7B | general vision | 55.0% | 55.0% | 15.0% | 0.273 |
| UI-TARS-7B | GUI-specialized | 55.0% | 50.0% | 10.0% | 0.182 |

### RQ I: Cross-Agent Comparison (multimodal, course_registration)

| Agent | Type | 2000s | 2010s | modern | TRS |
|---|---|---|---|---|---|
| gpt-oss-120B | text-only | 85.0% | 90.0% | 90.0% | 1.059* |
| Qwen3-VL-30B | general vision | 65.0% | 90.0% | 90.0% | 1.385* |
| InternVL2-8B | general vision | 55.0% | 80.0% | 70.0% | 1.273* |
| Qwen2.5-VL-7B | general vision | 70.0% | 80.0% | 70.0% | 1.000* |
| UI-TARS-7B | GUI-specialized | 90.0% | 65.0% | 75.0% | 0.722 |

*TRS > 1.0 indicates inverse degradation pattern. See Finding 9.

---

### RQ II: Test-Time Interventions (house_renting, vision_only)

| Agent | Memory Rate | Mem Hall. | CoT Rate | CoT Hall. |
|---|---|---|---|---|
| Qwen2.5-VL-7B | **52.1%** | 60 | 4.2% | 10 |
| InternVL2-8B | 41.8% | 107 | 11.3% | 44 |
| Qwen3-VL-30B | 35.9% | 23 | 6.2% | 29 |
| UI-TARS-7B | 23.2% | 104 | 4.0% | 65 |

### RQ II: Test-Time Interventions (personal_website, vision_only)

| Agent | Memory Rate | Mem Hall. | CoT Rate | CoT Hall. |
|---|---|---|---|---|
| InternVL2-8B | 9.5% | 38 | 7.1% | 23 |
| UI-TARS-7B | 7.1% | 28 | 7.1% | 23 |
| Qwen2.5-VL-7B | 4.8% | 40 | 7.1% | 23 |
| Qwen3-VL-30B | 0.0% | 31 | 2.4% | 8 |

### RQ II: Test-Time Interventions (course_registration, vision_only)

| Agent | Memory Rate | Mem Hall. | CoT Rate | CoT Hall. |
|---|---|---|---|---|
| UI-TARS-7B | 21.6% | 28 | 13.5% | 28 |
| Qwen2.5-VL-7B | 5.7% | 33 | **22.9%** | 20 |
| InternVL2-8B | 5.4% | 35 | 13.5% | 27 |
| Qwen3-VL-30B | 3.0% | 31 | 15.2% | 21 |

**Key finding:** Course_registration is the only website where CoT consistently outperforms memory across all agents. This is the reverse of house_renting and suggests CoT is more effective when failures require reasoning about interactive UI state.

---

## Summary of Key Findings

### Finding 1: Input modality is the primary driver of robustness

| Mode | TRS (house_renting) | TRS (personal_website) |
|---|---|---|
| text_only | 0.988 | 0.842 |
| multimodal | 0.791 | 0.867 |
| vision_only | 0.236 | 0.500 |

### Finding 2: GUI specialization outperforms scale in vision-only mode (interaction-heavy sites)

UI-TARS-7B (TRS=0.414) outperforms Qwen3-VL-30B (TRS=0.236) on house\_renting vision-only despite being 4x smaller. This advantage disappears on navigation-dominated websites like personal\_website where all agents converge.

### Finding 3: UI-TARS multimodal is the optimal configuration for interaction-heavy websites

UI-TARS in multimodal mode achieves TRS=0.981, nearly matching text-only (TRS=0.988), while using a 17x smaller model.

### Finding 4: click_to_reveal and tab_navigation are irreducible barriers in vision-only mode

All five vision agents score 0% on these perturbation types. No intervention can help because information is fundamentally inaccessible in a static screenshot.

### Finding 5: Memory intervention effectiveness depends on failure mode type and agent

Memory helps when information exists on the page but layout changed (up to 52.1% on house\_renting). It is actively harmful when failures are navigation-based (near 0% on personal\_website).

### Finding 6: CoT effectiveness depends on the website domain

CoT is consistently weak on house\_renting (4-11%) and personal\_website (2-11%). It outperforms memory on course\_registration (13-23% vs 3-22%), suggesting it is more effective when failures require reasoning about interactive UI state.

### Finding 7: Agent rankings differ by website and mode

UI-TARS leads on house\_renting (interaction-heavy). Qwen2.5 leads on personal\_website multimodal (text-heavy). InternVL2 has the highest vision-only TRS on course\_registration (0.875). No single agent dominates everywhere.

### Finding 8: Vision agents converge on navigation-dominated websites

On personal\_website vision-only, all agents cluster at TRS=0.417-0.500 regardless of size or specialization. Failure mode type is a stronger predictor of robustness than model architecture.

### Finding 9: Era-style perturbations show inverse degradation on course_registration

For course\_registration, text-only and multimodal agents perform better on 2010s and modern templates than the 2000s baseline (TRS > 1.0). Table-based 2000s HTML is harder to parse than modern semantic HTML, reversing the expected degradation direction. Vision-only agents still show normal degradation on modern (10-35%) because modern UI hides details behind interactive components.

---

## Failure Analysis

**Viewport limitation (12.5% of house_renting failures):** Information below 720px fold. Fixable with full-page screenshots.

**Interaction limitation (75.0% of house_renting failures):** Content behind buttons, tabs, or toggles. Fundamental barrier for static screenshot evaluation.

**Navigation limitation (66.7% of personal_website failures):** Information on a linked page. Agent cannot follow links in static evaluation mode.

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