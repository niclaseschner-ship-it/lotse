---
description: Reift status:spec-Tickets bis status:ready — parallel zu /arbeitstag, mit Nic als einzigem Stempel-Setzer. Zwei harte Phasen: Koordinations-Block (autonom) ↔ Nic-Block (ununterbrochen, du schreibst nur Labels).
argument-hint: "[optional: einzelne Issue-Nr; leer = alle offenen status:spec]"
---

# /arbeitstag-prep — Tickets reif machen, Nic als einziger Stempel

Du reifst Tickets von `status:spec` auf `status:ready` — das Handoff-Signal an
`/arbeitstag`. Der Stempel ist die **Membran** (WORKFLOW.md#stempel-membran):
`/arbeitstag` nimmt nur Gestempeltes, du nur Ungestempeltes.

**Zwei Regeln über allem:**
1. **Du stempelst NIE aus eigenem Urteil.** Nur Nics ausdrückliches `stempeln`
   im Nic-Block löst `gh issue edit … --add-label status:ready` aus
   (false-ready-Schutz, WORKFLOW.md#handoff). Der `watchdog-prep` urteilt, du zeigst,
   **Nic entscheidet**.
2. **Nic-Per-Karte-Verdikt ist Pflicht; du handelst nie autonom.** Das ist der
   ROOT der Regel — **nicht** die literale Sequenz „eine Karte, dann die
   nächste". Der Schutz ist dreiteilig: (a) **kein autonomes Handeln** —
   keine Karte wird ausgeführt, die Nic nicht entschieden hat; (b) **jede Karte
   trägt ein explizites Nic-Verdikt** (im Chat einzeln, im HTML-Loop per
   Radio — beide erfassen ein Per-Karte-Verdikt); (c) der Skill **führt nur die
   erfassten Verdikte aus und SURFACED Mid-Ausführungs-Funde** (Re-Verdict-Flip,
   fehlgeschlagener Edit) **statt blind zu stempeln**. Der Rückfall am
   2026-06-05 war genau autonomes Handeln OHNE Nic-Verdikt — nicht zu wenig
   Sequenz (`feedback_ticket_review_modus`). Belegt: #1150 (erledigt-statt-
   Stempel gefangen), #1172 (gefangener Fehl-Edit).
   (ENTSCHEID-File Paket-Sektion „Die Gabel" Zweig A → Regel auf ihren ROOT
   re-artikuliert; literale Sequenz-zwischen-Karten ist NICHT der Schutz)

## Die zwei Phasen — harter Riegel, kein Vorsatz

Du arbeitest in genau zwei Modi und **nennst bei jedem Schritt, in welchem du
bist**. Der Übergang ist eine **prüfbare Bedingung**, keine Absicht.

### KOORDINATIONS-BLOCK (autonom, kein Nic-Input nötig)
Hier sammelst und bereitest du vor — du darfst alles Read-only + Subagenten:
1. **Kandidaten sammeln:**
   `gh issue list --repo ${LOTSE_PROJECT_REPO} --label "status:spec" --state open --json number,title,labels`
   (oder die im Argument genannte Einzel-Nr).
   **Trigger-vertagte ausklammern, aber sichtbar halten (PW-3):** Kandidaten mit Label
   `blocked` sind bewusst bis zu einem Trigger geparkt — **dispatch sie NICHT** an
   `watchdog-prep` (spart den teuren Lauf). Statt sie zu verstecken, **druck eine
   sichtbare Zeile** pro Lauf: `⏸ Deferred (blocked): #261 — Trigger: <…>` (Trigger aus dem
   `## Wiederaufnahme-Trigger`-Heading des Issue-Body). So bleiben sie auf dem Radar — feuert
   der Trigger, entfernt jemand `blocked` und das Ticket kehrt regulär in die Kandidatenliste
   zurück. **Nicht still wegfiltern** (das begräbt sie — Codex-Einwand der PW-3-Runde).

   **Werft-aktive ausklammern, aber sichtbar halten (PW-25 RATIFIZIERT 2026-06-21):**
   Kandidaten mit Label `in-werft` werden gerade von `/werft` (F1-F4) gehalten —
   **dispatch sie NICHT** an `watchdog-prep` (Werft hat eigene F5-Reife-Probe,
   PW-43). Statt sie zu verstecken, **druck eine sichtbare Zeile** analog `blocked`:
   `⏸ Deferred (in-werft): #<nr> — Werft-Lauf seit <iso>` (Zeitstempel aus
   `gh issue view <nr> --json timelineItems` für das `in-werft`-LabeledEvent).
   **Verwaiste `in-werft`-Labels** (Werft-Lauf > 24h ohne F5-Stempel) bekommen
   zusätzlich Warn-Marker `⚠️` und werden Nic im Koord-Block vorgelegt — prep
   schließt das NICHT selbst (das ist Werft-F1-Cleanup-Job).

   **Epic-Herzschlag (Feature-Epics):** Zusätzlich zu den `status:spec`-Kandidaten
   sammelst du die offenen Initiativen:
   `gh issue list --repo ${LOTSE_PROJECT_REPO} --label epic --state open --json number,title,labels,body`.
   Pro offenem Epic rendere eine **Herzschlag-Karte** für den Nic-Block, die genau
   ein Verdikt **treiben/halten/töten** erzwingt (bei `needs-triage`: nur die
   Klassifikations-Frage Prozess/Code). Regeln, Karten-Form und die
   Verdikt-Aktionen (treiben → Kind-Ticket `status:spec` + `Part of #<epic>`;
   halten nur mit datiertem Re-Visit-Trigger; töten → schließen) stehen
   **vollständig in `conventions/epics.md` → „Der Herzschlag"** — hier NICHT
   duplizieren. Epics tragen kein `status:*`, brauchen also **keinen prep-Claim
   und keinen Watchdog-Dispatch**.
2. **Pro Kandidat zuerst CLAIMEN, dann `watchdog-prep` dispatchen** (PW-33, 2026-06-09):
   - **Claim setzen** (Lock-Semantik — niemand anders prept dieses Ticket parallel):
     ```bash
     gh issue edit <nr> --repo ${LOTSE_PROJECT_REPO} --remove-label status:spec --add-label status:spec-in-progress  # status_rollback_guard:skip prep-claim
     ```
     `status_rollback_guard.py` erlaubt diesen Übergang nur mit Skip-Marker und exakt diesen Labels.
   - **Dann Dispatch** (Agent-Tool, `subagent_type: "watchdog-prep"`).
     Subagent-Prompt MUSS am Anfang einen `contract_kind: subagent`-Block mit
     `parent_ticket: ${LOTSE_PROJECT_REPO}#<nr>` und `mode: read` tragen
     (PW-31). Sonst lehnt `dispatch_status_guard.py` ab. Watchdog-prep liefert
     den parsebaren `prep_verdict`-YAML-Fence. **Du grepst NICHT selbst doppelt** —
     eine Quelle pro Achse ist der Agent.
   - Bei Watchdog-Lauf-Fehler ODER wenn die nächste Koordinations-Runde abgebrochen
     wird: **Release zurück** (`-spec-in-progress +spec` mit Skip-Marker), sonst
     bleibt das Ticket gelockt.
3. **Verdikt parsen + Karte rendern** (Format unten). Reconcile-`dup` und
   `re-litigation` werden zu **Schließ-/Halt-Empfehlungen**, nicht zu Stempel-Karten.
4. **Vorbedingung: Spec-vor-Karte (PW-26-RATIFIZIERT 2026-06-09).**
   Keine Karte wird Nic vorgelegt, ohne dass die zugehörige Spec auf
   `origin/main` liegt — oder die Karte ist explizit eine **Wahl-Karte (🔱 ARCH-WAHL)**
   (Architektur-Wahl) oder **Wahl-Karte (⚠️ KOORD-WAHL, Cross-Spec)** (Spec-Pfad-Konflikt).
   Die alte „Pflicht, nicht Optional"-Disziplin (Nic n=3 am 2026-06-09) wird
   durch eine Sequenz-Vorbedingung ersetzt: die Frage „muss ich Spec-PR
   mergen?" stellt sich nie — sie ist die einzige Form, in der überhaupt
   eine Stempel-Karte entsteht. Mechanik-Sperre: `status_rollback_guard.py`
   (`check_spec_binding` + `check_spec_path_exclusive` + Hash umfasst
   `verdict_repo_sha`). Vier Sub-Pfade je nach Verdikt:

   - **`reif: spec-gemergt` UND `architecture_class: nachzeichnen`** → direkt
     Stempel-Karte mit SPEC-DIFF von main. Kein Spec-PR nötig.

   - **`reif: spec-fehlt` UND `architecture_class: nachzeichnen`** (Spec-Inhalt
     ist aus Constitution + RAT-Bestand ableitbar: Wortlaut-Schärfung,
     Mechanik-Klausel für WAS/WIE-Spalt, Refactor-Spec für gebauten Pfad) →
     **Spec-PR autonom schreiben + mergen**. Branch `spec/<nr>-…`, Änderung
     unter `specs/` oder `conventions/` (Label `type:docs` für conventions/),
     `gh pr create` mit **`Refs #<nr>`** (NICHT `Closes`), Watchdog-Checks
     abwarten, `gh pr merge --merge`. `closes-guard` lässt den Spec-Ausgang
     durch (`Refs` + Pfad). Nach dem Merge: Verdikt-Comment-Schema um
     `spec_merge_sha: <merge-sha>` ergänzen (für `rollback-koord`-Probe).
     Karte zitiert SPEC-DIFF von main.

   - **`architecture_class: wahl`** (A/B-Optionen im Body, neuer Buddy,
     Privacy/Familie, RAT-Konflikt-Verdacht, OPEN-* ohne entscheidbaren Pfad)
     → **Wahl-Karte (🔱 ARCH-WAHL) vor Spec-Merge.** Kein autonomes Mergen — der Hook
     blockt `gh pr merge` für `spec/<nr>-…`-Branches mit `architecture_class:
     wahl` bis Nic einen `arch_choice`-Marker postet. Wahl-Karte (🔱 ARCH-WAHL) trägt
     beide (oder drei) Varianten + Argumente + Empfehlung; Nic wählt
     `A` / `B` / `halt`; Skill mergt dann den Spec-PR mit der gewählten
     Variante und produziert in der nächsten Runde die Stempel-Karte.

   - **`reif: keine-spec-noetig`** — zwei Sub-Klassen:
     - **Drift-gegen-Spec**: Watchdog-Befund „Code weicht von bindender
       Spec ab" (z. B. `routine.py:142` bricht `ROU-15`). Verdikt zitiert
       die Spec strukturiert (`reif_spec_path`/`reif_requirement_id`/…) +
       füllt `drift_target`. Karte zeigt zusätzlich eine **DRIFT-Zeile**.
       Direkt Stempel-Karte, kein Spec-PR.
     - **Reines Chore**: Dead-Code/Format/Type-Hint ohne Spec-Anker. Verdikt
       füllt `chore_evidence` (Datei:Zeile + Convention/CLAUDE.md-Verweis).
       Hook prüft, dass die Datei auf `origin/main` existiert. Direkt
       Stempel-Karte.

   - **`reconcile: dup` oder `re-litigation`** → keine Stempel-Karte, sondern
     Schließ-/Halt-Karte. Spec-vor-Karte-Probe greift nicht.

5. **Pre-Merge-Probe Cross-Spec (PW-26-RATIFIZIERT, Codex-Bruch 3).** Bevor
   du `gh pr merge` auf einen `spec/<nr>-…`-Branch absetzt: der Hook prüft
   automatisch, ob die berührten `specs/`/`conventions/`-Pfade in offenen
   `status:in-progress`-Tickets als `reif_spec_path` zitiert werden. Treffer
   → Hook deniert mit Hinweis auf das konfligierende Ticket. Produziere statt
   der Stempel-Karte eine **`cross-spec-koord`-Karte**: „Spec X wird parallel
   von #N1 konsumiert — Reihenfolge entscheiden". Nic wählt; der nachgereihte
   Spec-PR wartet.

6. **Re-Verdict nach autonomem Spec-Merge.** Wenn der Spec-PR die Frage löst,
   lass `watchdog-prep` einmal neu laufen (mit aktuellem
   `verdict_repo_sha = origin/main` und ergänztem `spec_merge_sha`).
   Die Karte trägt am Ende den **finalen** Stand, nicht den Anfangs-Stand.

### Maturation-Runden (Berater-Mechanik — PREP-12)

Braucht ein Ticket auf dem Weg zur Stempelreife einen Berater-Lauf (Wahl-
Reifung, OPEN-*-Auflösung, Nachschärfung nach `halt: berater-runde`), gilt
`conventions/prep-lifecycle.md` **PREP-12**: benannte berater-runde-Teile
(Subagent-Header, R1-Lese-Disziplin, BRICHT/RISKANT-Semantik, Runden-Deckel),
**Codex-Sanity-Pass in JEDER Runde** (Crawl-Schranke Pflicht; Opus-Fallback als
schwächer kennzeichnen), Voll-Pingpong nur bei den PREP-12-Triggern (a)–(c),
pro Lauf den `antiberater_sanity:`-Marker als Issue-Comment oder Retro-Zeile
(Mess-Pflicht Welle 1). Details wohnen in der Konvention — hier nicht duplizieren.

### Das GATE (Übergang Koordination → Nic)
**Der Nic-Block startet erst, wenn JEDE Karte des Stapels ein Verdikt trägt.**
Solange auch nur eine Karte `watchdog-prep: pending` hat, bleibst du im
Koordinations-Block. Prüf das explizit, bevor du Nic die erste Karte zeigst:
„Alle N Karten haben ein Verdikt? → ja → Nic-Block." Kein Teilstapel.

### NIC-BLOCK (Fokus geschützt, ununterbrochen)

**Karten zu Nic sind FERTIG** (PREP-11). Du legst NUR Karten vor, die
stempel-/wahl-/schließbar sind — keine `[zurück]`-Action. Wäre die Karte
zurückzuschicken, geht sie gar nicht zu Nic; der Skill hat das im Koord-
Block aufgefangen.

1. **Jede Karte trägt ein explizites Nic-Verdikt — das ist der Schutz, nicht
   die literale Reihenfolge.** Im **Chat-Modus** (Default unter N≥7) legst du
   die Karten einzeln vor und wartest je auf das Verdikt. Im **HTML-Loop**
   (Default ab N≥7, siehe „HTML-Karten-Loop" unten) zeigt der Browser den
   Stapel; Nic gibt **pro Karte** ein Radio-Verdikt und submittet als Batch.
   Beide Wege erfassen ein Per-Karte-Verdikt — keine Stapel-*Entscheidung*
   (Nic entscheidet jede einzeln), nur ein gebündelter *Transport*. Der Skill
   führt danach nur die erfassten Verdikte aus.
   (ENTSCHEID-File Paket-Sektion „Die Gabel" Zweig A → Radio = expliziter
   Per-Karte-Verdikt; Batch ist Transport, nicht Stapel-Entscheidung)
   Verdikt-Optionen je Klasse:
   - **Stempel-Karte:** `stempeln` / `parken`
   - **🔱 ARCH-WAHL:** `A` / `B` / `C` / `halt`
   - **⚠️ KOORD-WAHL:** `a` / `b` / `parken`
   - **Schließen-Karte:** `schließen` / `parken`
2. **Einziger erlaubter Seiteneffekt in diesem Modus: Nics Verdikt ausführen.**
   **SURFACE statt blind stempeln (Batch-Schutz):** Taucht beim Ausführen der
   erfassten Verdikte ein Fund auf, den Nic so nicht entschieden hat —
   Re-Verdict-Flip (ein Ticket ist inzwischen erledigt, vgl. #1150), ein
   fehlgeschlagener Edit (#1172), ein Build-Claim (RAT-21) —, **hältst du an
   und legst den Fund Nic vor**, statt das alte Verdikt blind auszuführen. Das
   gilt im HTML-Batch besonders: Nic entscheidet alle N, bevor eine ausgeführt
   ist; ein Flip, der erst NACH dem Batch-Submit auffällt, MUSS gesurfaced
   werden, nicht weggestempelt. (Das ist zugleich das Kill-Kriterium des
   HTML-Defaults — siehe „HTML-Karten-Loop".)
   (ENTSCHEID-File Paket-Sektion „Die Gabel" Zweig A → Skill surfaced
   Mid-Ausführungs-Funde statt blind zu stempeln)
   <a id="nic-stamp"></a>
   - `stempeln` → **ZWEI Schritte in der Reihenfolge** (PW-26-RATIFIZIERT
     2026-06-09 — der alte „Falls Spec-PR mergen"-Sub-Absatz fliegt, weil
     Spec-PRs sind zum Stempel-Moment schon auf main):
     1. **prep_verdict-Comment posten**: den vollständigen `prep_verdict`-YAML
        aus dem Watchdog-Output als Issue-Comment, **erste Zeile**:
        `<!-- prep_verdict v1 issue:<NR> sha:<HASH> -->`. HASH-Form:
        - **PW-26-Schema** (Verdikt trägt `architecture_class:`):
          `sha256(json({verdict, axes, verdict_repo_sha, architecture_class}, sort_keys=True))[:16]`.
        - **Legacy PW-30** (Verdikt ohne `architecture_class:`):
          `sha256(json({verdict, axes}, sort_keys=True))[:16]`.
        Plus YAML-Fence mit dem Verdikt + `stamp_repo_sha:
        <git -C ${LOTSE_PROJECT_ROOT} rev-parse origin/main>` (separat — `verdict_repo_sha`
        bleibt IMMUTABLE aus dem Prep-Moment, Codex-Bruch 4).
     2. **Build-Claim-Respekt vor Release (RAT-21, PW-70 — ENTSCHEID-File
        `20260624-1430-RATIFIZIERT-pw70-claim-early-reservierung.md`):** Vor dem
        Label-Flip prüfen, ob das Ticket inzwischen `status:in-progress` trägt — dann
        hat eine Build-Session es reserviert (reserve-at-plan). **Halt**, KEIN Flip:
        Comment „von Build-Session reserviert (`status:in-progress`), prep-Release
        ausgesetzt" ans Ticket, Befund in die Karte. Schließt den #1075-Pfad (frisch
        gereiftes Ticket, das Build parallel greift).
        **TOCTOU-Verkürzung (Antiberater Pass-2):** Der Status-Read und der Flip in
        Schritt 3 sind zwei Operationen — ein Build-PR kann dazwischen landen. Den
        `status:in-progress`-Read **unmittelbar vor** dem `gh issue edit` wiederholen,
        nicht am Karten-Anfang cachen. Mechanische Hook-Verriegelung (prep-release
        deniert bei aktuellem `status:in-progress`) ist RAT-21-Reopen-Trigger, falls
        das Disziplin-Fenster reißt.
     3. **Label-Flip — prep-Release auf ready** (Skip-Marker, PW-33):
        `gh issue edit <nr> --repo ${LOTSE_PROJECT_REPO} --remove-label status:spec-in-progress --add-label status:ready  # status_rollback_guard:skip prep-release-forward (Nic-Stempel)`.
        Hook prüft jetzt: prep_verdict-Comment liegt + Hash matcht + Spec-Binding
        (`check_spec_binding` semantisch, RAT-11-Heading-Filter mechanisch) +
        kein Spec-/Decision-Drift seit `verdict_repo_sha`. Ohne grün → deny.
   - `parken` → Label `blocked` o. Ä. nach Nics Wort. Plus prep-Release zurück auf
     `status:spec`, sonst bleibt das Ticket als gelockt + blocked sichtbar.
   - **🔱 ARCH-WAHL** (`architecture_class: wahl`) — Nic wählt `A` / `B` /
     `C` / `halt`: poste `<!-- arch_choice v1 issue:<nr> choice:A -->` als
     Comment am Ticket (Hook akzeptiert nur A/B/C; `halt` heißt: Halt-Karte,
     kein Spec-PR). Dann mergt der Skill den Spec-PR mit der gewählten
     Variante, ein neuer Watchdog-Lauf liefert das aktualisierte Verdikt, in
     der nächsten Charge erscheint die Stempel-Karte. Wahl-Karten produzieren
     **kein** `prep_verdict`-Comment — die PW-30-Existenzprobe verhindert
     mechanisch, dass eine Wahl-Karte versehentlich zur Stempel-Karte mutiert.
   - **⚠️ KOORD-WAHL** — Nic wählt `a` / `b` / `parken`:
     - bei Cross-Spec-Reihenfolge: der nachgereihte Spec-PR bleibt offen, das
       Ticket bleibt auf `status:spec-in-progress` bis das vorlaufende fertig
       ist.
     - bei Rollback-Koord (Folge-Merges berühren die Spec-Datei): siehe
       „Rollback bei Spec-Fehlern" unten.
   - **Schließen-Karte** — Nic wählt `schließen` / `parken`:
     `gh issue close <nr> --repo ${LOTSE_PROJECT_REPO} --reason "<dup|completed|not_planned>"`.
     **Kein** `status:*`-Labelwechsel (RECON-3 bleibt unangetastet).

**Ausnahme — Nic findet Mangel an einer als FERTIG vorgelegten Karte:**
Dann ist der Pre-Flight-Block (PREP-11) falsch gefüllt gewesen. Skill notiert
Mangel als Comment am Issue, **prep-Release back** (`-spec-in-progress
+spec`), und nimmt das Ticket in die nächste Koordinations-Runde mit
geschärftem Befund. **Bei „Spec falsch"** (Nic findet Fehler im autonom
gemergten Spec-PR): zusätzlich Rollback-Pfad starten (siehe „Rollback bei
Spec-Fehlern" unten). Das ist eine Korrektur-Disziplin, nicht eine reguläre
Aktion auf der Karte.
3. **Keine neue Koordination im Nic-Block → Halt.** Der Schutz ist, dass du im
   Nic-Block **nicht neu koordinierst** (kein `gh issue list`, kein `git grep`,
   kein neuer Subagent-Dispatch, kein neues Verdikt erfinden) — **nicht** die
   literale Lücke „zwischen zwei Karten". Im Chat-Modus heißt das: nichts
   zwischen den Karten. Im HTML-Loop heißt es: während Nic den gerenderten
   Stapel entscheidet und während du seine erfassten Verdikte ausführst, kommt
   kein Koordinations-Tool-Call dazu. Merkst du, dass du koordinieren willst:
   Stop, das gehört in die nächste Koordinations-Runde. (Einzige Ausnahme: ein
   gesurfacedter Mid-Ausführungs-Fund nach Punkt 2 — der wird Nic vorgelegt,
   nicht selbst koordiniert.)
   (ENTSCHEID-File Paket-Sektion „Die Gabel" Zweig A → kein autonomes Handeln;
   literale Sequenz-zwischen-Karten ist NICHT der Schutz)
4. **Neu-Eingänge wandern auf die nächste Charge.** Fällt Nic mitten im Block
   etwas Neues ein, notier es als Karte für die **nächste** Koordinations-Runde —
   der laufende Stapel wird zuerst abgearbeitet (Vorbild `arbeitstag.md` „Aufgabe
   taucht mitten auf").

## HTML-Karten-Loop (Render-Medium ab N≥7)

Ab **N≥7 Karten** pro Prep-Lauf ist der HTML-Browser-Loop der **Default**-Weg,
um den Stapel im Nic-Block zu rendern (darunter: Chat-Default, oder Nic-Wahl pro
Lauf). Die v5-Felder und der Per-Karte-Verdikt-Schutz bleiben unverändert
(`conventions/prep-lifecycle.md` PREP-10 „Render-Medium der v5-Karten"); der
Browser ist nur die Anzeige, die durable Wahrheit bleibt das GitHub-Issue.
(ENTSCHEID-File Paket-Sektion „Zweit-Gabel" → gethresholdeter Default ab N≥7)

### Ablage + Aufruf

- **Server-/Template-Code liegt unter `tools/prep-karten/`** im Projekt-Repo —
  **NICHT** im lotse-Repo. `deploy.sh` (lotse, SSoT) deployt nur
  agents/commands/contracts/hooks an den Runtime-Ort; ein `tools/…` im
  Framework-Repo käme dort nie an. Der Command ruft den Server über den
  **absoluten Pfad** (`${LOTSE_PROJECT_ROOT}/tools/prep-karten/…`).
  (ENTSCHEID-File Paket-Sektion „Konvergiert" → Ablage `tools/prep-karten/`;
  Command ruft absoluten Pfad)
- **Port `:8765`** — ephemeres Operator-Tool, **außerhalb** des
  Service-Bereichs 5000-5099 (`conventions/ports.md` PORT-1/2 bindet dort
  nicht). Der Server lebt nur für die Dauer des Nic-Blocks, danach wird er
  beendet. **Bindung:** der Server hört über Loopback hinaus, damit Nic ihn
  übers Tailnet erreicht — bewusste Ausnahme zu PORT-3 (`127.0.0.1` für
  Komponenten); das Bau-Ticket bindet auf das **Tailscale-Interface**
  (Tailnet-IP), nicht offen auf `0.0.0.0`, um LAN-Exposition zu vermeiden.
  (ENTSCHEID-File Paket-Sektion „Konvergiert" → :8765 ephemeres Operator-Tool,
  außerhalb 5000-5099; Pass-2 PORT-3-Loopback-Hinweis)
- **Mess-Naht:** Im HTML-Modus postet der Skill **pro Karte einen durablen
  Issue-Comment** via `POST http://<tailscale-ip>:8765/post-comment` —
  **einziger Live-Erzeugungs-Weg** (PREP-10, `make_durable_comment` im Tool
  ist die einzige Quelle der Comment-Form). Payload:
  `{"issue_number": <int>, "card": <card-Objekt>, "decision": "<Verdikt>"}`.
  Der Skill prüft die 200-Antwort; bei Fehler bricht er die Runde ab.
  Der Skill komponiert die `card_pre_flight`-Form **nicht mehr von Hand**
  und ruft `gh issue comment` **nicht direkt** auf — das Tool übernimmt
  beides vollständig (`<!-- card_pre_flight v1 … -->`-Marker + `#<nr>`-Header
  + `→ [Aktion]`-Zeile). `followup_pain` misst **spätere Korrektur-Comments
  nach** dem Marker — nicht Nics Submit-Verdikt selbst; Marker und Verdikt
  dürfen daher nicht im selben Comment kollabieren. So messen alle drei
  Metriken korrekt (kein `preflight_missing`-False-Positive). Verbindlich in
  `conventions/prep-lifecycle.md` PREP-10 „Mess-Naht im HTML-Modus".

### Vier Pflicht-Härtungen (Klauseln)

1. **Vor-Ausliefern-Check (Render-Probe vor Nic).** Bevor der gerenderte Stapel
   Nic gezeigt wird, läuft `node --check` auf das Server-/Template-JS **und** ein
   **DOM-Stub-Render** des kompletten Stapels (alle Karten-Klassen, headless).
   Bricht das (Syntax oder Render), geht der Loop **nicht** an Nic — Fallback auf
   Chat-Modus oder Fix-Runde. Das fängt den Klassen-Bug deutsche-Anführung
   (`„…“`) vs. gerades JS-Quote (`"`), der eine Karte still leer rendern würde.
   (ENTSCHEID-File Paket-Sektion „Konvergiert" → Vor-Render-Check: node --check +
   DOM-Stub gegen deutsche-Quote-vs-gerades-Quote-JS-Bug)
2. **Closes/Creates nur mit Freigabe.** Schreibt der Loop am Ende Issues
   (`gh issue close`, `gh issue create`), braucht das eine **Chat-Freigabe pro
   Runde** — der Auto-Mode-Classifier liest die HTML-Antwort-Datei **nicht** als
   Intent. Kein stiller Massen-Schreibvorgang aus dem Browser heraus; der
   Per-Karte-Verdikt-Schutz (Regel 2 oben) gilt auch für die Ausführung der
   gebündelten Verdikte. (Label-Flips/Comments mit gültigem `prep_verdict`
   laufen wie gehabt.) **Kein skill-verankerter Auto-Mode-Freigabe-Pfad** —
   RAT-22 hält „Auto-Mode" als Defer und die Regeln hart; eine etwaige
   operatorseitige `autoMode`-Setzung ist Nics Umgebung, nicht Skill-Ledger.
   (ENTSCHEID-File Paket-Sektion „Konvergiert" → Closes/Creates: Chat-Freigabe;
   Pass-2 RAT-22-Patch)
3. **`answers/` zuerst lesen — vor allem anderen.** Der Server schreibt Nics
   Verdikte still nach `${LOTSE_PROJECT_ROOT}/tools/prep-karten/answers/`
   (`answers-latest.json` + Zeitstempel-Kopie); es gibt **keine**
   Benachrichtigung. Also: nach jedem Karten-Loop **und zu Beginn jeder
   Fortsetzung** als allererstes `ls -lt …/answers/` — bevor du neu koordinierst,
   Karten baust oder Nic einen Stand meldest. Belegfall 2026-08-11: sechs
   abgeschickte Verdikte lagen 38 Stunden ungelesen, in der Zeit gingen dieselben
   sechs Fragen zweimal erneut an Nic und die Bilanz meldete „11 Entscheidungen
   warten", als sechs davon längst beantwortet waren.
4. **Kein pkill-Selbstkill.** Zum Beenden des Servers **nie** ein `pkill`/
   `kill`-Muster verwenden, das die **eigene** Bash-Zeile mit-matcht (Pattern
   trifft den eigenen Prozess → `exit 144`). Server über die gemerkte **PID**
   (aus dem Start) beenden, nicht über einen Namens-/Port-Pattern-Kill.
   (ENTSCHEID-File Paket-Sektion „Konvergiert" → kein pkill-Selbstkill)

## Karten-Formate v5 (Anzeige-Artefakt; SSoT bleibt das GitHub-Issue)

Drei Karten-Klassen, alle ampel-first und empfehlungs-first.
Form bindend in `conventions/prep-lifecycle.md` PREP-10 und PREP-11
(RATIFIZIERT 2026-06-21, xbuddy#1055). **Karten zu Nic sind FERTIG** —
kein `[zurück: was fehlt]` als Aktion. Wäre eine Karte zurückzuschicken,
geht sie gar nicht zu Nic — der Skill schärft im Koord-Block nach.

### Stempel-Karte (Default — Spec liegt auf main, Nic stempelt oder lehnt)

```
#<nr> <Titel>
TREIBER:     <Quelle>: <konkreter Befund>
EMPFEHLUNG:  stempeln

RISIKO:        🟢 niedrig  (Schaden klein · Wahrscheinlichkeit selten)
VERTRAUTHEIT:  🟢 LEGO  (<Begründung, bei LEGO mit n=…>)

WIRKUNG:  <ein Satz: was es bewirkt>
KONTEXT:  <ein Satz: woran es anknüpft>

→  [stempeln]   [parken]                                  Belege: <Datei:Zeile> · <Datei:Zeile>
```

Beispiel:

```
#758  ROUTINE-21c — Focus-Halbsatz streichen
TREIBER:     Watchdog Linse-1 (Spec-Drift): Code .focus() entfernt, ROUTINE-21c nennt es noch.
EMPFEHLUNG:  stempeln

RISIKO:        🟢 niedrig  (Schaden klein · selten)
VERTRAUTHEIT:  🟢 LEGO  (Spec-Nachzieher, n-ter Drift-Fix in diesem Buddy)

WIRKUNG:  Spec wird an gebauten Code nachgezogen — Cursor-Sprung am Display weg.
KONTEXT:  knüpft an ROU-15 + Live #728, keine neue Setzung.

→  [stempeln]   [parken]                                  Belege: routine.md:704 · routine-anpassen.js:813-821
```

### Wahl-Karte (zwei Sub-Klassen — `architecture_class: wahl` oder Koordinations-Wahl)

Wahl-Karten produzieren **kein** `prep_verdict`-Comment (PW-30-Hook-Sperre
gegen versehentlichen Stempel). Header-Marker unterscheidet zwei Sub-Klassen:

**🔱 ARCH-WAHL** (Architektur-Wahl vor Spec-Merge):

```
#<nr> <Titel>                                                              🔱 ARCH-WAHL
TREIBER:     <Quelle>: <konkreter Befund>
EMPFEHLUNG:  <A | B | C>

KERNFRAGE:  <ein Satz>

A · <Kurzname>    <Halbsatz Mechanik> — <Halbsatz Trade-Off>
B · <Kurzname>    <Halbsatz Mechanik> — <Halbsatz Trade-Off>          ← empfohlen
C · <Kurzname>    <Halbsatz Mechanik> — <Halbsatz Trade-Off>

→  [A]   [B]   [C]   [halt: berater-runde]
```

Nic-Aktion: postet `<!-- arch_choice v1 issue:<nr> choice:A -->` als Comment;
Skill mergt dann Spec-PR mit der gewählten Variante, neue Charge zeigt
Stempel-Karte. `halt` heißt: kein Spec-PR, `/berater-runde` ist der nächste
Schritt.

**⚠️ KOORD-WAHL** (Cross-Spec-Reihenfolge oder Rollback-Pfad):

```
#<nr> <Titel>                                                              ⚠️ KOORD-WAHL
TREIBER:     <Quelle>: <konkreter Befund>
EMPFEHLUNG:  <a | b>

KERNFRAGE:  <Reihenfolge zu #<m> | Rollback-Pfad bei Spec-Fehler>

a · <Option>    <Mechanik> — <Trade-Off>                              ← empfohlen
b · <Option>    <Mechanik> — <Trade-Off>

→  [a]   [b]   [parken]
```

Subsumiert die zwei Bestands-Fälle:
- **Cross-Spec-Reihenfolge** (PREP-6 Komponente 2): Spec-Pfad parallel
  konsumiert; Nic entscheidet Reihenfolge.
- **Rollback-Koord** (PREP-7 nicht-trivial): Folge-Merges berühren die
  Spec-Datei; Nic wählt Folge-Reverts vs. Vorwärts-Fix.

### Schließen-Karte (dup / erledigt / überholt)

```
#<nr> <Titel>
TREIBER:     <Quelle>
EMPFEHLUNG:  schließen — <dup von #MM | erledigt durch <commit> | überholt>

WIRKUNG:  <ein Satz: warum kein Bau nötig>

→  [schließen]   [parken]                                  Belege: <#MM-PR oder commit-sha>
```

Nic-Aktion: `[schließen]` führt `gh issue close <nr>` aus — **kein**
`status:*`-Labelwechsel (RECON-3 bleibt unangetastet, siehe
`conventions/prep-lifecycle.md` PREP-1).

### Pflicht-Felder + Sprachregeln (PREP-10)

**TREIBER ist Pflicht** mit Quelle + konkretem Befund. Kanonische Formen:

- `Nic <Datum>: <Stichwort>`
- `Watchdog Linse-<N> (<Linsen-Name>): <Befund>`
- `Werft #<idee>: <Stichwort>`
- `Live-Bug #<nr> (<Kanal>): <Beobachtung>`
- `Lego-Offensive: <Sorte> n=<N> erreicht`
- `Folge aus #<vorigem-Ticket>: <Stichwort>`

**Ampel-Stempel** (Risiko + Vertrautheit) sind Pflicht bei Stempel-Karten:

| Risiko | Schaden × Wahrscheinlichkeit |
|---|---|
| 🟢 niedrig | klein · selten |
| 🟡 mittel | klein · oft  ODER  groß · selten |
| 🟠 hoch | groß · oft  ODER  irreversibel · selten |
| 🔴 kritisch | irreversibel · oft — Empfehlung `stempeln` verboten, wird zur WAHL-Karte (machen-mit-Mitigation vs. nicht) |

| Vertrautheit | Bedeutung |
|---|---|
| 🟢 LEGO | Sorte existiert n≥2, Convention trägt |
| 🟡 NEU-MISCHUNG | bekannte Stücke neu komponiert |
| 🟠 EXPERIMENT | neue Mechanik, brauchen Probe |
| 🔴 OFFEN | wir wissen nicht wie — /berater-runde nötig |

**Schwellen xbuddy-konkret:** „irreversibel" = Daten-Verlust ohne Backup;
„oft" = ≥1× pro Familien-Tag; „selten" = ≤1× pro Familien-Woche.

**Sprachregel Wahl-Karte:** Trade-Off in Freitext, **Konsequenz statt
Mechanik**. Keine Spec-IDs im Variante-Text (nur in Belegen). Form: „wird
teuer ab 3. Buddy", nicht „ROU-34 zeigt auf ROU-12".

### Pre-Flight-Block (PREP-11 — Schreib-Reflex am Issue)

Vor jeder Karte rendert der Skill einen HTML-Kommentar als
Selbstreflexion am Issue:

```
<!-- card_pre_flight v1 issue:<nr> kind:stempel|wahl|schliessen -->
- [x] Spec liegt auf main (origin/main:<sha>)                                  [stempel]
- [x] Bestand-Grep gemacht — keine offene Karte zum gleichen Thema
- [x] RAT/Memory durchgesehen — keine ratifizierte Klausel wird übergangen
- [x] Risiko in zwei Achsen einzeln bewertet, dann Gesamtnote                  [stempel]
- [x] Vertrautheit bewertet (bei LEGO: Geschwister gezählt n=…)                [stempel]
- [x] Empfehlung folgt aus den Achsen, keine Improvisation
- [x] Karte ist FERTIG — kein „zurück" implizit
- [x] Jede Variante ist baubar (eigener Spec-Pfad denkbar)                     [wahl]
- [x] Trade-Off pro Variante in einfachen Worten (Konsequenz, kein ID-Jargon)  [wahl]
<!-- /card_pre_flight -->
```

Welle 1 ohne mechanischen Hook (befristet, Nic-Setzung 2026-06-21
„Disziplin appellieren statt mechanisch prüfen"). Mess-Pflicht via
`tools/card_form_quote.py` (xbuddy-prozess#69); Welle-1-Uhr startet erst
mit der ersten messbaren Bilanz. Welle-2-Auslöser und -Pfade
(Hook ODER Form-Überarbeitung) siehe PREP-11.

Risiko-Sperre: Empfehlung `stempeln` ist verboten bei 🔴 kritisch
(irreversibel · oft) — solche Karten werden WAHL-Karten (machen-mit-
Mitigation vs. nicht-machen).

### Disziplinen aller Karten

- **TREIBER/RISIKO/VERTRAUTHEIT/WIRKUNG/KONTEXT** kommen direkt aus den
  `axes`/`eine_frage_an_nic` des Verdikts — du erfindest nichts dazu.
- **EMPFEHLUNG ist Pflicht.** Du legst Nic nie eine Karte neutral vor:
  - `stempeln` — alle Achsen grün, Risiko nicht kritisch.
  - `parken` — Blocker offen, Wiederaufnahme braucht externes Ereignis.
  - `A` / `B` / `C` (Wahl-Karte) — Empfehlung mit `← empfohlen`-Marker
    an der Variante.
  - `schließen — <Grund>` — dup/erledigt/überholt, RECON-3-Beleg im
    `Belege:`-Anker.
- **SPEC-DIFF zitiert IMMER origin/main**, nie einen Entwurf. Stempel-Karten
  existieren nur, wenn die Spec auf main liegt (PW-26 Sequenz-Vorbedingung).
- **Keine Implementations-Linie auf der Karte** (Codex-Bruch 6 / PW-26):
  Spec=Verhalten, Convention=WIE. Wenn die Spec mehrere konforme Linien zulässt,
  ist das per Definition Architektur-Wahl → Wahl-Karte (🔱 ARCH-WAHL), nicht Stempel-Karte.
- Karte ändert nie das Issue. Erst Nics Verdikt im Nic-Block schreibt etwas.

## Disziplinen — schon im Verdikt verdrahtet

Die load-bearing Disziplinen sind **die fünf Achsen des `watchdog-prep`** (REIF
strukturiert, SUBSTANZ, RECONCILE, LEDGER, ARCHITECTURE_CLASS) plus die drei
Hook-Sperren in `status_rollback_guard.py` (`check_spec_binding` semantisch +
`check_spec_path_exclusive` + `arch_choice`-Pflicht bei `wahl`). Du musst sie
nicht separat fahren — du musst die Karte **ehrlich** rendern. Bei einer Stempel-
Karte gilt: alle Achsen grün, RISIKO nicht irreversibel+hoch, SPEC-DIFF zitiert
main 1:1. Bei `wahl`: Wahl-Karte (🔱 ARCH-WAHL) produzieren, keinen `prep_verdict`-Comment
posten. Bei Cross-Spec-Treffer: `cross-spec-koord`-Karte.

**Existenz-Grep-Reflex** zusätzlich (Vorbild `arbeitstag.md` Phase 0): bevor du
ein Ticket überhaupt aufnimmst, kurz prüfen, ob sein Deliverable nicht schon auf
main steht — der `watchdog-prep`-RECONCILE deckt das ab, aber wenn dir beim
Sammeln etwas auffällt, nimm es ernst.

## Rollback bei Spec-Fehlern (PW-26 Komponente E)

Wenn Nic im Nic-Block `zurück: Spec falsch` sagt (autonom gemergter Spec-PR hat
einen Fehler):

1. **Vor-Probe auf Folge-Touches.** Bevor du blind revertierst, lies
   `git -C ${LOTSE_PROJECT_ROOT} log <spec_merge_sha>..origin/main -- <betroffene-pfade>`.
   `spec_merge_sha` steht im prep_verdict-Comment (Schema-Feld).

2. **Trivialer Fall (kein Folge-Touch)**:
   - `git checkout -b revert/<nr>-spec`
   - `git revert -m 1 <spec_merge_sha>` (RAT-9 `--merge` macht den Revert sauber)
   - `gh pr create --base main --title "Revert spec/<nr> — <Grund>" --body "Refs #<nr>  ... " --label type:docs`
     (Label `type:docs` falls `conventions/` betroffen, closes-guard greift über
     den Spec-Ausgang.)
   - Nach Checks-grün: `gh pr merge --merge`.
   - Label-Reset: `gh issue edit <nr> --remove-label status:spec-in-progress
     --add-label status:spec  # status_rollback_guard:skip prep-release-back`.

3. **Nicht-trivialer Fall (Folge-Merges berühren die Spec-Datei)**: produziere
   **`rollback-koord`-Karte** in der nächsten Charge:

   ```
   #<nr> <Titel>   ⚠️ ROLLBACK-KOORD (Spec-Revert blockiert)
   SPEC-MERGE-SHA: <sha>
   FOLGE-MERGES SEIT DEM:  <PR# (Titel)>, <PR# (Titel)>, …
   OPTIONEN:
     (a) Folge-Reverts erst — <welche PRs>
     (b) Vorwärts-Fix als neuer Spec-PR — <Skizze>
   EMPFEHLUNG: <a | b> — <ein-Satz-Begründung>
   →  [a]   [b]   [parken]
   ```

   Nic entscheidet. Skill landet weder Revert noch Vorwärts-Fix autonom — diese
   Klasse ist Architektur-Wahl, die nicht aus RAT ableitbar ist.

4. **Comment am Issue** (durabler Mess-Anker für die 14-Tage-Rollback-Quote):
   ```
   <!-- prep_rollback v1 issue:<nr> spec_pr:<x> rollback_pr:<y> reason:"<text>" -->
   ```
   Das Mess-Skript (Folge-Ticket) zählt diese Marker.

## Abschluss

Wenn der Stapel durch ist: kurze Bilanz an Nic (wie viele gestempelt /
geparkt / als erledigt geschlossen) und was für die nächste Koordinations-Runde
notiert wurde. Du startest **keine** Impl-Tracks — das ist `/arbeitstag`.

**Karten-Form-Bilanz (PREP-11 Mess-Pflicht).** Führe vor der Retro das
Mess-Skript einmal aus und hänge die einzeilige Bilanz an die Retro:

```bash
python3 ${LOTSE_PROJECT_ROOT}/tools/card_form_quote.py
# Beispiel-Ausgabe:
# cards=8 preflight_missing=100% over_14_lines=0% followup_pain=0% (last 7 days)
```

Welle-2-Auslöser (eine Schwelle reißt → neue `/berater-runde`):
`preflight_missing > 10%` · `over_14_lines > 20%` · `followup_pain ≥ 62%`.

**Retro — Pflicht-Abschluss-Schritt.** Schreibe zum Schluss eine kurze
Start/Stop/Continue-Retro über die *Arbeitsweise* dieses Prep-Laufs (Reibung beim
Karten-Rendern, Nic-Block-Fluss, Reconcile/Ledger-Lücken) — Format + Pfad:
`~/.claude/contracts/retro.md` → `~/.claude/retros/JJJJ-MM-TT-arbeitstag-prep.md`.
Die Karten-Form-Bilanz-Zeile gehört an den Anfang der Retro (vor
Start/Stop/Continue), als Welle-1-Beobachtungs-Datenpunkt.
