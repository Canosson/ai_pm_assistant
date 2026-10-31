---
name: product-strategy
description: >
  Turn a vision into a strategy: a diagnosis of the situation, a guiding policy that makes
  choices, and coherent actions, including what the product will not do. Use when the team has
  a vision but no agreed choices about where to play and how to win. Not for the destination
  itself (use product-vision) and not for quarterly goals (use product-okrs).
stage: direction
stage_order: 2
version: 0.1.0
---

# Product strategy

Source: the kernel of a strategy (diagnosis, guiding policy, coherent action), Richard Rumelt
(https://hbr.org/2011/06/the-perils-of-bad-strategy).

## When to use
- The vision exists but teams make conflicting trade-offs.
- A new market, competitor or constraint changes the situation.
- You need to explain why the roadmap has these themes and not others.

## Inputs
- **Product vision** (required): read `product.md` or `artifacts/direction/`.
- **Situation facts** (required): market, customers, competitors, internal strengths and limits.
  Read `research/`. Run `competitive-analysis` first if missing.
- **Constraints** (optional): budget, team, regulation, runway.

## Steps
1. Write the **diagnosis**: the one or two crux challenges that decide success, in plain facts.
2. Write the **guiding policy**: the approach to those challenges. It must rule things out.
3. Choose **where to play** (segments, use cases, channels) and **how to win** (the advantage).
4. List 3-5 **coherent actions** that reinforce each other and follow from the policy.
5. List explicit **trade-offs and non-goals**: what you will not do, and why that is acceptable.
6. Flag **bad strategy signs**: a goals list with no choices, vague fluff, or no diagnosis.
7. Name the 2-3 riskiest assumptions and how each would be tested.

## Output template
```markdown
# Product strategy (<date>)
## Diagnosis
## Guiding policy
## Where to play / How to win
## Coherent actions
## Non-goals and trade-offs
## Riskiest assumptions
```

## Quality checklist
- [ ] Diagnosis names the crux, not a list of problems.
- [ ] The policy rules something out.
- [ ] Each action traces to the policy.
- [ ] Non-goals are listed.
- [ ] No sentence could appear unchanged in a competitor's strategy.

## Handoff
Writes `artifacts/direction/<date>-product-strategy.md`; after approval it updates `product.md`.
Consumed by `north-star-metric`, `product-okrs`, `product-roadmap` and `feature-request-triage`
(strategy fit).
