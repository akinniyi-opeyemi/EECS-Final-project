# scripts/visualize.py
# Generates visualizations for evaluation results.
# Usage:
#   python scripts/visualize.py --website house_renting
#   python scripts/visualize.py --website personal_website
#   python scripts/visualize.py --website all

import json, argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# ============================================================
# ARGUMENT PARSING
# ============================================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "--website",
    required=True,
    choices=["house_renting", "personal_website",
             "job_application", "course_registration", "all"],
    help="Which website to visualize"
)
args = parser.parse_args()

# ============================================================
# CONFIGURATION
# ============================================================
CONFIGS = {
    "house_renting": {
        "summary":   Path("results/metrics/house_renting/summary.json"),
        "per_task":  Path("results/metrics/house_renting/per_task_results.json"),
        "templates": ["classic", "modern", "hidden"],
        "baseline":  "classic",
        "title":     "House Renting",
        "colors":    ["#2ecc71", "#f39c12", "#e74c3c"]
    },
    "personal_website": {
        "summary":   Path("results/metrics/personal_website/summary.json"),
        "per_task":  Path("results/metrics/personal_website/per_task_results.json"),
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
        "baseline":  "raw_html_1998",
        "title":     "Personal Website",
        "colors":    ["#3498db", "#9b59b6", "#e67e22", "#1abc9c"]
    },
    "job_application": {
        "summary":   Path("results/metrics/job_application/summary.json"),
        "per_task":  Path("results/metrics/job_application/per_task_results.json"),
        "templates": ["classic", "modern", "notion"],
        "baseline":  "classic",
        "title":     "Job Application",
        "colors":    ["#2ecc71", "#3498db", "#9b59b6"]
    },
    "course_registration": {
        "summary":   Path("results/metrics/course_registration/summary.json"),
        "per_task":  Path("results/metrics/course_registration/per_task_results.json"),
        "templates": ["2000s", "2010s", "modern"],
        "baseline":  "2000s",
        "title":     "Course Registration",
        "colors":    ["#e74c3c", "#f39c12", "#2ecc71"]
    }
}

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# HELPER: load results for one website
# ============================================================
def load_results(website):
    config = CONFIGS[website]
    if not config["summary"].exists():
        print(f"No results found for {website}. Run evaluate.py first.")
        return None, None
    with open(config["summary"]) as f:
        summary = json.load(f)
    with open(config["per_task"]) as f:
        per_task = json.load(f)
    return summary, per_task


# ============================================================
# CHART 1: Success rate by template (bar chart)
# ============================================================
def plot_success_by_template(website, summary, ax=None):
    config    = CONFIGS[website]
    templates = config["templates"]
    colors    = config["colors"]
    sr        = summary["success_rates"]

    values = [sr.get(t, 0) * 100 for t in templates]
    show   = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(templates, values, color=colors, edgecolor="white",
                  linewidth=1.5, width=0.6)

    # add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{val:.1f}%",
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    # baseline line
    baseline_sr = sr.get(config["baseline"], 0) * 100
    ax.axhline(y=baseline_sr, color="gray", linestyle="--",
               linewidth=1, alpha=0.7, label=f"Baseline ({baseline_sr:.1f}%)")

    ax.set_ylim(0, 110)
    ax.set_ylabel("Success Rate (%)", fontsize=12)
    ax.set_title(f"{config['title']}: Success Rate by Template",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if show:
        plt.tight_layout()
        path = VIZ_DIR / f"{website}_success_by_template.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {path}")


# ============================================================
# CHART 2: Temporal degradation (waterfall style)
# ============================================================
def plot_temporal_degradation(website, summary, ax=None):
    config    = CONFIGS[website]
    templates = config["templates"]
    sr        = summary["success_rates"]

    values = [sr.get(t, 0) * 100 for t in templates]
    show   = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(templates, values, marker="o", linewidth=2.5,
            markersize=10, color="#2c3e50", zorder=3)

    # fill area under line
    ax.fill_between(templates, values,
                    alpha=0.15, color="#2c3e50")

    # annotate each point
    for i, (t, v) in enumerate(zip(templates, values)):
        ax.annotate(
            f"{v:.1f}%",
            (t, v),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=11,
            fontweight="bold"
        )
        if i > 0:
            deg = values[0] - v
            color = "#e74c3c" if deg > 0 else "#27ae60"
            ax.annotate(
                f"{deg:+.1f}%",
                (t, v),
                textcoords="offset points",
                xytext=(0, -18),
                ha="center",
                fontsize=9,
                color=color
            )

    ax.set_ylim(max(0, min(values) - 15), 110)
    ax.set_ylabel("Success Rate (%)", fontsize=12)
    ax.set_title(f"{config['title']}: Temporal Degradation",
                 fontsize=13, fontweight="bold")
    ax.grid(alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if show:
        plt.tight_layout()
        path = VIZ_DIR / f"{website}_temporal_degradation.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {path}")


# ============================================================
# CHART 3: Match tier breakdown (pie chart)
# ============================================================
def plot_tier_breakdown(website, summary, ax=None):
    config = CONFIGS[website]
    tiers  = summary.get("tier_breakdown", {})

    if not tiers:
        return

    labels = list(tiers.keys())
    values = list(tiers.values())
    colors = ["#27ae60", "#2ecc71", "#f39c12",
              "#e67e22", "#e74c3c", "#95a5a6"]

    show = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors[:len(labels)],
        startangle=90,
        pctdistance=0.8
    )
    for text in autotexts:
        text.set_fontsize(9)

    ax.set_title(f"{config['title']}: Match Tier Breakdown",
                 fontsize=13, fontweight="bold")

    if show:
        plt.tight_layout()
        path = VIZ_DIR / f"{website}_tier_breakdown.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {path}")


# ============================================================
# CHART 4: Success by task type (personal_website)
# ============================================================
def plot_task_type_results(website, summary, ax=None):
    config     = CONFIGS[website]
    task_types = summary.get("task_type_results", {})

    if not task_types:
        return

    labels = list(task_types.keys())
    values = [task_types[t]["success_rate"] * 100 for t in labels]
    colors = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c", "#e74c3c"]

    show = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.barh(labels, values,
                   color=colors[:len(labels)],
                   edgecolor="white", linewidth=1.5)

    for bar, val in zip(bars, values):
        ax.text(
            val + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center", fontsize=11, fontweight="bold"
        )

    ax.set_xlim(0, 115)
    ax.set_xlabel("Success Rate (%)", fontsize=12)
    ax.set_title(f"{config['title']}: Success by Task Type",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if show:
        plt.tight_layout()
        path = VIZ_DIR / f"{website}_task_type_results.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {path}")


# ============================================================
# CHART 5: Perturbation type results (house_renting)
# ============================================================
def plot_perturbation_results(website, summary, ax=None):
    config = CONFIGS[website]
    perturb = summary.get("perturbation_results", {})

    if not perturb:
        return

    labels = list(perturb.keys())
    values = [perturb[p]["success_rate"] * 100 for p in labels]
    counts = [perturb[p]["count"] for p in labels]
    colors = ["#27ae60", "#f39c12", "#e67e22",
              "#e74c3c", "#9b59b6", "#3498db"]

    show = ax is None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.barh(labels, values,
                   color=colors[:len(labels)],
                   edgecolor="white", linewidth=1.5)

    for bar, val, cnt in zip(bars, values, counts):
        ax.text(
            val + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%  (n={cnt})",
            va="center", fontsize=10, fontweight="bold"
        )

    ax.set_xlim(0, 120)
    ax.set_xlabel("Success Rate (%)", fontsize=12)
    ax.set_title(f"{config['title']}: Success by Perturbation Type",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if show:
        plt.tight_layout()
        path = VIZ_DIR / f"{website}_perturbation_results.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved: {path}")


# ============================================================
# CHART 6: TRS comparison across all websites
# ============================================================
def plot_trs_comparison(summaries):
    websites = list(summaries.keys())
    trs_vals = [summaries[w]["trs"] for w in websites]
    colors   = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c"]

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(websites, trs_vals,
                  color=colors[:len(websites)],
                  edgecolor="white", linewidth=1.5,
                  width=0.5)

    for bar, val in zip(bars, trs_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{val:.3f}",
            ha="center", va="bottom",
            fontsize=12, fontweight="bold"
        )

    ax.axhline(y=1.0, color="green", linestyle="--",
               linewidth=1, alpha=0.5, label="Perfect robustness")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Temporal Robustness Score (TRS)", fontsize=12)
    ax.set_title("TRS Comparison Across All Websites",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = VIZ_DIR / "trs_comparison_all_websites.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ============================================================
# GENERATE FULL DASHBOARD FOR ONE WEBSITE
# ============================================================
def generate_dashboard(website):
    summary, per_task = load_results(website)
    if summary is None:
        return

    config = CONFIGS[website]
    has_task_types  = bool(summary.get("task_type_results"))
    has_perturbation = bool(summary.get("perturbation_results"))

    # determine layout
    n_charts = 3
    if has_task_types:
        n_charts += 1
    if has_perturbation:
        n_charts += 1

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        f"{config['title']} — Evaluation Dashboard (text-only)",
        fontsize=15, fontweight="bold", y=1.02
    )

    plot_success_by_template(website, summary, ax=axes[0])
    plot_temporal_degradation(website, summary, ax=axes[1])
    plot_tier_breakdown(website, summary, ax=axes[2])

    plt.tight_layout()
    path = VIZ_DIR / f"{website}_dashboard.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved dashboard: {path}")

    # individual charts
    plot_success_by_template(website, summary)
    plot_temporal_degradation(website, summary)
    plot_tier_breakdown(website, summary)

    if has_task_types:
        plot_task_type_results(website, summary)
    if has_perturbation:
        plot_perturbation_results(website, summary)

# ============================================================
# CHART 7: Cross-mode comparison for one website
# ============================================================
def plot_cross_mode_comparison(website):
    """
    Compare text_only, multimodal, vision_only
    success rates across templates.
    """
    config    = CONFIGS[website]
    templates = config["templates"]
    modes     = ["text_only", "multimodal", "vision_only"]
    mode_colors = {
        "text_only":   "#2ecc71",
        "multimodal":  "#3498db",
        "vision_only": "#e74c3c"
    }

    # load summaries for each mode
    summaries = {}
    for mode in modes:
        summary_path = Path(f"results/metrics/{website}/{mode}/summary.json")
        if summary_path.exists():
            with open(summary_path) as f:
                summaries[mode] = json.load(f)
        else:
            print(f"  No results for {website}/{mode}, skipping")

    if len(summaries) < 2:
        print(f"  Need at least 2 modes to compare")
        return

    available_modes = list(summaries.keys())

    # ---- Chart A: grouped bar chart by template ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        f"{config['title']} — Cross-Mode Comparison",
        fontsize=15, fontweight="bold"
    )

    # grouped bars
    ax = axes[0]
    x    = np.arange(len(templates))
    width = 0.25
    offsets = np.linspace(
        -(len(available_modes)-1)*width/2,
        (len(available_modes)-1)*width/2,
        len(available_modes)
    )

    for i, mode in enumerate(available_modes):
        sr = summaries[mode]["success_rates"]
        values = [sr.get(t, 0) * 100 for t in templates]
        bars = ax.bar(
            x + offsets[i], values,
            width, label=mode.replace("_", " "),
            color=mode_colors[mode],
            edgecolor="white", linewidth=1.2
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f"{val:.0f}%",
                ha="center", va="bottom",
                fontsize=8, fontweight="bold"
            )

    ax.set_xticks(x)
    ax.set_xticklabels(templates, rotation=15, ha="right")
    ax.set_ylim(0, 115)
    ax.set_ylabel("Success Rate (%)", fontsize=12)
    ax.set_title("Success Rate by Template and Mode", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ---- Chart B: TRS comparison ----
    ax2 = axes[1]
    trs_values = [summaries[m]["trs"] for m in available_modes]
    mode_labels = [m.replace("_", " ") for m in available_modes]
    colors = [mode_colors[m] for m in available_modes]

    bars = ax2.bar(
        mode_labels, trs_values,
        color=colors, edgecolor="white",
        linewidth=1.5, width=0.4
    )

    for bar, val in zip(bars, trs_values):
        ax2.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.01,
            f"{val:.3f}",
            ha="center", va="bottom",
            fontsize=12, fontweight="bold"
        )

    ax2.axhline(
        y=1.0, color="gray", linestyle="--",
        linewidth=1, alpha=0.5,
        label="Perfect robustness"
    )
    ax2.set_ylim(0, 1.15)
    ax2.set_ylabel("TRS", fontsize=12)
    ax2.set_title("Temporal Robustness Score by Mode", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(axis="y", alpha=0.3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    path = VIZ_DIR / f"{website}_cross_mode_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

    # ---- Print summary table ----
    print(f"\nCross-mode summary for {website}:")
    print(f"{'Template':<20}", end="")
    for mode in available_modes:
        print(f"{mode.replace('_',' '):<15}", end="")
    print()
    print("-" * (20 + 15 * len(available_modes)))
    for t in templates:
        print(f"{t:<20}", end="")
        for mode in available_modes:
            sr = summaries[mode]["success_rates"].get(t, 0)
            val_str = f"{sr:.1%}"
            print(f"{val_str:<15}", end="")
        print()
    print(f"\n{'TRS':<20}", end="")
    for mode in available_modes:
        print(f"{summaries[mode]['trs']:<15.3f}", end="")
    print()


# ============================================================
# MAIN
# ============================================================
print(f"Generating visualizations for: {args.website}\n")

if args.website == "all":
    summaries = {}
    for website in ["house_renting", "personal_website",
                    "job_application", "course_registration"]:
        summary, _ = load_results(website)
        if summary:
            generate_dashboard(website)
            summaries[website] = summary
        # cross-mode comparison for each website
        plot_cross_mode_comparison(website)
    if len(summaries) > 1:
        plot_trs_comparison(summaries)
        print(f"\nCross-website comparison saved")
else:
    generate_dashboard(args.website)
    plot_cross_mode_comparison(args.website)

print(f"\nAll visualizations saved to: {VIZ_DIR}")