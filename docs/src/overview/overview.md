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

## How it works

Every folder under `context-db/` has a `<folder-name>.md` descriptor file with a
YAML `description` frontmatter field. Every content file has the same field. A
small Python script (`context-db-generate-toc.py`) walks any folder and prints a
table of contents with each entry's description.

The agent navigates the way it would any well-organized filesystem: read the
TOC, follow descriptions that match the task, drill into subfolders the same
way. Everything else is skipped. With ~5–10 items per folder and ~100 lines per
file, the amount read is proportional to the task, not the total knowledge base.

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
Folders parallel to it are project-agnostic — usually symlinked from a shared
standards repo so multiple projects pull from the same source. See
[Cross-Project Sharing](../guide/cross-project-sharing.md).

`ON_START.md` is inlined once per session at the top of the on-start payload;
`ON_ALL.md` is inlined right before the user's instructions on every command.
Both are optional. See [Configuring Posture](../guide/configuring-posture.md).

`general-standards/` is special-cased: the agent reads every file in it before
any task, the way it would read a `CLAUDE.md`. Use it for standards that apply
universally — agent behavior, coding rules, language conventions.

The install path shown above (`.claude/skills/context-db/`) is what Claude Code
expects. The scripts themselves are pure Python and run in any terminal —
Cursor, Codex, and other agents call the same dispatcher with their own wiring.
See [Getting Started](../guide/getting-started.md).

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
per-command mode, model, and the `no-auto-read` / `no-auto-update` toggles that
switch the posture.

## The context problem

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems. There
is [increasing discussion](https://arxiv.org/abs/2602.11988) about whether
`CLAUDE.md`, `AGENTS.md`, and `.cursorrules` actually help performance. Agents
given context files that describe code state trust those descriptions, read less
actual code, and perform _worse_ when descriptions drift. Cost goes up, success
rate goes down.

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
