# Commands

context-db's behavior is exposed as sub-commands on a single dispatcher script:

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

This page describes each command at the level of "what would I use this for."

- For the literal `--help` output and the verbatim instruction text each command
  emits to the agent, see [CLI reference](../reference/cli.md) — it is generated
  from the dispatcher and the prompt templates so it cannot drift.
- For full payloads under different `.context-db.json` configs, see
  [Config Effects](../reference/config-effects.md).
- For per-command `mode` / `model` / posture overrides, see
  [Configuring Posture](configuring-posture.md).

Multi-word instructions must be quoted as a single shell argument. The script
runs in any terminal; most agents wrap it for ergonomics — see
[Per-agent invocation](#per-agent-invocation).

## Read commands

### `prompt <instruction>`

Re-inject context relevant to a specific piece of work. Use it when the agent
should ground its next step in project knowledge before answering or coding —
the standing rule already loads the on-start payload, but `prompt` pulls in just
the topical material the next task needs. Adding `--use-git-diff` focuses on
context-db files touched recently.

### `pre-review <plan>`

Pre-flight check before code is written. Surfaces standards and conventions that
apply to the described change so the plan can be adjusted before implementation.
Cheaper to fix a plan than to fix the diff.

### `review`

Audits the current diff or branch against context-db conventions. Reads only the
standards relevant to what changed. Defaults to a stronger model than the read
commands because review needs more reasoning depth than navigation.

## Write commands

### `update <what was learned>`

Files learnings into context-db — gotchas, convention decisions, surprises. The
agent picks the right home (defaulting to the project folder), updates
frontmatter descriptions, and re-runs the TOC where needed. Add `--push` to
commit and push the result in the same call.

```
update "Polling Linear webhooks doesn't deliver retries"
update --push "Same, and ship it"
```

### `maintain [folder]`

Multi-phase audit that keeps context-db from bloating into what it was built to
avoid: structural health, content freshness, content value, coverage gaps, doc
drift, cross-references, reindex. Default posture is to **cut**. An optional
folder argument scopes the audit.

## Loader commands

### `load-start-context`

Emits the on-start payload — read mechanics, context-usage framing, and every
file matched by `on_start` and `on_all` globs. The default rule calls this once
per session. See [Rules](rules.md) and
[Configuring Posture](configuring-posture.md).

### `load-manual <section>`

Loads a single instruction template by name (`read-mechanics`,
`write-mechanics`, `pre-review`, `review`, and others). Useful mid-conversation
when the agent has lost a specific skill instruction.

```
load-manual --help        # list sections
load-manual write-mechanics
```

## Per-agent invocation

The underlying script call is identical across agents. Each one has its own
ergonomic wrapper.

### Claude Code

The dispatcher is packaged as the `/context-db` skill, so commands run as:

```
/context-db prompt "..."
/context-db update --push "..."
```

The skill's `SKILL.md` quotes the user's instruction correctly and forwards
everything to the dispatcher.

### Cursor

No native skill system, so the simplest path is to call the script directly from
chat with the terminal tool, or define a shell alias:

```bash
alias cdb='python3 .claude/skills/context-db/scripts/context-db-main-agent.py'
cdb prompt "..."
```

A project-level `.cursor/rules/` file can document the alias so the agent uses
it consistently.

### Codex / generic

The agent runs the script directly via its shell tool, exactly as shown at the
top of this page. No wrapper required.
