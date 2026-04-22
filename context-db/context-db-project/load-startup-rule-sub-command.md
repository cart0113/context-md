---
description:
  load-startup-rule subcommand and the load_on_startup / load_always config
  fields — two-tier always-loaded content, inlined (not referenced) so it lands
  in context reliably.
---

## What it does

`load-startup-rule` emits the session-startup orientation: content inlined from
`load_on_startup`, then content inlined from `load_always` with an `IMPORTANT!`
preamble, then the standard read-mechanics and read-usage blocks. Rule files
(`templates/rules/startup-*.md`) delegate to this command so changes to the two
config lists propagate without editing rules.

## Usage

    /context-db load-startup-rule

No arguments. Config is read from `.context-db.json`.

## Config fields

Two top-level lists of glob patterns, relative to `context-db/`:

- `load_on_startup` — fires once per session via the startup rule, and on demand
  via the `--load-startup-rule` flag on other subcommands. Use for orienting
  content an agent needs to read to work effectively on the project. Heavier
  content is OK here; it loads once.
- `load_always` — fires automatically at the top of every subcommand invocation
  (`prompt`, `pre-review`, `review`, `update`, `maintain`). Must be BRIEF — real
  estate is at a premium because this content lands in front of every command
  output.

Both default to empty. Opt in by adding globs. Folders expand recursively; globs
use pathlib semantics.

Example:

```jsonc
{
  "load_on_startup": ["*-project/PROJECT.md"],
  "load_always": ["*-project/critical-invariants.md"],
}
```

## Flags on other subcommands

`--load-startup-rule` on `prompt`, `pre-review`, `review`, `update`, and
`maintain` prepends the expanded `load_on_startup` block to that command's
output. Intended for sub-agent invocations that missed the session-start load.
`load_always` fires on every subcommand automatically — no flag needed.

## Design rationale

**Inline, don't delegate.** Output includes the full file contents, not a "you
must read X" instruction. Telling an agent to read a file is unreliable; putting
the bytes in front of the model is not. The `read` subcommand exists for the
same reason — anywhere the agent must see content, we emit the content.

**Two tiers.** `load_always` runs on every subcommand, so it multiplies across
the session and must stay small. `load_on_startup` runs once per session and can
carry more orienting material. Mixing the two would either bloat every command
or starve the startup of useful context.

**Auto-fire for `load_always`, flag-gated for `load_on_startup`.** The
always-tier is cheap enough to include unconditionally. Startup content is
heavier, so it's opt-in via the flag (and fires automatically only via the rule
file at session start).

**Preamble only for `load_always`.** Because it lands mid-session in front of
arbitrary commands, it gets an `IMPORTANT!` framing so the agent treats it as
binding. Startup content is self-framing — the agent is orienting anyway.
