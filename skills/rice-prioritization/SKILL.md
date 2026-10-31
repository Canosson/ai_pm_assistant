---
name: rice-prioritization
description: >
  Score and rank a candidate list with RICE (Reach, Impact, Confidence, Effort). Use when a long
  list needs a defensible value-per-effort ranking. Not for one incoming request
  (use feature-request-triage), 2-5 exclusive options (use trade-off-analysis), fixed-deadline
  scope (use moscow-prioritization), timing (use cost-of-delay) or customer delight (use kano-model).
stage: prioritise
stage_order: 3
version: 0.1.0
---

# RICE prioritization

Source: RICE scoring, Intercom (https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/).

## When to use
- A backlog or idea list needs a first-pass ranking by expected value per unit of effort.
- A stakeholder asks "why is X above Y?" and you need numbers to point at.
- Items are comparable in kind (all features, or all experiments), not a mix of bugs and strategy bets.

## Inputs
- **Candidate items** (required): name plus one-line description each. Read from `backlog/` if present, else ask.
- **Time window** (required): the period Reach and Effort are measured over, for example one quarter.
- **Evidence per item** (optional but weighs on Confidence): analytics, interview notes, support volume.
- **North star / OKRs** (optional): read `product.md` to sanity-check Impact against the goal.

Never invent Reach or Effort numbers. If a value is unknown, record the assumption and lower Confidence.

## Steps
1. Fix the time window and write the unit of Reach (users, accounts, or events per window).
2. For each item, set **Reach**: how many units it touches in the window.
3. Set **Impact** on the fixed scale: 3 massive, 2 high, 1 medium, 0.5 low, 0.25 minimal.
4. Set **Confidence** as a percentage: 100 high (data), 80 medium, 50 low (gut). Below 50: flag as moonshot.
5. Set **Effort** in person-months (total across roles). Use one unit for every item.
6. Compute `score = (Reach x Impact x Confidence) / Effort`. Round to one decimal.
7. Sort descending. Mark items within 15% of each other as a tie group and break ties by strategic fit.
8. Run a sanity pass: does the top 3 match intuition? If not, find the input that drives the gap and re-check it.
9. List the 2-3 assumptions with the biggest effect on the order.

## Output template
```markdown
# RICE ranking: <scope>  (<window>)

| Rank | Item | Reach | Impact | Confidence | Effort (pm) | Score |
|------|------|-------|--------|------------|-------------|-------|

## Tie groups
## Key assumptions (sensitivity)
## Recommended next step
```

## Quality checklist
- [ ] Time window and Reach unit stated once, used consistently.
- [ ] Impact values come only from the fixed scale.
- [ ] Every Confidence below 80% has a stated reason.
- [ ] Effort uses one unit for all items.
- [ ] Scores recompute correctly from the table.
- [ ] Top-3 sanity pass and key assumptions are present.

## Handoff
Writes `artifacts/prioritise/<date>-rice-ranking.md` (`skill: rice-prioritization`, `stage: prioritise`,
`status: draft`, `inputs: [backlog items]`). Consumed by `product-roadmap` and `moscow-prioritization`
(as the ordering inside a bucket).
