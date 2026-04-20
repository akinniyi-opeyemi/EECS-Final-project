# scripts/visualize_agents.py
# Cross-agent comparison visualization.
# Usage: python scripts/visualize_agents.py

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
AGENTS = {
    "gpt_oss":  {"label": "GPT-oss-120B",   "color": "#3266ad", "marker": "o",
                 "tier": "text-only", "modes": ["text_only"]},
    "qwen_vl":  {"label": "Qwen3-VL-30B",   "color": "#d85a30", "marker": "^",
                 "tier": "general",   "modes": ["text_only", "multimodal", "vision_only"]},
    "uitars":   {"label": "UI-TARS-7B",      "color": "#7f77dd", "marker": "D",
                 "tier": "GUI-specialized", "modes": ["multimodal", "vision_only"]},
    "qwen25":   {"label": "Qwen2.5-VL-7B",  "color": "#1d9e75", "marker": "s",
                 "tier": "general",   "modes": ["multimodal", "vision_only"]},
    "internvl": {"label": "InternVL2-8B",    "color": "#ba7517", "marker": "P",
                 "tier": "general",   "modes": ["multimodal", "vision_only"]},
}

WEBSITES = {
    "house_renting": {
        "title":     "House Renting",
        "templates": ["classic", "modern", "hidden"],
        "baseline":  "classic",
    },
    "personal_website": {
        "title":     "Personal Website",
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
        "baseline":  "raw_html_1998",
    },
}

MODES = {
    "text_only":   "text only",
    "vision_only": "vision only",
}

# ============================================================
# HELPERS
# ============================================================
def load_summary(website, mode, agent):
    # new structure with agent subfolder
    path = Path(f"results/metrics/{website}/{mode}/{agent}/summary.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    # old structure without agent subfolder (gpt_oss, qwen_vl)
    path_old = Path(f"results/metrics/{website}/{mode}/summary.json")
    if path_old.exists():
        with open(path_old) as f:
            return json.load(f)
    return None

def short_label(t):
    return t.replace("_html_1998", "\n1998")\
             .replace("hugo_papermod", "hugo\npapermod")\
             .replace("jekyll_alfolio", "jekyll\nalfolio")\
             .replace("_", " ")

# ============================================================
# FIGURE 1: TRS comparison across agents (main figure)
# ============================================================
def plot_agent_trs_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        "temporal robustness score across agents and websites",
        fontsize=15, fontweight="bold", y=1.02
    )

    for col, (website_key, config) in enumerate(WEBSITES.items()):
        ax = axes[col]

        agents_found = []
        trs_text     = []
        trs_vision   = []

        for agent_key, agent_cfg in AGENTS.items():
            s_text   = load_summary(website_key, "text_only",   agent_key)
            s_vision = load_summary(website_key, "vision_only", agent_key)

            if s_text or s_vision:
                agents_found.append(agent_key)
                trs_text.append(s_text["trs"]   if s_text   else None)
                trs_vision.append(s_vision["trs"] if s_vision else None)

        x      = np.arange(len(agents_found))
        width  = 0.35
        colors = [AGENTS[a]["color"] for a in agents_found]

        bars_t = []
        bars_v = []

        for i, (agent_key, tv, vv) in enumerate(
                zip(agents_found, trs_text, trs_vision)):
            color = AGENTS[agent_key]["color"]
            if tv is not None:
                b = ax.bar(
                    i - width/2, tv, width,
                    color=color, alpha=0.6,
                    edgecolor="white", linewidth=1.2,
                    zorder=3
                )
                ax.text(
                    i - width/2, tv + 0.01,
                    f"{tv:.3f}",
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold"
                )
            if vv is not None:
                b = ax.bar(
                    i + width/2, vv, width,
                    color=color, alpha=1.0,
                    edgecolor="white", linewidth=1.2,
                    zorder=3
                )
                ax.text(
                    i + width/2, vv + 0.01,
                    f"{vv:.3f}",
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold"
                )

        ax.axhline(
            y=1.0, color="gray", linestyle="--",
            linewidth=1, alpha=0.4, label="perfect robustness"
        )
        ax.set_xticks(x)
        ax.set_xticklabels(
            [AGENTS[a]["label"] for a in agents_found],
            fontsize=9, rotation=15, ha="right"
        )
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("TRS", fontsize=11)
        ax.set_title(config["title"], fontsize=12, fontweight="bold")
        ax.grid(alpha=0.25, axis="y", zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    legend_handles = [
        plt.Rectangle((0,0), 1, 1, fc="gray", alpha=0.5, label="text only"),
        plt.Rectangle((0,0), 1, 1, fc="gray", alpha=1.0, label="vision only"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.97),
        ncol=2, fontsize=11, frameon=False
    )

    plt.tight_layout()
    path = VIZ_DIR / "agent_trs_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ============================================================
# FIGURE 2: Per-template line chart per agent (vision only)
# ============================================================
def plot_agent_degradation_lines():
    for website_key, config in WEBSITES.items():
        for mode in ["vision_only", "multimodal", "text_only"]:
            # only plot if we have at least 2 agents
            agents_with_data = []
            for agent_key, agent_cfg in AGENTS.items():
                if mode not in agent_cfg.get("modes", []):
                    continue
                s = load_summary(website_key, mode, agent_key)
                if s:
                    agents_with_data.append(agent_key)
            if len(agents_with_data) < 2:
                continue

            templates = config["templates"]
            x         = list(range(len(templates)))
            labels    = [short_label(t) for t in templates]

            fig, ax = plt.subplots(figsize=(12, 6))
            fig.suptitle(
                f"{config['title']} — per-template success rate by agent ({mode.replace('_',' ')})",
                fontsize=13, fontweight="bold"
            )

            for agent_key in agents_with_data:
                agent_cfg = AGENTS[agent_key]
                s = load_summary(website_key, mode, agent_key)
                values = [s["success_rates"].get(t, 0) * 100 for t in templates]
                ax.plot(
                    x, values,
                    color=agent_cfg["color"],
                    linestyle="-",
                    marker=agent_cfg["marker"],
                    linewidth=2.5,
                    markersize=8,
                    label=agent_cfg["label"],
                    zorder=3
                )
                ax.annotate(
                    f"{values[-1]:.0f}%",
                    (len(templates) - 1, values[-1]),
                    textcoords="offset points",
                    xytext=(9, 0),
                    fontsize=9,
                    color=agent_cfg["color"],
                    fontweight="bold"
                )

            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=10)
            ax.set_ylim(0, 115)
            ax.set_ylabel("success rate (%)", fontsize=11)
            ax.legend(fontsize=10, loc="upper right")
            ax.grid(alpha=0.25, axis="y", zorder=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            plt.tight_layout()
            path = VIZ_DIR / f"agent_degradation_{website_key}_{mode}.png"
            plt.savefig(path, dpi=150, bbox_inches="tight")
            plt.close()
            print(f"Saved: {path}")

    for agent_key, agent_cfg in AGENTS.items():
        if mode not in agent_cfg.get("modes", [mode]):
            continue
        s = load_summary(website_key, mode, agent_key)
# ============================================================
# FIGURE 3: Agent tier comparison (model size vs TRS)
# ============================================================
def plot_size_vs_trs():
    model_sizes = {
        "gpt_oss":  120,
        "qwen_vl":  30,
        "uitars":   7,
        "qwen25":   7,
        "internvl": 8,
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "model size vs temporal robustness score (vision only)",
        fontsize=13, fontweight="bold"
    )

    for col, (website_key, config) in enumerate(WEBSITES.items()):
        ax = axes[col]

        for agent_key, agent_cfg in AGENTS.items():
            s = load_summary(website_key, "vision_only", agent_key)
            if not s:
                continue

            size = model_sizes[agent_key]
            trs  = s["trs"]
            tier = agent_cfg["tier"]

            ax.scatter(
                size, trs,
                color=agent_cfg["color"],
                marker=agent_cfg["marker"],
                s=150, zorder=3,
                label=f"{agent_cfg['label']} ({tier})"
            )
            ax.annotate(
                agent_cfg["label"],
                (size, trs),
                textcoords="offset points",
                xytext=(8, 4),
                fontsize=9,
                color=agent_cfg["color"]
            )

        ax.set_xlabel("model size (B parameters)", fontsize=11)
        ax.set_ylabel("TRS", fontsize=11)
        ax.set_title(config["title"], fontsize=12, fontweight="bold")
        ax.set_ylim(0, 1.1)
        ax.axhline(y=1.0, color="gray", linestyle="--",
                   linewidth=1, alpha=0.4)
        ax.grid(alpha=0.25, zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = VIZ_DIR / "agent_size_vs_trs.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ============================================================
# FIGURE 4: Perturbation type heatmap across agents
# ============================================================
def plot_perturbation_heatmap():
    website_key = "house_renting"
    ptypes = [
        "visible", "tab_navigation", "tab_then_expand",
        "filter_navigation", "click_to_reveal"
    ]

    agents_found = []
    data_matrix  = []

    for agent_key in AGENTS:
        s = load_summary(website_key, "vision_only", agent_key)
        if not s or not s.get("perturbation_results"):
            continue
        agents_found.append(agent_key)
        row = []
        for pt in ptypes:
            sr = s["perturbation_results"].get(pt, {}).get("success_rate", 0)
            row.append(sr * 100)
        data_matrix.append(row)

    if not data_matrix:
        print("No perturbation data found, skipping heatmap")
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle(
        "success rate by agent and perturbation type (house renting, vision only)",
        fontsize=13, fontweight="bold"
    )

    matrix = np.array(data_matrix)
    im     = ax.imshow(matrix, aspect="auto", cmap="RdYlGn",
                       vmin=0, vmax=100)

    ax.set_xticks(range(len(ptypes)))
    ax.set_xticklabels(
        [p.replace("_", "\n") for p in ptypes],
        fontsize=10
    )
    ax.set_yticks(range(len(agents_found)))
    ax.set_yticklabels(
        [AGENTS[a]["label"] for a in agents_found],
        fontsize=10
    )

    for i in range(len(agents_found)):
        for j in range(len(ptypes)):
            val = matrix[i, j]
            color = "white" if val < 30 or val > 70 else "black"
            ax.text(
                j, i, f"{val:.0f}%",
                ha="center", va="center",
                fontsize=11, fontweight="bold",
                color=color
            )

    plt.colorbar(im, ax=ax, label="success rate (%)")
    plt.tight_layout()
    path = VIZ_DIR / "agent_perturbation_heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ============================================================
# MAIN
# ============================================================
print("Generating cross-agent visualizations...\n")

plot_agent_trs_comparison()
plot_agent_degradation_lines()
plot_size_vs_trs()
plot_perturbation_heatmap()

print(f"\nAll saved to: {VIZ_DIR}")