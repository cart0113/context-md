---
description:
  Working notes for agents modifying the context-db codebase itself —
  templates / install relationship, dispatcher as API surface, sub-agent
  status. For an overview of what context-db is, see the README.
---

# context-db (project notes)

This repo ships the context-db tooling. A few things worth knowing before
making changes.

- The dispatcher (`context-db-main-agent.py`) is the API surface. Subcommands
  print structured payloads that calling agents read and follow. Adding a
  subcommand means adding a prompt template under `scripts/prompts/` and a
  handler in the dispatcher.
- Templates live under `templates/skills/context-db/scripts/` and are
  hardlinked into `.claude/skills/context-db/scripts/`. Either side reflects
  the change; do not duplicate by hand.
- Sub-agent dispatch is functional but still being tuned. Defaults remain
  `main-agent` until the patterns stabilize.
- Tests live under `tests/`. Run them after touching prompt templates or
  dispatcher logic.

For everything else — what context-db is, the user-facing subcommand catalog,
config schema — see the README or the docs site under `docs/src/`.
