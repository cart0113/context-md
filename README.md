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

The install path shown above (`.claude/skills/context-db/`) is what Claude Code
expects. The scripts themselves are pure Python and run in any terminal —
Cursor, Codex, and other agents call the same dispatcher with their own wiring.

## Wiring it in

context-db works with any agent that has a project-level standing instruction
mechanism — Claude Code rules, Cursor rules, `AGENTS.md`, `.cursorrules`,
`copilot-instructions.md`. The pattern is universal:

> Tell the agent to run `context-db-main-agent.py load-on-start-context` at the
> start of every conversation, and follow what it prints.

That single delegation gives the agent the read-mechanics, the context-usage
framing, and every file matched by `on_start` / `on_all` globs in
`.context-db.json`.

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

## The context problem

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems.
Agents given context files that describe code state trust those descriptions,
read less actual code, and perform _worse_ when descriptions drift. Yet agents
left with no guidance default to their training and miss every project-specific
constraint.

The principle context-db follows: contain the gap between what the code shows
and what the agent needs to know. Conventions it wouldn't infer. Pitfalls it
will hit. Rationale not visible in source. Everything else is noise that
displaces code the agent could read instead.

The shipped instructions reinforce this directly. Context delivered through
context-db is framed as "a starting point, a map, a hint — not a complete
picture." Where context-db disagrees with the project's actual code, the agent
is told to trust the code.

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
