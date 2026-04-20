# scripts/evaluate.py
# Configurable evaluation script for all four websites.
# Usage:
#   python scripts/evaluate.py --website house_renting
#   python scripts/evaluate.py --website personal_website
#   python scripts/evaluate.py --website job_application
#   python scripts/evaluate.py --website course_registration

import json, argparse
from pathlib import Path
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--website",
    required=True,
    choices=["house_renting", "personal_website",
             "job_application", "course_registration"],
    help="Which website to evaluate"
)
parser.add_argument(
    "--mode",
    default="text_only",
    choices=["text_only", "multimodal", "vision_only"],
    help="Which inference mode to evaluate"
)
args = parser.parse_args()

# ============================================================
# WEBSITE CONFIGURATIONS
# ============================================================
CONFIGS = {
   "house_renting": {
    "task_file":      Path("house-renting-eval/tasks.json"),
    "raw_output_dir": Path(f"results/raw_outputs/house_renting/{args.mode}"),
    "results_dir":    Path(f"results/metrics/house_renting/{args.mode}"),
    "templates":      ["classic", "modern", "hidden"],
    "baseline":       "classic",
    },
    "personal_website": {
        "task_file":      Path("Personal Website/tasks/test.raw.json"),
        "raw_output_dir": Path(f"results/raw_outputs/personal_website/{args.mode}"),
        "results_dir":    Path(f"results/metrics/personal_website/{args.mode}"),
        "templates":      ["raw_html_1998", "hugo_papermod",
                        "notion", "jekyll_alfolio"],
        "baseline":       "raw_html_1998",
    },
    "job_application": {
        "task_file":      Path("job_application/tasks.json"),
        "raw_output_dir": Path(f"results/raw_outputs/job_application/{args.mode}"),
        "results_dir":    Path(f"results/metrics/job_application/{args.mode}"),
        "templates":      ["classic", "modern", "notion"],
        "baseline":       "classic",
    },
    "course_registration": {
        "task_file":      Path("course_registration/tasks.json"),
        "raw_output_dir": Path(f"results/raw_outputs/course_registration/{args.mode}"),
        "results_dir":    Path(f"results/metrics/course_registration/{args.mode}"),
        "templates":      ["2000s", "2010s", "modern"],
        "baseline":       "2000s",
    },
}

config        = CONFIGS[args.website]
TASK_FILE     = config["task_file"]
RAW_DIR       = config["raw_output_dir"]
RESULTS_DIR   = config["results_dir"]
TEMPLATES     = config["templates"]
BASELINE      = config["baseline"]
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FUZZY_THRESHOLD    = 0.75
SEMANTIC_THRESHOLD = 0.80

# ============================================================
# LOAD SEMANTIC MODEL
# ============================================================
print("Loading semantic similarity model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Ready.\n")

# ============================================================
# FUNCTION 1: Three-tier evaluation
# ============================================================
def evaluate_prediction(prediction, reference_answers):
    if not prediction:
        return False, "no_prediction", {}

    prediction = prediction.strip()

    # tier 1: exact match
    exact = reference_answers.get("exact_match")
    if exact:
        if prediction.lower() == exact.lower():
            return True, "exact_match", {"matched": exact}
        if exact.lower() in prediction.lower():
            return True, "exact_match_contained", {"matched": exact}

    # tier 2: must_include
    must = reference_answers.get("must_include") or []
    if must:
        if all(kw.lower() in prediction.lower() for kw in must):
            return True, "must_include", {"keywords": must}

    # tier 3a: fuzzy string match
    fuzzy_refs = reference_answers.get("fuzzy_match") or []
    for ref in fuzzy_refs:
        score = fuzz.ratio(prediction.lower(), ref.lower()) / 100
        if score >= FUZZY_THRESHOLD:
            return True, "fuzzy_string", {
                "matched": ref, "score": round(score, 3)
            }

    # tier 3b: semantic similarity
    if fuzzy_refs:
        pred_emb = embedder.encode(prediction, convert_to_tensor=True)
        for ref in fuzzy_refs:
            ref_emb = embedder.encode(ref, convert_to_tensor=True)
            sim = float(util.cos_sim(pred_emb, ref_emb))
            if sim >= SEMANTIC_THRESHOLD:
                return True, "semantic_match", {
                    "matched": ref, "score": round(sim, 3)
                }

    return False, "no_match", {}


# ============================================================
# FUNCTION 2: Metrics
# ============================================================
def success_rate(results):
    if not results:
        return 0.0
    return sum(1 for r in results if r["success"]) / len(results)

def temporal_degradation(sr_baseline, sr_later):
    return round(sr_baseline - sr_later, 4)

def compute_trs(sr_baseline, all_sr_values):
    if sr_baseline == 0:
        return 0.0
    max_deg = max(sr_baseline - sr for sr in all_sr_values)
    return round(1 - (max_deg / sr_baseline), 4)


# ============================================================
# MAIN: Load and evaluate
# ============================================================
print(f"Website:  {args.website}")
print(f"Mode:     {args.mode}")
print(f"Tasks:    {TASK_FILE}")
print(f"Outputs:  {RAW_DIR}\n")

with open(TASK_FILE) as f:
    tasks = json.load(f)

task_lookup = {str(t["task_id"]): t for t in tasks}

raw_files = list(RAW_DIR.glob("*.json"))
print(f"Found {len(raw_files)} raw output files")
print(f"Total tasks: {len(tasks)}\n")

# ============================================================
# EVALUATE EACH TASK
# ============================================================
evaluated = []
missing   = []

for task in tasks:
    task_id  = str(task["task_id"])
    out_file = RAW_DIR / f"{task_id}.json"

    if not out_file.exists():
        missing.append(task_id)
        continue

    with open(out_file) as f:
        raw = json.load(f)

    prediction       = raw.get("raw_output", "")
    ref_answers      = task["eval"]["reference_answers"]
    raw_annotation   = task["eval"].get("reference_answer_raw_annotation", "")

    # skip unverified tasks (course_registration)
    if not task["eval"].get("verified", True) and not raw_annotation:
        missing.append(task_id)
        continue

    success, tier, details = evaluate_prediction(prediction, ref_answers)

    evaluated.append({
        "task_id":           task_id,
        "website":           args.website,
        "template":          task.get("template", ""),
        "template_style":    task.get("template_style", ""),
        "perturbation_type": task.get("perturbation_type", ""),
        "task_type":         task.get("task_type", ""),
        "instruction":       task.get("instruction") or task.get("intent", ""),
        "interaction":       task.get("interaction", "none"),
        "prediction":        prediction,
        "ground_truth":      raw_annotation,
        "success":           success,
        "tier_matched":      tier,
        "match_details":     details,
        "mode":              raw.get("mode", "text_only"),
        "model":             raw.get("model", "")
    })

print(f"Evaluated: {len(evaluated)}")
print(f"Missing:   {len(missing)}")

# ============================================================
# METRICS BY TEMPLATE
# ============================================================
template_results = {}
for template in TEMPLATES:
    t_results = [e for e in evaluated if e["template"] == template]
    template_results[template] = {
        "results":      t_results,
        "count":        len(t_results),
        "success_rate": success_rate(t_results)
    }

# ============================================================
# METRICS BY TASK TYPE (personal_website and course_registration)
# ============================================================
task_types = sorted(set(e["task_type"] for e in evaluated if e["task_type"]))
task_type_results = {}
for tt in task_types:
    tt_results = [e for e in evaluated if e["task_type"] == tt]
    task_type_results[tt] = {
        "count":        len(tt_results),
        "success_rate": success_rate(tt_results)
    }

# ============================================================
# METRICS BY PERTURBATION TYPE
# ============================================================
perturbation_types = sorted(set(
    e["perturbation_type"] for e in evaluated
    if e["perturbation_type"]
))
perturbation_results = {}
for ptype in perturbation_types:
    p_results = [e for e in evaluated if e["perturbation_type"] == ptype]
    perturbation_results[ptype] = {
        "count":        len(p_results),
        "success_rate": success_rate(p_results)
    }

# ============================================================
# TEMPORAL DEGRADATION AND TRS
# ============================================================
sr_by_template = {
    t: template_results[t]["success_rate"]
    for t in TEMPLATES
    if t in template_results
}

sr_baseline = sr_by_template.get(BASELINE, 0)
other_srs   = [sr for t, sr in sr_by_template.items() if t != BASELINE]
trs         = compute_trs(sr_baseline, other_srs) if other_srs else 1.0

degradation = {}
for template in TEMPLATES:
    if template != BASELINE and template in sr_by_template:
        degradation[f"{BASELINE}_to_{template}"] = temporal_degradation(
            sr_baseline, sr_by_template[template]
        )

# ============================================================
# PRINT RESULTS
# ============================================================
print(f"\n{'='*50}")
print(f"EVALUATION RESULTS: {args.website} (text-only)")
print(f"{'='*50}")

print(f"\nSUCCESS RATES BY TEMPLATE:")
for template in TEMPLATES:
    if template in template_results:
        sr   = template_results[template]["success_rate"]
        cnt  = template_results[template]["count"]
        star = " ← baseline" if template == BASELINE else ""
        print(f"  {template:<20} {sr:.1%}  ({cnt} tasks){star}")

print(f"\nTEMPORAL DEGRADATION:")
for label, deg in degradation.items():
    direction = "↓ degraded" if deg > 0 else "↑ improved"
    print(f"  {label:<35} {deg:+.1%}  {direction}")

print(f"\nTEMPORAL ROBUSTNESS SCORE (TRS): {trs:.3f}")
print(f"  (1.0 = perfect robustness, 0.0 = complete failure)")

if task_type_results:
    print(f"\nSUCCESS RATES BY TASK TYPE:")
    for tt, data in sorted(task_type_results.items(),
                           key=lambda x: x[1]["success_rate"],
                           reverse=True):
        print(f"  {tt:<25} {data['success_rate']:.1%}  ({data['count']} tasks)")

if perturbation_results:
    print(f"\nSUCCESS RATES BY PERTURBATION TYPE:")
    for ptype, data in sorted(perturbation_results.items(),
                               key=lambda x: x[1]["success_rate"],
                               reverse=True):
        print(f"  {ptype:<25} {data['success_rate']:.1%}  ({data['count']} tasks)")

print(f"\nMATCH TIER BREAKDOWN:")
tier_counts = {}
for e in evaluated:
    tier = e["tier_matched"]
    tier_counts[tier] = tier_counts.get(tier, 0) + 1
for tier, count in sorted(tier_counts.items(),
                           key=lambda x: x[1], reverse=True):
    pct = count / len(evaluated) * 100 if evaluated else 0
    print(f"  {tier:<25} {count:3d}  ({pct:.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================
per_task_path = RESULTS_DIR / "per_task_results.json"
with open(per_task_path, "w") as f:
    json.dump(evaluated, f, indent=2)

summary = {
    "website":         args.website,
    "model":           evaluated[0]["model"] if evaluated else "",
    "mode":            args.mode,

    "total_tasks":     len(tasks),
    "evaluated_tasks": len(evaluated),
    "missing_tasks":   len(missing),
    "baseline":        BASELINE,
    "success_rates":   {t: round(sr_by_template.get(t, 0), 4)
                        for t in TEMPLATES},
    "temporal_degradation": degradation,
    "trs":             trs,
    "task_type_results":    task_type_results,
    "perturbation_results": perturbation_results,
    "tier_breakdown":       tier_counts
}

summary_path = RESULTS_DIR / "summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved:")
print(f"  Per-task: {per_task_path}")
print(f"  Summary:  {summary_path}")

if missing:
    print(f"\nWARNING: {len(missing)} tasks missing or unverified")