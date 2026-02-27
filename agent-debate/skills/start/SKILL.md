---
name: start
description: Launch a multi-round adversarial debate on any topic using a team of four agents
---

You are launching the **agent-debate** plugin — a multi-agent adversarial debate system.

The user's raw input is: `$ARGUMENTS`

## Argument Parsing

1. **Check for `--rounds N` flag**: Scan `$ARGUMENTS` for `--rounds <number>`. If found, extract the number as `ROUNDS` and remove the flag from the arguments. The remaining text is the `TOPIC`.
2. **If no `--rounds` flag**: Set `ROUNDS` to `auto`. The entire `$ARGUMENTS` is the `TOPIC`.
3. **If `TOPIC` is empty** after parsing: Ask the user "What topic would you like to debate?" and wait for their response before proceeding.

Examples:
- `--rounds 2 "Is water wet?"` → ROUNDS=2, TOPIC=`Is water wet?`
- `"Is water wet?" --rounds 4` → ROUNDS=4, TOPIC=`Is water wet?`
- `"Should AI have rights?"` → ROUNDS=auto, TOPIC=`Should AI have rights?`

## Your job

Delegate entirely to the `debate-lead` agent by spawning it with the Task tool:

```
Task(
  subagent_type: "general-purpose",
  name: "debate-lead",
  prompt: "You are the debate lead. Launch and orchestrate a full adversarial debate. Follow your agent instructions in agents/debate-lead.md exactly.

<topic>TOPIC</topic>
<rounds>ROUNDS</rounds>",
  mode: "bypassPermissions"
)
```

Replace `TOPIC` with the parsed topic and `ROUNDS` with the parsed round count (a number or `auto`).

The debate-lead agent handles everything: team creation, round orchestration, output writing, and cleanup.

Wait for the debate-lead to finish, then report the results to the user. Point them to the `debate-output/` directory for the full transcripts.
