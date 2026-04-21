# scripts/visualize_agent_dashboard.py
# Comprehensive cross-agent dashboard for benchmark presentation.
# Usage: python scripts/visualize_agent_dashboard.py

import json
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONFIGURATION
# ============================================================
AGENTS = {
    "gpt_oss":  {"label": "GPT-oss-120B",   "color": "#3266ad", "marker": "o", "ls": "-"},
    "qwen_vl":  {"label": "Qwen3-VL-30B",   "color": "#d85a30", "marker": "^", "ls": "-"},
    "uitars":   {"label": "UI-TARS-7B",      "color": "#7f77dd", "marker": "D", "ls": "-"},
    "qwen25":   {"label": "Qwen2.5-VL-7B",  "color": "#1d9e75", "marker": "s", "ls": "-"},
    "internvl": {"label": "InternVL2-8B",    "color": "#ba7517", "marker": "P", "ls": "-"},
}

VISION_AGENTS = ["qwen_vl", "uitars", "qwen25", "internvl"]

WEBSITES = {
    "house_renting": {
        "title":     "House Renting",
        "templates": ["classic", "modern", "hidden"],
        "baseline":  "classic",
        "xlabels":   ["classic", "modern", "hidden"],
    },
    "personal_website": {
        "title":     "Personal Website",
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
        "baseline":  "raw_html_1998",
        "xlabels":   ["raw\n1998", "hugo\npapermod", "notion", "jekyll\nalfolio"],
    },
}

def load_summary(website, mode, agent):
    path = Path(f"results/metrics/{website}/{mode}/{agent}/summary.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    path_old = Path(f"results/metrics/{website}/{mode}/summary.json")
    if path_old.exists():
        with open(path_old) as f:
            return json.load(f)
    return None


# ============================================================
# FIGURE: 2x2 dashboard
# Row 1: vision_only line charts (house_renting, personal_website)
# Row 2: TRS bar charts (vision_only, multimodal)
# ============================================================
fig = plt.figure(figsize=(18, 12))
fig.suptitle(
    "GUI Agent Temporal Robustness: Cross-Agent Comparison",
    fontsize=16, fontweight="bold", y=1.01
)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.3)

# ============================================================
# ROW 1: Per-template success rate lines (vision_only)
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[0, col])
    templates = wconfig["templates"]
    xlabels   = wconfig["xlabels"]
    x         = list(range(len(templates)))

    for agent_key in VISION_AGENTS:
        s = load_summary(website_key, "vision_only", agent_key)
        if not s:
            continue
        cfg    = AGENTS[agent_key]
        values = [s["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(
            x, values,
            color=cfg["color"], linestyle=cfg["ls"],
            marker=cfg["marker"], linewidth=2.5, markersize=8,
            label=cfg["label"], zorder=3
        )
        ax.annotate(
            f"{values[-1]:.0f}%",
            (len(templates) - 1, values[-1]),
            textcoords="offset points", xytext=(8, 0),
            fontsize=9, color=cfg["color"], fontweight="bold"
        )

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=10)
    ax.set_ylim(0, 115)
    ax.set_ylabel("success rate (%)", fontsize=11)
    ax.set_title(
        f"{wconfig['title']} — vision only",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 2: TRS bar charts
# Left: vision_only TRS by agent and website
# Right: multimodal TRS by agent and website
# ============================================================
modes_config = {
    "vision_only": {"title": "TRS by Agent (vision only)",   "col": 0},
    "multimodal":  {"title": "TRS by Agent (multimodal)",    "col": 1},
}

for mode, mconfig in modes_config.items():
    ax = fig.add_subplot(gs[1, mconfig["col"]])

    agents_to_show = VISION_AGENTS
    n_agents       = len(agents_to_show)
    n_websites     = len(WEBSITES)
    width          = 0.35
    x              = np.arange(n_agents)

    website_keys   = list(WEBSITES.keys())
    website_colors = ["#4a90d9", "#e07b39"]
    website_labels = ["House Renting", "Personal Website"]

    for wi, (website_key, wlabel, wcolor) in enumerate(
            zip(website_keys, website_labels, website_colors)):
        trs_vals = []
        for agent_key in agents_to_show:
            s = load_summary(website_key, mode, agent_key)
            trs_vals.append(s["trs"] if s else 0)

        offset = (wi - 0.5) * width
        bars = ax.bar(
            x + offset, trs_vals, width,
            color=wcolor, alpha=0.85,
            label=wlabel,
            edgecolor="white", linewidth=1.2,
            zorder=3
        )
        for bar, val in zip(bars, trs_vals):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + 0.01,
                    f"{val:.3f}",
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold"
                )

    ax.axhline(y=1.0, color="gray", linestyle="--",
               linewidth=1, alpha=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [AGENTS[a]["label"] for a in agents_to_show],
        fontsize=9, rotation=15, ha="right"
    )
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("TRS", fontsize=11)
    ax.set_title(mconfig["title"], fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout()
path = VIZ_DIR / "agent_comprehensive_dashboard.png"
plt.savefig(path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {path}")