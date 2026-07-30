# Setup — adopting Lotse in a fresh project

*(This guide is in English — it is the on-ramp for newcomers. The framework's
content itself is German; see [`README.md`](README.md).)*

Lotse is not a standalone app you run. It is a **layer of discipline** you deploy
onto an AI coding agent (the reference harness is Claude Code) and point at *your*
project. This guide gets a project that has **never seen xbuddy** from zero to a
working pipeline.

> **Honest expectation:** Lotse gives you the *method* — commands, adversarial
> review roles, guard hooks, machine-readable contracts. It assumes your project
> brings a few things (a GitHub repo, a small set of labels, a couple of CI
> workflows, and a place for specs/decisions). This guide ships templates for all
> of them. Budget ~30 minutes for a first adoption.

## Prerequisites

- **An agent harness that reads `~/.claude/`** (reference: [Claude Code](https://claude.com/claude-code)). The commands are Markdown "slash commands"; the hooks are Python guard scripts wired into the harness settings.
- **`git`** and the **[`gh` CLI](https://cli.github.com/), authenticated** (`gh auth status`).
- **Python 3.11+** (the hooks are dependency-free stdlib).
- **A GitHub repo for your project**, where your work lives as Issues + PRs.

## Step 1 — Get Lotse and deploy the glue

```bash
git clone https://github.com/niclaseschner-ship-it/lotse.git
cd lotse
./deploy.sh          # copies commands/ agents/ contracts/ hooks/ → ~/.claude/
```

`deploy.sh` mirrors the four glue folders into your harness runtime (`~/.claude/`).
Re-run it after every `git pull`. `--dry-run` previews, `--verify-only` checks drift.

## Step 2 — Set the environment variables (required)

The commands and hooks reference your project through env vars. Set them in your
shell profile (or your harness's env). **These are required — without them the
`git`/`gh` calls inside the commands have no target.**

```bash
export LOTSE_PROJECT_ROOT="$HOME/code/my-project"     # your project's checkout
export LOTSE_PROJECT_REPO="my-org/my-project"          # its GitHub slug (owner/repo)
export LOTSE_PROCESS_REPO="my-org/my-project-process"  # optional: separate process-ticket repo
export LOTSE_SCRATCH="$HOME/lotse-scratch"             # drafts & round notes
# CLAUDE_HOME defaults to ~/.claude — override only if your harness differs.
```

## Step 3 — Give your project the scaffold Lotse expects

Lotse orchestrates a project that carries its own **specs, decisions, and
conventions**. Starter templates are in [`templates/`](templates/):

```bash
cd "$LOTSE_PROJECT_ROOT"
mkdir -p specs decisions conventions
cp /path/to/lotse/templates/constitution.md specs/constitution.md   # then edit it
# specs/      — one spec per component (behaviour = source of truth)
# decisions/  — your ratification ledger (one file per ratified decision)
# conventions/— cross-cutting rules, one home per rule
```

See [`templates/README.md`](templates/README.md) for what each folder is for.
These do not have to be perfect on day one — Lotse fills them as you work.

## Step 4 — Create the GitHub labels

The status lifecycle runs on labels. Create them once:

```bash
/path/to/lotse/bootstrap/create-labels.sh "$LOTSE_PROJECT_REPO"
```

## Step 5 — Install the CI workflows (the automation half)

The commands *read* labels; the workflows in [`workflows/`](workflows/) *flip* them
as PRs move. Copy the ones you want into your project's `.github/workflows/`:

```bash
cp /path/to/lotse/workflows/ticket-status-flow.yml "$LOTSE_PROJECT_ROOT/.github/workflows/"
cp /path/to/lotse/workflows/ticket-defaults.yml     "$LOTSE_PROJECT_ROOT/.github/workflows/"
```

Each template notes what it does and what to adapt (e.g. `runs-on`).

## Step 6 — Wire the hooks into your harness

[`settings.fragment.json`](settings.fragment.json) shows how the guard hooks hang
off `PreToolUse`/`PostToolUse`. Merge that `hooks` block into your
`~/.claude/settings.json` (which stays machine-local).

## Step 7 — First run

```
/berater-runde     # one architecture round on a real question
/werft             # carry an idea to a hand-off-ready ticket
```

---

## What Lotse assumes about your project (the honest list)

- Work is tracked as **GitHub Issues**, changes as **PRs** that say `Closes #<n>`.
- Issues move through a **status label lifecycle** (`status:spec → ready →
  in-progress → in-review`), flipped by the shipped workflows.
- Your project has a **specs / decisions / conventions** structure (templates provided).
- The human is the only one who stamps `status:ready` — that is by design.

## Reference-project material (adapt or ignore)

Some content is battle-tested *against a real project (xbuddy)* and carries its
vocabulary — you are meant to replace it with your own:

- Cross-references like `RAT-N` (ledger) / `PW-N` (process tickets) in command and
  agent text are **examples**, not requirements.
- `hooks/restart_pending_log.py` is **reference ops** (it maps changed paths to
  systemd services after a pull). It is project-specific; adapt it to your deploy
  model or leave it out of your settings wiring.
