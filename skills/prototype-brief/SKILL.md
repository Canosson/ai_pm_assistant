---
name: prototype-brief
description: >
  Write a brief for a throwaway prototype that tests one risky assumption: what to build, how
  real it must be, who tests it and what result decides. Use before investing in design or
  engineering when the riskiest assumption is untested. Not for the full requirements
  (use prd-template), not for measuring a live feature (use experiment-design) and not for
  interview prep (use interview-guide).
stage: define
stage_order: 2
version: 0.1.0
---

# Prototype brief

Source: practitioner pattern; related method: Design Sprint prototype and test (https://www.gv.com/sprint/).

## When to use
- A risky assumption (desirability, usability, feasibility) can be tested cheaply.
- Design or engineering asks "what exactly should we mock up?"
- Debate continues because nobody has seen the idea working.

## Inputs
- **Assumption to test** (required): from the PR/FAQ, opportunity tree or strategy risks.
- **Target users** (required): who will try it and how many.
- **Constraints** (optional): time budget, tools, designer availability.

## Steps
1. State the one **hypothesis**: "We believe <user> will <behavior> because <reason>".
2. Define the **decision rule**: the result that means go, change, or stop, set before testing.
3. Choose the **fidelity**: sketch, clickable mock, concierge (human behind the scenes) or code.
   Pick the cheapest level that can answer the question.
4. Set the **scope**: the 1-3 flows to include and everything explicitly left fake or out.
5. Write 3-5 **test tasks** in neutral wording, with no hints about the interface.
6. Plan the **session**: participants, recruiting, length, who observes, what is recorded.
7. List what you will **not** learn from this prototype.
8. Set the timebox and the owner.

## Output template
```markdown
# Prototype brief: <name>
- Hypothesis / Decision rule
- Fidelity and why / Scope (in, fake, out)
## Test tasks
## Session plan (users, recruiting, observers)
## Limits of this test
## Timebox and owner
```

## Quality checklist
- [ ] One hypothesis, one decision rule written before testing.
- [ ] Fidelity is the cheapest that answers the question.
- [ ] Tasks use neutral wording.
- [ ] Out-of-scope and limits are explicit.
- [ ] Timebox and owner set.

## Handoff
Writes `artifacts/define/<date>-prototype-brief-<slug>.md`. Results feed `interview-synthesis`,
`prd-template` and `decision-log`.
