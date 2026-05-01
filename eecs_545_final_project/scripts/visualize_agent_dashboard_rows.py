# scripts/visualize_agent_dashboard_rows.py
# Saves each of the 5 dashboard rows as a separate figure for paper use.
# Output files:
#   results/visualizations/row1_success_rate.png
#   results/visualizations/row2_trs.png
#   results/visualizations/row3_recovery_rate.png
#   results/visualizations/row4_hallucination_rate.png
#   results/visualizations/row5_net_improvement.png
# Usage: python scripts/visualize_agent_dashboard_rows.py

import json
import matplotlib.pyplot as plt
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
UMICH_SHADES  = ["#00274C", "#1a4f7a", "#4a90c4", "#8ab8d8"]

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

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_summary(website, mode, agent):
    for p in [
        Path(f"results/metrics/{website}/{mode}/{agent}/summary.json"),
        Path(f"results/metrics/{website}/{mode}/summary.json"),
    ]:
        if p.exists():
            return json.load(open(p))
    return None

def get_rq2_sr(website, mode, agent, strategy, templates):
    for p in [
        Path(f"results/metrics/{website}/rq2_{mode}_{agent}/{strategy}_per_task.json"),
        Path(f"results/metrics/{website}/rq2_{mode}/{strategy}_per_task.json"),
    ]:
        if p.exists():
            tasks = json.load(open(p))
            return {
                t: (sum(1 for x in tasks if x["template"] == t and x["success"])
                    / max(1, sum(1 for x in tasks if x["template"] == t)))
                for t in templates
            }
    return None

def get_rq2_stat(website, mode, agent, strategy, key):
    for p in [
        Path(f"results/metrics/{website}/rq2_{mode}_{agent}/summary.json"),
        Path(f"results/metrics/{website}/rq2_{mode}/summary.json"),
    ]:
        if p.exists():
            s = json.load(open(p))
            return s.get("strategies", {}).get(strategy, {}).get(key, 0) * 100
    return 0

def style_ax(ax):
    ax.grid(alpha=0.25, axis="y", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", labelsize=12)
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight("bold")

def note(ax, txt):
    ax.text(0.5, -0.16, txt, transform=ax.transAxes,
            ha="center", va="top", fontsize=8.5,
            style="italic", color="gray", fontweight="bold")

# ── Row factory ───────────────────────────────────────────────────────────────
FIGSIZE = (18, 5)   # width × height per row (good for a paper column-span)
DPI     = 180

def make_fig():
    return plt.subplots(1, 3, figsize=FIGSIZE)

# =============================================================================
# ROW 1 — Success rate line charts
# =============================================================================
fig, axes = make_fig()
for ax, (website_key, wconfig) in zip(axes, WEBSITES.items()):
    templates = wconfig["templates"]
    x         = list(range(len(templates)))

    s_text = load_summary(website_key, "text_only", "gpt_oss")
    if s_text:
        cfg    = AGENTS["gpt_oss"]
        vals   = [s_text["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, vals, color=cfg["color"], linestyle="--",
                marker=cfg["marker"], linewidth=2, markersize=7,
                label=f"{cfg['label']} (text-only)", alpha=0.7, zorder=3)

    for ak in VISION_AGENTS:
        s = load_summary(website_key, "vision_only", ak)
        if not s:
            continue
        cfg  = AGENTS[ak]
        vals = [s["success_rates"].get(t, 0) * 100 for t in templates]
        ax.plot(x, vals, color=cfg["color"], linestyle="-",
                marker=cfg["marker"], linewidth=2.5, markersize=8,
                label=cfg["label"], zorder=3)

    for ak in VISION_AGENTS:
        sr = get_rq2_sr(website_key, "vision_only", ak, "memory", templates)
        if sr:
            ax.plot(x, [sr[t] * 100 for t in templates],
                    color=MEMORY_COLORS[ak], linestyle=":", marker="o",
                    linewidth=1.8, markersize=6, alpha=0.9,
                    label=f"{AGENTS[ak]['label']} + mem", zorder=2)

    for ak in VISION_AGENTS:
        sr = get_rq2_sr(website_key, "vision_only", ak, "cot", templates)
        if sr:
            ax.plot(x, [sr[t] * 100 for t in templates],
                    color=COT_COLORS[ak], linestyle="-.", marker="x",
                    linewidth=1.8, markersize=6, alpha=0.9,
                    label=f"{AGENTS[ak]['label']} + CoT", zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(wconfig["xlabels"], fontsize=12)
    ax.set_ylim(0, 140)
    ax.set_ylabel("Success rate (%)", fontsize=14, fontweight="bold")
    ax.set_title(f"{wconfig['title']}", fontsize=14, fontweight="bold", pad=10)
    ax.legend(fontsize=7, loc="upper right", ncol=3,
              framealpha=0.9, edgecolor="lightgray")
    note(ax, "† GPT-oss-120B: text-only upper bound, not a vision agent")
    style_ax(ax)

fig.suptitle("Success Rate — Vision only (solid)  +  Memory (dotted)  +  CoT (dash-dot)",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = VIZ_DIR / "row1_success_rate.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {out}")

# =============================================================================
# ROW 2 — TRS vision_only vs multimodal
# =============================================================================
fig, axes = make_fig()
for ax, (website_key, wconfig) in zip(axes, WEBSITES.items()):
    x     = np.arange(len(VISION_AGENTS))
    width = 0.35

    trs_v = [min(load_summary(website_key, "vision_only", a)["trs"], 1.5)
             if load_summary(website_key, "vision_only", a) else 0
             for a in VISION_AGENTS]
    trs_m = [min(load_summary(website_key, "multimodal", a)["trs"], 1.5)
             if load_summary(website_key, "multimodal", a) else 0
             for a in VISION_AGENTS]

    bv = ax.bar(x - width/2, trs_v, width, color=UMICH_SHADES,
                alpha=0.85, label="Vision only", edgecolor="white", zorder=3)
    bm = ax.bar(x + width/2, trs_m, width, color=UMICH_SHADES,
                alpha=0.35, label="Multimodal",  edgecolor="white", zorder=3)

    for bar, val in zip(bv, trs_v):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.015,
                f"{val:.3f}", ha="center", va="bottom",
                fontsize=7.5, fontweight="bold")
    for bar, val in zip(bm, trs_m):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.015,
                f"{val:.3f}", ha="center", va="bottom",
                fontsize=7.5, fontweight="bold")

    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1,
               alpha=0.5, label="Perfect robustness (1.0)")
    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in VISION_AGENTS],
                       fontsize=10, rotation=12, ha="center")
    ax.set_ylim(0, 1.65)
    ax.set_ylabel("TRS", fontsize=14, fontweight="bold")
    ax.set_title(f"{wconfig['title']}", fontsize=14, fontweight="bold", pad=10)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9)
    n = ("*TRS > 1.0 = inverse degradation (2000s harder than later)"
         if website_key == "course_registration"
         else "Note: GPT-oss-120B excluded (text-only mode)")
    note(ax, n)
    style_ax(ax)

fig.suptitle("Template Robustness Score (TRS) — Vision only vs. Multimodal",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = VIZ_DIR / "row2_trs.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {out}")

# =============================================================================
# ROW 3 — Recovery rate
# =============================================================================
fig, axes = make_fig()
for ax, (website_key, wconfig) in zip(axes, WEBSITES.items()):
    x     = np.arange(len(VISION_AGENTS))
    width = 0.35
    mem_r = [get_rq2_stat(website_key, "vision_only", a, "memory", "recovery_rate")
             for a in VISION_AGENTS]
    cot_r = [get_rq2_stat(website_key, "vision_only", a, "cot",    "recovery_rate")
             for a in VISION_AGENTS]

    bm = ax.bar(x - width/2, mem_r, width, color=UMICH_SHADES,
                alpha=0.85, label="Memory", edgecolor="white", zorder=3)
    bc = ax.bar(x + width/2, cot_r, width, color=UMICH_SHADES,
                alpha=0.35, label="CoT",    edgecolor="white", zorder=3)

    for bar, val in zip(bm, mem_r):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                f"{val:.1f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")
    for bar, val in zip(bc, cot_r):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                f"{val:.1f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in VISION_AGENTS],
                       fontsize=10, rotation=10, ha="center")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Recovery rate (%)", fontsize=14, fontweight="bold")
    ax.set_title(f"{wconfig['title']}", fontsize=14, fontweight="bold", pad=10)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    note(ax, "Note: GPT-oss-120B excluded — text-only mode has near-zero failures")
    style_ax(ax)

fig.suptitle("RQ2 Recovery Rate — Memory vs. CoT (vision-only failures only)",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = VIZ_DIR / "row3_recovery_rate.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {out}")

# =============================================================================
# ROW 4 — Hallucination rate
# =============================================================================
fig, axes = make_fig()
for ax, (website_key, wconfig) in zip(axes, WEBSITES.items()):
    x     = np.arange(len(VISION_AGENTS))
    width = 0.35
    mem_h = [get_rq2_stat(website_key, "vision_only", a, "memory", "hallucination_rate")
             for a in VISION_AGENTS]
    cot_h = [get_rq2_stat(website_key, "vision_only", a, "cot",    "hallucination_rate")
             for a in VISION_AGENTS]

    bm = ax.bar(x - width/2, mem_h, width, color=UMICH_SHADES,
                alpha=0.85, label="Memory", edgecolor="white", zorder=3)
    bc = ax.bar(x + width/2, cot_h, width, color=UMICH_SHADES,
                alpha=0.35, label="CoT",    edgecolor="white", zorder=3)

    for bar, val in zip(bm, mem_h):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                f"{val:.0f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")
    for bar, val in zip(bc, cot_h):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                f"{val:.0f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in VISION_AGENTS],
                       fontsize=10, rotation=10, ha="center")
    ax.set_ylim(0, 115)
    ax.set_ylabel("Hallucination rate (%)", fontsize=14, fontweight="bold")
    ax.set_title(f"{wconfig['title']}", fontsize=14, fontweight="bold", pad=10)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    note(ax, "Note: % of vanilla failures where agent gave a confident wrong answer")
    style_ax(ax)

fig.suptitle("Hallucination Rate after Intervention — Memory vs. CoT",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = VIZ_DIR / "row4_hallucination_rate.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {out}")

# =============================================================================
# ROW 5 — Net improvement
# =============================================================================
fig, axes = make_fig()
for ax, (website_key, wconfig) in zip(axes, WEBSITES.items()):
    x     = np.arange(len(VISION_AGENTS))
    width = 0.35
    mem_n = [get_rq2_stat(website_key, "vision_only", a, "memory", "recovery_rate") -
             get_rq2_stat(website_key, "vision_only", a, "memory", "hallucination_rate")
             for a in VISION_AGENTS]
    cot_n = [get_rq2_stat(website_key, "vision_only", a, "cot", "recovery_rate") -
             get_rq2_stat(website_key, "vision_only", a, "cot", "hallucination_rate")
             for a in VISION_AGENTS]

    bm = ax.bar(x - width/2, mem_n, width, color=UMICH_SHADES,
                alpha=0.85, label="Memory", edgecolor="white", zorder=3)
    bc = ax.bar(x + width/2, cot_n, width, color=UMICH_SHADES,
                alpha=0.35, label="CoT",    edgecolor="white", zorder=3)

    for bar, val in zip(bm, mem_n):
        off = 0.5 if val >= 0 else -3
        ax.text(bar.get_x() + bar.get_width()/2, val + off,
                f"{val:+.0f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")
    for bar, val in zip(bc, cot_n):
        off = 0.5 if val >= 0 else -3
        ax.text(bar.get_x() + bar.get_width()/2, val + off,
                f"{val:+.0f}%", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")

    ax.axhline(0, color="black", linewidth=0.8, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([AGENTS[a]["label"] for a in VISION_AGENTS],
                       fontsize=10, rotation=10, ha="center")
    ax.set_ylabel("Net improvement (%)", fontsize=14, fontweight="bold")
    ax.set_title(f"{wconfig['title']}", fontsize=14, fontweight="bold", pad=10)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)
    note(ax, "Positive = net benefit; Negative = intervention made things worse")
    style_ax(ax)

fig.suptitle("Net Improvement = Recovery Rate − Hallucination Rate",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = VIZ_DIR / "row5_net_improvement.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight")
plt.close()
print(f"Saved: {out}")
