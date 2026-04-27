# Rules

Every modern coding agent has a mechanism for project-level standing
instructions — a small set of bytes the agent re-reads on every turn (or at
session start) so a project's standards persist across long conversations.
Different agents call them different things — rules, `AGENTS.md`,
`.cursorrules`, `copilot-instructions.md` — but the role is the same.

context-db works with any of them. The pattern is universal:

> Tell the agent to run `context-db-main-agent.py load-start-context` at the
> start of every conversation, then follow what it prints.

The script emits the read-mechanics, the context-usage framing, and every file
matched by `on_start` / `on_all` globs (see
[Configuring Posture](configuring-posture.md)) — inlined raw, ready to act on.

## The default rule body

Whatever your agent's mechanism is, the body to install is one line:

```markdown
On session start, run `context-db-main-agent.py load-start-context` and follow
its output.
```

The script does the rest — read-mechanics, context-usage framing, and every file
matched by `on_start` / `on_all` globs gets inlined into the agent's context.
Posture (reactive vs. active) is controlled by the `remind-on-demand-read` /
`remind-on-demand-update` flags in `.context-db.json`, not the rule. See
[Configuring Posture](configuring-posture.md).

The exact path to the script depends on where it's installed. The canonical
install location is `.claude/skills/context-db/scripts/context-db-main-agent.py`
(see [Getting Started](getting-started.md)), but the scripts are pure Python and
run from anywhere — adjust the path in the rule to match your layout.

## Per-agent integration

### Claude Code

Drop the body into `.claude/rules/context-db.md`. Rules in that directory load
on every conversation turn and survive context compaction. The shipped template
is at `templates/rules/context-db.md` — copy or symlink it.

Claude Code also exposes the dispatcher as the `/context-db` skill, so the rule
can call `/context-db load-start-context` instead of the longer script path.

### Cursor

Two options. Newer projects use `.cursor/rules/context-db.md` — same format as
Claude rules. Older projects use a single `.cursorrules` file at the repo root.
Either works; paste the same body, with the script path set to wherever the
dispatcher lives.

### Codex / `AGENTS.md`

The emerging cross-agent convention is a top-level `AGENTS.md` file. Codex reads
it directly; many other agents also pick it up. Paste the rule body into
`AGENTS.md` (or append it under an existing `## context-db` heading).

### GitHub Copilot

`.github/copilot-instructions.md` plays the same role. Paste the body there.

### Anything else

Any agent that reads a project-level instruction file works. The only
requirement is that the agent can run a Python script and read its output.

## Calling the script manually

The script doesn't need an agent — it runs in any terminal:

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py \
  load-start-context
```

Output is the full payload: read-mechanics, context-usage, and every `on_start`
/ `on_all` file inlined raw with frontmatter stripped. Pipe it through `pbcopy`
(macOS) or `xclip` (Linux) to inspect or capture.

## Writing your own rule

The rule body is just text. Replace the default with something more opinionated
whenever the convention-driven behavior doesn't fit. A common pattern: capture
the script output, trim what's not needed, paste into the rule file. The agent
now sees the exact bytes chosen, with no indirection through the script.

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py \
  load-start-context > .claude/rules/context-db.md
# edit to taste
```

This is useful when:

- The rule should fail closed — no script execution required at startup.
- Specific sections need adding or removing without changing `.context-db.json`.
- Different rules per environment (dev vs. CI) are required without touching the
  command pipeline.

The tradeoff is staleness: a captured rule won't update when the underlying
templates or `on_start` / `on_all` files change. The default script-delegating
rule is recommended unless there's a specific reason to freeze the payload.

## Why a rule and not just `CLAUDE.md` / `AGENTS.md` body

Project instruction files (`CLAUDE.md`, `AGENTS.md`, plain `.cursorrules`) are
loaded as user context — the model weighs them but can skip them. Dedicated
rules directories (`.claude/rules/`, `.cursor/rules/`) are presented as project
rules, not background guidance, and they survive compaction. For something the
agent must do reliably across long sessions, a rule directory is the right home
where one exists; a top-level `AGENTS.md` is the right home where it doesn't.
