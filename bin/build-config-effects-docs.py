#!/usr/bin/env python3
"""
Generate docs/src/reference/config-effects.md from the acme example fixture.

Runs the dispatcher under several preset .context-db.json configs and several
sub-commands, captures stdout, and writes a markdown page showing how config
shapes the injected context.

Run from anywhere:
    python3 bin/build-config-effects-docs.py

Re-run whenever the dispatcher, prompt templates, or the example fixture
change. The pre-commit hook does this automatically.

Dependencies: python3 (stdlib only).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIR = REPO_ROOT / "example" / "acme-payments-repo"
DISPATCHER = ".claude/skills/context-db/scripts/context-db-main-agent.py"
OUT_PATH = REPO_ROOT / "docs" / "src" / "reference" / "config-effects.md"


# A scenario is a (name, description, config dict, list of commands) tuple.
# Each command is (label, argv list passed after the dispatcher).
SCENARIOS = [
    {
        "name": "Default config",
        "anchor": "default",
        "blurb": (
            "The shipped default. `main-agent` mode, both `on_start` and "
            "`on_all` populated with the project's `ON_START.md` / "
            "`ON_ALL.md`."
        ),
        "config": {
            "defaults": {
                "mode": "main-agent",
                "remind-on-demand-read": False,
                "remind-on-demand-update": False,
            },
            "on_start": ["*-project/ON_START.md"],
            "on_all": ["*-project/ON_ALL.md"],
        },
        "commands": [
            ("load-start-context", ["load-start-context"]),
            (
                'prompt "How do I add a new payment endpoint?"',
                ["prompt", "How do I add a new payment endpoint?"],
            ),
            (
                'update "Refunds must be filed as new entries, not edits"',
                [
                    "update",
                    "Refunds must be filed as new entries, not edits",
                ],
            ),
        ],
    },
    {
        "name": "Reactive posture",
        "anchor": "reactive",
        "blurb": (
            "`remind-on-demand-read` and `remind-on-demand-update` set to "
            "`true`. The dispatcher appends reminders telling the agent to "
            "read or write context-db only when the user explicitly invokes "
            "a `/context-db` command."
        ),
        "config": {
            "defaults": {
                "mode": "main-agent",
                "remind-on-demand-read": True,
                "remind-on-demand-update": True,
            },
            "on_start": ["*-project/ON_START.md"],
            "on_all": ["*-project/ON_ALL.md"],
        },
        "commands": [
            (
                'prompt "How do I add a new payment endpoint?"',
                ["prompt", "How do I add a new payment endpoint?"],
            ),
            (
                'update "Refunds must be filed as new entries, not edits"',
                [
                    "update",
                    "Refunds must be filed as new entries, not edits",
                ],
            ),
        ],
    },
    {
        "name": "Minimal — no on_start, no on_all",
        "anchor": "minimal",
        "blurb": (
            "Empty globs for both always-loaded lists. `load-start-context` "
            "emits only the read mechanics and context-usage framing; no "
            "project-specific content is inlined."
        ),
        "config": {
            "defaults": {
                "mode": "main-agent",
                "remind-on-demand-read": False,
                "remind-on-demand-update": False,
            },
            "on_start": [],
            "on_all": [],
        },
        "commands": [
            ("load-start-context", ["load-start-context"]),
            (
                'prompt "How do I add a new payment endpoint?"',
                ["prompt", "How do I add a new payment endpoint?"],
            ),
        ],
    },
    {
        "name": "Per-subcommand supplement (`on_prompt`)",
        "anchor": "on-prompt",
        "blurb": (
            "`on_prompt` carries content scoped to `/context-db prompt` only. "
            "Here it reuses the project's `ON_START.md` to demonstrate "
            "placement: the `on_prompt` block is inlined right after `on_all` "
            "and right before the user's instructions when `prompt` runs, but "
            "is absent when `update` runs."
        ),
        "config": {
            "defaults": {
                "mode": "main-agent",
                "remind-on-demand-read": False,
                "remind-on-demand-update": False,
            },
            "on_start": [],
            "on_all": ["*-project/ON_ALL.md"],
            "on_prompt": ["*-project/ON_START.md"],
        },
        "commands": [
            (
                'prompt "How do I add a new payment endpoint?"',
                ["prompt", "How do I add a new payment endpoint?"],
            ),
            (
                'update "Refunds must be filed as new entries, not edits"',
                [
                    "update",
                    "Refunds must be filed as new entries, not edits",
                ],
            ),
        ],
    },
]


def run_dispatcher(argv):
    """Run dispatcher with cwd=EXAMPLE_DIR, return stdout."""
    result = subprocess.run(
        ["python3", DISPATCHER, *argv],
        cwd=EXAMPLE_DIR,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        sys.exit(
            f"dispatcher failed for {argv!r}: {result.stderr}"
        )
    return result.stdout.rstrip()


def render_config(config):
    """Pretty-print a config dict as JSONC-style block."""
    return json.dumps(config, indent=2)


def render_scenario(scenario):
    """Render one scenario as a markdown section."""
    lines = []
    lines.append(f"## {scenario['name']} {{#{scenario['anchor']}}}")
    lines.append("")
    lines.append(scenario["blurb"])
    lines.append("")
    lines.append("**`.context-db.json`:**")
    lines.append("")
    lines.append("```jsonc")
    lines.append(render_config(scenario["config"]))
    lines.append("```")
    lines.append("")

    for label, argv in scenario["commands"]:
        output = run_dispatcher(argv)
        lines.append(f"### `/context-db {label}`")
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>injected context</summary>")
        lines.append("")
        lines.append("```")
        lines.append(output)
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)


def main():
    if not EXAMPLE_DIR.is_dir():
        sys.exit(f"missing fixture: {EXAMPLE_DIR}")
    if not (EXAMPLE_DIR / DISPATCHER).exists():
        sys.exit(f"missing dispatcher symlink: {EXAMPLE_DIR / DISPATCHER}")

    config_path = EXAMPLE_DIR / ".context-db.json"
    backup = config_path.read_text() if config_path.exists() else None

    try:
        sections = []
        for scenario in SCENARIOS:
            config_path.write_text(render_config(scenario["config"]) + "\n")
            sections.append(render_scenario(scenario))
    finally:
        if backup is not None:
            config_path.write_text(backup)

    header = dedent(
        """\
        # How `.context-db.json` shapes injected context

        > [!note] Auto-generated. Do not edit by hand.
        >
        > This page is regenerated from the
        > [`example/acme-payments-repo/`](https://github.com/cart0113/context-db/tree/main/example/acme-payments-repo)
        > fixture by `bin/build-config-effects-docs.py`. The pre-commit
        > hook re-runs the script whenever the dispatcher, prompt
        > templates, or the example fixture change.

        Each scenario below shows a different `.context-db.json` config and
        the literal text the dispatcher emits for the listed sub-commands.
        Output is what the calling agent reads on every invocation —
        instruction templates, the `on_start` / `on_all` payload, and the
        user instructions appended last.

        See [Configuring Posture](../guide/configuring-posture.md) for the
        full schema.

        """
    )

    body = "\n".join(sections)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(header + body + "\n")
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
