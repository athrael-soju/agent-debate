# agent-debate

A Claude Code plugin that runs multi-agent adversarial debates using Team agents.

## Usage

```
/agent-debate:start <topic>
```

Example:
```
/agent-debate:start "Should AI systems have legal personhood?"
```

## How It Works

The plugin creates a **team of 4 agents** that debate any topic through structured rounds:

1. **Critic** — finds every weakness, logical flaw, and unsupported claim
2. **Advocate** — builds and defends the strongest version of the position
3. **Judge** — evaluates arguments impartially and controls debate termination
4. **Scribe** — records neutral summaries and produces the final synthesis

A **debate-lead** agent orchestrates the team, managing rounds and collecting output.

## Debate Flow

Each round runs sequentially: Critic → Advocate → Judge → Scribe

- **Round 1**: Initial critique, defense, evaluation, and summary
- **Round 2**: Focus on unresolved issues from round 1
- **Round 3** (final): Judge must issue a binding ruling

The judge can end the debate early if arguments become circular.

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
