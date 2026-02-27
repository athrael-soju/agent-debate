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

The plugin creates a **team of 4 agents** that debate any topic through structured rounds:

1. **Critic** — finds every weakness, logical flaw, and unsupported claim
2. **Advocate** — builds and defends the strongest version of the position
3. **Judge** — evaluates arguments impartially and controls debate termination
4. **Scribe** — records neutral summaries and produces the final synthesis

A **debate-lead** agent orchestrates the team, managing rounds and collecting output.

## Debate Flow

Each round runs sequentially: Critic → Advocate → Judge → Scribe

- The number of rounds is configurable via `--rounds N` (2-5)
- When omitted, the judge assesses topic complexity and recommends a round count
- The final round requires the judge to issue a binding ruling
- The judge can end the debate early if arguments become circular
- Only the judge and debate-lead know the total round count — other agents argue on the merits without convergence pressure

## Output

Results are written to `debate-output/`:
- `round-1.md`, `round-2.md`, etc. — per-round transcripts
- `final-synthesis.md` — comprehensive synthesis with verdicts

## Key Design: Persistent Context

Each agent is a persistent teammate (not a stateless subagent), so they **remember** previous rounds:
- The critic evolves their arguments across rounds
- The advocate builds on previous defenses
- The judge tracks argument quality over time
- The scribe produces increasingly informed summaries

## Agent Files

Agent instructions live in `agents/`:
- `debate-lead.md` — orchestrator
- `critic.md` — adversarial thinker
- `advocate.md` — rigorous defender
- `judge.md` — impartial arbiter
- `scribe.md` — neutral recorder
