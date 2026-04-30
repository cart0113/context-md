---
description:
  Two docs pages are generated from real dispatcher output and prompt templates
  so they cannot drift from the agent-facing surface. The rule and the fixture
  coupling that supports it.
---

# Auto-generated docs pages

## The rule

When a doc would duplicate canonical agent-facing text — the literal payload the
dispatcher emits, the literal prompt-template body the agent reads, or the
literal `--help` of the CLI — generate the doc, do not paraphrase it.
Paraphrases drift; the generated docs are the project's evidence that they have
not.

## What is generated today

| Page                                   | Generator                          | Source                                                                                     |
| -------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------ |
| `docs/src/reference/config-effects.md` | `bin/build-config-effects-docs.py` | dispatcher run against `example/acme-payments-repo/` under preset `.context-db.json`s      |
| `docs/src/reference/cli.md`            | `bin/build-cli-reference.py`       | dispatcher `--help` plus prompt templates under `templates/skills/.../prompts/main-agent/` |

Both pages start with a `> [!note] Auto-generated. Do not edit by hand.` banner.
Edits go to the generator script and / or the source files; the page is
overwritten on next run.

## Pre-commit hook

`hooks/pre-commit` regenerates each page when its inputs change:

- Section 5 — `config-effects.md` re-runs when the dispatcher, prompt templates,
  the example fixture, or `bin/build-config-effects-docs.py` changes.
- Section 6 — `cli.md` re-runs when the dispatcher, prompt templates, or
  `bin/build-cli-reference.py` changes.

Both generators are idempotent — the regex sanity test in the hook should catch
trigger drift before generators stop firing.

## Fixture coupling

`example/acme-payments-repo/` is both a runnable reference layout for users
**and** the fixture the config-effects generator runs against. Moving, renaming,
or restructuring it breaks the generator. Four assumptions the generator
currently encodes:

- The repo lives at `example/acme-payments-repo/`.
- The dispatcher is reachable at
  `example/acme-payments-repo/.claude/skills/context-db/scripts/context-db-main-agent.py`
  (currently a symlink chain back to `templates/skills/...`).
- The project folder name matches `*-project/`.
- `ON_START.md` and `ON_ALL.md` exist inside that project folder so the
  default-config scenario produces a non-trivial payload.

If any of those change, update `bin/build-config-effects-docs.py` in the same
commit. The pre-commit hook will fail otherwise.

## When NOT to auto-generate

If a page is genuinely user-intent material (worked examples, "what would I use
this for", per-agent invocation), it stays hand-written. The generator pattern
only applies where the doc is a window onto something the agent already reads at
runtime.
