# Contract-Schemas

Sechs YAML-Schemas, eines pro Phase. Felder sind **Pflicht**, außer als
`optional` markiert. Pflicht-Felder dürfen `[]` sein, wenn die leere Liste
etwas aussagt („nichts außerhalb Whitelist", „keine Echo-Verletzung").
Optional-Felder werden bei leerem Inhalt **weggelassen**, nicht als `[]`
geschrieben — das spart Output-Tokens.

Die Schemas sind **Vorlage**, keine Library. Orchestrator und Subagent füllen
sie als Markdown-YAML-Block, der direkt am Issue / im PR-Body lebt.

## Token-Budget — Grundregel über allen Schemas

Contracts sind **knapp**, nicht erschöpfend. Pflicht-Grenzen pro Phase:

| Phase | Spec-Slices | Dateien/Slices | Conventions/Rules | AC | Stop Rules |
|---|---|---|---|---|---|
| Ticket Contract (§1) | max 3 | — | max 10 | max 5 | — |
| Sub-Agent Contract (§2) | max 3 | max 5–8 | max 10 | max 5 | max 3 (zusätzlich zu Standard) |
| Handoff (§3) | nur Touches | nur Changed | nur Touches | alle aus §2 | — |
| Watchdog Summary (§4) | nur Touched | nur Changed | nur Touched | alle aus §2 | — |

Wenn mehr nötig ist: `high_context_track: true` + Begründung. Triggert
Eskalation auf Opus. **Default ist Sonnet (oder Haiku) + knapp.**

**Re-Use vor Re-Read.** Fix-Tracks nach Watchdog referenzieren via
`previous_handoff_id` auf den Vorlauf — kein Neu-Lesen aller Quellen.

---

## SCHICHT 1 — Standard-Inhalte (cacheable)

Diese Sektion ist **track-unabhängig** und wird am Anfang **jedes**
Sub-Agent-Prompts wörtlich mitgeschickt (siehe `arbeitstag.md` →
SUBAGENT-PROMPT-SCHICHTEN). Mit Prompt-Caching (`cache_control: ephemeral`
am Schicht-1-Ende) zahlt der zweite Subagent in derselben Session nur
noch 10% des Input-Preises für diesen Block.

Verweis aus jedem Track-Contract: „Standard aus Schicht 1 — siehe
schemas.md SCHICHT 1". Keine Wiederholung pro Track.

### S1.1 Standard-Stop-Rules

Gelten **immer** für jeden Subagent. Track-spezifische Stop-Rules in §2
nur **zusätzlich** (max 3 extra).

```yaml
standard_stop_rules:
  - id: scope_breach
    rule: "Edit/Write außerhalb write_allowed_files → STOP. Lesen aus read_context_files erlaubt; Edit darin ist scope_breach."
  - id: spec_violation
    rule: "Cited spec/convention würde verletzt → STOP."
  - id: acceptance_not_reachable
    rule: "AC nicht in ≤5 Schritten erreichbar → STOP."
  - id: wrong_worktree
    rule: "Setup-Reflex zeigt nicht-Worktree → STOP."
  - id: convention_needed
    rule: "Neue Bauregel/Konvention wäre nötig → STOP."
  - id: needs_escalation
    rule: "Checkpoint meldet needs_escalation=true → STOP."
```

### S1.2 Setup-Reflex-Template

Der **erste Bash-Call** hängt vom Dispatch-Modus ab (Gabel in `preflight.md §A.2`,
PW-87) — pro Modus genau **ein** zulässiger Erst-Call:

- **Auto** (`isolation: worktree`):
  ```bash
  pwd && git rev-parse --show-toplevel
  ```
- **Manuell** (RAT-21, claim-early, `t<nr>`, KEIN `isolation`): der Pfad steht im
  Prompt; der Erst-Call cd't zuerst hinein — das `Niemals cd`-Verbot des Auto-Modus
  gilt hier NICHT (der `t<nr>`-Pfad liegt bewusst unter dem Repo-Root):
  ```bash
  cd ${LOTSE_PROJECT_ROOT}/.claude/worktrees/t<nr> && pwd && git rev-parse --show-toplevel
  ```

Der aufgelöste Toplevel-Pfad MUSS EINE der zwei Worktree-Familien enthalten:
```
  Auto:    ~/.claude/worktrees/agent-<id>
  Manuell: ${LOTSE_PROJECT_ROOT}/.claude/worktrees/t<nr>
```
Regex (**SSoT — nur hier als Literal**; andere Stellen verweisen auf S1.2):
- POSIX ERE (`grep -E`): `\.claude/worktrees/(agent-[^/[:space:]]+|t[0-9]+)`
- Python `re`:           `\.claude/worktrees/(agent-[^/\s]+|t[0-9]+)`

Prüf-Beispiele: `agent-7f3a`, `t1418` passieren; Shared-Root, leer, `tbd`, `tXYZ`
fallen. Kein Match → STOP (`stop_reason: wrong_worktree`).

### S1.3 Programmer Execution Protocol — Feld-Vorlagen

`mode` kommt aus §2. Die zu liefernden Felder pro Checkpoint sind hier
festgelegt — §2 verweist nur, wiederholt nicht.

```yaml
checkpoint_fields:
  analysis_plan:
    required: [files_inspected, task_understanding, planned_files_to_change,
               planned_tests, local_style_observed, risks_or_unknowns,
               needs_escalation, blast_radius_probe]
    rules:
      - "planned_files_to_change MUSS Teilmenge von write_allowed_files."
      - "blast_radius_probe (PW-7 RATIFIZIERT 2026-06-21): findings + whitelist_delta;
         proaktive Probe vor Edit, ergänzt reaktives outside_whitelist_attempted."
  implementation_done:
    required: [deviations_from_plan, scope_still_respected, needs_escalation]
    # files_changed steht auf Handoff-Top-Level (§3) — hier NICHT dupliziert.
    rules:
      - "scope_still_respected: false → STOP."
  validation_handoff:
    required: [tests_run, test_results, acceptance_criteria_status,
               lint_clean, ready_for_watchdog]
    rules:
      - "lint_clean: false ohne Begründung → Handoff-Reject (Selbst-Gate vor Watchdog, STYLE-2)."
      - "Nicht-Python-Tracks (kein lint_command in §2): lint_clean: not_applicable."
    conditional_fields:
      mockup_visual_probe:
        # PW-54 V1 (2026-06-16 RATIFIZIERT; ENTSCHEID-File
        # "20260616-1715-RATIFIZIERT-pw54-werft-mockup-anker.md" Sektion
        # "Konvergenz/Brüche/Reparatur" → "(C) mockup_visual_probe-Slot").
        # Unabhängige visuelle Prüfung statt Self-Attest — zwei Artefakte
        # zum Auge-an-Auge: probe_url + probe_screenshot_path. Nic vergleicht
        # Mockup-Datei und Screenshot beim Ratifizieren.
        required_when: "ticket_contract.werft_mockup_path is set"
        fields:
          probe_url: "<Heim- oder Tailscale-URL auf den gebauten Screen>"
          probe_screenshot_path: "<Bauer-erzeugter Screenshot des gebauten Screens, repo-relativ>"
        rules:
          - "Fehlt mockup_visual_probe, obwohl werft_mockup_path im Prompt war, ist der Handoff unvollstaendig (Reject-Klasse mockup_visual_probe_missing, §3.1) — der Orchestrator prueft das, seit RAT-36:100 kein Hook mehr."

modes:
  combined:
    when: "risk_class: low"
    structure: "EIN Block, kompakt; alle Pflichtfelder aus den drei Checkpoints zusammengefasst."
  three_compact:
    when: "risk_class: medium"
    structure: |
      Alle Pflichtfelder aus den drei checkpoint_fields-Gruppen (analysis_plan,
      implementation_done, validation_handoff) im finalen Handoff. Drei-Block-
      Gliederung unter den Labels EMPFOHLEN für LLM-Lesbarkeit, NICHT erzwungen —
      ein flacher Handoff mit allen required-Feldern ist konform. Substanz = die
      required-Listen (checkpoint_fields, S1.3), nicht die Block-Labels.
      (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File 20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren
      Sektion "Was sich ändert" → Entzeremonialisierung)
  two_phase:
    when: "risk_class: high"
    DEPRECATED: |
      In diesem Harness nicht ausführbar (PW-8, xbuddy-prozess#8):
      - SendMessage / Agent-Resume existiert nicht.
      - Phase-1-Worktree wird auto-gelöscht, wenn Phase 1 nichts committet.
      Empfohlener Pfad für high: three_compact + Re-Dispatch nach Plan-Bewertung
      (Orchestrator startet Phase 2 als frischen Subagent mit eingebettetem
      Phase-1-Plan im Brief).
    structure: |
      Phase 1: NUR analysis_plan, status=awaiting_orchestrator_review.
      Phase 2: implementation_done + validation_handoff, selber Worktree.
```

### S1.4 Watchdog-Linsen (kanonisch)

```yaml
watchdog_lenses:
  1: spec-drift
  2: familie-3-probe
  3: sackgassen
  4: komplexität
  5: lego-probe
  6: genre-drift
  7: entry-path-coverage
```

### S1.5 Standard-Convention-Block (häufig zitierte Bauregeln)

Optional, je nach Track. Diese Conventions werden in 60%+ der Tracks
berührt. Wenn ein Track sie zitiert: nur die ID nennen, der Auszug kommt
aus Schicht 1.

```yaml
standard_conventions:
  IDENT-1: "conventions/identifiers.md — Stable-ID-Form"
  SVC-1:   "conventions/services.md — systemd-Unit + Health-Endpoint"
  PORT-2:  "conventions/ports.md — Buddies 50NN, Router-Mapping"
  LOG-4:   "conventions/logging.md — structlog key=value"
  URL-3:   "conventions/urls.md — /<buddy-name> ohne API-Präfix"
```

### S1.6 Handoff-Form-Pflichten (Spiegel auf §3, PW-45 V1, 2026-06-12)

Kompakter Pflicht-Auszug aus §3 für die Schicht-1-Transport-Disziplin.
SSoT bleibt §3 (Vollform) — diese Sektion ist Spiegel mit Reject-Klassen-
Bezug. Bei Widerspruch sticht §3.

```yaml
handoff_form_pflichten:
  fence:
    form: "letzter inhaltlicher Block, beginnt mit `contract_kind: handoff`"
    reject_klasse: fence_missing
  worktree_path:
    form: "~/.claude/worktrees/agent-<id> (Auto) ODER ${LOTSE_PROJECT_ROOT}/.claude/worktrees/t<nr> (RAT-21-Manuell, PW-87); nicht 'tbd', nicht leer"
    reject_klasse: worktree_path_unset
  files_changed:
    form: "exakt git diff --name-only origin/main...<branch>"
    reject_klasse: files_changed_diff_mismatch
  acceptance_criteria_met:
    form: "Liste pro AC mit id + met + evidence (Datei:Zeile / Test-ID / Befehl)"
    reject_klasse: evidence_unspecific      # 'siehe Tests' / 'passed' = Reject
  entry_path_probe_result:
    form: "status + (probed: entry_point + evidence) + (lower_level: reason)"
    reject_klasse: probe_status_without_entry_point
  related_echoes_checked:
    form: "ein Eintrag pro §2 related_echo_anchors; reason-Marker nur bei §2-leer"
    reject_klasse: related_echoes_skipped
# Voll-Schema + Reject-Trigger: §3 und §3.1.
```

---

## Self-Gate (Ruff + lint-imports) — Reihenfolge zum Scharfschalten

Das zweistufige Self-Gate (`lint_command` §2, `lint_clean` §3, `lint_status` §4)
ist heute zweistufig: Ruff (Code-Stil) **und** `lint-imports` (Modul-Grenzen
MOD-1..5). Die Konjunktion blockt den Handoff, sobald eine der beiden Stufen
fehlschlägt. Geschichte: Ruff wurde in drei Schritten scharf (Quelle:
brainstorm/ideas/ruff-code-gate); `lint-imports` kam 2026-06-08 dazu via PW-15
(xbuddy-prozess#15, ratifiziert in
`brainstorm/berater-runde/20260608-RATIFIZIERT-pw15-lint-imports.md`).

1. **Bulk-Autofix-PR ZUERST** — ein seriell-gemergter Hygiene-PR über die
   ~157 safe-autofixbaren Funde (I001/F401/RUF100/UPxx), repo-weit. Berührt
   heiße geteilte Dateien → Merge-Gate-Disziplin (eigener PR, zuerst mergen).
   Er trägt auch die `per-file-ignores` für den nicht-fixbaren Rest in die
   `pyproject.toml` ein (deren konkrete Liste erst nach dem Autofix feststeht).
2. **Felder DANN** — `lint_command`/`lint_clean` als Pflicht aktivieren.
3. **Self-Gate scharf** — `lint_clean: false` blockt den Handoff. Vorher scharf
   = Lärm + falsche Blocks auf ungefixter Altlast.

---

## §1 Ticket Contract

Wird vom Orchestrator **vor** jedem Subagent-Start gefüllt und als Kommentar
am GitHub-Issue gepostet via `gh issue comment <nr> --body-file …`.

```yaml
contract_kind: ticket
contract_id: T<issue-nr>
issue: <nr>
title: "<Issue-Titel — kurz, zitierfähig>"

mission: |                       # WHY in einem Satz
  <1 Satz>

backfill: <T-id>-B | null        # bei bestehenden Tickets (siehe §6)

# SSoT-Verweise — zitiert, nicht erraten.
requirement_ids: [ROU-15, WET-3]
spec_files:                       # max 3
  - specs/buddies/wetter.md
conventions: [PORT-2, URL-3]      # IDs; Standard-Block (S1.5) kommt aus Schicht 1

vertical_slice:
  trigger: "<konkreter Schritt am echten System>"
  observable: "<sichtbares Ergebnis>"

scope:
  in_scope: ["<Punkt>"]
  out_of_scope: ["<Punkt>"]

acceptance_criteria:              # max 5
  - id: AC1
    text: "<prüfbare Aussage>"
    evidence_hint: "<Pfad / Befehl / Beobachtung>"

# Pflichtfeld. Track-Ebenen-Variante der vertikalen Scheibe.
entry_path_probe:
  required: true | false
  reason: "<warum required so gesetzt>"
  # Bei required: true ALLE folgenden Pflicht; bei false nur reason.
  spec_source:
    requirement_ids: [...]
    acceptance_criteria: [...]
  expected_entry_point: "<echter Runtime-Pfad>"
  expected_observable: "<Sichtbares>"
  # PW-16 (xbuddy-prozess#16, 2026-06-08): Bei Service-Migrations-/Deploy-Tracks
  # (Pfad-Override aktivieren, Daten umziehen, Unit-Drop-in, neue Service-Vorlage)
  # MUSS write_verification_required gesetzt sein — NUR true oder false (kein
  # not_applicable, sonst Fail-Open). Bei true: pro betroffenem Schreib-Pfad
  # ein write_targets-Eintrag mit command + expected_observation; expected_observable
  # spiegelt das. Bei false: reason Pflicht (z. B. "reiner Lese-Service, keine
  # persistierten Schreibpfade").
  # Library-Sonderfall (z. B. tools/zugangsdaten, kein Service/HTTP-Endpoint):
  # write_verification_required gehört auf den KONSUMIERENDEN Service-Track,
  # nicht auf den Library-Track selbst; dort false mit reason "Library, Verifikation
  # via Konsument-Track <T-id>".
  # Auslöser: 2026-06-07-Vorfall — 7 SVC-5-Dienste als „verifiziert" gemeldet,
  # faktisch nur Lesen geprüft; Eltern-Chat ~14 Min stumm.
  write_verification_required: true | false
  # Pflicht bei write_verification_required: true. Eine Liste — heterogene
  # Multi-Store-Services (z. B. routine mit ROUTINE_DATA_FILE +
  # ROUTINE_STORE_FILE) bekommen pro Pfad einen Eintrag. Codex-Bruch:
  # ein PUT-Proof gegen routine.json darf nicht den ungemeinten Store-Pfad
  # grünmalen.
  write_targets:
    - target: "<ENV_NAME → konkreter Ziel-Pfad, z. B. ROUTINE_STORE_FILE → ~/xbuddy-data/routine/routine_store.json>"
      command: "<exakter Befehl, z. B. curl -X POST .../routine/abhaken -d '{...}'>"
      expected_observation: "<HTTP/Exit + Schreib-Beobachtung am Zielort, NICHT 'Service startet'>"
      cleanup_command: "<reversibler Cleanup-Befehl ODER 'n/a (irreversibel, mit Grund)'>"
  # Cleanup-Default ist Pflicht (SVC-5 verlangt additiv-rückrollbar, services.md
  # Z. 54). false NUR mit cleanup_skip_reason (irreversibles Schema-Migrate o.ä.).
  write_cleanup_required: true | false
  cleanup_skip_reason: "<Pflicht wenn write_cleanup_required: false>"

risk_class: low | medium | high
# Steuert §2 programmer_execution_protocol.mode:
#   low → combined, medium → three_compact, high → three_compact + Re-Dispatch
# (two_phase ist DEPRECATED — siehe §1.3, PW-8: SendMessage/Resume fehlt im Harness.)

model_choice:
  default_agent: haiku | sonnet | opus
  reason: "<warum diese Stufe>"
  # Begründungspflicht GEGEN Haiku: Bei trivial-mechanischem Track (Link-/
  # Verweis-Fix, #nr-Annotation, README-Tabelle, Hygiene-Welle, Test-Skelett
  # entlang Vorlage) ist haiku der Default; wer sonnet/opus wählt, begründet im
  # reason ausdrücklich, WARUM nicht Haiku. Kein hartes Verbot (Token-Strategien
  # sind Annahmen, 2-Reject-Rückfall gilt), aber kein reflexhaftes Sonnet.
  # Standard-Triggers (kanonisch, vgl. arbeitstag.md MODELL-WAHL):
  #   haiku  → trivial-mechanisch: Link-Fixes, Verweis-Updates, Ticket-
  #            Annotationen #nr, README-Tabellen-Ergänzungen, Hygiene-
  #            Welle, Test-Skelett entlang Vorlage
  #   sonnet → Code-/Spec-Tracks, Fix-Tracks nach Watchdog, Folge-Tracks
  #   opus   → cross-component, unclear specs, public API/auth/payment,
  #            repeated failure, watchdog structural/critical,
  #            high_context_track
  escalate_if: [...]              # optional

cited_rules:                       # max 10; nur track-spezifische
  - id: ROU-15
    file: specs/platform/router.md
    excerpt: "<Auszug>"
# Standard-Conventions (PORT-2, URL-3 etc.) NICHT hier wiederholen —
# kommen aus S1.5. Nur ID in `conventions:` oben reicht.

missing_required_context: []
# Wenn nicht leer: HALT zu Nic. Kein Subagent-Dispatch.

# Optional — nur bei Inhalt:
# dependencies: { blocks: [...], blocked_by: [...], related: [...] }
# notes_for_day_close: [...]

# PW-54 V1 (2026-06-16 RATIFIZIERT; ENTSCHEID-File "20260616-1715-RATIFIZIERT-
# pw54-werft-mockup-anker.md" Sektion "Konvergenz/Brüche/Reparatur" →
# "(B) stat()-Existenz-Check"): Werft setzt werft_mockup_path bei UI-Bau-
# Übergaben (F4). Repo-relativer Pfad nach specs/mockups/<slug>/ (mindestens
# eine .html-Datei). dispatch_status_guard.py prüft Existenz via stat() vor
# Subagent-Dispatch — kein Self-Attest, mechanische Mindestform. /tmp/- oder
# brainstorm/-Pfade sind verboten und werden geblockt. Nicht-UI-Tracks lassen
# das Feld weg.
# werft_mockup_path: "specs/mockups/<slug>/index.html"
```

---

## §2 Sub-Agent Contract

Bündelt den Ticket Contract mit operativen Details, wird **nach Schicht 1**
im Sub-Agent-Prompt eingebaut.

```yaml
contract_kind: subagent
contract_id: T137-S1
# PW-17 / RAT-15 (2026-06-08): parent_ticket trägt jetzt die Repo-Identität
# (`<owner>/<repo>#<nr>`), damit der PreToolUse-Hook
# `dispatch_status_guard.py` ohne CWD-Abhängigkeit via `gh issue view <repo>
# <nr>` arbeiten kann. Alte Form `T<nr>` ohne Repo-Marker ist deprecated und
# wird vom Hook hart geblockt (keine Bypass-Logik bei fehlendem Marker).
parent_ticket: ${LOTSE_PROJECT_REPO}#137
previous_handoff_id: null         # bei Fix-Tracks nach Watchdog
high_context_track: false         # true → Opus + Begründung

# PW-31 (xbuddy-prozess#30, 2026-06-09): Track-Mode-Pflicht.
# Bestimmt, welche Output-Sorte der Subagent liefert UND welchen Scope er hat.
# - read       : Bestand lesen/sortieren, KEINE Lösungs-Vorschläge.
#                Pflicht: write_allowed_files MUSS leer sein ([]) — macht S1.1
#                scope_breach mechanisch scharf.
# - propose    : Lösungs-Vorschlag liefern (z. B. /berater-runde R2). Keine
#                acceptance_criteria-Pflicht. Kein Code-Edit.
# - build      : Code-/Doku-Änderung (Standard /arbeitstag-Track).
#                Pflicht: acceptance_criteria gesetzt.
# - formalize  : Spec-/Convention-Entwurf (Berater-Modus C). Keine
#                acceptance_criteria-Pflicht (Spec-Drafts haben kein AC-Korsett).
# Hook dispatch_status_guard.py prüft Vorhandensein UND Wertebereich.
mode: read | propose | build | formalize

mission: |                        # 1 Satz, aus §1
  ...

scope:
  write_allowed_files: [...]      # max 5–8 — Konflikt-Prüfung NUR hier
  read_context_files: [...]       # max 5–8 — darf überschneiden
  forbidden_files: [...]
  out_of_scope: [...]

cited_specs:                       # max 3 Slices, track-spezifisch
  - id: ROU-15
    file: specs/platform/router.md
    excerpt: "<Auszug>"

cited_conventions:                 # max 10
  # Standard-Conventions: nur ID, Auszug aus S1.5
  - id: PORT-2
  # Track-spezifische: voll mit Excerpt
  - id: ROU-15-CONV          # Beispiel
    file: conventions/...
    excerpt: "<Auszug>"

acceptance_criteria: [...]         # max 5, aus §1
# Pflicht bei mode: build. Bei mode: read | propose | formalize optional/leer.
# Wenn entry_path_probe.required: true in §1: ein AC drückt den Probe-Pfad aus.

# PW-54 V1 (2026-06-16 RATIFIZIERT): wenn §1 werft_mockup_path gesetzt hat,
# MUSS der Subagent-Prompt es spiegeln — sonst sieht dispatch_status_guard.py
# das Feld nicht (Hooks lesen nur den Prompt).
# Plus: Pfad MUSS in read_context_files erscheinen, damit der Subagent das
# Mockup-File überhaupt konsumieren darf (sonst scope_breach).
# werft_mockup_path: "specs/mockups/<slug>/index.html"   # aus §1 spiegeln

# Standard-Stop-Rules (S1.1) gelten IMMER. Hier nur track-spezifische:
stop_rules: []                     # max 3 zusätzlich, leer wenn keine

related_echo_anchors:              # Echo-Prüfung, NICHT Mit-Edit
  - "specs/buddies/wetter.md WET-3"

# Verweis statt Wiederholung:
programmer_execution_protocol:
  mode: combined | three_compact | two_phase   # two_phase DEPRECATED, siehe S1.3
  # Feldlisten + Regeln: siehe Schicht 1 (S1.3).
  # Für risk_class:high → mode three_compact + Re-Dispatch (Orchestrator
  # startet Phase 2 als frischen Subagent mit eingebettetem Phase-1-Plan).

operational:
  worktree_required: true
  shared_root: ${LOTSE_PROJECT_ROOT}
  branch_name: feature/137-wetter-routing
  base: main
  # setup_reflex: siehe Schicht 1 (S1.2).
  test_command: "pytest tests/test_router.py -k wetter"
  # Nur Python-Tracks. Spec-/Doku-/JSON-Tracks: weglassen → lint_clean: not_applicable.
  # Scope-Regel (2026-07-05, #1262/test_ETAB6_V1): Ändert der Diff Signatur/Guard/
  # Default einer breit-konsumierten Funktion (z. B. build_catalog), MUSS
  # test_command die Testdateien ALLER Konsumenten einschließen (grep der
  # Aufrufer, analog blast_radius_probe) — der eng gescopte Self-Gate ist bis
  # #1310 (pytest-CI) der EINZIGE Test-Enforcer; ein verpasster Konsument
  # landet sonst unsichtbar rot auf main.
  # Zweistufig (STYLE-2): Ruff && lint-imports — die Konjunktion blockt den Handoff,
  # sobald entweder Code-Stil (Ruff) oder Modul-Grenzen (MOD-1..5) verletzt sind.
  # Form fix: NIE --diff auf Ruff (das ist Fix-Preview, exit 0 trotz Fehler).
  # --no-cache bei lint-imports vermeidet .import_linter_cache-Schreib im Worktree.
  # AKTIV seit #324 (pyproject.toml [tool.ruff] auf main, 2026-06-05) +
  # PW-15 (xbuddy-prozess#15, 2026-06-08): lint_command ist für Python-Tracks Pflicht,
  # lint_clean: false blockt den Handoff (STYLE-2).
  # RAT-30, Teil 5 (2026-07-27): Der Self-Gate (ruff && lint-imports) bleibt Handoff-
  # Blocker; ZUSÄTZLICH gilt am Merge-Gate die lokale Volllauf-Pflicht — solange pytest
  # advisory ist (nur closes-guard required), muss vor dem Merge `python3 -m pytest -q`
  # repo-weit grün sein. Details: commands/arbeitstag.md (Merge-Gate), decisions/RAT-30.
  lint_command: "uvx ruff@0.15.15 check $(git diff --name-only --diff-filter=d origin/main...HEAD -- '*.py') && uvx --from import-linter==2.11.* lint-imports --no-cache"

# expected_handoff: siehe §3. Pflichtfelder kommen aus Schicht 1.

model: haiku | sonnet | opus       # aus §1 model_choice
```

---

## §3 Structured Handoff

Der Subagent gibt einen **parsebaren YAML-Fence** zurück, der mit
`contract_kind: handoff` beginnt. Dieser Fence ist der **letzte** inhaltliche
Block der Antwort — nach dem schließenden ` ``` ` kein inhaltlicher Zusatz.
**Bullet/YAML, keine Wiederholung des Contracts.**

```yaml
contract_kind: handoff
contract_id: T137-S1
parent_ticket: T137

status: completed | partial | stopped | awaiting_orchestrator_review
stop_reason: null | scope_breach | spec_violation | acceptance_not_reachable
             | wrong_worktree | convention_needed | missing_context
             | needs_escalation

steps:                              # 3–5 Zeilen, was tatsächlich getan wurde
  - "..."

# Pflicht. Form richtet sich nach §2 programmer_execution_protocol.mode.
# Feld-Pflichten siehe Schicht 1 (S1.3).
checkpoints:
  # mode: combined → genau dieser Block:
  combined:
    task_understanding: "<1 Satz>"
    files_inspected: [...]
    planned_files_to_change: [...]
    deviations_from_plan: []        # weglassen wenn leer
    scope_still_respected: true
    tests_run: [...]
    test_results: "<knapp>"
    lint_clean: true | false | not_applicable    # Self-Gate Ruff + lint-imports (STYLE-2); n/a = Nicht-Python
    acceptance_criteria_status: "<knapp>"
    ready_for_watchdog: true
    needs_escalation: false
  # mode: three_compact → alle Pflichtfelder der drei checkpoint_fields-Gruppen
  #   (analysis_plan, implementation_done, validation_handoff) im finalen Handoff.
  #   Drei-Block-Gliederung unter den Labels EMPFOHLEN für Lesbarkeit, NICHT
  #   erzwungen — ein flacher Handoff mit allen required-Feldern ist konform.
  #   Substanz = die required-Listen (S1.3), nicht die Block-Labels.
  #   AUSNAHME High-Phase-1 (status: awaiting_orchestrator_review): expliziter
  #   analysis_plan-Block bleibt Pflicht (preflight.md §B.3 Carve-out).
  #   (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File
  #   20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren Sektion
  #   "Was sich ändert" → Entzeremonialisierung; Antiberater-Pass-2 §3-SSoT-Fix)
  # mode: two_phase Phase 1 → DEPRECATED (PW-8). Empfohlen: three_compact + Re-Dispatch.

# Pflicht im analysis_plan ODER (bei combined) hier auf Top-Level.
# Geschlankt auf drei Felder:
local_style_observed:
  files_sampled: [...]              # 2–5 Nachbardateien
  observations: ["<kurze Bullet-Liste der relevanten Muster>"]
  inconsistencies_found: []         # leer = konsistent

# PW-7 RATIFIZIERT 2026-06-21: Blast-Radius-Probe.
# Bei mode: three_compact → Pflichtfeld im analysis_plan-Block (siehe S1.3 :80-85).
# Bei mode: combined → Top-Level-Feld mit einer von zwei Formen:
#   blast_radius_probe: "not_applicable"
#     (kein Default-/Signatur-/Removal-/Deploy-Touch sichtbar)
#   ODER triggerbasiert:
#     blast_radius_probe:
#       trigger: "default_change | signature_change | removal | deploy_config_touch"
#       findings:                    # konkrete Grep-Befunde, evidence-getrieben
#         - "git grep -rn 'fn_name1' --include='*.py' -> 3 Treffer in [..., ..., ...]"
#       whitelist_delta:             # leeres Array wenn Blast ⊆ Phase-0-Whitelist
#         additional_files: [...]
#         reason: "..."

worktree_path: ~/.claude/worktrees/agent-<id>   # Auto-Beispiel; RAT-21-Manuell wäre …/xbuddy/.claude/worktrees/t<nr> (siehe S1.2)
branch: feature/137-wetter-routing

files_changed:                      # exakt git diff --name-only origin/main...<branch>
  - router/routes.json

outside_whitelist_attempted: []     # MUSS leer für valid handoff (reaktiv)

acceptance_criteria_met:             # alle AC aus §2
  - id: AC1
    met: true | false | partial
    evidence: "<datei:zeile | test-id | befehl>"

# Pflicht. Spiegel zu §1 entry_path_probe.
entry_path_probe_result:
  status: probed | lower_level | not_applicable
  # probed/lower_level: entry_point + evidence Pflicht
  # lower_level/not_applicable: reason Pflicht
  entry_point: "<getroffener Pfad>"
  evidence: "<Test-ID / Befehl / Beobachtung>"
  reason: "<bei lower_level / N/A>"
  # PW-16 (xbuddy-prozess#16, 2026-06-08): Bei §1
  # write_verification_required: true MUSS write_proofs gesetzt sein —
  # eine Liste mit einem Eintrag PRO §1 write_targets-Eintrag, in derselben
  # Reihenfolge. Cardinalität: len(write_proofs) == len(write_targets), sonst
  # Reject (Codex-Bruch: Multi-Store wie routine bekommt sonst False-Pass mit
  # einem PUT-Proof). Reine Lese-Verifikation („Service startet + lädt Datei")
  # ist KEIN write_proof — preflight rejected write_verification_required: true
  # ohne write_proofs.
  write_proofs:
    - target: "<spiegelt §1 write_targets[i].target>"
      command_run: "<exakt der Befehl aus §1; bei Abweichung Grund>"
      before: "<Zustand am Zielort VOR der Probe — Datei-Inhalt/Größe/Hash, NICHT geraten>"
      after: "<Zustand am Zielort NACH der Probe — Schreib-Beobachtung, kein Mock>"
      exit_or_http: "<Exit-Code / HTTP-Status>"
  # Pflicht wenn §1 write_cleanup_required: true (sonst weglassen).
  # Liste wie write_proofs, Cardinalität identisch.
  write_cleanups:
    - target: "<spiegelt §1 write_targets[i].target>"
      command_run: "<Cleanup-Befehl aus §1>"
      after_cleanup: "<Zustand am Zielort nach Cleanup — muss Ausgangszustand entsprechen>"
      exit_or_http: "<Exit-Code / HTTP-Status>"

related_echoes_checked:              # eine Aussage pro Anker aus §2
  - anchor: "<§2-Anker>"
    finding: "<konsistent + Kurz-Begründung ODER konkreter Befund>"
# Null-Fall: wenn §2 keine related_echo_anchors enthielt:
#   related_echoes_checked: []
#   related_echoes_reason: "no related_echo_anchors in contract"

watchdog_hints:
  lenses_relevant: [1, 6]
  diff_summary: "<2–4 Zeilen>"
  # lenses_not_applicable NICHT mehr pflicht — die schweigt der Subagent.

# Optional — nur bei Inhalt einfügen:
# spec_touches: [...]
# convention_touches: [...]
# open_questions: [...]
# risks_noticed: [...]
```

### §3.1 Form-Drift-Reject-Klassen (PW-45 / xbuddy-prozess#45, 2026-06-12)

Diese Klassen sind **Reject-Gründe** für den Orchestrator. Sie schärfen die
Pflichtfelder oben — die SSoT für die Felder bleibt §3 selbst. Geprüft wird
ausschließlich vom Orchestrator; der früher hier vorgesehene Hook ist mit
**RAT-36:100** gestorben (xbuddy-prozess#52 damit erledigt).

| Klasse | Trigger | Beispiel-Drift |
|---|---|---|
| `fence_missing` | Antwort enthält kein `contract_kind: handoff`-Fence als letzten Block | Top-level `handoff:` ohne Fence (T-A-v1 2026-06-12) |
| `evidence_unspecific` | `acceptance_criteria_met[*].evidence` ist Stub („siehe Tests", „passed", leer) | kein Bezug auf konkrete Datei/Test-ID/Befehl |
| `probe_status_without_entry_point` | `entry_path_probe_result.status: probed` ohne `entry_point` UND `evidence`; oder `lower_level` ohne `reason` | Probe behauptet, aber kein konkreter Treffer/Beleg |
| `files_changed_diff_mismatch` | `files_changed` ≠ `git diff --name-only origin/main...<branch>` | Liste aus Plan übernommen statt aus Diff |
| `worktree_path_unset` | `worktree_path` ist leer, `tbd`, oder matcht **keine** der zwei Worktree-Familien gemäß **Schicht 1 S1.2** (Auto `agent-<id>` \| RAT-21-Manuell `t<nr>`, PW-87; Regex-Literal nur dort) | Subagent hat im Shared-Root gearbeitet |
| `related_echoes_skipped` | §2 `related_echo_anchors` nicht-leer UND (a) `related_echoes_checked` leer ODER Cardinalität ≠ Anker-Zahl, ODER (b) `related_echoes_reason` ist gesetzt obwohl §2-Anker vorhanden | Anker übergangen / `reason`-Marker zweckentfremdet |

Trifft eine Klasse, wird der Handoff vom Orchestrator abgelehnt (Backfill-
Pflicht oder Re-Dispatch). **Pragma-Durchwinken gibt es nicht mehr** — Reject
bleibt Reject (Nic-Setzung 2026-08-17, im Vollzug von RAT-36:100). Die frühere
Ausnahme war an einen Log-Eintrag gebunden, dessen Hook gestorben ist; sie
ersatzlos stehenzulassen hätte das Durchwinken bedingungslos erlaubt — eine
Lockerung, die niemand beschlossen hat.

---

## §4 Watchdog-Ready Summary

Wird vom **Orchestrator** aus Ticket Contract + Sub-Agent Contract + Handoff
erzeugt. Diff-basiert, nicht Full-Scan.

**Eingaben:** §1, §2 (**inkl. `acceptance_criteria[*].id` + `.text`**), §3
(Checkpoints, files_changed, acceptance_criteria_met, related_echoes_checked,
local_style_observed, risks_noticed), `git diff --name-only origin/main...<branch>`.

**AC-Abdeckungs-Check (PW-12):** Der Watchdog gleicht pro AC den `.text` (§2) gegen
`acceptance_criteria_met` (§3) + den Diff ab — ist die `met:true`-Behauptung durch
den Diff **gedeckt**? Mengen-AC („alle N") mit Evidenz auf nur *eine* Stelle = Befund.
**Grenze (ehrlich):** das prüft *Coverage* (Behauptung vs. Diff), **nicht** ob die
geänderte Stelle in Wahrheit grün ist — der Watchdog sieht nur den Diff, nicht den
Live-Vollstand.

**Was NICHT in den Watchdog-Prompt:** ganze Specs, ganzes Repo,
Session-History, frühere Contracts anderer Tickets.

```yaml
contract_kind: watchdog_summary
contract_id: T137-S1-W
parent_ticket: T137
pr: <pr-nr>
branch: feature/137-wetter-routing

diff_scope:
  files: [...]
  loc_added: <n>
  loc_removed: <n>

specs_touched: [ROU-15]
conventions_touched: [PORT-2, URL-3]

lint_status: clean | dirty | not_applicable   # eine Zeile aus §3.lint_clean —
# Self-Gate Ruff (Code-Stil) + lint-imports (Modul-Grenzen MOD-1..5). Damit
# der Watchdog mechanische Funde (unused import, MOD-Verstoß) nicht selbst sucht.

checkpoints_summary:                 # destilliert aus §3, max 4 Zeilen
  local_style: "<konsistent | Kurz-Befund>"
  deviations: "<leer | Kurzfassung>"
  remaining_risks: "<leer | Kurzfassung>"

# Linsen-IDs siehe Schicht 1 (S1.4).
lenses_requested:
  - id: 1
    reason: "<warum diese Linse für den Diff>"
# lenses_skipped: NUR Einträge mit nicht-trivialer Begründung.
# Standard-Skip („Diff hat kein neues Verhalten" etc.) bleibt implizit.
lenses_skipped: []                   # leer = alle Nicht-Requested-Linsen trivial skip

acceptance_evidence: [...]            # aus §3
risks: [...]                          # aus §3.risks_noticed
echo_check: [...]                     # aus §3.related_echoes_checked

# Optional:
# orchestrator_caveats: [...]
```

---

## §5 Decision Record (Open Decision)

**Nur Pflicht, wenn `blocks_execution: true`.** Bei kleinen Klärungen
reicht ein Eintrag in `## Offene Punkte` der Spec (etablierte Form in
xbuddy) ohne YAML-Overhead.

| Klassifikation | Schema-Pflicht? | Wohin damit |
|---|---|---|
| spec-local / Produkt-Verhalten | nur bei blocks_execution | `## Offene Punkte` in der Spec |
| architecture / cross-cutting | ja, bei blocks_execution | **Halt zu Nic.** Issue + `blocked`. Bei 3+ Vorkommen: Ticket „Ort dafür". |
| reusable engineering rule | ja | Convention-Ticket |
| pure execution blocker | optional | Ticket-Kommentar, Label `blocked` |

```yaml
contract_kind: decision
decision_id: D-T137-1
status: open | proposed | accepted | rejected | deferred
scope: ticket | spec | architecture | convention | product | execution
question: "<was muss entschieden werden>"
options: ["<Option A>", "<Option B>"]
recommendation: "<vorgeschlagene Option oder null>"
owner: Nic | Orchestrator
source_ticket: 137
target_document: specs/buddies/wetter.md
blocks_execution: true | false
```

---

## §6 Contract Backfill Report

Für **bestehende** Tickets ohne Contract. **Nur** aktive oder unmittelbar
geplante Tickets. **Kein** Backlog-Backfill.

Source/Confidence pro Feld: **Nicht für jedes Feld**. Default ist
`source: ticket, confidence: high` — nicht annotieren. Nur abweichende
Felder tragen den Tag.

```yaml
contract_kind: backfill
contract_id: T<nr>-B
parent_ticket: T<nr>

status: ready_for_execution
        | needs_orchestrator_review
        | needs_PO_decision
        | blocked_missing_contract

# Nur Felder mit nicht-Default-Provenance:
field_provenance:
  - field: <feldname>
    source: inferred | convention | ownership_table | spec | missing
    confidence: high | medium | low
    note: "<woher / warum>"

# Optional — nur bei Inhalt:
# open_questions: [...]
# linked_decisions: [...]
```

**Backfill-Budget:** Wenn ein Ticket nach ~5 Min Recherche nicht in einen
Contract gegossen werden kann → `blocked_missing_contract`.
