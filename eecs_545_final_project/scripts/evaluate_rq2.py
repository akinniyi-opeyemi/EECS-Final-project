# scripts/evaluate_rq2.py
# Evaluates RQ II intervention strategies and compares
# recovery rates against vanilla baseline.
# Usage:
#   python scripts/evaluate_rq2.py --website house_renting --mode vision_only --agent qwen_vl
#   python scripts/evaluate_rq2.py --website house_renting --mode vision_only --agent uitars

import json, argparse
from pathlib import Path
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument("--website", required=True,
    choices=["house_renting", "personal_website", "course_registration"])
parser.add_argument("--mode", required=True,
    choices=["text_only", "multimodal", "vision_only"])
parser.add_argument("--agent", default="qwen_vl",
    choices=["gpt_oss", "qwen_vl", "uitars", "qwen25", "internvl"],
    help="Which agent to evaluate")
args = parser.parse_args()

FUZZY_THRESHOLD    = 0.75
SEMANTIC_THRESHOLD = 0.80

print("Loading semantic similarity model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Ready.\n")

TASK_FILES = {
    "house_renting":    Path("house-renting-eval/tasks.json"),
    "personal_website": Path("Personal Website/tasks/test.raw.json"),
    "course_registration": Path("course_registration/tasks.json")
}

def evaluate_prediction(prediction, reference_answers):
    if not prediction:
        return False, "no_prediction"
    prediction = prediction.strip()
    exact = reference_answers.get("exact_match")
    if exact:
        if prediction.lower() == exact.lower():
            return True, "exact_match"
        if exact.lower() in prediction.lower():
            return True, "exact_match_contained"
    must = reference_answers.get("must_include") or []
    if must:
        if all(kw.lower() in prediction.lower() for kw in must):
            return True, "must_include"
    fuzzy_refs = reference_answers.get("fuzzy_match") or []
    for ref in fuzzy_refs:
        score = fuzz.ratio(prediction.lower(), ref.lower()) / 100
        if score >= FUZZY_THRESHOLD:
            return True, "fuzzy_string"
    if fuzzy_refs:
        pred_emb = embedder.encode(prediction, convert_to_tensor=True)
        for ref in fuzzy_refs:
            ref_emb = embedder.encode(ref, convert_to_tensor=True)
            sim = float(util.cos_sim(pred_emb, ref_emb))
            if sim >= SEMANTIC_THRESHOLD:
                return True, "semantic_match"
    return False, "no_match"

with open(TASK_FILES[args.website]) as f:
    tasks = json.load(f)
task_lookup = {str(t["task_id"]): t for t in tasks}

# load vanilla metrics (try agent subfolder first, then legacy path)
vanilla_metrics = Path(
    f"results/metrics/{args.website}/{args.mode}/{args.agent}/per_task_results.json"
)
if not vanilla_metrics.exists():
    vanilla_metrics = Path(
        f"results/metrics/{args.website}/{args.mode}/per_task_results.json"
    )

with open(vanilla_metrics) as f:
    vanilla_results = json.load(f)

vanilla_failed  = {r["task_id"] for r in vanilla_results if not r["success"]}
vanilla_success = {r["task_id"] for r in vanilla_results if r["success"]}

print(f"Website: {args.website}")
print(f"Mode:    {args.mode}")
print(f"Agent:   {args.agent}")
print(f"Vanilla failed:    {len(vanilla_failed)}")
print(f"Vanilla succeeded: {len(vanilla_success)}")
print()

strategies = ["memory", "cot"]
strategy_results = {}

for strategy in strategies:
    # try new path with agent first, fall back to legacy
    output_dir = Path(
        f"results/raw_outputs/{args.website}/rq2_{strategy}_{args.mode}_{args.agent}"
    )
    if not output_dir.exists():
        output_dir = Path(
            f"results/raw_outputs/{args.website}/rq2_{strategy}_{args.mode}"
        )

    if not output_dir.exists():
        print(f"No results for strategy {strategy}, skipping")
        continue

    files = list(output_dir.glob("*.json"))
    if not files:
        print(f"No output files for strategy {strategy}, skipping")
        continue

    evaluated    = []
    recovered    = []
    still_failed = []
    hallucinated = []

    for f in files:
        with open(f) as fp:
            result = json.load(fp)

        task_id    = result["task_id"]
        prediction = result.get("raw_output", "")
        task       = task_lookup.get(task_id, {})
        if not task:
            continue

        ref_answers  = task["eval"]["reference_answers"]
        raw_gt       = task["eval"].get("reference_answer_raw_annotation", "")
        perturbation = task.get("perturbation_type", "")
        template     = task.get("template", "")

        success, tier = evaluate_prediction(prediction, ref_answers)

        entry = {
            "task_id":            task_id,
            "template":           template,
            "perturbation_type":  perturbation,
            "instruction":        task.get("instruction", ""),
            "prediction":         prediction,
            "ground_truth":       raw_gt,
            "success":            success,
            "tier":               tier,
            "was_vanilla_failed": task_id in vanilla_failed
        }

        evaluated.append(entry)

        if success:
            recovered.append(entry)
        else:
            still_failed.append(entry)
            not_found_phrases = [
                "not visible", "not found", "not available",
                "not specified", "not listed", "not shown"
            ]
            pred_lower = (prediction or "").lower()
            is_conservative = any(p in pred_lower for p in not_found_phrases)
            if not is_conservative and prediction:
                hallucinated.append(entry)

    strategy_results[strategy] = {
        "evaluated":    evaluated,
        "recovered":    recovered,
        "still_failed": still_failed,
        "hallucinated": hallucinated
    }

    print(f"Strategy: {strategy.upper()}")
    print(f"  Evaluated:    {len(evaluated)}")
    print(f"  Recovered:    {len(recovered)} ({len(recovered)/len(evaluated)*100:.1f}%)")
    print(f"  Still failed: {len(still_failed)}")
    print(f"  Hallucinated: {len(hallucinated)}")
    print()

print(f"\n{'='*55}")
print(f"RQ II COMPARISON: {args.website} ({args.mode}, {args.agent})")
print(f"{'='*55}")
print(f"{'Strategy':<15} {'Recovered':<12} {'Rate':<10} {'Hallucinated'}")
print(f"{'-'*55}")
print(f"{'vanilla':<15} {'0':<12} {'0.0%':<10} 0")

for strategy, data in strategy_results.items():
    n    = len(data["evaluated"])
    rec  = len(data["recovered"])
    hall = len(data["hallucinated"])
    rate = rec/n*100 if n > 0 else 0
    print(f"{strategy:<15} {rec:<12} {rate:.1f}%{'':4} {hall}")

print(f"\nRECOVERY RATE BY PERTURBATION TYPE:")
print(f"{'Perturbation':<25} {'vanilla':<12}", end="")
for strategy in strategy_results:
    print(f"{strategy:<12}", end="")
print()
print("-" * (25 + 12 + 12 * len(strategy_results)))

perturbation_types = sorted(set(
    e["perturbation_type"]
    for data in strategy_results.values()
    for e in data["evaluated"]
))

for ptype in perturbation_types:
    print(f"{ptype:<25} {'0%':<12}", end="")
    for strategy, data in strategy_results.items():
        p_evals = [e for e in data["evaluated"] if e["perturbation_type"] == ptype]
        p_rec   = [e for e in p_evals if e["success"]]
        rate    = len(p_rec)/len(p_evals)*100 if p_evals else 0
        print(f"{rate:.0f}%{'':<9}", end="")
    print()

results_dir = Path(f"results/metrics/{args.website}/rq2_{args.mode}_{args.agent}")
results_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "website":        args.website,
    "mode":           args.mode,
    "agent":          args.agent,
    "vanilla_failed": len(vanilla_failed),
    "strategies":     {}
}

for strategy, data in strategy_results.items():
    n   = len(data["evaluated"])
    rec = len(data["recovered"])
    summary["strategies"][strategy] = {
        "evaluated":          n,
        "recovered":          rec,
        "recovery_rate":      round(rec/n, 4) if n > 0 else 0,
        "hallucinated":       len(data["hallucinated"]),
        "hallucination_rate": round(len(data["hallucinated"])/n, 4) if n > 0 else 0
    }
    per_task_path = results_dir / f"{strategy}_per_task.json"
    with open(per_task_path, "w") as f:
        json.dump(data["evaluated"], f, indent=2)

summary_path = results_dir / "summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved to: {results_dir}")