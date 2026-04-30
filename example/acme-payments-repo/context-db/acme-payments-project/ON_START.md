---
description:
  Orientation for agents working on Acme Payments. Inlined once per session at
  startup.
---

# On Start

Acme Payments is a three-tier payment service: API gateway, payment engine, and
an append-only ledger. Inter-service communication is async via message queue.

Before making changes:

- Architecture and API endpoints live under `acme-payments-project/`. Data-model
  conventions are in `acme-payments-project/data-model/`.
- Coding and git standards are shared with sister projects via symlinks
  (`coding-standards/`, `git-standards/`). Treat those as authoritative.
- The ledger is append-only — never write a path that mutates a posted
  transaction. Refunds and reversals are new entries, not edits.
