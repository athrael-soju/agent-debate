# agent-debate

A Claude Code plugin that runs multi-agent adversarial debates using Team agents.

## Usage

```
/agent-debate:start [--rounds N] <topic>
```

Examples:
```
/agent-debate:start "Should AI systems have legal personhood?"
/agent-debate:start --rounds 2 "Is water wet?"
/agent-debate:start --rounds 5 "Should humanity pursue interstellar colonization?"
```

When `--rounds` is omitted, the judge automatically recommends a round count based on topic complexity.

## How It Works

The plugin creates a **team of 3 agents** that debate any topic through structured rounds:

1. **Critic** — finds every weakness, logical flaw, and unsupported claim
2. **Advocate** — builds and defends the strongest version of the position
3. **Judge** — evaluates arguments impartially, verifies claims, controls debate termination, and produces the final synthesis

A **debate-lead** agent orchestrates the team, managing rounds, threading context, and collecting output.

## Debate Flow

**Round 1**: Advocate → Critic → Judge (advocate establishes the case first)

**Round 2+**: Critic → Advocate → Judge (critic leads with objections)

- The number of rounds is configurable via `--rounds N`
- When omitted, the judge assesses topic complexity and recommends a round count
- The final round requires the judge to issue a binding ruling with synthesis and quality metrics
- The judge can end the debate early if arguments become circular
- Only the judge and debate-lead know the total round count — other agents argue on the merits without convergence pressure

## Context Threading

The debate-lead threads context between rounds via:
- **Issue tracker**: A running file (`issue-tracker.md`) in the output directory, updated after each round based on the judge's assessment. Tracks resolved, open, and stalled issues.
- **Task descriptions**: Each round's task descriptions include the issue tracker contents and file paths to prior round outputs, so agents can read the raw arguments for full context.

## Output

Results are written to the output directory (typically `debate-output/`, with collision avoidance for successive debates):

```
<output-dir>/
  round-1/
    advocate.md
    critic.md
    judge.md
  round-2/
    critic.md
    advocate.md
    judge.md
  ...
  issue-tracker.md
  debate.log
```

The judge's final ruling (in the last round's `judge.md`) serves as the debate's synthesis, including per-issue verdicts, points of agreement, concessions, dismissed arguments, unresolved disagreements, and quality metrics.

## Agent Files

Agent instructions live in `agents/`:
- `debate-lead.md` — orchestrator
- `critic.md` — adversarial thinker
- `advocate.md` — rigorous defender
- `judge.md` — impartial arbiter
