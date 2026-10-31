---
name: stakeholder-update
description: >
  Write a short progress brief for a named audience: status, progress, risks and the decisions
  or help needed. Use for recurring or ad-hoc updates to leaders, engineering or customers.
  Not for deciding who to engage (use stakeholder-mapping), not for customer-facing change
  announcements (use release-notes) and not for the end-of-launch evaluation (use post-launch-review).
stage: decide
stage_order: 4
version: 0.1.0
---

# Stakeholder update

Source: practitioner pattern (status brief with RAG status), no single canonical framework.

## When to use
- A weekly or milestone update is due.
- Something changed (slip, risk, scope cut) and affected people need to know.
- Leadership needs a decision and the ask must be unmistakable.

## Inputs
- **Audience** (required): who reads it and what they care about; read the stakeholder map if present.
- **Progress facts** (required): done, in progress, next; read `artifacts/` and `launches/`.
- **Risks and asks** (required, may be none): ask rather than assume.

Never report status you cannot support; say "unknown" and name who will confirm.

## Steps
1. Choose the audience and set the length: leaders get five lines, engineering gets detail.
2. Lead with the **overall status**: green (on track), amber (at risk), red (off track).
3. Give **one-sentence headline** of the most important change since last update.
4. List **progress** against plan: done, in progress, next, with dates only if committed.
5. List the top **risks** with impact, owner and mitigation; drop resolved ones.
6. State **decisions and help needed**: what, from whom, by when, and the cost of delay.
7. Link to detail instead of pasting it. Remove jargon the audience does not use.
8. Check: could the reader act on this in 60 seconds?

## Output template
```markdown
# Update: <initiative>  (<date>)  Status: GREEN | AMBER | RED
**Headline:**
## Progress   ## Risks (impact, owner, mitigation)
## Decisions / help needed (who, by when)
## Links
```

## Quality checklist
- [ ] Status given first and is justified.
- [ ] Asks name a person and a date.
- [ ] Risks have owners.
- [ ] Nothing unsupported is reported as fact.
- [ ] Fits the audience's time.

## Handoff
Writes `artifacts/decide/<date>-update-<initiative>.md`. Uses `decision-log` entries and feeds
`post-launch-review` as history.
