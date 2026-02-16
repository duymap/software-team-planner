# Software Project Planner — Multi-Agent System

A multi-agent orchestration demo using AG2 (formerly AutoGen) with a local Ollama LLM/LMStudio LLM. The system simulates a software development team that takes a project idea and produces a structured plan through collaborative agent interaction.

## Agents

| Agent | Role |
|-------|------|
| **PM** | Extracts requirements, defines scope, creates task breakdown |
| **Architect** | Designs tech stack, system architecture, data models |
| **Developer** | Creates file structure, implementation plan, code snippets |
| **Reviewer** | Reviews for quality & consistency; approves or requests revision |
| **QA** | Defines test strategy, test cases, acceptance criteria |

## Flow

```
PM → Architect → Developer → Reviewer → QA
                      ↑           │
                      └───────────┘
                    (revision loop)
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running with your model:
   ```bash
   ollama list
   ```

3. Update the model name in `config.py` if needed.

4. Run:
   ```bash
   python main.py
   ```

## Configuration

Edit `config.py` to change the model, context window size, or temperature.
