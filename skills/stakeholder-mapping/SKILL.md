---
name: stakeholder-mapping
description: >
  Identify who is affected or influential and plan how to engage each person, using a
  power/interest grid. Use at the start of an initiative or when alignment keeps failing. Not
  for writing the message itself (use stakeholder-update) and not for choosing between options
  (use trade-off-analysis).
stage: decide
stage_order: 2
version: 0.1.0
---

# Stakeholder mapping

Source: stakeholder analysis, power/interest grid (https://www.mindtools.com/aol9n8w/stakeholder-analysis).

## When to use
- A new initiative touches teams or leaders you have not worked with.
- Decisions get blocked late by people no one consulted.
- You need a communication plan that is not "tell everyone everything".

## Inputs
- **Initiative and its changes** (required).
- **Known people and groups** (required, or ask): internal, customers, partners, regulators.
- **Org context** (optional): read `product.md` and earlier `decisions/`.

Never rate a person's attitude without evidence; mark "unknown" and plan to learn it.

## Steps
1. List all **stakeholders** by name or role, including quiet decision-makers and affected teams.
2. For each, note what they **care about** and what they could **gain or lose**.
3. Rate **power** (can they stop or fund this?) and **interest** (how much does it affect them?)
   as high or low.
4. Place each in the grid: **manage closely** (high/high), **keep satisfied** (high power, low
   interest), **keep informed** (low power, high interest), **monitor** (low/low).
5. Note the current stance: supporter, neutral, skeptic, or unknown, with evidence.
6. Write an **engagement plan** per person or group: goal, channel, cadence, owner.
7. Flag **risks**: a high-power skeptic, an unknown decision-maker, a missing voice.

## Output template
```markdown
# Stakeholder map: <initiative>
| Stakeholder | Cares about | Power | Interest | Stance | Quadrant |
## Engagement plan (goal, channel, cadence, owner)
## Risks and unknowns
```

## Quality checklist
- [ ] Affected teams and customers included, not only executives.
- [ ] Stance backed by evidence or marked unknown.
- [ ] Every high-power person has an engagement owner.
- [ ] Cadence is specific.
- [ ] Risks listed.

## Handoff
Writes `artifacts/decide/<date>-stakeholder-map-<initiative>.md`. Consumed by `stakeholder-update`
(audiences) and `gtm-plan` (internal enablement).
