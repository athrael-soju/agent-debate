---
name: start
description: Launch a multi-round adversarial debate on any topic using a team of three agents
---

You are launching the **agent-debate** plugin — a multi-agent adversarial debate system.

The user's raw input is: `$ARGUMENTS`

## Argument Parsing

1. **Check for `--rounds N` flag**: Scan `$ARGUMENTS` for `--rounds <value>`. If found, extract `<value>` as the candidate round count and remove the flag from the arguments.
2. **Check for `--evidence <path>` flag**: Scan the remaining arguments for `--evidence <value>`. If found, extract `<value>` as the `EVIDENCE_DIR` and remove the flag. This is an optional directory path containing supporting evidence files (papers, data, reports, etc.) that agents must search through during the debate.
3. **If no `--rounds` flag**: Set `ROUNDS` to `auto`.
4. **If no `--evidence` flag**: Set `EVIDENCE_DIR` to empty (no evidence directory).
5. The remaining text after extracting all flags is the `TOPIC`.
6. **If `TOPIC` is empty or whitespace-only** after parsing: Ask the user "What topic would you like to debate?" and wait for their response before proceeding.

### Input Validation

After parsing, validate **before** spawning the debate-lead:

- **`--rounds` value must be a positive integer**: If the value after `--rounds` is not a number (e.g. `--rounds abc`), is zero, negative, or a decimal, tell the user: "Invalid --rounds value '...'. Please provide a positive integer (e.g. --rounds 3)." and stop.
- **`--rounds` must be between 1 and 10**: If the number is outside this range, tell the user: "Rounds must be between 1 and 10. Got: N." and stop.
- **`--evidence` path must be a valid directory**: If provided, verify the path exists using `ls` or `Bash`. If it does not exist, tell the user: "Evidence directory not found: '...'. Please provide a valid directory path." and stop.
- **`TOPIC` must not be empty**: If no topic remains after extracting the flag, ask the user "What topic would you like to debate?" and wait.

Only proceed to spawn the debate-lead once `ROUNDS` (valid integer or `auto`), `TOPIC` (non-empty string), and `EVIDENCE_DIR` (valid path or empty) are confirmed.

### Examples

- `--rounds 2 "Is water wet?"` → ROUNDS=2, TOPIC=`Is water wet?`, EVIDENCE_DIR=empty
- `"Is water wet?" --rounds 4` → ROUNDS=4, TOPIC=`Is water wet?`, EVIDENCE_DIR=empty
- `"Should AI have rights?"` → ROUNDS=auto, TOPIC=`Should AI have rights?`, EVIDENCE_DIR=empty
- `--evidence ./research "Should AI have rights?"` → ROUNDS=auto, TOPIC=`Should AI have rights?`, EVIDENCE_DIR=`./research`
- `--rounds 3 --evidence /path/to/papers "Is fusion viable?"` → ROUNDS=3, TOPIC=`Is fusion viable?`, EVIDENCE_DIR=`/path/to/papers`
- `--rounds abc "topic"` → error: invalid rounds value
- `--rounds 0 "topic"` → error: rounds must be between 1 and 10
- `--evidence /nonexistent "topic"` → error: evidence directory not found
- `--rounds 3` → ask for topic (empty after flag removal)

## Your job

Delegate entirely to the `debate-lead` agent by spawning it with the Task tool:

```
Task(
  subagent_type: "agent-debate:debate-lead",
  name: "debate-lead",
  prompt: "You are the debate lead. Launch and orchestrate a full adversarial debate. Follow your agent instructions in agents/debate-lead.md exactly.

<topic>TOPIC</topic>
<rounds>ROUNDS</rounds>
<evidence>EVIDENCE_DIR</evidence>",
  mode: "bypassPermissions"
)
```

Replace `TOPIC` with the parsed topic, `ROUNDS` with the parsed round count (a number or `auto`), and `EVIDENCE_DIR` with the evidence directory path (or empty string if not provided).

The debate-lead agent handles everything: team creation, round orchestration, output writing, and cleanup.

Wait for the debate-lead to finish, then report the results to the user. Point them to the `debate-output/` directory for the full transcripts.
