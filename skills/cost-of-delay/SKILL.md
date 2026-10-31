---
name: cost-of-delay
description: >
  Rank items by what each week of delay costs, using CD3 (Cost of Delay divided by Duration).
  Use when timing matters: expiring windows, competitor moves, regulatory dates, or items of very
  different size. Not for general value-per-effort ranking (use rice-prioritization) and not for
  fixed-deadline scope (use moscow-prioritization) or customer delight (use kano-model).
stage: prioritise
stage_order: 2
version: 0.1.0
---

# Cost of delay (CD3)

Source: Cost of Delay, Black Swan Farming (https://blackswanfarming.com/cost-of-delay/).

## When to use
- Several items compete and some lose value quickly if they slip.
- Items differ a lot in duration, so a small fast item should beat a large slow one.
- A deadline, market window or contract date exists.

## Inputs
- **Items** (required): name and a one-line description.
- **Value per week of having the item live** (required): money, retained users, or a stated proxy.
- **Duration** (required): weeks from start to live, for each item.
- **Urgency profile** (required per item): see step 3.
- **Evidence for the value estimate** (optional): analytics, contracts, deal sizes.

Never invent values. If the value is unknown, state the proxy and mark it low confidence.

## Steps
1. Pick one value unit and one time unit (per week) for all items.
2. Estimate the weekly cost of delay for each item: what is lost each week it is not live.
3. Tag the urgency profile: **standard** (steady loss), **expedite** (loss accelerates fast),
   **fixed date** (value drops to zero after a date), or **intangible** (value grows slowly, for
   example tech debt or learning).
4. Estimate duration in weeks.
5. Compute `CD3 = cost of delay per week / duration in weeks`.
6. Rank by CD3 descending. Move **fixed-date** items to the top if their date is reachable, and
   mark them unreachable otherwise.
7. Note the items whose rank changes if cost of delay is off by 50%.

## Output template
```markdown
# Cost of delay: <scope>
| Rank | Item | Profile | CoD / week | Duration (wk) | CD3 |
|------|------|---------|-----------|---------------|-----|

## Fixed-date items and whether each date is reachable
## Sensitivity (rank changes at +/-50% CoD)
## Recommended sequence
```

## Quality checklist
- [ ] One value unit and one time unit used everywhere.
- [ ] Every item has a profile tag.
- [ ] CD3 recomputes from the table.
- [ ] Fixed-date items are checked against their date.
- [ ] Sensitivity note present.

## Handoff
Writes `artifacts/prioritise/<date>-cost-of-delay.md`. Consumed by `product-roadmap` (sequencing)
and `launch-checklist` (date-driven items).
