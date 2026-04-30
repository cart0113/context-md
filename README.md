# context-db

At its core, `context-db` works like an extended `AGENTS.md` or commonly-used
startup rules to load context into an agent session so your instructions and
specifications are followed. However `context-db` provides:

- **Logarithmic search**: md files are organized into hierarchical folders
  (b-tree) so finding relevant context is logarithmic (as opposed to a single
  file or a single linear TOC of context system). Files and folders use yaml
  frontmatter like a `SKILL.md` file and the system uses a script to dynamically
  build table of contents listings of every folder. By convention, md file
  databases have 5–10 items per folder and ~150 lines of context per file. This
  way, the amount of context loaded scales with the task, not the total
  knowledge base.

- **An update protocol that keeps the database fresh**: agents file what they
  learn back into the md file database — gotchas, decisions, conventions — using
  the project's own writing standards and folder-routing conventions, so updates
  respect the same frontmatter and structure rules as hand-written entries. A
  multi-phase maintenance pass trims dead content and fixes drift, so the
  database does not bloat into what it was built to avoid.

- **`/context-db` skill with subcommands**: a single `/context-db` skill exposes
  the system to the user. `/context-db prompt` re-injects context relevant to
  the next piece of work — agents drift from startup context on long sessions,
  and this puts them back on the rails. `/context-db update` files learnings via
  the protocol above. Additional subcommands run pre-flight checks against your
  standards (`pre-review`), audit a diff against them (`review`), and drive
  database maintenance (`maintain`).

- **Global and local context**: leveraging the on-demand TOC generation and a
  few conventions, `context-db` was designed to symlink into other databases,
  allowing common standards and procedures to live in global locations but
  integrate easily into a project's overall md file database.

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
project-agnostic and often symlinked from a shared standards repo.

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
[Config Effects](https://cart0113.github.io/context-db/#/reference/config-effects),
generated from the dispatcher itself so it can't drift from what the agent
actually receives. For the underlying schema, posture toggles, and per-command
overrides, see
[Configuring Posture](https://cart0113.github.io/context-db/#/guide/configuring-posture)
and [Commands](https://cart0113.github.io/context-db/#/guide/commands).

## The late-session forgetting problem

Anyone who has run an agent on a long task has seen the failure mode: session
starts well, the agent reads the standing instructions, follows them for the
first dozen turns, then drifts. The standards get compacted out of context. By
turn 40 the agent is back to its training defaults.

context-db fights this by making the standards explicitly re-loadable. The
`prompt` command pulls in just the context relevant to the next piece of work.
The `pre-review` command surfaces the standards that apply to a planned change
before code is written. The `review` command audits the diff against them after
the fact. Each is a deliberate moment where the user re-points the agent at the
project's conventions — without having to remember which standards apply or
where they live.

## Getting started

1. Copy `templates/skills/context-db/` into `.claude/skills/context-db/` (or
   symlink it).
2. Copy `templates/rules/context-db.md` into `.claude/rules/context-db.md`, or
   paste its body into `AGENTS.md` / `.cursor/rules/` / wherever your agent
   reads standing instructions.
3. Copy `templates/context-db-files/ON_START.md` and `ON_ALL.md` into
   `context-db/<project-name>-project/` and populate them.
4. Drop a `.context-db.json` at the repo root (the shipped one is a good
   starting point).

Full guide:
[Getting Started](https://cart0113.github.io/context-db/#/guide/getting-started).
For when context engineering helps, when it hurts, and the design choices that
keep context-db on the right side of that line, see
[Efficacy](https://cart0113.github.io/context-db/#/guide/efficacy).

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
