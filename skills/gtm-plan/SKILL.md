---
name: gtm-plan
description: >
  Plan how a product reaches the market: target segment, positioning, messaging, channels,
  pricing and packaging notes, launch tier and success targets. Use when a launch needs a
  market-facing strategy. Not for the internal task list with owners and dates (use
  launch-checklist), not for the go/no-go gate (use launch-readiness-review) and not for
  customer-facing change text (use release-notes).
stage: launch
stage_order: 1
version: 0.1.0
---

# Go-to-market plan

Source: go-to-market strategy (https://www.productmarketingalliance.com/go-to-market-strategy/).

## When to use
- A new product, feature or pricing change must be introduced to customers.
- Teams (marketing, sales, support) need one shared story and priorities.
- Launch scope depends on its tier (big launch vs quiet release).

## Inputs
- **What is launching and for whom** (required): from the PRD and PR/FAQ.
- **Positioning evidence** (required): read `competitive-analysis` and `jobs-to-be-done` artifacts.
- **Success targets** (required): from `success-metrics`.
- **Budget, constraints, dates** (optional).

Do not invent pricing or numbers; mark them TBD with an owner.

## Steps
1. Define the **target segment** and the job they hire the product for.
2. Write the **positioning**: for whom, the category, the key benefit, the proof, the alternative.
3. Draft **messaging**: one headline, 3 supporting points, and objections with answers.
4. Choose a **launch tier** (major, standard, quiet) and say what that implies for effort.
5. Select **channels** and activities per audience (new, existing, internal), with owners.
6. Note **pricing and packaging** decisions and who decides.
7. Plan **enablement**: what sales and support need and when.
8. Set the **targets and review points**, copied from `success-metrics`.
9. List **risks and dependencies**.

## Output template
```markdown
# GTM plan: <launch>  (tier: <...>)
## Segment and job   ## Positioning   ## Messaging and objections
## Channels and activities (owner)   ## Pricing and packaging (TBD owner)
## Enablement   ## Targets and review points   ## Risks and dependencies
```

## Quality checklist
- [ ] One primary segment.
- [ ] Positioning names the real alternative.
- [ ] Every activity has an owner.
- [ ] Targets match the success-metrics artifact.
- [ ] Unknown pricing marked TBD with an owner.

## Handoff
Writes `artifacts/launch/<date>-gtm-<launch>.md`. Feeds `launch-checklist` (tasks) and
`release-notes` (messaging).
