---
description:
  What context-db is, why it exists, folder structure, how agents use it, the
  context problem (why less is more), and maintenance
---

# context-db

At its core, `context-db` works like an extended `AGENTS.md` or commonly used
startup rules to load context into an agent session so your instructions and
specifications are followed. However `context-db`:

- Organizes md files in a hierarchical b-tree using the file system so context
  can be efficiently loaded based on the task at hand: files and folders employ
  yaml frontmatter like a `SKILL.md` file and the system uses a script to build
  table of contents listings of every folder on demand. By convention, md file
  databases have 5-10 items per folder and ~150 lines of context per file. This
  way, the amount of context loaded scales with the task, not the total
  knowledge base.

- Leveraging the on demand table of contents generation and a few conventions,
  `context-db` was designed to symlink into other databases, allowing you to
  have common standards and procedures in global locations but easily
  integratable into your project's overall md file database.

- A single `/context-db` skill is provided with various subcommands available,
  most notably `/context-db prompt` and `/context-db update`. `prompt` allows
  you to reinforce important context on demand as agents often forget startup
  context during long sessions. `update` provides instructions so an agent
  updates the md file database with important information needed for future
  sessions using correct conventions and standards. Additional subcommands are
  also provided to perform code reviews against your md knowledge database and
  complete database maintenance which ensures the database is following
  necessary conventions and structure.

- A `<root>/.context-db.json` file provides the ability to customize how the
  system operates, allowing you to either provide more system knowledge on
  startup or use the tool more on-demand. Also, new features are being added to
  interact with the system using subagents, saving cost and providing
  independent code reviews against the md file database.

## Typical Folder Structure

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

By conventions, the `<project-name>-project/` folder holds project-specific
knowledge. Folders parallel to it (like `coding-standards/`) are
project-agnostic and often symlinked from a shared standards repo.

`ON_START.md` is inlined once per session at the top of the on-start payload;
`ON_ALL.md` is inlined right before the user's instructions on every command.
Both are optional.

## Wiring It In

The agent needs instructions on how to run the TOC script and navigate. This is
packaged as a **skill** (`.claude/skills/context-db/`). A **rule** and a
**SessionStart hook** ensure the skill loads every conversation.

Any mechanism that gets the SKILL.md content in front of the agent works:
`AGENTS.md`/`CLAUDE.md`, a rule with inline instructions, or just placing the
TOC script somewhere accessible and telling the agent about it.

## Private or Public

The TOC script runs dynamically — anything it finds at runtime appears in the
agent's navigation, whether committed, gitignored, or symlinked. Gitignored
symlinks can point anywhere. See
[cross-project-sharing.md](cross-project-sharing.md) for patterns.

## The Context Problem

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems. There
is [increasing discussion](https://arxiv.org/abs/2602.11988) about whether
`CLAUDE.md`, `AGENTS.md`, `.cursorrules` actually help. Agents given context
files that describe code state trust those descriptions, read less actual code,
and perform _worse_ when descriptions drift. Cost goes up, success rate goes
down.

Yet agents left with no guidance default to their training: generic patterns, no
awareness of project-specific constraints. The result is code that compiles but
doesn't match how the project works.

The principle: context-db contains the gap between what the code shows and what
the agent needs to know. Conventions it wouldn't infer. Pitfalls it will hit.
Rationale not visible in source. Everything else — code summaries, module
inventories — is noise that displaces code the agent could read instead.

The hierarchical structure helps too. A flat 5,000-line `CLAUDE.md` forces every
agent to read database rules when working on CSS. The B-tree means the context
cost is proportional to the task, not the total knowledge base.

## Maintenance

`/context-db maintain` runs a 7-phase audit: structural health, content
freshness, content value, coverage gaps, doc drift, cross-references, and
reindex. Default posture is to cut — leave context-db smaller and sharper.

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
