---
name: trade-off-analysis
description: >
  Choose between a FEW mutually exclusive options (2-5) with a weighted decision matrix and a
  recommendation. Use before a decision when options differ on several criteria. Not for ranking
  a long backlog by value per effort (use rice-prioritization) and not for recording the outcome
  afterwards (use decision-log).
stage: decide
stage_order: 3
version: 0.1.0
---

# Trade-off analysis

Source: weighted decision matrix (https://asq.org/quality-resources/decision-matrix).

## When to use
- Two to five realistic options exist and only one can be chosen (build vs buy, vendor A vs B,
  launch now vs later).
- Stakeholders argue from different criteria and need them made explicit.
- A decision needs a documented rationale.

## Inputs
- **Decision to make** (required): one sentence.
- **Options** (required): 2-5, including "do nothing" if viable.
- **Criteria and priorities** (required): what matters; ask the decision owner for weights.
- **Evidence per option** (optional): costs, estimates, research.

## Steps
1. State the decision and who owns it.
2. Define 4-7 **criteria** that are independent (avoid double counting), such as cost, time,
   risk, customer impact, strategic fit, reversibility.
3. Assign **weights** summing to 100, agreed with the owner before scoring.
4. Score each option 1-5 per criterion with a one-line evidence note; no unexplained scores.
5. Compute the **weighted totals**.
6. Run a **sensitivity check**: change the top two weights by 10 points; does the winner change?
7. Note **non-quantified factors** and the biggest risk of the leading option.
8. State the **recommendation** and what would change it.

## Output template
```markdown
# Trade-off analysis: <decision>
| Criterion | Weight | Option A | Option B | Option C |
Weighted total
## Evidence notes   ## Sensitivity   ## Risks and unquantified factors
## Recommendation and what would change it
```

## Quality checklist
- [ ] Weights set before scoring and sum to 100.
- [ ] Every score has an evidence note.
- [ ] Criteria are independent.
- [ ] Sensitivity check run.
- [ ] Recommendation names what would change it.

## Handoff
Writes `artifacts/decide/<date>-tradeoff-<decision>.md`. Once decided, record it with `decision-log`.
