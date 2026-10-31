---
name: kano-model
description: >
  Classify features by how customers feel about having or lacking them (must-be, performance,
  attractive, indifferent, reverse) using Kano survey questions. Use when deciding which features
  create delight versus table stakes, before investing in polish. Not for ranking by value per
  effort (use rice-prioritization) and not for time-sensitive ordering (use cost-of-delay).
stage: prioritise
stage_order: 5
version: 0.1.0
---

# Kano model

Source: Kano model (https://en.wikipedia.org/wiki/Kano_model).

## When to use
- You must decide between fixing basics and adding delight.
- A feature debate rests on opinion and you can survey 15 or more target users.
- Roadmap themes need a "table stakes versus differentiator" view.

## Inputs
- **Features** (required): 5-12 features, each described in one concrete sentence.
- **Survey responses** (required, or ask to design the survey): per feature, a functional answer
  ("how do you feel if the product has it?") and a dysfunctional answer ("if it does not?").
  Answers use five options: Like, Expect, Neutral, Live with, Dislike.
- **Segment** (required): who was surveyed. Never mix segments in one table.

If no responses exist, produce the survey (two questions per feature, same five options) and stop.

## Steps
1. Check the sample: fewer than 15 responses per segment means results are directional only.
2. For each response, look up the category in the evaluation table below.
3. Count categories per feature. The feature's class is the most frequent one. If the top two are
   within 10%, report it as mixed and name both.
4. Interpret: **Must-be** (taken for granted, never delights), **Performance** (more is better),
   **Attractive** (unexpected delight), **Indifferent** (skip), **Reverse** (some users dislike it).
5. Recommend: cover all must-be first, invest in performance by cost, add one or two attractive
   items, drop indifferent ones.
6. Note that attractive features decay into performance and must-be over time.

Evaluation table (rows = functional answer, columns = dysfunctional answer):

| Func \ Dysf | Like | Expect | Neutral | Live with | Dislike |
|---|---|---|---|---|---|
| Like | Q | A | A | A | O |
| Expect | R | I | I | I | M |
| Neutral | R | I | I | I | M |
| Live with | R | I | I | I | M |
| Dislike | R | R | R | R | Q |

A attractive, O performance, M must-be, I indifferent, R reverse, Q questionable (contradictory answer).

## Output template
```markdown
# Kano: <product area>  (segment: <...>, n = <...>)
| Feature | M | O | A | I | R | Q | Class |
## Recommendations
## Caveats (sample size, mixed results)
```

## Quality checklist
- [ ] Segment and sample size stated.
- [ ] Each class traces to counted responses, not opinion.
- [ ] Mixed results are labeled mixed.
- [ ] Questionable (Q) share reported; above 10% triggers a survey-wording warning.
- [ ] Recommendations follow the must-be, performance, attractive order.

## Handoff
Writes `artifacts/prioritise/<date>-kano-<area>.md`. Consumed by `product-roadmap` and
`prd-template` (requirement tiers).
