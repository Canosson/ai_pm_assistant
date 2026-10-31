---
name: user-stories
description: >
  Write well-formed user stories with Given/When/Then acceptance criteria, checked against INVEST.
  Use when requirements or story-map items must become stories a team can estimate and build.
  Not for the whole requirements document (use prd-template) and not for the journey view
  (use story-mapping).
stage: define
stage_order: 5
version: 0.1.0
---

# User stories

Source: user stories and INVEST, Mike Cohn (https://www.mountaingoatsoftware.com/agile/user-stories).

## When to use
- Requirements need to become buildable, estimable items.
- Existing stories are vague, too big or have no acceptance criteria.
- A story-map release needs its top stories detailed.

## Inputs
- **Requirement or story-map item** (required): read `artifacts/define/`.
- **Persona** (required): who needs it.
- **Business rules and constraints** (optional): from the PRD.

If a rule is unknown, add it as an open question; do not guess it into a criterion.

## Steps
1. Write the story: **As a** <persona>, **I want** <capability>, **so that** <benefit>.
2. Check the benefit is real and customer-facing; if not, reconsider the story.
3. Write 3-6 acceptance criteria in **Given / When / Then** form, covering the main path and at
   least one error or edge case.
4. Test against **INVEST**: Independent, Negotiable, Valuable, Estimable, Small, Testable.
5. If it fails Small, split it by workflow step, data variation, rule or happy/unhappy path.
6. Add notes: dependencies, out of scope, design links. No implementation instructions.
7. Number the stories and order by value and dependency.

## Output template
```markdown
## US-<n>: <short title>
As a <persona>, I want <capability>, so that <benefit>.
**Acceptance criteria**
1. Given <context>, when <action>, then <result>.
**Notes / out of scope / dependencies**
**INVEST check:** I N V E S T (pass or fix)
```

## Quality checklist
- [ ] Persona, capability and benefit all present.
- [ ] Criteria are testable, with at least one edge or error case.
- [ ] Story passes INVEST or has a split plan.
- [ ] No implementation prescribed.
- [ ] Unknown rules listed as open questions.

## Handoff
Writes `artifacts/define/<date>-user-stories-<slug>.md`. Consumed by engineering, QA and
`launch-readiness-review`.
