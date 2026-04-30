# Example: acme-payments-repo

A runnable reference layout for context-db. Doubles as the fixture for the
dynamic config-effects documentation generator
(`bin/build-config-effects-docs.py`).

```
example/
├── shared/                          ← cross-project standards
│   ├── coding-standards/
│   └── git-standards/
└── acme-payments-repo/              ← the example project
    ├── .context-db.json
    ├── .claude/
    │   ├── rules/context-db.md
    │   └── skills/context-db/       ← scripts symlink to ../templates/...
    └── context-db/
        ├── acme-payments-project/
        │   ├── ON_START.md
        │   ├── ON_ALL.md
        │   ├── architecture.md
        │   ├── api-reference.md
        │   └── data-model/
        ├── coding-standards -> ../../shared/coding-standards
        └── git-standards -> ../../shared/git-standards
```

The `coding-standards/` and `git-standards/` symlinks demonstrate the
cross-project sharing pattern — a single source of truth lives under
`example/shared/`, and the project's `context-db/` reaches into it.

The dispatcher scripts under `.claude/skills/context-db/scripts/` are symlinked
back to `templates/skills/context-db/scripts/`, so the layout is genuinely
runnable without copying scripts.

## Run the dispatcher against this fixture

```bash
cd example/acme-payments-repo
python3 .claude/skills/context-db/scripts/context-db-main-agent.py load-start-context
python3 .claude/skills/context-db/scripts/context-db-main-agent.py prompt "How do I add a new payment endpoint?"
```

Output is what a calling agent would see when the user invokes
`/context-db load-start-context` or `/context-db prompt "..."`.

## Generated docs

`bin/build-config-effects-docs.py` runs the dispatcher against this fixture
under several preset `.context-db.json` configs and renders
[Config Effects](../docs/src/reference/config-effects.md). The pre-commit hook
regenerates the page when the dispatcher, prompt templates, or this fixture
change.
