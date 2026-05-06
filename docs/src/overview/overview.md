# context-db

`context-db` is a project-knowledge layer for coding agents. The starting
picture is `AGENTS.md` or `CLAUDE.md` — a project's standing instructions for
the agent — but hierarchical instead of monolithic, re-loadable on demand
instead of only at session start, and bounded by a maintenance pass that keeps
it from bloating into what it was built to avoid. The four ideas:

- **Hierarchical Markdown, navigated on demand.** Every file and folder carries
  YAML `description` frontmatter (the same shape as a `SKILL.md`). A small
  Python script renders the table of contents for any folder at call time, so
  the agent walks a B-tree of descriptions and reads only the leaves it needs.
  By convention, 5–10 items per folder and ~150 lines per file: context loaded
  scales with the task, not with the size of the database.

- **Re-injection at decision points, not only at startup.** Standards loaded
  once at session start compact out of the agent's context on long sessions; by
  turn 40 the agent has drifted back to its training defaults.
  `/context-db prompt` re-fetches just the slice relevant to the next step.
  `/context-db pre-review` surfaces the standards a planned change has to clear
  before code is written. `/context-db review` audits the diff against them
  after the fact. Each is a deliberate moment where the user re-points the agent
  at the project's conventions, without having to remember which standards apply
  or where they live.

- **A bounded write loop.** `/context-db update` files what the agent learned —
  gotchas, decisions, conventions — using the same frontmatter and folder
  routing as hand-written entries, so the protocol that produces the database is
  the same one that grows it. `/context-db maintain` runs a multi-phase audit
  whose default posture is to **cut**: trim dead content, prune redundant
  entries, fix drift, reindex. Updates and maintenance balance each other so the
  database stays useful without bloating.

- **Global and local knowledge in one tree.** Symlink folders from a personal or
  team standards repo and they appear in the TOC alongside project-local content
  — coding standards, writing conventions, library runbooks, written once and
  used from every project. Per-subcommand `on_<command>` lists let
  project-specific notes layer on top of those shared, read-only docs without
  forking them.

## Typical folder structure

```
your-project/
├── .claude/
│   ├── rules/context-db.md                ← load the skill every conversation
│   └── skills/
│       └── context-db/                    ← unified skill: all commands + scripts
│           ├── SKILL.md
│           └── scripts/
│               ├── context-db-generate-toc.py
│               ├── context-db-main-agent.py
│               └── context-db-sub-agent.py
├── .context-db.json                       ← per-command mode/model/posture
└── context-db/
    ├── <project-name>-project/            ← project-specific knowledge
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── ON_START.md                    ← orientation, inlined once per session
    │   ├── ON_ALL.md                      ← brief rules, inlined every command
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

By convention, the `<project-name>-project/` folder holds project-specific
knowledge. Folders parallel to it (like `coding-standards/`) are
project-agnostic and often symlinked from a shared standards repo — see
[Cross-Project Sharing](../guide/cross-project-sharing.md).

## Wiring it in

context-db works with any agent that has a project-level standing instruction
mechanism — Claude Code rules, Cursor rules, `AGENTS.md`, `.cursorrules`,
`copilot-instructions.md`. The pattern is universal:

> Tell the agent to run `/context-db load-start-context` at the start of every
> conversation, and follow what it prints.

That single delegation gives the agent the read mechanics, the context-usage
framing, and every file matched by `on_start` / `on_all` globs in
`.context-db.json`. The five subcommands — `prompt`, `pre-review`, `review`,
`update`, `maintain` — handle context re-injection, plan checks, diff audits,
filing learnings, and database upkeep respectively.

The exact text each subcommand injects into the agent's context is shown in
[Config Effects](../reference/config-effects.md), generated from the dispatcher
itself so it can't drift from what the agent actually receives. For the
underlying schema, posture toggles, and per-command overrides, see
[Configuring Posture](../guide/configuring-posture.md) and
[Commands](../guide/commands.md). For the rule body and per-agent install, see
[Rules](../guide/rules.md) and [Getting Started](../guide/getting-started.md).

## Why this design

Context files are often a net negative for coding agents.
[ETH Zurich research](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found LLM-generated context files reduced task success by ~3% and increased cost
by 20%+; even hand-written ones showed only marginal gains. Agents trust the
file, read less of the actual code, and amplify any drift between description
and reality. Separately,
[Chroma's context-rot study](https://www.trychroma.com/research/context-rot)
showed every frontier model performs worse as input length grows, well below
context limits — so even correct context degrades the agent when there is too
much of it.

context-db's design follows from those two findings. Hierarchical Markdown plus
an on-demand TOC keeps the loaded slice small. Re-injection commands keep that
slice _fresh_ as the session grows. The `maintain` audit cuts content that no
longer earns its tokens. The litmus test for every entry: if you removed it,
would the agent make a mistake it wouldn't otherwise make? Anything that doesn't
clear that bar is, by the ETH Zurich finding, a _negative_-value document.

For the full treatment — including the negative result that motivated the
project — see [Efficacy](../guide/efficacy.md).

## Where to next

- [Getting Started](../guide/getting-started.md) — install paths for Claude
  Code, Cursor, Codex/`AGENTS.md`, and Copilot.
- [Commands](../guide/commands.md) — the sub-command catalog: `prompt`,
  `pre-review`, `review`, `update`, `maintain`.
- [Configuring Posture](../guide/configuring-posture.md) — `.context-db.json`,
  `on_start` / `on_all` / per-subcommand globs.
- [Reference](../reference/specification.md) — format specification, CLI, and
  the literal text the dispatcher emits under different configs.
