# Reference

## Description files

A folder is a **context node** if it contains a descriptor file:

- `<folder_name>.md`
- `<folder_name>-instructions.md`
- `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`

The descriptor has YAML frontmatter with a `description` key and an empty body.

```yaml
---
description: Acme Payments — architecture, APIs, and data model
---
```

Descriptions can span multiple lines using YAML block scalar syntax:

```yaml
---
description:
  Acme Payments — architecture, APIs, data model, and deployment constraints
---
```

The descriptor for the **project folder** should open with the marker
`Main project folder for this repo.` — the dispatcher and `maintain` command
rely on it to distinguish the project folder from parallel external folders.

```yaml
---
description:
  Main project folder for this repo. Acme Payments — architecture, APIs, data
  model.
---
```

## Context documents

Individual `.md` files with YAML frontmatter and body. The `description` appears
in the parent's TOC when the TOC script is run.

```yaml
---
description: System components, data flow, and service boundaries
---
# Architecture

(content)
```

## Optional fields

The only required frontmatter field is `description`.

### `status`

Lifecycle stage of the document: `draft`, `stable`, or `deprecated`. Default
(when omitted): `stable`.

```yaml
---
description: Legacy payment processing flow
status: deprecated
---
```

When `status` is not `stable`, the TOC script appends it to the entry so agents
see the lifecycle without opening the file.

## Directory layout

```
your-project/
├── .claude/
│   ├── rules/context-db.md                ← standing rule loaded every session
│   └── skills/context-db/                 ← unified skill: dispatcher + scripts
│       ├── SKILL.md
│       └── scripts/
│           ├── context-db-generate-toc.py
│           ├── context-db-main-agent.py
│           ├── context-db-resolve-path.py
│           └── context-db-sub-agent.py
├── .context-db.json                       ← per-command mode/model/posture
└── context-db/
    ├── <project-name>-project/            ← knowledge specific to this repo
    │   ├── <project-name>-project.md      ← folder descriptor
    │   ├── ON_START.md                    ← inlined once per session
    │   ├── ON_ALL.md                      ← inlined every command
    │   ├── architecture.md                ← context document
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/                  ← project-agnostic, often symlinked
```

## `.context-db.json` schema

JSONC (JSON with `// line comments` and trailing commas). All keys optional.

```jsonc
{
  // Fallback for any per-command key not set below.
  "defaults": {
    "mode": "main-agent", // main-agent | sub-agent
    "model": "haiku", // haiku | sonnet | opus
    "remind-on-demand-read": false,
    "remind-on-demand-update": false,
  },

  // Per-command overrides. Only set keys that should differ from defaults.
  "review": { "model": "sonnet" },
  "update": { "model": "sonnet" },

  // Glob patterns relative to context-db/.
  "on_start": ["*-project/ON_START.md"],
  "on_all": ["*-project/ON_ALL.md"],
}
```

### Per-command keys

| Key                       | Type | Default      | Effect                                                                                                                        |
| ------------------------- | ---- | ------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `mode`                    | enum | `main-agent` | `main-agent` runs in the active conversation. `sub-agent` spawns a separate process.                                          |
| `model`                   | enum | `haiku`      | Model used for sub-agent dispatch and recommended for main-agent execution.                                                   |
| `remind-on-demand-read`   | bool | `false`      | Appends a reminder telling the agent to read context-db only when the user explicitly invokes a `/context-db` command.        |
| `remind-on-demand-update` | bool | `false`      | Appends a reminder telling the agent to write to context-db only via explicit `/context-db update` or `/context-db maintain`. |

`update` and `maintain` are pinned to `main-agent` regardless of `mode` because
they edit the working tree. Set the `remind-on-demand-*` flags in `defaults` to
apply them across all commands; per-command overrides are still allowed.

### Always-loaded content

| Key        | Type           | Effect                                                                             |
| ---------- | -------------- | ---------------------------------------------------------------------------------- |
| `on_start` | array of globs | Files inlined raw at the top of `load-start-context` (once per session).           |
| `on_all`   | array of globs | Files inlined raw at the end of every sub-command, right before user instructions. |

Globs are relative to `context-db/`. Folders expand recursively. Frontmatter is
stripped from inlined content; body is emitted as-is.

## Symlinks

Symlinked folders appear in the TOC when the script runs on the parent. The
script resolves symlinks to find the real folder name for descriptor lookup, so
symlinks can be named freely. Cross-references that traverse symlinked subtrees
should use the path-resolver script:

```bash
python3 .claude/skills/context-db/scripts/context-db-resolve-path.py \
  <containing-file> <link>
```

It prints an absolute path that resolves correctly through the symlink. Direct
`..` traversal is unreliable inside a symlinked tree.

To keep a symlink private, add it to `.gitignore`:

```gitignore
context-db/my-private-link
```

The TOC is generated on the fly, so private symlinks appear in your TOC without
affecting anyone else's working tree. See
[Cross-Project Sharing](../guide/cross-project-sharing.md).

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always
skipped.

## TOC format

`context-db-generate-toc.py` prints to stdout in this format:

<!-- prettier-ignore -->
```markdown
## Subfolders

- description: Database schema, entities, and relationships
  path: data-model/

## Files

- description: REST API endpoints, authentication, and error codes
  path: api-reference.md
- description: System components, data flow, and service boundaries
  path: architecture.md
```

Each entry has `description:` on the first line and `path:` on the second.
Sections only appear when there are entries. An empty folder produces no output.

## Scripts

### `context-db-generate-toc.py`

Generates a TOC for a context-db folder and prints it to stdout.

```bash
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/my-project/
```

- Single directory argument.
- Finds the descriptor file for that directory.
- Lists subfolders (that are context nodes) and files with descriptions.
- Resolves symlinks for descriptor lookup but follows them for reading.
- Skips underscore-prefixed and dot-prefixed names.
- Pure Python 3 — no third-party dependencies.

### `context-db-main-agent.py`

The sub-command dispatcher. See [Commands](../guide/commands.md) for the
sub-command catalog.

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

Each sub-command takes one positional `instruction` argument where one applies.
Multi-word instructions must be quoted as a single shell argument.

### `context-db-sub-agent.py`

Internal — invoked by the dispatcher when a sub-command's `mode` is `sub-agent`.
Not run directly. See [Sub-Agents](../guide/sub-agents.md).

### `context-db-resolve-path.py`

Resolves cross-reference paths inside symlinked subtrees. Prints an absolute
path to stdout.

```bash
python3 .claude/skills/context-db/scripts/context-db-resolve-path.py \
  <containing-file> <link>
```

## `build_site.sh`

Generates a browsable Docsify site from a context-db directory.

```bash
bin/build_site.sh <source_dir> <output_dir>
bin/build_site.sh --embed <source_dir> <output_dir>
bin/build_site.sh --template file.html <source_dir> <output_dir>
```

| Flag         | Effect                                                                |
| ------------ | --------------------------------------------------------------------- |
| `--embed`    | Skip `index.html` / `.nojekyll` (for nesting under existing Docsify). |
| `--template` | Use a custom `index.html` instead of the default.                     |

## pre-commit hook

Runs formatters (prettier, ruff) on staged files:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
