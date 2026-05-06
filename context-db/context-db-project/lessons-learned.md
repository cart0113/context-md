---
description:
  Lessons from building context delivery — late-session recall, pre-loading
  pitfalls, prompt engineering for cheap models, relative paths, rules vs hooks
  for on-start context. Applies to the unified /context-db skill.
---

# Lessons Learned

## Late-session recall problem

Context loaded at session start gets compressed away after 15-20 turns. By turn
40, the agent has lost standards. Re-instructing on every call avoids this.

## Pre-loading all files breaks the B-tree

Stuffing every `.md` file into the prompt fails: Python can't judge relevance
(that's a language task), doesn't scale, and bypasses description-based routing.
Let the agent navigate the hierarchy.

## Cheap models need structured output constraints

Haiku ignores "do NOT help with the task" — it treats the user's prompt as its
own task. Fix: structured output format ("respond with ONLY verbatim snippets")
and framing the prompt as data in the system prompt (`# Main Prompt`).

## Positive-first role framing for sub-agents

Leading with DO NOT constraints ("You do NOT perform tasks, do NOT write code,
do NOT run git") made haiku refuse to navigate entirely — it concluded it
couldn't help and returned nothing useful. The fix: lead with the positive job
description ("Your job is to find all relevant context from context-db"), then
add constraints after. The model needs to know what it SHOULD do before hearing
what it shouldn't.

## Combined role blocks work, scattered constraints don't

Splitting identity, task description, and navigation constraints across separate
tagged blocks caused coherence issues — the model lost the connection between
"what I am" and "what I'm supposed to do." One combined `# Sub Agent Role`
section per command, containing identity + task + constraints, keeps the
sub-agent on track. Per-command variants are needed because "what to find"
differs (prompt: applicable context, pre-review: applicable standards, review:
convention violations).

## Mandatory rules go last, not first

Recency wins. Rules placed at the top of a composed prompt get diluted by
everything after; rules placed just before the user's instructions stay freshest
when the model acts. `on_all` content is emitted at the end of each command's
output (before the user-instructions block), not prepended. The tool also adds
no framing — file authors own their own preamble.

## Content-first ordering matters

Prompt before navigation instructions produces better results. The model reads
what it needs context for, then navigates with that filter in mind.

For sub-agents, this means injecting the developer's prompt into the system
prompt as a labeled data block (`# Main Prompt`) before the role instructions.
The role then references it: "find context for the `# Main Prompt` above." This
frames the prompt as a search query — the model sees what to look up before
being told how. Without this, cheap models treat the prompt as a task and
execute it (e.g. running `git commit` when the prompt says "Commit").

## Review sub-agents need different constraints than lookup sub-agents

Prompt and pre-review sub-agents are pure knowledge lookups — lock them to TOC
script + Read only. Review sub-agents need to read source files, run git diff,
and potentially grep for patterns. Only ban destructive commands (git add,
commit, push, reset). Over-constraining review breaks it; under-constraining
lookup lets haiku run wild.

## Self-review catches real bugs

Running the review sub-agent against its own changes (with sonnet) caught an
IndexError bug where the `# Main Prompt` injection split failed when the role
template was the first in the composition. Sonnet is the right model for review
— haiku lacks the reasoning depth to compare code against conventions.

## Rules for behavior, config for execution

Rules (`.claude/rules/`) survive compaction — they're system prompt, re-injected
every turn. Hook output lives in conversation and gets compacted away. Startup
instructions belong in rules, not hooks.

The clean separation: the single rule (`rules/context-db.md`) tells the agent to
run `/context-db load-start-context` on session start. Config
(`.context-db.json`) controls HOW commands execute (sub-agent vs main-agent,
which model) and WHICH project files are always-loaded (`on_start`, `on_all`).
Workflow choice (reader vs contributor vs autonomous) lives in the project's
`ON_START.md`, not in separate rule presets.

## Constrain navigation to TOC + Read only

Without constraints, haiku adds `find`, `ls -la`, `head -50` that waste turns.
"Do not use find, grep, or ls" produces clean 2-3 step navigation.

## All paths must be relative to cwd

Absolute paths and symlink resolution cause double-reads (wrong path, then
self-correction). All paths relative to cwd: TOC script is
`.claude/skills/.../context-db-generate-toc.py`, context-db is `context-db/`.

## Feed standards before agents start, not at session start

Standards loaded at session start fade. Pre-review mode forces the agent to
fetch standards _immediately before starting edits_ — a structural fix.

## Do not anthropomorphize in prompts

Frame sub-agent responses as "additional context" — not advice from a junior to
a senior. The goal is to inform, not establish hierarchy.

## H1 markdown headers work as well as custom bracket tags

No performance difference between `[tag-name]...[end tag-name]` and `# Tag Name`
for section delimitation. LLMs are trained extensively on markdown — H1 headers
are among the most common structural tokens in training data. H1 headers are
more human-readable, need no closing tag, and use standard formatting. One H1
per template file; sub-sections use H2/H3.

## Self-reference guard

Without scope filtering, the subagent returns information about context-db
itself when asked about a project that uses context-db. Constrain to information
found in the knowledge base, not about the knowledge base system.

## Project-folder convention: marker in frontmatter, not in read prompts

context-db follows a one-`<name>-project/`-per-repo convention. Other top-level
folders are external (global standards, symlinked shared content). The
dispatcher detects this via `find_project_folders()` and emits a
`# Project Folder` section on WRITE commands (update, maintain) naming the
folder so the agent defaults to writing there. READ commands (prompt,
pre-review, review) get no prompt-level reinforcement — instead, the maintain
workflow ensures the project folder's descriptor frontmatter opens with "Main
project folder for this repo." Read-side agents pick up the role distinction via
TOC navigation (frontmatter is re-read every nav, no late-session decay).

Why not reinforce on reads too: writes have direction (focus is helpful); reads
want recall (focus actively hurts — narrowing attention biases the agent away
from globally-applicable context). The asymmetry is intentional. Maintain's
frontmatter enforcement is the load-bearing piece that makes "let frontmatter do
the talking" actually work for reads.

## Retire specialized primitives once a flexible one subsumes them

The `on_<command>` tier (per-subcommand always-on globs) made the
`remind-on-demand-read` / `remind-on-demand-update` flags redundant: any "don't
touch context-db unless invoked" reminder a project wants is just a one-line
markdown file wired into `on_all` or the relevant `on_<command>`. Keeping both
meant two flags, two prompt templates, four if-blocks across the dispatcher's
handlers, three doc sections, and a config-effects scenario — all to deliver
text the user can author directly.

The lesson: when a more flexible primitive subsumes a specialized one, delete
the specialized one. Two ways to do the same thing is worse than one — every
extra surface is config to remember, docs to maintain, code to keep working, and
a decision the user has to make at adoption. The flexible primitive also lets
users tune the wording, scope it per-command, or skip it entirely; the
specialized flag could only emit one fixed string.
