# agent-debate

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that runs multi-agent adversarial debates. Three persistent agents argue any topic through structured rounds, culminating in a judge's binding ruling.

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

The plugin spawns a team of 4 agents:

| Agent | Role |
|-------|------|
| **Debate Lead** | Orchestrates rounds, manages tasks, writes output |
| **Critic** | Finds every weakness, logical flaw, and unsupported claim |
| **Advocate** | Builds and defends the strongest version of the position |
| **Judge** | Evaluates arguments impartially, verifies claims, controls when the debate ends, and produces the final synthesis |

### Debate Flow

```
/agent-debate:start [--rounds N] "<topic>"
        |
   debate-lead
        |
        +-- spawns critic, advocate, judge
        |
        +-- if --rounds given, use N
        |   if omitted, judge recommends round count
        |
   ROUND 1 (advocate establishes the case first)
        |  advocate --> point-by-point defense
        |  critic ---> critique with severity ratings
        |  judge ----> impartial evaluation
        |
   ROUND 2..N (critic leads with objections)
        |  critic ---> sharpened critique
        |  advocate -> refined defense
        |  judge ----> evaluation + issue tracking
        |
   FINAL ROUND (judge must issue binding ruling)
        |  ...same flow, judge issues JUDGE'S RULING...
        |
   OUTPUT --> debate-output/
```

Each round runs sequentially. The judge can end the debate early if arguments become circular or repetitive. Only the judge and debate-lead know the total round count — other agents argue on the merits without convergence pressure.

### Output

Results are written to `debate-output/`:

```
debate-output/
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

The judge's final ruling (in the last round's `judge.md`) serves as the debate synthesis, including:
- Per-issue verdicts (ACCEPTED / REJECTED / REVISION REQUIRED)
- Points of agreement
- Concessions from each side
- Dismissed arguments (with reasoning)
- Unresolved disagreements
- Quality metrics

## Why Teams (Not Subagents)

Each agent is a **persistent teammate** with their own context window, not a stateless subagent that starts fresh each invocation. This means:

- The **critic** remembers their own arguments and can sharpen them ("In round 1 I raised X — the advocate's response was insufficient because...")
- The **advocate** builds on previous defenses without re-reading everything
- The **judge** tracks argument quality over time and notices patterns

This persistent context is what makes the debate feel like a real conversation rather than independent evaluations.

### Tradeoffs

- Higher token usage (4 separate context windows)
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
│   │   └── judge.md               # Impartial arbiter + synthesizer
│   ├── skills/
│   │   ├── start/
│   │   │   └── SKILL.md           # /agent-debate:start entry point
│   │   └── cleanup/
│   │       └── SKILL.md           # /agent-debate:cleanup teardown
│   ├── style-guides/
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
