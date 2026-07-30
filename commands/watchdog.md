---
description: Startet den architecture-watchdog auf den aktuellen Stand des Repos.
argument-hint: "[optional: Scope wie 'PR #NN', 'controller/', 'specs/buddies/plan.md' — leer = ganzes Repo]"
---

# /watchdog — Architektur-Wachhund für xbuddy

Du rufst den Subagenten `architecture-watchdog` auf und gibst seinen
Bericht **1:1 weitergeleitet** an Nic zurück. Du ziehst keine eigenen
Schlüsse und schreibst keine neuen Befunde dazu.

## Aufruf

Starte den Subagenten via `Agent`-Tool mit `subagent_type: "architecture-watchdog"`.

**Hook-Header — Pflicht (PW-39).** Der PW-31-Dispatch-Hook
(`dispatch_status_guard.py`) prüft den Prompt-Text auf `contract_kind:` +
`mode:`. Der Watchdog ist semantisch ein Subagent in Lese-Modus. Setze als
**ersten Block des Prompts**:

- **Stand-alone /watchdog ohne parent_ticket** (Repo-weit oder Branch-Diff
  ohne konkretes Ticket — der Normalfall für diesen Command):
  ```
  <!-- dispatch_status_guard:skip -->
  contract_kind: subagent_no_ticket
  mode: read
  write_allowed_files: []
  ```
  Die Skip-Marker-Zeile muss **die allererste Zeile** des Prompts sein
  (sonst greift der Skip nicht). `subagent_no_ticket` ist der ratifizierte
  no-ticket-Pfad — Mode `read` ist Pflicht, `build` ist auf Skip-Pfaden
  verboten.

- **/arbeitstag-Kontext mit Track-Ticket** (Watchdog auf Track-Branch nach
  Subagent-Rückkehr — siehe `commands/arbeitstag.md`):
  ```
  contract_kind: subagent
  mode: read
  parent_ticket: ${LOTSE_PROJECT_REPO}#<nr>
  write_allowed_files: []
  ```
  Kein Skip-Marker, Standard-Pfad. Das Ticket muss offen und
  `status:in-progress` sein, sonst blockt RAT-15.

**Nicht** `contract_kind: watchdog` — der Wert ist im Hook-Regex
(`dispatch_status_guard.py:45`) nicht zugelassen und führt zu Reject-Schleifen.
Architektonisch ist der Watchdog kein eigener Vertragstyp, sondern ein
Subagent in `mode: read`.

**Scope-Logik:**
- **Kein Argument:** „Schau dir den ganzen Stand von `${LOTSE_PROJECT_ROOT}/` an. Priorisiere Linsen 1 (Spec-Drift), 2 (Familie-3-Probe) und 5 (Lego-Probe). Linsen 3, 4 und 6 nimm mit, soweit sie beim Durchgehen auffallen."
- **Argument vorhanden** (z. B. `PR #89`, `controller/`, `specs/buddies/plan.md`): „Konzentriere dich auf <Scope>, prüfe aber Spec-Bezug auch für angrenzende Bereiche."
- **Argument `branch:<name>`** (z. B. `branch:feat/wetter-routing` — gedacht für den **Merge-Gate-Lauf im Arbeitstag**, vor `git push`/PR): „Scope ist der Diff von `<name>` gegen `origin/main` plus die berührten Specs und Konventionen. Priorisiere Linsen 1 (Spec-Drift) und 6 (Genre-Drift); Linse 2 nur, soweit *dieser Diff* neue Familie-1-Annahmen einbäckt (hartcodierte Pfade/IDs im Diff selbst). Linsen 3, 4, 5 fallen aus — die greifen repo-weit, nicht auf einem PR-Diff." Verifiziere den Diff vor dem Lauf: `git -C ${LOTSE_PROJECT_ROOT} diff --name-only origin/main...<name>`.

**Fallback,** falls der Subagent im Agent-Tool noch nicht im Cache ist
(Fehler „agent type not found"): Starte einmalig `general-purpose` mit
dem vollständigen Watchdog-Prompt inline; beim nächsten Session-Start ist
der reguläre Aufruf wieder möglich.

## Nach Rückkehr des Agenten

- Bericht ungekürzt an Nic ausgeben, im Format das der Agent liefert
  (Verdikt, Befunde, optional „Was gut bleibt").
- **Nicht** Befunde umformulieren, ergänzen oder weglassen.
- Auf Wunsch von Nic einzeln durchgehen, fixen, Ticket anlegen — das
  sind Folge-Aktionen, kein Teil dieses Commands.

## Disziplin

- Du fügst dem Bericht nichts hinzu — auch nicht „eine Sache wäre noch …".
- Wenn der Agent „alles ok" sagt, gib das so wieder. Keine
  Pflicht-Befunde.
- Nummern (Issues/PRs/Requirement-IDs) immer mit kurzer Überschrift
  zitieren (CLAUDE.md §7 im xbuddy-Repo).
- Nur xbuddy-Code ist im Scope. Buddyboard*, Workspace, Brainstorm
  bleiben unberührt.
