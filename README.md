# agent-debate

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that runs multi-agent adversarial debates. Four persistent agents argue any topic through structured rounds to produce a rigorous synthesis.

Built on Claude Code's **Team agents** feature — each debater is an independent agent with their own context window, so they remember and evolve their arguments across rounds.

## Quick Start

### From the marketplace

```bash
claude plugin marketplace add athrael-soju/kimchi-cult
claude plugin install agent-debate@kimchi-cult
```

### For local development

```bash
git clone https://github.com/athrael-soju/agent-debate.git
claude --plugin-dir ./agent-debate/agent-debate
```

Then inside Claude Code:

```
/agent-debate:start "Should AI systems have legal personhood?"
/agent-debate:start --rounds 2 "Is water wet?"
```

## How It Works

The plugin spawns a team of 5 agents:

| Agent | Role |
|-------|------|
| **Debate Lead** | Orchestrates rounds, manages tasks, writes output |
| **Critic** | Finds every weakness, logical flaw, and unsupported claim |
| **Advocate** | Builds and defends the strongest version of the position |
| **Judge** | Evaluates arguments impartially, controls when the debate ends |
| **Scribe** | Records neutral summaries and produces the final synthesis |

### Debate Flow

```
/agent-debate:start [--rounds N] "<topic>"
        |
   debate-lead
        |
        +-- spawns critic, advocate, judge, scribe
        |
        +-- if --rounds given, use N
        |   if omitted, judge recommends round count
        |
   ROUND 1
        |  critic -----> critique with severity ratings
        |  advocate ---> point-by-point defense
        |  judge ------> impartial evaluation
        |  scribe -----> round summary
        |
   ROUND 2..N
        |  ...same flow, agents remember previous rounds...
        |
   FINAL ROUND (judge must issue binding ruling)
        |  ...same flow, judge issues JUDGE'S RULING...
        |
   FINAL SYNTHESIS
        |  scribe produces comprehensive report
        |
   OUTPUT --> debate-output/
```

Each round runs sequentially: **Critic -> Advocate -> Judge -> Scribe**. The judge can end the debate early if arguments become circular or repetitive. Only the judge and debate-lead know the total round count — other agents argue on the merits without convergence pressure.

### Output

Results are written to `debate-output/`:

- `round-1.md`, `round-2.md`, etc. — per-round transcripts with all four agent outputs
- `final-synthesis.md` — structured report with verdicts

The final synthesis includes:
- Points of agreement
- Concessions from each side
- Dismissed arguments (with reasoning)
- Judge's per-issue rulings (ACCEPTED / REJECTED / REVISION REQUIRED)
- Unresolved disagreements
- Overall verdict

## Why Teams (Not Subagents)

Each agent is a **persistent teammate** with their own context window, not a stateless subagent that starts fresh each invocation. This means:

- The **critic** remembers their own arguments and can sharpen them ("In round 1 I raised X — the advocate's response was insufficient because...")
- The **advocate** builds on previous defenses without re-reading everything
- The **judge** tracks argument quality over time and notices patterns
- The **scribe** produces increasingly informed summaries with accurate issue tracking

This persistent context is what makes the debate feel like a real conversation rather than independent evaluations.

### Tradeoffs

- Higher token usage (5 separate context windows)
- Teams are an experimental Claude Code feature
- More coordination overhead than simple subagent calls

## Project Structure

```
agent-debate/                       # repo root
├── agent-debate/                   # plugin directory
│   ├── .claude-plugin/
│   │   └── plugin.json            # Plugin manifest
│   ├── agents/
│   │   ├── debate-lead.md         # Team lead — orchestrates rounds
│   │   ├── critic.md              # Adversarial thinker
│   │   ├── advocate.md            # Rigorous defender
│   │   ├── judge.md               # Impartial arbiter
│   │   └── scribe.md              # Neutral recorder
│   ├── skills/
│   │   ├── start/
│   │   │   └── SKILL.md           # /agent-debate:start entry point
│   │   └── cleanup/
│   │       └── SKILL.md           # /agent-debate:cleanup teardown
│   ├── output-styles/
│   │   └── agent-debate.md        # Output formatting guide
│   ├── settings.json              # Agent model configuration
│   └── CLAUDE.md                  # Plugin docs (loaded into context)
├── README.md
├── LICENSE                         # MIT
└── .gitignore
```

## Configuration

`settings.json` sets the debate lead to use the `opus` model for orchestration quality. Teammate agents inherit the default model.

```json
{
  "agent": {
    "debate-lead": {
      "model": "opus"
    }
  }
}
```

## License

MIT
