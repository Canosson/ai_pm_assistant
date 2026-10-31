---
name: prd-template
description: >
  Write a product requirements document engineers will actually read: problem, goals, non-goals,
  users, requirements, success metrics, risks and open questions. Use once an idea is accepted
  and needs a spec. Not for the pitch (use working-backwards-prfaq), not for story-level detail
  (use user-stories) and not for release scope cuts (use moscow-prioritization).
stage: define
stage_order: 3
version: 0.1.0
---

# PRD template

Source: product requirements document structure (https://www.atlassian.com/agile/product-management/requirements).

## When to use
- An initiative passed triage or the PR/FAQ and engineering needs a shared spec.
- A feature has unclear scope or several owners.
- You need a single source for what is in, what is out and how success is judged.

## Inputs
- **Problem and evidence** (required): from research, triage or PR/FAQ artifacts.
- **Goal link** (required): the objective or North Star it serves; read `product.md`.
- **Scope decision** (optional): `moscow-prioritization` artifact if one exists.
- **Constraints** (optional): technical, legal, timeline.

Do not invent requirements or numbers. Unknowns go in Open questions.

## Steps
1. Write a **summary**: problem, who is affected, proposed solution, in five sentences or fewer.
2. State **goals** and **non-goals**. Non-goals must be real exclusions, not afterthoughts.
3. Describe **users and use cases**: who, in what situation, what outcome.
4. List **requirements** as numbered, testable statements, grouped Must / Should / Could.
5. Define **success metrics** with baseline, target and window (see `success-metrics`).
6. Add **design and technical notes**: links, constraints, dependencies. No solution detail the
   engineers should decide.
7. List **risks and assumptions** with an owner and a mitigation each.
8. List **open questions** with owner and due date, and the decision log link.
9. Add the **rollout and launch notes** in two lines, linking to `launch-checklist`.

## Output template
```markdown
# PRD: <title>  (status, owner, date)
## Summary   ## Goals / Non-goals   ## Users and use cases
## Requirements (R1..Rn, priority)   ## Success metrics
## Design and technical notes   ## Risks and assumptions
## Open questions   ## Rollout
```

## Quality checklist
- [ ] Problem stated before the solution.
- [ ] Non-goals present and real.
- [ ] Every requirement is testable and prioritized.
- [ ] Success metrics have baseline, target and window.
- [ ] Open questions have owner and due date.

## Handoff
Writes `artifacts/define/<date>-prd-<slug>.md`. Consumed by `user-stories`, `story-mapping`,
`success-metrics` and `launch-readiness-review`.
