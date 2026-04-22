# scripts/show_and_delete_later.py
# TEMPORARY — preview of hallucination rate charts. Delete when done.
# Usage: python scripts/show_and_delete_later.py

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

AGENTS = {
    "qwen_vl":  {"label": "Qwen3-VL-30B",  "color": "#00274C"},
    "uitars":   {"label": "UI-TARS-7B",     "color": "#1a4f7a"},
    "qwen25":   {"label": "Qwen2.5-VL-7B", "color": "#4a90c4"},
    "internvl": {"label": "InternVL2-8B",   "color": "#8ab8d8"},
}

WEBSITES = ["house_renting", "personal_website", "course_registration"]
WEBSITE_TITLES = {
    "house_renting":      "House Renting",
    "personal_website":   "Personal Website",
    "course_registration":"Course Registration",
}

def load_rq2_summary(website, agent):
    p = Path(f"results/metrics/{website}/rq2_vision_only_{agent}/summary.json")
    if not p.exists():
        p = Path(f"results/metrics/{website}/rq2_vision_only/summary.json")
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return None

# ============================================================
# Build data
# ============================================================
# For each website x agent: mem_hall, cot_hall, mem_rec, cot_rec
data = {w: {a: {} for a in AGENTS} for w in WEBSITES}
for w in WEBSITES:
    for a in AGENTS:
        s = load_rq2_summary(w, a)
        if s:
            data[w][a] = {
                "mem_hall": s["strategies"]["memory"]["hallucination_rate"] * 100,
                "cot_hall": s["strategies"]["cot"]["hallucination_rate"] * 100,
                "mem_rec":  s["strategies"]["memory"]["recovery_rate"] * 100,
                "cot_rec":  s["strategies"]["cot"]["recovery_rate"] * 100,
            }

# ============================================================
# FIGURE: 2 rows x 3 cols
# Row 1: Hallucination rate (memory vs CoT) per website
# Row 2: Net improvement = recovery - hallucination per website
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(22, 10),
                         gridspec_kw={"hspace": 0.35, "wspace": 0.30})

agent_keys  = list(AGENTS.keys())
agent_labels = [AGENTS[a]["label"] for a in agent_keys]
colors       = [AGENTS[a]["color"] for a in agent_keys]
x      = np.arange(len(agent_keys))
width  = 0.35

# ── ROW 1: Hallucination rates ──────────────────────────────
for col, w in enumerate(WEBSITES):
    ax = axes[0, col]

    mem_halls = [data[w][a].get("mem_hall", 0) for a in agent_keys]
    cot_halls = [data[w][a].get("cot_hall", 0) for a in agent_keys]

    bars_mem = ax.bar(x - width/2, mem_halls, width,
                      color=colors, alpha=0.85,
                      edgecolor="white", linewidth=1.2,
                      label="Memory", zorder=3)
    bars_cot = ax.bar(x + width/2, cot_halls, width,
                      color=colors, alpha=0.35,
                      edgecolor="white", linewidth=1.2,
                      label="CoT", zorder=3)

    for bar, val in zip(bars_mem, mem_halls):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.8, f"{val:.0f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar, val in zip(bars_cot, cot_halls):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.8, f"{val:.0f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(agent_labels, fontsize=9, rotation=10, ha="right")
    ax.set_ylim(0, 115)
    ax.set_ylabel("Hallucination rate (%)", fontsize=11)
    ax.set_title(f"{WEBSITE_TITLES[w]}",
                 fontsize=12, fontweight="bold", pad=10)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.5, -0.14,
            "Note: % of vanilla failures where agent gave a wrong specific answer",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8, style="italic", color="gray", fontweight="bold")

# ── ROW 2: Net improvement = recovery - hallucination ───────
for col, w in enumerate(WEBSITES):
    ax = axes[1, col]

    mem_net = [data[w][a].get("mem_rec", 0) - data[w][a].get("mem_hall", 0)
               for a in agent_keys]
    cot_net = [data[w][a].get("cot_rec", 0) - data[w][a].get("cot_hall", 0)
               for a in agent_keys]

    bars_mem = ax.bar(x - width/2, mem_net, width,
                      color=colors, alpha=0.85,
                      edgecolor="white", linewidth=1.2,
                      label="Memory", zorder=3)
    bars_cot = ax.bar(x + width/2, cot_net, width,
                      color=colors, alpha=0.35,
                      edgecolor="white", linewidth=1.2,
                      label="CoT", zorder=3)

    for bar, val in zip(bars_mem, mem_net):
        offset = 0.8 if val >= 0 else -3
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + offset, f"{val:+.0f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar, val in zip(bars_cot, cot_net):
        offset = 0.8 if val >= 0 else -3
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + offset, f"{val:+.0f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.axhline(y=0, color="black", linewidth=0.8, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(agent_labels, fontsize=9, rotation=10, ha="right")
    ax.set_ylabel("Net improvement (%)", fontsize=11)
    ax.set_title(f"{WEBSITE_TITLES[w]}",
                 fontsize=12, fontweight="bold", pad=10)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9, edgecolor="lightgray")
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.5, -0.14,
            "Positive = net benefit; Negative = intervention made things worse",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=8, style="italic", color="gray", fontweight="bold")

path = VIZ_DIR / "agent_hallucination_charts.png"
plt.savefig(path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {path}")
