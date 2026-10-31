---
name: opportunity-solution-tree
description: >
  Build an Opportunity Solution Tree: one desired outcome, the customer opportunities under it,
  solution ideas per opportunity and the assumption tests that decide what to explore next. Use
  to choose where to focus discovery. Not for scoring a backlog (use rice-prioritization) and
  not for writing job statements (use jobs-to-be-done).
stage: discover
stage_order: 4
version: 0.1.0
---

# Opportunity Solution Tree

Source: Opportunity Solution Trees, Teresa Torres, Product Talk (https://www.producttalk.org/opportunity-solution-tree/).

## When to use
- The team jumps from an outcome straight to a favorite solution.
- Discovery produced many needs and nobody knows which to pursue.
- You must show how a solution connects to the outcome.

## Inputs
- **Desired outcome** (required): one measurable product outcome; read `product.md` (OKRs, north star).
- **Opportunities** (required): customer needs, pains and desires from `interview-synthesis` or
  `jobs-to-be-done`, as evidence, not guesses.
- **Solution ideas** (optional): ask for them; generate more if fewer than three per opportunity.

## Steps
1. Put the **outcome** at the root, phrased as a metric the team can influence.
2. List **opportunities** from customer evidence, in the customer's words, and group parent and
   child opportunities until each leaf is small enough to solve.
3. Compare sibling opportunities on importance, how often it occurs and how poorly it is served,
   and **choose one target** opportunity.
4. For the target, generate **at least three solutions**, including a cheap one.
5. For each leading solution, list **assumptions** (desirability, usability, feasibility, viability).
6. Pick the **riskiest assumption** and propose the smallest **test** (interview, prototype,
   experiment). Link to `prototype-brief` or `experiment-design`.
7. Mark the path through the tree you will pursue and what you park.

## Output template
```markdown
# Opportunity Solution Tree: <outcome>
Outcome
 - Opportunity A (evidence)
    - Opportunity A1 (target)
       - Solution 1 / 2 / 3 -> assumptions -> test
 - Opportunity B ...
## Chosen path and why
## Riskiest assumptions and tests
```

## Quality checklist
- [ ] One outcome at the root, measurable.
- [ ] Opportunities cite customer evidence.
- [ ] At least three solutions for the target opportunity.
- [ ] Riskiest assumption has a concrete, small test.
- [ ] Parked branches listed.

## Handoff
Writes `artifacts/discover/<date>-ost-<outcome>.md`. Consumed by `rice-prioritization`,
`prototype-brief`, `experiment-design` and `product-roadmap`.
