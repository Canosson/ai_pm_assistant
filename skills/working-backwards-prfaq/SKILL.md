---
name: working-backwards-prfaq
description: >
  Write a Working Backwards PR/FAQ: a one-page future press release plus customer and internal
  FAQs, to test whether an idea is worth building before any spec. Use at the start of a new
  initiative to force clarity on customer and benefit. Not for detailed requirements (use
  prd-template) and not for the company-level vision (use product-vision).
stage: define
stage_order: 1
version: 0.1.0
---

# Working Backwards PR/FAQ

Source: Working Backwards PR/FAQ (https://www.workingbackwards.com/concepts/working-backwards-pr-faq/).

## When to use
- A new product or major feature needs a go / no-go before a PRD.
- The team describes the solution but not the customer benefit.
- Stakeholders need a short, readable pitch that can be challenged.

## Inputs
- **Customer and problem** (required): from `product-vision`, `jobs-to-be-done` or research.
- **The solution in one sentence** (required).
- **Evidence and numbers** (optional): read `research/`. Mark any number you cannot source as TBD.

## Steps
1. Write the **headline**: product name and the benefit, in customer words.
2. Write a one-sentence **subheading** naming the customer and the benefit.
3. Write the **summary paragraph**: what it is, who it is for, why it matters.
4. Write the **problem** paragraph: the customer pain today.
5. Write the **solution** paragraph: how the product removes the pain.
6. Add a **customer quote** (clearly marked as fictional) and a **how to get started** line.
7. Write **customer FAQs** (price, how it works, who it is for, what it replaces).
8. Write **internal FAQs**: cost, feasibility, risks, dependencies, metrics, and the kill criteria.
9. Cut the press release to one page. Remove adjectives that carry no fact.

## Output template
```markdown
# <Headline>
*<Subheading>*
<date, city>: <summary>
**Problem** ... **Solution** ... **Quote (fictional)** ... **Get started** ...
## Customer FAQ
## Internal FAQ (including kill criteria)
```

## Quality checklist
- [ ] Press release fits one page and reads without jargon.
- [ ] Names one customer and one benefit.
- [ ] Fictional quote is labeled fictional.
- [ ] Internal FAQ states risks and kill criteria.
- [ ] No invented numbers; unknowns marked TBD.

## Handoff
Writes `artifacts/define/<date>-prfaq-<slug>.md`. Consumed by `prd-template`, `prototype-brief`
and `gtm-plan`.
