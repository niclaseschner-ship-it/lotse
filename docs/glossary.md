# Glossary — house terms → industry terms

Lotse grew inside a real project, so its vocabulary did too. This table maps the
house terms to the vocabulary the spec-driven / agent-harness community uses.

**Markers:** `≡` means the concepts are equivalent · `≈` means analogy — the
mapping is our reading, not an established equation.

| House term | | Industry term | What it is |
|---|---|---|---|
| **RAT** / ratification ledger (`decisions/`) | ≡ | **Architecture Decision Records (ADR)** with a **no-relitigation policy** | Every ratified decision is a numbered, immutable record; autonomous runs must grep the ledger before reopening a settled question. |
| **constitution** (`specs/constitution.md`) | ≡ | **Project constitution** (as in spec-kit) | A short principles layer above all specs — what always holds, regardless of feature. |
| **Spec anchors** / requirement IDs | ≡ | **Spec-driven development**, traceable requirements | Behavior changes ship with their spec change in the same PR; every requirement carries a stable ID with a test anchor. |
| **Werft** (gates A/B/C) | ≈ | **Spec intake workflow** with human approval gates | Takes a raw idea to a build-ready ticket; a human approves at fixed gates (compare spec-kit's specify → plan → tasks). |
| **prep** + **Stempel** (`status:ready`) | ≡ | **Definition of Ready** + human-in-the-loop approval gate | Tickets mature until a human — never the agent — stamps them ready to build. |
| **arbeitstag** (worktrees, disjoint scopes) | ≡ | **Parallel multi-agent orchestration** with worktree isolation | Many build agents in parallel, each locked to disjoint file scopes, coordinated by claims. |
| **Watchdog** / render gate | ≡ | **Automated verification loop** | Independent review agents check drift and quality against the specs before merge — deterministic checks first. |
| **Antiberater** | ≡ | **Adversarial review / cross-model red-teaming** | A second model is briefed to *refute* the advisor's proposal or find the condition under which it breaks. |
| **Contracts + hooks** | ≈ | **Harness engineering** | Machine-checkable prompt contracts, enforced by deterministic hooks — guardrails as mechanism, not prose. |
| **Drei Schwäne** (three swans) | ≈ | **Triple-loop learning** / second-order observation | Three altitudes at once: doing, watching the doer, watching the watcher. Analogy only — the three-level image follows Bernd Schmid's »The Third Swan« (isb Wiesloch), and mapping it onto learning-loop theory is our own reading. |

If you know one column, you know the other. The German names stay — they are the
API of the framework — but nothing behind them is exotic: it is spec-driven
development plus harness engineering, run in production since mid-2026.
