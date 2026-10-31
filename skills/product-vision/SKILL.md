---
name: product-vision
description: >
  Write a one-paragraph product vision: who it serves, the problem, the future state and why it
  wins. Use when starting a product or when the team cannot say in one sentence where it is
  heading. Not for how to get there (use product-strategy) and not for measurable goals
  (use product-okrs).
stage: direction
stage_order: 1
version: 0.1.0
---

# Product vision

Source: Product Vision Board, Roman Pichler (https://www.romanpichler.com/blog/product-vision-board/).

## When to use
- A new product or major bet needs a shared picture of success.
- Stakeholders describe the product differently.
- A strategy or roadmap discussion keeps drifting because the destination is unclear.

## Inputs
- **Target customer** (required): the specific segment, not "everyone".
- **Problem or need** (required): what they struggle with today and the evidence.
- **Product and key differentiator** (required): what it is and why it beats the alternatives.
- **Time horizon** (optional): default 3-5 years.
- **Existing research** (optional): read `research/` and `product.md`.

Do not invent customers or evidence. Ask, or mark the field as an assumption.

## Steps
1. Name one target customer segment and the job they are trying to do.
2. State the problem in their words, with one piece of evidence.
3. Describe the future state: what is different for them if the product succeeds.
4. State the differentiator against the real alternative (including doing nothing).
5. Draft the vision in one to three sentences, plain words, no jargon or metrics.
6. Test it: could a new hire repeat it? Could it guide a "no"? Would a competitor sign it?
7. Write 2 sentences on what the vision deliberately excludes.

## Output template
```markdown
# Product vision
> <one to three sentence vision>

- For: <customer>   - Problem: <...>   - Future state: <...>   - Differentiator: <...>
- Horizon: <years>
## Not in the vision
## Assumptions to validate
```

## Quality checklist
- [ ] One named customer segment.
- [ ] Describes an outcome for the customer, not a feature list.
- [ ] Contains no metrics or dates.
- [ ] Specific enough to say "no" to something.
- [ ] Assumptions are listed.

## Handoff
Writes `artifacts/direction/<date>-product-vision.md`. After approval, its text becomes the Vision
section of `product.md`. Consumed by `product-strategy` and `working-backwards-prfaq`.
