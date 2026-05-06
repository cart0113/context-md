---
description:
  load-start-context subcommand and the on_start / on_all / on_<command> config
  fields — three-tier always-loaded content, inlined (not referenced) so it
  lands in context reliably.
---

## What it does

`load-start-context` emits the on-start context in this order:

1. `read-mechanics` — how to navigate `context-db/` via the TOC script
2. `context-usage` — context-db is a map, not truth; verify against code
3. `on_start` files — inlined raw, frontmatter stripped
4. `on_all` files — inlined raw, frontmatter stripped

Rule files (`templates/rules/context-db.md`) delegate to this command so changes
to the always-loaded config lists propagate without editing rules.

Inlined files are printed as-is. The tool adds no preamble, no section header,
and no path attribution — the file's author owns the framing. If you want a
heading or an `IMPORTANT!` line, put it in the file.

The `read` subcommand is what this code uses internally to strip frontmatter and
concatenate files. It's system machinery — the agent does not need to know about
it, so it is not taught here.

## Usage

    /context-db load-start-context

No arguments. Config is read from `.context-db.json`.

## Config fields

Top-level lists of glob patterns, relative to `context-db/`. Three tiers,
ordered broadest scope to narrowest:

- `on_start` — fires once per session via the on-start context, and on demand
  via the `--load-start-context` flag on other subcommands. Use for orienting
  content an agent needs to read to work effectively on the project. Heavier
  content is OK here; it loads once.
- `on_all` — fires automatically at the end of every subcommand invocation
  (`prompt`, `pre-review`, `review`, `update`, `maintain`). Must be BRIEF — real
  estate is at a premium because this content lands in front of every command
  output.
- `on_<command>` — fires only when that subcommand runs, right after `on_all`.
  One key per subcommand: `on_prompt`, `on_pre_review`, `on_review`,
  `on_update`, `on_maintain`. Use to surface rules that only matter for a
  specific operation, without paying their cost on the others.

All default to empty. Opt in by adding globs. Folders expand recursively; globs
use pathlib semantics.

Example:

```jsonc
{
  "on_start": ["*-project/ON_START.md"],
  "on_all": ["*-project/ON_ALL.md"],
  "on_prompt": ["*-project/<some-tool>/local-notes.md"],
}
```

Boilerplate files for the always-on tiers live at
`templates/context-db-files/ON_START.md` and
`templates/context-db-files/ON_ALL.md` — copy into a project's `<name>-project/`
folder and populate. The per-command lists have no boilerplate — they exist for
narrowly scoped supplements that don't generalize.

### `on_<command>` use case: layering local notes on a shared doc folder

The motivating case: `context-db/<tool-name>/` ships from another repo (often
symlinked) and is read-only — you can't add project-specific gotchas there. The
local supplement goes inside the project folder
(`context-db/<name>-project/<tool-name>/local-notes.md`) and rides into context
via `on_prompt`:

```jsonc
{
  "on_prompt": ["<name>-project/<tool-name>/local-notes.md"],
}
```

Now `/context-db prompt` always sees the local supplement right before the
user's instruction, while `update` / `review` / `maintain` skip it. Same lever
for review checklists (`on_review`), house rules about where new entries belong
(`on_update`), or audit invariants (`on_maintain`).

## Flags on other subcommands

`--load-start-context` on `prompt`, `pre-review`, `review`, `update`, and
`maintain` prepends the expanded `on_start` block to that command's output.
Intended for sub-agent invocations that missed the on-start load. `on_all` fires
on every subcommand automatically — no flag needed.

## Placement in command output

- `on_start` is emitted at the very top when the flag is used (orientation
  first).
- `on_all` is emitted near the **end** of each command's output, right before
  the user's instructions block (or last, if the command has no
  user-instructions block — `maintain`). Recency matters: the final thing the
  model reads carries more weight, so always-on rules sit as close to the user's
  ask as possible.
- `on_<command>` is emitted immediately after `on_all`, so the per-command
  supplement is the very last always-on block before the user's instructions.
  Narrower scope wins recency.

## Design rationale

**Inline, don't delegate.** Output includes the full file contents, not a "you
must read X" instruction. Telling an agent to read a file is unreliable; putting
the bytes in front of the model is not. The `read` subcommand exists for the
same reason — anywhere the agent must see content, we emit the content.

**Three tiers, broadest to narrowest.** `on_start` runs once per session and can
carry more orienting material. `on_all` runs on every subcommand, so it
multiplies across the session and must stay small. `on_<command>` is scoped to a
single operation — a 50-line `on_prompt` only costs you on `prompt` calls, not
on every command. Mixing the tiers would either bloat unrelated commands or
starve specific operations of supplements they need.

**Auto-fire for `on_all` and `on_<command>`, flag-gated for `on_start`.** The
always-tiers are cheap enough to include unconditionally for the operation they
target. On-start content is heavier, so it's opt-in via the flag (and fires
automatically only via the rule file at session start).

**No tool-injected framing.** The system doesn't add preambles, headers, or path
tags to inlined files. Whatever the file contains is what the agent sees. If you
want an `IMPORTANT!` line or a section heading, put it in the file — the author
controls the framing.
