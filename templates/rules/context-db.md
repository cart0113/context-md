On session start, run `/context-db load-on-start-context` and follow its output.

Outside of that on-start load, do not browse or read `context-db/` on your own.
The user invokes `/context-db` commands when they want you to use project
knowledge.

Do not write to or update context-db on your own. Wait for the user to
explicitly run `/context-db update` or `/context-db maintain`. If you think
something belongs in context-db, mention it and let the user decide.
