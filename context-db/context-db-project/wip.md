---
description: Active work items. Update as items are completed or added.
---

# Work in Progress

## `general-standards/` special-case — docs/code disagree (2026-04-27)

User flagged: with `on_start`/`on_all` globs in place, the special-cased
always-read `general-standards/` folder may be redundant. Docs were updated to
drop it from folder-structure trees and remove the "always-loaded" prose
(`README.md`, `docs/src/overview/overview.md`,
`docs/src/reference/specification.md`). But the prompt templates still hard-code
it as MUST-read in five files:

- `templates/skills/context-db/scripts/prompts/main-agent/read-mechanics.md`
- `templates/skills/context-db/scripts/prompts/main-agent/read-all.md`
- `templates/skills/context-db/scripts/prompts/sub-agent/output-format.md`
- `templates/skills/context-db/scripts/prompts/sub-agent/prompt-sub-agent-role.md`

The folder still exists on disk at `context-db/general-standards/`. Decision
pending: either (a) fully retire the special case — strip it from prompt
templates and migrate the folder's contents to `on_start` globs, or (b)
re-document it as a still-supported special case. Do NOT silently "fix" one side
to match the other without checking with the user.

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
`/context-db load-on-start-context`. Rules survive compaction, require no
config. Two-tier always-load config (`on_start` + `on_all`) wires in
project-specific files that get inlined at session start (`on_start`) or on
every command (`on_all`). The 4 preset rule files (on-demand, reader,
contributor, autonomous) were dropped 2026-04-22 — workflow choice now belongs
in the project's `ON_START.md`, not in separate rules. See
`load-on-start-context-sub-command.md`.

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

## On-demand toggles added (2026-04-26)

`no-auto-update` and `no-auto-read` manual entries plus matching per-command
config flags in `.context-db.json` (default `false`). Lets users opt into a
fully-reactive posture where the agent only touches context-db when explicitly
invoked. The startup rule (`templates/rules/context-db.md`) carries the
no-auto-update guidance directly. See lessons-learned for rationale.
