---
name: success-metrics
description: >
  Define how one feature or launch will be judged: a primary metric, supporting and guardrail
  metrics, baselines, targets and a measurement window. Use before building or launching so
  success is agreed in advance. Not for the product-wide measure (use north-star-metric) and
  not for designing a controlled test (use experiment-design).
stage: measure
stage_order: 1
version: 0.1.0
---

# Success metrics

Source: HEART framework, Google (https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/).

## When to use
- A PRD or launch lacks measurable success criteria.
- Teams disagree after launch about whether it worked.
- A feature must be tied back to an objective or the North Star.

## Inputs
- **Goal of the feature** (required): read the PRD and `product.md`.
- **User journey** (required): where the feature sits.
- **Available data** (required): what can be measured today and where.
- **Baselines** (optional): current values; mark unknown ones explicitly.

## Steps
1. State the goal in one sentence and the user behavior that shows it worked.
2. Map candidate metrics to **HEART**: Happiness, Engagement, Adoption, Retention, Task success.
   Keep only the dimensions that match the goal.
3. Choose **one primary metric**, defined precisely: numerator, denominator, window.
4. Add 2-3 **supporting metrics** that explain the primary one.
5. Add 1-2 **guardrail metrics** that must not worsen (performance, support load, churn).
6. Set **baseline and target** for each; if the baseline is unknown, plan to measure it first.
7. Define the **measurement window**, the data source and the owner.
8. Write the **decision rule**: what result means keep, fix or remove.

## Output template
```markdown
# Success metrics: <feature>
| Type | Metric | Definition | Baseline | Target | Window | Source | Owner |
Primary / Supporting / Guardrail
## Decision rule (keep / fix / remove)
## Unknowns to resolve before launch
```

## Quality checklist
- [ ] Exactly one primary metric, precisely defined.
- [ ] At least one guardrail.
- [ ] Baselines given or measurement planned.
- [ ] Every metric has a source and owner.
- [ ] Decision rule agreed before launch.

## Handoff
Writes `artifacts/measure/<date>-success-metrics-<slug>.md`. Consumed by `experiment-design`,
`launch-readiness-review` and `post-launch-review`.
