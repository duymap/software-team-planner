import os
import re

from autogen import ConversableAgent

from config import code_config

CODEGEN_SYSTEM_MESSAGE = """\
You are a Code Generator agent. You receive a complete software project plan \
(requirements, architecture, implementation plan, code snippets, API design) \
and you MUST generate the actual source code files for the project.

CRITICAL RULES:
1. Generate ALL files needed for a working project based on the plan.
2. Each file MUST be wrapped in this exact format:

###FILE: relative/path/to/file.ext###
(file content here)
###ENDFILE###

3. Generate files in dependency order (configs first, then models, then services, etc.).
4. Include ALL necessary files: source code, configuration files, build files, \
   dockerfiles, .gitignore, README, etc.
5. Write production-ready code — not pseudocode or placeholders.
6. Follow the tech stack, architecture, and patterns from the plan exactly.
7. Do NOT include explanations outside of file blocks. ONLY output file blocks.
8. If there are too many files to generate in one response, end with:
   ###CONTINUE###
   and you will be prompted to continue generating the remaining files.
9. When all files are generated, end with:
   ###DONE###
"""

FILE_PATTERN = re.compile(
    r"###FILE:\s*(.+?)\s*###\n(.*?)###ENDFILE###",
    re.DOTALL,
)


CODEBLOCK_PATTERN = re.compile(r"^```[a-zA-Z0-9]*\n?", re.MULTILINE)
CODEBLOCK_END_PATTERN = re.compile(r"\n?```\s*$", re.MULTILINE)


def _strip_markdown_codeblocks(content: str) -> str:
    """Remove markdown code fences (```lang ... ```) wrapping file content."""
    stripped = content.strip()
    # Check if entire content is wrapped in a single code block
    if stripped.startswith("```") and stripped.endswith("```"):
        stripped = CODEBLOCK_PATTERN.sub("", stripped, count=1)
        stripped = CODEBLOCK_END_PATTERN.sub("", stripped, count=1)
        return stripped.strip() + "\n"
    return content


def _extract_files(text: str) -> list[tuple[str, str]]:
    """Extract (filepath, content) pairs from agent output."""
    return [
        (m.group(1).strip(), _strip_markdown_codeblocks(m.group(2)))
        for m in FILE_PATTERN.finditer(text)
    ]


def _build_plan_summary(chat_history: list[dict]) -> str:
    """Concatenate the planning session into a single prompt for the code generator."""
    skip_agents = {"reviewer"}
    parts = []
    for msg in chat_history:
        name = msg.get("name", msg.get("role", "unknown"))
        if name.lower() in skip_agents:
            continue
        content = msg.get("content", "")
        if content:
            parts.append(f"=== {name.upper()} ===\n{content}")
    return "\n\n".join(parts)


def generate_codebase(chat_history: list[dict], output_dir: str) -> int:
    """Generate project files from the planning session and write them to output_dir.

    Returns the number of files written.
    """
    plan_text = _build_plan_summary(chat_history)

    print("\n" + "=" * 60)
    print("  Plan Summary (sent to code generator)")
    print("=" * 60)
    print(plan_text)
    print("=" * 60 + "\n")

    # Agent that generates code
    coder = ConversableAgent(
        name="coder",
        system_message=CODEGEN_SYSTEM_MESSAGE,
        human_input_mode="NEVER",
        llm_config=code_config,
    )

    # Proxy that sends the plan and asks for continuation
    proxy = ConversableAgent(
        name="proxy",
        system_message="You send the project plan and ask for code generation.",
        human_input_mode="NEVER",
        llm_config=False,
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda msg: "###DONE###" in msg.get("content", ""),
    )

    initial_message = (
        "Here is the complete project plan. Generate ALL source code files now.\n\n"
        f"{plan_text}\n\n"
        "Generate all files using the ###FILE: path### ... ###ENDFILE### format. "
        "When finished, end with ###DONE###."
    )

    # Register a reply function so proxy asks coder to continue if needed
    def continue_reply(recipient, messages, sender, config):
        last = messages[-1].get("content", "") if messages else ""
        if "###CONTINUE###" in last and "###DONE###" not in last:
            return True, "Continue generating the remaining files. When finished, end with ###DONE###."
        return False, None

    proxy.register_reply([coder], continue_reply)

    chat_result = proxy.initiate_chat(
        coder,
        message=initial_message,
    )

    # Collect all files from every coder message
    all_files: list[tuple[str, str]] = []
    for msg in chat_result.chat_history:
        if msg.get("name") == "coder" or msg.get("role") == "assistant":
            all_files.extend(_extract_files(msg.get("content", "")))

    # Write files to disk
    written = 0
    for filepath, content in all_files:
        # Sanitize: remove leading slashes, prevent path traversal
        filepath = filepath.lstrip("/").lstrip("\\")
        if ".." in filepath:
            print(f"  Skipping suspicious path: {filepath}")
            continue

        full_path = os.path.join(output_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Created: {filepath}")
        written += 1

    return written
