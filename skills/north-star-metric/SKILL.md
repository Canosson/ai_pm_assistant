---
name: north-star-metric
description: >
  Choose the single North Star Metric that captures the value customers get, plus 3-5 input
  metrics the team can move. Use when a product needs one shared measure of progress or the
  team tracks many unrelated numbers. Not for targets of one launch or feature (use
  success-metrics) and not for quarterly goals (use product-okrs).
stage: direction
stage_order: 3
version: 0.1.0
---

# North Star Metric

Source: North Star Playbook, Amplitude (https://amplitude.com/books/north-star).

## When to use
- The team cannot agree on how to tell whether the product is succeeding.
- Dashboards show many metrics and none drive decisions.
- OKRs or a roadmap need one outcome measure to anchor on.

## Inputs
- **Strategy and vision** (required): read `product.md`.
- **Customer value moment** (required): the action where a customer first gets real value.
- **Candidate metrics and current data** (optional): ask for what is already tracked.

## Steps
1. Describe the **value moment**: what the customer does when the product works for them.
2. List 4-6 candidate metrics that count that moment (frequency, volume or depth).
3. Test each candidate: reflects customer value, leads revenue, measurable weekly, influenced by
   the team, understandable to everyone. Reject revenue itself and vanity counts such as sign-ups.
4. Pick one. Write the exact definition: numerator, denominator, window, inclusions, exclusions.
5. Break it into 3-5 **input metrics** (breadth, depth, frequency, efficiency) with owners.
6. Add 1-2 **guardrail metrics** that must not worsen (quality, support load, churn).
7. Record the current baseline or state it as unknown, and a review cadence.

## Output template
```markdown
# North Star Metric
- Metric: <name>   - Definition: <precise>   - Baseline: <value or unknown>
## Why this metric (tests passed / failed per candidate)
## Input metrics (owner, current)
## Guardrails
## Review cadence
```

## Quality checklist
- [ ] One metric, defined with numerator, denominator and window.
- [ ] Tied to a customer value moment, not revenue or vanity counts.
- [ ] 3-5 input metrics, each with an owner.
- [ ] At least one guardrail.
- [ ] Baseline given or marked unknown.

## Handoff
Writes `artifacts/direction/<date>-north-star.md`; after approval it updates `product.md`.
Consumed by `product-okrs`, `success-metrics` and `experiment-design`.
