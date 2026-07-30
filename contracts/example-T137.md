# Beispiel-Durchlauf — T137 Wetter-Routing

Ein **vollständiger** Contract-First-Durchlauf an einem realen offenen Thema
(siehe Memory `project_xbuddy_wetter_v1`: Wetter-Buddy V1 läuft auf :5030,
Integration ins Routing+Controller ist offen, Issue #137).

> **Hinweis:** Dieses Beispiel zeigt die **unverkürzte** Form aller
> Felder zum besseren Verständnis. Im Live-Betrieb mit Schichten-Caching
> wandern die generischen Teile (Standard-Stop-Rules, Setup-Reflex,
> Checkpoint-Feld-Vorlagen, Standard-Convention-Block S1.5) in
> **Schicht 1** und werden im Track-Contract nur referenziert
> (`siehe Schicht 1 S1.x`). Optional-Felder wie `dependencies`,
> `notes_for_day_close`, `open_questions` etc. werden weggelassen
> wenn leer. Pro Live-Track erwartete YAML-Größe: ~1.5–2.5K Tokens
> statt der hier gezeigten ~5K. Disziplin bleibt identisch — nur die
> Wiederholungen entfallen.

> Inhalte sind illustrativ — IDs und Texte spiegeln plausible Specs/
> Conventions wider, sind aber als Schaubild zu lesen, nicht als
> verbindlicher PR-Inhalt.

---

## Phase [1] — Ticket Contract

Orchestrator liest Issue #137 (Wetter-Routing in Controller integrieren),
`specs/buddies/wetter.md`, `specs/platform/router.md`,
`conventions/ports.md`, `conventions/urls.md`. Füllt:

```yaml
contract_kind: ticket
contract_id: T137
issue: 137
title: "Wetter-Routing in Controller integrieren (#137)"

mission: |
  Wetter-V1 (:5030) über Controller-Routing erreichbar machen,
  damit das Tablet ohne Direktzugriff darauf zugreift.

requirement_ids: [ROU-15, WET-3]
spec_files:
  - specs/buddies/wetter.md
  - specs/platform/router.md
conventions: [PORT-2, URL-3]

vertical_slice:
  trigger: "Nic öffnet auf dem Tablet die Kachel 'Wetter'"
  observable: "Wochenwetter erscheint, geroutet über Controller, nicht direkt :5030"

scope:
  in_scope:
    - "router/routes.json um Wetter-Eintrag erweitern (Buddy → :5030)"
    - "Smoke-Test, der /wetter über die Router-Adresse trifft"
    - "specs/platform/router.md ROU-15 mit #137 annotieren"
  out_of_scope:
    - "Kachel-App im Controller (#138 — Eltern-Chat-Skill 'Apps einbinden')"
    - "nginx-Mapping (separater Deploy-Track, kein Code-Change)"
    - "Wetter-Cache-Layer (kein Issue, kein Bedarf nachgewiesen)"

acceptance_criteria:
  - id: AC1
    text: "Eintrag für Wetter in router/routes.json sichtbar und konform zu PORT-2 / URL-3"
    evidence_hint: "router/routes.json:<line> + grep nach PORT-2-Form"
  - id: AC2
    text: "Live-Probe: GET /wetter via Router-Adresse liefert 200 + Wochenansicht-Marker"
    evidence_hint: "Integration-Test gegen Router (nicht direkt :5030); curl-Smoke nach Deploy"
  - id: AC3
    text: "ROU-15 in specs/platform/router.md trägt Annotation #137"
    evidence_hint: "git diff specs/platform/router.md zeigt '#137' an ROU-15"

# Track ändert HTTP-Routing → Entry-Path-Probe Pflicht.
entry_path_probe:
  required: true
  reason: "Routing-Diff: ohne Probe auf echtem Router-Pfad wäre Tests-Grün nicht aussagekräftig (Helper-Probe würde reichen, Live-Pfad nicht)."
  spec_source:
    requirement_ids: [ROU-15, WET-3]
    acceptance_criteria: [AC2]
  expected_entry_point: "GET /wetter via Router (öffentlicher Pfad, nicht :5030 direkt)"
  expected_observable: "200 + Wochenansicht-HTML auf der Router-Adresse"

dependencies:
  blocks: []
  blocked_by: []
  related: [138]                       # #138 Apps-Kachel-Skill — out of scope

risk_class: low

model_choice:
  default_agent: sonnet
  reason: "Folge-Track entlang etablierter Vorlagen (PORT-2/URL-3), keine neue Konvention nötig."
  escalate_to_opus_if:
    - "Routes.json-Schema-Anpassung würde nötig (dann ist es kein Folge-Track mehr)"

cited_rules:
  - id: PORT-2
    file: conventions/ports.md
    excerpt: "Buddies binden auf 50NN; Router mapped öffentliche Pfade auf interne 50NN-Ports."
  - id: URL-3
    file: conventions/urls.md
    excerpt: "Buddy-Pfade folgen /<buddy-name> ohne API-Präfix."
  - id: ROU-15
    file: specs/platform/router.md
    excerpt: "Routen werden ausschließlich in router/routes.json gepflegt; Code lädt, ändert nicht."

missing_required_context: []
notes_for_day_close:
  - "Cache-Diskussion vertagt, kein Folge-Ticket — erst bei konkretem Schmerz."
```

Orchestrator postet das via:

```bash
gh issue comment 137 --body-file <(cat <<'YAML'
... obiger YAML-Block ...
YAML
)
```

---

## Preflight §A

- §A.1 ✅ — `mission` 1 Satz; `cited_rules` per grep verifiziert;
  `vertical_slice.observable` ist Tablet-Beobachtung; `missing_required_context: []`.
- §A.2 ✅ — Shared-Root clean, `feature/137-wetter-routing` ist neu.
- §A.3 ✅ — Sonnet-Default, Begründung trägt.
- §A.4 ✅ — `grep -r "PORT-2" conventions/ports.md` findet IDs; ROU-15 in
  router.md; WET-3 in wetter.md.

Preflight grün → Sub-Agent Contract bauen.

---

## Phase [3] — Sub-Agent Contract

```yaml
contract_kind: subagent
contract_id: T137-S1
parent_ticket: T137

mission: |
  Wetter-V1 (:5030) über Controller-Routing erreichbar machen,
  damit das Tablet ohne Direktzugriff darauf zugreift.

scope:
  write_allowed_files:
    - router/routes.json
    - tests/test_router.py
    - specs/platform/router.md
  read_context_files:
    - router/main.py            # Stil-/Pattern-Referenz
    - specs/buddies/wetter.md   # WET-3 verifizieren
    - conventions/ports.md      # PORT-2-Form prüfen
    - conventions/urls.md       # URL-3-Form prüfen
  forbidden_files:
    - controller/**
    - deploy/nginx/**
    - wetter/**
  out_of_scope:
    - "Kachel-App im Controller (#138)"
    - "nginx-Mapping (separater Deploy-Track)"
    - "Wetter-Cache-Layer"

cited_specs:
  - id: ROU-15
    file: specs/platform/router.md
    excerpt: "Routen werden ausschließlich in router/routes.json gepflegt; Code lädt, ändert nicht."
  - id: WET-3
    file: specs/buddies/wetter.md
    excerpt: "Wetter-V1 lauscht auf 5030; öffentlich erreichbar via /wetter."

cited_conventions:
  - id: PORT-2
    file: conventions/ports.md
    excerpt: "Buddies binden auf 50NN; Router mapped öffentliche Pfade auf interne 50NN-Ports."
  - id: URL-3
    file: conventions/urls.md
    excerpt: "Buddy-Pfade folgen /<buddy-name> ohne API-Präfix."

acceptance_criteria:
  - id: AC1
    text: "Eintrag für Wetter in router/routes.json sichtbar und konform zu PORT-2 / URL-3"
    evidence_hint: "router/routes.json:<line> + grep nach PORT-2-Form"
  - id: AC2
    text: "pytest test_router_wetter liefert 200 + Wochenansicht-Marker"
    evidence_hint: "pytest tests/test_router.py::test_wetter_route_200 PASS"
  - id: AC3
    text: "ROU-15 in specs/platform/router.md trägt Annotation #137"
    evidence_hint: "git diff specs/platform/router.md zeigt '#137' an ROU-15"

stop_rules:
  - "Edit/Write außerhalb write_allowed_files → STOP (scope_breach). Lesen aus read_context_files ist erlaubt; Edit darin ist scope_breach."
  - "ROU-15/WET-3/PORT-2/URL-3 würde verletzt → STOP (spec_violation)."
  - "AC in >5 Schritten → STOP (acceptance_not_reachable)."
  - "Worktree-Setup-Reflex zeigt Shared-Root → STOP (wrong_worktree)."
  - "Neue Convention nötig → STOP (convention_needed)."

related_echo_anchors:
  - "specs/buddies/wetter.md WET-3"
  - "conventions/urls.md URL-3"
  - "conventions/ports.md PORT-2"

expected_steps: "3–5 Schritte, je 1 Zeile, im Handoff dokumentieren"

# risk_class: low → mode combined: ein kompakter Checkpoint im Handoff.
programmer_execution_protocol:
  mode: combined
  required_checkpoints:
    - id: analysis_plan
      fields: [files_inspected, task_understanding, planned_files_to_change,
               planned_tests, local_style_observed, risks_or_unknowns,
               needs_escalation]
    - id: implementation_done
      fields: [files_changed, deviations_from_plan, scope_still_respected,
               needs_escalation]
    - id: validation_handoff
      fields: [tests_run, test_results, acceptance_criteria_status,
               ready_for_watchdog]
  rules:
    - "needs_escalation=true → sofort STOP."
    - "planned_files_to_change ⊄ write_allowed_files → STOP (scope_breach)."

operational:
  worktree_required: true
  shared_root: ${LOTSE_PROJECT_ROOT}
  branch_name: feature/137-wetter-routing
  base: main
  setup_reflex: |
    pwd && git rev-parse --show-toplevel
  test_command: "pytest tests/test_router.py -k wetter"

expected_handoff:
  schema: contracts/schemas.md §3
  required_fields: [status, steps, checkpoints, files_changed,
                    outside_whitelist_attempted, acceptance_criteria_met,
                    related_echoes_checked, watchdog_hints,
                    worktree_path, branch]

model: sonnet
```

Orchestrator dispatcht via `Agent`-Tool, `subagent_type: general-purpose`,
`model: "sonnet"`, `isolation: "worktree"`, `run_in_background: true`.

---

## Phase [5] — Handoff vom Subagenten

```yaml
contract_kind: handoff
contract_id: T137-S1
parent_ticket: T137

status: completed
stop_reason: null

steps:
  - "Specs/Conventions gelesen: ROU-15, WET-3, PORT-2, URL-3"
  - "router/routes.json um Eintrag {path: '/wetter', port: 5030, buddy: 'wetter'} erweitert"
  - "tests/test_router.py::test_wetter_route_200 ergänzt; pytest grün"
  - "specs/platform/router.md ROU-15 mit Annotation #137 versehen"

# Mode: combined → ein kompakter Checkpoint-Block
checkpoints:
  combined:
    task_understanding: "Wetter-Route in routes.json eintragen, Spec annotieren, Test."
    files_inspected: [router/routes.json, router/main.py, specs/platform/router.md,
                      specs/buddies/wetter.md, conventions/ports.md, conventions/urls.md]
    planned_files_to_change: [router/routes.json, tests/test_router.py, specs/platform/router.md]
    files_changed: [router/routes.json, tests/test_router.py, specs/platform/router.md]
    deviations_from_plan: []
    scope_still_respected: true
    tests_run: ["pytest tests/test_router.py -k wetter"]
    test_results: "1 passed, 0 failed"
    acceptance_criteria_status: "AC1/AC2/AC3 alle met"
    ready_for_watchdog: true
    needs_escalation: false

local_style_observed:
  files_sampled: [router/main.py, router/health.py, tests/test_health.py]
  naming: "snake_case, Modul-Präfix bei öffentlichen Funktionen"
  imports: "absolute Imports"
  error_handling: "FastAPI HTTPException, kein silent except"
  logging: "structlog, key=value"
  test_pattern: "pytest mit FastAPI TestClient"
  service_or_component_pattern: "FastAPI-Router, routes.json als Daten-Quelle"
  inconsistencies_found: []

worktree_path: ~/.claude/worktrees/agent-7f3a
branch: feature/137-wetter-routing

files_changed:
  - router/routes.json
  - tests/test_router.py
  - specs/platform/router.md

outside_whitelist_attempted: []

acceptance_criteria_met:
  - id: AC1
    met: true
    evidence: "router/routes.json:14 — Wetter-Eintrag PORT-2-konform (5030)"
  - id: AC2
    met: true
    evidence: "tests/test_router.py::test_wetter_route_200 PASS — TestClient gegen Router-App, nicht gegen :5030 direkt (Integration-Test über Router-Dispatch)"
  - id: AC3
    met: true
    evidence: "specs/platform/router.md:42 — '#137' an ROU-15 ergänzt"

entry_path_probe_result:
  status: probed
  entry_point: "GET /wetter via Router-FastAPI-App (TestClient simuliert öffentlichen Pfad)"
  evidence: "tests/test_router.py::test_wetter_route_200 — Request über Router-App-Instance, Response.status_code == 200, Response.text enthält 'Wochenansicht'"
  reason: null

spec_touches:
  - file: specs/platform/router.md
    requirement: ROU-15
    change: "Ticket-Annotation #137 angefügt; Verhalten unverändert"

convention_touches: []

related_echoes_checked:
  - anchor: "specs/buddies/wetter.md WET-3"
    finding: "konsistent — WET-3 nennt /wetter als öffentlichen Pfad; jetzt erfüllt durch Router-Eintrag"
  - anchor: "conventions/urls.md URL-3"
    finding: "konsistent — /wetter folgt der /<buddy-name>-Form"
  - anchor: "conventions/ports.md PORT-2"
    finding: "konsistent — 5030 ist 50NN, Router mapped intern; PORT-2 erfüllt"

open_questions: []

risks_noticed:
  - "Wetter-Buddy hat keinen Health-Endpoint — falls Router das später erwartet, wird das ein eigenes Ticket (kein Blocker hier)."

watchdog_hints:
  lenses_relevant: [1, 6]
  lenses_not_applicable: [2, 3, 4, 5]
  diff_summary: |
    router/routes.json: +1 Eintrag (5 Zeilen)
    specs/platform/router.md: +Annotation (1 Zeile)
    tests/test_router.py: +1 Test (14 Zeilen)
```

---

## Phase [6] — Orchestrator Review (Preflight §B)

- §B.1 ✅ — Handoff-Block vorhanden, `contract_id` matched, `status: completed`.
- §B.2 ✅ — `steps` 4 Zeilen, alle Pflichtfelder gesetzt, `acceptance_criteria_met`
  deckt AC1/AC2/AC3, alle drei `related_echo_anchors` adressiert.
- §B.3/B.4 ✅ — Diff-Prüfung mit merge-base-Form:
  `git -C ~/.claude/worktrees/agent-7f3a diff --name-only origin/main...feature/137-wetter-routing`
  liefert genau die drei Pfade aus `write_allowed_files`;
  `outside_whitelist_attempted: []`; Worktree-Pfad ist nicht Shared-Root.
- §B.4 ✅ — alle ACs mit konkretem Evidence-Verweis, Spec-Annotation #137
  im Diff verifizierbar, Echos je mit Begründung.
- §B.5 entfällt (Status `completed`).

Review grün. Risiko „Health-Endpoint fehlt" wandert als Folge-Beobachtung in
die Tagesbilanz, kein neues Ticket heute (es ist noch kein konkreter Schmerz).

---

## Phase [7] — Watchdog-Ready Summary

```yaml
contract_kind: watchdog_summary
contract_id: T137-S1-W
parent_ticket: T137
pr: <pr-nr-sobald-eröffnet>
branch: feature/137-wetter-routing

diff_scope:
  files: [router/routes.json, specs/platform/router.md, tests/test_router.py]
  loc_added: 20
  loc_removed: 0

specs_touched: [ROU-15, WET-3]
conventions_touched: [PORT-2, URL-3]

lenses_requested:
  - id: 1
    name: spec-drift
    reason: "ROU-15 berührt; Test deckt; prüfen, ob Spec-Text konsistent zu Diff-Verhalten."
  - id: 6
    name: genre-drift
    reason: "Mehrere Convention-IDs zitiert; prüfen, dass keine Bauregel-Aussage in die Spec rutscht."
  - id: 7
    name: entry-path-coverage
    reason: "HTTP-Routing geändert; prüfen, dass AC2 wirklich über Router-Dispatch probt und nicht nur einen Helper trifft."

lenses_skipped:
  - id: 2
    reason: "PR-scoped; Diff bäckt keine neue Family-1-Annahme ein (Buddy-Name als Daten, kein hartcodierter Pi-Pfad)."
  - id: 3
    reason: "Keine neuen Singletons / globalen Zugriffe."
  - id: 4
    reason: "Diff trivial (1 JSON-Eintrag, 1 Annotation, 1 Test) — keine neue Komplexität."
  - id: 5
    reason: "Routes-Eintrag bestätigt bestehende Konvention, baut keine neue Sorte."

acceptance_evidence:
  - id: AC1
    state: met
    evidence: "router/routes.json:14"
  - id: AC2
    state: met
    evidence: "pytest tests/test_router.py::test_wetter_route_200 PASS"
  - id: AC3
    state: met
    evidence: "specs/platform/router.md:42 '#137' an ROU-15"

risks: ["Wetter-Buddy ohne Health-Endpoint — Folge-Beobachtung, kein Blocker."]
echo_check:
  - "specs/buddies/wetter.md WET-3 konsistent"
  - "conventions/urls.md URL-3 konsistent"
  - "conventions/ports.md PORT-2 konsistent"

orchestrator_caveats: []
```

Orchestrator ruft den Watchdog mit `branch:feature/137-wetter-routing` auf,
hängt die Summary an den Prompt und nennt die Linsen [1, 6] explizit.

---

## Phase [8] — Merge-Gate

Unverändert zu `arbeitstag.md` Merge-Gate:

1. Watchdog → Verdikt PASS (klein/gesund) erwartet.
2. Pre-merge-Dry-Run: `git merge-tree origin/main HEAD`.
3. Whitelist-Check (im Handoff bereits validiert, hier nur Doppelprüfung).
4. Merge auf `main`.
5. Andere Live-Tracks rebasen.
6. Smoke-Test am Pi (Deploy-Schritt, siehe arbeitstag.md „AM ENDE").

---

## Was dieser Beispiel-Lauf zeigt

- **Vor dem Subagent steht kein „Prompt-Bau", sondern ein Kontrakt.** Der
  Subagent-Prompt fällt aus dem Sub-Agent Contract heraus.
- **`missing_required_context` ist die einzige legitime Stelle für „weiß
  ich nicht".** Alles andere ist zitiert.
- **Der Handoff ist maschinen-validierbar.** Der Orchestrator muss am Ende
  nicht aus dem Diff rückwärts rekonstruieren, ob AC2 erfüllt war.
- **Watchdog-Linsen sind diff-basiert begründet.** Vier von sieben Linsen
  laufen hier nicht — das spart Tokens und macht den Bericht ehrlich.
  Linse 7 (Entry-Path Coverage) ist mit dabei, weil HTTP-Routing geändert wird.
- **Folge-Beobachtung (Health-Endpoint) bleibt Beobachtung, nicht Reflex-
  Ticket.** Genau die Disziplin aus `feedback_folge_tickets_bremsen`.
