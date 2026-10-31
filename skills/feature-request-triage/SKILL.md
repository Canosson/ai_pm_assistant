---
name: feature-request-triage
description: >
  Decide what to do with one incoming feature request or a messy pile of them: accept, defer,
  decline, or ask for more info, with a rationale and a reply draft. Use when requests arrive from
  customers, sales or support and the PM must say yes or no. Not for ranking a shortlist of
  accepted items (use rice-prioritization) and not for scope cuts under a deadline
  (use moscow-prioritization).
stage: prioritise
stage_order: 1
version: 0.1.0
---

# Feature request triage

Source: practitioner pattern, no single canonical framework.

## When to use
- A request lands ("can you add X?") and needs a decision and an answer.
- A backlog is full of unsorted requests and needs a first cut before any scoring.
- You need a consistent, explainable way to say no.

## Inputs
- **Request(s)** (required): the raw text, who asked, and the channel.
- **Strategy and north star** (required): read `product.md`. If absent, ask for the one-line strategy.
- **Evidence** (optional): how many independent requesters, revenue at stake, support volume.
- **Existing backlog** (optional): read `backlog/` to catch duplicates.

## Steps
1. Restate the request as the underlying problem ("user cannot do Y"), not the proposed solution.
2. Classify: bug, feature, enhancement, integration, or question disguised as a request.
3. Check duplicates against the backlog. If a match exists, merge and add the requester.
4. Check strategy fit: does it advance the north star or a current objective? Yes, partly, or no.
5. Check evidence: count independent requesters, not repeat mentions; note segment and revenue.
6. Estimate effort roughly: small, medium or large. Do not score precisely here.
7. Decide: **accept** (goes to prioritization), **defer** (revisit on a named trigger), **decline**
   (out of strategy), or **needs info** (name the exact question).
8. Draft the reply: thanks, the problem as you understood it, the decision, and the reason in
   customer terms. Never promise a date.

## Output template
```markdown
# Triage: <request title>
- Requester / channel:
- Underlying problem:
- Type / duplicate of:
- Strategy fit: yes | partial | no, because ...
- Evidence: <n> independent requesters, <segment>, <revenue>
- Rough effort: S | M | L
- Decision: accept | defer (until ...) | decline | needs info (question)
- Reply draft:
```
For a pile, output one table row per request with the same fields.

## Quality checklist
- [ ] Problem stated apart from the requested solution.
- [ ] Decision is one of the four allowed values.
- [ ] Declines and defers cite strategy or evidence, not taste.
- [ ] Deferred items carry a revisit trigger.
- [ ] Reply draft has no dates or promises.

## Handoff
Writes `artifacts/prioritise/<date>-triage-<slug>.md`. Accepted items are added to `backlog/` and
feed `rice-prioritization`, `cost-of-delay` or `moscow-prioritization`.
