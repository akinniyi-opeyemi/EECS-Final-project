# scripts/agents/memory_agent.py
# Strategy B: Experience Memory Agent
# Shows agent examples of successful past interactions
# before asking it to solve the current task

STRATEGY_NAME = "memory"
STRATEGY_DESCRIPTION = """
Memory agent: provides few-shot examples of successful
task completions before the current task.
Examples are drawn from correct predictions on the
same task type across different properties/templates.
"""

# successful examples per task type
# drawn from text_only correct predictions
MEMORY_EXAMPLES = {
    "rent": {
        "instruction": "Find the monthly rent for Maplewood Apartments.",
        "page_snippet": "Maplewood Apartments\n$1,450/month\n2 Bedrooms",
        "answer": "$1,450/month"
    },
    "bedrooms": {
        "instruction": "Find the number of bedrooms in Sunset Ridge Home.",
        "page_snippet": "Sunset Ridge Home\n3 Bedrooms\n$2,200/month",
        "answer": "3"
    },
    "deadline": {
        "instruction": "Find the application deadline for Lakeside Condo.",
        "page_snippet": "Application Deadline: July 15, 2025\nContact: leasing@lakesidecondo.com",
        "answer": "July 15, 2025"
    },
    "email": {
        "instruction": "Find the contact email address for Parkview Terrace.",
        "page_snippet": "Contact Information\nEmail: leasing@parkviewterrace.com",
        "answer": "leasing@parkviewterrace.com"
    },
    "availability": {
        "instruction": "Check whether Cedar Grove Flat is currently available for rent.",
        "page_snippet": "Status: Available\nMonthly Rent: $1,350/month",
        "answer": "Available"
    },
    "pet_policy": {
        "instruction": "Find the pet policy for Maplewood Apartments.",
        "page_snippet": "Pet Policy: No pets allowed\nParking: 1 spot included",
        "answer": "No pets allowed"
    },
    "parking": {
        "instruction": "Find the parking details for Sunset Ridge Home.",
        "page_snippet": "Parking: 2-car garage\nLease: 12 months",
        "answer": "2-car garage"
    },
    "default": {
        "instruction": "Find the monthly rent for Oak Hill House.",
        "page_snippet": "Oak Hill House\nRent: $1,750/month\nBedrooms: 3",
        "answer": "$1,750/month"
    }
}


def get_task_type(instruction):
    """Classify instruction to find relevant example."""
    instruction_lower = instruction.lower()
    if "rent" in instruction_lower and "monthly" in instruction_lower:
        return "rent"
    elif "bedroom" in instruction_lower:
        return "bedrooms"
    elif "deadline" in instruction_lower:
        return "deadline"
    elif "email" in instruction_lower or "contact" in instruction_lower:
        return "email"
    elif "available" in instruction_lower:
        return "availability"
    elif "pet" in instruction_lower:
        return "pet_policy"
    elif "parking" in instruction_lower:
        return "parking"
    else:
        return "default"


def build_prompt(page_text, instruction,
                 interaction_hint="", screenshot_b64=None):
    """
    Memory-augmented prompt with relevant example
    prepended before the actual task.
    """
    text = page_text or ""
    if len(text) > 4000:
        text = text[:4000] + "\n...[truncated]"

    task_type = get_task_type(instruction)
    example   = MEMORY_EXAMPLES[task_type]

    prompt = f"""Here is an example of a similar task that was solved correctly:

Example page content:
{example['page_snippet']}

Example task: {example['instruction']}
Example answer: {example['answer']}

---

Now solve this task:

Page content:
{text}
{interaction_hint}

Task: {instruction}

Answer:"""

    return prompt


def build_vision_content(screenshot_b64, instruction,
                         interaction_hint="", page_text=None):
    """
    Memory-augmented vision prompt.
    Example is provided as text since we cannot show
    example screenshots easily.
    """
    task_type = get_task_type(instruction)
    example   = MEMORY_EXAMPLES[task_type]

    text = page_text or ""
    if text and len(text) > 3000:
        text = text[:3000] + "\n...[truncated]"

    system_addition = f"""Here is an example of a similar task solved correctly:
Example task: {example['instruction']}
Example answer: {example['answer']}

Now solve the current task using the screenshot provided.
"""

    content = [{
        "type": "text",
        "text": system_addition
    }]

    if screenshot_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{screenshot_b64}"
            }
        })

    if page_text and len(page_text) > 0:
        content.append({
            "type": "text",
            "text": f"Page text:\n{text}\n{interaction_hint}"
        })

    content.append({
        "type": "text",
        "text": f"\nTask: {instruction}\n\nAnswer:"
    })

    return content