# Handoff: PM Agent (product-manager-assistant)

Status as of 2026-10-31. Nothing is committed: this folder is untracked in the parent git repo.

## What this is
A self-contained, packageable assistant for product managers, organised around the 7-stage / 31-skill
framework in `AI Product Manager.gif`. Four layers were planned: an agent stack, a memory
repository, tool/browser integration, and a command-center dashboard. The plan is in
`~/.claude/plans/quirky-percolating-hamming.md` (outside the repo; its "orchestrator" wording is stale,
see Decisions).

## What exists vs. what does not
| Plan step | State |
|---|---|
| 1. 31 skills (`skills/<slug>/SKILL.md`) | Done. 5/5/5/5/4/4/3 per stage, lint-tested. |
| 2. Memory repository + index + dependencies | Done and reviewed (`pm_agent/memory*.py`, `index.py`, `dependencies.py`). |
| Routing eval | Done (`evals/routing_cases.json`, `pm_agent/routing_eval.py`, `llm_router.py`). |
| 3. Main agent + skill loader | Built and run live on Haiku (`pm_agent/agent*.py`). Cost anomaly open, see below. |
| 4. `critic` subagent | Not built. `agents/` does not exist yet; the loader handles it when it does. |
| 5. `researcher` subagent + Playwright MCP + approval gate | Not built. |
| 6. Dashboard (FastAPI + HTMX) | Not built. |
| 7. README / packaging | Not done. `README.md` is empty (pyproject references it, so keep the file). |

## Run it
```bash
python3 -m pytest -q                                   # 128 tests, stdlib only, no network
python3 -m pm_agent.routing_eval                       # offline baseline router

# Model-backed router (needs the anthropic 1.x SDK and an API key; costs money)
uv run --no-project --python 3.13 --with "anthropic>=1" python -m pm_agent.routing_eval --router llm --dry-run
#   ... --router llm --limit 10 --model claude-haiku-5-5 --confirm-spend    # refuses without the flag

# The agent (uses your Claude Code login; no API key needed)
uv run --no-project --python 3.13 --with claude-agent-sdk python -m pm_agent.agent \
  --product demo --root /tmp/pm-demo --model claude-haiku-5-5 --check      # shows what loaded
uv run --no-project --python 3.13 --with claude-agent-sdk python -m pm_agent.agent \
  --product demo --root /tmp/pm-demo --model claude-haiku-5-5 --max-budget-usd 0.30 "your request"
```
Traces (model, tool calls, per-turn usage, tool-result sizes, usage by model) go to stderr; the answer to stdout.
Use `--root` outside the project, or you create `workspace/` here.

## Decisions (and why)
- **One main agent + 31 skills + at most 2 subagents** (`researcher`, `critic`), not 10 agents. Anthropic's guidance:
  start simple; multi-agent costs 3-10x tokens and fits poorly when agents share context and depend on each
  other, which the PM pipeline does. A preliminary paper (arXiv 2601.04748) says skill selection degrades past
  ~20-30 skills, hence distinct descriptions with "Not for X (use Y)" lines and the routing eval.
- **Flat `skills/<slug>/`**, stage in frontmatter; the repo is also a Claude Code plugin (`.claude-plugin/plugin.json`).
- **All skill text is original.** `NOTICE` lists the Apache-2.0/MIT sources used for structure only. The `design`,
  `data` and `zizi-skills` plugins have no checked license: do not copy from them.
- **Memory = markdown files + derived SQLite index.** Artifacts are immutable; approval writes a new version. Only
  approved artifacts may update `product.md` (marker-fenced sections).
- **The agent has only `Skill` + 6 memory tools.** No Read/Glob/Grep (not confined to the workspace), no Write/Bash/web.
  `write_artifact` saves drafts only; there is deliberately **no approve tool** (a human approves, via the future dashboard).
- `setting_sources=[]`: the agent never inherits the developer's `~/.claude` skills, hooks or plugins.
- Default model `claude-opus-5-5`, effort `medium`, `max_budget_usd` 2.0, 40 turns.

## Live findings
- Skills load: `--check` shows the plugin and 31 `pm-agent:*` skills; the agent called `Skill pm-agent:rice-prioritization`.
- A real run wrote a correct draft (RICE scores right, flagged that "Q3" was already past) in run 1; run 2 was cut off by its budget cap.
- **Bug found only by the real SDK:** with `tools` set, `"Skill"` must be listed or no skill can be invoked. Fixed and tested.
- **Cost anomaly (unresolved).** Fixed overhead is small: about $0.001 and ~8k tokens per Haiku turn (diagnostics: full setup
  5.2k cache-write; without plugin/skills 2.8k; without memory server 6.2k). But the two RICE runs cost $0.1974 and $0.1945
  and wrote about 197k cache tokens in 4 turns, at a price implying prompts over 100K tokens. Cause not identified; the
  per-turn usage and tool-result-size tracing was added to find it. Next run will show it.
- The `--max-budget-usd` cap is checked between turns; one expensive turn can overshoot it.
- Total agent spend so far is about $0.40. The "$65 session cost" warnings are the whole Claude Code session.

## Routing eval
115 cases (3 plain per skill + 22 hard boundary cases), written by the same author as the descriptions.
Offline lexical baseline: 73.0% overall, 54.5% hard. Haiku via three independent subagents: 115/115 (100%), blind and
shuffled, transcripts confirmed not to read the answer key. Treat 100% with caution (friendly prompts, small sample,
not the API setup). `llm_router.py` has **never been run against the live API** (no key was available); only its request
shape is unit-tested with a fake client.

## Open issues, most important first
1. Find the cost anomaly (rerun the RICE prompt with the new tracing, cap $0.30).
2. Whether the model can still see the 18 bundled Claude Code skills. `skills=[...]` limits invocation; the init list
   shows all 49 discovered. Verify with a prompt that asks the model what it can invoke.
3. `acknowledge_missing` is not a real gate: the agent can set it. The bypass is recorded in the artifact (`bypassed:`),
   but a true gate needs the dashboard's human approval.
4. Add harder, messier routing cases (ideally written by real PMs) and run the API router for the real number.
5. Stage 3, 5 and 6 skill names are my proposal; the GIF does not list them and the user never confirmed them.
6. Skill `Source:` URLs came from a research agent's memory and were not fetched.
7. The final batch of review fixes was not re-reviewed; test coverage vs the 80% target was never measured.
8. `.python-version` and `requires-python` say 3.14 but this machine runs 3.13; everything here is stdlib and works on both.
9. Editor warning: `claude_agent_sdk` unresolved in Pylance because the SDK is imported lazily and installed only via `uv --with`.

## Housekeeping
- `.claude/settings.local.json` sets `ECC_GATEGUARD=off` for this project (gitignored). Remove it when the build is done.
- Removed in cleanup: `.pytest_cache/`, `__pycache__/` folders and the unused `main.py`. Kept `README.md` (empty), the GIF,
  `.python-version`.
- Temporary test workspaces from live runs are under `/tmp/pm-*`; safe to delete.

## File map
`skills/` 31 skills | `pm_agent/` skills.py (loader), memory.py, index.py, dependencies.py, memory_tools.py, agent.py,
agent_prompt.py, agent_trace.py, agents.py, llm_router.py, routing_eval.py | `tests/` 128 tests | `evals/routing_cases.json` |
`docs/skill-authoring.md` (skill template and rules) | `.claude-plugin/plugin.json` | `NOTICE`

## Next steps
1. Cost anomaly run (above), then fix whatever it reveals.
2. `critic` subagent (`agents/critic.md`, Claude Code subagent format) checking artifacts against each skill's quality checklist.
3. `researcher` subagent with Playwright MCP for competitive-analysis; add an approval gate for outward actions.
4. Dashboard: pipeline, activity (reads an `events.jsonl` the agent must start writing), artifacts, approvals.
5. README, packaging, and a decision on which model the product defaults to once cost is understood.
