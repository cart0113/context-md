# Sub-Agents

> [!note] Work in progress. The sub-agent dispatch path is functional but still
> being tuned. Defaults remain `main-agent` until the patterns stabilize.

Every sub-command can run in two modes, set per-command in `.context-db.json`:

- **main-agent** — the prompt is delivered to the agent currently in the
  conversation. The agent navigates context-db itself and applies what it finds.
- **sub-agent** — the dispatcher spawns a separate agent process, hands it the
  prompt and navigation constraints, captures its findings, and returns those
  findings to the main agent as context.

Sub-agent mode exists because navigating a knowledge base is mostly a filtering
task — read descriptions, decide what's relevant, fetch a few files. That work
is well-suited to a cheaper model like `haiku`. The main agent (typically
`sonnet` or `opus`) doesn't spend turns on navigation; it gets a curated set of
context delivered in one shot.

## Per-command configuration

```jsonc
{
  "defaults": { "mode": "main-agent", "model": "haiku" },

  "prompt": { "mode": "sub-agent", "model": "haiku" },
  "review": { "mode": "sub-agent", "model": "sonnet" },
}
```

Read commands (`prompt`, `pre-review`, `review`) are the strongest sub-agent
candidates — they read but don't write. Write commands (`update`, `maintain`)
must run in `main-agent` mode because they need to edit files in the active
working tree. The dispatcher pins them there.

## What the main agent receives

A sub-agent invocation returns a prefixed block:

```
# Context Usage

context-db is a starting point ... not a complete picture.

# Findings

(The sub-agent's relevant excerpts and pointers.)

# Interpreting * Response

(Reminder that the findings are additional context, not a directive.)
```

The framing is deliberate: the response is "additional context," not advice from
a junior to a senior. The main agent decides what to do with it.

## Implementation notes

- Sub-agent prompts are tuned hardest for `haiku`, where structured output and
  positive-first role framing matter most. Larger models work too but are
  over-constrained.
- Review sub-agents need broader tool access (Read plus Bash for `git diff`)
  than lookup sub-agents (Read only). The dispatcher applies the right
  constraints per command.
- Sub-agent output passes through the main agent before it's acted on, which
  adds a turn. For very small lookups this can be more expensive than letting
  the main agent navigate directly. Profile before turning it on globally.

## Platform support

Sub-agent dispatch is currently implemented for Claude Code, where the
dispatcher spawns a `claude -p` subprocess with constrained tools and streams
the result back. Other agents will need their own spawn mechanism. Until then,
leave `mode` set to `main-agent` on those platforms — the script will run the
same prompt template inline.
