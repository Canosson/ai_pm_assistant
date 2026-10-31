---
name: experiment-design
description: >
  Design a controlled experiment (A/B test): hypothesis, metrics, minimum detectable effect,
  sample size, duration and decision rule, written before launch. Use when a change can be
  tested on live traffic. Not for defining feature success criteria (use success-metrics) and not
  for testing a mock with a few users (use prototype-brief).
stage: measure
stage_order: 2
version: 0.1.0
---

# Experiment design

Source: Trustworthy Online Controlled Experiments, Kohavi, Tang, Xu (https://experimentguide.com/).

## When to use
- A change has enough traffic to be tested with a control group.
- Teams want to ship on opinion and a test could settle it.
- A past test was inconclusive because it was under-powered or stopped early.

## Inputs
- **Hypothesis** (required): change, audience, expected effect.
- **Primary metric and guardrails** (required): from `success-metrics`.
- **Baseline rate and daily traffic** (required): ask for the numbers; never guess them.
- **Constraints** (optional): maximum duration, risk tolerance.

## Steps
1. Write the hypothesis: "If we <change> for <audience>, then <metric> will <direction> because <reason>".
2. Fix the **randomization unit** (user, account, session) and the eligible population.
3. Fix the **primary metric**, 1-2 guardrails and any segments, before launch.
4. Set the **minimum detectable effect** (the smallest change worth acting on) and the
   significance level (default 5%) and power (default 80%).
5. Compute the **sample size** per variant from the baseline and the MDE, then the duration from
   traffic. Round the duration up to whole weeks to cover weekly cycles.
6. Write the **decision rule**: ship, iterate or stop for each outcome, including a flat result.
7. List pitfalls to guard against: peeking early, sample ratio mismatch, novelty effect,
   overlapping tests, many metrics without correction.
8. Define the checks: A/A or sanity metrics, logging verified, owner and review date.

## Output template
```markdown
# Experiment: <name>
- Hypothesis / Unit / Population
- Primary metric, guardrails, segments
- MDE, alpha, power, sample size per variant, duration
## Decision rule
## Risks and checks
```

## Quality checklist
- [ ] One primary metric fixed before launch.
- [ ] MDE, power and sample size are stated with the inputs used.
- [ ] Duration covers whole weeks.
- [ ] Decision rule covers a flat result.
- [ ] Peeking and mismatch checks planned.

## Handoff
Writes `artifacts/measure/<date>-experiment-<slug>.md`. Results are analyzed in
`post-launch-review`.
