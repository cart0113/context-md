---
description: Active work items. Update as items are completed or added.
---

# Work in Progress

## Sub-agent system overhaul — in progress

Sub-agent architecture rebuilt with composable templates. Three template
directories: `main-agent/` (core, reused), `sub-agent/` (role + constraints),
`spawn/` (dispatch instructions). Config `rerun-init` flag replaces old
`response-*.md` remind templates.

Done:

- Per-command instruction files: `prompt-sub-agent-role.md`,
  `pre-review-instructions.md`, `review-instructions.md`,
  `review-instructions-context-db-only.md`
- `# Main Prompt` / `# User Guidance` — conditional injection when user provides
  a prompt, with `{user_guidance_note}` template variable for instructions to
  heed it
- Response wrapping: prefix (`# Context Usage`) + findings + suffix
  (`# Interpreting * Response`)
- Spawn templates for all three commands
- Pre-review: main-agent mode needs no prompt (agent knows plan from
  conversation). Sub-agent mode: spawn template walks agent through writing a
  detailed plan.
- Review: full review is default, `--context-db-only-review` for rare case

Remaining:

- Clean up deprecated files (`role.md`, `role-review.md`, `role-pre-review.md`,
  `navigation-constraints.md`, `output-format.md`, `output-format-review.md`,
  `output-format-review-full.md`, `output-context-db-review.md`,
  `output-general-review.md`)
- Test pre-review with haiku
- Delete `old-prompts/` once all commands are verified

## On-start context delivery — resolved

Replaced hook-based `load-manual` compositing with a single rule file
(`templates/rules/context-db.md`) that tells the agent to run
`/context-db load-start-context`. Rules survive compaction, require no config.
Two-tier always-load config (`on_start` + `on_all`) wires in project-specific
files that get inlined at session start (`on_start`) or on every command
(`on_all`). The 4 preset rule files (on-demand, reader, contributor, autonomous)
were dropped 2026-04-22 — workflow choice now belongs in the project's
`ON_START.md`, not in separate rules. See `load-start-context-sub-command.md`.

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.

## Project-folder convention enforced (2026-04-26)

Dispatcher detects `context-db/*-project/` and emits a `# Project Folder`
section in update + maintain output naming the folder. Maintain Phase 0 now
ensures the project folder descriptor frontmatter opens with "Main project
folder for this repo." Read-side agents pick up the priority signal via TOC
navigation rather than prompt-level reinforcement. See lessons-learned for the
read/write asymmetry rationale.

## Per-subcommand on\_<command> tier added; reminder system removed (2026-05-06)

Extended `on_start` / `on_all` with `on_prompt`, `on_pre_review`, `on_review`,
`on_update`, `on_maintain` — each fires only when its subcommand runs, inlined
right after `on_all`. Same day, deleted the `remind-on-demand-read` /
`remind-on-demand-update` flags and their two prompt templates. The
`on_<command>` mechanism subsumes the use case: a project that wants the agent
to stay hands-off can drop a one-line "do not touch context-db unless invoked"
supplement into `on_all` (or any `on_<command>`) and get the same recency-driven
reminder without a dedicated flag, manual entry, or template. Two flags + two
templates + four if-blocks gone. See lessons-learned for the surface-area
rationale.
