# Getting Started

## 1. Create your context-db

Create a `context-db/` directory with a `<project-name>-project/` subfolder. Add
a descriptor file — frontmatter only, no body:

```
context-db/
└── acme-payments-project/
    └── acme-payments-project.md
```

```yaml
---
description:
  Main project folder for this repo. Acme Payments — architecture, APIs, data
  model.
---
```

The `Main project folder for this repo.` opening is a soft convention the
dispatcher and `maintain` command rely on. The body of the descriptor file stays
empty; topic content goes in sibling files.

Add context documents alongside it. Each gets its own `description` frontmatter
and a Markdown body. Keep folders to 5–10 items — split into subfolders when one
grows beyond that.

## 2. Install the dispatcher

The dispatcher is a Python script. The canonical location is inside a Claude
Code skill folder:

```bash
cp -r templates/skills/context-db your-project/.claude/skills/context-db
```

The same scripts run unchanged from any path. Non-Claude users can put them
anywhere and reference that path from their rule body. There's nothing
Claude-specific about the script itself — it's a Python file that reads
context-db markdown and prints text.

Drop the project-level config:

```bash
cp .context-db.json your-project/.context-db.json
```

Edit per-command mode/model/posture as needed. See
[Configuring Posture](configuring-posture.md).

## 3. Install `ON_START.md` and `ON_ALL.md` (optional)

Drop the boilerplate into the project folder and edit:

```bash
cp templates/context-db-files/ON_START.md \
   your-project/context-db/<project-name>-project/ON_START.md
cp templates/context-db-files/ON_ALL.md \
   your-project/context-db/<project-name>-project/ON_ALL.md
```

These are the always-loaded content files. Use `ON_START.md` for orientation an
agent needs once per session. Use `ON_ALL.md` for the handful of rules that must
be re-pinned in front of every command. See
[Configuring Posture](configuring-posture.md).

## 4. Wire up the rule

Tell the agent to load context-db on session start. Each agent has its own rule
mechanism — pick the section that matches yours. The body to install is the same
in all cases (see [Rules](rules.md)).

### Claude Code

```bash
cp templates/rules/context-db.md your-project/.claude/rules/context-db.md
```

Rules in `.claude/rules/` load on every conversation turn and survive context
compaction.

### Cursor

Newer projects use `.cursor/rules/context-db.md` — same format. Older projects
use a single `.cursorrules` at the repo root. Either works:

```bash
cp templates/rules/context-db.md your-project/.cursor/rules/context-db.md
# or
cat templates/rules/context-db.md >> your-project/.cursorrules
```

If the path to the dispatcher script differs in your project, edit the rule body
to match.

### Codex / generic `AGENTS.md`

The cross-agent convention is a top-level `AGENTS.md`. Append the rule body
under a `## context-db` heading:

```bash
{
  echo
  echo "## context-db"
  cat templates/rules/context-db.md
} >> your-project/AGENTS.md
```

### GitHub Copilot

`.github/copilot-instructions.md` plays the same role:

```bash
cat templates/rules/context-db.md >> your-project/.github/copilot-instructions.md
```

### Anything else

Any agent that reads a project-level instruction file works. The only runtime
requirement is that the agent can run a Python script and read its output.

## 5. Verify

```bash
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/
python3 .claude/skills/context-db/scripts/context-db-main-agent.py load-start-context
```

The first prints the TOC. The second prints the on-start payload — the exact
bytes the agent will see when the rule fires.

## Next steps

- [Commands](commands.md) — the sub-command catalog.
- [Rules](rules.md) — how the rule body works and how to customize it.
- [Configuring Posture](configuring-posture.md) — `.context-db.json`, `on_start`
  / `on_all`, reactive toggles.
- [Cross-Project Sharing](cross-project-sharing.md) — symlink folders from other
  repos.
- [Reference](../reference/specification.md) — format specification.
