---
name: jobs-to-be-done
description: >
  Express why customers hire a product as job statements ("When..., I want..., so I can...") with
  the forces that push them to switch or stay. Use to understand customer motivation and
  competing alternatives. Not for summarizing themes across sessions (use interview-synthesis)
  and not for mapping opportunities to solutions (use opportunity-solution-tree).
stage: discover
stage_order: 3
version: 0.1.0
---

# Jobs to be done

Source: Jobs to Be Done, Christensen Institute (https://www.christenseninstitute.org/jobs-to-be-done/).

## When to use
- The team describes users by demographics but not by what they are trying to achieve.
- You need to see what a customer "fires" when they hire your product.
- Positioning and feature choices need a motivation-based foundation.

## Inputs
- **Interview evidence** (required): switch stories or synthesis; read `artifacts/discover/` and `research/`.
- **Segment** (required): whose jobs these are.
- **Known alternatives** (optional): what customers use instead, including doing nothing.

## Steps
1. Reconstruct each **switch story**: first thought, passive looking, active looking, decision, use.
2. Identify the **situation** that triggered the search and the **progress** the customer wanted.
3. Write job statements: **When** <situation>, **I want to** <motivation>, **so I can** <outcome>.
   Keep them solution-free.
4. Split into **functional**, **emotional** and **social** dimensions of each job.
5. List the **forces**: push (problem today), pull (new solution), anxiety (about changing),
   habit (comfort with the old way).
6. List the **alternatives** hired today for each job and where they fall short.
7. Rank jobs by importance and how poorly they are served; flag evidence strength.

## Output template
```markdown
# Jobs to be done: <segment>
| Job statement | Functional | Emotional | Social | Evidence |
## Forces of progress (push, pull, anxiety, habit)
## Alternatives and gaps
## Underserved jobs, ranked
```

## Quality checklist
- [ ] Each job is solution-free and starts from a situation.
- [ ] Jobs are separated from personas and features.
- [ ] Four forces covered for the top jobs.
- [ ] Alternatives include doing nothing.
- [ ] Evidence strength noted per job.

## Handoff
Writes `artifacts/discover/<date>-jtbd-<segment>.md`. Consumed by `opportunity-solution-tree`,
`product-vision` and `working-backwards-prfaq`.
