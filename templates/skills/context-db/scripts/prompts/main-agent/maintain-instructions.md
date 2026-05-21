# Maintain Instructions

Target: {target_path}

Before starting, ask the user how they want to run this:

1. **Guided** — stop after each phase, wait for input
2. **Review** — run all phases, report findings, don't change without approval
3. **Autonomous** — run all phases, fix what's clear, summarize + ask on
   ambiguity

Wait for their answer before proceeding.

Phase 0 — Project folder convention: `{context_db_rel}/` should contain exactly
one `<name>-project/` folder for knowledge specific to this repo. Other
top-level folders are broader standards or symlinks shared across projects.

- If no project folder exists, ask the user whether to create one.
- If a project folder exists, open its descriptor at
  `<name>-project/<name>-project.md` and ensure the frontmatter `description`
  opens by marking the folder as the main project folder for this repo — e.g.
  `description: Main project folder for this repo. <one-line summary of what's inside>`.
  Read-side agents rely on this marker to weight the project folder above the
  parallel external folders, so do not skip it.
- If multiple `*-project/` folders exist, surface this to the user — the
  convention is one per repo.

Phase 1 — Structural health: 5-10 items per folder, 50-150 lines per file, 2-3
levels deep max. Split oversized files/folders, merge tiny ones, fill missing
folder descriptors, sharpen vague descriptions.

Phase 2 — Content freshness: Use git log and git diff. Verify referenced
files/functions still exist. Fix outdated content directly.

Phase 3 — Content value: Cut content that restates what's in the code — CLI
flags, function signatures, file layouts, property lists, step-by-step
instructions. But do not remove real knowledge (decisions, rationale, gotchas,
conventions) just because it could be shorter. If the detail would be lost, keep
it.

Phase 4 — Coverage gaps: Check recent git history for corrections, reverts,
pitfalls. Add only genuinely non-obvious entries.

Phase 5 — Documentation drift: Compare context-db against project docs. Where
they disagree, trust the project assets.

Phase 6 — Cross-references: All cross-reference paths must be file-relative
(`./foo.md`, `../bar/baz.md`). Convert any absolute or project-rooted paths
(`context-db/...`) to file-relative form. Verify `..`-style links resolve
correctly: `python3 {resolve} <containing-file> <link>`. Fix broken links. Add
new ones only where genuinely helpful.

Phase 7 — Reindex: Re-read every file, update all description fields to match
current content. Work bottom-up (deepest folders first). Run TOC on every
changed folder.

The default posture is to cut bloat — code summaries, derivable facts, stale
references. But an audit should leave context-db sharper, not just smaller.
Preserve details that carry real knowledge the next agent would miss.

Do not run /context-db maintain yourself. The user invokes this.
