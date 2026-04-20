from pathlib import Path
import random
import json
import re

random.seed(42)

TEMPLATE_DIR = Path("templates")
OUTPUT_DIR = Path("generated_sites")
OUTPUT_DIR.mkdir(exist_ok=True)

template_files = [
    "job_site_1_classic.html",
    "job_site_2_modern.html",
    "job_site_3_notion.html",
]

job_titles = [
    "Research Engineer — Job Application Agents",
    "PhD Research Assistant in Web Agent Robustness",
    "Postdoctoral Fellow — Adaptive Job Search Agents",
    "Research Scientist — Interactive AI Systems",
    "ML Engineer — Workflow Automation",
    "Applied Scientist — GUI Agent Evaluation",
]

closed_titles = [
    "ML Intern — Synthetic Website Generation",
    "Undergraduate Research Intern",
    "Research Assistant — Evaluation Infrastructure",
]

deadline_pool = [
    "May 20, 2026",
    "May 25, 2026",
    "June 1, 2026",
    "June 10, 2026",
    "June 15, 2026",
]

emails = [
    "careers@nexa-ai.example",
    "ameliahartlab@university.edu",
    "atlaslab-hiring@example.com",
    "apply-robustness@example.com",
]

materials_sets = [
    ["CV", "Transcript", "Short statement of interest", "GitHub or portfolio"],
    ["CV", "Unofficial transcript", "Research statement"],
    ["Resume", "Project portfolio", "One writing sample"],
    ["CV", "Two representative papers or projects", "Research statement", "2 references"],
]

status_words = [
    "OPEN",
    "Open",
    "Currently Open",
]

apply_phrases = [
    "How to apply",
    "Application Instructions",
    "Submit Materials",
    "Apply Here",
]

recent_markers = [
    "Most recent role",
    "Most recent opening",
    "Newest opening",
    "Latest opening",
]

def safe_replace_first(text, pattern, repl):
    return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE | re.DOTALL)

def replace_any_first(text, candidates, repl):
    for c in candidates:
        if c in text:
            return text.replace(c, repl, 1)
    return text

def shuffle_materials_list(items):
    items = items[:]
    random.shuffle(items)
    return items

def to_html_list(items):
    return "\n".join(f"<li>{x}</li>" for x in items)

def wording_shift(html):
    html = replace_any_first(
        html,
        ["How to apply", "Application Instructions", "Submit Materials", "Apply Here"],
        random.choice(apply_phrases),
    )
    html = replace_any_first(
        html,
        ["Most recent role", "Most recent opening", "Newest opening", "Latest opening", "Most recent opening: Yes"],
        random.choice(recent_markers),
    )
    html = replace_any_first(
        html,
        ["OPEN", "Open", "Currently Open"],
        random.choice(status_words),
    )
    return html

def content_shift(html):
    new_job = random.choice(job_titles)
    new_closed = random.choice(closed_titles)
    new_deadline = random.choice(deadline_pool)
    new_email = random.choice(emails)
    new_materials = shuffle_materials_list(random.choice(materials_sets))

    title_candidates = [
        "Research Engineer — Job Application Agents",
        "PhD Research Assistant in Web Agent Robustness",
        "Postdoctoral Fellow — Adaptive Job Search Agents",
    ]
    for old in title_candidates:
        if old in html:
            html = html.replace(old, new_job, 1)
            break

    for old in closed_titles:
        if old in html:
            html = html.replace(old, new_closed, 1)
            break

    html = re.sub(
        r"(Application deadline:\s*</strong>\s*)([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"\g<1>" + new_deadline,
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    html = re.sub(
        r"(Deadline:\s*)([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"\g<1>" + new_deadline,
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    html = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        new_email,
        html,
        count=1,
    )

    html = re.sub(
        r"<li>CV</li>.*?</ul>",
        to_html_list(new_materials) + "\n        </ul>",
        html,
        count=1,
        flags=re.DOTALL,
    )

    return html

def layout_shift(html):
    # 轻量级结构扰动：改 section 顺序、标题级别、强调样式
    html = html.replace("<h2>Open Positions</h2>", "<h2>Hiring Opportunities</h2>")
    html = html.replace("<h2>Opportunities</h2>", "<h2>Available Roles</h2>")
    html = html.replace("<h4>Required materials</h4>", "<h4>Application package</h4>")
    html = html.replace("<h4>How to apply</h4>", "<h4>Submission method</h4>")

    # 给一些元素加折叠风格 class 名，模拟视觉变化
    html = html.replace('class="job-box"', 'class="job-box variant-card"')
    html = html.replace('class="database-row"', 'class="database-row compact-row"')
    return html

def workflow_shift(html):
    # 让“apply信息”更可能隐藏在按钮后
    if "id=\"applyInfo\"" in html and "display: none" in html:
        return html

    if "How to apply" in html or "Submission method" in html:
        pattern = r"(<h4>(How to apply|Submission method)</h4>\s*<p>.*?</p>)"
        match = re.search(pattern, html, flags=re.DOTALL | re.IGNORECASE)
        if match:
            original = match.group(1)
            replacement = """
<h4>Submission method</h4>
<button onclick="var x=document.getElementById('hiddenApply'); x.style.display=(x.style.display==='block'?'none':'block');">
Reveal application instructions
</button>
<div id="hiddenApply" style="display:none; margin-top:10px;">
""" + original + """
</div>
"""
            html = html.replace(original, replacement, 1)
    return html

def visibility_shift(html):
    # 把 materials 或 deadline 隐藏一层
    pattern = r"(<h4>(Required materials|Application package)</h4>\s*<ul>.*?</ul>)"
    match = re.search(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    if match:
        block = match.group(1)
        hidden = """
<button onclick="var x=document.getElementById('materialsBox'); x.style.display=(x.style.display==='block'?'none':'block');">
Show required materials
</button>
<div id="materialsBox" style="display:none; margin-top:10px;">
""" + block + """
</div>
"""
        html = html.replace(block, hidden, 1)
    return html

def inject_banner(html, variant_name, change_type):
    banner = f"""
<div style="margin:12px 0; padding:10px 14px; border:1px solid #ccc; background:#f4f4f4; font-size:14px;">
  Synthetic Variant: <strong>{variant_name}</strong> |
  Change Type: <strong>{change_type}</strong>
</div>
"""
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + banner, 1)
    return html

def generate_variant(base_html, variant_idx):
    html = base_html
    applied = []

    html = content_shift(html)
    html = wording_shift(html)

    optional_changes = [
        ("layout", layout_shift),
        ("workflow", workflow_shift),
        ("visibility", visibility_shift),
    ]

    num_changes = random.choice([1, 2, 2, 3])
    chosen = random.sample(optional_changes, k=num_changes)

    for name, fn in chosen:
        html = fn(html)
        applied.append(name)

    variant_name = f"variant_{variant_idx:02d}"
    html = inject_banner(html, variant_name, "+".join(applied))
    return html, applied

def main(num_variants=30):
    manifest = []

    for i in range(num_variants):
        template_name = random.choice(template_files)
        template_path = TEMPLATE_DIR / template_name
        base_html = template_path.read_text(encoding="utf-8")

        html, applied = generate_variant(base_html, i + 1)

        out_dir = OUTPUT_DIR / f"site_{i+1:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / "index.html"
        out_file.write_text(html, encoding="utf-8")

        metadata = {
            "site_id": f"site_{i+1:02d}",
            "base_template": template_name,
            "change_types": applied,
            "goal_domain": "job_application",
            "notes": "Synthetic website variant for GUI robustness evaluation"
        }

        with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        manifest.append(metadata)

    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {num_variants} sites in: {OUTPUT_DIR.resolve()}")

if __name__ == "__main__":
    main(num_variants=30)