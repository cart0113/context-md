# How `.context-db.json` shapes injected context

> [!note] Auto-generated. Do not edit by hand.
>
> This page is regenerated from the
> [`example/acme-payments-repo/`](https://github.com/cart0113/context-db/tree/main/example/acme-payments-repo)
> fixture by `bin/build-config-effects-docs.py`. The pre-commit
> hook re-runs the script whenever the dispatcher, prompt
> templates, or the example fixture change.

Each scenario below shows a different `.context-db.json` config and
the literal text the dispatcher emits for the listed sub-commands.
Output is what the calling agent reads on every invocation —
instruction templates, the `on_start` / `on_all` payload, and the
user instructions appended last.

See [Configuring Posture](../guide/configuring-posture.md) for the
full schema.

## Default config {#default}

The shipped default. `main-agent` mode, both `on_start` and `on_all` populated with the project's `ON_START.md` / `ON_ALL.md`.

**`.context-db.json`:**

```jsonc
{
  "defaults": {
    "mode": "main-agent"
  },
  "on_start": [
    "*-project/ON_START.md"
  ],
  "on_all": [
    "*-project/ON_ALL.md"
  ]
}
```

### `/context-db load-start-context`

<details>
<summary>injected context</summary>

```

# Read Mechanics

`context-db/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 .claude/skills/context-db/scripts/context-db-resolve-path.py <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.


# Context Usage

Context-db is a starting point, a map, a hint — not a complete picture. It
documents conventions, gotchas, design decisions, and cross-file connections
that you can't learn from reading any single file.

Use it to orient yourself, then verify against the actual project assets (code,
configs, docs, etc.). If what you read conflicts with what the project shows,
trust the project's assets, especially project code.


# On Start

Acme Payments is a three-tier payment service: API gateway, payment engine, and
an append-only ledger. Inter-service communication is async via message queue.

Before making changes:

- Architecture and API endpoints live under `acme-payments-project/`. Data-model
  conventions are in `acme-payments-project/data-model/`.
- Coding and git standards are shared with sister projects via symlinks
  (`coding-standards/`, `git-standards/`). Treat those as authoritative.
- The ledger is append-only — never write a path that mutates a posted
  transaction. Refunds and reversals are new entries, not edits.


# On All

Ledger entries are immutable. Never edit a posted transaction — file a reversal
entry instead.
```

</details>

### `/context-db prompt "How do I add a new payment endpoint?"`

<details>
<summary>injected context</summary>

```

# Read Mechanics

`context-db/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 .claude/skills/context-db/scripts/context-db-resolve-path.py <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.


# Context Usage

Context-db is a starting point, a map, a hint — not a complete picture. It
documents conventions, gotchas, design decisions, and cross-file connections
that you can't learn from reading any single file.

Use it to orient yourself, then verify against the actual project assets (code,
configs, docs, etc.). If what you read conflicts with what the project shows,
trust the project's assets, especially project code.


# Prompt Instructions

Navigate the project's context-db for context and standards directly relevant to
the user's request — things you would get wrong or miss without seeing them. Be
selective: use TOC descriptions to judge relevance, skip anything not directly
related, and don't read files just because they're nearby. Use what you find to
inform your response.

Do not run /context-db prompt yourself. The user invokes this. If you need more
context from context-db later, use the read mechanics above directly.


# On All

Ledger entries are immutable. Never edit a posted transaction — file a reversal
entry instead.


# Prompt User Instructions

How do I add a new payment endpoint?
```

</details>

### `/context-db update "Refunds must be filed as new entries, not edits"`

<details>
<summary>injected context</summary>

```

# Write Mechanics

`context-db/` is this project's knowledge base. When writing the db, to
see which folders and files you can edit, use the TOC script with
--no-external-symlinks:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py --no-external-symlinks context-db/

This filters out symlinked folders from other repos. Only edit local files.

Drill into subfolders the same way — run the TOC script again on a subfolder to
see its contents, always with --no-external-symlinks.

### File format

Every `.md` file needs YAML frontmatter with a `description` field — this is the
routing decision agents use to decide whether to open the file. Be specific:
"scheduler execution flow, budget enforcement hook" not "Architecture overview."

Two types:

- Documents — frontmatter + body
- Folder descriptors — frontmatter only, named `<folder-name>.md`

Every subfolder needs a folder descriptor. The root `context-db/` does not.

Structure:

- 5-10 items per folder
- 50-150 lines per file, 200 max
- If a file exceeds 200 lines, split it into a subfolder with the same name

Status field (optional in frontmatter): `draft`, `stable` (default when
omitted), `deprecated`, `experiment`, `work-in-progress`, `refactor`.

After changes, run the TOC script to verify YAML frontmatter is correct:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py <sub-folder-that-was-altered>/


# Project Folder

This repo's project folder is `context-db/acme-payments-project/`. That is where knowledge specific to this project lives. Other top-level folders under `context-db/` are external — global standards, shared conventions, or folders symlinked in from other repos.

When writing or maintaining context-db, default to writing inside the project folder. Only edit a parallel folder when the content is genuinely not project-specific.

# Context Db Memory System

Context-db is the project's memory system. Do not use auto-memory, MEMORY.md, or
any vendor-specific persistence. Users will call the /context-db update skill
when they want to persist important project knowledge. If you think you should
save something to memory, ask the user if they want to run /context-db update
instead.


# Update Instructions

Think about your current session — corrections the user made, conventions you
learned, pitfalls you hit, decisions and why. Then decide: would the next agent
get something wrong or miss something without this knowledge? If not, tell the
user there's nothing to add.

Most sessions produce nothing worth storing — that is the normal outcome, not a
failure. Every addition dilutes what's already there, so non-critical entries
actively reduce the system's value.

If there is something worth persisting, use the read mechanics above to see
what's already documented. Update existing files when they cover the topic.
Create new files only for genuinely new topics. You can use other tools — like
running git diff — to provide additional context on what to store.

Project-specific knowledge — decisions, conventions, architecture — typically
belongs in the project's `<name>-project/` folder. Other top-level folders hold
broader standards shared across projects. Route accordingly, but use judgement.

Do not persist things derivable from the code — CLI flags, function signatures,
file layouts. The code is the source of truth for those.

If what you are persisting is critical enough that the next agent must see it
every session (or on every subcommand), emit a single concise hint line after
your update — e.g.
`hint: consider adding <file> to on_start in .context-db.json`. Only suggest
this when the content is clearly load-bearing; real estate in those files
(especially on_all) is at a premium.

If you are unsure or want clarification, ask the user.

Do not run /context-db update yourself. The user invokes this. If you need to
write to context-db later, use the read mechanics and write-file-format above
directly.


# Always-Read Files

The files listed below are inlined into the agent's context automatically. Every line in them costs tokens on every invocation, so real estate is at a premium. Use strong judgement before writing to them — most learnings belong in a regular context-db file, not here. When in doubt, ask the user before adding anything.

These files are the `on_start` set — inlined once per session at start:
- `context-db/acme-payments-project/ON_START.md`

These files are the `on_all` set — inlined before every /context-db command (prompt, pre-review, review, update, maintain):
- `context-db/acme-payments-project/ON_ALL.md`

# On All

Ledger entries are immutable. Never edit a posted transaction — file a reversal
entry instead.


# Update User Instructions

Refunds must be filed as new entries, not edits
```

</details>

## Minimal — no on_start, no on_all {#minimal}

Empty globs for both always-loaded lists. `load-start-context` emits only the read mechanics and context-usage framing; no project-specific content is inlined.

**`.context-db.json`:**

```jsonc
{
  "defaults": {
    "mode": "main-agent"
  },
  "on_start": [],
  "on_all": []
}
```

### `/context-db load-start-context`

<details>
<summary>injected context</summary>

```

# Read Mechanics

`context-db/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 .claude/skills/context-db/scripts/context-db-resolve-path.py <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.


# Context Usage

Context-db is a starting point, a map, a hint — not a complete picture. It
documents conventions, gotchas, design decisions, and cross-file connections
that you can't learn from reading any single file.

Use it to orient yourself, then verify against the actual project assets (code,
configs, docs, etc.). If what you read conflicts with what the project shows,
trust the project's assets, especially project code.
```

</details>

### `/context-db prompt "How do I add a new payment endpoint?"`

<details>
<summary>injected context</summary>

```

# Read Mechanics

`context-db/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 .claude/skills/context-db/scripts/context-db-resolve-path.py <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.


# Context Usage

Context-db is a starting point, a map, a hint — not a complete picture. It
documents conventions, gotchas, design decisions, and cross-file connections
that you can't learn from reading any single file.

Use it to orient yourself, then verify against the actual project assets (code,
configs, docs, etc.). If what you read conflicts with what the project shows,
trust the project's assets, especially project code.


# Prompt Instructions

Navigate the project's context-db for context and standards directly relevant to
the user's request — things you would get wrong or miss without seeing them. Be
selective: use TOC descriptions to judge relevance, skip anything not directly
related, and don't read files just because they're nearby. Use what you find to
inform your response.

Do not run /context-db prompt yourself. The user invokes this. If you need more
context from context-db later, use the read mechanics above directly.


# Prompt User Instructions

How do I add a new payment endpoint?
```

</details>

## Per-subcommand supplement (`on_prompt`) {#on-prompt}

`on_prompt` carries content scoped to `/context-db prompt` only. Here it reuses the project's `ON_START.md` to demonstrate placement: the `on_prompt` block is inlined right after `on_all` and right before the user's instructions when `prompt` runs, but is absent when `update` runs.

**`.context-db.json`:**

```jsonc
{
  "defaults": {
    "mode": "main-agent"
  },
  "on_start": [],
  "on_all": [
    "*-project/ON_ALL.md"
  ],
  "on_prompt": [
    "*-project/ON_START.md"
  ]
}
```

### `/context-db prompt "How do I add a new payment endpoint?"`

<details>
<summary>injected context</summary>

```

# Read Mechanics

`context-db/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 .claude/skills/context-db/scripts/context-db-resolve-path.py <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.


# Context Usage

Context-db is a starting point, a map, a hint — not a complete picture. It
documents conventions, gotchas, design decisions, and cross-file connections
that you can't learn from reading any single file.

Use it to orient yourself, then verify against the actual project assets (code,
configs, docs, etc.). If what you read conflicts with what the project shows,
trust the project's assets, especially project code.


# Prompt Instructions

Navigate the project's context-db for context and standards directly relevant to
the user's request — things you would get wrong or miss without seeing them. Be
selective: use TOC descriptions to judge relevance, skip anything not directly
related, and don't read files just because they're nearby. Use what you find to
inform your response.

Do not run /context-db prompt yourself. The user invokes this. If you need more
context from context-db later, use the read mechanics above directly.


# On All

Ledger entries are immutable. Never edit a posted transaction — file a reversal
entry instead.


# On Start

Acme Payments is a three-tier payment service: API gateway, payment engine, and
an append-only ledger. Inter-service communication is async via message queue.

Before making changes:

- Architecture and API endpoints live under `acme-payments-project/`. Data-model
  conventions are in `acme-payments-project/data-model/`.
- Coding and git standards are shared with sister projects via symlinks
  (`coding-standards/`, `git-standards/`). Treat those as authoritative.
- The ledger is append-only — never write a path that mutates a posted
  transaction. Refunds and reversals are new entries, not edits.


# Prompt User Instructions

How do I add a new payment endpoint?
```

</details>

### `/context-db update "Refunds must be filed as new entries, not edits"`

<details>
<summary>injected context</summary>

```

# Write Mechanics

`context-db/` is this project's knowledge base. When writing the db, to
see which folders and files you can edit, use the TOC script with
--no-external-symlinks:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py --no-external-symlinks context-db/

This filters out symlinked folders from other repos. Only edit local files.

Drill into subfolders the same way — run the TOC script again on a subfolder to
see its contents, always with --no-external-symlinks.

### File format

Every `.md` file needs YAML frontmatter with a `description` field — this is the
routing decision agents use to decide whether to open the file. Be specific:
"scheduler execution flow, budget enforcement hook" not "Architecture overview."

Two types:

- Documents — frontmatter + body
- Folder descriptors — frontmatter only, named `<folder-name>.md`

Every subfolder needs a folder descriptor. The root `context-db/` does not.

Structure:

- 5-10 items per folder
- 50-150 lines per file, 200 max
- If a file exceeds 200 lines, split it into a subfolder with the same name

Status field (optional in frontmatter): `draft`, `stable` (default when
omitted), `deprecated`, `experiment`, `work-in-progress`, `refactor`.

After changes, run the TOC script to verify YAML frontmatter is correct:

python3 .claude/skills/context-db/scripts/context-db-generate-toc.py <sub-folder-that-was-altered>/


# Project Folder

This repo's project folder is `context-db/acme-payments-project/`. That is where knowledge specific to this project lives. Other top-level folders under `context-db/` are external — global standards, shared conventions, or folders symlinked in from other repos.

When writing or maintaining context-db, default to writing inside the project folder. Only edit a parallel folder when the content is genuinely not project-specific.

# Context Db Memory System

Context-db is the project's memory system. Do not use auto-memory, MEMORY.md, or
any vendor-specific persistence. Users will call the /context-db update skill
when they want to persist important project knowledge. If you think you should
save something to memory, ask the user if they want to run /context-db update
instead.


# Update Instructions

Think about your current session — corrections the user made, conventions you
learned, pitfalls you hit, decisions and why. Then decide: would the next agent
get something wrong or miss something without this knowledge? If not, tell the
user there's nothing to add.

Most sessions produce nothing worth storing — that is the normal outcome, not a
failure. Every addition dilutes what's already there, so non-critical entries
actively reduce the system's value.

If there is something worth persisting, use the read mechanics above to see
what's already documented. Update existing files when they cover the topic.
Create new files only for genuinely new topics. You can use other tools — like
running git diff — to provide additional context on what to store.

Project-specific knowledge — decisions, conventions, architecture — typically
belongs in the project's `<name>-project/` folder. Other top-level folders hold
broader standards shared across projects. Route accordingly, but use judgement.

Do not persist things derivable from the code — CLI flags, function signatures,
file layouts. The code is the source of truth for those.

If what you are persisting is critical enough that the next agent must see it
every session (or on every subcommand), emit a single concise hint line after
your update — e.g.
`hint: consider adding <file> to on_start in .context-db.json`. Only suggest
this when the content is clearly load-bearing; real estate in those files
(especially on_all) is at a premium.

If you are unsure or want clarification, ask the user.

Do not run /context-db update yourself. The user invokes this. If you need to
write to context-db later, use the read mechanics and write-file-format above
directly.


# Always-Read Files

The files listed below are inlined into the agent's context automatically. Every line in them costs tokens on every invocation, so real estate is at a premium. Use strong judgement before writing to them — most learnings belong in a regular context-db file, not here. When in doubt, ask the user before adding anything.

These files are the `on_all` set — inlined before every /context-db command (prompt, pre-review, review, update, maintain):
- `context-db/acme-payments-project/ON_ALL.md`

These files are the `on_prompt` set — inlined on every /context-db prompt:
- `context-db/acme-payments-project/ON_START.md`

# On All

Ledger entries are immutable. Never edit a posted transaction — file a reversal
entry instead.


# Update User Instructions

Refunds must be filed as new entries, not edits
```

</details>

