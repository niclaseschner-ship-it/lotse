---
description: Parallel-Lauf zu /watchdog mit OpenAI Codex (CLI-Default-Modell, read-only) — Vergleichsbericht für die Cross-Engine-Probe.
argument-hint: "[optional: gleicher Scope wie /watchdog — 'PR #NN', 'controller/', 'specs/buddies/plan.md']"
---

# /watchdog-codex — Codex-Variante des Architektur-Wachhunds

Du rufst die OpenAI-Codex-CLI über den Wrapper auf und gibst seinen Bericht
**1:1 weitergeleitet** an Nic zurück. Identischer Brief wie der Claude-
Watchdog (`architecture-watchdog`), nur andere Engine — damit Nic
die Befunde gegeneinander legen kann.

## Aufruf

Starte per Bash:

```bash
~/bin/watchdog-codex.sh "$ARGUMENTS"
```

Der Wrapper:
- lädt den Watchdog-Brief aus `.claude/agents/architecture-watchdog.md`
- ruft Codex (CLI-Default-Modell — kein `-m`-Flag gesetzt) mit `--sandbox read-only` auf
- cwd = `${LOTSE_PROJECT_ROOT}`, `--add-dir` für `xbuddy-knowledge`
- schreibt Bericht nach `brainstorm/watchdog-vergleich/<timestamp>-codex-<slug>.md`
- Run-Log daneben als `.log`

Scope-Logik ist identisch zu `/watchdog`:
- Kein Argument: ganzes Repo, Linsen 1/2/5 priorisiert.
- Argument: konzentrieren auf Scope, Spec-Bezug für angrenzende Bereiche.

## Nach Rückkehr

- Lies die Reportdatei (Pfad steht in der letzten stdout-Zeile des Wrappers)
  per `Read` und gib den Inhalt ungekürzt an Nic aus.
- **Nicht** umformulieren, ergänzen oder weglassen.
- Bei Fehler: Log-Datei zeigen, nicht „best effort"-improvisieren.

## Disziplin

- Du kommentierst nicht, wie Codex sich gegenüber Claude schlägt. Den
  Vergleich macht Nic.
- Sandbox ist `read-only` — Codex kann nichts ins Repo schreiben. Du auch
  nicht im Anschluss; Folge-Aktionen sind separater Auftrag.
- Nur xbuddy-Code ist im Scope. Buddyboard*/workspace/brainstorm bleiben
  unberührt (außer dem Vergleichs-Ordner für Reports).
- Nummern (Issues/PRs/Requirement-IDs) immer mit kurzer Überschrift
  zitieren — gilt nur, falls du beim Weiterreichen eigene Sätze schreibst.
  Codex-Output bleibt 1:1.
