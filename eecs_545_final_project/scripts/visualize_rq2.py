# scripts/visualize_rq2.py
# Generates visualizations for RQ II intervention results.
# Usage:
#   python scripts/visualize_rq2.py --website house_renting --mode vision_only

import json, argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument("--website", required=True,
    choices=["house_renting", "personal_website"])
parser.add_argument("--mode", required=True,
    choices=["text_only", "multimodal", "vision_only"])
args = parser.parse_args()

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD RESULTS
# ============================================================
summary_path = Path(
    f"results/metrics/{args.website}/rq2_{args.mode}/summary.json"
)
if not summary_path.exists():
    print(f"No RQ II results found. Run evaluate_rq2.py first.")
    exit(1)

with open(summary_path) as f:
    summary = json.load(f)

strategies    = list(summary["strategies"].keys())
vanilla_failed = summary["vanilla_failed"]

# ============================================================
# CHART 1: Recovery rate comparison
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle(
    f"RQ II: Test-Time Interventions — {args.website.replace('_',' ').title()} ({args.mode.replace('_',' ')})",
    fontsize=14, fontweight="bold"
)

# recovery rates
ax = axes[0]
strategy_labels = ["vanilla"] + strategies
recovery_rates  = [0.0] + [
    summary["strategies"][s]["recovery_rate"] * 100
    for s in strategies
]
colors = ["#95a5a6", "#3498db", "#e67e22"]

bars = ax.bar(strategy_labels, recovery_rates,
              color=colors[:len(strategy_labels)],
              edgecolor="white", linewidth=1.5,
              width=0.5)

for bar, val in zip(bars, recovery_rates):
    ax.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.5,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=12, fontweight="bold"
    )

ax.set_ylim(0, 100)
ax.set_ylabel("Recovery Rate (%)", fontsize=12)
ax.set_title("Recovery Rate\n(% of vanilla failures recovered)", fontsize=11)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# hallucination rates
ax2 = axes[1]
hallucination_rates = [0.0] + [
    summary["strategies"][s]["hallucination_rate"] * 100
    for s in strategies
]
colors2 = ["#95a5a6", "#e74c3c", "#c0392b"]

bars2 = ax2.bar(strategy_labels, hallucination_rates,
                color=colors2[:len(strategy_labels)],
                edgecolor="white", linewidth=1.5,
                width=0.5)

for bar, val in zip(bars2, hallucination_rates):
    ax2.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.5,
        f"{val:.1f}%",
        ha="center", va="bottom",
        fontsize=12, fontweight="bold"
    )

ax2.set_ylim(0, 100)
ax2.set_ylabel("Hallucination Rate (%)", fontsize=12)
ax2.set_title("Hallucination Rate\n(% giving wrong specific answer)", fontsize=11)
ax2.grid(axis="y", alpha=0.3)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

# net improvement (recovery - hallucination)
ax3 = axes[2]
net_improvements = [0.0] + [
    (summary["strategies"][s]["recovery_rate"] -
     summary["strategies"][s]["hallucination_rate"]) * 100
    for s in strategies
]
net_colors = ["#95a5a6"] + [
    "#27ae60" if v >= 0 else "#e74c3c"
    for v in net_improvements[1:]
]

bars3 = ax3.bar(strategy_labels, net_improvements,
                color=net_colors,
                edgecolor="white", linewidth=1.5,
                width=0.5)

for bar, val in zip(bars3, net_improvements):
    ax3.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + (0.5 if val >= 0 else -2),
        f"{val:+.1f}%",
        ha="center", va="bottom",
        fontsize=12, fontweight="bold"
    )

ax3.axhline(y=0, color="black", linewidth=0.8, alpha=0.5)
ax3.set_ylabel("Net Improvement (%)", fontsize=12)
ax3.set_title("Net Improvement\n(recovery - hallucination)", fontsize=11)
ax3.grid(axis="y", alpha=0.3)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

plt.tight_layout()
path = VIZ_DIR / f"rq2_{args.website}_{args.mode}_comparison.png"
plt.savefig(path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {path}")

# ============================================================
# CHART 2: Recovery by perturbation type
# ============================================================
# load per-task results for breakdown
per_task_data = {}
for strategy in strategies:
    per_task_path = Path(
        f"results/metrics/{args.website}/rq2_{args.mode}/{strategy}_per_task.json"
    )
    if per_task_path.exists():
        with open(per_task_path) as f:
            per_task_data[strategy] = json.load(f)

if per_task_data:
    perturbation_types = sorted(set(
        e["perturbation_type"]
        for data in per_task_data.values()
        for e in data
    ))

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle(
        f"RQ II: Recovery Rate by Perturbation Type\n{args.website.replace('_',' ').title()} ({args.mode.replace('_',' ')})",
        fontsize=13, fontweight="bold"
    )

    x      = np.arange(len(perturbation_types))
    width  = 0.35
    colors = ["#3498db", "#e67e22"]

    for i, strategy in enumerate(strategies):
        data = per_task_data.get(strategy, [])
        rates = []
        for ptype in perturbation_types:
            p_data = [e for e in data if e["perturbation_type"] == ptype]
            p_rec  = [e for e in p_data if e["success"]]
            rate   = len(p_rec)/len(p_data)*100 if p_data else 0
            rates.append(rate)

        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, rates, width,
                      label=strategy, color=colors[i],
                      edgecolor="white", linewidth=1.2)

        for bar, val in zip(bars, rates):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.5,
                    f"{val:.0f}%",
                    ha="center", va="bottom", fontsize=9
                )

    ax.set_xticks(x)
    ax.set_xticklabels(perturbation_types, rotation=15, ha="right")
    ax.set_ylim(0, 110)
    ax.set_ylabel("Recovery Rate (%)", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path2 = VIZ_DIR / f"rq2_{args.website}_{args.mode}_by_perturbation.png"
    plt.savefig(path2, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path2}")

print(f"\nRQ II visualizations saved to: {VIZ_DIR}")