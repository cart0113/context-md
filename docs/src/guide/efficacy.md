# Efficacy

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems. This
page is the honest version: when context-db helps, when it hurts, and the design
choices that try to keep it on the right side of that line.

## When context engineering hurts

There's a reasonable argument that context engineering hurts more than it helps.
[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found LLM-generated context files reduced task success by ~3% and increased
costs by 20%+. Even human-written files showed only marginal gains. Separately,
[Chroma's context rot research](https://www.trychroma.com/research/context-rot)
demonstrated that every model they tested performed worse as input length grew.

The mechanism is the same in both: agents trust context files, read less actual
code, and amplify whatever drift exists between description and reality. A
context file that says "the auth middleware lives in `auth/middleware.py`" stays
in the agent's head even after that file gets renamed — so the agent edits a
file that no longer exists.

I hit this directly. My first attempt at the od-do `context-db` was 671 lines
across 13 files — code summaries, property lists, module layouts, API
signatures. The agent with verbose context-db spent 30 turns reading
documentation, then wrote code that was missing properties the no-context-db
agent found by reading the actual source. Cost $0.69 vs $0.42 — 64% more
expensive for worse code.

Same story with a flat (non-hierarchical) gemini-cli context-db: $1.35 and 507s
with context-db vs $0.84 and 143s without. Restructuring into a hierarchy with
topic subfolders fixed it. Verbose context-db is worse than no context-db.

## What Anthropic's own memory system says

Claude Code ships with a persistent, file-based memory system. The instructions
Anthropic gives the agent for using it are blunt about what does and doesn't
belong:

> **What NOT to save in memory:** Code patterns, conventions, architecture, file
> paths, or project structure — these can be derived by reading the current
> project state. Git history, recent changes, or who-changed-what — `git log` /
> `git blame` are authoritative. Debugging solutions or fix recipes — the fix is
> in the code; the commit message has the context. Anything already documented
> in CLAUDE.md files.

And on staleness:

> A memory that names a specific function, file, or flag is a claim that it
> existed when the memory was written. It may have been renamed, removed, or
> never merged. Before recommending it: check the file exists, grep for it.

Anthropic's framing: a memory file is **a starting point**, and it carries
**verification debt**. The agent is told to read code first and to treat the
memory record as historical until proven current.

That's the same principle context-db is built on. Every payload context-db emits
opens with this paragraph (`prompts/main-agent/context-usage.md`):

> Context-db is a starting point, a map, a hint — not a complete picture. It
> documents conventions, gotchas, design decisions, and cross-file connections
> that you can't learn from reading any single file.
>
> Use it to orient yourself, then verify against the actual project assets
> (code, configs, docs, etc.). If what you read conflicts with what the project
> shows, trust the project's assets, especially project code.

If the project disagrees with context-db, the project wins. That single
instruction is what protects the agent from following stale context off a cliff.

## Agents forget — even mid-session

Even with a perfect context file at session start, agents drift over long
sessions. Three known mechanisms compound:

1. **Context rot.**
   [Chroma's research](https://www.trychroma.com/research/context-rot) measured
   every frontier model performing worse as input length grew. The degradation
   appeared well below context limits — it's not about running out of room, it's
   about attention spreading thin.
2. **Lost-in-the-middle.** [Liu et al. (2023)](https://arxiv.org/abs/2307.03172)
   showed models attend most to content at the start and end of long contexts
   and undervalue what sits in the middle. Standing instructions placed at
   session start get pushed into the middle as the conversation grows.
3. **Compaction.** When a session approaches the context window, prior turns get
   summarized into a shorter history. The standing instructions and the user's
   earlier corrections often don't survive intact.

The practical effect: a session that starts well drifts by turn 40. The
standards get compacted out, attention dilutes, and the agent reverts to its
training defaults — the generic patterns it knew before it ever saw your
project.

## How context-db responds

The skill is designed around the assumption that the agent will forget. Four
mechanisms push back.

**1. A standing rule that survives compaction.** Every conversation gets a
one-line rule (`templates/rules/context-db.md`):

> On session start, run `/context-db load-start-context` and follow its output.

Rules are re-injected every turn, so they survive compaction. The script
re-emits read-mechanics + context-usage + on_start/on_all every time the agent
runs it. The agent doesn't have to remember any of it — it gets re-told.

**2. Re-anchoring commands for critical prompts.** When you really want
context-db top of mind for the next piece of work, you re-load it explicitly:

- `/context-db prompt` pulls in just the standards relevant to the next task.
- `/context-db pre-review` surfaces them before code is written.
- `/context-db review` audits the diff against them after the fact.

Each is a deliberate moment where the user re-points the agent at conventions,
mid-session, without depending on the agent to remember. The "agent will forget"
assumption is baked into the workflow.

**3. Read instructions push back on context-db.** Every read payload starts with
the "verify against the project's assets" framing above, and includes a
selectivity rule (`prompts/main-agent/read-mechanics.md`):

> Skip files and subfolders whose descriptions don't suggest direct relevance.
> Be selective — reading everything wastes time and dilutes useful context.

This is the ETH Zurich finding turned into a read filter: the agent is told
_not_ to read context-db exhaustively, even when invited to. Less context with
high signal beats more context with noise.

**4. Write instructions are aggressively restrictive.** The update / maintain
templates (`prompts/main-agent/update-general.md`,
`prompts/main-agent/write-content-guide.md`) tell the writing agent the opposite
of what most documentation systems tell it:

> Most sessions produce nothing worth storing — that is the normal outcome, not
> a failure. Every addition dilutes what's already there, so non-critical
> entries actively reduce the system's value.

> Do not persist things derivable from the code — CLI flags, function
> signatures, file layouts. The code is the source of truth for those.

> Update context-db only if you encountered something that would mislead the
> next agent — a non-obvious dependency, a constraint invisible in the project
> assets, a convention the agent wouldn't know, or a correction from the user.

This is the same finding turned into a write filter. Verbose context-dbs grow
because writers feel obligated to capture everything. The instructions tell the
writing agent the opposite. `maintain` reinforces it from the other direction —
a 7-phase audit whose default posture is to **cut**.

## What we measured

Three codebases, the harness in
[git-context-md-tests](https://github.com/cart0113/git-context-md-tests). The
harness runs `claude -p` in two copies of the same codebase (one with
context-db, one without), captures cost/tokens/turns/time from the JSON output,
and resets the source between runs.

The short version: verbose context-db hurts — the ETH Zurich finding is real.
Slim context-db focused on gotchas and checklists consistently helps. Opus is
smart enough to figure most things out by reading the code; context-db just gets
it there faster and with fewer mistakes.

### FastAPI

Well-known Python framework, ~5,000-line core files. Likely in training data,
which makes it a harder test for context-db — the model already knows the
codebase.

The context-db is 182 lines: a file map with section offsets for the huge
`routing.py` and `applications.py` files, gotchas (body embedding, cache keys,
schema caching, scope restrictions), change patterns (the 6-level parameter
threading chain), and design decisions.

**Add an `after_endpoint` hook** — thread a callback through
`APIRoute.__init__()`, `get_route_handler()`, and `get_request_handler()` in
`routing.py`.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.39           | $0.49   | -20%  |
| Time  | 74.2s           | 171.6s  | -57%  |
| Turns | 20              | 16      | +4    |

Both agents found the right locations. The "with" agent handled both sync and
async callbacks, matching the existing `before_endpoint` pattern. The "without"
agent introduced a sync/async bug — bare `await` on what could be a sync
callback. The change-patterns doc was the difference.

**Add `deprecated_message` to OpenAPI** — thread a parameter through
`APIRoute.__init__()` and into OpenAPI generation.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $1.97           | $1.40   | +41%  |
| Time  | 310s            | 214.7s  | +44%  |
| Turns | 60              | 42      | +18   |

The "with" agent cost more but threaded `deprecated_message` through the full
registration chain (decorators, `APIRouter`, `FastAPI` class), making the
feature actually usable from `@app.get(...)`. The "without" agent only wired it
through `APIRoute.__init__()` — technically correct for the prompt, but
inaccessible from the API developers actually use.

**Add `on_dependency_resolved` callback** — same sync/async bug pattern appeared
again. The "with" agent used the `isawaitable` check; the "without" agent used
bare `await`. Across all three FastAPI tests, the context-db agent consistently
matched existing codebase conventions while the no-context agent consistently
introduced the same class of bug.

### Gemini CLI

[google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — 457K
lines of TypeScript, released June 2025. Monorepo with 7 packages. Not in
training data, big enough that navigating blind is expensive.

The context-db is 376 lines across a hierarchical structure: architecture, three
topic-specific subfolders (policy-and-hooks, scheduler, config-and-extensions)
each with gotchas and checklists, and design decisions.

**Add a `ToolTiming` hook event:**

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.84           | $1.05   | -20%  |
| Time  | 127.4s          | 191.6s  | -34%  |
| Turns | 34              | 32      | +2    |

The "with" agent modified 4 files (correct minimum from the checklist) and
correctly skipped `hookPlanner.ts` and `hookAggregator.ts` (default case covers
them). The "without" agent modified 5 files, adding a redundant case that falls
through to the same default handler. Not a bug, but unnecessary code. The
checklist guided the "with" agent to the minimal correct set.

**Add a `ToolBlocked` hook event** — both agents modified the same 4 files and
placed the hook correctly. No quality difference. The gemini-cli codebase is
well-structured enough that the hook patterns are discoverable without
context-db. Honest result: context-db helped less here than on FastAPI's huge
files or od-do's bespoke conventions.

### od-do

[od-do](https://github.com/cart0113/od-do) — a Python diagramming toolkit. Not
in training data. ~180 source files.

The context-db is 143 lines: architecture, a checklist for adding shapes (5
files in order), gotchas, and drawio adaptation notes.

**Add a `DashedBorder` shape:**

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.49           | $0.56   | -13%  |
| Time  | 94.7s           | 201.9s  | -53%  |
| Turns | 26              | 15      | +11   |

The "with" agent inherited from `Shape` (getting `bbox`, `points`, `fill_color`,
etc. for free), exported correctly, and placed the isinstance dispatch after
existing shapes. The "without" agent wrote a standalone class, reimplemented
properties manually, used the wrong export pattern, and missed four properties.
The checklist told the "with" agent exactly which properties were required and
which files to touch.

## What works

1. **Checklists for multi-file changes.** The code shows how each file works.
   context-db shows which files must change _together_. Highest-value content
   type by a wide margin.
2. **Gotchas the code doesn't reveal.** Init ordering traps, naming conventions
   not enforced by the language, past bugs that would recur.
3. **Why, not what.** The code shows what. Only context-db explains why. "Why"
   prevents the agent from undoing intentional decisions.
4. **Nothing else.** No code summaries. No property lists. No module layouts.

The litmus test: if you removed a document, would the agent make a mistake it
wouldn't otherwise make? If not, the document isn't earning its tokens — and
under the ETH Zurich finding, an unearning document is a _negative_-value
document.
