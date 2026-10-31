---
name: release-notes
description: >
  Write customer-facing release notes: what changed, why it matters and how to use it, in plain
  benefit-led language. Use when shipping changes users will see. Not for internal progress
  reports (use stakeholder-update), not for the market launch strategy (use gtm-plan) and not for
  a technical changelog of commits.
stage: launch
stage_order: 3
version: 0.1.0
---

# Release notes

Source: product release notes practice (https://www.atlassian.com/blog/inside-atlassian/release-notes).

## When to use
- A release contains changes customers will notice.
- Support keeps answering "what changed?"
- A raw changelog or ticket list must become something readable.

## Inputs
- **Changes shipped** (required): tickets, PRs or the PRD; read `artifacts/define/`.
- **Audience** (required): admins, end users, developers.
- **Messaging** (optional): `gtm-plan` for tone and key points.

Include only what actually shipped. If something is partial or behind a flag, say so.

## Steps
1. Group changes into **New**, **Improved**, **Fixed** and, if needed, **Heads up** (breaking or
   behavior changes).
2. For each item write a **benefit-led headline** ("Export reports to CSV"), not the internal name.
3. Add one or two sentences: **what it does and how to use it**, with a link to docs.
4. Put the **most important change first**; drop internal refactors.
5. Call out **breaking changes** and required actions with dates.
6. Check **tone**: plain words, no blame, no hype, no internal jargon or ticket IDs.
7. Add the **availability**: who gets it, when, which plan or region.
8. Have a second reader confirm accuracy against what shipped.

## Output template
```markdown
# <Product> release notes - <date / version>
## New   ## Improved   ## Fixed   ## Heads up (action required by <date>)
```

## Quality checklist
- [ ] Every item leads with a customer benefit.
- [ ] Only shipped changes are included.
- [ ] Breaking changes are called out with required actions.
- [ ] No internal jargon or ticket IDs.
- [ ] Availability stated.

## Handoff
Writes `artifacts/launch/<date>-release-notes-<version>.md`. Publishing it is an outward action
and needs approval in the dashboard.
