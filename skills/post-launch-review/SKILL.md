---
name: post-launch-review
description: >
  Review a launched feature against its targets and decide keep, fix or remove, with what
  happened, why, lessons and next actions in a blameless format. Use once the measurement window
  from success-metrics has passed. Not for defining success beforehand (use success-metrics),
  not for designing the test (use experiment-design) and not for the pre-launch gate
  (use launch-readiness-review).
stage: measure
stage_order: 3
version: 0.1.0
---

# Post-launch review

Source: blameless postmortem practice (https://sre.google/sre-book/postmortem-culture/).

## When to use
- The measurement window of a launch or experiment has ended.
- Stakeholders ask "did it work and what do we do now?"
- You want lessons recorded so the next launch is better.

## Inputs
- **Success metrics artifact** (required): read `artifacts/measure/` for targets and the decision rule.
- **Actual results** (required): the measured values and where they came from.
- **Launch timeline and changes** (optional): read `launches/`.
- **Qualitative signals** (optional): support tickets, interviews, feedback.

Never fill in results that were not measured; mark them "not measured" and say what is needed.

## Steps
1. Restate the goal, the targets and the decision rule agreed before launch.
2. Compare **actual vs target** per metric, including guardrails. Note data quality caveats.
3. Explain **what happened** as a timeline of facts, not blame.
4. Analyze **why**: separate what the evidence shows from hypotheses, and label each.
5. Apply the decision rule: **keep**, **fix** (name what and the next test) or **remove**.
6. Capture **lessons**: what to repeat, what to change, what surprised the team.
7. List **next actions** with owner and date, including updates to `product.md` or the roadmap.
8. Share the summary with `stakeholder-update`.

## Output template
```markdown
# Post-launch review: <feature>  (window: <dates>)
## Goal and decision rule
| Metric | Target | Actual | Verdict |
## What happened   ## Why (evidence vs hypothesis)
## Decision: keep | fix | remove
## Lessons   ## Next actions (owner, date)
```

## Quality checklist
- [ ] Targets and decision rule match the pre-launch artifact.
- [ ] Unmeasured results are marked, not guessed.
- [ ] Evidence and hypotheses are labeled apart.
- [ ] Decision follows the decision rule or explains the deviation.
- [ ] Blameless tone; actions have owners and dates.

## Handoff
Writes `artifacts/measure/<date>-post-launch-review-<slug>.md`. Feeds `product-okrs` for the next
cycle, `feature-request-triage` (new requests) and `decision-log`.
