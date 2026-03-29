# agent-debate

A Claude Code plugin that runs multi-agent adversarial debates using Team agents.

## Usage

```
/agent-debate:start [--rounds N] [--evidence <path>] <topic>
```

Examples:
```
/agent-debate:start "Should AI systems have legal personhood?"
/agent-debate:start --rounds 2 "Is water wet?"
/agent-debate:start --rounds 5 "Should humanity pursue interstellar colonization?"
/agent-debate:start --evidence ./research "Is fusion energy viable by 2040?"
/agent-debate:start --rounds 3 --evidence /path/to/papers @paper.pdf
```

- When `--rounds` is omitted, the judge automatically recommends a round count based on topic complexity.
- When `--evidence` is provided, agents will search the directory for relevant files to use as primary sources alongside their web research.

## How It Works

The plugin creates a **team of 3 agents** that debate any topic through structured rounds:

1. **Critic** — finds every weakness, logical flaw, and unsupported claim
2. **Advocate** — builds and defends the strongest version of the position
3. **Judge** — evaluates arguments impartially, verifies claims, controls debate termination, and produces the final synthesis

Your main session acts as the **moderator**, orchestrating the team: creating teammates, managing rounds, threading context, and collecting output. This means teammates are visible in your CLI via Shift+Down.

### Research Enforcement

All agents are required to conduct independent research before arguing. Each agent's output must include a **Research Log** documenting web searches performed and evidence files examined. The judge scores agents on research effort — arguments that cite only the subject material under debate ("closed-book arguing") carry less weight than those corroborated by independent external sources.

When an `--evidence` directory is provided, agents must search it for relevant files in addition to performing web research.

## Debate Flow

**Every round**: Advocate → Moderator Handoff → Critic → Judge

- **Round 1**: Advocate builds the initial case from scratch, critic responds
- **Round 2+**: Advocate responds to the prior round's critique, critic responds to the advocate's updated defense

- The number of rounds is configurable via `--rounds N`
- When omitted, the judge assesses topic complexity and recommends a round count
- The final round requires the judge to issue a binding ruling with synthesis and quality metrics
- The judge can end the debate early if arguments become circular
- Only the judge and moderator know the total round count — other agents argue on the merits without convergence pressure

## Context Threading

The moderator threads context between rounds via:
- **Issue tracker**: A running file (`issue-tracker.md`) in the output directory, updated after each round based on the judge's assessment. Tracks resolved, open, and stalled issues.
- **Redacted handoffs**: When passing one agent's output to the other, the moderator strips internal sections (Research Log, Sources, self-assessment labels like DEFENDED/NEEDS TIGHTENING/VULNERABLE). Each agent only sees the other's public argument with inline citations. The judge receives full unredacted output from both sides to score research effort.
- **Task descriptions**: Each round's task descriptions include the issue tracker contents and file paths to prior round outputs for full context.

## Live Progress

The moderator outputs a brief summary to the user after each advocate and critic turn — round number, key points (2-3 bullets), and file path. This provides visibility as the debate unfolds rather than requiring the user to wait for the full debate to complete. Detailed events are also logged to `debate.log` for real-time monitoring via `tail -f`.

## Output

Results are written to the output directory (typically `debate-output/`, with collision avoidance for successive debates):

```
<output-dir>/
  round-1/
    advocate.md
    moderator.md
    critic.md
    judge.md
  round-2/
    advocate.md
    moderator.md
    critic.md
    judge.md
  ...
  issue-tracker.md
  debate.log
```

The judge's final ruling (in the last round's `judge.md`) serves as the debate's synthesis, including per-issue verdicts, points of agreement, concessions, dismissed arguments, unresolved disagreements, and quality metrics.

## Agent Files

Agent instructions live in `agents/`:
- `moderator.md` — orchestrator (followed by your main session)
- `critic.md` — adversarial thinker
- `advocate.md` — rigorous defender
- `judge.md` — impartial arbiter
