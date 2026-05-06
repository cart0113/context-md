# CLI reference

> [!note] Auto-generated. Do not edit by hand.
>
> This page is regenerated from the dispatcher's `--help` output and
> the prompt templates under
> `templates/skills/context-db/scripts/prompts/main-agent/` by
> `bin/build-cli-reference.py`. The pre-commit hook re-runs the
> script whenever the dispatcher or any prompt template changes.

For each subcommand, this page shows the literal `--help` output and
the verbatim instruction text the dispatcher emits to the agent at
run time. For the higher-level guide, see
[Commands](../guide/commands.md). For complete payloads under
different `.context-db.json` configs, see
[Config Effects](config-effects.md).

## Top-level

```text
usage: context-db [-h]
                  {load-manual,prompt,pre-review,review,update,read-all,read,load-start-context,maintain}
                  ...

Project knowledge base

positional arguments:
  {load-manual,prompt,pre-review,review,update,read-all,read,load-start-context,maintain}
    load-manual         Load a single instruction template
    prompt              Consult knowledge base
    pre-review          Check plan against standards before implementing
    review              Review changes against conventions
    update              File learnings into context-db
    read-all            Exhaustively read everything under a folder
    read                Inline full content of files/folders/globs
    load-start-context  Emit on-start context: on_start + on_all + read
                        mechanics/usage
    maintain            Audit and maintain context-db

optional arguments:
  -h, --help            show this help message and exit
```

## `/context-db load-start-context` {#load-start-context}

**CLI**

```text
usage: context-db load-start-context [-h] [--config CONFIG]

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG
```

## `/context-db prompt` {#prompt}

**CLI**

```text
usage: context-db prompt [-h] [--use-git-diff [N]]
                         [--mode {sub-agent,main-agent,ask}]
                         [--model {haiku,sonnet,opus,ask}] [--config CONFIG]
                         [--debug] [--load-start-context]
                         [instruction]

positional arguments:
  instruction

optional arguments:
  -h, --help            show this help message and exit
  --use-git-diff [N]    Use git diff to examine context-db changes to focus on
                        recently updated context. N=commits (default 3,
                        0=uncommitted only)
  --mode {sub-agent,main-agent,ask}
  --model {haiku,sonnet,opus,ask}
  --config CONFIG
  --debug
  --load-start-context  Also inline on_start content before the command output
                        (use for sub-agents that missed the session-start
                        load).
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
# Prompt Instructions

Navigate the project's context-db for context and standards directly relevant to
the user's request — things you would get wrong or miss without seeing them. Be
selective: use TOC descriptions to judge relevance, skip anything not directly
related, and don't read files just because they're nearby. Use what you find to
inform your response.

Do not run /context-db prompt yourself. The user invokes this. If you need more
context from context-db later, use the read mechanics above directly.
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/prompt.md`_

## `/context-db pre-review` {#pre-review}

**CLI**

```text
usage: context-db pre-review [-h] [--mode {sub-agent,main-agent,ask}]
                             [--model {haiku,sonnet,opus,ask}]
                             [--config CONFIG] [--debug]
                             [--load-start-context]
                             [instruction]

positional arguments:
  instruction

optional arguments:
  -h, --help            show this help message and exit
  --mode {sub-agent,main-agent,ask}
  --model {haiku,sonnet,opus,ask}
  --config CONFIG
  --debug
  --load-start-context  Also inline on_start content before the command output
                        (use for sub-agents that missed the session-start
                        load).
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
# Pre Review Instructions

You are about to start coding. Before you do, navigate context-db for standards,
conventions, and pitfalls that apply to your planned changes.

You already know your plan from the conversation. Look for:

- Coding standards (general and language-specific for what you're writing)
- Conventions and patterns used in this project
- Pitfalls, gotchas, things that break in non-obvious ways
- Files that must change together, ordering dependencies
- Design decisions that constrain your approach

Follow what you find when making your edits.

Do not run /context-db pre-review again yourself. The user invokes this. If you
need more context from context-db later, use the read mechanics above directly.
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/pre-review.md`_

## `/context-db review` {#review}

**CLI**

```text
usage: context-db review [-h] [--context-db-only-review]
                         [--mode {sub-agent,main-agent,ask}]
                         [--model {haiku,sonnet,opus,ask}] [--config CONFIG]
                         [--debug] [--load-start-context]
                         [instruction]

positional arguments:
  instruction

optional arguments:
  -h, --help            show this help message and exit
  --context-db-only-review
                        Only flag issues backed by context-db conventions
  --mode {sub-agent,main-agent,ask}
  --model {haiku,sonnet,opus,ask}
  --config CONFIG
  --debug
  --load-start-context  Also inline on_start content before the command output
                        (use for sub-agents that missed the session-start
                        load).
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
# Review Command Instructions

Review your recent changes against the project's context-db knowledge base.

1. Run git diff to see what changed
2. Navigate context-db for relevant conventions and standards
3. Compare your changes against what you find
4. Fix real issues, use your judgment on edge cases

Do not run /context-db review again yourself. The user will invoke it if needed.
If you need more context from context-db later, use the read mechanics above
directly. If you need to write to context-db:
`/context-db load-manual write-mechanics`
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/review.md`_

## `/context-db update` {#update}

**CLI**

```text
usage: context-db update [-h] [--commit] [--push]
                         [--mode {sub-agent,main-agent,ask}]
                         [--model {haiku,sonnet,opus,ask}] [--config CONFIG]
                         [--debug] [--load-start-context]
                         [instruction]

positional arguments:
  instruction

optional arguments:
  -h, --help            show this help message and exit
  --commit              Commit affected files after updating context-db
  --push                Push after committing (implies --commit)
  --mode {sub-agent,main-agent,ask}
  --model {haiku,sonnet,opus,ask}
  --config CONFIG
  --debug
  --load-start-context  Also inline on_start content before the command output
                        (use for sub-agents that missed the session-start
                        load).
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
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
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/update-general.md`_

## `/context-db maintain` {#maintain}

**CLI**

```text
usage: context-db maintain [-h] [--config CONFIG] [--load-start-context]
                           [path]

positional arguments:
  path

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG
  --load-start-context  Also inline on_start content before the command
                        output.
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
# Maintain Instructions

Target: {target_path}

Before starting, ask the user how they want to run this:

1. **Guided** — stop after each phase, wait for input
2. **Review** — run all phases, report findings, don't change without approval
3. **Autonomous** — run all phases, fix what's clear, summarize + ask on
   ambiguity

Wait for their answer before proceeding.

Phase 0 — Project folder convention: `{context_db_rel}/` should contain exactly
one `<name>-project/` folder for knowledge specific to this repo. Other
top-level folders are broader standards or symlinks shared across projects.

- If no project folder exists, ask the user whether to create one.
- If a project folder exists, open its descriptor at
  `<name>-project/<name>-project.md` and ensure the frontmatter `description`
  opens by marking the folder as the main project folder for this repo — e.g.
  `description: Main project folder for this repo. <one-line summary of what's inside>`.
  Read-side agents rely on this marker to weight the project folder above the
  parallel external folders, so do not skip it.
- If multiple `*-project/` folders exist, surface this to the user — the
  convention is one per repo.

Phase 1 — Structural health: 5-10 items per folder, 50-150 lines per file, 2-3
levels deep max. Split oversized files/folders, merge tiny ones, fill missing
folder descriptors, sharpen vague descriptions.

Phase 2 — Content freshness: Use git log and git diff. Verify referenced
files/functions still exist. Fix outdated content directly.

Phase 3 — Content value: Cut content that restates what's in the code — CLI
flags, function signatures, file layouts, property lists, step-by-step
instructions. But do not remove real knowledge (decisions, rationale, gotchas,
conventions) just because it could be shorter. If the detail would be lost, keep
it.

Phase 4 — Coverage gaps: Check recent git history for corrections, reverts,
pitfalls. Add only genuinely non-obvious entries.

Phase 5 — Documentation drift: Compare context-db against project docs. Where
they disagree, trust the project assets.

Phase 6 — Cross-references: All cross-reference paths must be file-relative
(`./foo.md`, `../bar/baz.md`). Convert any absolute or project-rooted paths
(`context-db/...`) to file-relative form. Verify `..`-style links resolve
correctly: `python3 {resolve} <containing-file> <link>`. Fix broken links. Add
new ones only where genuinely helpful.

Phase 7 — Reindex: Re-read every file, update all description fields to match
current content. Work bottom-up (deepest folders first). Run TOC on every
changed folder.

The default posture is to cut bloat — code summaries, derivable facts, stale
references. But an audit should leave context-db sharper, not just smaller.
Preserve details that carry real knowledge the next agent would miss.

Do not run /context-db maintain yourself. The user invokes this.
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/maintain-instructions.md`_

## `/context-db load-manual` {#load-manual}

**CLI**

```text
usage: context-db load-manual [-h] section

positional arguments:
  section     Section to load (see list below)

optional arguments:
  -h, --help  show this help message and exit

available sections:

  read-mechanics          How to navigate context-db via TOC script
  prompt                  Instructions for prompt command
  context-usage           Context-db is a map, not truth — verify against code
  write-mechanics         How to edit context-db files
  write-content-guide     What belongs in context-db
  persist-to-context-db   Use context-db, not auto-memory, for project knowledge
  pre-review              Check plan against standards before implementing
  review                  Review changes against conventions
  update-general          File learnings into context-db
  update-commit           How to write commit messages
```

## `/context-db read` {#read}

**CLI**

```text
usage: context-db read [-h] paths [paths ...]

positional arguments:
  paths       One or more paths or glob patterns

optional arguments:
  -h, --help  show this help message and exit
```

## `/context-db read-all` {#read-all}

**CLI**

```text
usage: context-db read-all [-h] [folder]

positional arguments:
  folder

optional arguments:
  -h, --help  show this help message and exit
```

**Canonical instruction text** — what the dispatcher
emits to the agent when this subcommand runs:

```markdown
# Read All

Read everything in `{target_path}` exhaustively — every file, every subfolder,
all the way down.

Use the TOC script to list each level:

    python3 {toc} {target_path}

For every file listed, read the whole file. For every subfolder listed, run the
TOC script on that subfolder and repeat — read all files, recurse into all
subfolders. Do not skip anything based on relevance; the goal is complete
coverage.
```

_Source: `templates/skills/context-db/scripts/prompts/main-agent/read-all.md`_

