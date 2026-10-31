---
name: interview-synthesis
description: >
  Turn collected raw material (interview notes, transcripts, survey answers, support tickets)
  into themes, evidence quotes and insights using affinity mapping. Use AFTER research data
  exists. Not for planning interviews (use interview-guide) and not for writing job statements
  or switching forces (use jobs-to-be-done).
stage: discover
stage_order: 2
version: 0.1.0
---

# Interview and research synthesis

Source: affinity diagramming, Nielsen Norman Group (https://www.nngroup.com/articles/affinity-diagram/).

## When to use
- Notes or transcripts from several sessions sit unread.
- A decision needs "what did we learn?" in a form others trust.
- Findings must be traced back to evidence.

## Inputs
- **Raw data** (required): transcripts, notes, survey responses or tickets. Read `research/`.
- **Research goal** (required): the question from the interview guide, or ask for it.
- **Participant info** (optional): segment and role per participant.

Never paraphrase beyond what was said. If evidence is thin, say so.

## Steps
1. State the research goal and list the sources and sample size.
2. Pull out **atomic observations**: one fact, behavior, quote or pain per note, tagged by participant.
3. **Cluster** similar observations into themes (affinity mapping); name each theme as a finding.
4. Count **how many participants** support each theme; separate majority patterns from outliers.
5. Attach the **best 1-2 verbatim quotes** per theme with the participant label.
6. Write **insights**: what the pattern means for the product, labeled as interpretation.
7. List **contradictions and gaps**, and what to ask next.
8. Rank findings by frequency and impact and give 3-5 **recommended actions**.

## Output template
```markdown
# Research synthesis: <topic>  (n = <participants>)
## Goal and sources
## Themes (finding, support n/N, quotes)
## Insights (interpretation, labeled)
## Contradictions and gaps
## Recommendations
```

## Quality checklist
- [ ] Every theme shows participant counts and quotes.
- [ ] Observations are separated from interpretation.
- [ ] Outliers are named, not hidden.
- [ ] Gaps and next questions listed.
- [ ] Recommendations trace to themes.

## Handoff
Writes `artifacts/discover/<date>-synthesis-<topic>.md` and files raw sources under `research/`.
Consumed by `jobs-to-be-done`, `opportunity-solution-tree` and `product-strategy`.
