---
description: Orchestriert einen Arbeitstag mit mehreren parallelen Umsetzungen — konfliktfrei.
argument-hint: (keine Argumente — sondiert den Tag selbst)
---

# ARBEITSTAG — ORCHESTRIERUNG MEHRERER UMSETZUNGEN

## DEINE ROLLE

Du bist der Orchestrator dieses Arbeitstags. Du allein hältst die vollständige
Datei-Landkarte im Kontext. Du baust nicht alles selbst — du planst, verteilst,
serialisierst die geteilten Stellen, führst zusammen. Es gilt die xBuddy-Regelwelt:
Spec vor Code, Gates, Stop-Bedingungen.

## MODELL-WAHL — TOKEN-EFFIZIENZ MIT DER RICHTIGEN STUFE

Ein Arbeitstag verbraucht viele Tokens, weil viele Subagenten parallel laufen.
Wähle das Modell bewusst pro Track-Typ — nicht „alles Opus, sicher ist sicher".

- **Orchestrator (du): immer Opus.** Du hältst die Datei-Landkarte, koordinierst
  Whitelists, übersetzt Watchdog-Verdikte in Gate-Entscheidungen. Modellwechsel
  mitten in der Session geht für dich ohnehin nicht.
- **Watchdog-Subagenten (`architecture-watchdog`): immer Opus.** Spec-Drift
  und Genre-Drift sind subtil, Sonnet übersieht das eher. Pro Token sehr wertvoll.
- **Code-/Spec-Subagenten — drei Stufen, nach Track-Klasse:**
  - **Haiku 4.5** für **trivial-mechanische** Tracks entlang klarer Vorlage:
    Markdown-Link-Fixes nach Datei-Move, veraltete Verweis-Updates
    (FAM-11 → FAM-12), Spec-Ticket-Annotation `#nr` an bestehender
    Requirement-ID, README-Tabellen-Einträge nach neuer Komponente,
    Hygiene-Welle zum Abschluss, Test-Skelett strikt entlang vorhandenem
    Pattern. Mode `combined`, `risk_class: low`. Haiku ist Default-Wahl
    für Low-Hanging-Fruits — nicht Sonnet.
  - **Sonnet 4.6** für Code-/Spec-Tracks mit echter Verhaltens-Logik,
    Fix-Tracks nach Watchdog, Folge-Tracks entlang etablierter Vorlage,
    Konventions-Patches, Mini-Tests mit eigener Logik.
  - **Opus** bei: erstmaligen Architektur-Entscheidungen,
    Cross-Komponenten-Verkabelung, unclear specs / vielen offenen
    Designfragen, public API / schema / auth / payment changes,
    repeated Sonnet failure auf demselben Track, Watchdog-Verdikt
    `strukturell` / `kritisch` (Fix-Track-Eskalation), `high_context_track: true`.
- **Modell explizit setzen** beim Agent-Dispatch (`model: "haiku"` /
  `"sonnet"` / `"opus"`). Default ohne Override erbt Opus vom Parent — was
  teuer ist.
- **Codex / andere Engines: deferred until signal.** Wir erweitern den
  Engine-Pool nicht spekulativ. Eine neue Coding-Engine kommt erst, wenn
  ein klares Signal trägt: (a) das aktuelle System übersieht relevante
  Fehler systematisch; (b) Sonnet/Opus sind für eine klar abgrenzbare
  Task-Klasse messbar zu teuer/langsam; (c) der neue Engine-Typ bringt
  konkret Nutzen für mechanische, eng gescopte Arbeit, die Sonnet heute
  nicht trifft. Bis dahin: Opus = Orchestrator/Watchdog/Architektur,
  Sonnet = Code/Fix/Folge. Kein Verbot, nur kein eigenmächtiger Ausbau.

Wenn unsicher, ob Sonnet reicht: **Probieren beim Folge-Track**, nicht beim
ersten Brocken. Erster Brocken setzt das Vorbild (Test-Naht, Anker-Form,
Service-Layout), Folge-Tracks adoptieren — die sind Sonnet-tauglich.

## SESSIONSTART — TAG SONDIEREN, BEVOR DU PLANST

Warte nicht, bis dir eine fertige Liste gegeben wird. Zwei Schritte zuerst:

**A. Sammle selbst, was anstehen könnte.** Sieh im Repo nach Kandidaten:
- **Übernehmbare Tickets = `status:ready`, offen**
  (`gh issue list --label "status:ready" --state open`). Das ist die **harte
  Grenze**: /arbeitstag implementiert **ausschließlich Gestempeltes**. Der Stempel
  ist die Membran zwischen `/arbeitstag-prep` (reift Tickets) und `/arbeitstag`
  (setzt um) — WORKFLOW.md, „Der Stempel ist die Membran". Pro Kandidat das
  `status:`-Label mitführen:
  - `status:ready` → **das Implementierungs-Signal**: Spec reviewt und gemerged,
    Implementation darf heute starten. Das sind die Impl-Kandidaten des Tags.
  - `status:spec` / ungestempelt → **nicht dein Revier.** Reifen ist Sache von
    `/arbeitstag-prep` — nicht im arbeitstag mitziehen oder selbst stempeln.
    Erscheint dir ein ungereiftes Ticket dringend, **melde es an Nic / den prep**,
    aber **dispatche es nicht**. (Früher zog der arbeitstag alle offenen Issues
    ein, weil `status:spec` unzuverlässig war und Tickets sonst aus dem Tag fielen
    — #298. Diese Lücke schließt jetzt der prep + die `prep-reconcile`-Action; das
    Label trägt wieder, der arbeitstag muss nicht mehr selbst breit sammeln.)
  - `status:in-progress` / `status:in-review` → laufender PR; zur Kenntnis, nicht
    neu dispatchen.
- offene PRs (`gh pr list`) — was hängt im Review, was ist fast fertig;
- offene oder stale Branches;
- TODO/FIXME im Code, fehlgeschlagene Tests, bekannte Chores.

Render daraus eine **nummerierte Kandidatenliste** — je ein Satz, mit grober
Einschätzung (Größe, Abhängigkeit, fasst es geteilte Dateien an?).

**B. Frag Nic, was IHM wichtig ist.** Stell explizit:
- Was steht heute an, das im Repo nicht sichtbar ist (Termine, externe
  Freigaben, was gerade drückt)?
- Welche der Kandidaten sind heute relevant, welche nicht?
- Gibt es ein Ziel des arbeitstags oder eine klare Priorität?
- **Hat heute ein dickes Brett Vorrang vor mehreren leichten Wins?** Ein
  arbeitstag ist elastisch (darf über mehrere Kalendertage laufen) — „muss
  heute fertig" ist keine Bremse. Frag explizit, ob der arbeitstag ein Brett tief
  bohren soll; ein Brett wird dann intern gefächert (interface-first, siehe
  Parallelisierungs-Vertrag), nicht zu unzusammenhängenden Mini-Tracks zerfasert.
- **Was soll Nic am echten System selbst ausprobieren können?** (Konkreter Schritt am
  echten System, nicht „grüne Tests". Daraus ergibt sich die vertikale
  Scheibe — siehe nächste Sektion.)

Dann schneidet ihr **gemeinsam** aus Kandidatenliste + Nics Input die
endgültige arbeitstag-Liste. **Nic entscheidet, was rein- und rausfällt** — du
schlägst vor, du sammelst nicht ungefragt 15 Sachen in den arbeitstag. Halte die
Liste klein genug, dass sie mit dem WIP-Limit (siehe unten) machbar ist.
Erst wenn die Liste steht, geht es in Phase 0.

## DER ARBEITSTAG ENDET MIT DER VERTIKALEN SCHEIBE — NICHT MIT DER UHR

Ein arbeitstag ist **so lang, wie eine vertikale Scheibe braucht**. Er ist
**nicht** an einen Kalendertag, „den Abend" oder „heute" gebunden — sein Ende
ist eine **Bedingung, kein Zeitpunkt**: die Scheibe steht und Nic hat sie am
echten System geprüft (siehe „AM ENDE"). Solange die Scheibe nicht steht,
läuft der arbeitstag weiter — über Stunden, über mehrere Kalendertage, egal.

**Wellen/Stücke sind interne Meilensteine, NICHT das Ende.** Ist ein dickes
Brett interface-first in Wellen zerlegt (Rückgrat → Stücke), wird **durch alle
Wellen durchgezogen**, bis die Scheibe ganz steht. Nicht nach jeder Welle (oder
jedem gemergten PR) den Sack zumachen — kein Deploy/Bilanz/Cleanup/Retro pro
Meilenstein. Der Abschluss-Block läuft **einmal**, wenn die Scheibe fertig ist.
Den Sack nach einem Teil-Meilenstein zuzumachen ist genau die Bastelei, die wir
abstellen.

Nic muss am Ende eine Funktion **selbst benutzen und prüfen** können — nicht
„Code, der theoretisch trägt", sondern ein durchgehender Weg von Eingabe zur
sichtbaren Wirkung. Das ist der erste Filter über jede arbeitstag-Liste.

Pro Aufgabe explizit beantworten (gehört in Phase 0):
- **Wo schneidet diese Aufgabe die vertikale Scheibe?** Eingabe → System →
  sichtbares Ergebnis. Nur Backend ohne Trigger ist keine Scheibe. Nur UI ohne
  echte Daten ist keine Scheibe. Reines Refactoring ist keine Scheibe.
- **Was kann Nic mit einem realen Schritt prüfen?** Eine Nachricht schicken,
  ein Bild hochladen, das Display ansehen, im Chat eine Antwort bekommen —
  etwas Konkretes, das ohne dich reproduzierbar ist.
- **Die Scheibe wird NICHT zerschnitten, damit sie „in einen Tag passt".** Es
  gibt keine Uhr — der arbeitstag läuft, bis die Scheibe steht. Dünner
  schneiden nur, wenn eine echte durchgehende Teil-Scheibe für sich nützlich
  ist (eine dünne Treppe), niemals um vorzeitig zumachen zu können.

Aufgaben ohne vertikale Wirkung (Cleanup-Refactor ohne Konsument,
Infrastruktur „für später", „könnte mal nützlich sein") gehören nicht in den
arbeitstag — außer sie sind harte Voraussetzung für eine andere Aufgabe des
arbeitstags, und das wird beim Schnitt benannt.

## VORAUSSETZUNGEN, LOGINS, KONFIGS — DER WEG IST DER ELTERN-CHAT

Alles, was wir an Infos, Logins, Tokens, Geräte-Bindungen oder Konfiguration
ins System holen — also alles, was eine **Familie 3 oder 4** beim Onboarding
genauso bräuchte — wird über den **Eltern-Chat als Prozess/Funktion** eingezogen.
Nicht von Hand, nicht per `scp`, nicht im Klartext in der Shell, nicht „nur
für unseren Pi".

Der Eltern-Chat ist hier der **Testballon für genau die Onboarding-Funktionen,
die wir später sowieso brauchen**. Jeder Hack daneben verbrennt diesen Test
und macht den Pi zum von Hand verdrahteten Einzelstück
(vgl. [[feedback-onboarding-flow-prerequisites]], [[project-xbuddy-eltern-chat]]).

Konkret beim Aufgaben-Schnitt:
- Braucht die arbeitstag-Aufgabe einen neuen Key, Token, Geräte-Pin,
  Kalender-Account, Anbieter-Login, CA-Vertrauen o. ä. → das ist eine
  **eigene Eltern-Chat-Aufgabe** und Teil der vertikalen Scheibe, kein
  Vorgeplänkel daneben.
- Vorhandene Bausteine wiederverwenden: KI-Anbieter-Onboarding (#33,
  ONB-1…9), Familien-Gruppen-Bindung, Bestätigungswort-Pattern (E-EC-7).
  Fehlt ein Schritt, wird er als Spec im Eltern-Chat-Katalog ergänzt — nicht
  außen herum gelöst.
- Geheimnisse landen in der gitignorierten Per-Instanz-Datei, nie im Code,
  nie in den Logs.

**Wenn du erwägst, eine Voraussetzung „eben schnell außenrum" zu erledigen,
ist das ein Halt.** Eltern-Chat-Schritt entwerfen, Nic vorlegen, dann weiter.

## AUFGABEN DES ARBEITSTAGS  (Ergebnis des Sessionstarts)

Format je Zeile: `#Issue — Ziel in einem Satz — Stand (Spec da? Branch da? hängt von welcher Aufgabe ab?)`

1.
2.
3.
4.
5.

## CONTRACT-FIRST FLOW — DER NEUE ARBEITSVERTRAG

Pro arbeitstag-Aufgabe gilt **ein expliziter Kontrakt-Pfad**, bevor ein Subagent
startet. Er ersetzt nicht Phase 0 (Ownership-Tabelle), den Parallelisierungs-
Vertrag, das Merge-Gate oder die Watchdog-Disziplin — er füttert sie mit
Eingaben, die nicht mehr aus dem Subagent-Bericht zurückgerechnet werden müssen.

```
Ticket → Ticket Contract → Operational Preflight → Sub-Agent Contract
       → Sub-Agent Execution → Structured Handoff → Orchestrator Review
       → Watchdog-Ready Summary → Merge-Gate
```

**Quelle der Wahrheit für Schemas und Validierung:** `~/.claude/contracts/`.
Du liest sie zu Sessionstart einmal ein und behandelst sie verbindlich:

- `contracts/README.md` — Überblick und Verzahnung.
- `contracts/schemas.md` — sechs YAML-Schemas (§1 Ticket Contract,
  §2 Sub-Agent Contract, §3 Handoff, §4 Watchdog-Ready Summary,
  §5 Decision Record, §6 Contract Backfill Report).
- `contracts/preflight.md` — §A Vor-Dispatch und §B Handoff-Validierung.
- `contracts/example-T137.md` — vollständiger Beispiel-Durchlauf.

**Claim-PR-at-pick (RAT-15, PW-17) — VOR jedem Subagent-Dispatch:**

Vor dem Posten des Ticket-Contracts und dem Subagent-Dispatch muss der
Orchestrator das Ticket *action-getrieben* auf `status:in-progress` heben.
RECON-3 verbietet jedem Agent (auch dem Orchestrator) das per-Shell-
`gh issue edit` auf `status:*`-Labels — der ratifizierte Pfad ist ein leerer
Draft-PR mit `Closes #<nr>`, der `ticket-status-flow.yml` triggert.

Drei Schritte (Codex-R2-gehärtet — manueller Worktree statt
`isolation:worktree`, weil Auto-Worktree Branch-Bindung bricht):

1. **Manueller Worktree** im xbuddy-Checkout anlegen:
   ```bash
   git -C ${LOTSE_PROJECT_ROOT} worktree add \
     .claude/worktrees/t<nr> -b feature/<branch> origin/main
   ```
2. **Leerer Draft-PR mit `Closes #<nr>`:**
   ```bash
   cd ${LOTSE_PROJECT_ROOT}/.claude/worktrees/t<nr>
   git commit --allow-empty -m "WIP: T<nr> (claim)"
   git push -u origin feature/<branch>
   gh pr create --draft --title "WIP: T<nr>" --body "Closes #<nr>" --base main
   ```
3. **Verify-by-read** (warten bis Action durch, ~5 s):
   ```bash
   gh issue view <nr> --json labels --jq '.labels[].name' | grep -q status:in-progress
   ```
   Fehlt das Label → **Halt**, Track nicht dispatchen, Befund in Retro.

**Cleanup-Pfad bei Track-Abbruch:** `gh pr close <pr-nr>` (ohne Merge) →
`ticket-status-flow` setzt zurück auf `status:ready` MIT Doppelbau-Schutz
(andere offene Closing-PRs werden geprüft, RAT-15 § Workflow-Patch).

**Sicherungsnetz (RAT-15 § D):** `~/.claude/hooks/dispatch_status_guard.py`
ist als PreToolUse-Hook für `Agent` registriert und blockiert Dispatch, wenn
das Ticket nicht auf `status:in-progress` ist oder `parent_ticket` ohne
Repo-Marker bleibt. Die Mechanik ist die positive Seite, der Hook die
negative Versicherung.

**Disziplin auf einer Postkarte:**

- **Kein Subagent ohne Sub-Agent Contract.** Der Subagent-Prompt beginnt mit
  dem YAML-Block aus `schemas.md §2`. Keine freien „mach mal X"-Aufträge mehr.
- **`mode: build` ist Pflicht für /arbeitstag-Subagenten** (PW-31, 2026-06-09).
  Der `dispatch_status_guard.py`-Hook lehnt Subagent-Dispatches ohne `mode:`-Feld
  hart ab. Der Generator-Pfad setzt `mode: build` deterministisch — niemals
  hand-gesetzt fehlend. Reject-Message ist handlungsleitend: „füge `mode: build`
  ein" (nicht „ungültig"). Andere Modi (`read`/`propose`/`formalize`) sind dem
  Skip-Pfad (`contract_kind: subagent_no_ticket`, /berater-runde) vorbehalten —
  /arbeitstag-Tracks nutzen IMMER `mode: build`.
- **Kein Ticket Contract ohne Issue-Comment.** Bestehende Tickets erst durch
  Backfill (`schemas.md §6`, max ~5 Min Recherche pro Ticket). Bei
  `blocked_missing_contract` Label `blocked` setzen, **nicht** Stunden recherchieren.
  **Blocker-Zeile (PW-13):** Wer `blocked` setzt, schreibt in den Issue-Body eine
  Zeile `Blocker: <wer/was> — Auflösung: agent-prüfbar | nic` (klassifiziert den
  *aktuell nächsten* Blocker: kann der Agent die Auflösung selbst feststellen →
  `agent-prüfbar`; braucht es eine Nic-Entscheidung/Freigabe/externe Handlung →
  `nic`). Hier `agent-prüfbar` (Backfill nachholbar).
- **Konventionen werden zitiert, nicht erraten.** Jede ID per `grep` verifiziert.
  Was fehlt, landet in `missing_required_context` — und stoppt den Track.
- **Spec-Werte wörtlich, defensive Abweichung = STOP (Nacht-Lauf 2026-06-22, n=3).**
  Der Brief fordert ausdrücklich: Werte (Ports, URLs, Pfade) aus der konkreten
  `Spec-Datei:Zeile` übernehmen, NICHT aus Plausibilität ableiten; User-sichtbare
  Strings (Umlaute, Labels) bleiben wörtlich wie in der Spec. Kommt einem Subagenten
  ein Spec-Wert „defensiv falsch" vor (Encoding-Sorge, fehlende Infrastruktur), ist das
  ein **STOP + Rückmeldung**, KEINE stillschweigende Abweichung (ASCII-isieren,
  `llm_fn=None`-Default, halluzinierte Tabellen-Werte). Drei Sonnet-Subagenten taten
  genau das in einer Nacht; der Watchdog fing es — der Brief soll es verhindern.
- **Token-Budget pro Contract eingehalten** (`schemas.md` Tabelle): ≤3
  Spec-Slices, ≤5–8 Dateien, ≤10 Conventions, ≤5 AC, ≤5 Stop Rules. Sonst
  `high_context_track: true` mit Begründung **und** Opus.
- **Programmer Execution Protocol gestaffelt nach `risk_class`:**
  - `low` → ein kompakter Combined-Checkpoint im Handoff.
  - `medium` → alle Pflichtfelder der drei Checkpoint-Gruppen (analysis_plan,
    implementation_done, validation_handoff) im finalen Handoff; Drei-Block-
    Gliederung empfohlen, nicht erzwungen.
    (PW-79 RATIFIZIERT 2026-06-30; ENTSCHEID-File 20260630-2035-RATIFIZIERT-pw79-handoff-entzeremonialisieren
    Sektion "Was sich ändert" → Entzeremonialisierung)
  - `high` → **three_compact + Re-Dispatch** (PW-8, xbuddy-prozess#8): Phase 1
    läuft als eigener Subagent-Dispatch nur mit `analysis_plan`. Du liest den
    Plan, bewertest, und startest Phase 2 als **frischen** Subagent mit dem
    Phase-1-Plan im Brief eingebettet. Live-Streaming gibt's nicht — Subagent-
    Calls sind atomar; die zwei Dispatches sind unser Ersatz für Mid-Flight-
    Checkpoints. (Der alte `two_phase`-Pfad „Phase 2 im selben Worktree" ist
    DEPRECATED — SendMessage/Resume existiert nicht, Phase-1-Worktree wird
    ohne Commit auto-gelöscht.)
- **`local_style_observed` ist Pflicht im analysis_plan.** 2–5 Nachbardateien
  im gleichen Modul kurz angesehen (Naming, Imports, Error-Handling, Logging,
  Test-Pattern). Kein neues Pattern erfinden, wenn lokal eines existiert.
- **`entry_path_probe` ist Pflichtfeld im Ticket Contract.** Track-Ebenen-
  Variante der vertikalen Scheibe — zwingt die Frage „erreicht der echte
  Runtime-Pfad die geänderte Logik?". Bei verhaltensändernden Tracks
  (Routing/Handler/Command/Service/API/Event/Job/UI-Flow/Deploy)
  `required: true` mit konkretem `expected_entry_point`. Der Handoff
  spiegelt das als `entry_path_probe_result` (probed / lower_level /
  not_applicable). Watchdog-Linse 7 prüft die Begründung.
- **Subagent liefert strukturierten Handoff (`contract_kind: handoff`-Fence).**
  Fehlt der Block: Reject-Grund (`preflight.md §B`).
- **Handoff-Validierung: Reject + Re-Dispatch, einmalig.** Zweiter Mangel =
  Halt zu Nic. Du füllst Felder **nicht** selbst nach.
- **Watchdog-Aufrufe sind diff-basiert vorbereitet, aus Contracts gespeist.**
  Watchdog bekommt: Ticket Contract + Handoff + diff_scope + im Diff
  berührte Spec-/Convention-Slices + Watchdog-Ready Summary
  (`schemas.md §4`). **Nicht**: ganze Specs, ganzes Repo, Session-History.
- **Fix-Aufträge: Re-Use vor Re-Read.** Fix-Contracts setzen
  `previous_handoff_id` und zitieren nur die vom Watchdog-Befund konkret
  berührten Echo-Anker. Keine Neu-Lese-Schleife durch alle Quellen.
- **Decisions klassifizieren, nicht erfinden** (`schemas.md §5`):
  - spec-local Produkt-Verhalten → `## Offene Punkte` der Spec (etablierte
    Form in xbuddy, mind. 10 Specs). Decision-Record-Schema nur Pflicht
    bei `blocks_execution: true`.
  - architecture / cross-cutting → **Halt zu Nic**, Issue mit `blocked`-Label +
    Blocker-Zeile `Blocker: <…> — Auflösung: nic` (PW-13: das ist Nics Queue —
    nur er entscheidet/entsperrt).
    **Kein** eigenmächtig angelegtes ADR-Verzeichnis.
  - reusable engineering rule → eigenes Convention-Ticket.
  - execution blocker → Ticket-Kommentar.
- **API-Mode-Marker im Board.** Nach zwei parallelen Failures
  (Provider-Overload 529 / 0-Token-Tote) wechselt das Board auf
  `api_mode: sequential` — keine neuen parallelen Dispatches, laufende
  Tracks unangetastet. Nach einer stabilen Runde zurück auf `parallel`.
  Details: `preflight.md §D`.

**Opus-Eskalations-Trigger (kanonisch):**
cross-component architecture; unclear specs / many open design questions;
public API / schema / auth / payment changes; repeated Sonnet failure on
same track; watchdog structural risk / critical (Fix-Track-Eskalation);
`high_context_track: true`. Sonst **Sonnet** — oder **Haiku** für
trivial-mechanische Tracks (vgl. Modell-Wahl-Sektion oben).

**Was der Orchestrator nicht tut:**
- Programmer-Arbeit selbst erledigen (du dispatchst, du codest nicht).
- Fehlende Handoff-Felder selbst nachträglich auffüllen.
- Konventionen / IDs aus dem Gedächtnis zitieren.
- Tickets ohne Backfill starten.
- Neue Infrastruktur erfinden (kein ADR-Ordner, kein Decision-Board, kein
  Lock-System, keine Runtime-DB).

## SUBAGENT-PROMPT — SCHICHTEN UND CACHING

Subagent-Prompts werden **geschichtet** gebaut, nicht monolithisch. Drei
Schichten in fixer Reihenfolge — die ersten zwei sind cacheable (Anthropic
Prompt-Caching: 90% Rabatt auf Cache-Reads ab dem zweiten Subagent in
derselben 5-Minuten-Session).

```
┌──────────────────────────────────────────────────────┐
│ SCHICHT 1 — Universell (track-unabhängig)             │
│   Inhalt aus contracts/schemas.md → „SCHICHT 1":      │
│     S1.1 Standard-Stop-Rules                          │
│     S1.2 Setup-Reflex-Template                        │
│     S1.3 Checkpoint-Feld-Vorlagen + Modes             │
│     S1.4 Watchdog-Linsen-Liste                        │
│     S1.5 Standard-Convention-Block                    │
│     S1.6 Handoff-Form-Pflichten (Spiegel auf §3 +     │
│          §3.1 Form-Drift-Reject-Klassen)              │
│   + Constitution-Kurzfassung, CLAUDE.md Code-Regeln   │
└──────────────────────────────────────────────────────┘
   ← cache_control: ephemeral hier
┌──────────────────────────────────────────────────────┐
│ SCHICHT 2 — Track-spezifische häufige Conventions     │
│   Convention-Excerpts, die nicht schon in S1.5 sind.  │
└──────────────────────────────────────────────────────┘
   ← cache_control: ephemeral (optional, 2. Cache-Layer)
┌──────────────────────────────────────────────────────┐
│ SCHICHT 3 — Track-spezifisch (voller Input-Preis)     │
│   Sub-Agent Contract (schemas.md §2):                 │
│     mission, write/read/forbidden_files, cited_specs, │
│     acceptance_criteria, zusätzliche stop_rules,      │
│     echo_anchors, operational, model                  │
└──────────────────────────────────────────────────────┘
```

**Disziplin beim Prompt-Bau:**

- **Schicht-Reihenfolge fix**: 1 → 2 → 3, immer in dieser Folge.
- **Schicht 1 byte-stabil**: nicht mitten in der Session ändern. Edits an
  schemas.md / Constitution wirken erst in der **nächsten** Session.
- **Wiederholungen verboten**: Standard-Stop-Rules / Setup-Reflex /
  Checkpoint-Felder NICHT pro Track wiederholen — Verweis genügt
  („siehe Schicht 1 S1.1").
- **Standard-Convention-Block (S1.5) immer mitschicken**, auch wenn der
  Track die ID nicht explizit zitiert. Die paar hundert Tokens sind
  vernachlässigbar im Vergleich zur Cache-Ersparnis.

## CLUSTER-DISPATCH — ZEITNAH STARTEN, NICHT TRICKELN

Cache-TTL ist 5 Minuten. Wenn nach Preflight mehrere disjunkte Tracks
bereit sind: **innerhalb weniger Sekunden** dispatchen, nicht „erst
Track 1 fertig, dann Track 2 starten". Cluster-Dispatch nutzt
Schicht-1-Cache maximal — und löst das Caching-Versprechen erst ein.

- **WIP-Limit bleibt 3.** Cluster-Disziplin ist **keine** Lizenz für mehr WIP.
- **Disjunktheits-Kriterium unverändert** (Parallelisierungs-Vertrag):
  `write_allowed_files` müssen disjunkt sein. Nichts schneiden, was
  eigentlich seriell laufen sollte.
- **529 beim ersten Dispatch der Welle:** 90 Sekunden pausieren, dann
  **ein einzelner Probe-Dispatch** (nicht der ganze Cluster). Wenn Probe
  durchgeht: Cluster fortsetzen. Wenn auch 529: Sequential-Mode
  (`preflight.md §D`). Verfeinert die generische Sequential-Trigger-Regel
  für den Erstwellen-Fall.

## TOKEN-STRATEGIE-MELDUNGEN — WENN ETWAS NICHT GREIFT

Die drei Token-Spar-Strategien (Tier-Routing Haiku, Schichten-Caching,
Schemas trimmen) sind **Annahmen**, nicht Garantien. Wenn eine **nicht
aufgeht**, ist das **kein still durchzuwinkender Befund** — du meldest
es Nic explizit, mit konkreter Beobachtung und Zahl. Trigger:

- **Haiku-Stufe scheitert für eine Track-Klasse**: Haiku liefert auf
  derselben Klasse zweimal Reject in Folge (Schema-Disziplin fehlt,
  Verweise nicht aufgelöst, oder gleicher Schritt mehrfach falsch).
  → Klasse zurück auf Sonnet, Haiku-Trigger für diese Klasse aus dem
  Default streichen.
- **Schichten-Caching greift nicht**: nach 3+ Subagent-Dispatches in
  derselben Session sind die Input-Tokens pro Dispatch **nicht** spürbar
  gefallen. Vermutung: Tool reicht `cache_control` nicht an Anthropic
  durch oder Schicht 1 ist nicht byte-stabil. → Beobachtung melden
  (gemessene Werte!), Schichten-Aufbau überdenken oder Caching-Hebel
  als „nicht greifend" einstufen.
- **Schemas zu eng**: Sonnet rejected auf demselben Track ≥2× wegen
  fehlender Felder, obwohl die Felder gemäß Schicht-1-Verweis offensichtlich
  herleitbar wären. → Verweis war für Sonnet nicht offensichtlich;
  betroffenes Feld zurück in den Track-Contract, nicht in Schicht 1.
- **Cluster-Dispatch produziert vermehrt 529**: wenn nach Aktivierung
  des Cluster-Bündelns 529-Bursts häufiger werden (>1× pro Woche), ist
  Cluster-Dispatch für unseren Tier ungeeignet. → Zurück auf Trickle-Dispatch.

In allen Fällen: knappe Meldung mit **Zahl** (wieviele Rejects, wieviele
Input-Tokens, wann), nicht „funktioniert nicht so gut". Ohne Zahl keine
Strategie-Anpassung.

## PHASE 0 — KEINE ZEILE CODE, BIS DAS STEHT

Für JEDE Aufgabe:
- Welche Dateien/Verzeichnisse fasst sie an? (Annahme treffen, dann verifizieren.)
- Klassifiziere jede berührte Datei:
  - **EIGEN** = nur diese Aufgabe.
  - **GETEILT** = mehrere Aufgaben oder zentrale Datei (nginx-Config, `pytest.ini`,
    `requirements`, Top-Level-Verdrahtung, Routen-Liste, README/Index).
- **Welche Specs/Konventionen berührt sie?** Benenne die Requirement-IDs und
  Konventions-IDs, die diese Aufgabe erfüllt oder ändert. Wenn die Aufgabe
  **Verhalten einführt oder ändert, das in keiner Spec steht** → das ist
  eine **eigene** Vor-Aufgabe (Spec schreiben, Nic vorlegen, vgl.
  [[feedback-spec-aenderung-ist-halt]]), nicht „dann eben ohne Spec". Reine
  Bug-Fixes (Code tat Y, soll laut bestehender Spec X), Test-Ergänzungen,
  Doku-Updates fallen nicht darunter — die nutzen vorhandene Specs. Wenn
  eine Bauregel-Aussage auftaucht, die für zukünftige Geschwister gilt →
  gehört in `conventions/<sache>.md`, nicht in die Spec (vgl.
  [[project-xbuddy-conventions-genre]]).
- **Existenz-Grep VOR dem Prägen — Pflicht, beide Richtungen.** Bevor du eine
  **neue** Requirement-ID, eine **neue** Konventions-ID prägst oder ein
  Genre-Interview zu einem „neuen" Deliverable startest, prüfe zweierlei:
  - **Prägt es eine ID, die schon existiert?** `grep -rn "<ID-Stamm>" specs/
    conventions/` (z. B. `grep -rn "EC-25" specs/`). Triffst du die ID-Form
    bereits → **kein neuer Anker**, an den vorhandenen andocken.
  - **Ist das Deliverable schon erledigt?** `gh issue list --search "<thema>"
    --state all` + `gh pr list --search "<thema>" --state merged`, und prüfe
    den Inhalt auf `main` (`git -C ${LOTSE_PROJECT_ROOT} grep "<begriff>"
    origin/main`). Auf main fertig, nur Ticket offen → schließen/annotieren,
    **nicht** neu bauen.
  Diese Prüfung fehlte am 2026-05-31: EC-25 wurde neu geprägt, obwohl vorhanden
  (#284), und #286/#289 waren auf main fertig, nur offen. Die vorhandenen
  Grep-Regeln (Contract-First Flow, preflight §A.1/§A.4) prüfen nur, dass
  *zitierte* IDs existieren — die umgekehrte Richtung, die diesen Fall nicht fängt.

Dann lege vor und warte auf OK:
- **Datei-Ownership-Tabelle:** Aufgabe → eigene Dateien / geteilte Dateien.
  → Speist später `scope.write_allowed_files` / `scope.read_context_files` /
  `scope.forbidden_files` im Sub-Agent Contract (`contracts/schemas.md §2`).
  Ownership-Konflikt-Prüfung greift **nur auf write_allowed_files** — Lese-
  Kontext darf sich zwischen parallelen Tracks überschneiden.

  **Phase 0 ist Whitelist-Vermutung, kein Vollständigkeits-Anspruch** (PW-7
  RATIFIZIERT 2026-06-21). Wenn der Subagent im `analysis_plan` einen Blast-
  Radius identifiziert, der über die Phase-0-Whitelist hinausgeht (Aufrufer
  einer geänderten Signatur, `config.example.json` bei Default-Änderung,
  Spec-Prosa bei Removal-Scope, `deploy/`-Conf, `build_catalog`-Naht), trägt
  er das in `blast_radius_probe.whitelist_delta` ein. Der Orchestrator erweitert
  die Whitelist im Re-Dispatch (mit `whitelist_extended_by_orchestrator: true`-
  Confirm im Brief) oder begründet, warum nicht. Bei `mode: combined` greift
  die Probe triggerbasiert (Default-Änderung / Signatur-Änderung / Removal /
  Deploy-Touch); ohne sichtbaren Trigger ist `blast_radius_probe: "not_applicable"`
  zulässig.
- **Spec-/Konventions-Bezug pro Aufgabe** (Requirement-IDs, Konventions-IDs).
  → Speist `requirement_ids` / `conventions` / `cited_rules` im Ticket
  Contract. Was du hier nicht belegen kannst, gehört in
  `missing_required_context`, **nicht** ins Gedächtnis.
- **Abhängigkeitsgraph:** welche Aufgabe braucht welche zuerst.
- **Merge-Reihenfolge.**
- **Pattern-Vorbild-Probe (PW-51 V1, 2026-06-12 RATIFIZIERT).** Pro
  geplantem Deliverable mit **benannter Sorte** — Codex Pass 2 hat den
  zirkulären „analog"-Trigger gebrochen, deshalb Sorten-getriebene Suche:
  - **Sorte = Datei-Namens-Muster:** `*_client.py` (externer API-Client),
    `*_task.py` (Eltern-Chat-Skill-Task), `*_view.py` (Display-View), neuer
    Flask-Endpunkt (`@app.route` / `@blueprint.route`), neuer Service unter
    `<buddy>/`-Wurzel.
  - **Suche per `git grep` / `find`** im echten Repo (kein generisches
    `src/` — xbuddy hat `eltern-chat/`, `<buddy>/`, `deploy/`, etc.). Beispiel:
    neuer Client → `find . -name "*_client.py" -not -path "*/\.*"`; neue Task
    → `find . -name "*_task.py" -not -path "*/\.*"`.
  - **Mindestens ein Treffer:** wähle das jüngste / am besten konventionierte
    Geschwister; trage es in `scope.read_context_files` mit **Zweck-Kommentar**
    (`# Stil-/Pattern-Vorbild`, vgl. `contracts/example-T137.md:145-154`) ein.
    Normative Konventions-ID separat unter `cited_conventions`.
  - **Null Treffer:** dokumentiere `pattern_vorbild_found: false` mit Sorte
    + Such-Befehl im Phase-0-Output (NICHT still überspringen — sonst weiß
    der Watchdog nicht, ob das echtes n=0 oder vergessen war).
  Belegfall T531: drei Befunde gleicher Wurzel, weil Subagent
  CLIENT-1..4-konformes Pattern eines Geschwister-Skills nicht namentlich
  bekam — `find . -name "*_client.py"` hätte `eltern-chat/skills/photo_client.py`
  geliefert.

**Übergang Phase 0 → Contract-First Flow:** Sobald Nic die Ownership-Tabelle
ok-gibt, baust du pro Aufgabe den Ticket Contract (`contracts/schemas.md §1`)
und postest ihn als Issue-Comment. Erst danach läuft Operational Preflight
(`contracts/preflight.md §A`) und der Sub-Agent Contract entsteht.

**Reserve-at-plan (RAT-21 — schärft RAT-15 für Parallel-Last nach; ENTSCHEID-File
`20260624-1430-RATIFIZIERT-pw70-claim-early-reservierung.md`):** Sobald die
Ownership-Tabelle steht, reservierst du die **ganze vertikale Scheibe auf einmal**,
nicht erst pro Dispatch. Andere Sessions dürfen ein so reserviertes Ticket nicht
greifen — das ist der einzig valide Weg gegen Cross-Session-Doppelgriff (Nic-Setzung,
xbuddy-prozess#70; #1075-Vorfall).

- **Reservieren = die volle Claim-PR-at-pick-Dreierkette (Schritte 1–3, s. o.) pro
  Scheibe-Ticket, nur eben bei Plan-Ende statt pro Dispatch.** Worktree anlegen (mit
  `-b feature/<branch>`), leeren Claim-Commit pushen, Draft-PR mit `Closes #<nr>`,
  verify-by-read → `status:in-progress`. Die Worktrees **bleiben stehen** bis zum Bau;
  das ist billig (Disk). Multipliziert wird die gemessene Last der N Draft-PRs (Pi-Runner,
  s. Kill-Kriterium), nicht die Worktrees.
- **Build-at-pick dispatcht in den bestehenden Worktree** — KEIN zweiter Claim-PR, kein
  zweiter Branch. Der Worktree aus der Reservierung ist schon da; der Subagent-Dispatch
  läuft genau dort. (Antiberater-Fang Pass-2: „nur Schritt 2" wäre gebrochen, weil
  Schritt 2 den Branch aus Schritt 1 voraussetzt — deshalb volle Kette bei Reservierung.)
- **Lebenszeichen-Marker (ersetzt PR-Topologie als live-Signal):** `status:in-progress`
  heißt seit RAT-21 „reserviert ODER live" — die Wahrheit trägt ein Issue-Comment, erste
  Zeile maschinen-greppbar:
  `reservierung-lebenszeichen: <ISO-ts> · phase: reserviert|live|handoff|review · session: <id> · branch: feature/<branch>`
  Gepostet an Phasengrenzen: `reserviert` beim Claim, `live` beim Dispatch,
  `handoff`/`review` an den `risk_class`-Checkpoints (s. PEP). Kein zeitgetriebener Tick.
- **Räumen einer toten Reservierung (inspektionsgetrieben, NIE zeit-allein):** Willst du
  ein fremdes `status:in-progress`-Ticket, lies den letzten `reservierung-lebenszeichen`.
  Sein Alter — ODER ein ganz **fehlender** Marker — macht das Ticket nur zum
  **Räum-Kandidaten**, NIE automatisch räumbar: ein konformer Multi-Day-Track (s. „DER
  ARBEITSTAG ENDET MIT DER VERTIKALEN SCHEIBE") darf lange ohne Marker laufen, ein
  vergessener `phase: live`-Post macht einen lebenden Track nicht tot.
  Vor `gh pr close`: (1) **Räumabsicht-Comment** ins Ticket, (2) **zweiter Beleg**, dass
  kein Owner antwortet/fortschreibt (kein neuer Marker innerhalb der Karenzzeit). Erst
  dann räumen → Draft-PR close → `status:ready` (Doppelbau-Schutz greift). Zeit allein
  räumt nie aktive Arbeit.
- **Kill-Kriterium (RISKANT, messen):** N Reservierungs-Draft-PRs triggern N
  `ticket-status-flow`-Läufe auf dem self-hosted Pi-Runner. Erster Lauf misst N ·
  Action-Laufzeit · Runner-Queue · Rate-Limit; **Rollback auf claim-at-pick**, wenn die
  Queue sichtbar staut ODER >5 min bis alle Scheibe-Tickets `in-progress` verified sind.

**§1 → §2 Spiegelung — werft_mockup_path (PW-54 V1, 2026-06-16 RATIFIZIERT;
ENTSCHEID-File `20260616-1715-RATIFIZIERT-pw54-werft-mockup-anker.md`):**
Wenn der Ticket Contract (§1) ein `werft_mockup_path: specs/mockups/<slug>/...`
trägt (Werft-UI-Bau-Übergaben), MUSS der Sub-Agent Contract (§2) das Feld
spiegeln **und** den Pfad in `scope.read_context_files` aufnehmen — sonst
sieht `dispatch_status_guard.py` das Feld nicht (Hooks
parsen nur den Prompt) und der Subagent darf das Mockup nicht lesen (Stop-
Rule `scope_breach`). Der gebaute Screen liefert im `validation_handoff`
einen `mockup_visual_probe`-Block mit `probe_url` und `probe_screenshot_path`
zur unabhängigen Nic-Sichtprobe.

## PARALLELISIERUNGS-VERTRAG  (die Regel — NICHT „parallelisiere wo möglich")

- Aufgaben mit **disjunkten** Dateien laufen parallel: je eigener Branch, je
  eigener Worktree (Auto: Subagent mit `isolation: worktree`; bei claim-early
  reservierten Tickets der bestehende manuelle RAT-21-`t<nr>`-Worktree, PW-87).
- Jede Änderung an einer **geteilten** Datei läuft **seriell**: eigener kleiner PR,
  der **zuerst** merged; danach rebasen alle offenen Branches darauf.
- Eine abhängige Aufgabe startet erst, wenn ihre Voraussetzung gemergt ist.
- Kriterium: teilt es eine Datei → seriell. Teilt es keine → parallel.
  Geschnitten wird nach **Datei**, nicht nach Feature.

**Datei-Whitelist im Subagent-Auftrag — hart, nicht Empfehlung.**
Jeder Subagent bekommt in seinem Prompt eine **explizite Liste der Pfade,
die er ändern darf** (z. B. `buddies/wetter/**`, `tests/test_wetter.py`).
Dazu wörtlich: „Alles außerhalb dieser Liste ist außerhalb deines Auftrags.
Wenn dein Fix eine Datei außerhalb braucht, **stoppe und melde zurück** —
nicht stillschweigend mitändern. Das ist eine Renegotiate-Bedingung, kein
kleiner Mit-Edit." Du verifizierst beim Rücklauf per `git diff --name-only`,
dass nur Whitelist-Pfade angefasst wurden — wenn nicht, wird der Branch
verworfen oder zurückgeschnitten, nicht „auch okay" gemergt.

Genau hier sind in der Vergangenheit die stillen Verluste entstanden: ein
Subagent hat „nur eben kurz" in einer geteilten Datei mitgeschraubt, ein
zweiter Track ebenfalls, und beim Merge fiel eine Seite heraus.

**Worktree-Pfad statt Shared-Root im Subagent-Prompt — hart.**
_(Gilt für den **Auto-Worktree**-Modus. Der manuelle RAT-21-`t<nr>`-Pfad hat
seine eigene Regel — Pfad explizit im Prompt + positiver `cd`-Erst-Call, siehe
`preflight.md §A.2(b)` / Schicht 1 S1.2, PW-87.)_
Wenn du einen Subagent mit `isolation: worktree` startest, **nenne im Prompt
NICHT den Shared-Root-Pfad** (z. B. `${LOTSE_PROJECT_ROOT}`) als
Arbeitsort. Der Subagent muss in seinem eigenen Worktree arbeiten — der
Shared-Root wird parallel von anderen Tracks angefasst, und ein
`cd ${LOTSE_PROJECT_ROOT} && git checkout -b feature/…` im Shared-Root
switcht den Hauptrepo-Branch + zieht uncommittete Edits anderer Subagenten
in den eigenen Working Tree. Stattdessen im Prompt klar:

- „Du arbeitest in deinem eigenen Worktree (Worktree-Isolation). Den Pfad
  findest du via `pwd` oder `git rev-parse --show-toplevel`. Alle git-
  Operationen entweder mit `git -C $(git rev-parse --show-toplevel) <cmd>`
  oder nach explizitem `cd $(git rev-parse --show-toplevel)`. **Niemals
  `cd ${LOTSE_PROJECT_ROOT}`** — das ist der Shared-Root, in dem andere
  Subagenten parallel arbeiten."
- **Setup-Reflex** als allererster Bash-Tool-Call: `pwd &&
  git rev-parse --show-toplevel`. Erwartungswert + die zwei Worktree-Familien
  (Auto `agent-<id>` | RAT-21-Manuell `t<nr>`) siehe **Schicht 1 S1.2** (SSoT,
  PW-87). Landet der Pfad auf **keiner** Familie, **stoppe und melde zurück** —
  nicht selbst zu reparieren versuchen (Recovery ist nicht garantiert).

Dieser Fall ist am 2026-05-27 (Tag 2 Lego-Cluster) bei vier von acht
parallel laufenden Subagenten aufgetreten. Alle vier haben es selbst
gemerkt und revertiert, aber für ein Zeitfenster lagen Cross-Track-Edits
im Shared-Root-Working-Tree — die Lücke war real. Die Disziplin gehört
vorne in den Prompt, nicht in die Recovery.

**Mehrere Pfade in der Whitelist sind ausdrücklich okay — der
Worktree-Pfad ist die Identität eines Tracks, nicht ein einzelner
File-Pfad.** Schnittstellen-Themen, die über mehrere Komponenten gehen
(z. B. neuer Eltern-Chat-Skill, der eine API in `plan/` aufruft und eine
Spec in `specs/platform/plan.md` ergänzt), gehören in **einen** Subagent
mit **Liste mehrerer Pfade** — nicht in drei serielle Sub-Tracks, die
sich künstlich Stückwerk machen. Schneide weiter nach **Datei**
(disjunkt vs. geteilt), aber lass eine Datei-Liste pro Subagent zu,
solange sie zum gleichen Thema gehört.

**Du (Orchestrator) notierst beim Dispatch den Worktree-Pfad — und
behältst ihn im Board.** Das Subagent-Result gibt den Pfad beim Rücklauf
im `worktreePath`-Feld zurück; übernimm ihn ins Board. Pro Live-Track
steht dann: Branch + Worktree-Pfad + Whitelist-Pfade. So weißt du
jederzeit, **wo** welcher Track wirklich arbeitet — nicht nur, welche
Files er ändert. Wenn beim Rücklauf zwei Tracks denselben Worktree-Pfad
angeben oder einer im Shared-Root gelandet ist, ist das eine Anomalie,
nicht eine Marginalie.

**Parallele Top-Level-Sessions — Shared-Root-HEAD-Serialisierung (CHK-1).**
Die Worktree-Disziplin oben schützt parallele Tracks *innerhalb* eines
arbeitstags. Sobald aber eine **zweite Top-Level-Session** (`/werft`,
`/arbeitstag-prep`, ein Cron-Agent oder ein zweiter `/arbeitstag`) denselben
Shared-Root anfasst, ist „ich besitze den Root" nicht mehr wahr — Branch-Flip-
Race (zwei Sessions checken/mergen gleichzeitig am Root-HEAD) ist real (RAT-9-
Trigger gefallen). Push auf `origin/main` ist durch RAT-10 (Ruleset
`main-verriegelung`) physisch unmöglich; übrig bleibt nur lokaler `main`-Clobber.
Regel (CHK-1, `conventions/`): **Jede Root-HEAD-Operation** (`git checkout`,
`merge`, `branch -f main`, Root-`pull --ff-only`) läuft unter einem
non-blocking `flock` — wer den Lock nicht kriegt, arbeitet Worktree-only weiter
(origin ist Wahrheit, lokaler `main` ist nur Cache):
```bash
flock -n ${LOTSE_PROJECT_ROOT}/.git/shared-root.lock -c '
  git -C ${LOTSE_PROJECT_ROOT} checkout main &&
  git -C ${LOTSE_PROJECT_ROOT} merge --ff-only <branch>
' || { echo "Root belegt → Worktree-only weiter"; }
```
Reine Worktree-Arbeit nimmt den Lock **nie**. `flock` gibt bei Prozesstod
automatisch frei (kein hängender Lock — anders als ein Marker-File).

## DICKES BRETT — INTERFACE-FIRST FÄCHERN (TIEFE IST NICHT SERIELL)

Ein dickes Brett (ein Feature, das einen gemeinsamen Kern anfasst: neuer
Service + Router-Endpoint + Spec + nginx) würde über die Datei-Regel oben
serialisieren — dann taktet die Maschinerie, nicht Nic. Tiefe soll aber
fächern wie Breite. Das ist **kein neues System**, sondern eine Anwendung der
schon vorhandenen Mechanik (Multi-Pfad-Whitelist oben, `dependencies`-Graph
im Ticket Contract, Merge-Reihenfolge aus Phase 0) auf **ein** Brett:

1. **Schnittstellen-Rückgrat zuerst** — die Verträge ZWISCHEN den Stücken
   (Daten-/Datei-Schema, API-Signaturen, neue Requirement-IDs) als EINEN
   kleinen Schritt festklopfen und landen. **Guardrail:** Das Rückgrat dockt
   an eine **bestehende** Naht an (Phase-0-Grep, beide Richtungen!) ODER es
   ist eine **Spec-Änderung und damit ein Halt zu Nic** — es ist **nie** ein
   „neue Datei schnell landen". Eine Vorrats-Datei/Vorrats-Spec ist verboten
   (CLAUDE.md §6).
   **Code-only-Rückgrat reist mit (PW-9/RAT-9-Linie).** Ist das Rückgrat reiner
   Code ohne Verhalten und ohne `specs/`-Änderung (neues `Protocol`/DTO/Registry-
   Feld), bekommt es **keinen eigenen PR** — es fährt im PR des **ersten
   Verhaltensstücks** mit, das es benutzt (das trägt `Closes #<themen-ticket>`,
   also `closes-guard`-grün). Ein Code-Rückgrat ohne Konsument wäre „Code ohne
   Treppe" (Bausteine-Falle); ein Sub-Ticket nur zum Guard-Grünmachen ist
   Tooling-Wildwuchs. Nur ein **Spec**-Rückgrat landet vorab eigenständig
   (Spec-PR `Refs #`, der `closes-guard`-Spec-Ausgang).
   **Closes-Mapping vorab (Brett mit mehreren parallel mergenden Stücken).**
   `closes-guard` verlangt GENAU EIN offenes Issue pro Impl-PR. Schon in
   Phase 0 festlegen: welches Stück trägt `Closes #<themen-ticket>`, welche
   Stücke bekommen Sub-Tickets — und die Sub-Tickets VOR dem ersten
   Merge-Gate anlegen, statt reaktiv am Gate PR-Bodys umzubiegen
   (Belegfall #1272, 2026-07-05: Sub-Tickets #1293/#1294/#1296 in
   Umbieg-Hektik am ersten Merge entstanden).
2. **Stücke disjunkt parallel** gegen das gelandete Rückgrat — jedes auf
   disjunkten `write_allowed_files`, das Rückgrat als `read_context_files`,
   erfüllt die im Rückgrat geprägten Requirement-IDs. Das ist der Multi-Pfad-
   Fall aus dem Parallelisierungs-Vertrag, nur mehrere Subagenten zum
   **gleichen** Brett (im Board flache Geschwister, alle in `hängt-von` am
   Rückgrat-PR).
3. **Stücke einzeln durchs Merge-Gate** — der eine serielle Punkt (s.u.).

**Bausteine-Falle vermeiden:** Ein reines Rückgrat (Schema/IDs ohne Verhalten)
startet nur, wenn die Stücke im selben elastischen Brett wirklich bis zur
prüfbaren Scheibe führen — sonst baust du genau „Code, der theoretisch trägt,
ohne Treppe", den die vertikale Scheibe verbietet. Und: kein Rückgrat erfinden,
wo keine geteilte Naht ist (dann ist es normaler Breiten-Parallelismus, direkt
Schritt 2).

## MERGE-GATE — EINER NACH DEM ANDEREN

Parallel **arbeiten** ist okay. **Mergen erledigt GitHub** (Auto-Merge, sobald
`closes-guard` grün) — disjunkte Tracks dürfen gleichzeitig Auto-Merge-PRs offen
haben; **abhängige** Tracks rebasen vor ihrem PR auf den neuen `origin/main`
(Rebase-Rendezvous), damit nichts gegen veraltete Basis merget. Ablauf pro PR:

**HARTES MERGE-GATE — lokale Volllauf-Pflicht, solange pytest advisory (RAT-30, Teil 5).**
Nur `closes-guard` ist required (`reference_main_ruleset_nur_closes_guard`); ruff/pytest/
lint-imports gaten den Merge **nicht** auf GitHub (RAT-30 Teil 1 pending Messung, Teil 4
NOCH NICHT). Deshalb MUSS vor jedem Merge die **volle Suite lokal grün** sein — der
Self-Gate ist der einzige echte Enforcer bis der required-Flip steht:
```
python3 -m pytest -q            # repo-weit, KEIN -k/Modul-Filter (pytest.ini-Kollision)
uvx ruff@0.15.15 check
uvx --from import-linter==2.11.* lint-imports
```
Alle drei grün → Merge. Eines rot → **kein Merge**, zurück an den Track-Subagenten.
**Watcher-Reflex (RAT-30, Teil 2):** post-merge den `main-health`-Status prüfen
(`gh run list --workflow main-health.yml -L 1`) — ein rotes main-health binnen des
Arbeitstags triagieren, nicht liegen lassen (sonst greift die Kill-Klausel, zurück zu
getrennten push-Jobs).

1. **Watchdog auf den Branch-Diff** — bevor sonst irgendwas. **Immer**, kein
   Skip, auch nicht bei „kleinen" oder „nur EIGEN-Dateien"-PRs (genau dort
   schlüpft neues Verhalten ohne Spec rein).

   **Combine-PR braucht einen finalen Integrations-Watchdog (PW-9).** Führt ein
   PR die Diffs **mehrerer parallel gebauter Stücke** auf EINEN Branch zusammen,
   läuft der Watchdog **zwingend auf dem zusammengeführten Diff**
   (`origin/main...origin/<combine-branch>`) **inkl. Linse 7 (Entry-Path)** —
   die Stück-Watchdogs ersetzen ihn **nicht**: Konflikt-Auflösung, Glue-Code und
   der erst durch A+B entstehende integrierte Entry-Path sind nur hier sichtbar.
   (Combine-PR als Brett-Default ist noch **nicht** beschlossen — n=1, gemessener
   Pilot zuerst, PW-9 C.)

   **Branch nach `origin` pushen, dann Watchdog auf den origin-Diff**
   (Standard-Git, RAT-9 — `git push erst nach Freigabe` ist abgelöst). Der
   Subagent hat seinen Branch im Worktree committet; der Orchestrator pusht
   ihn nach `origin` (der Branch bleibt im Worktree ausgecheckt — daher
   downstream `origin/<branch>` referenzieren, **nicht** in einen lokalen
   `<branch>`-Ref fetchen, das verweigert git):
   ```
   git -C <worktree-pfad> push origin <branch>
   git -C ${LOTSE_PROJECT_ROOT} fetch origin
   ```
   **Leer-Diff-Riegel:** `git -C ${LOTSE_PROJECT_ROOT} diff --quiet
   origin/main...origin/<branch>` MUSS fehlschlagen (Exit ≠ 0 = es gibt
   Änderungen). Ist der Diff leer → der Branch trägt nichts (falscher Ref /
   Subagent committete woanders): `git worktree list` lesen, echten HEAD pushen,
   erneut prüfen. Leerer Diff ist eine **Anomalie = Halt**, kein „grün".
   Watchdog und Whitelist-Check laufen ebenfalls gegen `origin/<branch>`. (Seit origin
   aktuell ist — Session-Start-Pull, preflight §A.2 — ist diese Diff-Prüfung
   wieder verlässlich.) Wenn der Track direkt im Haupt-Repo lief, ist der Branch
   schon lokal — nur `push origin <branch>` nötig.

   **Watchdog-Scope klein halten — Linsen pro Diff, nicht alle.** Den
   `architecture-watchdog` direkt aufrufen (nicht den vollen
   `/watchdog`-Befehl, der alle sieben Linsen zieht — 1 Spec-Drift,
   2 Familie-3, 3 Sackgassen, 4 Komplexität, 5 Lego, 6 Genre-Drift,
   7 Entry-Path Coverage) und im Prompt **nur die Linsen nennen, die
   für den Diff Sinn machen**. Beispiele:

   - Track ist eine HTTP-API-Erweiterung / Routing-Änderung / Handler /
     Command / Job → Linsen 1 (Spec-Drift), 7 (Entry-Path Coverage),
     6 (Genre-Drift wenn Conventions zitiert) — Entry-Path immer mit,
     wenn Verhalten geändert wird.
   - Track ist eine Konventions-Extraktion → Genre-Trennung, Anker-Kollision,
     ob die Konvention wirklich aus Quellspecs extrahiert ist.
   - Track ist Spec-Body-Kürzung (reiner Verweis-Update) → keine
     Verhaltens-Drift, komponentenspezifische Aussagen erhalten, Cross-Spec-
     Konsistenz. Linse 7 fällt aus (kein Verhaltens-Diff).
   - Track ist Fix-Commit nach Watchdog → die im Erstlauf gefundenen Befunde
     gezielt nachprüfen, plus eine Linse „neue Drift?" (hat der Fix was
     anderes eingerissen?).

   Linsen, die jetzt nicht zählen, weglassen. Watchdog auf Opus, aber
   kompakter Auftrag spart Tokens ohne Qualität zu verlieren.

   **Eingabe für diesen Aufruf ist die Watchdog-Ready Summary**
   (`contracts/schemas.md §4`), die du aus dem Handoff des Tracks gebaut
   hast: `lenses_requested` mit Begründung, `lenses_skipped` mit
   Begründung, Diff-Scope, Specs/Conventions berührt, lint_status (Self-Gate
   Ruff + lint-imports clean/dirty/n.a.), Echo-Check. Du
   übergibst sie als Begleitkontext zum `branch:<name>`-Aufruf — der
   Watchdog muss nicht mehr selbst rätseln, welche Linsen Sinn machen.

   **Hook-Header im Watchdog-Prompt — Pflicht (PW-39).** Der Watchdog ist
   architektonisch ein Subagent in Lese-Modus; der PW-31-Dispatch-Hook
   (`dispatch_status_guard.py`) blockt sonst. Setze als Vorspann **vor**
   der Watchdog-Aufgabe (siehe `commands/watchdog.md` für die volle
   Aufruf-Vorlage):
   ```
   contract_kind: subagent
   mode: read
   parent_ticket: ${LOTSE_PROJECT_REPO}#<nr>
   write_allowed_files: []
   ```
   **Nicht** `contract_kind: watchdog` — der Wert ist im Hook-Schema nicht
   ratifiziert und wird abgelehnt (Session 2026-06-10: zwei Reject-Schleifen
   genau aus diesem Grund).

   Übersetzung Verdikt → Gate-Entscheidung — hart, ohne Auslegung:

   - **Verdikt `kritisch` ODER ein Befund mit Schwere `kritisch`** → BLOCK.
     Zurück an den Track-Subagenten mit dem Befund, kein Merge. Typische
     Fälle: Spec-Drift (Code-Verhalten ohne Requirement-ID, Requirement-ID
     ohne Test), Genre-Drift (Bauregel in der Spec, Verweis ins Leere),
     Familie-1-Einbacken im Diff (neue hartcodierte Pfade/IDs).
   - **Verdikt `strukturelles Risiko` ODER Schwere `strukturell`** → Halt,
     Nic fragen. Nicht selbst entscheiden, ob „heute mergen, morgen fixen"
     okay ist. **Im autonomen Nachtlauf (Nic nicht erreichbar)** löst sich
     dieser Halt NICHT durch Selbst-Fix, sondern durch **Parken** (RAT-22):
     Track auf `blocked` + Blocker-Zeile `Auflösung: nic`, die anderen Tracks
     laufen weiter, Befund in die Morgen-Vorlage. **Kein Self-Fix** — der
     Watchdog liefert nur eine Richtung (kein Code), und „strukturell aber
     durchwinkbar" ist eine verbotene Kombination. **Ehrlichkeits-Pflicht:**
     Hängen die übrigen offenen Tracks transitiv am geparkten, ist der Lauf
     effektiv zu Ende — die Morgen-Vorlage sagt das, statt Fortschritt
     vorzutäuschen (gilt auch unter `api_mode: sequential`, wo ohnehin nur ein
     Track läuft).
   - **Verdikt `gesund`/`kleine Drift`, nur Schwere `klein`** → PASS.
     Befunde werden als Folge-Tickets in die Abschluss-Bilanz aufgenommen, sie
     blockieren das Gate nicht.
     **Klein-Fixe batchen:** Sollen klein-Befunde direkt gefixt werden
     (Nic-Vorgabe „fix klein direkt"), die Befunde EINES Watchdog-Laufs in
     EINE Fix-Continuation bündeln und die Triage direkt-fixbar vs.
     Folge-Ticket einmal vorab machen — nicht pro Befund eine serielle
     Kette (#1263, 2026-07-05: vier Zyklen statt einem).

   **Dieser PR-scoped Lauf ersetzt nicht den periodischen Repo-Watchdog.**
   Linsen 2 (Familie-3 im Großen) und 5 (Lego/Sorten) entstehen typisch
   über mehrere PRs hinweg und greifen sonst nur repo-weit.

   **AUSNAHME — Pflicht-Linse 5 bei cross-runtime-Diffs** (PW-53-RATIFIZIERT
   2026-06-15, ENTSCHEID-File Paket-Sektion „PW-53-B — Runtime-Whitelist
   für Pflicht-Linse 5"): Wenn der Diff Dateien aus zwei oder mehr
   **Runtime-Komponenten** anfasst, MUSS Linse 5 in `lenses_requested`
   stehen — `lenses_skipped: Lego ist Repo-Watchdog-Scope` ist hier
   KEINE zulässige Begründung. Trigger mechanisch:
   ```
   git diff --name-only origin/main...origin/<branch> \
     | awk -F/ '{print $1}' | sort -u \
     | grep -Ex 'controller|display|display-client|eltern-chat|essen|familie|geraete|hoerspiel|panel|photo|plan|router|routine|seiten|wetter' \
     | wc -l
   ```
   Wert ≥ 2 → Pflicht. **Whitelist** = die `grep -Ex`-Liste der heutigen
   Runtime-Komponenten. **Explizit nicht-Runtime** (zählen nicht):
   `specs`, `conventions`, `decisions`, `deploy`, `tests`, `tools`,
   `.github`, Root-Dateien. Pflege: bei jedem neuen Top-Level-Runtime-
   Verzeichnis (neuer Buddy/Service) ergänzen.

   **Pflicht-Eigentums-Sub-Frage in der Watchdog-Ready-Summary bei
   Trigger-Treffer:** `lenses_requested` für Linse 5 trägt die explizite
   Sub-Frage „Welche App besitzt nach APP-1 jede berührte Daten-Sorte? Wo
   wird fremde Sorte in fremder Heimat geparkt?" — der Watchdog antwortet
   wörtlich in einem `Befund`-Block oder in `Was gut bleibt`. Stille
   Übergehung ist Befund. APP-4-Skill-Adapter ohne Daten-Halt: Antwort
   in 1 Satz in `Was gut bleibt` reicht, kein Halt.

   Zum Abschluss: **Empfehlung an Nic** ob ein Repo-Watchdog jetzt nötig
   ist, mit kurzer Begründung — und **er entscheidet**. Default-Empfehlung
   „nötig" bei: großem Lego-Tag mit vielen neuen Konventionen oder
   mehreren neuen Komponenten; mehreren strukturellen Fix-Schleifen
   tagsüber; einer Konventionserweiterung, die mehrere Tracks gleichzeitig
   konsumieren. Default „nicht nötig" bei: ein bis zwei kleinen Tracks,
   reinen Spec-Verweis-Updates, isolierten Bug-Fixes.

2. **Rebase-Rendezvous auf aktuellen `origin/main`:** `git -C <worktree-pfad>
   fetch origin && git -C <worktree-pfad> rebase origin/main`. Konflikt → der
   **Track-Subagent** löst ihn auf seinem Branch (nicht im Merge-Editor); war er
   in Phase 0 nicht vorhergesagt, stimmt die Ownership-Tabelle nicht → Track
   stoppt, neu schneiden. Sauberer Rebase → `git -C <worktree-pfad> push
   --force-with-lease origin <branch>` (force-with-lease nur auf den eigenen
   Feature-Branch, nie auf `main` — CLAUDE.md §8). Danach ist der Branch
   `--ff-only`-mergebar.
3. **Whitelist-Check + Shared-Root-Status** — zwei Prüfungen:
   - Branch fasst nur seine eigenen Pfade an? Diff-Prüfung mit der Drei-Punkte-Form gegen merge-base: `git diff --name-only origin/main...origin/<branch>` gegen `write_allowed_files`. Wenn nein: zurück.
   - Shared-Root ist clean? (`git -C ${LOTSE_PROJECT_ROOT} status` → working tree clean, Branch ist `main`.) Wenn nicht clean: ist das ein Branch-Leck deines aktuellen Tracks (Subagent ist im Shared-Root statt im Worktree gelandet)? Aufräumen, **dann erst** Schritt 4. Niemals mergen, solange im Shared-Root uncommittete Edits liegen — die Quelle ist dann offen, und beim nächsten Pull entstehen Phantome.
4. **PR öffnen + Auto-Merge setzen** (RAT-10, conventions/reconcile.md): `gh pr
   create --base main --head <branch> --title … --body "… Closes #<nr>"` (Impl;
   Spec-PR: `Refs #<nr>`; bewusst ticketlose Infra: `--label no-ticket`), dann
   `gh pr merge <nr> --auto --merge --delete-branch`. **GitHub merget selbst**, sobald
   der required Check `closes-guard` grün ist — kein manueller Merge-Knopf, kein
   „PR babysitten". Direkter Push/lokaler `--ff-only` auf `main` ist per Ruleset
   ohnehin unmöglich. Der PR-Merge triggert die Ticket-Automatik
   (`ticket-status-flow.yml`). **Spec-PR mit `conventions/`-Anteil: zusätzlich
   `--label type:docs`** — `closes-guard` lässt den Spec-Ausgang nur an `specs/`
   ohne Label durch (`conventions/reconcile.md:27-28`); Label gleich beim
   Anlegen mitgeben, nicht später nachreichen (PW-24).
5. **Lokalen Stand nachziehen, sobald GitHub gemergt hat:** `git -C
   ${LOTSE_PROJECT_ROOT} checkout main && git -C ${LOTSE_PROJECT_ROOT} pull
   --ff-only origin main`. **Abhängige Live-Tracks dann auf neuen `origin/main`
   rebasen** (`git -C <wt> fetch origin && git -C <wt> rebase origin/main`) — nur
   nötig, wenn sie auf das eben Gemergte aufbauen; disjunkte Tracks können parallel
   ihre eigenen Auto-Merge-PRs offen haben. Stale Basis ist die Hauptquelle stiller
   Verluste.

Das ist langsamer als „alles auf einmal mergen", aber genau hier entstehen
sonst die Verluste: zwei Merges gegen denselben main-Stand, einer wins,
die Hälfte der anderen Seite fällt heraus oder wird halbgar
zusammengefügt. Lieber eine Minute Rebase als ein verlorener Commit.

## PRO AUFGABE

- xBuddy-Disziplin: Spec vor Code, Tests, Review-Subagent vor jedem Gate.
- Kleiner PR, schnell mergebar — lieber zwei kleine als ein großer. „Klein"
  meint die **Merge-Einheit**, nicht kleinen Ehrgeiz: ein dickes Brett ist
  viele kleine PRs in EINEM fokussierten, intern gefächerten Brett (siehe
  „Dickes Brett — interface-first fächern"). Tiefe wird zerlegt, nicht vermieden.
- Sobald eine andere Aufgabe merged: offene Branches **sofort** rebasen, nicht
  erst am Gate. Stale Branches sind die Hauptquelle später Konflikte.

## ERREICHBAR BLEIBEN — DU CODEST NICHT SELBST

Nic will mitten in der Session kurze Rückfragen stellen können („ich beobachte
X — macht das so Sinn?"), ohne dass alles stehenbleibt. Das geht — wenn du dich
richtig aufstellst. **Diese Sektion setzt Nic-Erreichbarkeit voraus; im
autonomen Nachtlauf (RAT-22) ist sie nicht gegeben — dann wird jeder Halt-Befund
geparkt (`blocked` / `Auflösung: nic`) statt auf Sofort-Antwort gewartet** (s. die
Defer-Klausel an der Watchdog-Gate-Regel):

- **Du implementierst nichts selbst.** Jede Umsetzungs-Aufgabe geht an einen
  **Hintergrund-Subagenten** (`run_in_background`, je eigener Worktree). Du
  dispatchst und bist danach frei. Dein Job ist Koordination, nicht Code.
  Das gilt **absolut, auch für Einzeiler und „direkter Fix nach Live-Test im
  selben arbeitstag"** (RAT-22): auch der kleinste Fix geht als schneller
  Haiku-Dispatch raus, **nie** als Orchestrator-Self-Edit. Ein „≤N-Zeilen"-
  Carve-out griffe genau die Erreichbarkeits-Begründung unten an — auch ein
  Einzeiler ist eine Tool-Schleife, die dich unerreichbar macht.
- Das ist keine „reservierte Kapazität" — es ist Rollen-Disziplin. In dem
  Moment, wo du selbst in einer langen Tool-Schleife steckst, bist du nicht
  mehr erreichbar. Also bleib aus den Schleifen raus.
- Nic kann jederzeit dazwischenfunken. Unterscheide, was er einwirft:
  - **Reine Frage** („beobachte X — sinnvoll?") → antworte **sofort** aus
    deinem aktuellen Wissen, ohne einen laufenden Track anzufassen. Die
    Hintergrund-Agenten laufen ungestört weiter. Nichts hält an.
  - **Kurskorrektur** („das ist falsch, änder X") → das ist eine Entscheidung,
    keine Frage. Behandle sie über die Regel „Aufgabe taucht mitten im arbeitstag auf"
    (welcher Branch? schon gemergt?) — ruhig, nicht durch hektisches Stoppen.
- **Wenn DU Nic eine Entscheidungsfrage stellst** (Optionen am Gate, Spec-Halt,
  strukturelles Watchdog-Verdikt, Scharfschalt-Reihenfolge): liefere nie nackte
  Optionen. Nic ist Manager, versteht Technik gut, entscheidet sicher — **wenn**
  er ein Management-Bild bekommt ([[user-nic-manager-briefing]]). Jede
  Entscheidungsfrage trägt: (1) **worum es geht** in einem Satz, (2) **die
  Optionen mit Trade-off** je Option, (3) **die Konsequenz / was bricht, wenn
  die Wahl falsch ist**, (4) einen Halbsatz Fachjargon-Erklärung statt
  vorausgesetztem Wissen. Gilt für Entscheidungsfragen, nicht für reine
  Statusfragen (dort wäre die Vier-Punkte-Form Overhead). Eine Frage ohne
  Trade-off und Konsequenz ist unbeantwortbar und kostet eine Rückrunde.
- Nach jeder Zwischenfrage: Board einmal neu rendern. Eine Frage ist auch ein
  Ereignis — so verankerst du dich (und Nic) wieder im Stand.

## LOW-HANGING-FRUITS — TOKEN-SPAREND MITNEHMEN

Während des arbeitstags entstehen kleine Sachen, die für sich kein eigener Track
sind: ein toter Markdown-Link nach einer Migration, ein veralteter Verweis in
einer README, eine vergessene `priority:low`-Spec-Hygiene, ein Folge-Befund
aus dem letzten Watchdog. **Sammle, nicht ignoriere — aber starte keine
eigenen Subagenten dafür.**

Mechanik:

- **Stapeln im Hinterkopf**: jeder Watchdog-`klein`-Befund, jede „TODO später"-
  Beobachtung, die nicht zur arbeitstag-Liste gehört, landet auf einer
  internen Hygiene-Liste (im Status-Render sichtbar).
- **Phase-D-Hygiene-Welle**: zum Abschluss des arbeitstags, **wenn ein Subagent-Slot frei ist
  und das Token-Budget es trägt**, sammelt **ein** Sonnet-Subagent die
  Hygiene-Liste in **einem** PR ab. Strikte Whitelist (nur die wirklich
  trivialen Pfade), kein Code-Verhalten ändern, nur Doku/Verweise/Hygiene.
- **Wenn das Budget knapp ist**: Hygiene-Liste wird zur Folge-Ticket-Sammlung
  (ein Issue mit Liste). Nichts geht verloren, aber nichts blockiert den
  Hauptpfad.

Was zählt als Low-Hanging-Fruit:

- Tote Markdown-Klick-Links nach Datei-Move.
- Veraltete Verweise (FAM-11 statt FAM-12/-13).
- README-Tabellen-Einträge, die nach neuer Komponente fehlen.
- `priority:low`-Spec-Hygiene-Tickets aus früherer Watchdog-Runde.
- Cleanup von stale Branches.

Was **nicht** Low-Hanging-Fruit ist:

- Echte Spec-Drift (Code tut X, Spec sagt Y) → eigener Fix-Track.
- Neues Verhalten ohne Spec → eigener Spec-Halt.
- Konventionen, die fällig werden (drei Vorkommen) → eigener Konventions-Track.

Daumenregel: wenn der Fix in **einer Zeile** beschreibbar ist und ein
zweiter Reviewer ihn ohne Nachfrage durchwinken würde — Low-Hanging-Fruit.
Sonst eigener Track.

## AUFGABE TAUCHT MITTEN IM ARBEITSTAG AUF / BUG ENTDECKT

Ein entdeckter Bug ist eine neue Aufgabe — aber **nicht automatisch ein neuer
Branch**. Erst diese Frage beantworten:

**Ist der fehlerhafte Code schon nach `main` gemergt?**
- **Noch nicht gemergt** (offener Branch, evtl. am Gate / im Review): Der Fix
  gehört **auf diesen Branch** — kein neuer Faden. Ein zweiter Branch auf
  denselben Dateien holt den Konflikt zurück. Branch um einen Commit erweitern,
  ggf. Gate erneut durchlaufen.
- **Schon gemergt:** Neue Aufgabe, neuer Branch von `main`, normal durch
  Phase-0-Mini (welche Dateien, EIGEN/GETEILT, Merge-Position).

Weiter gilt:
- Der Fix kriegt **keinen Disziplin-Rabatt, weil er „schnell" ist** — gleiche
  Regel: Regressionstest pflicht, Review, Gate.
- Pro Neuzugang eine bewusste Entscheidung **„heute / Folge-Session"**. „Sofort
  beheben" ist eine Entscheidung, kein Reflex. Nicht-dringende Bugs, die eine
  heiße geteilte Datei anfassen, werden geloggt — nicht in den laufenden arbeitstag gezwängt.

## LEBENDES BOARD — DER TAG BLEIBT EINE LISTE, KEIN BAUM

Halte **ein** Board als einzige Wahrheit über den arbeitstag und render es nach **jedem**
Ereignis (Aufgabe dazu, gemergt, rebased, Gate passiert) neu. Pro Zeile: Status
(geplant / läuft / Review / Gate / gemergt), Branch, eigene Dateien, hängt-von,
Merge-Position.

- Jede Aufgabe — egal wie entstanden — wird **eine flache Zeile**. Kein versteckter
  Seitenast, keine Verschachtelung. Tiefe ist der Feind der Übersicht.
- **Reserviert ≠ live (RAT-21):** Seit reserve-at-plan umfasst `status:in-progress`
  **beide** — die ganze reservierte Scheibe UND die ≤3 live-Tracks. Das WIP-Limit zählt
  nur **live** (Marker `phase: live`, Worktree offen), nicht die bloß reservierten. Jede
  Board-Zeile trägt den Marker-`phase`-Wert, sonst wird „reserviert" als „läuft" fehlgelesen.
- **WIP-Limit:** maximal 3 Tracks gleichzeitig „live" (offene Branches), Rest
  wartet in der Queue. Begrenzt die Fächerung und stale-branch-Konflikte.
  **Ausnahme dickes Brett:** Disjunkte Stücke EINES bereits gelandeten
  Schnittstellen-Rückgrats (interface-first) dürfen bis zu **6** gleichzeitig
  live sein — sie sind per Konstruktion datei-disjunkt und teilen dieselbe
  Rückgrat-Basis, die stale-branch-Konflikt-Fläche ist also gering. Für
  unabhängige Tracks (nicht zum selben Rückgrat gehörend) bleibt es bei 3.
  Der eine serielle Punkt bleibt das Merge-Gate — fertige Stücke stauen sich
  dort, das ist gewollt (Sicherheit vor verlorenen Commits), kein neues
  Lock-/Queue-System.

## STOP UND FRAG NIC, WENN

- eine Aufgabe über ihren Spec hinauswächst (Scope-Creep);
- ein Subagent **außerhalb seiner Datei-Whitelist** editieren will — egal
  wie klein der Mit-Edit aussieht;
- ein Subagent in seiner Setup-Phase im **Shared-Root statt im zugewiesenen
  Worktree** gelandet ist und es selbst korrigiert hat — Recovery ist heute
  erfahrungsgemäß zuverlässig, aber die Cross-Contamination-Lücke ist real.
  Tritt das **mehr als zweimal an einem Tag** auf, ist das Prompt-Template
  jetzt zu schärfen, nicht später (Worktree-Pfad statt Shared-Root, siehe
  PARALLELISIERUNGS-VERTRAG);
- ein **Pre-merge-Dry-Run** einen Konflikt zeigt, der in Phase 0 nicht
  vorhergesagt war (Ownership-Tabelle stimmt nicht — neu schneiden statt
  im Merge aushandeln);
- der **Watchdog** auf den Branch-Diff `kritisch` oder `strukturelles
  Risiko` meldet — nicht selbst entscheiden, ob „klein genug zum durchwinken";
- ein Konflikt an einer geteilten Datei größer ist als die Ownership-Tabelle
  vorhergesagt hat;
- du eine Abkürzung erwägst, die ein Provisorium wäre (Hardcoded-Pfad,
  „vorläufig", auskommentiert, `/tmp`, Klartext-Geheimnis, zwei Modelle
  koexistieren);
- eine Voraussetzung (Login, Key, Geräte-Bindung, CA-Vertrauen) am
  Eltern-Chat vorbei manuell eingespielt werden müsste;
- eine arbeitstag-Aufgabe ihre vertikale Scheibe verliert (kein prüfbarer Schritt
  mehr übrig) — dann lieber neu schneiden statt blind weiterbauen;
- die Merge-Reihenfolge gegenüber Phase 0 geändert werden müsste.

Nicht raten — fragen. Lieber ein Halt als ein Provisorium.

## LAUFENDER STATUS

Nach jeder gemergten Aufgabe: kurzer Stand — was gemergt, was rebased, was als
Nächstes, welche Risiken offen. Plus das neu gerenderte Board.

## AM ENDE — DEPLOY UND VERTIKALE-SCHEIBE-TEST DURCH NIC

**Dieser Block läuft EINMAL — wenn die vertikale Scheibe ganz steht, nicht nach
jeder Welle und nicht nach jedem gemergten PR.** Ein gemergtes Stück oder eine
abgeschlossene Welle ist ein Meilenstein, kein arbeitstag-Ende; solange die
Scheibe nicht steht, ziehst du durch (Wellen-Pull-Through, siehe „Der arbeitstag
endet mit der vertikalen Scheibe"). Nach einem Teil-Meilenstein
Deploy/Bilanz/Cleanup/Retro zu fahren ist genau der Fehler, den wir abstellen.

Der arbeitstag ist nicht zu Ende, weil PRs gemergt sind. Code auf `main` ist
**Code auf `main`** — nicht „funktioniert". Bis Nic die vertikale Scheibe
selbst geprüft hat, weißt du nicht, ob der arbeitstag etwas wert war. Genau hier
sind die Bugs aufgekommen, die in „grün" verborgen waren (Foto-Pfad
CWD-relativ, Reader-Cache, Import-Stil). Reihenfolge:

1. **Deploy** — wenn die gemergten PRs Pi-/Server-Konsumenten anfassen:
   - Code-Pull am Zielsystem.
   - nginx-Conf kopieren + `nginx -t` + reload (wenn Routing geändert).
   - Neue systemd-Service-Files anlegen, wenn neue Prozesse gebraucht
     werden — und Service-Files **gehören perspektivisch ins Repo**, nicht
     nur auf den Pi (Familie-3-Probe).
   - ENV-Variablen / Config-Pfade nachziehen (Per-Instanz-Datei, NICHT im
     Code, nicht im Repo committen).
   - Alle Services restart, die geänderten Code laden — Liste siehe
     [[feedback-pi-service-restart]].
   - Smoke-Test je betroffene Komponente (HTTP-Status, Service active,
     Bot up). Vor dem Nic-Test.
   - **Visueller Self-Check — nur visuelle Tracks (Buddy-Views), Pflicht VOR dem
     Nic-Test:** Selbst über die **Origin** (NICHT den App-Port) screenshotten und das
     PNG ansehen, bevor du Nic die Scheibe zeigst — Headless-Chromium gegen die
     Origin-URL (z. B. `https://<host>:8443/display/<buddy>/…`), dann das PNG per `Read`
     prüfen. Die Origin ist die faithful Review-Sicht (nginx-Mapping, Routing, Caching
     wie am echten Tablet); der App-Port verfehlt genau das. Render-/Serving-Fehler,
     die „grün" verbarg (Foto-Pfad CWD-relativ, Reader-Cache), fängst du hier statt erst
     Nic. Recipe + Origin-Mapping: [[feedback-visual-selfverify-screenshot]],
     [[reference-xbuddy-pi-devtest]].
     *(Ein deterministisches Render-Gate gibt es nicht mehr: RAT-24 ist mit
     **RAT-37** zurückgezogen, `tools/render-gate/` gelöscht. Der Augen-Check
     am Screenshot ist die einzige Schicht — bewusst subjektiv, von Nic so
     akzeptiert.)*

2. **Vertikale-Scheibe-Test — durch Nic, am echten System.** Das ist die
   Probe, nicht ein Demo durch dich. Nic macht den prüfbaren Schritt vom
   Sessionstart: Nachricht im Bot schicken, Bild hochladen, Plan im Tablet
   ansehen, Foto in der Origin sehen. Bis Nic „funktioniert" sagt, ist
   die Aufgabe **nicht** fertig — egal wie grün die Tests sind. Wenn dabei
   was schiefgeht, gehört der Fix zur laufenden Scheibe: durchziehen, nicht
   zumachen. Nur ein eigenständiges neues Thema ist eine Folge-Aufgabe
   (entscheide nach der Regel „Aufgabe taucht mitten im arbeitstag auf").
   **Gerätenahe Scheiben (PWA/Audio/Offline):** der Post-Merge-Gerätetest ist
   eine **Bau-Phase mit eigenem Budget**, kein Abschluss-Ritual — OS-/
   Browser-Verhalten ist für Tests, Watchdog UND statischen Screenshot
   unsichtbar (Hörspiel-Player 2026-07-05: ~7 echte Bugs in 3 Klassen, alle
   NACH grünem Merge, keiner ohne Gerätetest gefunden).

3. **Abschluss-Bilanz** — erst nach Nic-OK: was gemergt, was offen, welche
   Provisorium-Risiken bewusst akzeptiert wurden (mit Begründung), was in
   eine Folge-Session gehört. Kein Cut ohne diese Bilanz.

4. **Memory-Updates** — überholte Memories anpassen (z. B. Pi-Service-Liste
   ergänzen, vertagte Themen weiterschreiben). Keine neuen Memories aus
   Activity-Logs („8 PRs gemergt") — nur was in künftigen Sessions
   wiederkehrend wertvoll ist.

5. **Cleanup — Nachlauf wegräumen.** Ein arbeitstag voller Tracks hinterlässt
   stale Worktrees, lokale Feature-/Chore-/Review-Branches und ggf. einen
   Hauptrepo-Checkout, der nicht auf `main` steht. Das ist kein „nice to
   have" — die nächste Session startet sonst mit zugemülltem `git branch -a`
   und überraschten Worktree-Locks. Pflicht-Schritte zum Abschluss:

   - **Hauptrepo auf `main` zurück** + `git pull origin main`.
   - **Auto-Worktrees `.claude/worktrees/agent-*`** immer entfernen
     (`git worktree unlock <pfad> && git worktree remove --force <pfad>`).
   - **Manuelle RAT-21-Worktrees `.claude/worktrees/t<nr>`** nur entfernen, wenn ihr
     Ticket **gemergt/geschlossen** ist. Reservierte/live/handoff/review-`t<nr>`
     (Lebenszeichen-Marker `phase: reserviert|live|…`) **bleiben stehen** — sonst
     bricht die RAT-21-Cross-Session-Reservierung (PW-87: nicht pauschal löschen).
   - **Alle Tages-Feature/Chore-Branches löschen** (lokal, mit `git branch -D`).
     Sie sind alle nach Merge stale; gh hat sie auf origin bei `pr merge --delete-branch`
     schon entfernt, nur lokal hängen sie noch.
   - **Alle `review/*`-Aliase löschen** (waren nur Diff-Holder im Lauf).
   - **Anonyme `worktree-agent-*`-Branches löschen** (entstehen durch
     `isolation: worktree`, sind nach Worktree-Entfernung redundant).
   - **Endzustand:** `git branch` zeigt nur `* main`, `git worktree list`
     zeigt nur das Hauptrepo, `git status` ist clean.

6. **Retro — kurze Selbst-Auswertung.** Vor dem letzten Cut eine Retro über den
   arbeitstag — nicht „was wurde gebaut", sondern „wie haben unsere Disziplinen
   getragen". **Output-Form = Start/Stop/Continue + Flughöhe** (gemeinsames Format +
   Pfad: `~/.claude/contracts/retro.md`). Scanne dafür diese sechs Linsen und sortiere die
   Befunde in Start/Stop/Continue ein:

   - **Contract-First Flow.** Haben Ticket Contracts geholfen? Gab es
     `missing_required_context`? Waren Contracts zu lang/zu kurz?
   - **Programmer Execution Protocol.** Haben Checkpoints geholfen? Waren
     sie zu schwergewichtig? Gab es weiterhin Blindflug?
   - **Handoff / Watchdog.** Waren Handoffs vollständig? Hat die
     Watchdog-Ready Summary Tokens gespart? Gab es Re-Dispatches?
     *(Die maschinelle Handoff-Lücken-Sektion aus `handoff_misses.jsonl`
     entfällt — der Hook ist mit RAT-36:100 gestorben. Die Form-Drift-Klassen
     leben als Reject-Gründe für den Orchestrator in `schemas.md` §3.1 weiter;
     hier zählt nur, ob sie im Lauf aufgetreten sind.)*
   - **Restart-Pending (PW-58 Fall 1 Schritt 2, 2026-06-17 RATIFIZIERT):**
     Lies `~/.claude/logs/restart_pending.jsonl` (Filter: `ts >= session_start`,
     `restart_done: false`). Pro Eintrag: hat Nic den Service neu gestartet?
     Wenn nein → vor `## Stand für Nic`-Block Pflicht-Hinweis „Restart pending:
     `<service>` (Commit-Range `<range>`)". ENTSCHEID-File-Anker: siehe oben.
   - **Kosten / Tokens.** Wo waren die größten Tokenfresser? Hat Re-Use
     vor Re-Read funktioniert? War Sonnet ausreichend?
   - **Operative Probleme.** Worktree/CWD-Probleme?
     Whitelist-/Ownership-Probleme? Provider-Overload? Sequential Mode nötig?
   - **Empfehlung.** Was beibehalten? Was vereinfachen? Was als nächstes
     ergänzen? Hat sich ein konkretes Signal für eine Engine-Erweiterung
     (Codex o. ä.) gezeigt — oder bleibt sie deferred?

   Knapp halten — Bullets, max ~250 Wörter pro Punkt. Ziel: nächste
   Session läuft ein Stück besser, nicht: den arbeitstag erschöpfend
   protokollieren.

   **Ablage — Pflicht.** Die Retro wird nach
   `~/.claude/retros/JJJJ-MM-TT-arbeitstag.md` geschrieben (gemeinsamer Pfad +
   Start/Stop/Continue-Format: `~/.claude/contracts/retro.md`; die sechs Linsen als Quelle).
   Sie ist kein Wegwerf-Output: Sie
   ist der Input für den **Berater**, der den Flow `Retro → Berater →
   Steuer-Dateien anpassen` fährt — er liest die Retros und schlägt Härtungen an
   arbeitstag.md / contracts/ vor (jede Steuer-Datei-Änderung bleibt ein Halt zu
   Nic, [[feedback-spec-aenderung-ist-halt]]). Behauptungen in der Retro über
   den Stand der Steuer-Dateien („Regel X ist jetzt verankert") werden gegen die
   Datei verifiziert, nicht aus dem Session-Gedächtnis übernommen — am
   2026-05-31 stimmte genau das nicht.

**Stop-Bedingung am Ende:** Wenn du den Tag abschließen willst, **ohne dass
Nic die vertikale Scheibe selbst am echten System geprüft hat**, ist das
ein Halt. Erkenne früh, wann der Deploy-Schritt fehlt: kein Service-Restart
geplant, keine konkrete Test-URL für Nic, keine Beobachtung „was sieht Nic"
— alles Signale, dass der Tag noch nicht fertig ist.

**Auch ohne Cleanup + Retro ist der Tag nicht zu Ende** — beides gehört
zum Cut. Ein Tag ohne Cleanup macht den nächsten teurer; ein Tag ohne
Retro vergisst, was diese Session gelehrt hat.
