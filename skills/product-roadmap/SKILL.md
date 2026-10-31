---
name: product-roadmap
description: >
  Build an outcome-based Now/Next/Later roadmap from OKRs and prioritized opportunities. Use when
  stakeholders need to see direction and sequencing without date promises. Not for goals
  (use product-okrs), not for ranking items (use rice-prioritization) and not for sprint or
  delivery plans.
stage: direction
stage_order: 5
version: 0.1.0
---

# Product roadmap

Source: goal-oriented roadmap (Roman Pichler, https://www.romanpichler.com/blog/goal-oriented-product-roadmap/)
and Now/Next/Later (https://www.prodpad.com/blog/invented-now-next-later-roadmap/).

## When to use
- Leadership or customers ask "what are you working on and what is next?"
- Priorities were decided and need to be communicated as a sequence.
- A roadmap lists features with dates and keeps slipping.

## Inputs
- **OKRs** (required): read `artifacts/direction/` or `product.md`.
- **Prioritized items** (required): read `artifacts/prioritise/` (RICE, cost of delay, MoSCoW, Kano).
- **Audience** (required): internal team, leadership or customers; this sets the detail level.
- **Dependencies and capacity** (optional).

## Steps
1. Choose the audience and set the detail: customer-facing means themes only.
2. Create three columns: **Now** (committed, in progress), **Next** (planned, shaped),
   **Later** (direction, unshaped).
3. Frame each entry as a problem or outcome plus the objective it serves, not a feature name.
4. Place items using the prioritization artifacts; fixed-date items follow `cost-of-delay`.
5. Limit Now to what capacity can finish; push the rest down and say so.
6. Show dependencies and risks for Now and Next items.
7. Add confidence per column: Now high, Next medium, Later low. No dates beyond Now.
8. Write the change log: what moved since the last version and why.

## Output template
```markdown
# Roadmap (<audience>, <date>)
| Now | Next | Later |
|-----|------|-------|
| outcome - objective - confidence | ... | ... |
## Dependencies and risks
## What changed since last version
```

## Quality checklist
- [ ] Every entry names an outcome and the objective it supports.
- [ ] Now fits capacity.
- [ ] No dates outside Now.
- [ ] Detail suits the audience.
- [ ] Change log present.

## Handoff
Writes `artifacts/direction/<date>-roadmap.md`. Consumed by `stakeholder-update`, `story-mapping`
and `launch-checklist`.
