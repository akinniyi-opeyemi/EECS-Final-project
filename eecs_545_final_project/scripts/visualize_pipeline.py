# scripts/visualize_pipeline.py
# Generates a polished pipeline diagram for the poster
# Usage: python scripts/visualize_pipeline.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

VIZ_DIR = Path("results/visualizations")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# ── Colors ────────────────────────────────────────────────────────────────────
NAVY      = "#00274C"
GOLD      = "#FFCB05"
ORANGE    = "#E8622A"
TEAL      = "#00788C"
LIGHT_BLUE= "#4A90C4"
LIGHT_GRAY= "#F4F4F4"
MID_GRAY  = "#CCCCCC"
RED       = "#C0392B"
GREEN     = "#1D7A4A"
WHITE     = "#FFFFFF"

fig, axes = plt.subplots(1, 2, figsize=(22, 13),
                         gridspec_kw={"width_ratios": [1, 1.35]})
fig.patch.set_facecolor(WHITE)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def box(ax, x, y, w, h, color, text, fontsize=10, text_color=WHITE,
        bold=False, radius=0.04, alpha=1.0, style="round,pad=0.05"):
    b = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle=style,
                       facecolor=color, edgecolor=WHITE,
                       linewidth=1.5, alpha=alpha, zorder=3)
    ax.add_patch(b)
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, color=text_color,
            fontweight=weight, zorder=4,
            multialignment="center")

def diamond(ax, x, y, w, h, color, text, fontsize=9, text_color=WHITE):
    dx, dy = w/2, h/2
    pts = [(x, y+dy), (x+dx, y), (x, y-dy), (x-dx, y)]
    diamond_patch = plt.Polygon(pts, closed=True,
                                facecolor=color, edgecolor=WHITE,
                                linewidth=1.5, zorder=3)
    ax.add_patch(diamond_patch)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, color=text_color,
            fontweight="bold", zorder=4)

def arrow(ax, x1, y1, x2, y2, color=NAVY, lw=2, style="->",
          label=None, label_offset=(0, 0), dashed=False):
    ls = "--" if dashed else "-"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, linestyle=ls),
                zorder=5)
    if label:
        mx, my = (x1+x2)/2 + label_offset[0], (y1+y2)/2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=8, color=color, style="italic", zorder=6)

def section_title(ax, text):
    ax.text(0.5, 1.01, text, transform=ax.transAxes,
            ha="center", va="bottom", fontsize=13,
            fontweight="bold", color=NAVY)

# ══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Preliminary Study (Uncontrolled)
# ══════════════════════════════════════════════════════════════════════════════
ax = axes[0]
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis("off")
ax.set_facecolor(WHITE)

section_title(ax, "Preliminary Study  —  Uncontrolled")
ax.axhline(y=13.35, color=NAVY, linewidth=2, xmin=0.02, xmax=0.98)

# Nodes
box(ax, 5, 12.2, 3.2, 0.85, NAVY,    "Task Instructions",   fontsize=10, bold=True)
box(ax, 5, 10.5, 3.2, 0.85, ORANGE,  "VLM Agent",           fontsize=10, bold=True)
box(ax, 5,  8.7, 3.6, 1.1,  TEAL,
    "Web Archive\nCraigslist · IMDB · Reddit", fontsize=9, bold=False)
diamond(ax, 5, 6.8, 3.0, 1.1, LIGHT_BLUE, "Evaluation\n(SR)", fontsize=9)
box(ax, 5,  5.0, 3.8, 1.0,  RED,
    "Identified Limitations", fontsize=9, bold=True)

# Arrows
arrow(ax, 5, 11.77, 5, 10.92)
arrow(ax, 5, 10.07, 5,  9.25)
arrow(ax, 5,  8.15, 5,  7.35)
arrow(ax, 5,  6.25, 5,  5.50)

# Limitations callout
lims = [
    "✗  Data contamination",
    "✗  Uncontrolled change",
    "✗  Unquantified difficulty",
    "✗  No template control",
]
for i, txt in enumerate(lims):
    ax.text(1.2, 4.1 - i*0.55, txt, fontsize=8.5, color="#555555",
            va="center", style="italic")

ax.add_patch(FancyBboxPatch((0.6, 1.7), 8.8, 2.8,
             boxstyle="round,pad=0.1",
             facecolor="#FFF3F0", edgecolor=RED,
             linewidth=1.2, alpha=0.6, zorder=1))
ax.text(5, 1.3, "These limitations motivated a controlled benchmark.",
        ha="center", fontsize=8.5, color=RED, style="italic")

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Final Study (Controlled)
# ══════════════════════════════════════════════════════════════════════════════
ax = axes[1]
ax.set_xlim(0, 14)
ax.set_ylim(0, 14)
ax.axis("off")
ax.set_facecolor(WHITE)

section_title(ax, "Final Study  —  Controlled Benchmark")
ax.axhline(y=13.35, color=NAVY, linewidth=2, xmin=0.02, xmax=0.98)

# ── RQ1 column (left) ────────────────────────────────────────────────────────
box(ax, 4, 12.2, 3.2, 0.85, NAVY,   "Task Instructions", fontsize=10, bold=True)
box(ax, 4, 10.5, 3.2, 0.85, ORANGE, "VLM Agent\n(5 models)", fontsize=9, bold=True)

# Website templates block
box(ax, 4, 8.5, 4.2, 1.6, TEAL,
    "Controlled Websites\n3 domains × 3–4 templates\n"
    "Classic  ·  Modern  ·  Hidden",
    fontsize=8.5, bold=False)

diamond(ax, 4, 6.5, 3.2, 1.1, LIGHT_BLUE,
        "Evaluation\n(SR · TRS)", fontsize=9)

box(ax, 4, 4.9, 3.8, 0.9, GREEN,
    "RQ1: Robustness across templates", fontsize=8.5, bold=True)

# RQ1 arrows
arrow(ax, 4, 11.77, 4, 10.92)
arrow(ax, 4, 10.07, 4,  9.30)
arrow(ax, 4,  7.70, 4,  7.05)
arrow(ax, 4,  5.95, 4,  5.35)

# ── RQ2 intervention loop (right branch) ─────────────────────────────────────
# Intervention box
box(ax, 10.5, 6.5, 4.0, 2.2, GOLD,
    "Test-time Interventions\n"
    "① Memory  (1-shot example)\n"
    "② Chain of Thought  (5-step)\n"
    "Applied to FAILED tasks only",
    fontsize=8.5, bold=False, text_color=NAVY)

diamond(ax, 10.5, 4.5, 3.2, 1.1, LIGHT_BLUE,
        "Re-Evaluation", fontsize=9)

# Two outcome branches from Re-Evaluation
# Left branch: Recovery
box(ax, 8.2, 2.7, 3.2, 1.0, GREEN,
    "✔ Recovery\nTask now succeeds", fontsize=8.5, bold=False)

# Right branch: Hallucination
box(ax, 12.8, 2.7, 3.2, 1.0, RED,
    "✘ Hallucination\nConfident wrong answer", fontsize=8.5, bold=False)

# Net improvement box at bottom
box(ax, 10.5, 1.2, 6.8, 0.9, NAVY,
    "RQ2: Net Improvement  =  Recovery Rate  −  Hallucination Rate",
    fontsize=8.5, bold=True)

# Dashed arrow: Evaluation → failed tasks → Intervention
arrow(ax, 5.6, 6.5, 8.5, 6.5, color=RED, lw=1.8, dashed=True,
      label="failed tasks →", label_offset=(0, 0.25))

# Intervention → Re-Evaluation
arrow(ax, 10.5, 5.40, 10.5, 5.05)

# Re-Evaluation → Recovery (left)
arrow(ax, 9.3, 4.1, 8.5, 3.20, color=GREEN, lw=1.8)
ax.text(8.1, 3.75, "success", fontsize=7.5, color=GREEN,
        style="italic", ha="center")

# Re-Evaluation → Hallucination (right)
arrow(ax, 11.7, 4.1, 12.5, 3.20, color=RED, lw=1.8)
ax.text(12.9, 3.75, "still fails\n+ wrong answer", fontsize=7.5,
        color=RED, style="italic", ha="center")

# Recovery → Net improvement
arrow(ax, 8.2, 2.20, 9.6, 1.65, color=NAVY, lw=1.5)

# Hallucination → Net improvement
arrow(ax, 12.8, 2.20, 11.4, 1.65, color=NAVY, lw=1.5)

# ── Metrics legend ─────────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.3, 0.05), 13.4, 0.85,
             boxstyle="round,pad=0.1",
             facecolor=LIGHT_GRAY, edgecolor=MID_GRAY,
             linewidth=1, zorder=1))
ax.text(7.0, 0.77, "Metrics", ha="center", fontsize=9,
        fontweight="bold", color=NAVY)
metrics = [
    ("SR",                   "Success Rate — % tasks correctly completed"),
    ("TRS",                  "Template Robustness Score — SR ratio across templates"),
    ("Recovery Rate",        "% vanilla failures fixed by intervention"),
    ("Hallucination Rate",   "% failures answered confidently but incorrectly after intervention"),
]
for i, (k, v) in enumerate(metrics):
    col = 0.6 + (i % 2) * 6.8
    row = 0.60 - (i // 2) * 0.30
    ax.text(col, row, f"• {k}:", fontsize=7.5, fontweight="bold",
            color=NAVY, va="center")
    ax.text(col + 1.7, row, v, fontsize=7.5, color="#333333", va="center")

# ══════════════════════════════════════════════════════════════════════════════
# OVERALL TITLE
# ══════════════════════════════════════════════════════════════════════════════
fig.text(0.5, 0.97, "Perturbation Benchmark Pipeline",
         ha="center", va="top", fontsize=16,
         fontweight="bold", color=WHITE,
         bbox=dict(facecolor=NAVY, edgecolor=NAVY,
                   boxstyle="round,pad=0.4", linewidth=0))

plt.tight_layout(rect=[0, 0, 1, 0.96])
path = VIZ_DIR / "pipeline_diagram.png"
plt.savefig(path, dpi=180, bbox_inches="tight", facecolor=WHITE)
plt.close()
print(f"Saved: {path}")
