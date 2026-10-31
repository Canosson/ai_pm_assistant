---
name: product-okrs
description: >
  Write quarterly product OKRs: 1-3 outcome-based Objectives, each with 3-5 measurable Key
  Results, tied to the strategy and North Star. Use at planning time or when goals are a list of
  tasks. Not for the long-term destination (use product-vision) and not for the plan of work
  (use product-roadmap).
stage: direction
stage_order: 4
version: 0.1.0
---

# Product OKRs

Source: What Matters OKR guide (https://www.whatmatters.com/faqs/okr-meaning-definition-example).

## When to use
- A new quarter or cycle starts and the team needs shared goals.
- Existing goals read as outputs ("ship X") and not outcomes.
- You need to connect daily work to the strategy.

## Inputs
- **Strategy and North Star** (required): read `product.md`.
- **Cycle** (required): the quarter and its dates.
- **Last cycle's OKRs and results** (optional): read `artifacts/direction/`.
- **Capacity** (optional): the team size, to avoid overcommitting.

## Steps
1. Pick 1-3 priorities from the strategy that matter most this cycle. More than 3 means no focus.
2. Write each **Objective**: qualitative, inspiring, one sentence, no numbers.
3. Write 3-5 **Key Results** per Objective: each a measurable outcome with a baseline and a target
   (`from X to Y by <date>`). Outputs such as "launch feature" are not Key Results.
4. Link at least one Key Result to the North Star or an input metric.
5. Set the ambition: aim for about 70% attainment on stretch goals; committed goals target 100%.
6. Check each Key Result is measurable now: name the data source.
7. List dependencies and risks, and what is explicitly out of focus this cycle.
8. Define the check-in cadence and how scoring works (0.0-1.0).

## Output template
```markdown
# OKRs <cycle>
## Objective 1: <...>
| KR | Baseline | Target | Source | Owner | Committed/Stretch |
## Objective 2 ...
## Not in focus this cycle
## Dependencies and risks
```

## Quality checklist
- [ ] 1-3 Objectives, no numbers inside them.
- [ ] 3-5 Key Results each, all outcomes with baseline and target.
- [ ] Linked to the North Star or an input metric.
- [ ] Every Key Result has a data source and owner.
- [ ] Out-of-focus list present.

## Handoff
Writes `artifacts/direction/<date>-okrs-<cycle>.md`; after approval it updates `product.md`.
Consumed by `product-roadmap`, `success-metrics` and `post-launch-review`.
