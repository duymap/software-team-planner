# Software Project Planner — Multi-Agent System with AG2 + Ollama

## Context

Build a multi-agent orchestration demo using the AG2 framework (formerly AutoGen) with a local Ollama LLM. The system simulates a software development team that takes a user's project idea and produces a structured project plan through collaborative agent interaction.

## Architecture Overview

```
User Input (project idea)
       │
       ▼
┌─────────────┐
│  PM Agent   │  ← Breaks down requirements, manages flow
└──────┬──────┘
       │
       ▼
┌──────────────┐
│  Architect   │  ← Designs technical architecture
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Developer   │  ← Writes implementation plan & code snippets
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Reviewer    │  ← Reviews quality, can send back to Developer
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  QA Agent    │  ← Defines test strategy, finalizes
└──────────────┘
```

**Orchestration pattern:** GroupChat with **custom speaker selection function** + **constrained transitions**

This gives us:
- Deterministic flow (PM → Architect → Developer → Reviewer → QA)
- Feedback loops (Reviewer can reject back to Developer)
- Intelligent termination (QA approves → done)

## Files to Create

```
multi-agents/
├── requirements.txt          # Dependencies
├── config.py                 # LLM & app configuration
├── agents.py                 # Agent definitions (5 agents)
├── orchestrator.py           # GroupChat, speaker selection, transitions
├── main.py                   # Entry point — accepts user input, runs pipeline
└── README.md                 # How to run the project
```

## Step-by-Step Implementation

### Step 1: `requirements.txt`

```
ag2[ollama]
```

### Step 2: `config.py` — LLM Configuration

- Define Ollama LLM config pointing to local model
- Model name as a variable (easy to change)
- Config structure:
  ```python
  llm_config = LLMConfig(
      api_type="ollama",
      model="<user's model tag>",
      client_host="http://localhost:11434",
      num_ctx=8192,
      temperature=0.7,
  )
  ```

### Step 3: `agents.py` — Define 5 Specialized Agents

Each agent = `ConversableAgent` with:
- Unique `name`
- Detailed `system_message` (role, responsibilities, output format)
- `description` (used by GroupChatManager for routing)
- Shared `llm_config` from config.py

| Agent | Name | Role |
|-------|------|------|
| PM | `pm` | Analyzes user request, extracts requirements, defines scope, creates task breakdown |
| Architect | `architect` | Designs system architecture, tech stack, component diagram, data flow |
| Developer | `developer` | Creates implementation plan, file structure, key code snippets, API design |
| Reviewer | `reviewer` | Reviews architect & developer output for quality, consistency, feasibility. Approves or requests revision |
| QA | `qa` | Defines test strategy, test cases, acceptance criteria, gives final sign-off |

### Step 4: `orchestrator.py` — Custom GroupChat Orchestration

**Transition graph (constrained):**
```python
allowed_transitions = {
    pm:        [architect],
    architect: [developer],
    developer: [reviewer],
    reviewer:  [developer, qa],   # reject → developer, approve → qa
    qa:        [pm],              # final summary back to PM or terminate
}
```

**Custom speaker selection function:**
```python
def select_next_speaker(last_speaker, groupchat):
    last_msg = groupchat.messages[-1]["content"].lower()

    if last_speaker == pm:
        return architect
    elif last_speaker == architect:
        return developer
    elif last_speaker == developer:
        return reviewer
    elif last_speaker == reviewer:
        if "approved" in last_msg:
            return qa
        else:
            return developer  # feedback loop
    elif last_speaker == qa:
        return None  # terminate
```

**GroupChat setup:**
- `max_round=15` (enough for 1-2 revision cycles)
- `send_introductions=True`
- `speaker_selection_method=select_next_speaker`

### Step 5: `main.py` — Entry Point

- Accept project idea from user (command line input or hardcoded example)
- Import agents and orchestrator
- PM initiates chat with GroupChatManager
- Print final conversation summary

## Verification

1. Install: `pip install -r requirements.txt`
2. Ensure Ollama running with model: `ollama list`
3. Run: `python main.py`
4. Verify: PM → Architect → Developer → Reviewer → QA flow completes
5. Verify feedback loop: Reviewer rejection routes back to Developer
