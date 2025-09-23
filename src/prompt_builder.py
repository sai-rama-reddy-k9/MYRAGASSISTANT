# prompt_builder.py
from typing import Union, List, Optional, Dict, Any
from pathlib import Path

def format_prompt_section(lead_in: str, value: Union[str, List[str]]) -> str:
    """Formats a prompt section by joining a lead-in with content."""
    if isinstance(value, list):
        # filter out any empty items and ensure each is a single line
        items = [str(item).strip() for item in value if str(item).strip()]
        formatted_value = "\n".join(f"- {item}" for item in items)
    else:
        formatted_value = str(value).strip()
    return f"{lead_in}\n{formatted_value}"

def build_prompt_from_config(
    config: Dict[str, Any],
    input_data: Union[str, Dict[str, Any]] = "",
    app_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Builds a complete prompt string based on a config dictionary."""
    prompt_parts = []

    # Role
    if role := config.get("role"):
        prompt_parts.append(f"You are {role.strip()}")

    # Instruction
    instruction = config.get("instruction")
    if not instruction:
        raise ValueError("Missing required field: 'instruction'")
    prompt_parts.append(format_prompt_section("Your task is as follows:", instruction))

    # Extra fields (context, constraints, tone, etc.)
    if context := config.get("context"):
        prompt_parts.append(f"Here’s some background that may help you:\n{context}")

    if constraints := config.get("output_constraints"):
        prompt_parts.append(format_prompt_section("Ensure your response follows these rules:", constraints))

    if tone := config.get("style_or_tone"):
        prompt_parts.append(format_prompt_section("Follow these style and tone guidelines in your response:", tone))

    if format_ := config.get("output_format"):
        prompt_parts.append(format_prompt_section("Structure your response as follows:", format_))

    if examples := config.get("examples"):
        prompt_parts.append("Here are some examples to guide your response:")
        if isinstance(examples, list):
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"Example {i}:\n{example}")
        else:
            prompt_parts.append(str(examples))

    if goal := config.get("goal"):
        prompt_parts.append(f"Your goal is to achieve the following outcome:\n{goal}")

    # 🔹 Handle input_data if it's a dict with query + docs
    if isinstance(input_data, dict):
        query = input_data.get("query", "")
        docs = input_data.get("documents", [])
        context = "\n\n".join(docs)

        prompt_parts.append(f"User Question:\n{query}")
        prompt_parts.append(
            "Relevant Documents:\n"
            "<<<BEGIN DOCUMENTS>>>\n"
            f"{context}\n"
            "<<<END DOCUMENTS>>>"
        )
    elif isinstance(input_data, str) and input_data.strip():
        # Fallback: treat as raw string
        prompt_parts.append(
            "Here is the content you need to work with:\n"
            "<<<BEGIN CONTENT>>>\n"
            f"{input_data.strip()}\n"
            "<<<END CONTENT>>>"
        )

    # Reasoning strategy
    reasoning_strategy = config.get("reasoning_strategy")
    if reasoning_strategy and app_config:
        strategies = app_config.get("reasoning_strategies", {})
        if strategy_text := strategies.get(reasoning_strategy):
            prompt_parts.append(format_prompt_section("Use the following reasoning approach:", strategy_text.strip()))

    prompt_parts.append("Now perform the task as instructed above.")
    return "\n\n".join(prompt_parts)


def print_prompt_preview(prompt: str, max_length: int = 800) -> None:
    """Prints a preview of the constructed prompt for debugging purposes."""
    print("=" * 80)
    print("PROMPT PREVIEW (first {} chars):".format(max_length))
    print("=" * 80)
    if len(prompt) > max_length:
        # print(prompt[:max_length] + "...")
        print(f"\n[Truncated - Full prompt length: {len(prompt)} characters]")
    else:
        print(prompt)
    print("=" * 80)


def build_system_prompt_from_config(
    config: Dict[str, Any],
    publication_content: str = "",
) -> str:
    """Builds a system prompt string based on a config dictionary."""
    prompt_parts = []

    # Role (required)
    role = config.get("role")
    if not role:
        raise ValueError("Missing required field: 'role'")
    prompt_parts.append(f"You are {role.strip()}")

    # Behavioral constraints
    if constraints := config.get("output_constraints"):
        prompt_parts.append(format_prompt_section("Follow these important guidelines:", constraints))

    # Style/tone
    if tone := config.get("style_or_tone"):
        prompt_parts.append(format_prompt_section("Communication style:", tone))

    # Output format requirements
    if format_ := config.get("output_format"):
        prompt_parts.append(format_prompt_section("Response formatting:", format_))

    # Goal
    if goal := config.get("goal"):
        prompt_parts.append(f"Your primary objective: {goal}")

    # Publication content (include if present)
    if publication_content:
        prompt_parts.append(
            "Base your responses on this publication content:\n\n"
            "=== PUBLICATION CONTENT ===\n"
            f"{publication_content.strip()}\n"
            "=== END PUBLICATION CONTENT ==="
        )

    return "\n\n".join(prompt_parts)
