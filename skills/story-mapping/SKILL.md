---
name: story-mapping
description: >
  Build a user story map: the user's journey as a backbone, stories beneath it, sliced into
  releases. Use when you must see the whole experience and plan a thin end-to-end first release.
  Not for writing a single story (use user-stories) and not for the requirements document
  (use prd-template).
stage: define
stage_order: 4
version: 0.1.0
---

# Story mapping

Source: User Story Mapping, Jeff Patton (https://www.jpattonassociates.com/user-story-mapping/).

## When to use
- A backlog is a flat list and nobody can see the user's whole journey.
- You must choose the smallest release that works end to end.
- Scope debates need a visual, shared model.

## Inputs
- **Persona and goal** (required): who and what they want to accomplish.
- **Journey steps** (required, or derive from research): read `research/` and the PRD.
- **Constraints** (optional): release dates, `moscow-prioritization` artifact.

## Steps
1. State the persona and the goal of the whole journey.
2. Write the **narrative** left to right: the activities (big steps) the user performs, in order.
3. Under each activity, write the **steps** the user takes.
4. Under each step, brainstorm **stories** (details, variations, edge cases), best first.
5. Draw **release lines**: Release 1 is the thinnest slice that lets the persona complete the
   goal end to end; later releases deepen it.
6. Check each release line: can the persona still finish the journey after this release?
7. Mark gaps, risks and stories needing a spike.
8. Hand the top stories to `user-stories` for acceptance criteria.

## Output template
```markdown
# Story map: <goal>  (persona: <...>)
| Activity | A1 | A2 | A3 |
| Steps | ... |
## Release 1 (walking skeleton)
## Release 2
## Release 3
## Gaps and risks
```

## Quality checklist
- [ ] Backbone reads as the user's journey, in order.
- [ ] Release 1 completes the journey end to end.
- [ ] Stories under each step are ordered by value.
- [ ] Gaps and risks are listed.
- [ ] No stories without a parent step.

## Handoff
Writes `artifacts/define/<date>-story-map-<slug>.md`. Consumed by `user-stories`,
`product-roadmap` and `launch-checklist`.
