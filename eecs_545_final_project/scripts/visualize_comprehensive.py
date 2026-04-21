# scripts/visualize_comprehensive.py
# Comprehensive dashboard: 3 line charts + 3 TRS bar charts
# Usage: python scripts/visualize_comprehensive.py

import json
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from pathlib import Path

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONFIGURATION
# ============================================================
WEBSITES = {
    "house_renting": {
        "title":     "House Renting",
        "templates": ["classic", "modern", "hidden"],
        "baseline":  "classic",
        "modes": {
            "text_only":   Path("results/metrics/house_renting/text_only/summary.json"),
            "multimodal":  Path("results/metrics/house_renting/multimodal/summary.json"),
            "vision_only": Path("results/metrics/house_renting/vision_only/summary.json"),
        },
        "rq2_per_task": {
            "memory": Path("results/metrics/house_renting/rq2_vision_only/memory_per_task.json"),
            "cot":    Path("results/metrics/house_renting/rq2_vision_only/cot_per_task.json"),
        }
    },
    "personal_website": {
        "title":     "Personal Website",
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
        "baseline":  "raw_html_1998",
        "modes": {
            "text_only":   Path("results/metrics/personal_website/text_only/summary.json"),
            "multimodal":  Path("results/metrics/personal_website/multimodal/summary.json"),
            "vision_only": Path("results/metrics/personal_website/vision_only/summary.json"),
        },
        "rq2_per_task": {
            "memory": Path("results/metrics/personal_website/rq2_vision_only/memory_per_task.json"),
            "cot":    Path("results/metrics/personal_website/rq2_vision_only/cot_per_task.json"),
        }
    },
    "course_registration": {
        "title":     "Course Registration",
        "templates": ["2000s", "2010s", "modern"],
        "baseline":  "2000s",
        "modes": {
            "text_only":   Path("results/metrics/course_registration/text_only/summary.json"),
            "multimodal":  Path("results/metrics/course_registration/multimodal/summary.json"),
            "vision_only": Path("results/metrics/course_registration/vision_only/summary.json"),
        },
        "rq2_per_task": {
            "memory": Path("results/metrics/course_registration/rq2_vision_only/memory_per_task.json"),
            "cot":    Path("results/metrics/course_registration/rq2_vision_only/cot_per_task.json"),
        }
    }
}

MODE_COLORS = {
    "text_only":      "#3266ad",
    "multimodal":     "#1d9e75",
    "vision_only":    "#d85a30",
    "vision+memory":  "#7f77dd",
    "vision+cot":     "#ba7517",
}

MODE_STYLES = {
    "text_only":     {"linestyle": "-",  "marker": "o",  "linewidth": 2.5},
    "multimodal":    {"linestyle": "-",  "marker": "s",  "linewidth": 2.5},
    "vision_only":   {"linestyle": "-",  "marker": "^",  "linewidth": 2.5},
    "vision+memory": {"linestyle": "--", "marker": "D",  "linewidth": 2.0},
    "vision+cot":    {"linestyle": "--", "marker": "P",  "linewidth": 2.0},
}

# ============================================================
# HELPERS
# ============================================================
def load_summary(path):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return None

def load_per_task(path):
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return []

def compute_trs(sr_by_template, templates, baseline):
    sr_base = sr_by_template.get(baseline, 0)
    others  = [sr_by_template.get(t, 0)
               for t in templates if t != baseline]
    if sr_base == 0 or not others:
        return 1.0
    max_deg = max(sr_base - sr for sr in others)
    return round(1 - (max_deg / sr_base), 4)

def get_intervention_rates(config, strategy):
    vision_summary = load_summary(config["modes"]["vision_only"])
    if not vision_summary:
        return {}

    per_task = load_per_task(config["rq2_per_task"].get(strategy, Path("")))
    if not per_task:
        return vision_summary["success_rates"]

    recovered_by_template = {}
    total_by_template     = {}
    for item in per_task:
        t = item.get("template", "")
        if t not in total_by_template:
            total_by_template[t]     = 0
            recovered_by_template[t] = 0
        total_by_template[t] += 1
        if item.get("success"):
            recovered_by_template[t] += 1

    base_sr  = vision_summary["success_rates"]
    adjusted = {}
    for t in config["templates"]:
        base   = base_sr.get(t, 0)
        n_fail = total_by_template.get(t, 0)
        n_rec  = recovered_by_template.get(t, 0)
        if n_fail > 0:
            boost = n_rec / n_fail * (1 - base)
            adjusted[t] = min(1.0, base + boost)
        else:
            adjusted[t] = base
    return adjusted

def shorten_label(t):
    t = t.replace("_html_1998", "\n1998")
    t = t.replace("hugo_papermod", "hugo\npapermod")
    t = t.replace("jekyll_alfolio", "jekyll\nalfolio")
    t = t.replace("_", " ")
    return t

def has_any_data(config):
    for path in config["modes"].values():
        if Path(path).exists():
            return True
    return False

# ============================================================
# FIGURE: 2 rows x 3 cols
# Row 1: line charts (one per website)
# Row 2: TRS bar charts (one per website)
# ============================================================
fig, axes = plt.subplots(
    2, 3,
    figsize=(20, 12),
    gridspec_kw={"height_ratios": [1.3, 1], "hspace": 0.45, "wspace": 0.3}
)

fig.suptitle(
    "GUI agent robustness: input modes and test-time interventions",
    fontsize=16, fontweight="bold", y=0.98
)

websites_list = list(WEBSITES.items())

# ============================================================
# ROW 1: line charts
# ============================================================
for col, (website_key, config) in enumerate(websites_list):
    ax        = axes[0, col]
    templates = config["templates"]
    x         = list(range(len(templates)))
    labels    = [shorten_label(t) for t in templates]
    has_data  = has_any_data(config)

    if not has_data:
        ax.set_facecolor("#f8f8f8")
        ax.text(
            0.5, 0.5,
            "pending annotation",
            ha="center", va="center",
            fontsize=13,
            color="#aaaaaa",
            style="italic",
            transform=ax.transAxes
        )
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 115)
        ax.set_ylabel("success rate (%)", fontsize=11)
        ax.set_title(config["title"], fontsize=13, fontweight="bold")
        ax.grid(alpha=0.15, axis="y")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        continue

    all_lines = {}

    for mode in ["text_only", "multimodal", "vision_only"]:
        s = load_summary(config["modes"][mode])
        if s:
            all_lines[mode] = [
                s["success_rates"].get(t, 0) * 100
                for t in templates
            ]

    for strategy, key in [("memory", "vision+memory"), ("cot", "vision+cot")]:
        adj = get_intervention_rates(config, strategy)
        if adj:
            all_lines[key] = [adj.get(t, 0) * 100 for t in templates]

    for mode_key, values in all_lines.items():
        style = MODE_STYLES[mode_key]
        color = MODE_COLORS[mode_key]
        ax.plot(
            x, values,
            color=color,
            linestyle=style["linestyle"],
            marker=style["marker"],
            linewidth=style["linewidth"],
            markersize=8,
            zorder=3
        )
        ax.annotate(
            f"{values[-1]:.0f}%",
            (len(templates) - 1, values[-1]),
            textcoords="offset points",
            xytext=(9, 0),
            fontsize=9,
            color=color,
            fontweight="bold"
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("success rate (%)", fontsize=11)
    ax.set_title(config["title"], fontsize=13, fontweight="bold")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 2: TRS bar charts (one per website)
# ============================================================
modes_order = [
    "text_only", "multimodal", "vision_only",
    "vision+memory", "vision+cot"
]
mode_labels = [
    "text only", "multimodal", "vision only",
    "vision+memory", "vision+CoT"
]

for col, (website_key, config) in enumerate(websites_list):
    ax        = axes[1, col]
    templates = config["templates"]
    baseline  = config["baseline"]
    has_data  = has_any_data(config)

    if not has_data:
        ax.set_facecolor("#f8f8f8")
        ax.text(
            0.5, 0.5,
            "pending annotation",
            ha="center", va="center",
            fontsize=13,
            color="#aaaaaa",
            style="italic",
            transform=ax.transAxes
        )
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("TRS", fontsize=11)
        ax.set_title(f"{config['title']}: TRS",
                     fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        continue

    n        = len(modes_order)
    width    = 0.6
    x_pos    = np.arange(n)
    trs_vals = []

    for mode in modes_order:
        if mode in ["text_only", "multimodal", "vision_only"]:
            s = load_summary(config["modes"].get(mode, Path("")))
            trs_vals.append(s["trs"] if s else 0)
        else:
            strategy = mode.split("+")[1]
            adj = get_intervention_rates(config, strategy)
            trs_vals.append(compute_trs(adj, templates, baseline) if adj else 0)

    bars = ax.bar(
        x_pos, trs_vals, width,
        color=[MODE_COLORS[m] for m in modes_order],
        edgecolor="white", linewidth=1.2, zorder=3
    )
    for bar, val in zip(bars, trs_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.01, f"{val:.3f}",
            ha="center", va="bottom",
            fontsize=8, fontweight="bold"
        )

    ax.axhline(y=1.0, color="gray", linestyle="--", linewidth=1, alpha=0.4)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        [m.replace("_", " ").replace("vision+", "v+") for m in modes_order],
        fontsize=8
    )
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("TRS", fontsize=11)
    ax.set_title(f"{config['title']}: TRS", fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# SHARED LEGEND (top)
# ============================================================
legend_handles = [
    mlines.Line2D([], [], color=MODE_COLORS["text_only"],
                  linestyle="-", marker="o", linewidth=2,
                  label="text only"),
    mlines.Line2D([], [], color=MODE_COLORS["multimodal"],
                  linestyle="-", marker="s", linewidth=2,
                  label="multimodal"),
    mlines.Line2D([], [], color=MODE_COLORS["vision_only"],
                  linestyle="-", marker="^", linewidth=2,
                  label="vision only (vanilla)"),
    mlines.Line2D([], [], color=MODE_COLORS["vision+memory"],
                  linestyle="--", marker="D", linewidth=2,
                  label="vision + memory"),
    mlines.Line2D([], [], color=MODE_COLORS["vision+cot"],
                  linestyle="--", marker="P", linewidth=2,
                  label="vision + CoT"),
]

fig.legend(
    handles=legend_handles,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.965),
    ncol=5,
    fontsize=10,

    frameon=False
)

# ============================================================
# SAVE
# ============================================================
path = VIZ_DIR / "comprehensive_dashboard.png"
plt.savefig(path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {path}")
print(f"Open:  open {path}")