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

MEMORY_COLORS = {
    "qwen_vl":  "#f5a0a0",
    "uitars":   "#b8b4f0",
    "qwen25":   "#a0d4b8",
    "internvl": "#e8c98a",
}

COT_COLORS = {
    "qwen_vl":  "#c0392b",
    "uitars":   "#6c3483",
    "qwen25":   "#1a5276",
    "internvl": "#784212",
}

WEBSITES = {
    "house_renting": {
        "title":     "House Renting",
        "templates": ["classic", "modern", "hidden"],
        "xlabels":   ["Classic", "Modern", "Hidden"],
    },
    "personal_website": {
        "title":     "Personal Website",
        "templates": ["raw_html_1998", "hugo_papermod", "notion", "jekyll_alfolio"],
        "xlabels":   ["Raw\n1998", "Hugo\nPaperMod", "Notion", "Jekyll\nAlFolio"],
    },
    "course_registration": {
        "title":     "Course Registration",
        "templates": ["2000s", "2010s", "modern"],
        "xlabels":   ["2000s", "2010s", "Modern"],
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
# figure: 3 rows x 3 cols
# ============================================================
fig = plt.figure(figsize=(30, 22))
fig.suptitle(
    "GUI agent temporal robustness: cross-agent comparison",
    fontsize=18, fontweight="bold", y=0.998
)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.62, wspace=0.30)

# ============================================================
# ROW 1: line charts per website (vision_only + memory overlay)
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[0, col])
    templates = wconfig["templates"]
    xlabels   = wconfig["xlabels"]
    x         = list(range(len(templates)))

    s_text = load_summary(website_key, "text_only", "gpt_oss")
    if s_text:
        cfg    = AGENTS["gpt_oss"]
        values = [s_text["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=cfg["color"], linestyle="--",
                marker=cfg["marker"], linewidth=2, markersize=7,
        label=f"{cfg['label']} (text-only)", alpha=0.7, zorder=3)

    for agent_key in VISION_AGENTS:
        s = load_summary(website_key, "vision_only", agent_key)
        if not s:
            continue
        cfg    = AGENTS[agent_key]
        values = [s["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=cfg["color"], linestyle="-",
                marker=cfg["marker"], linewidth=2.5, markersize=8,
                label=cfg["label"], zorder=3)

    for agent_key in VISION_AGENTS:
        mem_sr = get_rq2_sr(website_key, "vision_only", agent_key, "memory", templates)
        if not mem_sr:
            continue
        values = [mem_sr.get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=MEMORY_COLORS[agent_key], linestyle=":",
                marker="o", linewidth=1.8, markersize=6,
                label=f"{AGENTS[agent_key]['label']} + mem", zorder=2, alpha=0.9)

    for agent_key in VISION_AGENTS:
        cot_sr = get_rq2_sr(website_key, "vision_only", agent_key, "cot", templates)
        if not cot_sr:
            continue
        values = [cot_sr.get(t, 0) * 100 for t in templates]
        ax.plot(x, values, color=COT_COLORS[agent_key], linestyle="-.",
                marker="x", linewidth=1.8, markersize=6,
                label=f"{AGENTS[agent_key]['label']} + CoT", zorder=2, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=10)
    ax.set_ylim(0, 140)
    ax.set_ylabel("Success rate (%)", fontsize=11)
    ax.set_title(f"{wconfig['title']} — Vision only (solid) + Memory (dotted) + CoT (dash-dot)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.text(0.5, -0.14,
            "† GPT-oss-120B: text-only upper bound, not a vision agent",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8, style="italic", color="red", fontweight="bold")
    ax.legend(fontsize=7, loc="upper right", ncol=3,
              framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 2: TRS vision_only vs multimodal per website (Option A)
# Same chart type for all 3 websites
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[1, col])
    x      = np.arange(len(VISION_AGENTS))
    width  = 0.35

    trs_vision = []
    trs_multi  = []
    for agent_key in VISION_AGENTS:
        s = load_summary(website_key, "vision_only", agent_key)
        trs_vision.append(min(s["trs"], 1.5) if s else 0)
        s = load_summary(website_key, "multimodal", agent_key)
        trs_multi.append(min(s["trs"], 1.5) if s else 0)

    bars_v = ax.bar(x - width/2, trs_vision, width, color="#7f77dd",
                    alpha=0.85, label="Vision only",
                    edgecolor="white", linewidth=1.2, zorder=3)
    bars_m = ax.bar(x + width/2, trs_multi, width, color="#1d9e75",
                    alpha=0.85, label="Multimodal",
                    edgecolor="white", linewidth=1.2, zorder=3)

    for bar, val in zip(bars_v, trs_vision):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.015, f"{val:.3f}",
                ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    for bar, val in zip(bars_m, trs_multi):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.015, f"{val:.3f}",
                ha="center", va="bottom", fontsize=7.5, fontweight="bold")

    ax.axhline(y=1.0, color="gray", linestyle="--",
               linewidth=1, alpha=0.5, label="Perfect robustness (1.0)")
    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in VISION_AGENTS],
                       fontsize=8.5, rotation=12, ha="right")
    ax.set_ylim(0, 1.65)
    ax.set_ylabel("TRS", fontsize=11)
    ax.set_title(f"{wconfig['title']} — TRS by agent",
                 fontsize=12, fontweight="bold", pad=12)
    note = "*TRS > 1.0 = inverse degradation (2000s era harder than later)" \
           if website_key == "course_registration" \
           else "Note: GPT-oss-120B excluded (text-only mode)"
    ax.text(0.5, -0.14, note,
            transform=ax.transAxes, ha="center", va="top",
            fontsize=7.5, style="italic", color="red", fontweight="bold")
    ax.legend(fontsize=9, loc="upper right",
              framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# ============================================================
# ROW 3: Memory and CoT recovery (all 3 websites)
# ============================================================
for col, (website_key, wconfig) in enumerate(WEBSITES.items()):
    ax = fig.add_subplot(gs[2, col])

    memory_rates = []
    cot_rates    = []
    labels       = []

    for agent_key in VISION_AGENTS:
        memory_rates.append(get_rq2_recovery_rate(website_key, "vision_only", agent_key, "memory"))
        cot_rates.append(get_rq2_recovery_rate(website_key, "vision_only", agent_key, "cot"))
        labels.append(AGENTS[agent_key]["label"])

    x          = np.arange(len(VISION_AGENTS))
    width      = 0.35
    colors_mem = [AGENTS[a]["color"] for a in VISION_AGENTS]

    bars_mem = ax.bar(x - width/2, memory_rates, width,
                      color=colors_mem, alpha=0.85,
                      edgecolor="white", linewidth=1.2,
                      label="Memory", zorder=3)
    bars_cot = ax.bar(x + width/2, cot_rates, width,
                      color=colors_mem, alpha=0.4,
                      edgecolor="white", linewidth=1.2,
                      label="CoT", zorder=3)

    for bar, val in zip(bars_mem, memory_rates):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.5, f"{val:.1f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar, val in zip(bars_cot, cot_rates):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.5, f"{val:.1f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, rotation=10, ha="right")
    ax.set_ylabel("Recovery rate (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_title(f"{wconfig['title']} — RQ II recovery (vision only)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.text(0.5, -0.14,
            "Note: GPT-oss-120B excluded — text-only mode has near-zero failures",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8, style="italic", color="red", fontweight="bold")
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