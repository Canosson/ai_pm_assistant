---
name: launch-readiness-review
description: >
  Hold the go/no-go gate BEFORE launch: judge checklist status, open risks, metrics readiness
  and rollback, and output a decision. Use in the final days before release. Not for building the
  task list (use launch-checklist) and not for evaluating results AFTER launch
  (use post-launch-review).
stage: launch
stage_order: 4
version: 0.1.0
---

# Launch readiness review

Source: launch readiness / production readiness review (https://sre.google/sre-book/launch-checklist/).

## When to use
- The launch date is close and someone must decide go, delay or no-go.
- Teams disagree on whether the product is ready.
- A launch has risk (data, security, scale, legal) that needs explicit sign-off.

## Inputs
- **Launch checklist status** (required): read `artifacts/launch/`.
- **Success metrics and tracking readiness** (required): from `success-metrics`.
- **Open risks and bugs** (required): ask for current severity counts and known issues.
- **Rollback plan** (required).

Never mark an item ready without evidence; unverified means not ready.

## Steps
1. Restate the **launch scope, date and decision owner**.
2. Review each **readiness area** with a verdict (ready, ready with risk, not ready) and evidence:
   product and QA, performance and reliability, security and privacy, legal and compliance,
   analytics and success metrics, support and docs, go-to-market, rollback.
3. List **open issues**: severity, owner, workaround, decision needed.
4. Check the **rollback plan**: trigger, who decides, how long it takes.
5. Check **monitoring**: what will be watched in the first 24-72 hours and who is on call.
6. Decide: **go**, **go with conditions** (named, with deadlines), **delay** (new date and gate
   to pass) or **no-go**.
7. Record dissent and accepted risks by name.
8. Log the decision in `decision-log`.

## Output template
```markdown
# Launch readiness: <launch>  (decision owner: <name>, <date>)
| Area | Verdict | Evidence | Owner |
## Open issues   ## Rollback and monitoring
## Decision: GO | GO WITH CONDITIONS | DELAY | NO-GO
## Conditions, accepted risks, dissent
```

## Quality checklist
- [ ] Every area has a verdict backed by evidence.
- [ ] Rollback trigger, owner and time are stated.
- [ ] Conditions have owners and deadlines.
- [ ] Accepted risks are named.
- [ ] Decision logged.

## Handoff
Writes `artifacts/launch/<date>-readiness-<launch>.md` and a `decision-log` entry. After launch,
evaluation moves to `post-launch-review`.
