# Commands

context-db's behavior is exposed as sub-commands on a single dispatcher script:

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

Each sub-command loads a different prompt template, may consult
`.context-db.json` for mode/model overrides, and prints text the agent acts on.
Multi-word instructions must be quoted as a single argument.

The script runs in any terminal. Most agents wrap it for ergonomics — see
[Per-agent invocation](#per-agent-invocation) below.

## Read commands

### `prompt <instruction>`

Navigate context-db for context relevant to the instruction. The agent loads the
TOC, follows descriptions that match, reads selectively, and applies what it
finds. Use this when the agent should ground its next steps in project knowledge
before answering or coding.

```
prompt "How does the dispatcher decide whether to spawn a sub-agent?"
```

### `pre-review <plan>`

Pre-flight check. The agent fetches standards and conventions that apply to a
described change and surfaces anything the plan would violate before code is
written. Cheaper to fix a plan than to fix the diff.

### `review`

Audits the current diff or branch against context-db conventions. Reads only the
standards relevant to what changed. Defaults to a stronger model because review
needs more reasoning depth than navigation.

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

Seven-phase audit: structural health, content freshness, content value, coverage
gaps, doc drift, cross-references, reindex. Default posture is to **cut** —
leave context-db smaller and sharper. An optional folder argument scopes the
audit. Interactive by default; can run in `Review` or `Autonomous` mode.

## Loader commands

### `load-start-context`

Emits the on-start payload: read-mechanics, context-usage framing, and every
file matched by `on_start` and `on_all` globs from `.context-db.json`, inlined
raw. The default rule calls this once per session. See [Rules](rules.md) and
[Configuring Posture](configuring-posture.md).

### `load-manual <section>`

Loads a single instruction template by name — `read-mechanics`,
`write-mechanics`, `pre-review`, `review`, and others. Useful mid-conversation
when the agent has lost a specific skill instruction.

```
load-manual --help        # list sections
load-manual write-mechanics
```

## Per-agent invocation

Each agent has its own way of making the dispatcher ergonomic. The underlying
script call is identical.

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
the chat with the terminal tool, or define a shell alias:

```bash
alias cdb='python3 .claude/skills/context-db/scripts/context-db-main-agent.py'
cdb prompt "..."
```

A project-level `.cursor/rules/` file can document the alias so the agent uses
it consistently.

### Codex / generic

The agent runs the script directly via its shell tool, exactly as shown at the
top of this page. No wrapper required.

## Where to set per-command behavior

Mode (`main-agent` / `sub-agent`), model (`haiku` / `sonnet` / `opus`), and
posture toggles are configured per command in `.context-db.json`. See
[Configuring Posture](configuring-posture.md).
