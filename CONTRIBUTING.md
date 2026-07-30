# Mitarbeit

Diese Methode wird **mit ihren eigenen Regeln** weiterentwickelt — sie ist ihr
erstes Anwendungsbeispiel.

## Grundregeln

- **Plan vor Code.** Substanzielle Änderungen erst skizzieren und bestätigen
  lassen, dann bauen.
- **Eine Quelle pro Regel.** Jede Regel hat genau einen Home; andere Dokumente
  verweisen, statt zu duplizieren (siehe `AGENTS.md` des Referenz-Projekts).
- **Sprache:** Deutsch; etablierte Fachbegriffe (Commit, Spec, Issue, …) englisch.

## Änderungen an der Methode

- **Wortlaut-/Doku-Schärfungen** (Commands, Contracts, README): normaler PR.
- **Architektur-/Design-Änderungen** an der Methode selbst (neue Mechanik, neuer
  Command, geänderter Contract-Vertrag): durch eine **Berater-Runde**
  (`/berater-runde`) — Berater schlägt vor, ein **anderer Kopf/Modell** widerlegt,
  Landung auf MACH ES / NOCH NICHT / ECHTE GABEL. Ergebnis wird ratifiziert
  festgehalten, bevor gebaut wird.
- **Contracts sind ein Vertrag mit Code.** `contracts/schemas.md` und die `hooks/`
  hängen zusammen — Wortlaut/Format eines Contracts nur ändern, wenn der zugehörige
  Hook mitgezogen wird (und umgekehrt).

## Hooks (ausführbares Harness)

Die `hooks/*.py` sind Guard-Hooks des Agent-Harness. Sie haben legitime Laufzeit-
Bindungen (Log-Pfade am Laufzeit-Ort). Vor einer Hook-Änderung: das Verhalten gegen
eine repräsentative Eingabe (stdin-JSON) prüfen — ein Hook, der bei fehlerhafter
Eingabe hart bricht, blockiert jeden Tool-Aufruf.

## PR-Disziplin

- Kleine PRs, ein Thema pro PR.
- Kein toter Code, keine „auf Vorrat"-Anlagen.
- Verhalten ändern → Test/Probe mitliefern, wo es ein Verhalten gibt.

## Referenz-Projekt-Artefakte

Verweise auf `RAT-N` / `PW-N` / `specs/`-Pfade stammen aus dem Referenz-Projekt
(xbuddy) und illustrieren die Methode real. Beim Adaptieren auf ein eigenes Projekt
werden sie durch das eigene Ledger / die eigenen Specs ersetzt — sie sind kein
Bestandteil des Framework-Kerns.
