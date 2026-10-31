---
name: competitive-analysis
description: >
  Compare competitors and alternatives: positioning, feature matrix, pricing signals and gaps,
  with sources. Use when the team needs to know how the product stacks up. Heavy web research
  goes to the researcher subagent. Not for deciding the product's own strategy
  (use product-strategy) and not for the launch plan (use gtm-plan).
stage: discover
stage_order: 5
version: 0.1.0
---

# Competitive analysis

Source: competitive analysis practice (https://www.atlassian.com/agile/product-management/competitive-analysis).

## When to use
- A new product, feature or positioning needs a view of the landscape.
- Sales or leadership asks "how are we different?"
- A strategy or launch plan needs grounded competitor facts.

## Inputs
- **Our product and segment** (required).
- **Competitor set** (required, or propose 3-6): direct, indirect and the do-nothing alternative.
- **Comparison criteria** (required): what customers care about; derive from `research/`.
- **Existing notes** (optional): read `research/` for earlier competitor notes.

Every claim needs a source URL and date. If you cannot verify, mark it "unverified".

## Steps
1. Define the **scope**: segment, competitors, and criteria. Include indirect alternatives.
2. Delegate the fact-gathering to the `researcher` subagent when the set is more than two
   competitors; require a source URL and date per fact.
3. Build the **feature and capability matrix** against the criteria (yes, partial, no, unknown).
4. Summarize each competitor's **positioning**: target customer, promise, price signals.
5. Identify **strengths and weaknesses** relative to our product, in customer terms.
6. Find **gaps and openings**: unmet needs nobody serves well, and where we are behind.
7. Write **implications**: 3-5 actions and the strategy or roadmap questions they raise.
8. Record the **freshness**: date of the data and what to re-check in 90 days.

## Output template
```markdown
# Competitive analysis: <segment>  (data as of <date>)
## Scope and criteria   ## Matrix   ## Positioning per competitor
## Strengths and weaknesses vs us   ## Gaps and openings
## Implications   ## Sources and freshness
```

## Quality checklist
- [ ] Includes indirect alternatives and doing nothing.
- [ ] Every fact has a source and date; unknowns marked.
- [ ] Criteria come from customer evidence.
- [ ] Gaps are stated as customer needs.
- [ ] Freshness date present.

## Handoff
Writes `artifacts/discover/<date>-competitive-<segment>.md` and raw notes under `research/`.
Consumed by `product-strategy`, `gtm-plan` and `product-vision`.
