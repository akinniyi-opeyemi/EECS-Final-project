# scripts/agents/vanilla.py
# Strategy A: Vanilla agent
# No additional context, just the task instruction
# This is already implemented in infer.py
# This file documents the strategy for comparison

STRATEGY_NAME = "vanilla"
STRATEGY_DESCRIPTION = """
Vanilla agent: provides only the task instruction and page content.
No examples, no reasoning guidance.
Baseline strategy.
"""

def build_prompt(page_text, instruction, interaction_hint="",
                 screenshot_b64=None):
    """Standard prompt with no enhancements."""
    text = page_text or ""
    if len(text) > 5000:
        text = text[:5000] + "\n...[truncated]"

    return f"Page content:\n{text}\n{interaction_hint}\n\nTask: {instruction}\n\nAnswer:"