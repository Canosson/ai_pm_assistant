---
name: interview-guide
description: >
  Prepare customer interviews BEFORE talking to anyone: research goal, screener and open,
  past-behavior questions. Use when the user is about to run discovery calls. Not for making
  sense of notes already collected (use interview-synthesis) and not for testing a mock or
  prototype with users (use prototype-brief).
stage: discover
stage_order: 1
version: 0.1.0
---

# Interview guide

Source: The Mom Test, Rob Fitzpatrick (https://www.momtestbook.com/).

## When to use
- Discovery interviews are about to start and nothing is prepared.
- Past interviews drew compliments and opinions but no usable facts.
- A new segment or problem needs first-hand evidence.

## Inputs
- **Research goal** (required): the one decision this research should inform.
- **Target persona** (required): who qualifies, and who does not.
- **Existing knowledge** (optional): read `research/` so you do not re-ask known things.

## Steps
1. Write the **learning goal** as a question the research must answer, plus the decision it feeds.
2. Define the **screener**: 3-5 questions that include the right people and exclude the wrong ones.
3. List the **assumptions** to test, riskiest first.
4. Draft 6-10 **questions about past behavior** ("Tell me about the last time you..."), not
   opinions or hypotheticals; no pitching of the idea.
5. Add **follow-ups** that dig for specifics: what happened, what did you do, what did it cost.
6. Add **closing questions**: who else should I talk to, and is there anything I should have asked.
7. Write the **logistics**: length (30-45 min), recording consent, note-taker, how many interviews.
8. List the **traps to avoid**: leading questions, future promises, feature requests taken literally.

## Output template
```markdown
# Interview guide: <topic>
- Learning goal / decision it feeds / Persona
## Screener   ## Assumptions to test
## Questions (opening, core, follow-ups, closing)
## Logistics   ## Traps to avoid
```

## Quality checklist
- [ ] Goal tied to a named decision.
- [ ] Every question asks about past behavior or facts.
- [ ] No question mentions the proposed solution.
- [ ] Screener excludes as well as includes.
- [ ] Consent and recording handled.

## Handoff
Writes `artifacts/discover/<date>-interview-guide-<topic>.md`. After the calls, notes go to
`interview-synthesis`.
