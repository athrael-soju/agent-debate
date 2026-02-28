# Agent Debate Output Style

## Citation Format

All agent outputs should use inline citations.

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

## Round Output Structure (`<output-dir>/round-N/`)

Each round gets its own folder with independent files per agent:

```
<output-dir>/
  round-1/
    critic.md
    advocate.md
    judge.md
  round-2/
    ...
  issue-tracker.md
  debate.log
```

### `critic.md`
```markdown
# Round N — Critic

[Structured critique with severity ratings and citations]
```

### `advocate.md`
```markdown
# Round N — Advocate

[Point-by-point rebuttal with evidence and citations]
```

### `judge.md`
```markdown
# Round N — Judge

[Impartial evaluation of both sides, including fact-check report]
```

## Final Synthesis (Judge's Final Ruling)

The judge's final ruling (issued on the last round or via early termination) serves as the debate's final synthesis. It follows this structure within the judge's output file:

```markdown
## JUDGE'S RULING

### Per-Issue Verdicts
[For each open issue:]
- **[Issue]**: ACCEPTED / REJECTED / REVISION REQUIRED
  - Reasoning: [why]
  - Evidence quality: [assessment of sources cited by both sides]

### Points of Agreement
[Issues where both sides converged during the debate]

### Concessions
[What each side conceded during the debate and why]

### Dismissed Arguments
[Arguments the judge found unpersuasive from either side, with reasoning]

### Unresolved Disagreements
[Issues that remained genuinely contested through the end]

### Quality Metrics
- **Citations verified**: N confirmed, N disputed, N fabricated
- **Issues resolved**: N of M total
- **Issues stalled**: N (argued 2+ rounds without progress)
- **Argument evolution**: [Did arguments meaningfully develop across rounds, or mostly repeat?]

### Overall Verdict
[Judge's final assessment of the position as a whole]
```

## Formatting Guidelines

- Use clear markdown headers for structure
- Quote specific arguments when referencing them
- Use bullet points for lists of issues/arguments
- Include severity ratings where applicable (Critical / Major / Minor)
- Keep language precise and analytical -- no rhetorical flourishes in summaries
- **Every major claim must have an inline citation** -- unsourced claims should be explicitly marked
- Use markdown tables for counterargument assessments where appropriate
