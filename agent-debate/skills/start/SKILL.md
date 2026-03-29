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

After parsing, validate **before** proceeding:

- **`--rounds` value must be a positive integer**: If the value after `--rounds` is not a number (e.g. `--rounds abc`), is zero, negative, or a decimal, tell the user: "Invalid --rounds value '...'. Please provide a positive integer (e.g. --rounds 3)." and stop.
- **`--rounds` must be between 1 and 10**: If the number is outside this range, tell the user: "Rounds must be between 1 and 10. Got: N." and stop.
- **`--evidence` path must be a valid directory**: If provided, verify the path exists using `ls` or `Bash`. If it does not exist, tell the user: "Evidence directory not found: '...'. Please provide a valid directory path." and stop.
- **`TOPIC` must not be empty**: If no topic remains after extracting the flag, ask the user "What topic would you like to debate?" and wait.

Only proceed once `ROUNDS` (valid integer or `auto`), `TOPIC` (non-empty string), and `EVIDENCE_DIR` (valid path or empty) are confirmed.

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

You are the **moderator**. After parsing and validating arguments, you run the debate directly from this session — no intermediate subagent.

1. **Read the moderator instructions**: Read `agents/moderator.md` and follow them exactly for the rest of the debate. Those instructions define the full orchestration protocol: team creation, teammate spawning, round execution, context threading, output writing, and cleanup.

2. **Pass the parsed values**: As you follow the moderator instructions, use these values:
   - `TOPIC` → the parsed topic
   - `ROUNDS` → the parsed round count (a number or `auto`)
   - `EVIDENCE_DIR` → the evidence directory path (or empty string if not provided)

   The moderator instructions reference `<topic>`, `<rounds>`, and `<evidence>` tags — substitute the parsed values from above.

3. **Run the full debate**: Follow the moderator instructions through setup, round execution, and cleanup. You are the moderator — you create the team, spawn teammates, and orchestrate the entire debate from this session.

4. **Report results**: When the debate completes, point the user to the output directory for full transcripts.
