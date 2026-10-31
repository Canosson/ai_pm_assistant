---
name: launch-checklist
description: >
  Build the cross-functional task list that leads to launch day: workstreams, tasks, owners,
  dates and dependencies. Use to organize the work of shipping. Not for the market strategy
  (use gtm-plan), not for the go/no-go judgment at the gate (use launch-readiness-review) and
  not for customer-facing text (use release-notes).
stage: launch
stage_order: 2
version: 0.1.0
---

# Launch checklist

Source: practitioner pattern; related practice: launch coordination (https://sre.google/sre-book/launch-checklist/).

## When to use
- A launch date exists and many teams must finish things before it.
- Tasks live in many heads and nobody can see what is blocking.
- You need a single list to run weekly launch meetings from.

## Inputs
- **Launch scope and date** (required): from the PRD and `gtm-plan`.
- **Teams involved** (required): product, engineering, QA, design, marketing, sales, support, legal.
- **Tier of launch** (optional): from `gtm-plan`.

Never assign an owner or date yourself; propose and mark "proposed" until confirmed.

## Steps
1. Set the **launch date** and work backwards to key milestones.
2. Create **workstreams**: build and QA, data and analytics, marketing, sales enablement, support
   and docs, legal and compliance, operations and rollout.
3. For each, list **tasks** with an owner, a due date and a "done" definition.
4. Mark **dependencies** and the **critical path**.
5. Add the **rollout plan**: flags, phases, who is exposed first, how to roll back.
6. Add **post-launch tasks**: monitoring period, metrics check, feedback review.
7. Set the **review cadence** and where status is tracked.
8. Flag tasks that are blocked, unowned or past due.

## Output template
```markdown
# Launch checklist: <launch>  (launch date: <date>)
| Workstream | Task | Owner | Due | Done when | Status | Depends on |
## Critical path   ## Rollout and rollback   ## Post-launch tasks
```

## Quality checklist
- [ ] Every task has an owner, a date and a done definition.
- [ ] Critical path identified.
- [ ] Rollback is defined.
- [ ] Post-launch tasks included.
- [ ] Proposed vs confirmed owners are distinguished.

## Handoff
Writes `artifacts/launch/<date>-checklist-<launch>.md`. Its status is the input to
`launch-readiness-review`.
