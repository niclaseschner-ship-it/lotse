# Preflight & Handoff-Validierung

Fünf Checklisten. Sie sind die einzige Validierung — kein Tool, kein Linter.
Der Orchestrator hakt sie selbst ab und meldet ihre Ergebnisse im Board.

| Sektion | Wann | Was |
|---|---|---|
| §A | vor Subagent-Dispatch | Operational Preflight |
| §B | nach Subagent-Rückkehr | Handoff-Validierung (Reject + Re-Dispatch, einmalig) |
| §C | vor Watchdog-Aufruf | Watchdog-Summary-Check |
| §D | jederzeit | Provider Health / Sequential Mode |
| §E | Sessionstart | Decision-Discovery (vor §A.0 Backfill) |
| §F | jederzeit | Token-Strategie-Meldungen (wenn Annahmen nicht aufgehen) |

---

## §A Operational Preflight (vor Subagent-Dispatch)

### A.0 Backfill-Klassifikation (nur bei bestehenden Tickets)

Wenn das Ticket VOR der Contract-First-Einführung existierte (kein
Ticket-Comment-Contract am Issue): erst Backfill, dann §A.1.

- [ ] Backfill-Report (`schemas.md §6`) gefüllt, am Issue gepostet.
- [ ] Status klassifiziert:
  - `ready_for_execution` → weiter mit §A.1.
  - `needs_orchestrator_review` → Klärung intern, dann §A.1.
  - `needs_PO_decision` → Decision Record (`schemas.md §5`), Halt zu Nic.
  - `blocked_missing_contract` → Backfill abbrechen, Ticket bekommt
    Label `blocked`, Halt zu Nic. **Nicht** Stunden in Context-Recherche
    verbrennen.
- [ ] Backfill-Budget eingehalten: maximal ~5 Min Recherche pro Ticket.
- [ ] **Kein Backfill des gesamten Backlogs** — nur aktive oder
      unmittelbar geplante Tickets.

### A.1 Ticket Contract vollständig?

- [ ] `mission` ist EIN Satz (kein Absatz).
- [ ] `requirement_ids` ist explizit (auch wenn `[]`, dann Bug-Fix mit
      Begründung im PR-Body).
- [ ] `cited_rules` zitiert nur IDs, die per `grep -r "^### .*ID:" specs/ conventions/`
      auffindbar sind. Wenn nicht: `missing_required_context`-Eintrag, kein
      „wird schon stimmen".
- [ ] **Existenz-Grep (Gegenrichtung) erledigt**, wenn der Track eine NEUE ID
      prägt oder ein NEUES Deliverable annimmt: `grep -rn "<ID-Stamm>" specs/
      conventions/` zeigt KEINE bestehende ID gleicher Form; `gh issue list
      --search "<thema>" --state all` + `gh pr list --search "<thema>" --state
      merged` + `git -C ${LOTSE_PROJECT_ROOT} grep "<schlüsselbegriff>"
      origin/main` zeigen das Deliverable nicht schon auf main. Treffer → kein
      neuer Anker / kein neuer Track, andocken bzw. Ticket schließen.
      (arbeitstag.md Phase 0; Quelle Retro 2026-05-31: EC-25 #284, #286/#289.)
- [ ] `vertical_slice.observable` ist eine Sache, die Nic ohne Test-Pipeline
      sehen kann.
- [ ] `entry_path_probe` ist gesetzt. Bei Code-/Verhalten-Tracks
      `required: true` mit konkretem `expected_entry_point` + `spec_source`.
      Bei reinen Spec-/Doku-/Convention-Tracks `required: false` mit reason.
      „Unit-Test reicht" ist **keine** legitime Begründung für required:
      false bei verhaltensändernden Tracks — dafür gibt es den Status
      `lower_level` im Handoff mit Pflicht-Begründung.
- [ ] Wenn `entry_path_probe.required: true`: mindestens ein AC drückt den
      Probe-Pfad aus (nicht nur isolierte Helper-Probe).
- [ ] **PW-51 Live-Naht (V1, 2026-06-12 RATIFIZIERT — Codex Pass 2:
      Provider-Consumer-Reihenfolge zwingt AC-Sitz auf Naht-Eigentümer):**
      Wenn das übergeordnete Brett **mehrere Tracks** hat, deren **Runtime**
      sich an einer Naht trifft (Cross-Track-Aufruf: Track-A liefert
      Funktion/Endpunkt = Provider, Track-B ruft sie zur Laufzeit auf =
      Consumer):
      - **Provider-Track:** trägt **Contract-AC** für seine Schnittstelle
        (Eingabe-Schema, Ausgabe-Form, beobachtbar isoliert ohne den
        Consumer). Kein zusammengesetzter Pfad-AC — der wäre zu seinem
        Merge-Zeitpunkt nicht erfüllbar.
      - **Consumer-/Combine-Track (letzter Naht-Eigentümer):** trägt
        **mindestens ein Integration-AC** über den zusammengesetzten Pfad
        — Aufrufer + Aufgerufener mit beobachtbarem End-Ergebnis nach dem
        Merge beider Tracks. Reine Stück-ACs reichen hier NICHT — sie
        haben T531-Live-NO-OP nicht gefangen.
      Single-Track-Bretter sind nicht betroffen. PW-9 Final-Integrations-
      Watchdog bleibt für den zusammengeführten Diff zuständig
      (`arbeitstag.md` PW-9-Block); diese Klausel deckt die **Vertrags-Seite**
      vor Build und stellt sicher, dass der **letzte** Track im Brett die
      Integration ausführbar belegt.
- [ ] **PW-16:** Bei Service-Migrations-/Deploy-Tracks ist
      `entry_path_probe.write_verification_required` explizit gesetzt —
      `true` oder `false` mit reason. `not_applicable` ist KEIN gültiger Wert
      (Codex-Bruch: Fail-Open). Bei `true`: `write_targets` ist eine Liste
      mit einem Eintrag PRO migriertem Schreib-Pfad (Multi-Store-Services
      wie routine mit DATA+STORE bekommen mehrere Einträge). Jeder Eintrag
      hat `target`, `command`, `expected_observation`, `cleanup_command`.
      `write_cleanup_required: false` braucht `cleanup_skip_reason`
      (SVC-5 verlangt additiv-rückrollbar). Library-Tracks (z. B.
      `tools/zugangsdaten`): false mit reason „Library, Verifikation via
      Konsument-Track <T-id>".
- [ ] **Token-Budget eingehalten** (`schemas.md` Tabelle): ≤3 Spec-Slices,
      ≤10 Conventions, ≤5 AC. Sonst `high_context_track: true` mit
      Begründung **und** Opus.
- [ ] `missing_required_context` ist `[]`. Andernfalls **HALT zu Nic**.
- [ ] Ticket Contract als Issue-Comment gepostet
      (`gh issue comment <nr> --body-file …`).

### A.2 Repo- und Worktree-Setup

- [ ] Shared-Root `${LOTSE_PROJECT_ROOT}` ist sauber:
      `git -C ${LOTSE_PROJECT_ROOT} status` → working tree clean,
      Branch `main`. Wenn nicht: aufräumen (siehe arbeitstag.md Merge-Gate
      Punkt 3), dann erst weiter.
- [ ] **Lokaler `main` == `origin/main`** (Standard-Git, RAT-9): am
      Session-Start `git -C ${LOTSE_PROJECT_ROOT} fetch origin && git -C
      ${LOTSE_PROJECT_ROOT} pull --ff-only origin main`. So zweigt jeder
      `isolation: worktree`-Track von **aktuellem** `origin/main` ab — die alte
      Base-Drift (Folge-Track kennt Vortrack nicht) entsteht gar nicht mehr,
      weil jeder Merge sofort als PR nach `origin` geht. (Der CWD-Reflex unten
      bleibt davon unberührt — andere Ursache.)
- [ ] Branch-Name folgt `feature/<nr>-…` bzw. `fix/<nr>-…`.
- [ ] `write_allowed_files` überschneidet sich **nicht** mit
      `write_allowed_files` eines anderen Live-Tracks. **Konflikt-Prüfung,
      Ownership-Tabelle und Scope-Gate beziehen sich ausschließlich auf
      `write_allowed_files`.**
- [ ] `read_context_files` dürfen sich zwischen parallelen Tracks
      überschneiden — sie sind nur Lese-Kontext für Stil-/Schnittstellen-
      Prüfung, nicht Edit-Erlaubnis.
- [ ] **Dispatch-Modus bestimmt den Worktree-Pfad-Vertrag (PW-87 — zwei Modi):**
- [ ] **(a) Auto-Worktree** (`isolation: worktree`, Standard-Parallel-Tracks):
      Subagent wird mit `isolation: worktree` gestartet — Worktree-Pfad steht
      NICHT im Subagent-Prompt; der Subagent findet ihn via `pwd` /
      `git rev-parse --show-toplevel` (erwartet `~/.claude/worktrees/agent-<id>`).
      **Orchestrator steht im Repo-Root — im selben Aktions-Batch wie der
      Dispatch.** Unmittelbar vor jedem `isolation: worktree`-Dispatch eine
      **standalone** `cd ${LOTSE_PROJECT_ROOT}` (kein mehrzeiliges
      `cd X\n…`). Wichtig: Die Harness setzt die Shell-CWD zwischen Aktionen
      auf `~` zurück — eine `cd` in einem *früheren* Schritt wirkt
      beim Dispatch nicht mehr; sie muss dem Dispatch **unmittelbar
      vorausgehen** (gleicher Tool-Batch). Default ohne `cd` ist
      `~` (kein Repo → Worktree-Erstellung scheitert mit „not in a
      git repository"). (Datenbelegt durch Vererbungstest 2026-06-02; Symptom
      Retro 2026-06-02a, 2×.)
- [ ] **(b) Manueller RAT-21-Worktree** (claim-early, `.claude/worktrees/t<nr>`,
      **kein** `isolation: worktree`): der Worktree existiert schon (bei Plan-Ende
      alloziert). Der Orchestrator **nennt den Pfad explizit im Prompt** und der
      **erste Bash-Call des Subagenten ist**
      `cd ${LOTSE_PROJECT_ROOT}/.claude/worktrees/t<nr> && pwd` (positives Muster).
      Das negative `Niemals cd`-Verbot des Auto-Modus gilt hier NICHT — der
      `t<nr>`-Pfad liegt bewusst unter dem Repo-Root. Kein Orchestrator-`cd` vor
      Dispatch nötig (es wird kein Auto-Worktree erzeugt). (PW-87: weak-model-
      Fehllesung „keinen xbuddy-Pfad anfassen" → wrong_worktree, ~12 Retros.)

### A.3 Modellwahl plausibel?

Drei Stufen, gestaffelt nach Track-Klasse:

- [ ] **Haiku** für trivial-mechanische Tracks: Link-Fixes, Verweis-Updates,
      Ticket-Annotation `#nr` an bestehender Requirement-ID,
      README-Tabellen-Einträge, Hygiene-Welle, Test-Skelett strikt entlang
      Vorlage. Voraussetzung: `risk_class: low`, mode `combined`, kein
      Verhaltens-Code-Diff. Default-Wahl für Low-Hanging-Fruits — **nicht**
      Sonnet.
- [ ] **Sonnet** für Code-/Spec-Tracks mit echter Logik, Fix-Tracks nach
      Watchdog, Folge-Tracks entlang Vorlage, Mini-Tests mit eigener
      Logik.
- [ ] **Opus** nur bei dokumentiertem Trigger:
      - cross-component architecture
      - unclear specs / many open design questions
      - public API / schema / auth / payment changes
      - repeated Sonnet failure on same track (`previous_handoff_id`)
      - watchdog: structural risk / critical
      - `high_context_track: true`
- [ ] Watchdog-Subagenten bleiben **immer** Opus.
- [ ] Wenn die Modellwahl im Track gegen die Klasse läuft (z. B. Sonnet
      für reinen Link-Fix-Track): Begründung im `model_choice.reason`
      explizit — sonst zurück auf Klassen-Default.
- [ ] **Haiku-Default bei trivial-mechanisch: Begründungspflicht ist ein
      hartes Gate.** Ist der Track trivial-mechanisch (arbeitstag.md
      MODELL-WAHL: Link-/Verweis-Fix, #nr-Annotation, README-Tabelle,
      Hygiene-Welle, Test-Skelett entlang Vorlage) und `default_agent` ist
      nicht `haiku`, MUSS `model_choice.reason` ausdrücklich begründen, WARUM
      nicht Haiku. **Das Gate sitzt auf der FEHLENDEN Begründung, nicht auf der
      Modellwahl:** Sonnet/Opus MIT einem ausdrücklichen `reason` bleiben
      erlaubt (kein Verbot von Sonnet/Opus — das wäre inkonsistent zu
      `schemas.md` Zeile 215, „Kein hartes Verbot"). NUR wenn die Begründung
      fehlt → **Reject**: zurück auf Haiku, kein reflexhaftes Sonnet ohne
      `reason`. (Retro 2026-05-31: Haiku spezifiziert, aber ungenutzt; rein
      deterministische Fixes wie `ruff --fix` brauchen gar kein LLM. Kosten,
      Stand 2026-06: Haiku 4.5 $1/$5 vs. Sonnet 4.6 $3/$15 pro MTok, Quelle
      platform.claude.com/docs — bei Modell-/Preiswechsel neu prüfen.)
- [ ] **Reject-Quote notiert.** Jeder Haiku-Gate-Reject (trivial-mechanischer
      Track ohne Begründung, auf Haiku zurückgestellt) wird gezählt und am
      Tagesende in die Retro übernommen (`arbeitstag.md` Retro-Punkt
      „Kosten / Tokens"). Experiment-Datenpunkt: greift das Gate (Rejects > 0,
      teure Tracks wandern auf Haiku) oder läuft es leer (Rejects = 0, weil
      ohnehin nie ein trivialer Track mit Sonnet kam)?

### A.4 Konventions-Zitate solide?

- [ ] Jede ID in `cited_conventions` existiert in `conventions/` (per grep).
- [ ] Jede ID in `cited_specs` existiert in `specs/` (per grep).
- [ ] Wenn ein Zitat nicht gefunden: **kein Auffüllen aus Gedächtnis** —
      zurück zu A.1 (`missing_required_context`).

### A.5 Programmer Execution Protocol gestaffelt?

- [ ] `programmer_execution_protocol.mode` ist gesetzt und passt zu
      `risk_class`:
      - `risk_class: low` → mode `combined` (1 Checkpoint-Block).
      - `risk_class: medium` → mode `three_compact` (alle Pflichtfelder der
        drei Checkpoint-Gruppen im finalen Handoff; Drei-Block-Gliederung
        empfohlen, nicht erzwungen).
        (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File
        20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren Sektion "Was sich ändert" →
        Entzeremonialisierung)
      - `risk_class: high` → mode `three_compact` + Re-Dispatch
        (PW-8: `two_phase` DEPRECATED). Phase 1 als eigener Subagent-
        Dispatch nur mit `analysis_plan`; Phase 2 als frischer Dispatch
        mit Phase-1-Plan im Brief.
- [ ] Bei `risk_class: high` Re-Dispatch-Pfad: Orchestrator dispatcht
      Phase 2 **erst**, nachdem Phase-1-`analysis_plan` zurück ist und
      intern reviewt wurde. Phase 2 ist ein **frischer** Subagent (neuer
      Worktree), kein Resume.

### A.6 Re-Use vor Re-Read

- [ ] Wenn der Track ein Fix-Track nach Watchdog ist (`previous_handoff_id`
      gesetzt): Sub-Agent Contract referenziert den vorherigen Handoff,
      nicht alle Quellen neu. Cited Specs/Conventions nur, soweit der
      Fix-Befund sie konkret berührt.

---

## §B Handoff-Validierung (nach Subagent-Rückkehr)

Direkt nach Subagent-Rückkehr, vor Merge-Gate. Mangel → einmaliger Reject
+ Re-Dispatch mit konkreter Mangelliste. Zweiter Mangel → **Halt zu Nic**.

### B.1 Handoff-Block überhaupt geliefert?

- [ ] Antwort enthält einen **parsebaren** ` ```yaml `-Fence, dessen Inhalt
      mit `contract_kind: handoff` beginnt.
- [ ] Dieser Fence ist der **letzte inhaltliche Block** der Antwort. Nach
      dem schließenden ` ``` ` folgt **kein** inhaltlicher Zusatz (kein
      „Hoffe das hilft", keine Zusammenfassung, kein Folge-Vorschlag).
      Reine Whitespace-Zeilen sind tolerierbar. Verstößt der Subagent
      dagegen, ist der Handoff **nicht maßgeblich** → Reject mit Hinweis
      auf diese Regel.
- [ ] `contract_id` matched den Sub-Agent Contract.
- [ ] `status` gesetzt.

### B.2 Felder vollständig?

**Pflicht-Felder** (immer da):

- [ ] `steps` enthält 3–5 Zeilen.
- [ ] `files_changed` gesetzt.
- [ ] `outside_whitelist_attempted` explizit (auch `[]`).
- [ ] `acceptance_criteria_met` deckt **alle** AC-IDs aus §2 ab. **Fail-closed
      (PW-12):** Feld **fehlt ganz**, ist **leer**, ODER lässt eine §2-AC-ID aus →
      **Reject + Re-Dispatch**, kein stiller Pass. Ein Merge mit fehlendem
      `acceptance_criteria_met` ist genau die #371/#377-Lücke (Halb-Merge schloss
      das Ticket). „Kein Feld" ≠ „erfüllt".
- [ ] `related_echoes_checked` mit einer Aussage pro Anker (oder Null-Fall, siehe B.5).
- [ ] `entry_path_probe_result` gesetzt (siehe B.5).
- [ ] `watchdog_hints` gesetzt (`lenses_relevant` + `diff_summary`).
- [ ] `worktree_path` matcht eine der zwei Worktree-Familien gemäß **Schicht 1 S1.2**
      (Auto `agent-<id>` ODER RAT-21-Manuell `t<nr>`, PW-87; Regex-Literal nur dort).
- [ ] `lint_clean` gesetzt (`true` / `false` / `not_applicable`). Bei
      Python-Tracks mit `lint_command` (§2): `false` ohne Begründung → **Reject**
      (Selbst-Gate vor Watchdog, STYLE-2). Nicht-Python-Tracks: `not_applicable`.
      **RAT-30, Teil 5:** Der Self-Gate (ruff + lint-imports) ist bindend UND — solange
      pytest advisory ist (nur `closes-guard` required) — muss vor dem Merge zusätzlich
      die **volle pytest-Suite lokal grün** sein (`python3 -m pytest -q`, repo-weit,
      kein `-k`-Filter). Siehe Merge-Gate in `commands/arbeitstag.md`.

**Optional-Felder** — fehlen ist **kein** Reject-Grund, leeres `[]` ist
verschwendete Output-Token. Wenn inhaltslos, wird das Feld weggelassen.
Wenn das Feld **mit Inhalt** geliefert wird, muss der Inhalt sauber sein:

- `spec_touches` / `convention_touches` — nur wenn berührt
- `open_questions` / `risks_noticed` — nur wenn vorhanden
- `lenses_not_applicable` (Watchdog Hints) — entfällt; nicht-Requested-Linsen schweigen implizit

### B.3 Checkpoint-Validation

- [ ] `checkpoints`-Block vorhanden, mode entspricht §2.
- [ ] Mode `combined`: ein Block, alle Mindest-Felder gefüllt
      (`task_understanding`, `files_changed`, `acceptance_criteria_status`,
      `local_style_observed`).
- [ ] Mode `three_compact`: alle Pflichtfelder der drei checkpoint_fields-
      Gruppen (`analysis_plan`, `implementation_done`, `validation_handoff`)
      vorhanden. **Reject NUR bei fehlenden Pflichtfeldern, NICHT bei flacher
      Gliederung** — die Drei-Block-Gliederung unter den Labels ist EMPFOHLEN
      für Lesbarkeit, nicht erzwungen; ein flacher Handoff mit allen required-
      Feldern ist konform.
      (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File
      20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren Sektion "Was sich ändert" →
      Entzeremonialisierung)
- [ ] **CARVE-OUT High-Phase-1** (`risk_class: high`, `status:
      awaiting_orchestrator_review`, §B.6): Hier bleibt der **explizite
      `analysis_plan`-Block PFLICHT** — der Phase-1-Plan ist realer operativer
      Konsument der Plan-Abgrenzung (Orchestrator bewertet ihn, bevor Phase 2
      dispatcht wird). Die PW-79-Lockerung der Gliederung gilt NICHT für
      Phase-1; sie betrifft nur den medium-Final-Handoff und den
      High-Phase-2-Final-Handoff.
      (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File
      20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren Sektion "Was sich ändert" →
      Entzeremonialisierung; Antiberater RISKANT-1 Carve-out)
- [ ] Mode `two_phase` ist DEPRECATED (PW-8). Bei `risk_class: high` läuft
      stattdessen `three_compact + Re-Dispatch`: Phase 1 als eigener Subagent
      nur mit `analysis_plan`-Block (Block-Pflicht, siehe Carve-out oben),
      Phase 2 als frischer Subagent mit vollständigem three_compact-Output.
- [ ] `local_style_observed` ist gesetzt — entweder mit konsistenten
      Befunden oder `inconsistencies_found: [...]`-Liste.
- [ ] `planned_files_to_change` (analysis_plan) ⊆ `write_allowed_files`.
      Sonst: Reject mit Mangelliste.
- [ ] `files_changed` (Top-Level Handoff, siehe schemas.md:86-88) ⊆
      `write_allowed_files`. Sonst: siehe §B.4.
      (PW-7-Begleit-Edit 2026-06-21: korrigiert SSoT-Drift — files_changed
      ist NICHT in implementation_done, sondern Top-Level.)
- [ ] **PW-7 RATIFIZIERT 2026-06-21:**
      `analysis_plan.blast_radius_probe.whitelist_delta.additional_files`
      leer ODER vollständig in `write_allowed_files` enthalten ODER der Brief
      trägt `whitelist_extended_by_orchestrator: true` als Re-Dispatch-Confirm.
      Sonst: Reject mit Mangelliste „Whitelist-Extension nicht im Re-Dispatch
      nachgezogen" — Re-Use vor Re-Read, `previous_handoff_id`.

### B.4 Scope eingehalten?

- [ ] **Diff-Prüfung gegen merge-base, nicht blind gegen main:**
      ```
      git -C <worktree_path> fetch origin main
      git -C <worktree_path> diff --name-only origin/main...<branch>
      ```
      Die Drei-Punkte-Form `A...B` nutzt implizit die merge-base — sie
      listet **nur die Track-Änderungen** und ist robust gegen Drift in
      `origin/main`. Die Zwei-Punkte-Form `main..<branch>` würde bei
      veraltetem lokalem `main` falsche Listen produzieren.
- [ ] **Commit existiert wirklich (gestaged ≠ committet):** Ist `files_changed`
      im Handoff nicht-leer, der `git diff origin/main...<branch>` oben aber
      **leer** (oder `<branch>`-HEAD == merge-base), hat der Subagent nur
      **gestaged statt committet** — `status: done` mit „Commit" ist dann falsch.
      Der Commit-Behauptung **nicht** trauen, immer gegen den echten Diff/`git log`
      prüfen. Reagiere: Reject + Re-Dispatch „committe deine gestagte Arbeit"
      (Re-Use vor Re-Read, `previous_handoff_id`). Belegt 2× (Photo-Buddy + #335,
      2026-06-06): zwei unabhängige Agenten meldeten Commit, hatten aber nur
      gestaged → schlüpfte durch, weil ∅-Diff trivial jede Whitelist erfüllt.
- [ ] Die Liste enthält ausschließlich Pfade aus `write_allowed_files`.
      `read_context_files` dürfen **nicht** im Diff erscheinen — ein
      Edit darin ist scope_breach.
- [ ] `outside_whitelist_attempted` ist `[]`. Wenn nicht: Halt zu Nic
      (Ownership-Tabelle stimmt nicht — neu schneiden).
- [ ] `worktree_path` ist nicht der Shared-Root.

### B.5 Inhaltliche Konsistenz

- [ ] Jedes `acceptance_criteria_met[*].met: true` hat `evidence` mit
      konkretem Verweis (Datei:Zeile / Test-ID / Befehl).
- [ ] **Mengen-AC braucht erschöpfenden Beleg (PW-12).** Enthält der AC-Text einen
      Quantor (*alle / jede / keine / sämtliche /* vollständige Migration), genügt
      **kein Einzelverweis** als `evidence` — verlangt ist ein **erschöpfender Befund
      über alle N Fälle mit Null-Treffer-Ausgabe** (z. B. `grep -rc "<muster>" … = 0`,
      Test über alle Instanzen). Ein Beleg auf *eine* von *N* Stellen ist `partial`,
      nicht `true` (#377: 1/10 stale 422 mit `met:true` wäre so gefallen).
- [ ] `spec_touches`: falls Spec angefasst, ist Ticket-Annotation
      (`#<nr>`) im Diff sichtbar.
- [ ] `related_echoes_checked`: pro Anker aus §2 entweder „konsistent" mit
      Kurz-Begründung **oder** konkreter Befund. Befund ist eigenes
      Folge-Ticket, **nicht** Mit-Edit.
- [ ] **Null-Fall:** Enthielt §2 **keine** `related_echo_anchors`, ist
      `related_echoes_checked: []` erlaubt — aber nur mit explizitem
      Marker `related_echoes_reason: "no related_echo_anchors in contract"`.
      Fehlt dieser Marker bei leerer Liste, ist das ein Reject-Grund
      (Subagent hat Echo-Anker übersehen vs. es gab keine — beides muss
      sichtbar sein).
- [ ] **`entry_path_probe_result` gesetzt und konsistent zu §1:**
      - `status: probed` → `entry_point` + `evidence` Pflicht. Evidence
        muss den Live-Entry-Pfad belegen (Integration-Test-ID,
        Smoke-Befehl, Beobachtung am System) — nicht „pytest grün" allein.
      - `status: lower_level` → `entry_point` + `evidence` + `reason`
        Pflicht; nur legitim wenn §1 `required: false` ODER der Subagent
        begründet, warum Live-Probe heute technisch nicht praktikabel ist.
        Watchdog-Linse 7 prüft die Begründung kritisch.
      - `status: not_applicable` → `reason` Pflicht; nur legitim wenn §1
        `required: false`. Wenn §1 `required: true` und Handoff
        `not_applicable` meldet: Reject mit Mangelhinweis.
      - **PW-16 — Schreib-Verifikation:** Wenn §1
        `write_verification_required: true`, MUSS der Handoff `write_proofs`
        als Liste mit `len(write_proofs) == len(write_targets)` liefern
        (Codex-Bruch: Single-Proof für Multi-Store-Service ist
        False-Pass — ein PUT-Proof gegen routine.json darf den ungeprüften
        Store-Pfad nicht grünmalen). Jeder Eintrag braucht `target`,
        `command_run`, `before`, `after`, `exit_or_http`. „Service startet
        + lädt Datei" ist KEIN write_proof. Wenn §1
        `write_cleanup_required: true`, MUSS `write_cleanups` als Liste
        gleicher Länge folgen — jeder Eintrag belegt die Wiederherstellung
        des Ausgangszustands. Fehlt eins, ist die Karte unvollständig →
        Reject. Auslöser: 2026-06-07-Vorfall (Eltern-Chat ~14 Min stumm
        nach SVC-5-Etappe-1, „verifiziert" hieß nur Lesen).

### B.6 Stop-Reason-Behandlung

Bei `status: stopped`:
- `scope_breach` / `wrong_worktree` → Halt zu Nic.
- `spec_violation` → Spec-Halt; Spec-Track aufmachen.
- `convention_needed` → Convention-Track.
- `acceptance_not_reachable` → Ticket Contract neu schneiden.
- `missing_context` → zurück zu §A.1.
- `needs_escalation` → Orchestrator entscheidet: Re-Dispatch mit Opus,
  oder Halt zu Nic.

Bei `status: awaiting_orchestrator_review` (three_compact + Re-Dispatch
Phase 1, PW-8):
- analysis_plan inhaltlich prüfen (siehe §B.3).
- Bei OK: Phase 2 als **frischen** Subagent dispatchen (neuer Worktree,
  neuer Branch wird im Dispatch erzeugt), Contract-ID inkrementiert auf
  `Sn+1`, Phase-1-Plan im Brief eingebettet.
- Bei Korrekturbedarf: Phase 1 wiederholen mit konkreter Mangelliste
  (zählt als ein Re-Dispatch im Sinne von B.7).

### B.7 Re-Dispatch-Regel

Beim **ersten** Mangel pro Track: ein Re-Dispatch mit:

```
RE-DISPATCH. Dein erster Handoff war unvollständig. Konkrete Mängel:
- <Mangel 1>
- <Mangel 2>
Der Sub-Agent Contract (§2 unten) ist unverändert. Du arbeitest im
selben Worktree weiter. Liefere den vollständigen Handoff-Block.
```

Beim **zweiten** Mangel: kein dritter Versuch. **Halt zu Nic.**

---

## §C Watchdog-Ready Summary (vor Watchdog-Aufruf)

Wenn B sauber durchgelaufen ist, baut der Orchestrator die Summary aus
`schemas.md §4`. Sie wird **aus den Contracts gespeist**, nicht durch
Neu-Lesen.

**Hook-Voraussetzung (PW-39).** Der Watchdog-Subagent-Dispatch unterliegt
dem PW-31-Dispatch-Hook (`~/.claude/hooks/dispatch_status_guard.py`). Der
Watchdog ist im Hook-Schema **kein** eigener `contract_kind` — er läuft als
`contract_kind: subagent` (mit `parent_ticket`) in `mode: read`, im
Stand-alone-/watchdog-Fall als `subagent_no_ticket` + Skip-Marker. Volle
Aufruf-Vorlage und beide Pfade: `commands/watchdog.md` Abschnitt „Hook-
Header". Der Watchdog-Prompt muss diesen Header **vor** der eigentlichen
Aufgabe tragen, sonst wirft der Hook Reject.

- [ ] `lenses_requested` ist eine **Teilmenge** der sieben Linsen. Default
      ist **nicht** „alle sechs". Begründung pro Linse Pflicht.
- [ ] `lenses_skipped` nennt **nur** Einträge mit nicht-trivialer Begründung
      (konsistent mit schemas.md §4). Standard-Skip („Diff hat kein neues
      Verhalten" etc.) bleibt implizit; `[]` = alle Nicht-Requested-Linsen trivial.
- [ ] `checkpoints_summary` destilliert aus §3
      (`local_style`, `deviations_from_plan`, `unexpected_findings`,
      `remaining_risks`).
- [ ] Watchdog-Prompt enthält **nicht**: ganze Specs, ganzes Repo,
      Session-History, frühere Contracts anderer Tickets. Nur:
      Ticket Contract + Handoff + diff_scope + im Diff berührte
      Spec-/Convention-Slices + Summary.
- [ ] `orchestrator_caveats` ist `[]` oder nennt konkrete Unsicherheiten.

Dann Aufruf wie in `commands/watchdog.md` beschrieben, mit
`branch:<name>` als Scope-Argument und der Summary als Begleitkontext.

---

## §D Provider Health / Sequential Mode

Leichte Regel gegen wiederholten API-Overload. Lebt im Board als
`api_mode: parallel | sequential`.

**Trigger für `sequential`-Wechsel:**

- [ ] Zwei auffällige parallele Failures hintereinander:
      Provider-Overload (529), 0-Token-Tote, Tool-Result kommt mit
      Fehler statt Handoff zurück.

**Sonderfall — 529 beim ersten Dispatch einer Cluster-Welle:**

- [ ] Wenn der **erste** Dispatch eines geplanten Cluster-Bündels mit 529
      stirbt (bevor andere Dispatches überhaupt gestartet sind): **90s
      pausieren**, dann **einen einzelnen Probe-Dispatch** statt sofort
      den gesamten Cluster. Wenn Probe durchgeht: Cluster fortsetzen.
      Wenn auch Probe 529: in Sequential-Mode wechseln. Das fängt den
      Burst-Fall ab, ohne den 2-Failures-Trigger abzuwarten.

**Verhalten im `sequential` Mode:**

- [ ] Keine **neuen** parallelen Dispatches starten.
- [ ] Laufende erfolgreiche Tracks **nicht** stoppen.
- [ ] Board markieren: `api_mode: sequential`, mit Zeitstempel und Grund.
- [ ] Erst nach einer **stabilen Runde** (1 Track erfolgreich durch)
      darf wieder parallel dispatched werden — Board zurück auf
      `api_mode: parallel`.

**Anti-Pattern:** denselben Overload-Fehler mehrfach in Folge auslösen,
weil „der nächste Track ist ja klein". Sequential-Wechsel ist günstiger
als drei tote Subagent-Calls.

---

## §E Decision-Discovery beim Sessionstart

Pro Session **einmal**, vor dem ersten Backfill: schauen, was xbuddy an
Decision-Ablagen schon hat — nicht erfinden.

- [ ] `## Offene Punkte`-Sektion in den heute relevanten Specs lesen.
      Das ist die etablierte Form (mind. 10 Specs nutzen sie).
- [ ] `gh issue list --label blocked` — welche Tickets warten gerade auf
      Klärung.
- [ ] Wenn beim Backfill/Preflight/Handoff eine offene Entscheidung
      auftaucht: klassifizieren (siehe `schemas.md §5` Tabelle) und an
      die **bestehende** Stelle binden. **Kein** neues ADR-Verzeichnis,
      keine neue `decisions/`-Datei eigenmächtig anlegen — solche
      Entscheidungen landen erstmal als Halt zu Nic mit Issue +
      `blocked`-Label.

---

## §F Token-Strategie-Meldungen

Die drei Token-Spar-Strategien (Tier-Routing Haiku, Schichten-Caching,
Schemas trimmen) plus Cluster-Dispatch sind **Annahmen, keine Garantien**.
Wenn eine **nicht aufgeht**, ist das **kein still durchzuwinkender
Befund** — der Orchestrator meldet es Nic explizit, mit konkreter
Beobachtung und Zahl.

### F.1 Haiku-Stufe scheitert für eine Track-Klasse

- [ ] **Trigger:** Haiku liefert auf derselben Klasse zweimal Reject in
      Folge (Schema-Disziplin fehlt, Verweise nicht aufgelöst, oder
      derselbe Schritt mehrfach falsch).
- [ ] **Meldung an Nic:** „Klasse <X> ist für Haiku nicht geeignet —
      2× Reject auf Track T<n>, T<m>. Konkrete Symptome: <Mängel>.
      Empfehlung: Klasse zurück auf Sonnet."
- [ ] **Sofortmaßnahme:** Track auf Sonnet umstellen; Haiku-Trigger für
      diese Klasse aus dem session-internen Default streichen
      (`arbeitstag.md` selbst erst nach Nic-OK ändern).

### F.2 Schichten-Caching greift nicht

- [ ] **Trigger:** nach **3+ Subagent-Dispatches** in derselben Session
      sind die Input-Tokens pro Dispatch **nicht** spürbar gefallen.
      Was „spürbar" heißt: bei wiederholten Dispatches sollten
      Schicht-1-Tokens auf ~10% des Erstwerts kollabieren. Wenn
      Dispatch 2/3/4 ähnlich teuer wie Dispatch 1 ist, greift Caching
      nicht.
- [ ] **Meldung an Nic:** „Schichten-Caching scheint nicht zu greifen.
      Beobachtung: Dispatch 1 = X Input-Tokens, Dispatch 2 = Y, Dispatch
      3 = Z (Werte aus Tool-Ausgabe). Erwartet wäre Dispatch 2+ bei
      ~10% von 1. Vermutung: Tool reicht `cache_control` nicht durch
      oder Schicht 1 ist nicht byte-stabil."
- [ ] **Sofortmaßnahme:** Keine. Caching-Hebel als „nicht greifend"
      einstufen, andere Hebel werden wichtiger.

### F.3 Schemas zu eng nach Trim

- [ ] **Trigger:** Sonnet (oder Haiku) rejected auf demselben Track ≥2×
      wegen **fehlender Felder, die per Schicht-1-Verweis herleitbar
      sein sollten**. Beispiel: Subagent meldet „weiß nicht, welche
      Stop-Rules gelten" trotz S1.1.
- [ ] **Meldung an Nic:** „Verweis auf Schicht 1 für Feld <X> war für
      <Modell> nicht selbsterklärend. Konkrete Symptome: <Mängel>.
      Empfehlung: <X> zurück in den Track-Contract aufnehmen,
      Verweis-Pattern zurücknehmen."
- [ ] **Sofortmaßnahme:** Track manuell mit den fehlenden Feldern
      anreichern, weiter dispatchen.

### F.4 Cluster-Dispatch erzeugt vermehrt 529

- [ ] **Trigger:** seit Aktivierung des Cluster-Bündels treten 529-Bursts
      häufiger auf als vorher (Vergleich: vorher 1× in 6 Wochen).
      Konkret: ≥1 Burst pro Woche.
- [ ] **Meldung an Nic:** „Cluster-Dispatch korreliert mit 529-Bursts.
      Beobachtung: <Daten>. Empfehlung: zurück auf Trickle-Dispatch,
      Cache-Vorteil opfern."
- [ ] **Sofortmaßnahme:** auf Trickle-Dispatch zurück (Dispatches
      serieller starten, nicht im Bündel).

**Regel über allen vier Meldungen:** Knappe Meldung mit **Zahl**
(wieviele Rejects, wieviele Input-Tokens, wann), nicht „funktioniert
nicht so gut". Ohne Zahl keine Strategie-Anpassung.
