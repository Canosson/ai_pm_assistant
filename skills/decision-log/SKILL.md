---
name: decision-log
description: >
  Record ONE decision that has been made: context, options considered, the decision,
  consequences, owner and date, as a lasting record. Use right after a decision to capture why.
  Not for weighing options before deciding (use trade-off-analysis) and not for communicating
  status to others (use stakeholder-update).
stage: decide
stage_order: 1
version: 0.1.0
---

# Decision log

Source: Architecture Decision Records (https://adr.github.io/).

## When to use
- A product decision was just made and the reasoning will be forgotten in a month.
- Someone asks "why did we do it this way?"
- A decision reverses an earlier one and the change must be traceable.

## Inputs
- **The decision** (required): what was decided.
- **Context and options** (required): the problem, and the alternatives that were considered.
- **Decision owner and date** (required).
- **Evidence** (optional): read the `trade-off-analysis` artifact if one exists.

Do not invent options that were not discussed.

## Steps
1. Give the decision a **numbered title** in the form `DL-<n>: <verb phrase>`.
2. Write the **context**: the problem, constraints and forces in 3-6 sentences.
3. List the **options considered**, including doing nothing, each with its main upside and downside.
4. State the **decision** in one sentence and the **reason** it won.
5. List the **consequences**: what gets easier, what gets harder, new risks.
6. Add the **owner, date, status** (proposed, accepted, superseded) and a **revisit trigger**.
7. If it replaces an earlier decision, link it and mark that one superseded.
8. Update the index of decisions.

## Output template
```markdown
# DL-<n>: <title>
Status: accepted | superseded by DL-<m>   Owner:   Date: YYYY-MM-DD
## Context   ## Options considered   ## Decision and reason
## Consequences   ## Revisit when
```

## Quality checklist
- [ ] One decision per record.
- [ ] Options include doing nothing.
- [ ] Reason is stated, not only the outcome.
- [ ] Owner, date and status present.
- [ ] Superseded records are linked both ways.

## Handoff
Writes `decisions/DL-<n>-<slug>.md` and updates `decisions/index.md`. Consumed by `prd-template`
(open questions), `stakeholder-update` and `post-launch-review`.
