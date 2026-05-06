---
description:
  Instructions the agent must read once per session at startup. Orienting
  content — project identity, hard invariants, workflow entry points.
  Substantive is OK; this only fires once per session.
---

# On Start — Benjis

Benjis is Andrew's personal financial planning toolkit. Four goals (see
`project-goals.md`): track Fidelity, plot net worth, measure burn rate, project
retirement.

## Hard invariants (don't break)

1. **Performance must be Time-Weighted.** Cash flows are not returns. See
   `pipeline-pitfalls.md` and `CONTEXT.md`.
2. **Never commit `private/`, `statements/`, or `output/`.** All gitignored. See
   `private-balances.md`.
3. **Rebuild the DB from zero every run.** `python-main run_analysis.py` deletes
   `output/fidelity.db` first. Pipeline is fast and idempotent — never patch the
   DB in place.
4. **All manually-reported balances are stored in thousands** (1495 = $1.495M).

## How to actually do work

- New data dropped in `~/Downloads/`? Move + rename per `data-downloads.md`,
  then re-run.
- Burn-rate numbers wrong? Read `burn-rate-classifier.md` and tune the pattern
  lists.
- Architecture question? Start with `pipeline-architecture.md`.
- Need data the user hasn't given? Just ask — see `asking-for-data.md`.

## Standing rebalance preferences

- Cash target: **~$10K SPAXX in each Fidelity self-directed account**, no more.
  Andrew explicitly chose this over the strategy-doc 10% cash buffer.
- Equity allocation: **Growth profile** (60% US / 30% International). With cash
  forced to ~$10K (~3%), the equity portion is split 2:1 to maintain the 60/30
  ratio.
- **Eliminate active funds first** when raising cash (FSPTX, FBGRX, etc.). Index
  zero-expense funds (FZROX, FZILX) are the long-term core.
- FZIPX overlaps FZROX (small-cap) — sell when convenient to simplify.
- **Use Mutual Fund Exchange** (Trade → Mutual Fund Exchange) for same-account
  swaps. Avoids T+1 cash gap of separate sell-then-buy.
