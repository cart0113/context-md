# context-db

Project knowledge for AI coding agents — organized as hierarchical Markdown so
the agent can fetch only what it needs, and re-fetch it whenever a long session
has dulled its memory.

context-db is essentially an augmented `AGENTS.md`. The same problem (give the
agent project-specific knowledge it can't infer from code), with a different
shape (a B-tree of small files, navigable on demand) and a tooling layer that
makes the knowledge re-loadable mid-session.

## Why context-db

- **Hierarchical.** Filesystem as a B-tree. Agents read frontmatter descriptions
  at each level and branch into what's relevant, skipping everything else.
- **Logarithmic cost.** 5–10 items per folder, ~100 lines per file. The amount
  read scales with the task, not the total knowledge base.
- **Re-loadable.** Standing instructions fade over a long session. context-db
  exposes a `prompt` command the user can invoke whenever the agent needs to be
  re-pointed at the relevant project knowledge.
- **Configurable posture.** A small `.context-db.json` controls which model runs
  each command, whether the agent is allowed to read or write context-db on its
  own initiative, and which files are inlined every session or every command.
- **Minimal by enforcement.** The shipped instructions tell the agent to
  document only what code can't reveal — conventions, pitfalls, rationale. The
  `maintain` command actively prunes content that drifts.

## Folder structure

```
your-project/
├── .claude/
│   ├── rules/context-db.md                ← standing rule loaded every session
│   └── skills/context-db/                 ← unified skill: dispatcher + scripts
│       ├── SKILL.md
│       └── scripts/
│           ├── context-db-generate-toc.py
│           ├── context-db-main-agent.py
│           └── context-db-sub-agent.py
├── .context-db.json                       ← per-command mode/model/posture
└── context-db/
    ├── <project-name>-project/            ← knowledge specific to this repo
    │   ├── <project-name>-project.md      ← folder descriptor (frontmatter only)
    │   ├── ON_START.md                    ← orientation, inlined once per session
    │   ├── ON_ALL.md                      ← brief rules, inlined every command
    │   └── architecture.md                ← topic file (frontmatter + body)
    ├── general-standards/                 ← always loaded (like a CLAUDE.md)
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

The `<project-name>-project/` folder holds knowledge specific to this repo.
Folders parallel to it are project-agnostic and often symlinked from a shared
standards repo so multiple projects pull from the same source.

`ON_START.md` is inlined once per session at the top of the on-start payload;
`ON_ALL.md` is inlined right before the user's instructions on every command.
Both are optional.

`general-standards/` is special-cased: the agent reads every file in it before
any task, the way it would read a `CLAUDE.md`.

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
