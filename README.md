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
/agent-debate:start --evidence ./research "Is fusion energy viable by 2040?"
/agent-debate:start --rounds 3 --evidence /path/to/papers "Should we colonize Mars?"
```

## How It Works

The plugin creates a team of 3 agents, orchestrated by a debate-lead:

| Agent | Role |
|-------|------|
| **Debate Lead** | Orchestrator — manages rounds, threads context, writes output |
| **Critic** | Finds every weakness, logical flaw, and unsupported claim |
| **Advocate** | Builds and defends the strongest version of the position |
| **Judge** | Evaluates arguments impartially, fact-checks claims, controls when the debate ends, and produces the final synthesis |

### Debate Flow

```
/agent-debate:start [--rounds N] [--evidence <path>] "<topic>"
        |
   debate-lead
        |
        +-- spawns critic, advocate, judge
        |
        +-- if --rounds given, use N
        |   if omitted, judge recommends round count
        |
        +-- if --evidence given, index directory
        |   and include file listing in every task
        |
   EVERY ROUND (advocate always goes first)
        |  advocate --> research + defense (Round 1: from scratch, Round 2+: responds to prior critique)
        |  lead -----> writes handoff notes (debate-lead.md)
        |  critic ---> research + critique of advocate's defense
        |  judge ----> fact-check + evaluation + issue tracking
        |
   FINAL ROUND (judge must issue binding ruling)
        |  ...same flow, judge issues JUDGE'S RULING...
        |
   OUTPUT --> debate-output/
```

Each round runs sequentially with a consistent order: advocate, then debate-lead handoff, then critic, then judge. The debate-lead **redacts internal sections** (Research Log, Sources, self-assessment labels) when passing output between agents — each side only sees the other's public argument with inline citations. The judge receives full unredacted output to score research effort.

The judge can end the debate early if arguments become circular or repetitive. Only the judge and debate-lead know the total round count — other agents argue on the merits without convergence pressure.

After each advocate and critic turn, the debate-lead outputs a brief progress summary (round number, key points, file path) so you can follow the debate as it unfolds.

### Research Enforcement

All agents must conduct independent web research before arguing. Each agent's output includes a **Research Log** documenting:
- Web searches performed and key findings
- Evidence directory files examined (if `--evidence` was provided)

The judge scores research effort in the final ruling — arguments that cite only the subject material ("closed-book arguing") carry less weight than those corroborated by independent sources. Fabricated citations are flagged as serious offenses.

### Output

Results are written to `debate-output/`:

```
debate-output/
  round-1/
    advocate.md
    debate-lead.md
    critic.md
    judge.md
  round-2/
    advocate.md
    debate-lead.md
    critic.md
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

- Higher token usage (4 separate context windows — debate-lead + 3 agents)
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
