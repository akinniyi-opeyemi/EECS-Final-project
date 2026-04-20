# Synthetic Job Application Website Templates (WebArena Compatible)

## Overview

This folder contains 3 base HTML templates for job application websites, designed for evaluating **GUI agent robustness under UI and workflow changes**.

These templates are **WebArena-compatible** and can be served locally as evaluation environments.

---

## Templates

| Template                  | Description                            | Change Type                 |
| ------------------------- | -------------------------------------- | --------------------------- |
| `job_site_1_classic.html` | Plain academic style, all info visible | Baseline                    |
| `job_site_2_modern.html`  | Card-based UI with buttons             | Layout shift                |
| `job_site_3_notion.html`  | Tab + hidden content                   | Workflow + visibility shift |

---

## 1. Serving the Websites

Start a local server:

```bash
cd templates
python -m http.server 8000
```

Access:

```text
http://localhost:8000/job_site_1_classic.html
http://localhost:8000/job_site_2_modern.html
http://localhost:8000/job_site_3_notion.html
```

---

## 2. WebArena Environment Setup

Each HTML file can be treated as a **standalone WebArena environment**.

### Example environment config:

```json
{
  "env_id": "job_site_classic",
  "start_url": "http://localhost:8000/job_site_1_classic.html"
}
```

For multiple versions:

```json
[
  {
    "env_id": "job_site_classic",
    "start_url": "http://localhost:8000/job_site_1_classic.html"
  },
  {
    "env_id": "job_site_modern",
    "start_url": "http://localhost:8000/job_site_2_modern.html"
  },
  {
    "env_id": "job_site_notion",
    "start_url": "http://localhost:8000/job_site_3_notion.html"
  }
]
```

---

## 3. Task Format (WebArena-style)

Define tasks in JSON:

```json
[
  {
    "task_id": "J01",
    "env_id": "job_site_classic",
    "instruction": "Find the most recent job opening",
    "evaluation": {
      "type": "string_match",
      "target": "most recent"
    }
  }
]
```

Run the same task across all environments:

```json
{
  "task_id": "J01_modern",
  "env_id": "job_site_modern",
  "instruction": "Find the most recent job opening",
  "evaluation": {
    "type": "string_match",
    "target": "most recent"
  }
}
```

---

## 4. Recommended Task Set

Use the same tasks across all templates:

| Task ID | Instruction                         |
| ------- | ----------------------------------- |
| J01     | Find the most recent job opening    |
| J02     | Find the application deadline       |
| J03     | Find how to apply                   |
| J04     | Find required materials             |
| J05     | Check whether the job is still open |

---

## 5. Running Evaluation

Typical WebArena pipeline:

```bash
python run_eval.py \
  --env_config envs.json \
  --task_config tasks.json \
  --model qwen-vl
```

For each site:

* Agent starts at `start_url`
* Executes actions (click / scroll / read)
* Produces answer
* Evaluation checks correctness

---

## 6. Measuring Robustness

Run same tasks on all UI variants:

```text
Classic → Modern → Notion
```

Compute:

### Success Rate

```
SR = success / total
```

### Robustness Drop

```
Δ = SR(classic) - SR(notion)
```

---

## 7. Important Notes (WebArena Compatibility)

### ✔ Supported

* Static HTML pages
* DOM-based interaction
* Click / scroll / text extraction
* Button-triggered content (JS works)

### ⚠️ Limitations

* No backend APIs
* No login flows
* No dynamic network requests

---

## 8. Debug Tips

If agent fails:

* Check if element is:

  * hidden (display: none)
  * inside tab
  * behind button
* Inspect DOM in browser:

  ```bash
  right click → Inspect
  ```

---

## 9. Extending to More Sites

To generate more evaluation environments:

* Duplicate templates
* Apply UI transformations:

  * hide elements
  * change wording
  * move sections
  * add interactions

Keep:

* tasks identical
* semantics unchanged

---

## 10. Summary

These templates provide a **minimal WebArena-compatible testbed** for studying:

* Layout robustness
* Interaction robustness
* Generalization across UI changes

---

## How to use in WebArena

cd templates
python -m http.server 8000

python run_eval.py \
  --env_config envs.json \
  --task_config tasks.json