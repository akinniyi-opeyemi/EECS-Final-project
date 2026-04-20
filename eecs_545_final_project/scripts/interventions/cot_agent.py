# scripts/agents/cot_agent.py
# Strategy C: Chain of Thought Agent
# Asks agent to reason step by step before answering

STRATEGY_NAME = "cot"
STRATEGY_DESCRIPTION = """
Chain of Thought agent: instructs the agent to reason
step by step before giving the final answer.
Uses structured thinking to improve accuracy on
tasks requiring navigation or information extraction.
"""

COT_SYSTEM_PROMPT = """You are a web agent evaluating websites.
You will be given a page and a task.

IMPORTANT: Think step by step before answering:
1. What information am I looking for?
2. Where on the page would this typically appear?
3. Can I see this information directly?
4. If hidden, what interaction would reveal it?
5. What is my final answer?

After reasoning, provide your final answer on the last line
starting with: FINAL ANSWER:
"""

def build_prompt(page_text, instruction,
                 interaction_hint="", screenshot_b64=None):
    """
    Chain of thought prompt that asks agent to reason
    before giving the final answer.
    """
    text = page_text or ""
    if len(text) > 5000:
        text = text[:5000] + "\n...[truncated]"

    prompt = f"""Page content:
{text}
{interaction_hint}

Task: {instruction}

Think step by step:
1. What am I looking for?
2. Where would this appear on the page?
3. Can I see it directly in the content above?
4. If not visible, what would I need to do?
5. My final answer is:

FINAL ANSWER:"""

    return prompt


def build_vision_content(screenshot_b64, instruction,
                         interaction_hint="", page_text=None):
    """Chain of thought vision prompt."""

    text = page_text or ""
    if text and len(text) > 3000:
        text = text[:3000] + "\n...[truncated]"

    content = []

    if screenshot_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{screenshot_b64}"
            }
        })

    thinking_prompt = f"""
{interaction_hint}

Task: {instruction}

Think step by step:
1. What am I looking for?
2. Is it visible in the screenshot?
3. If hidden behind a button or tab, what would I click?
4. What is my final answer based on what I can see?

FINAL ANSWER:"""

    if page_text:
        content.append({
            "type": "text",
            "text": f"Page text:\n{text}\n{thinking_prompt}"
        })
    else:
        content.append({
            "type": "text",
            "text": thinking_prompt
        })

    return content


def parse_cot_output(raw_output):
    """
    Extract final answer from CoT output.
    Looks for 'FINAL ANSWER:' marker.
    """
    if not raw_output:
        return raw_output

    if "FINAL ANSWER:" in raw_output:
        parts = raw_output.split("FINAL ANSWER:")
        answer = parts[-1].strip()
        # take only first line of final answer
        answer = answer.split("\n")[0].strip()
        return answer

    # fallback: return last line
    lines = [l.strip() for l in raw_output.strip().split("\n") if l.strip()]
    return lines[-1] if lines else raw_output