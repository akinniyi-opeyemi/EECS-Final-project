# scripts/visualize_agent_dashboard.py
import json
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

AGENTS = {
    "gpt_oss":  {"label": "GPT-oss-120B",  "color": "#3266ad", "marker": "o"},
    "qwen_vl":  {"label": "Qwen3-VL-30B",  "color": "#d85a30", "marker": "^"},
    "uitars":   {"label": "UI-TARS-7B",     "color": "#7f77dd", "marker": "D"},
    "qwen25":   {"label": "Qwen2.5-VL-7B", "color": "#1d9e75", "marker": "s"},
    "internvl": {"label": "InternVL2-8B",   "color": "#ba7517", "marker": "P"},
}

VISION_AGENTS = ["qwen_vl", "uitars", "qwen25", "internvl"]
ALL_AGENTS    = ["gpt_oss", "qwen_vl", "uitars", "qwen25", "internvl"]

MEMORY_COLORS = {
    "qwen_vl":  "#f5a0a0",
    "uitars":   "#b8b4f0",
    "qwen25":   "#a0d4b8",
    "internvl": "#e8c98a",
}

WEBSITES = {
    "house_renting": {
        "title":     "House Renting",
        "templates": ["classic", "modern", "hidden"],
        "xlabels":   ["classic", "modern", "hidden"],
    },
    "personal_website": {
        "title":     "Personal Website",
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
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

def get_rq2_sr(website, mode, agent, strategy, templates):
    rq2_path = Path(f"results/metrics/{website}/rq2_{mode}_{agent}/{strategy}_per_task.json")
    if not rq2_path.exists():
        rq2_path = Path(f"results/metrics/{website}/rq2_{mode}/{strategy}_per_task.json")
    if not rq2_path.exists():
        return None
    with open(rq2_path) as f:
        tasks = json.load(f)
    sr = {}
    for t in templates:
        t_tasks = [x for x in tasks if x["template"] == t]
        sr[t] = sum(1 for x in t_tasks if x["success"]) / len(t_tasks) if t_tasks else 0
    return sr

def get_rq2_recovery_rate(website, mode, agent, strategy):
    path = Path(f"results/metrics/{website}/rq2_{mode}_{agent}/summary.json")
    if not path.exists():
        path = Path(f"results/metrics/{website}/rq2_{mode}/summary.json")
    if not path.exists():
        return 0
    with open(path) as f:
        s = json.load(f)
    return s.get("strategies", {}).get(strategy, {}).get("recovery_rate", 0) * 100

# ============================================================
# figure
# ============================================================
fig = plt.figure(figsize=(20, 20))
fig.suptitle(
    "GUI Agent Temporal Robustness: Cross-Agent Comparison",
    fontsize=18, fontweight="bold", y=0.995
)

gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.38, wspace=0.28)

# ============================================================
# ROW 1: Per-template lines vision_only + memory overlay
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[0, col])
    templates = wconfig["templates"]
    xlabels   = wconfig["xlabels"]
    x         = list(range(len(templates)))

    # gpt_oss text upper bound
    s_text = load_summary(website_key, "text_only", "gpt_oss")
    if s_text:
        cfg    = AGENTS["gpt_oss"]
        values = [s_text["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=cfg["color"], linestyle="--",
                marker=cfg["marker"], linewidth=2, markersize=7,
                label=f"{cfg['label']} (text-only upper bound)", alpha=0.7, zorder=3)

    # vision_only solid lines
    for agent_key in VISION_AGENTS:
        s = load_summary(website_key, "vision_only", agent_key)
        if not s:
            continue
        cfg    = AGENTS[agent_key]
        values = [s["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=cfg["color"], linestyle="-",
                marker=cfg["marker"], linewidth=2.5, markersize=8,
                label=cfg["label"], zorder=3)
        ax.annotate(f"{values[-1]:.0f}%",
                    (len(templates) - 1, values[-1]),
                    textcoords="offset points", xytext=(8, 0),
                    fontsize=8.5, color=cfg["color"], fontweight="bold")

    # memory dotted lines
    for agent_key in VISION_AGENTS:
        mem_sr = get_rq2_sr(website_key, "vision_only", agent_key, "memory", templates)
        if not mem_sr:
            continue
        values = [mem_sr.get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=MEMORY_COLORS[agent_key], linestyle=":",
                marker="o", linewidth=1.8, markersize=6,
                label=f"{AGENTS[agent_key]['label']} + memory", zorder=2, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=10)
    ax.set_ylim(0, 115)
    ax.set_ylabel("success rate (%)", fontsize=11)

    ax.set_title(
        f"{wconfig['title']} — vision only (solid) + memory (dotted)",
        fontsize=13, fontweight="bold", pad=14
    )
    ax.text(0.5, 1.045,
            "† GPT-oss-120B shown as text-only upper bound, not evaluated on vision tasks",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, style="italic", color="gray")

    ax.legend(fontsize=7.5, loc="upper right", ncol=2,
              framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 2: TRS bar charts
# ============================================================
modes_config = {
    "vision_only": {"col": 0, "title": "TRS by Agent (vision only)"},
    "multimodal":  {"col": 1, "title": "TRS by Agent (multimodal)"},
}

for mode, mconfig in modes_config.items():
    ax = fig.add_subplot(gs[1, mconfig["col"]])
    mode_per_agent = {
        "gpt_oss":  "text_only",
        "qwen_vl":  mode,
        "uitars":   mode,
        "qwen25":   mode,
        "internvl": mode,
    }

    x              = np.arange(len(ALL_AGENTS))
    width          = 0.35
    website_colors = ["#4a90d9", "#e07b39"]
    website_labels = ["House Renting", "Personal Website"]

    for wi, (website_key, wlabel, wcolor) in enumerate(
            zip(list(WEBSITES.keys()), website_labels, website_colors)):
        trs_vals = []
        for agent_key in ALL_AGENTS:
            s = load_summary(website_key, mode_per_agent[agent_key], agent_key)
            trs_vals.append(s["trs"] if s else 0)
        offset = (wi - 0.5) * width
        bars   = ax.bar(x + offset, trs_vals, width, color=wcolor,
                        alpha=0.85, label=wlabel,
                        edgecolor="white", linewidth=1.2, zorder=3)
        for bar, val in zip(bars, trs_vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        val + 0.01, f"{val:.3f}",
                        ha="center", va="bottom",
                        fontsize=7.5, fontweight="bold")

    ax.axhline(y=1.0, color="gray", linestyle="--",
               linewidth=1, alpha=0.4, label="perfect robustness")
    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in ALL_AGENTS],
                       fontsize=8.5, rotation=15, ha="right")
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("TRS", fontsize=11)

    ax.set_title(mconfig["title"], fontsize=13, fontweight="bold", pad=14)
    ax.text(0.5, 1.045,
            "† GPT-oss-120B uses text-only mode (DOM extraction, no vision)",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, style="italic", color="gray")

    ax.legend(fontsize=9, loc="upper left",
              framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 3: Memory and CoT recovery rate by agent
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[2, col])

    memory_rates = []
    cot_rates    = []
    labels       = []

    for agent_key in VISION_AGENTS:
        mem_rate = get_rq2_recovery_rate(website_key, "vision_only", agent_key, "memory")
        cot_rate = get_rq2_recovery_rate(website_key, "vision_only", agent_key, "cot")
        memory_rates.append(mem_rate)
        cot_rates.append(cot_rate)
        labels.append(AGENTS[agent_key]["label"])

    x          = np.arange(len(VISION_AGENTS))
    width      = 0.35
    colors_mem = [AGENTS[a]["color"] for a in VISION_AGENTS]

    bars_mem = ax.bar(x - width/2, memory_rates, width,
                      color=colors_mem, alpha=0.85,
                      edgecolor="white", linewidth=1.2,
                      label="memory", zorder=3)
    bars_cot = ax.bar(x + width/2, cot_rates, width,
                      color=colors_mem, alpha=0.4,
                      edgecolor="white", linewidth=1.2,
                      label="CoT", zorder=3)

    for bar, val in zip(bars_mem, memory_rates):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + 0.5, f"{val:.1f}%",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar, val in zip(bars_cot, cot_rates):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + 0.5, f"{val:.1f}%",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, rotation=10, ha="right")
    ax.set_ylabel("recovery rate (%)", fontsize=11)

    ax.set_title(
        f"{wconfig['title']} — RQ II intervention recovery (vision only)",
        fontsize=13, fontweight="bold", pad=14
    )
    ax.text(0.5, 1.045,
            "Note: GPT-oss-120B excluded — text-only mode has near-zero failures, no recovery needed",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, style="italic", color="gray")

    ax.legend(fontsize=10, loc="upper right",
              framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.995])
path = VIZ_DIR / "agent_comprehensive_dashboard.png"
plt.savefig(path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {path}")