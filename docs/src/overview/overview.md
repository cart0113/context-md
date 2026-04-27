# context-db

At its core, `context-db` works like an extended `AGENTS.md` or commonly used
startup rules to load context into an agent session so your instructions and
specifications are followed. However `context-db`:

- Organizes md files in a hierarchical b-tree using the file system so context
  can be efficiently loaded based on the task at hand: files and folders employ
  yaml frontmatter like a `SKILL.md` file and the system uses a script to
  dynamically build table of contents listings of every folder. By convention,
  md file databases have 5-10 items per folder and ~150 lines of context per
  file. This way, the amount of context loaded scales with the task, not the
  total knowledge base.

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
project-agnostic and often symlinked from a shared standards repo. See
[Cross-Project Sharing](../guide/cross-project-sharing.md).

`ON_START.md` is inlined once per session at the top of the on-start payload;
`ON_ALL.md` is inlined right before the user's instructions on every command.
Both are optional. See [Configuring Posture](../guide/configuring-posture.md).

## The late-session forgetting problem

Anyone who has run an agent on a long task has seen the failure mode: session
starts well, the agent reads the standing instructions, follows them for the
first dozen turns, then quietly drifts. The standards get compacted out of
context. By turn 40 the agent is back to its training defaults.

context-db fights this by making the standards explicitly re-loadable. The
`prompt` command pulls in just the context relevant to the next piece of work.
The `pre-review` command surfaces the standards that apply to a planned change
before code is written. The `review` command audits the diff against them after
the fact. Each is a deliberate moment where the user re-points the agent at the
project's conventions — without having to remember which standards apply or
where they live.

The standing rule (loaded every conversation turn) is what tells the agent these
commands exist. Standing rules survive compaction; chat history does not.

## Tailoring posture

context-db is configurable enough to fit a range of working styles. Two
extremes:

- **Hands-off.** The agent loads context-db at session start, navigates it on
  its own when it judges the work would benefit, and updates it when it learns
  something. Suits solo work where the agent is trusted to decide.
- **Reactive.** The agent treats context-db as available-on-request. It only
  reads or writes when the user explicitly invokes a command. Suits team work,
  code review, and any setting where determinism matters more than agent
  initiative.

Both come from the same machinery: a single `.context-db.json` file controls
per-command mode, model, and the `remind-on-demand-read` /
`remind-on-demand-update` toggles that switch the posture.

## The context problem

Context files are both the cause of, and solution to, many agent problems. There
is [increasing discussion](https://arxiv.org/abs/2602.11988) about whether
`CLAUDE.md`, `AGENTS.md`, and `.cursorrules` actually help performance. Agents
given context files that describe code state trust those descriptions, read less
actual code, and perform _worse_ when descriptions drift. Cost goes up, success
rate goes down. See [Efficacy](../guide/efficacy.md) for the experiments and the
trade-off in detail.

Yet agents left with no guidance default to their training: generic patterns, no
awareness of project-specific constraints. The result is code that compiles but
doesn't match how the project works.

The principle context-db follows: contain the gap between what the code shows
and what the agent needs to know. Conventions it wouldn't infer. Pitfalls it
will hit. Rationale not visible in source. Everything else — code summaries,
module inventories, restated function signatures — is noise that displaces code
the agent could read instead.

The shipped instructions reinforce this directly. Context delivered through
context-db is framed to the agent as "a starting point, a map, a hint — not a
complete picture." Where context-db disagrees with the project's actual code,
the agent is told to trust the code.

## Maintenance

`/context-db maintain` runs a seven-phase audit: structural health, content
freshness, content value, coverage gaps, doc drift, cross-references, and
reindex. Default posture is to **cut** — leave context-db smaller and sharper.
Without regular maintenance, any knowledge base drifts toward the bloated state
it was designed to avoid.

## Sub-agents

A second mode (still being tuned) hands navigation work to a cheap model spawned
as a sub-agent, freeing the main conversation agent to act on the curated
result. See [Sub-Agents](../guide/sub-agents.md).

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
