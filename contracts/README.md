# Contract-First Flow für /arbeitstag

Diese Sammlung definiert den Vertrag zwischen Orchestrator (Opus, `/arbeitstag`)
und Subagenten (Sonnet/Opus, je Track). Sie ersetzt **nicht** die in
`commands/arbeitstag.md` etablierten Mechaniken (Worktree-Isolation,
Datei-Whitelist, Ownership-Tabelle, Merge-Gate, Watchdog auf Diff) — sie macht
ihre Eingaben und Ausgaben explizit.

## Warum überhaupt

In der letzten Retro war der Hauptverlust **Context Drift**: der Orchestrator
musste am Ende jedes Tracks aus Prompt, Diff und Subagent-Bericht zurückrechnen,
was eigentlich beauftragt war. Lösung: vor dem Dispatch einen **expliziten,
ticketnahen Kontrakt** ablegen, gegen den hinterher abgeglichen wird.

## Flow

```
GitHub Issue
   │
   ▼  (bei bestehenden Tickets erst Backfill, siehe §6)
[0] CONTRACT BACKFILL        → schemas.md §6  (nur wenn nötig)
   │   Status: ready_for_execution | needs_orchestrator_review
   │           | needs_PO_decision | blocked_missing_contract
   ▼  (Orchestrator liest Spec, Conventions, Memory)
[1] TICKET CONTRACT          → schemas.md §1
   │                            postet als Issue-Comment via `gh issue comment`
   ▼
[2] OPERATIONAL PREFLIGHT    → preflight.md §A
   │
   ▼
[3] SUB-AGENT CONTRACT       → schemas.md §2
   │   risk_class steuert programmer_execution_protocol.mode:
   │     low → combined, medium → three_compact,
   │     high → three_compact + Re-Dispatch  (PW-8: two_phase DEPRECATED)
   ▼  (Agent-Dispatch, run_in_background, isolation: worktree —
   │   ODER manueller RAT-21-Worktree `t<nr>` ohne isolation, PW-87; Pfad-
   │   Vertrag beider Modi in preflight.md §A.2 / schemas.md S1.2)
[4] SUB-AGENT EXECUTION
   │   3 Checkpoint-Feldgruppen (analysis_plan / implementation_done /
   │   validation_handoff) gestaffelt nach mode; Block-Gliederung empfohlen,
   │   nicht erzwungen (PW-79). Bei high → Phase 1 als eigener Subagent nur mit
   │   analysis_plan, Phase 2 als frischer Subagent mit eingebettetem Plan.
   ▼
[5] STRUCTURED HANDOFF       → schemas.md §3
   │
   ▼  (Orchestrator validiert gegen Contract)
[6] ORCHESTRATOR REVIEW      → preflight.md §B
   │   Mangel: einmaliger Reject + Re-Dispatch. Zweiter Mangel: Halt zu Nic.
   ▼
[7] WATCHDOG-READY SUMMARY   → schemas.md §4
   │   Aus Contracts gespeist (kein Re-Read). Diff-basierte Linsen-Auswahl.
   ▼
[8] MERGE-GATE (unverändert, siehe arbeitstag.md)

Quer dazu:
- Decisions (§5): nur bei blocks_execution=true ins Record-Schema;
  sonst in `## Offene Punkte` der Spec (etablierte Form in xbuddy).
- Sequential Mode (preflight.md §D): nach 2 parallelen Failures.
- Re-Use vor Re-Read: Fix-Tracks zeigen via previous_handoff_id auf
  den vorherigen Lauf, statt Quellen neu zu lesen.
- Entry-Path-Probe: Pflichtfeld im Ticket Contract; bei verhaltens-
  ändernden Tracks Live-Pfad statt Helper-Test. Watchdog-Linse 7
  (Entry-Path Coverage) prüft Begründungen für lower_level / N/A.
- Token-Disziplin (schemas.md SCHICHT 1 + arbeitstag.md
  Schichten-Sektion): Standard-Inhalte in Schicht 1 (cacheable),
  Track-Contract referenziert nur. Tier-Routing mit Haiku als 3. Stufe.
  Cluster-Dispatch zur Cache-Nutzung. Meldungs-Trigger
  (preflight.md §F) wenn Annahmen nicht aufgehen.
```

## Was bewusst weggelassen wurde

- **Keine neue Runtime, kein neues Tool, kein Lock-System.** Der Kontrakt ist
  ein Dokument, das Orchestrator und Subagent gemeinsam lesen.
- **Keine Pflicht-Datei im xbuddy-Repo.** Contracts leben am Issue (Comment)
  bzw. im PR-Body, nicht als drittes Doku-Genre neben `specs/` und
  `conventions/`.
- **Keine generische Validierungs-Library.** Die Validierung ist die Checkliste
  in `preflight.md` §B.
- **Kein ADR-Verzeichnis.** xbuddy hat heute kein ADR-/Decision-Records-Genre.
  Spec-lokale Entscheidungen wandern in die etablierte `## Offene Punkte`-Sektion
  der Spec. Architektur-Decisions sind Halt zu Nic, kein eigenmächtig
  angelegter neuer Ort.
- **Kein Backfill des gesamten Backlogs.** Backfill nur für aktive oder
  unmittelbar geplante Tickets. Bei `blocked_missing_contract` lieber Label
  `blocked` setzen als Stunden recherchieren.
- **Kein eigenmächtiger Ausbau des Engine-Pools.** Codex und andere
  Coding-Engines bleiben „deferred until signal" (vgl. arbeitstag.md
  Modell-Wahl). Bis dahin: Opus = Orchestrator/Watchdog/Architektur,
  Sonnet = Code/Fix/Folge. Kein Verbot, aber kein vorgezogener Ausbau.

## Wiederverwendete Mechaniken

| Mechanik | Lebt in | Bleibt unverändert |
|---|---|---|
| Datei-Ownership-Tabelle | `arbeitstag.md` Phase 0 | ja — füttert jetzt `write_allowed_files` (Konflikt-Prüfung) + `read_context_files` (überschneiden erlaubt) |
| Worktree-Isolation | `arbeitstag.md` Parallelisierungs-Vertrag | ja — `operational.worktree_required` zitiert nur |
| Datei-Whitelist (hart) | `arbeitstag.md` Parallelisierungs-Vertrag | ja — wird im Sub-Agent Contract konkret |
| Merge-Gate + Pre-merge-Dry-Run | `arbeitstag.md` Merge-Gate | ja — Watchdog-Ready Summary speist das Gate |
| Watchdog-Linsen pro Diff | `arbeitstag.md` Merge-Gate Punkt 1 | ja — `watchdog_hints.lenses_relevant` schlägt vor |
| Spec-Halt-Reflex | `feedback_spec_aenderung_ist_halt` | ja — `missing_required_context` zwingt ihn ab Phase [1] |
| Modellwahl Sonnet/Opus | `arbeitstag.md` Modell-Wahl | ja — `model_choice` macht Default + Override-Grund explizit |
