# scripts/evaluate.py
# Evaluates raw inference outputs against three-tier ground truth.
# Computes per-task success, success rates per template,
# temporal degradation, and TRS scores.
# Answers RQ I directly.

import json, re
from pathlib import Path
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# ============================================================
# CONFIGURATION
# ============================================================
TASK_FILE      = Path("house-renting-eval/tasks.json")
RAW_OUTPUT_DIR = Path("results/raw_outputs/house_renting")
RESULTS_DIR    = Path("results/metrics/house_renting")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# semantic similarity threshold for fuzzy match
FUZZY_THRESHOLD     = 0.75   # rapidfuzz string similarity (0-100 scale, we use 0-1)
SEMANTIC_THRESHOLD  = 0.80   # sentence transformer cosine similarity

# load sentence transformer for semantic similarity
print("Loading semantic similarity model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Ready.\n")

# ============================================================
# FUNCTION 1: Three-tier evaluation
# ============================================================
def evaluate_prediction(prediction, reference_answers):
    """
    Evaluate a prediction against three-tier reference answers.
    Returns (success, tier_matched, details)
    """
    if not prediction:
        return False, "no_prediction", {}

    prediction = prediction.strip()

    # tier 1: exact match
    exact = reference_answers.get("exact_match")
    if exact:
        if prediction.lower() == exact.lower():
            return True, "exact_match", {"matched": exact}
        # also try if exact appears in prediction
        if exact.lower() in prediction.lower():
            return True, "exact_match_contained", {"matched": exact}

    # tier 2: must_include
    must = reference_answers.get("must_include", []) or []
    if must:
        all_present = all(
            kw.lower() in prediction.lower()
            for kw in must
        )
        if all_present:
            return True, "must_include", {"keywords": must}

    # tier 3a: fuzzy string match
    fuzzy_refs = reference_answers.get("fuzzy_match", []) or []
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
            ref_emb  = embedder.encode(ref, convert_to_tensor=True)
            sim = float(util.cos_sim(pred_emb, ref_emb))
            if sim >= SEMANTIC_THRESHOLD:
                return True, "semantic_match", {
                    "matched": ref, "score": round(sim, 3)
                }

    return False, "no_match", {}


# ============================================================
# FUNCTION 2: Compute success rate
# ============================================================
def success_rate(results):
    if not results:
        return 0.0
    return sum(1 for r in results if r["success"]) / len(results)


# ============================================================
# FUNCTION 3: Compute temporal degradation
# ============================================================
def temporal_degradation(sr_baseline, sr_later):
    return round(sr_baseline - sr_later, 4)


# ============================================================
# FUNCTION 4: Compute TRS
# ============================================================
def compute_trs(sr_baseline, all_sr_values):
    if sr_baseline == 0:
        return 0.0
    max_deg = max(sr_baseline - sr for sr in all_sr_values)
    trs = 1 - (max_deg / sr_baseline)
    return round(trs, 4)


# ============================================================
# MAIN
# ============================================================
print("Loading tasks and results...")

with open(TASK_FILE) as f:
    tasks = json.load(f)

# build task lookup
task_lookup = {t["task_id"]: t for t in tasks}

# load all raw outputs
raw_files = list(RAW_OUTPUT_DIR.glob("*.json"))
print(f"Found {len(raw_files)} raw output files")
print(f"Total tasks: {len(tasks)}\n")

# ============================================================
# EVALUATE EACH TASK
# ============================================================
evaluated = []
missing   = []

for task in tasks:
    task_id  = task["task_id"]
    out_file = RAW_OUTPUT_DIR / f"{task_id}.json"

    if not out_file.exists():
        missing.append(task_id)
        continue

    with open(out_file) as f:
        raw = json.load(f)

    prediction       = raw.get("raw_output", "")
    reference_answers = task["eval"]["reference_answers"]
    raw_annotation   = task["eval"].get("reference_answer_raw_annotation", "")

    success, tier, details = evaluate_prediction(
        prediction, reference_answers
    )

    evaluated.append({
        "task_id":          task_id,
        "website":          task.get("website", "house_renting"),
        "template":         task["template"],
        "perturbation_type": task.get("perturbation_type", ""),
        "instruction":      task["instruction"],
        "interaction":      task.get("interaction", "none"),
        "prediction":       prediction,
        "ground_truth":     raw_annotation,
        "success":          success,
        "tier_matched":     tier,
        "match_details":    details,
        "mode":             raw.get("mode", "text_only"),
        "model":            raw.get("model", "")
    })

print(f"Evaluated: {len(evaluated)}")
print(f"Missing:   {len(missing)}")
if missing:
    print(f"Missing task IDs: {missing[:5]}{'...' if len(missing) > 5 else ''}")

# ============================================================
# COMPUTE METRICS BY TEMPLATE
# ============================================================
templates = ["classic", "modern", "hidden"]

template_results = {}
for template in templates:
    t_results = [e for e in evaluated if e["template"] == template]
    template_results[template] = {
        "results":      t_results,
        "count":        len(t_results),
        "success_rate": success_rate(t_results)
    }

# ============================================================
# COMPUTE METRICS BY PERTURBATION TYPE
# ============================================================
perturbation_types = sorted(set(e["perturbation_type"] for e in evaluated))
perturbation_results = {}
for ptype in perturbation_types:
    p_results = [e for e in evaluated if e["perturbation_type"] == ptype]
    perturbation_results[ptype] = {
        "count":        len(p_results),
        "success_rate": success_rate(p_results)
    }

# ============================================================
# COMPUTE TEMPORAL DEGRADATION AND TRS
# ============================================================
sr_classic = template_results["classic"]["success_rate"]
sr_modern  = template_results["modern"]["success_rate"]
sr_hidden  = template_results["hidden"]["success_rate"]

deg_classic_to_modern = temporal_degradation(sr_classic, sr_modern)
deg_classic_to_hidden = temporal_degradation(sr_classic, sr_hidden)
deg_modern_to_hidden  = temporal_degradation(sr_modern,  sr_hidden)

trs = compute_trs(sr_classic, [sr_modern, sr_hidden])

# ============================================================
# PRINT RESULTS
# ============================================================
print(f"\n{'='*50}")
print(f"EVALUATION RESULTS: house_renting (text-only)")
print(f"{'='*50}")

print(f"\nSUCCESS RATES BY TEMPLATE:")
print(f"  Classic:  {sr_classic:.1%}  ({template_results['classic']['count']} tasks)")
print(f"  Modern:   {sr_modern:.1%}  ({template_results['modern']['count']} tasks)")
print(f"  Hidden:   {sr_hidden:.1%}  ({template_results['hidden']['count']} tasks)")

print(f"\nTEMPORAL DEGRADATION:")
print(f"  Classic → Modern: {deg_classic_to_modern:+.1%}")
print(f"  Classic → Hidden: {deg_classic_to_hidden:+.1%}")
print(f"  Modern  → Hidden: {deg_modern_to_hidden:+.1%}")

print(f"\nTEMPORAL ROBUSTNESS SCORE (TRS): {trs:.3f}")
print(f"  (1.0 = perfect robustness, 0.0 = complete failure)")

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
    pct = count / len(evaluated) * 100
    print(f"  {tier:<25} {count:3d}  ({pct:.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================
# save per-task results
per_task_path = RESULTS_DIR / "per_task_results.json"
with open(per_task_path, "w") as f:
    json.dump(evaluated, f, indent=2)

# save summary metrics
summary = {
    "model":     evaluated[0]["model"] if evaluated else "",
    "mode":      "text_only",
    "website":   "house_renting",
    "total_tasks":    len(tasks),
    "evaluated_tasks": len(evaluated),
    "missing_tasks":  len(missing),
    "success_rates": {
        "classic": round(sr_classic, 4),
        "modern":  round(sr_modern,  4),
        "hidden":  round(sr_hidden,  4)
    },
    "temporal_degradation": {
        "classic_to_modern": deg_classic_to_modern,
        "classic_to_hidden": deg_classic_to_hidden,
        "modern_to_hidden":  deg_modern_to_hidden
    },
    "trs": trs,
    "perturbation_results": perturbation_results,
    "tier_breakdown": tier_counts
}

summary_path = RESULTS_DIR / "summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved:")
print(f"  Per-task results: {per_task_path}")
print(f"  Summary metrics:  {summary_path}")

if missing:
    print(f"\nWARNING: {len(missing)} tasks not evaluated (no output file)")
    print(f"Re-run infer.py to complete missing tasks")