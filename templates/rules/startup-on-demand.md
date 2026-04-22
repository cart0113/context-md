This project uses a `context-db/` knowledge base — a hierarchical Markdown
repository of conventions, standards, design decisions, and pitfalls.

On session startup, run `/context-db load-startup-rule` and follow its output.
It inlines any content the project marks as always-load and gives you the
mechanics for reading context-db when you need more.

Outside of that startup load, do NOT browse or read `context-db/` on your own.
The user will explicitly invoke `/context-db` commands when they want you to
incorporate project knowledge.
