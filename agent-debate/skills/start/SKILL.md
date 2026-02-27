---
name: start
description: Launch a multi-round adversarial debate on any topic using a team of four agents
---

You are launching the **agent-debate** plugin — a multi-agent adversarial debate system.

The user wants to debate the following topic: **$ARGUMENTS**

If `$ARGUMENTS` is empty, ask the user: "What topic would you like to debate?" and wait for their response before proceeding.

## Your job

Delegate entirely to the `debate-lead` agent by spawning it with the Task tool:

```
Task(
  subagent_type: "general-purpose",
  name: "debate-lead",
  prompt: "You are the debate lead. Launch and orchestrate a full adversarial debate on the topic: <topic>$ARGUMENTS</topic>. Follow your agent instructions in agents/debate-lead.md exactly.",
  mode: "bypassPermissions"
)
```

The debate-lead agent handles everything: team creation, round orchestration, output writing, and cleanup.

Wait for the debate-lead to finish, then report the results to the user. Point them to the `debate-output/` directory for the full transcripts.
