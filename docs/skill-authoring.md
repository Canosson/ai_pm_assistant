# Skill authoring spec

Every PM skill is one folder: `skills/<slug>/SKILL.md` (flat, so it loads as a Claude Code / Agent SDK plugin).
The stage lives in frontmatter, not in the folder path.

## Frontmatter (all fields required)

```yaml
---
name: rice-prioritization          # = folder name, kebab-case
description: >                     # <= 400 chars. What it does + WHEN to use + "Not for X (use Y)".
  Score and rank a list of initiatives with RICE (Reach, Impact, Confidence, Effort).
  Use when the user has a candidate list and needs a defensible ranking.
  Not for deciding scope under a fixed deadline (use moscow-prioritization) or
  for time-critical items (use cost-of-delay).
stage: prioritise                  # prioritise|direction|discover|define|decide|launch|measure
stage_order: 3                     # position inside the stage (1..N)
version: 0.1.0
---
```

The `description` is what the agent sees for routing, so it must separate the skill from its
look-alikes. Always include a "Not for ... (use ...)" line when a look-alike exists.

## Body sections (in this order)

1. **When to use**: 2-4 bullets, concrete triggers.
2. **Inputs**: what to read from memory (`workspace/<product>/...`) and what to ask the user.
   Mark each `required` or `optional`. If a required input is missing, ask; never invent it.
3. **Steps**: numbered, imperative, 5-9 steps.
4. **Output template**: the exact Markdown the artifact must follow.
5. **Quality checklist**: 4-8 checkable items the `critic` subagent uses.
6. **Handoff**: which artifact is written (`artifacts/<stage>/<date>-<slug>.md`, frontmatter
   `skill`, `stage`, `status: draft`, `inputs: []`, `created: YYYY-MM-DD`) and which downstream
   skills consume it.

## Rules

- Original wording only. Cite the canonical framework by name and URL in a `Source:` line.
- Under 150 lines. Put long reference tables in `skills/<slug>/reference.md` (loaded on demand).
- No tool calls to outward systems inside a skill; outward actions go through the approval gate.
- Prioritization logic lives only in the stage-1 skills; other skills link to them instead of re-implementing.
