#!/usr/bin/env python3
"""
context-db-main-agent.py — dispatcher for /context-db skill.

Called by the main agent via SKILL.md. Reads config, determines mode, and
prints tagged output sections for the agent to follow.

Run with --help or <command> --help for usage.

Dependencies: python3 (stdlib only)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────────────
#
# Two execution modes:
#   main-agent — prints tagged prompt sections that the calling agent follows
#                directly (agent navigates context-db itself)
#   sub-agent  — prints instructions telling the calling agent to spawn
#                context-db-sub-agent.py (isolated claude -p lookup)
#
# Per-command defaults below can be overridden by .context-db.json in the
# project root, and further overridden by CLI flags (--mode, --model).

COMMANDS = ["prompt", "pre-review", "review", "update", "maintain"]

# Available sections for load-manual. Each entry is (name, description).
MANUAL_SECTIONS = [
    ("on-demand",            "Don't browse context-db — wait for /context-db commands"),
    ("read-mechanics",       "How to navigate context-db via TOC script"),
    ("prompt",               "Instructions for prompt command"),
    ("context-usage",        "Context-db is a map, not truth — verify against code"),
    ("write-mechanics",      "How to edit context-db files"),
    ("write-content-guide",  "What belongs in context-db"),
    ("persist-to-context-db","Use context-db, not auto-memory, for project knowledge"),
    ("pre-review",           "Check plan against standards before implementing"),
    ("review",               "Review changes against conventions"),
    ("update-general",       "File learnings into context-db"),
    ("update-commit",        "How to write commit messages"),
]

DEFAULT_CONFIG = {
    "defaults": {
        "mode": "sub-agent",
        "model": "haiku",
    },
    # Globs (relative to context-db/) whose content is inlined on session
    # startup via `load-startup-rule`. Use for orienting content the agent
    # needs once per session.
    "load_on_startup": [],
    # Globs inlined on EVERY subcommand invocation (prompt, pre-review,
    # review, update, maintain). Keep BRIEF — real estate is at a premium.
    "load_always": [],
    "prompt": {},
    "pre-review": {},
    "review": {
        "model": "sonnet",        # reviews need more reasoning
    },
    "update": {
        "mode": "main-agent",     # writes files — must run in main agent
        "model": "sonnet",
    },
    "maintain": {
        "mode": "main-agent",     # writes files — must run in main agent
    },
}


def strip_jsonc_comments(text):
    """Strip // comments from JSONC text. Ignores // inside strings."""
    import re
    return re.sub(r'(?<!:)//.*', '', text)


def load_config(config_path):
    """Load .context-db.json (JSONC — // comments allowed), merge with defaults.

    Merge strategy: user values override defaults at each level.
    Deep-copy via JSON round-trip so DEFAULT_CONFIG stays immutable.
    """
    config = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if os.path.exists(config_path):
        with open(config_path) as f:
            raw = f.read()
        user = json.loads(strip_jsonc_comments(raw))
        if "defaults" in user:
            config["defaults"].update(user["defaults"])
        for cmd in COMMANDS:
            if cmd in user:
                config[cmd].update(user[cmd])
        for key in ("load_on_startup", "load_always"):
            if key in user:
                config[key] = list(user[key])
    return config


def get_command_config(config, command):
    """Get effective config for a command (defaults merged with command-specific).

    Layering: DEFAULT_CONFIG defaults → user defaults → command overrides.
    """
    effective = dict(config["defaults"])
    effective.update(config[command])
    return effective


# ── Path discovery ──────────────────────────────────────────────────────────
# All paths returned relative to cwd so the agent's Bash/Read calls work
# without absolute-path issues (see feedback_paths_relative.md).
# Search order: standard .claude/ location → parent dir → __file__ fallback.


def find_toc_script():
    """Find context-db-generate-toc.py. Returns path relative to cwd."""
    rel = ".claude/skills/context-db/scripts/context-db-generate-toc.py"
    if os.path.exists(rel):
        return rel
    parent_rel = os.path.join("..", rel)
    if os.path.exists(parent_rel):
        return parent_rel
    candidate = Path(__file__).resolve().parent / "context-db-generate-toc.py"
    if candidate.exists():
        return str(candidate)
    return rel


def find_sub_agent_script():
    """Find context-db-sub-agent.py. Returns path relative to cwd."""
    rel = ".claude/skills/context-db/scripts/context-db-sub-agent.py"
    if os.path.exists(rel):
        return rel
    parent_rel = os.path.join("..", rel)
    if os.path.exists(parent_rel):
        return parent_rel
    candidate = Path(__file__).resolve().parent / "context-db-sub-agent.py"
    if candidate.exists():
        return str(candidate)
    return rel


def find_context_db():
    """Find context-db/ relative to cwd."""
    if os.path.isdir("context-db"):
        return "context-db"
    return "."


# ── Git diff collection ─────────────────────────────────────────────────────
# Used by --use-git-diff on the prompt command to show which context-db files
# were touched recently (likely relevant to where a prior session left off).

DIFF_LINE_CAP = 500


def collect_recent_changes(context_db_rel, n):
    """Collect recent git changes in context-db/. Returns formatted block, or None.

    n=0: uncommitted changes only.
    n>0: uncommitted + last n commits touching context-db/.

    If combined diff exceeds DIFF_LINE_CAP, falls back to --stat summary.
    """
    if context_db_rel == ".":
        # No context-db/ folder found — diff would be scoped to everything.
        return None

    def run(args):
        try:
            r = subprocess.run(
                args, capture_output=True, text=True, timeout=10,
            )
            return r.stdout if r.returncode == 0 else ""
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    sections = []  # list of (header, stat_text, full_diff_text)

    uncommitted_full = run(["git", "diff", "HEAD", "--", context_db_rel])
    if uncommitted_full.strip():
        uncommitted_stat = run(
            ["git", "diff", "HEAD", "--stat", "--", context_db_rel]
        )
        sections.append(
            ("## Uncommitted Changes", uncommitted_stat, uncommitted_full)
        )

    if n > 0:
        commits_full = run(
            ["git", "log", "-n", str(n), "-p", "--", context_db_rel]
        )
        if commits_full.strip():
            commits_stat = run([
                "git", "log", "-n", str(n), "--stat",
                "--format=%h %s", "--", context_db_rel,
            ])
            header = f"## Last {n} Commit{'s' if n != 1 else ''}"
            sections.append((header, commits_stat, commits_full))

    if not sections:
        return None

    total_lines = sum(len(full.splitlines()) for _, _, full in sections)
    use_stat = total_lines > DIFF_LINE_CAP

    out = []
    if use_stat:
        out.append(
            f"(Diff exceeded {DIFF_LINE_CAP} lines — showing file stats only. "
            f"Use `git diff HEAD -- {context_db_rel}/` or "
            f"`git log -p -n {n} -- {context_db_rel}/` for full content.)\n"
        )
    for header, stat, full in sections:
        out.append(header)
        out.append("")
        out.append((stat if use_stat else full).strip())
        out.append("")

    return "\n".join(out).strip()


# ── Pattern expansion and file inlining ─────────────────────────────────────
# Used by `read`, `load-startup-rule`, and the --load-startup-rule /
# --load-always flags. Patterns are globs resolved relative to base_dir
# (context-db/ by default). Folders match expand to every file underneath.


def expand_patterns(patterns, base_dir):
    """Expand glob patterns (relative to base_dir) into a list of files.

    Each pattern may match files or folders. Folders expand recursively to
    every file beneath them. Deduplicates while preserving pattern order.
    Returns paths relative to cwd.
    """
    base = Path(base_dir) if base_dir else Path(".")
    seen = set()
    files = []
    for pattern in patterns:
        for match in sorted(base.glob(pattern)):
            if match.is_file():
                rel = str(match)
                if rel not in seen:
                    seen.add(rel)
                    files.append(rel)
            elif match.is_dir():
                for sub in sorted(match.rglob("*")):
                    if sub.is_file():
                        rel = str(sub)
                        if rel not in seen:
                            seen.add(rel)
                            files.append(rel)
    return files


def inline_file(path):
    """Return a single file's content wrapped with a path header."""
    try:
        content = Path(path).read_text()
    except OSError as e:
        return f"## {path}\n\n(error reading: {e})\n"
    return f"## {path}\n\n{content.rstrip()}\n"


def inline_patterns(patterns, base_dir):
    """Expand patterns and return concatenated inlined content.

    Returns empty string if nothing matches.
    """
    files = expand_patterns(patterns, base_dir)
    if not files:
        return ""
    return "\n".join(inline_file(f) for f in files)


# ── Template loading ────────────────────────────────────────────────────────
# Prompt templates live in prompts/main-agent/*.md. Each has a single H1
# header (e.g. # Read Mechanics) as its section delimiter. Variables use
# {name} syntax.


def load_template(name, subdir="main-agent"):
    """Load a prompt template from prompts/<subdir>/<name>.md."""
    prompts_dir = Path(__file__).resolve().parent / "prompts" / subdir
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        sys.exit(f"Error: template not found: {path}")
    return path.read_text()


def fill_template(template, **kwargs):
    """Fill {variables} in a template. Unknown variables are left as-is."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


# ── Output helpers ─────────────────────────────────────────────────────────
# Everything this script prints goes directly into the agent's context.
# H1 headers (# Read Mechanics) delimit sections — they're the protocol
# between this script and the LLM.


def print_template(name, subdir="main-agent", **kwargs):
    """Load a template, fill variables, and print. H1 header is in the file."""
    print()
    print(fill_template(load_template(name, subdir), **kwargs))


def print_section(tag, content):
    """Print a dynamically H1-delimited section (for content not from templates).

    Used for user instructions and other dynamic content that doesn't
    have its own template file. Converts kebab-case tag to Title Case H1.
    """
    title = tag.replace("-", " ").title()
    print(f"\n# {title}\n")
    print(content.strip())


# ── Command handlers ────────────────────────────────────────────────────────
# Each handler assembles the right combination of templates for its command.
# Read commands (prompt, pre-review, review) get read-mechanics + context-usage.
# Write commands (update, maintain) get write-mechanics + write-content-guide.


def cmd_load_manual(args):
    """Load a single instruction template by name."""
    toc = find_toc_script()
    context_db_rel = find_context_db()
    print_template(args.section, subdir="main-agent", toc=toc,
                   context_db_rel=context_db_rel)


# ── load_always / load_on_startup emitters ──────────────────────────────────
# Shared between the load-startup-rule subcommand and the --load-always /
# --load-startup-rule flags on other subcommands. Output goes straight to
# stdout as H1-delimited sections.


ALWAYS_PREAMBLE = (
    "IMPORTANT! Please follow these instructions during any operation:"
)


def emit_load_always(config, context_db_rel):
    """Print load_always content (brief, fires on every subcommand).

    No-op if load_always is empty or nothing matches.
    """
    patterns = config.get("load_always", [])
    if not patterns:
        return
    content = inline_patterns(patterns, context_db_rel)
    if not content:
        return
    print(f"\n# Always-Load\n\n{ALWAYS_PREAMBLE}\n\n{content}")


def emit_load_on_startup(config, context_db_rel):
    """Print load_on_startup content. No-op if empty or nothing matches."""
    patterns = config.get("load_on_startup", [])
    if not patterns:
        return
    content = inline_patterns(patterns, context_db_rel)
    if not content:
        return
    print(f"\n# On-Startup\n\n{content}")


def cmd_read(args):
    """Inline full content for one or more paths/globs.

    Files are printed verbatim with an H2 path header; folders are
    expanded recursively. Paths resolve against cwd, not context-db/,
    so the caller controls the base.
    """
    files = expand_patterns(args.paths, ".")
    if not files:
        print("(no files matched)")
        return
    print("\n".join(inline_file(f) for f in files))


def cmd_load_startup_rule(args, config):
    """Print the session-startup rule: inlined startup + always content,
    then the read mechanics the agent needs to navigate context-db.
    """
    toc = find_toc_script()
    context_db_rel = find_context_db()

    emit_load_on_startup(config, context_db_rel)
    emit_load_always(config, context_db_rel)

    print_template("read-mechanics", toc=toc, context_db_rel=context_db_rel)
    print_template("read-usage", toc=toc, context_db_rel=context_db_rel)


def cmd_main_agent(command, prompt, cmd_config, debug=False):
    """Print tagged prompt sections so the calling agent navigates context-db itself.

    This is the "main-agent" mode — no sub-process, the agent uses its own
    tools (Read, Bash) to browse the TOC and read files.
    """
    toc = find_toc_script()
    context_db_rel = find_context_db()

    if debug:
        print(f"mode: main-agent")
        print(f"context-db: {context_db_rel}/")
        print(f"toc: {toc}")

    if command == "update":
        commit = cmd_config.get("commit", False)
        if commit:
            print_template("read-mechanics", toc=toc,
                            context_db_rel=context_db_rel)
        print_template("write-mechanics", toc=toc,
                        context_db_rel=context_db_rel)
        print_template("persist-to-context-db")
        print_template("update-general",
                        context_db_rel=context_db_rel)
        if prompt:
            print_section("update-user-instructions", prompt)
        if commit:
            print_template("update-commit")
        if cmd_config.get("push", False):
            print_template("update-push")
    else:
        # Read commands: prompt, pre-review, review
        print_template("read-mechanics", toc=toc, context_db_rel=context_db_rel)
        if command == "prompt":
            print_template("context-usage")
            use_git_diff = cmd_config.get("use-git-diff")
            if use_git_diff is not None:
                block = collect_recent_changes(context_db_rel, use_git_diff)
                if block:
                    print_template("recent-changes",
                                   recent_changes_block=block)
        print_template(command)
        if prompt:
            print_section(f"{command}-user-instructions", prompt)


def cmd_sub_agent(command, prompt, cmd_config, debug=False):
    """Print spawn instructions telling the main agent to invoke the sub-agent.

    The main agent will run the printed command via Bash, which spawns an
    isolated claude -p process (context-db-sub-agent.py). The sub-agent's
    response comes back as tagged blocks the main agent can use directly.
    """
    sub_agent = find_sub_agent_script()
    model = cmd_config["model"]
    rerun_init = cmd_config.get("rerun-init", False)

    # Build the shell command the main agent will run.
    # For pre-review, the agent fills in the plan; for others, prompt is baked in.
    cmd_parts = [f"python3 {sub_agent} {command}"]
    if command == "pre-review":
        cmd_parts.append('"<PLAN>"')
    else:
        cmd_parts.append(f'"{prompt}"')
    cmd_parts.append(f"--model {model}")
    if command == "review" and cmd_config.get("context-db-only-review"):
        cmd_parts.append("--context-db-only-review")
    if command == "prompt":
        use_git_diff = cmd_config.get("use-git-diff")
        if use_git_diff is not None:
            cmd_parts.append(f"--use-git-diff {use_git_diff}")
    if rerun_init:
        cmd_parts.append("--rerun-init")
    if debug:
        cmd_parts.append("--debug")

    run_cmd = " ".join(cmd_parts)

    if debug:
        print(f"mode: sub-agent")
        print(f"model: {model}")

    print_template(command, subdir="spawn", run_cmd=run_cmd)

    # For pre-review, print user instructions separately so the agent
    # incorporates them into the plan it sends to the sub-agent
    if command == "pre-review" and prompt:
        print_section("pre-review-user-instructions", prompt)



def cmd_ask_mode(command, prompt, cmd_config, debug=False):
    """Print instructions to ask the user which mode to use."""
    instructions = (
        f"Ask the user: Should I consult context-db as a **sub-agent** "
        f"(isolated lookup, faster) or **main-agent** (I navigate directly, "
        f"more thorough)?\n\n"
        f"Then re-run with their choice:\n"
        f"  /context-db {command} --mode <their-choice> {prompt}"
    )
    print_section("instructions", instructions)



def cmd_read_all(args):
    """Print instructions to exhaustively read a context-db folder."""
    toc = find_toc_script()
    context_db_rel = find_context_db()
    target_path = args.folder if args.folder else f"{context_db_rel}/"

    print_template("read-all", toc=toc, context_db_rel=context_db_rel,
                    target_path=target_path)


def cmd_maintain(args, config):
    """Print instructions for the maintain workflow (audit + fix context-db)."""
    toc = find_toc_script()
    context_db_rel = find_context_db()
    target_path = args.path if args.path else f"{context_db_rel}/"

    if getattr(args, "load_startup_rule", False):
        emit_load_on_startup(config, context_db_rel)
    emit_load_always(config, context_db_rel)

    print_template("write-mechanics", toc=toc, context_db_rel=context_db_rel)
    print_template("write-content-guide")
    print_template("maintain-instructions", toc=toc,
                    context_db_rel=context_db_rel, target_path=target_path)



# ── CLI ─────────────────────────────────────────────────────────────────────
# Subparsers mirror the COMMANDS list. Each read/write command gets --mode,
# --model, --debug, --config flags via add_mode_flags(). "load-manual" and
# "maintain" have their own argument shapes.

MODE_CHOICES = ["sub-agent", "main-agent", "ask"]
MODEL_CHOICES = ["haiku", "sonnet", "opus", "ask"]


def add_mode_flags(sub):
    """Add --mode, --model, --debug, --config to a subparser."""
    sub.add_argument("--mode", choices=MODE_CHOICES)
    sub.add_argument("--model", choices=MODEL_CHOICES)
    sub.add_argument("--config", default=".context-db.json")
    sub.add_argument("--debug", action="store_true")
    sub.add_argument("--load-startup-rule", action="store_true",
                     help="Also inline load_on_startup content before the "
                          "command output (use for sub-agents that missed "
                          "the session-start load).")


def dispatch_command(args, config):
    """Route a prompt/pre-review/review/update command by mode.

    Config layering: DEFAULT_CONFIG → .context-db.json → CLI flags.
    Final "mode" value determines which handler runs.
    """
    command = args.command
    prompt = args.instruction

    if not prompt and command not in ("update", "pre-review", "review"):
        print(f"No instruction provided. Ask the user what they want to "
              f"{command}.")

        return

    # Prepend always-load content on every subcommand, and startup content
    # on demand via --load-startup-rule (useful for sub-agents that missed
    # the session-start load).
    context_db_rel = find_context_db()
    if getattr(args, "load_startup_rule", False):
        emit_load_on_startup(config, context_db_rel)
    emit_load_always(config, context_db_rel)

    # Build effective config: defaults ← command overrides ← CLI flags
    cmd_config = get_command_config(config, command)

    if args.mode:
        cmd_config["mode"] = args.mode
    if args.model:
        cmd_config["model"] = args.model
    if hasattr(args, "context_db_only_review") and args.context_db_only_review:
        cmd_config["context-db-only-review"] = True
    if hasattr(args, "use_git_diff") and args.use_git_diff is not None:
        cmd_config["use-git-diff"] = args.use_git_diff
    if hasattr(args, "commit") and args.commit:
        cmd_config["commit"] = True
    if hasattr(args, "push") and args.push:
        cmd_config["push"] = True
        cmd_config["commit"] = True  # --push implies --commit

    mode = cmd_config["mode"]

    if mode == "main-agent":
        cmd_main_agent(command, prompt, cmd_config, args.debug)
    elif mode == "sub-agent":
        cmd_sub_agent(command, prompt, cmd_config, args.debug)
    elif mode == "ask":
        cmd_ask_mode(command, prompt, cmd_config, args.debug)


def main():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="Project knowledge base",
    )
    subs = parser.add_subparsers(dest="command")

    # load-manual
    section_names = [name for name, _ in MANUAL_SECTIONS]
    section_help = "\n".join(
        f"  {name:<24s}{desc}"
        for name, desc in MANUAL_SECTIONS
    )
    lm = subs.add_parser(
        "load-manual",
        help="Load a single instruction template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"available sections:\n\n{section_help}",
    )
    lm.add_argument("section", choices=section_names,
                    metavar="section",
                    help="Section to load (see list below)")

    # prompt
    p = subs.add_parser("prompt", help="Consult knowledge base")
    p.add_argument("instruction", nargs="?", default="")
    p.add_argument("--use-git-diff", nargs="?", const=3, default=None,
                   type=int, metavar="N",
                   help="Prepend recent context-db git changes. N=commits "
                        "to include (default 3, 0=uncommitted only)")
    add_mode_flags(p)

    # pre-review
    pr = subs.add_parser("pre-review",
                         help="Check plan against standards before implementing")
    pr.add_argument("instruction", nargs="?", default="")
    add_mode_flags(pr)

    # review
    rv = subs.add_parser("review",
                         help="Review changes against conventions")
    rv.add_argument("instruction", nargs="?", default="")
    rv.add_argument("--context-db-only-review", action="store_true",
                    help="Only flag issues backed by context-db conventions")
    add_mode_flags(rv)

    # update
    up = subs.add_parser("update", help="File learnings into context-db")
    up.add_argument("instruction", nargs="?", default="")
    up.add_argument("--commit", action="store_true",
                    help="Commit affected files after updating context-db")
    up.add_argument("--push", action="store_true",
                    help="Push after committing (implies --commit)")
    add_mode_flags(up)

    # read-all
    ra = subs.add_parser("read-all",
                         help="Exhaustively read everything under a folder")
    ra.add_argument("folder", nargs="?", default="")

    # read — inline file/folder content (glob-capable)
    rd = subs.add_parser("read",
                         help="Inline full content of files/folders/globs")
    rd.add_argument("paths", nargs="+",
                    help="One or more paths or glob patterns")

    # load-startup-rule — session-startup orientation
    lsr = subs.add_parser(
        "load-startup-rule",
        help="Emit session-startup rule: load_on_startup + load_always + "
             "read mechanics/usage")
    lsr.add_argument("--config", default=".context-db.json")

    # maintain
    mt = subs.add_parser("maintain", help="Audit and maintain context-db")
    mt.add_argument("path", nargs="?", default="")
    mt.add_argument("--config", default=".context-db.json")
    mt.add_argument("--load-startup-rule", action="store_true",
                    help="Also inline load_on_startup content before the "
                         "command output.")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = load_config(
        args.config if hasattr(args, "config") else ".context-db.json"
    )

    if args.command == "load-manual":
        cmd_load_manual(args)
    elif args.command == "read-all":
        cmd_read_all(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "load-startup-rule":
        cmd_load_startup_rule(args, config)
    elif args.command == "maintain":
        cmd_maintain(args, config)
    else:
        dispatch_command(args, config)


if __name__ == "__main__":
    main()
