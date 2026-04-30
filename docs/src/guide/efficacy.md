# Efficacy

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems.
Agents given context files that describe code state trust those descriptions,
read less actual code, and perform _worse_ when descriptions drift. Yet agents
left with no guidance default to their training and miss every project-specific
constraint. context-db is the attempt to stay on the right side of that line.

## When context engineering hurts

[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found LLM-generated context files reduced task success by ~3% and increased
costs by 20%+. Even hand-written ones showed only marginal gains. Separately,
[Chroma's context-rot research](https://www.trychroma.com/research/context-rot)
showed every frontier model performed worse as input length grew, well below
context limits — attention spreads thin.

The mechanism is the same in both: agents trust the file, read less actual code,
and amplify whatever drift exists between description and reality. A context
file that says "the auth middleware lives in `auth/middleware.py`" stays in the
agent's head after that file gets renamed — so the agent edits a file that no
longer exists.

## What Anthropic's own memory system says

Claude Code ships with a persistent, file-based memory system. The instructions
Anthropic gives the agent for using it are blunt about what does and doesn't
belong:

> **What NOT to save in memory:** Code patterns, conventions, architecture, file
> paths, or project structure — these can be derived by reading the current
> project state. Git history, recent changes, or who-changed-what — `git log` /
> `git blame` are authoritative. Debugging solutions or fix recipes — the fix is
> in the code; the commit message has the context.

And on staleness:

> A memory that names a specific function, file, or flag is a claim that it
> existed when the memory was written. It may have been renamed, removed, or
> never merged. Before recommending it: check the file exists, grep for it.

Anthropic frames the memory file as a **starting point** that carries
**verification debt** — the agent reads code first and treats the record as
historical until proven current. That same framing is what makes context-db
work, and the language is wired directly into the prompts the dispatcher emits.

## How that shaped the prompt language

Every read payload context-db emits opens with this paragraph
(`prompts/main-agent/context-usage.md`):

> Context-db is a starting point, a map, a hint — not a complete picture. It
> documents conventions, gotchas, design decisions, and cross-file connections
> that you can't learn from reading any single file.
>
> Use it to orient yourself, then verify against the actual project assets
> (code, configs, docs, etc.). If what you read conflicts with what the project
> shows, trust the project's assets, especially project code.

If the project disagrees with context-db, the project wins. That single
instruction is what protects the agent from following stale context off a cliff.

The read-mechanics block (`prompts/main-agent/read-mechanics.md`) turns the ETH
Zurich finding into a read filter:

> Skip files and subfolders whose descriptions don't suggest direct relevance.
> Be selective — reading everything wastes time and dilutes useful context.

The agent is told _not_ to read context-db exhaustively, even when invited to.
Less context with high signal beats more context with noise.

The write side is even more restrictive
(`prompts/main-agent/update-general.md`):

> Most sessions produce nothing worth storing — that is the normal outcome, not
> a failure. Every addition dilutes what's already there, so non-critical
> entries actively reduce the system's value.

Verbose context-dbs grow because writers feel obligated to capture everything.
The instructions tell the writing agent the opposite, and `maintain` reinforces
it from the other direction with a multi-phase audit whose default posture is to
**cut**.

## One negative, one positive

Same project, two context-dbs, opposite outcomes. The project: a Python
diagramming toolkit, ~180 source files, not in training data. Task: add a new
shape class.

**Negative — verbose context-db hurts.** A first-pass context-db of 671 lines
across 13 files: code summaries, property lists, module layouts, API signatures.
The verbose-context agent spent 30 turns reading documentation, then wrote code
that was missing properties the no-context agent found by reading the actual
source. Cost $0.69 vs $0.42 — 64% more expensive, for worse code. The context
file became the problem.

**Positive — slim context-db helps.** Cut to 143 lines: architecture, a
five-file checklist for adding shapes, a handful of gotchas. Same task, same
model.

|      | With context-db | Without | Delta |
| ---- | --------------- | ------- | ----- |
| Cost | $0.49           | $0.56   | -13%  |
| Time | 94.7s           | 201.9s  | -53%  |

The context-db agent inherited from `Shape` (getting `bbox`, `points`,
`fill_color`, etc. for free), exported the new shape correctly, and placed the
isinstance dispatch after the existing shapes. The no-context agent wrote a
standalone class, reimplemented properties manually, used the wrong export
pattern, and missed four properties. The checklist told the context-db agent
exactly which properties were required and which files to touch.

The same effect shows up across other tests on FastAPI and gemini-cli: a slim,
gotcha-and-checklist context-db consistently helps; a verbose one consistently
hurts.

## The principle

Contain the gap between what the code shows and what the agent needs to know.
Conventions it wouldn't infer. Pitfalls it will hit. Rationale not visible in
source. Everything else — code summaries, module inventories, restated function
signatures — is noise that displaces code the agent could read instead.

The litmus test: if you removed a document, would the agent make a mistake it
wouldn't otherwise make? If not, the document isn't earning its tokens — and
under the ETH Zurich finding, an unearning document is a _negative_-value
document.
