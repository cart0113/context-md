---
description:
  load-manual subcommand — loads a single instruction template by name. Used
  mid-conversation when the agent needs to refresh on a specific topic.
---

## What it does

`load-manual <section>` prints one prompt template. No compositing, no config.
Used when the agent needs instructions for a specific capability
mid-conversation (e.g., "how do I write to context-db?").

## Usage

    /context-db load-manual <section>

Run `--help` to see available sections with descriptions.

## Available sections

- `read-mechanics` — how to navigate context-db via TOC script
- `prompt` — instructions for prompt command
- `context-usage` — context-db is a map, not truth
- `write-mechanics` — how to edit context-db files
- `write-content-guide` — what belongs in context-db
- `persist-to-context-db` — use context-db, not auto-memory
- `pre-review` — check plan against standards before implementing
- `review` — review changes against conventions
- `update-general` — file learnings into context-db
- `update-commit` — how to write commit messages

## Design rationale

On-start instructions are delivered via a single rule file
(`templates/rules/context-db.md`) that users copy or symlink to
`.claude/rules/context-db.md`. The rule just tells the agent to run
`/context-db load-on-start-context`. Rules survive compaction and require no
hook or config. `load-manual` is the mid-conversation escape hatch for loading
individual instruction sections on demand.

Distinct from two sibling subcommands:

- `load-on-start-context` inlines the project's always-load content (see
  `load-on-start-context-sub-command.md`). That's about project-specific bytes.
- `read` inlines arbitrary file/folder content by path or glob. That's a generic
  content-delivery primitive.

`load-manual` is neither — it loads skill-internal instruction templates (how
the agent should behave), not project content.
