# Agent Debate Output Style

## Citation Format

All agent outputs should use inline citations. The viewer renders these as styled badges/links.

### Sourced Claims
```
The recidivism rate was 43% [Source: "Title of Paper", Author, Year](https://example.com/paper)
```

### Unsourced Claims
```
This suggests a broader trend [Unsourced -- analytical reasoning, not empirically verified]
```

### Standard Links
```
See [Stanford Law Review analysis](https://example.com/article) for details
```

### Fact-Check Results (Judge Only)
```
## Fact-Check Report

### Verified Claims
- Critic's claim about X: CONFIRMED -- [Source corroborates](URL)

### Disputed Claims
- Advocate's claim about Y: DISPUTED -- Source says Z, not Y

### Fabricated Citations
- Advocate cited "Non-Existent Paper" -- this source does not appear to exist
```

## Round Summaries (`round-N.md`)

Each round file should follow this structure:

```markdown
# Round N

## Critic's Arguments
[Structured critique with severity ratings and citations]

## Advocate's Defense
[Point-by-point rebuttal with evidence and citations]

## Judge's Assessment
[Impartial evaluation of both sides, including fact-check report]

## Round Summary
[Scribe's neutral summary: resolved issues, open issues, concessions, trajectory]
```

## Final Synthesis (`final-synthesis.md`)

The final synthesis should follow this structure:

```markdown
# Debate Synthesis: [Topic]

## Debate Overview
- **Topic**: [Full topic statement]
- **Rounds completed**: N
- **Termination**: [Early ruling / Full rounds completed]

## Points of Agreement
[Issues where both sides converged]

## Concessions
[What each side conceded and why]

## Dismissed Arguments
[Arguments the judge found unpersuasive, with reasoning]

## Evidence Quality Assessment
[Summary of citation quality from both sides: verified claims, disputed claims, fabricated citations]

## Judge's Rulings
[Per-issue: ACCEPTED / REJECTED / REVISION REQUIRED, with evidence quality noted]

## Unresolved Disagreements
[Issues that remained contested]

## Verdict
[Judge's final assessment of the overall position]

## Sources
[Consolidated list of all sources cited during the debate, with notes on which agent cited them and whether they were verified]
```

## Formatting Guidelines

- Use clear markdown headers for structure
- Quote specific arguments when referencing them
- Use bullet points for lists of issues/arguments
- Include severity ratings where applicable (Critical / Major / Minor)
- Keep language precise and analytical -- no rhetorical flourishes in summaries
- **Every major claim must have an inline citation** -- unsourced claims should be explicitly marked
- Use markdown tables for counterargument assessments where appropriate
