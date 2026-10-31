# PM Agent

An AI assistant for product managers. One main agent loads **31 product-management skills** on demand, remembers your product in a **markdown memory repository**, and writes drafts that a human approves.

The skills follow the seven stages of the "AI for Product Management" framework: prioritise, set direction, discover, define, decide and align, launch, and measure and learn.

> **Status: early (v0.1).** The skills, memory repository, routing eval and main agent work. The `critic` and `researcher` subagents, browser tools, and the dashboard are not built yet. See [`HANDOFF.md`](HANDOFF.md) for the full state and open issues.

## What is in it

| Layer | State | Where |
|---|---|---|
| 31 skills (7 stages) | Done | `skills/<slug>/SKILL.md` |
| Memory repository (markdown + SQLite search index) | Done | `pm_agent/memory.py`, `index.py`, `dependencies.py`, `memory_tools.py` |
| Main agent (Claude Agent SDK) | Works; cost anomaly open | `pm_agent/agent.py` |
| Skill routing eval (115 cases) | Done | `evals/`, `pm_agent/routing_eval.py` |
| `critic` / `researcher` subagents, browser tools | Not built | |
| Command-center dashboard | Not built | |

## The 31 skills

| Stage | Skills |
|---|---|
| 1. Prioritise and say no | feature-request-triage, cost-of-delay, rice-prioritization, moscow-prioritization, kano-model |
| 2. Set direction | product-vision, product-strategy, north-star-metric, product-okrs, product-roadmap |
| 3. Discover | interview-guide, interview-synthesis, jobs-to-be-done, opportunity-solution-tree, competitive-analysis |
| 4. Define | working-backwards-prfaq, prototype-brief, prd-template, story-mapping, user-stories |
| 5. Decide and align | decision-log, stakeholder-mapping, trade-off-analysis, stakeholder-update |
| 6. Launch | gtm-plan, launch-checklist, release-notes, launch-readiness-review |
| 7. Measure and learn | success-metrics, experiment-design, post-launch-review |

Each skill has a description that says what it is for and what it is not for ("Not for X, use Y"), so the agent can tell look-alikes apart (for example RICE vs. MoSCoW, or PRD vs. PR-FAQ). The stage names for stages 3, 5 and 6 are a proposal and can change.

## How it works

- **One agent, many skills.** A single main agent invokes skills as needed, with at most two subagents planned. Multi-agent setups cost several times more tokens and fit poorly when every step shares the same product context.
- **Memory.** Every skill output is a markdown artifact with frontmatter, saved under `workspace/<product>/`. Artifacts are immutable and versioned (`-v2`). A derived SQLite FTS5 index handles search.
- **Dependencies.** Some skills need earlier work first. For example, `experiment-design` needs approved `success-metrics`. The agent checks this before it writes.
- **Human approval.** The agent saves drafts only. It has no approve tool, and it cannot send, post or edit outside the workspace.
- **Isolated.** The agent does not load your personal `~/.claude` skills, hooks or plugins.

## Quick start

Requirements: Python 3.13 or newer, and [`uv`](https://docs.astral.sh/uv/) for the agent and the model-backed eval.

```bash
# Tests: stdlib only, no network
python3 -m pytest -q

# Skill routing eval, offline baseline
python3 -m pm_agent.routing_eval
```

Run the agent. It uses your Claude Code login, so no API key is needed. Use a `--root` outside this repo, or it will create a `workspace/` folder here.

```bash
# Show what loaded (plugin, 31 skills, tools)
uv run --no-project --python 3.13 --with claude-agent-sdk python -m pm_agent.agent \
  --product demo --root /tmp/pm-demo --check

# Ask for something
uv run --no-project --python 3.13 --with claude-agent-sdk python -m pm_agent.agent \
  --product demo --root /tmp/pm-demo --max-budget-usd 0.30 \
  "Prioritise these three features with RICE: ..."
```

Defaults are model `claude-opus-5-5`, effort `medium`, 40 turns and a $2.00 budget cap. Use `--model claude-haiku-5-5` for cheap tests. A trace of model, tool calls and token usage goes to stderr, and the answer goes to stdout. Live runs cost real money, and the budget cap is checked between turns only.

### Model-backed routing eval

This needs an `ANTHROPIC_API_KEY` and costs money, so it refuses to run without `--confirm-spend`.

```bash
uv run --no-project --python 3.13 --with "anthropic>=1" python -m pm_agent.routing_eval \
  --router llm --dry-run
```

## Use the skills in Claude Code

The repo is also a Claude Code plugin (`.claude-plugin/plugin.json`, name `pm-agent`). Skills appear as `pm-agent:<skill-name>`.

## Routing eval results

| Router | Accuracy (115 cases) | Hard cases (22) |
|---|---|---|
| Offline lexical baseline | 73.0% | 54.5% |
| Haiku, three blind subagent runs | 100% | 100% |

Treat the 100% with caution. The prompts were written by the same author as the descriptions, the sample is small, and it was not the real API setup. The live API router has not been run yet.

## Project layout

```
skills/           31 SKILL.md files
pm_agent/         skill loader, memory, index, dependencies, memory tools, agent, router, eval
evals/            routing_cases.json
tests/            128 tests
docs/             skill authoring guide
.claude-plugin/   plugin manifest
HANDOFF.md        current state, decisions, open issues, next steps
NOTICE            third-party credits
```

To add a skill, follow [`docs/skill-authoring.md`](docs/skill-authoring.md). A test checks that every skill has the required sections and that stage counts stay 5/5/5/5/4/4/3.

## Licence

MIT, see [`LICENSE`](LICENSE). All skill text is original. [`NOTICE`](NOTICE) credits the permissively licensed projects used for structure only.
