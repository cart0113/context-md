# Configuring Posture

`.context-db.json` lives at the repo root and controls how each sub-command runs
and what content gets inlined automatically. The default file ships with safe
values; edit it to tune the project's posture. The file is JSON with
`// line comments` allowed.

To see how each setting on this page changes the literal text the dispatcher
emits, see [Config Effects](../reference/config-effects.md) — it runs the
dispatcher under several preset configs against an example fixture and captures
the output, so the page can't drift from current behavior.

## Per-command settings

Each sub-command can override `mode` (`main-agent` / `sub-agent`), `model`
(`haiku` / `sonnet` / `opus`), and posture toggles. Unset keys fall back to
`defaults`.

```jsonc
{
  "defaults": { "mode": "main-agent", "model": "haiku" },

  "review": { "model": "sonnet" },
  "update": { "mode": "main-agent", "model": "sonnet" },
  "maintain": { "mode": "main-agent" },
}
```

`review`, `update`, and `maintain` benefit from a stronger model's reasoning.
Read commands like `prompt` and `pre-review` are well-served by `haiku` — the
navigation work doesn't need a large model and the cost delta is significant on
a busy project.

`update` and `maintain` are pinned to `main-agent` because they edit files in
the active working tree. Read commands are the natural place to experiment with
sub-agent mode — see [Sub-Agents](sub-agents.md).

## On-start and always-on content

Glob lists pull project files into the agent's context. Three tiers, ordered
from broadest scope to narrowest.

- `on_start` — fires once per session via the rule. Heavier orienting content is
  OK here; it loads once.
- `on_all` — fires at the end of every sub-command, right before the user's
  instructions. Recency wins: this content is the freshest thing in the agent's
  context when it acts. Keep it brief.
- `on_<command>` — fires only when that specific sub-command runs, right after
  `on_all`. One key per sub-command: `on_prompt`, `on_pre_review`, `on_review`,
  `on_update`, `on_maintain`. Use to surface rules that only matter for one
  operation, without bloating every other command.

```jsonc
{
  "on_start": ["*-project/ON_START.md"],
  "on_all": ["*-project/ON_ALL.md"],
  "on_prompt": ["*-project/PROMPT_NOTES.md"],
}
```

Globs are relative to `context-db/`. Folders expand recursively.

The dispatcher inlines matched files raw — frontmatter stripped, no preamble, no
path attribution, no headings added. Whatever the file contains is what the
agent sees. The author owns the framing.

### `ON_START.md` — orientation

Drop one of these into the project folder. It runs once per session and should
orient an agent walking in cold.

```markdown
# On Start

This repo ships the context-db tooling itself. Before making changes:

- The Python TOC script is the canonical way to inspect context-db. Don't invent
  a listing.
- Tests live under `tests/`. Run them after touching any prompt template or
  dispatcher logic.
- New prompt content goes under `templates/skills/context-db/scripts/prompts/`.
  Hardlinks propagate it into `.claude/...` automatically.
```

Reasonable length: 10–40 lines. Anything deeper belongs in regular context-db
files the agent fetches via the TOC.

### `ON_ALL.md` — every-call rules

The same mechanism, but fires on every sub-command. Reserve it for the rules an
agent keeps violating no matter how clearly they're stated elsewhere — the
equivalent of taping a sign to the monitor.

```markdown
# On All

Never edit `.claude/skills/context-db/scripts/...` directly — those are
hardlinks. Edit `templates/skills/context-db/scripts/...` instead.
```

The tradeoff is the obvious one. Every byte in `on_all` is a byte the agent
re-reads on every command. A 50-line `on_all` makes every `prompt` call 50 lines
more expensive. Reserve it for the rules where the cost of **not** having them
recently in context is higher than the cost of repeating them. Most projects
need somewhere between 0 and 10 lines.

### `on_<command>` — per-operation supplements

Same mechanism as `on_all`, but scoped to a single sub-command. The dispatcher
emits the matched content right after `on_all` and right before the user's
instructions when (and only when) that sub-command runs.

Use it when a rule only applies to one operation. The canonical case is layering
**local notes on top of a shared, read-only doc folder**:

```text
context-db/
├── mex-parser/                  ← symlinked from another repo, read-only
│   └── ...                      ← global mex-parser usage docs
└── acme-project/
    └── mex-parser/
        └── local-notes.md       ← what we've actually run into here
```

The shared `context-db/mex-parser/` folder ships from upstream and you can't
edit it. Discoveries specific to this project — gotchas, workarounds, version
pins — go into `acme-project/mex-parser/local-notes.md`. Wire that file into
`on_prompt` so the agent always sees the local supplement before answering a
question:

```jsonc
{
  "on_prompt": ["acme-project/mex-parser/local-notes.md"],
}
```

Now any `/context-db prompt` call inlines `local-notes.md` right before the
user's instruction, without forcing the same content onto `update` or `review`
calls that don't need it. As soon as the agent has touched the parser enough
times to learn the local quirks, those quirks are in front of it on every
question.

Other natural fits:

- `on_review` — review checklists or "things you keep missing" lists.
- `on_update` — house rules about where new context-db entries belong.
- `on_maintain` — invariants the audit pass should never violate.

Same cost discipline applies as `on_all`, but scoped: a 50-line `on_prompt` only
costs you on `prompt` calls, not on every command. The `on_<command>` lists
default to empty — opt in only when a rule genuinely needs to ride along on
every invocation of that operation.

## Reactive toggles

Two flags append a reminder to a sub-command's output instructing the agent
**not** to touch context-db on its own. They're how a project switches
context-db from "active participant" to "available on request."

- `remind-on-demand-read` — reminds the agent it should only read context-db
  when the user explicitly invokes a `/context-db` command.
- `remind-on-demand-update` — reminds the agent it should only write to
  context-db via explicit `/context-db update` or `/context-db maintain`.

```jsonc
{
  "defaults": {
    "remind-on-demand-read": true,
    "remind-on-demand-update": true,
  },
}
```

Both default to `false`. Set them in `defaults` to apply across all commands;
per-command overrides still work if you want, say, reactive lookups but normal
write behavior on `update` / `maintain`.

The naming is deliberate: these flags don't _enforce_ anything, they append
prompt reminders. `remind-` is honest about the mechanism.

The matching `load-manual remind-on-demand-read` and
`load-manual remind-on-demand-update` sections let the same reminders be loaded
mid-conversation if the agent starts drifting.

## Project-folder convention

The dispatcher detects `context-db/<name>-project/` folders by glob. Convention
is one such folder per repo, holding knowledge specific to the project. Other
top-level folders (e.g. `coding-standards/`, `writing-standards/`) are treated
as external — global standards or content symlinked from another repo.

`update` and `maintain` emit a reminder to the agent naming the detected project
folder, so writes default there rather than into the parallel external folders.
If multiple `*-project/` folders exist, the dispatcher surfaces all of them and
asks the agent to flag the anomaly.

The convention is enforced softly: the project folder's descriptor file
(`<name>-project/<name>-project.md`) should open its frontmatter description
with `Main project folder for this repo.` That marker is what read-side commands
pick up via TOC navigation. `/context-db maintain` ensures it stays in place.
