---
name: moscow-prioritization
description: >
  Cut a scope list into Must, Should, Could and Won't against a fixed constraint (date, budget or
  team size). Use when scope must fit a deadline or release and stakeholders need an explicit
  "not now" list. Not for ranking by value per effort (use rice-prioritization) and not for
  time-sensitive sequencing (use cost-of-delay).
stage: prioritise
stage_order: 4
version: 0.1.0
---

# MoSCoW prioritization

Source: MoSCoW, DSDM / Agile Business Consortium (https://www.agilebusiness.org/).

## When to use
- A release, MVP or sprint has a hard date or capacity and the scope list is too long.
- Stakeholders disagree on what is essential and need a shared vocabulary.
- You need a documented "Won't (this time)" list to protect the plan.

## Inputs
- **Scope list** (required): items with a one-line description.
- **The fixed constraint** (required): the date, budget or capacity, stated as a number.
- **Rough effort per item** (required): S/M/L or person-days. Read `artifacts/prioritise/` for an
  existing RICE or triage artifact and reuse its estimates.
- **Goal of the release** (required): read `product.md` or ask for one sentence.

## Steps
1. State the constraint and the release goal at the top.
2. Apply the **Must test** to each item: if it is left out, is the release illegal, unsafe,
   unusable or pointless? Yes means Must; otherwise it cannot be Must.
3. Sort the rest: **Should** (important, painful to omit, a workaround exists), **Could** (nice
   to have, cheap to drop), **Won't this time** (agreed out of scope, not never).
4. Sum the effort of Musts. As a guideline, Musts should be about 60% of capacity or less so there
   is room for risk. If Musts exceed capacity, challenge them or cut scope inside them.
5. Check that Musts alone still deliver the release goal.
6. For each Won't, write one line on why and when it will be reconsidered.
7. Inside each bucket, order by `rice-prioritization` if a RICE artifact exists.

## Output template
```markdown
# MoSCoW: <release>  (constraint: <...>)
## Must  (effort total / capacity)
## Should
## Could
## Won't this time (reason, revisit when)
## Risks and assumptions
```

## Quality checklist
- [ ] Constraint stated as a number.
- [ ] Every Must passes the Must test with a reason.
- [ ] Musts fit inside capacity with buffer.
- [ ] Musts alone deliver the release goal.
- [ ] Every Won't has a reason and a revisit point.

## Handoff
Writes `artifacts/prioritise/<date>-moscow-<release>.md`. Consumed by `prd-template` (scope
section), `story-mapping` (release slices) and `launch-checklist`.
