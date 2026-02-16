# Software Project Planner — Multi-Agent System

A multi-agent orchestration with local LLMs via Ollama or LM Studio. The system simulates a software development team that takes a project idea and produces a structured plan through collaborative agent interaction.

## Agents

The system uses **two LLM configurations** — a reasoning model for planning/analysis agents and a code model for implementation agents:

| Agent | Role | LLM Config |
|-------|------|------------|
| **PM** | Extracts requirements, defines scope, creates task breakdown | Reasoning |
| **Architect** | Designs tech stack, system architecture, data models, data flow | Reasoning |
| **Developer** | Creates file structure, implementation plan, code snippets, API design | Code |
| **Reviewer** | Reviews for quality, consistency, and feasibility; approves or requests revision | Code |
| **QA** | Defines test strategy, test cases, acceptance criteria; gives final sign-off | Reasoning |

## Flow

```
User Input
    │
    ▼
   PM ──► Architect ──► Developer ──► Reviewer ──► QA
                            ▲              │
                            └──────────────┘
                          (if REVISION NEEDED)
```

The flow is **deterministic** — a custom `select_next_speaker` function in `orchestrator.py` controls which agent speaks next (no LLM-based routing).

### How it works

1. **PM** receives the user's project idea and outputs requirements, scope, and task breakdown.
2. **Architect** reads the PM's output and designs the tech stack, architecture, data models, and data flow.
3. **Developer** reads all prior messages and produces file structure, implementation plan, code snippets, and API design.
4. **Reviewer** evaluates the plan and outputs either:
   - `APPROVED` — flow continues to QA.
   - `REVISION NEEDED: ...` — flow loops back to Developer for revisions.
5. **QA** defines the test strategy and ends the session with `FINAL SIGN-OFF: Project plan is complete.`

### Termination conditions

- QA outputs a message containing `"final sign-off"` (case-insensitive).
- Or the conversation reaches the `max_round=15` safety limit.

### Message passing

All agents share a single conversation history via `GroupChat.messages`. Each agent sees the **entire chat history** when generating its response — there is no explicit handoff between agents.

## Project Structure

```
multi-agents/
├── config.py         # LLM provider/model configuration (reasoning + code)
├── agents.py         # Agent definitions and system prompts
├── orchestrator.py   # GroupChat, speaker selection, termination logic
├── main.py           # Entry point — starts the planning session
├── requirements.txt  # Python dependencies
├── .env.example      # Example environment variables
└── .env              # Local environment variables (not committed)
```

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the example env file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Ensure your LLM provider is running:
   - **Ollama**: `ollama list` to verify models are available
   - **LM Studio**: start the local server

4. Run:
   ```bash
   python main.py
   ```

## Configuration

All settings are controlled via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | `ollama` or `lmstudio` |
| `LLM_BASE_URL` | `http://localhost:11434` | LLM server URL |
| `LLM_NUM_CTX` | `8192` | Context window size |
| `REASONING_MODEL` | `qwen3:latest` | Model for PM, Architect, QA |
| `REASONING_TEMPERATURE` | `0.7` | Temperature for reasoning agents |
| `CODE_MODEL` | `qwen3:latest` | Model for Developer, Reviewer |
| `CODE_TEMPERATURE` | `0.3` | Temperature for code agents |
