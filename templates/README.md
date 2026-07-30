# Templates — the scaffold Lotse expects in your project

Lotse orchestrates a project that carries its own **specs, decisions, and
conventions**. The commands and agents read these; you don't need them perfect on
day one, but the folders should exist and grow as you work.

Copy what you need into your project root (`$LOTSE_PROJECT_ROOT`):

| Path | What it is | Who writes it |
|------|-----------|---------------|
| `specs/constitution.md` | The overarching principles every ticket answers to. Start from [`constitution.md`](constitution.md). | You, rarely. |
| `specs/` | One spec per component. **Behaviour is the source of truth** — code implements specs, not the other way round. | `/werft`, you. |
| `decisions/` | Your **ratification ledger**: one file per ratified architecture decision. `/berater-runde` lands here. Re-litigation is checked against it. | `/berater-runde`, you. |
| `conventions/` | Cross-cutting rules, **one home per rule**; other docs reference instead of duplicating. | You, as patterns recur. |

## How they relate to the pipeline

- `/werft` turns an idea into a **spec** + a hand-off-ready ticket.
- `/berater-runde` writes a **decision** into `decisions/` (decide once, don't re-litigate).
- `/arbeitstag-prep` and `/arbeitstag` implement tickets that reference these specs.
- `/watchdog` reviews a diff against the specs + conventions.

## Naming your ledger entries

Lotse's reference project tags ratified decisions `RAT-<n>` and process tickets
`PW-<n>`. Those exact prefixes are **examples** — use whatever scheme you like
(`ADR-<n>`, dates, etc.). What matters is that a decision, once made, has one
stable home you can point back to.
