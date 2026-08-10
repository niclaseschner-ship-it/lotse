---
description: Buddy-Werft — führt eine Familien-Idee von der Rahmung bis zum übergabereifen xbuddy-Ticket (Idee → Übergabe-Ticket, vor /arbeitstag). Hält an Nic-Gates A/B/C.
argument-hint: "[Buddy-Idee in einem Satz ODER Ticket-Nr, z. B. 'Routine-Buddy' oder '#137']"
---

# /werft — die Buddy-Werft

Du führst **eine Familien-Idee** durch den Idee→MVP-Flow bis zu einem
übergabereifen GitHub-Ticket für `/arbeitstag`. Die Werft sitzt **vor**
`/arbeitstag`: arbeitstag baut bereits geklärte Tickets konfliktfrei parallel —
die Werft klärt **vorher, *was* gebaut wird**.

Engpass ist Nic. Alles zwischen den Gates machst du **autonom**; Nics Urteil
bündelst du auf **drei scharfe Gates** (A Spec · B Design · C Paket).

**Erdung:** der Checkout `${LOTSE_PROJECT_ROOT}` (Session-Start `git pull
--ff-only`, origin ist die Wahrheit — RAT-9). Nur xbuddy ist im Scope.

> **Datenbasis dieses Rezepts: n=2** (WetterBuddy #137, RoutineBuddy) — **beide
> display-only**, siehe „Grenzen" unten. (Verweise auf `RAT-`/`PW-`-Nummern + Specs
> im Text sind Referenz-Projekt-Artefakte, keine Framework-Pflicht — siehe README.)

---

## Bewusst NICHT Teil dieses Commands
- **Der KI-Eltern-Input-Katalog** (KI führt das *Gespräch mit der Familie* und
  verdichtet zu einem Spec-Rohentwurf) ist eine **Produkt-Funktion**, kein
  Entwickler-Prozess. **Geparkt** — kommt später, entweder als Erweiterung hier
  oder als zweiter Skill. **Hier nicht einbauen.**
- **Reine Eltern-Chat-Skills (kein neuer Buddy, kein View, kein neues DS)
  gehören in `/arbeitstag-prep`, nicht durch die Werft** (Nic-Befund
  2026-06-08, Werft-Retro #354). Die Werft ist auf Buddies/Views/DS-Beiträge
  geschnitten. Wenn die Idee als reiner Skill-Bau ankommt: an `/arbeitstag-prep`
  übergeben, nicht F2/F3 aufsetzen.
- **Deploy-Runbook** → das ist `/arbeitstag` hinter der Naht.
- **Domänen-spezifische Test-Regeln** (z. B. Wetter-Clock) → bei den Tests des
  Buddys, nicht als Werft-Regel.
- **Neue Konventionen auf Vorrat** → `conventions/` entsteht beim 2. Vorkommen
  mit konkretem Schmerz, nicht antizipativ.

## Disziplin (über allen Phasen)
- **Interface-first, immer (Nic-Standard 2026-06-06, n=PhotoBuddy).** Wenn ein
  Buddy später eine fremde Schnittstelle anfasst (z. B. Eltern-Chat-Schreibpfad),
  denkt die V1-Spec **schon jetzt die volle API-Schnittstelle mit, die es
  braucht** — inkl. des Schreib-/Ingest-Endpoints, den der spätere Konsument ruft.
  Die Integration des Konsumenten wird **nachgezogen**, aber V1 **exposed bereits
  alles**. Der Abend-Test läuft gegen genau diese API (z. B. `curl`-Seed). Der
  Contract IST die Architektur-Entscheidung — die kommt nach vorn, das Plumbing
  nach hinten. Entschärft die APP-4-/Schreibpfad-Strecke aus „Grenzen".
- **Plan vor Code, Spec-Änderung = Halt.** Lege keine Datei an / lande keine Spec
  ohne Nics Bestätigung (CLAUDE.md §7 im xbuddy-Repo).
- **Halt an jedem Gate.** Gate A (Spec-Freigabe), Gate B (Design-Wahl), Gate C
  (Paket inkl. reconcilte Spec **vor** Handoff zeigen).
- **Re-Litigations-Check zuerst:** bevor du etwas neu beräts, prüfe
  `decisions/INDEX.md` (Ratifizierungs-Ledger) **und** existierende
  Requirement-IDs/Ports/Tickets — ist das schon entschieden/gebaut?
- **Shared-Root-HEAD-Serialisierung (CHK-1):** Läuft parallel ein `/arbeitstag`,
  besitzt der den Shared-Root. Die Werft arbeitet dann **Worktree-only**
  (`git worktree add --detach /tmp/… origin/<branch>`, push, `gh pr`) und fasst
  den Root-HEAD (`checkout`/`merge`/`branch -f main`) nur unter `flock -n
  ${LOTSE_PROJECT_ROOT}/.git/shared-root.lock` an — kriegt sie den Lock nicht,
  bleibt sie im Worktree. Nie `git push origin main` (RAT-10 blockt es ohnehin).
- **Nummern nie nackt:** Issue-/PR-/Requirement-IDs immer mit kurzer Überschrift.
- **Nic mitnehmen, nicht autonom stempeln + hinterher informieren.** Was im Prep
  klärbar ist, klärst du mit Nic — schiebe es nicht auf `/arbeitstag`.

---

## F1 — Idee rahmen  *(kein Gate)*

**F1-Start: Werft-Held-Marker setzen + verwaiste Tickets prüfen (PW-25 RATIFIZIERT 2026-06-21):**

1. **Verwaisten-Check** — `gh issue list -R ${LOTSE_PROJECT_REPO} --label in-werft --state open --json number,title,updatedAt` listen. Tickets mit `updatedAt > 24h` Nic vorlegen: „Werft-Lauf an #<nr> begonnen am <iso>, kein F5-Stempel — fortsetzen, abbrechen (Label entfernen), oder neu starten?" Erst dann neue Werft.
2. **`+in-werft`-Label setzen** auf das aktuelle Werft-Ticket: `gh issue edit <nr> -R ${LOTSE_PROJECT_REPO} --add-label in-werft`. Property-Label (RECON-3-konform via `conventions/reconcile.md:67-71`), markiert „Werft hält dieses Ticket aktiv". `/arbeitstag-prep` filtert es und zeigt es als deferred (PW-25 Reparatur 3).
3. **Bei Werft-Abbruch zu jedem Zeitpunkt:** `-in-werft` entfernen, Nic kurz informieren.

- **Modus-Eingang ZUERST** (Werft-Retro #354 2026-06-08; erweitert PW-38 2026-06-10):
  drei legitime Modi —
  **Neu-Bau eines Buddys** (volles F1–F5), **Bündel-Lauf** (Spec liegt auf `main`,
  springt direkt zu F4/F5; F2/F3 wären Re-Litigation), **Update-Lauf** (Spec liegt,
  aber ein Verhaltens-Delta wird ergänzt — Delta-F2 + F3 + F4 + F5).
  **Triage am Ticket, ohne Pi-Lookup** (PW-38 Befund: Pi-Zustand darf semantische
  Klassifikation nicht verschieben):
  1. **Spec-Such-Probe:** `git log --oneline origin/main -- specs/buddies/<slug>.md
     specs/platform/<slug>.md` + `decisions/INDEX.md`-Grep + `gh issue view <nr>
     --json body | jq -r .body | grep -oE '<PREFIX>-[0-9]+'` gegen `grep -oE
     '^#+\s+<PREFIX>-[0-9]+' specs/.../<slug>.md` (Requirements dürfen `##`
     **oder** `###` sein, `specs/README.md:66-69` — nicht nur `###`).
  2. **Verhaltens-Delta-Probe:** Verlangt der Ticket-Body eine neue/geänderte
     Verhaltens-Klausel (Wenn/Dann, View-/API-Verhalten) gegenüber dem aktuellen
     Stand der Spec?

  | Probe 1 (Spec auf main, IDs zitiert) | Probe 2 (Verhaltens-Delta) | Modus |
  |---|---|---|
  | nein | — | **Neu-Bau** |
  | ja | nein | **Bündel-Lauf** |
  | ja | ja | **Update-Lauf** |

  Gemischte Sammler sind legal: **je Ticket-Cluster** klassifizieren, nicht je
  Sammler (Belegfall #578 — Plan-Aktivitäten: Bündel für #445/#471/#473 + paralleler
  Update-Lauf für PLAN-34/PAS).
  **Stack-förmiger Anlass** (Keystone-Entscheid + ≥3 Folge-Tickets / Initiative)
  → Epic + Kinder per `conventions/epics.md`, **kein** Werft-Sammler und kein
  eigener Werft-Modus (xbuddy-prozess#72, 2026-08-07).
- **Vertikale Scheibe** benennen: der eine Weg, den Nic am Abend klicken kann
  (z. B. „Kachel → Routine-View auf :8443 am Tablet").
- **Existenz-Grep** (mit `--exclude-dir=__pycache__,.git`):
  `find specs -iname '<slug>*'`, `grep -n <slug> conventions/ports.md`,
  bestehende Spec/Port/Ticket? Inkl. **`blocked`-Label-Check** am Ticket
  (n=1-Reibung: Ticket trug noch `blocked`, obwohl der Lauf startete).
  Zusätzlich **Verwandtschafts-Check über offene Tickets**:
  `gh issue list -R ${LOTSE_PROJECT_REPO} --state open --search "<thema>"`
  (Belegfall #1030: verwandter offener Track nur zufällig übers area-Label
  gefunden).
- **Asset-/Piktogramm-Abdeckungs-Check** gegen die Domäne — **früh**, nicht erst
  im Design (n=1: ARASAAC hatte keine Wetter-Szenen-Reihe, fiel zu spät auf).
  Bei ARASAAC: als **eigenes Artefakt `arasaac-probe/befund.md`** mit Tabelle
  `Kategorie | Label | ID | OK?` ablegen (Werft-Retro #474 2026-06-09), nicht
  nur in der Spec-Sektion abhaken — gibt der Spec einen reconcile-fähigen
  Beleg und überlebt die Werft als prüfbare Referenz für `/arbeitstag`.
- **„Trägt die Quelle schon?" ist eine Schema-Frage, keine Existenz-Frage.** Wenn
  der Buddy eine fremde Quelle als Add-/Daten-Quelle nutzt, das **Pflichtfeld-Schema
  des Konsumenten × das Schema der Quelle feldweise diffen**, BEVOR die Quelle als
  „trägt schon" gilt — eine Registry kann alle Einträge kennen und das eine
  Pflichtfeld trotzdem nicht führen (n=1: Seiten-Registry SREG-4 ohne `icons[]`, das
  Panel-Kachel PANEL-3 als Pflicht verlangt; fiel erst in F2 auf). Belegt mit Grep
  aufs echte Schema, nicht aus der Spec ableiten (CLAUDE.md §7).
- **Idee-Inhalt** liegt oft nur im Ticket-Body / einem verlinkten Bericht —
  dort extrahieren, nicht im Repo erwarten.
- Leg Nic das Ergebnis kurz vor, bevor du in die Spec-Runde gehst.

## F2 — Geführte Spec-Runde  →  ⛔ **GATE A: Spec-Freigabe (Nic)**

**Halte-Zeit-Disziplin (PW-44 V1, 2026-06-12 RATIFIZIERT — C3 Variante):** Der
Spec-PR wird in F2 **NICHT** angelegt. F2 produziert eine **Spec-Draft**, deren
Form vom F1-Modus abhängt (Codex-Bruch Pass 2: Update-Lauf bricht sonst PW-38):
- **Neu-Bau:** vollständiger Draft als brainstorm-File
  (`${LOTSE_SCRATCH}/werft-drafts/<ts>-<slug>-spec.md`) oder direkt im
  Ticket-Body.
- **Update-Lauf:** Draft ist ein **Delta-Patch gegen eine dokumentierte
  Base-SHA** (`git rev-parse origin/main`), KEINE vollständige Zweitkopie der
  bestehenden Spec — sonst wird PW-38 (Delta-Patches an existierender Spec,
  keine parallele Zweit-Datei) gebrochen. Speicherform:
  brainstorm-File mit `Base-SHA: <sha>` im Header + Unified-Diff im Body, oder
  Ticket-Body mit denselben Feldern. F3-Ende wendet den Delta-Patch auf den
  **aktuellen** Spec-Stand an (`git apply` ggf. mit Konflikt-Auflösung) und
  legt dann erst den PR an.

Gate A ratifiziert den Draft, nicht einen offenen Branch gegen `origin/main`.
So lebt die Spec **erst ab F3-Ende** als PR — Drift-Fenster schrumpft von
Stunden bis Tage auf typisch 30min–2h. Inhaltlicher Bonus: die Spec wird erst
NACH Design geschrieben, Reconcile wird trivial bis überflüssig.

- **Update-Lauf (PW-38 2026-06-10) — Triage in F1 hat klassifiziert.** Spec-Arbeit
  = **Delta-Patches** an existierender `specs/buddies/<slug>.md` /
  `specs/platform/<slug>.md`, **keine parallele Zweit-Datei**. Neu hinzukommende
  Sub-Fähigkeiten (Skills, eigenständige API-Specs nach `specs/README.md:17-19`)
  gehören als **eigene Datei in denselben Spec-PR** wie die Delta-Patches — nicht
  in Folge-PRs (Belegfall #578: PAS + PLAN-34 zogen mit Plan-Spec-Deltas im selben
  PR). Gate A oft dünn; Design→Spec-Reflux nach Gate B ist normal, kein Fehler.
- **Spec-Klausel-Lese-Falle (PW-38 2026-06-10):** „Layout 1:1" / „Verhalten
  unverändert" ist eine *Annahme*, keine *Prüfung*. F3 ist auch im Update-Lauf
  **Pflicht** — Daten-/Quelle-Wechsel ändern die visuelle Wirkung selbst bei
  identischem Layout (Belegfall Plan-Aktivitäten-Update 2026-06-09: ARASAAC brach
  Wireframe-Stil, F3 zunächst übersprungen).
- **Erst Features sammeln/verdichten, dann formalisieren** (n=1: zu früh in
  Spec-Form gerutscht; Slot für **vorhandene Vorarbeit** einlesen).
- Interview gegen die **6 optionalen** Checklisten-Punkte aus `specs/README.md`
  (optional heißt: **keine** Pflicht-Slots; leere Sektion = Fehler) + die
  xbuddy-Pflichtfragen:
  - **Schnittstellen-Abfrage:** Welche `/api/v1/<slug>/…` exponiert der Buddy?
    Welche fremde Schnittstelle konsumiert er? (Daten-API ≠ Registrierungs-
    Metadata wie Slug/View-Pfad/Port — nicht verwechseln.)
  - **Familie-3-Probe:** Was variiert je Familie → **Config, nicht Code**.
  - **Aktiviert dieser Buddy eine vertagte/vorbereitete Konvention?** (≥3-Regeln-
    Test für `conventions/buddies.md`; sonst durch `apps.md` erledigt.)
- Entwurf als `specs/buddies/<slug>.md`, Präfix `<SLUG>-`, Requirement-IDs
  (testbar, Wenn/Dann), OPEN-Punkte, Entscheidungen. Bei echter Architektur-Gabel:
  `/berater-runde` (sonst direkt als berater-Linse).
- **Skill-Specs gleich im selben Spec-PR mitziehen** (Nic 2026-06-09,
  Essens-Buddy-Werft #474): Wenn der Buddy V1 eigene Eltern-Chat-Skills hat,
  gehören deren Specs (z. B. `specs/platform/<skill>.md`) **in denselben
  Spec-PR** wie die Buddy-Spec — nicht in Folge-PRs. Spec-Vollständigkeit der
  V1 wird sonst in Etappen gestempelt; Gate A wird zu einem einzigen
  zusammenhängenden Review, `/arbeitstag` bekommt das vollständige Paket.
- **GATE A (Nic):** Spec-Draft lesen, freigeben. Der Draft lebt als brainstorm-
  File / Ticket-Body — **kein PR auf main** (PW-44 V1 C3, 2026-06-12). Der
  Draft wird in F3 weiter entwickelt; PR-Anlage ist F3-Schluss-Aufgabe.

  Wenn die Werft am F3-Ende die finale Spec als PR pusht, gelten weiterhin:
  - **Eigener Spec-PR** (`Refs #<nr>`, Änderung nur unter `specs/` — der
    `closes-guard`-Spec-Ausgang, RAT-10), den die **Werft selbst landet** (F5).
    **Nicht** `/arbeitstag`: der merget nie Specs (WORKFLOW.md#handoff).
  - **`conventions/` berührt? `--label type:docs` Pflicht** beim
    `gh pr create` — `closes-guard` lässt den Spec-Ausgang nur an `specs/` ohne
    Label durch (`conventions/reconcile.md:27-28`). PW-24: das Label nachträglich
    zu setzen triggert den Check nicht automatisch neu, also gleich beim Anlegen
    mitgeben statt PR close/reopen-Hack.

## F3 — Design-Schleife  →  ⛔ **GATE B: Design-Wahl (Nic)**
- 2–3 statische HTML-Mockups der View. **Stilquelle = der geteilte
  Design-Token-Strang** `/display/_shared/design/tokens.css`
  (`conventions/design-tokens.md`, DTOK-1..5; seit #323 live).
- **Echte ARASAAC-PNGs schon in Gate B**, keine Platzhalter — über die ARASAAC-
  Such-API sourcen (`api.arasaac.org/api/pictograms/de/search/<wort>`). Mockups
  ohne echte Icons täuschen die Beurteilung.
- **Live-Daten in den Mockups, nicht Fiktion** (Lesson aus #467-Lauf, Werft-Retro
  2026-06-08): render gegen den realen Snapshot der relevanten Quellen
  (Inventar `GET /api/v1/seiten`, `panels.json`, `views.json`-Manifeste je
  Buddy, Geräte-Registry o. ä.). Fiktive Beispiele glätten vier Klassen von
  Befunden, die nur real-geerdet hochkommen: (a) Render-Bugs im Mockup-Generator
  (z. B. übersehene `varianten[]`), (b) reale n=1- oder N:1-Konstellationen, die
  Layout-Entscheidungen früh erzwingen, (c) konzeptionelle Mittelschichten
  zwischen Daten-Sorten, die abstrakte Beispiele leicht überspringen, (d)
  visuelle Gruppierungs-Forderungen, die erst beim Anblick mehrerer realer
  Geschwister-Einträge auf den Tisch kommen. Wenn eine Quelle nicht erreichbar
  ist, Fiktion **transparent als Fiktion markieren** und Nic mit dem Beleg-Stand
  ins Gate gehen, damit er nicht gegen unbelegte Beispiele entscheidet.
- **Token-Disziplin = menschliche Review**, kein blinder `#`/`px`/`rgb(`-grep
  (Bestands-Vorbilder enthalten selbst harte Layout-Werte). Farben = Tokens;
  Layout-`px` ok.
- **Komponenten-Optik:** gleiche Tokens ≠ gleiche Optik. Gegen die **bestehende
  Buddy-Card** erden (`wetter/static/wetter.css` `.card`/`.card-label`), nicht nur
  Tokens teilen. (Ob ein geteilter Komponenten-Layer fällig wird = Prozess-
  Werkstatt-Thema, kein Werft-Blocker.)
- **„1-aus-3" ist nicht starr:** steht die Richtung schon fest, wird F3 iterative
  Verfeinerung statt 3 paralleler Varianten.
- **Form-Konsistenz zwischen F3-Iterationen (PW-38 2026-06-10):** Die erste
  Iteration legt die Render-Form fest (Mockup-Variante / Picker / Screenshot /
  Live-Render). Folge-Iterationen patchen dasselbe Format nach — **0 stille
  Form-Wechsel**. Wenn die Form nicht trägt (z. B. nackter Snapshot kaputt wegen
  origin-absoluter Pfade), wird der Wechsel als eigener Schritt **benannt**
  („Form-Korrektur: von Live-Render auf Picker, Grund: …") und Nic vor der
  nächsten Iteration kurz mitgeteilt. Benannt ≠ verboten; still ist verboten.
- **Lieferform = Heim-IP-URL, nicht File-Pfad oder Chat-PNG** (Werft-Retro #474
  2026-06-09): Nic begutachtet Mockups am Tablet — `file://`-Pfade und im Chat
  eingebettete PNGs sind die falsche Form. **Standard:** in F3 einen lokalen
  `python3 -m http.server <port> --bind 0.0.0.0` auf festem Mockup-Port starten
  und je Variante eine `http://<heim-ip>:<port>/<datei>.html`-URL liefern. Heim-IP
  ist die WLAN-Adresse des Devhosts (`ip -4 addr show | grep wlan` o. ä.), nicht
  `127.0.0.1` (Tablet erreicht den Devhost nur über LAN).
- **Mockup-Server trägt seine Assets selbst — keine `localhost`-URLs im
  Tablet-tauglichen HTML** (Werft-Retro #532 2026-06-11): vom Tablet aus zeigt
  `localhost` aufs Tablet, nicht auf den Pi/Devhost → Bilder erschienen leer.
  **Standard:** alle Assets (ARASAAC-PNGs, Icons, JS-Libs) in den Mockup-Port-CWD
  cachen, **relative Pfade** (`./arasaac/<id>.png`, `./icons/<id>.png`). Keine
  Annahme, dass auf der ausliefernden Maschine dieselben Services laufen wie auf
  der konsumierenden. „Snapshot-Origin" ≠ „Asset-Origin" — explizit trennen.
- **F3 im Update-Lauf — Outcome: aussagefähiges Front-End zum Review am Tablet
  (PW-38 2026-06-10).** Pflicht ist das *Ergebnis* (Nic muss am Tablet das Delta
  am echten View-Bild beurteilen können), Werkzeug-Wahl ist der Werft überlassen
  (Effizienz). Erlaubte Default-Werkzeuge:
  - **Picker-Galerie** für Auswahl-Entscheidungen — eigene `mockup-picker.html`
    mit klickbarer JS-Wahl, origin-absolute Pfade gegen Heim-IP zum echten Service
    aufgelöst (Belegfall Plan-Aktivitäten-Update 2026-06-09: drei Tile-Galerien
    mit klickbarer Wahl als gerettete Endform).
  - **Headless-Screenshot** für „so sieht's nachher aus" — `chromium --headless
    --screenshot=after.png http://localhost:<port>/live-patched.html` nach dem
    lokalen Patch, PNG-Galerie über Heim-IP. Funktion muss nicht laufen.
  - **Live-Render mit Pfad-Rewrite per Präfix-Routing** **nur**, wenn der
    gepatchte View **keine** Schreib-Calls enthält. Vor dem Anbieten an Nic
    prüfen: `grep -E '"(PUT|DELETE|POST)"' <template>`. Trifft das Pattern, ist
    Live-Render **verboten** — Tablet-Klicks würden reale Familien-Daten ändern
    (AB2-Befund am Plan-Template `plan/templates/plan_kinder.html:700-785`).
    Picker oder Screenshot statt dessen. **Mechanik:** origin-absolute Pfade
    (`/api/...`, `/display/_shared/...`) per **String-Rewrite** im Snapshot auf
    den passenden Heim-IP-Port pro Präfix umschreiben (`/display/_shared/` → Hub
    auf Port 5000, `/api/<buddy>/` → Buddy-Port, etc.). `<base href>` wirkt NUR
    auf relative URLs (`./...`, `foo.png`) — Pfade mit führendem `/` löst es
    nicht auf (Werft-Retro #532 2026-06-11, empirisch im Browser geprüft).
  Snapshot-Quelle ist der Live-Service per `curl
  http://<heim-ip>:<realport>/<view> > live-current.html`; lokaler Patch
  (Python+regex / Editor) baut das Delta ein; Lieferung in einer Wrapper-Seite
  mit klickbarer Wahl der gepatchten Varianten. Erfolg messen an: 0 stille
  Form-Wechsel, 0 Stempel vor Gate B, und (für Screenshot) PNG stimmt visuell
  mit Live bis aufs Delta.
- **GATE B (Nic):** wählt die Richtung, optional eine Korrektur-Iteration.
- **Nach Gate B: Spec ↔ Design reconcilen** — das gewählte Design gegen den
  Spec-Draft (aus F2, PW-44 V1 C3) prüfen, Abweichungen in den Draft
  nachziehen, **bevor** Code beginnt (n=1: Hero-Element ≠ gewähltes Design,
  erst im Impl-PR gefangen).
- **F3-Ende: Spec-PR anlegen (PW-44 V1 C3, 2026-06-12 RATIFIZIERT).** Erst
  jetzt — nicht vorher. `gh pr create --draft` mit der finalen reconcilten
  Spec aus dem Draft. Halte-Zeit-Startpunkt: jetzt. Drift-Anker persistieren
  (Codex-Bruch Pass 2: `.werft/`-CWD-relativ + Verzeichnis fehlt + nicht in
  .gitignore — fail-closed mit absolutem Pfad in Git-Metadaten):
  ```bash
  WERFT_WORKTREE=${LOTSE_PROJECT_ROOT}  # oder echter Werft-Worktree-Pfad
  anchor_file="$(git -C "$WERFT_WORKTREE" rev-parse --git-path werft/last_drift_anchor)"
  mkdir -p "$(dirname "$anchor_file")"
  git -C "$WERFT_WORKTREE" rev-parse --verify 'origin/main^{commit}' > "$anchor_file" || {
    echo "Drift-Anker konnte nicht geschrieben werden — Werft halten"; exit 1;
  }
  ```
  Der Anker lebt in `.git/werft/last_drift_anchor` (worktree-lokales Git-
  Verzeichnis), nicht in einer ignorierten Repo-Datei — überlebt
  Worktree-Cleanup nicht (gewollt: Drift-Anker pro Werft-Lauf, nicht global).
  Backstop-Probe in F5 liest ihn.
- **F3-Ende: Mockup ins xbuddy-Repo persistieren (PW-54 V1, 2026-06-16 RATIFIZIERT;
  ENTSCHEID-File `20260616-1715-RATIFIZIERT-pw54-werft-mockup-anker.md` Sektion
  „Konvergenz/Brüche/Reparatur" → „(A) Mockup-Heimat ins xbuddy-Repo").** Die in
  F3 erzeugten Mockup-HTML-Dateien (das nach Gate B durchgelassene Set) werden
  als durables Gate-B-Artefakt nach `<xbuddy-repo>/specs/mockups/<spec-slug>/`
  kopiert (inkl. Assets im Unterordner `assets/`). Pfad **relativ zur Repo-
  Wurzel** im Werft-Handoff-Brief als `werft_mockup_path` ans Übergabe-Ticket
  (F4). `/tmp/`- oder `brainstorm/werft-drafts/`-Pfade sind im Handoff
  verboten — sie verlassen die durable Repo-Heimat (`decisions/README.md:15-20`)
  und werden vom Hook `dispatch_status_guard.py` bei Subagent-Dispatch geblockt
  (`stat()`-Existenz-Check auf `werft_mockup_path`). **Ab PW-83 (2026-07-03) wird
  das Feld zusätzlich am F5-Stempel selbst erzwungen** (`status_rollback_guard.py`,
  `deliverable_kind: ui_build`): der Handoff kann UI nicht mehr ohne Mockup-Feld
  verlassen. Nicht-UI-Tracks setzen `deliverable_kind: non_ui` + `deliverable_evidence`
  (statt `werft_mockup_path` einfach wegzulassen).
- Render-/Screenshot-Rezept zur Laufzeit notieren (z. B. Sonnet-Subagent rendert,
  `chromium --headless` schießt Screenshot, Vorschau via `python3 -m http.server`).

## F4 — Übergabe-Ticket schnüren  →  ⛔ **GATE C: Paket-Abnahme (Nic)**
Das **GitHub-Issue** trägt (arbeitstag-Phase-0 entscheidet final):
1. **Vertikale Scheibe** (aus F1) = Nics Abend-Test.
2. **Requirement-IDs** der gemergten Spec + zu erfüllende Konventions-IDs.
3. **Belegte IDs:** Port, Slug, Display-Pfad.
4. **Track-Schnitt-VORSCHLAG** (arbeitstag entscheidet): EIGEN vs. GETEILT
   (Router-Eintrag, `ports.md`, ggf. `tasks.py`). **Achse = App-Eigentum**
   (APP-1, `conventions/apps.md:10-16` — eine App besitzt Daten + Funktion +
   Schnittstelle gemeinsam). Default: **ein Track je App-Eigentümer**.
   Multi-Track nur bei **Multi-App-Cluster** — wenn die Vertikale Scheibe zwei
   Apps anfasst, je ein Ticket je App plus identischer Bundle-Hinweis im
   Top-Kommentar (Belegfall #578: PAS lebt im Eltern-Chat = andere App als
   Plan-Buddy → echter Multi-App-Cluster mit zwei Tracks; PLAN-34 lebt im
   Plan-Buddy = dieselbe App wie der View → ein Track). View / API / Skill
   innerhalb derselben App zählen NICHT als getrennte Eigentümer (PW-38
   2026-06-10, Antiberater-Befund).
5. **Asset-/DS-Status:** braucht der Buddy neue Fundament-Assets (eigenes DS,
   Custom-Illustrationen), die noch nicht gelandet sind?
6. **1-vs-N-Heuristik:** Lego-Standard-Buddy (display-only, kein eigenes DS) → ein
   Track. Eigenes DS / Custom-Assets / **APP-4-Beitrag** → Fundament-Tracks
   **vorlagern**, interface-first.
- **GATE C (Nic):** Du zeigst Nic die **reconcilte Spec + das Ticket vor dem
  Weiterreichen** und holst Freigabe — erst dann an `/arbeitstag` (Werft-Standard).

## F5 — Handoff an /arbeitstag

**Drift-Anker-Backstop-Probe vor `gh pr merge` (PW-44 V1 A, 2026-06-12
RATIFIZIERT — Codex Pass 2: fail-CLOSED-Probe, sonst fail-OPEN bei fehlender
Anker-Datei):**
```bash
WERFT_WORKTREE=${LOTSE_PROJECT_ROOT}  # oder echter Werft-Worktree-Pfad
anchor_file="$(git -C "$WERFT_WORKTREE" rev-parse --git-path werft/last_drift_anchor)"
test -s "$anchor_file" || { echo "Drift-Anker fehlt oder leer — Werft halten"; exit 1; }
anchor="$(cat "$anchor_file")"
git -C "$WERFT_WORKTREE" cat-file -e "$anchor^{commit}" || { echo "Anker-SHA ungültig — Werft halten"; exit 1; }
git -C "$WERFT_WORKTREE" fetch origin main
diff_output="$(git -C "$WERFT_WORKTREE" diff "$anchor"..origin/main -- specs/ conventions/)"
diff_status=$?
test "$diff_status" -le 1 || { echo "git diff Fehler ($diff_status) — Werft halten"; exit 1; }
```
- **`$diff_output` leer:** keine Drift, weiter zum Merge.
- **`$diff_output` nicht-leer:** **harter Halt** — geänderte Pfade + Diff-Hunk
  Nic vorlegen. Nic urteilt pro Treffer: „irrelevant für diese Werft" /
  „Spec-Update nachziehen vor Merge" / „Werft abbrechen". Bei „nachziehen":
  Spec-PR rebasen/mergen mit `origin/main`, dann Anker neu schreiben
  (selbe Befehlskette wie F3-Ende), dann erneute Probe.

Filter ist `specs/ conventions/` (ALLE Unterpfade — auch `specs/buddies/`,
nicht nur `specs/platform/`). C3 schrumpft das Drift-Fenster strukturell auf
30min–2h; diese Probe ist der Diagnose-Backstop. Race zwischen letzter Probe
und Push bleibt offen — folge-PW-Notnagel ist GitHub-Branch-Protection,
geparkt bis n=2 belegt.

- **Spec landen, DANN stempeln — harter Halt, kein Soll.** Auf Nics Gate-Verdikt (A/C)
  merget die **Werft selbst** den Spec-PR (`gh pr merge <spec-pr> --repo
  ${LOTSE_PROJECT_REPO} --merge`; `Refs #` schließt das Issue NICHT — nur die Spec
  landet; derselbe erlaubte Seiteneffekt wie der /arbeitstag-prep-NIC-BLOCK). Dann **robust
  verifizieren**, dass die Spec wirklich auf `origin/main` liegt — **nicht** per ID-`grep`
  (grün schon vor dem Merge, wenn der PR eine *bestehende* ID ändert; das Remote-Ref kann
  stale sein), sondern:
  `gh pr view <spec-pr> --json state,mergeCommit` → `git -C ${LOTSE_PROJECT_ROOT} fetch
  origin main` → `git -C ${LOTSE_PROJECT_ROOT} merge-base --is-ancestor <mergeCommit>
  origin/main`. Vor dem Merge gestempelt = `status:ready` lügt, und `/arbeitstag` lehnt
  korrekt ab (n=2: genau hier zweimal gestrauchelt).

- **F5-Reife-Watchdog vor `status:ready` (PW-43 RATIFIZIERT 2026-06-21).** Werft-F5 ruft
  `watchdog-prep` symmetrisch zu `/arbeitstag-prep`. Brief-Parameter:
  - `parent_ticket: <werft-ticket-nr>`
  - `contract_kind: subagent`
  - `werft_gate_b_done: true` (Gate B hat in F3 die Architektur-Wahl ratifiziert)
  - `gate_b_evidence: <Nic-Comment-URL oder F3-Datei:Zeile>`

  Watchdog prüft 4 Achsen (REIF/SUBSTANZ/RECONCILE/LEDGER, PW-33). Achse 1b ist Werft-
  geeicht: `werft_gate_b_done: true` unterdrückt den `neuer Buddy/Schnittstelle`-Trigger
  (Wahl wurde in Gate B getroffen). **EIGENTUM/Daten-Heimat bleibt zwingend `wahl`** —
  PW-53-A-Lego-Bruch-Schutz unabhängig von Werft-Gate.

  Verdikt-Form: Watchdog liefert `architecture_class: nachzeichnen | wahl`, `axes`-Dict,
  Verdikt-Hash. Bei `architecture_class: wahl` → Werft fällt zurück auf F2-F4 (Spec
  schärfen), kein Stempel, `in-werft`-Label bleibt.

- **Bei Watchdog-Verdikt `READY` → `werft_verdict v1`-Comment posten + Label tauschen.**
  Werft postet:
  ```
  <!-- werft_verdict v1 issue:<nr> sha:<HASH> -->
  verdict: ready
  architecture_class: nachzeichnen
  verdict_repo_sha: <main-sha>
  axes:
    werft: true                    # P2-b Provenienz, geht in compute_verdict_hash
    reif: <verdikt>
    substanz: <verdikt>
    reconcile: <verdikt>
    ledger: <verdikt>
    deliverable_kind: ui_build     # PW-83: ui_build | non_ui — Pflicht
    werft_mockup_path: specs/mockups/<slug>/<variante>.html   # Pflicht bei ui_build
  ```
  Schema identisch zu `prep_verdict v1` (gleicher Hash-Compute-Pfad via
  `status_rollback_guard.py:compute_verdict_hash`). Nur Marker-Name + `werft: true`-Achse
  unterscheiden. Hook erkennt Werft-Pfad via `in-werft`-Label + Skip-Marker.

  **PW-83 RATIFIZIERT 2026-07-03 (ENTSCHEID `20260703-232716-RATIFIZIERT-membran-
  gate-am-akt.md` → „Fix B") — `deliverable_kind` ist Pflicht-Achse am F5-Stempel.**
  Der PW-54-`werft_mockup_path`-`stat()`-Check saß bisher nur konsumenten-seitig
  (`dispatch_status_guard` beim /arbeitstag-Dispatch, konditional auf Feld-Präsenz —
  fehlte das Feld ganz, feuerte nichts). Jetzt erzwingt `status_rollback_guard.py`
  ihn **am Werft-F5-Stempel selbst** (produzenten-seitig, am Akt):
  - `deliverable_kind: ui_build` ⟹ `werft_mockup_path` ist **unbedingt** Pflicht
    (present + `specs/mockups/`-Prefix + `.html` + `stat()`-Existenz). Fehlt es →
    **Stempel-deny**. (F3-Ende persistiert das Mockup ohnehin — jetzt kommt der
    zweite Halbschritt, das maschinen-lesbare Feld, nicht mehr weg.)
  - `deliverable_kind: non_ui` ⟹ `deliverable_evidence: <Datei:Zeile/Body-Stelle,
    warum kein UI>` ist Pflicht (kein ungeprüftes Selbst-Attest). `werft_mockup_path`
    entfällt dann.
  Beide Felder liegen unter `axes:` und gehen damit in `compute_verdict_hash` — nicht
  nachträglich fälschbar.

  **Erst wenn Verdikt + Comment grün:** Label-Tausch in EINEM `gh issue edit`:
  ```
  gh issue edit <nr> -R ${LOTSE_PROJECT_REPO} \
    --remove-label status:spec --remove-label in-werft \
    --add-label status:ready
    # status_rollback_guard:skip werft-stamp verdict_hash:<HASH>
  ```
  Das ist der **einzige** manuelle Status-Übergang von Werft (WORKFLOW.md#handoff;
  RECON-3-sanktioniert).
- Die **Naht zu /arbeitstag = das fertige Issue auf `status:ready`**. `/arbeitstag` liest die
  Felder, verifiziert/entscheidet den Track-Schnitt, fährt sein eigenes **Code**-Merge-Gate +
  Deploy + Nic-Test.
- **Test-Determinismus** als Buddy-Requirement, wo Zeit im Spiel ist: injizierbares
  `now`, nie Wall-Clock tief im Code (n=1: Rollover-Test grün beim Merge, Stunden
  später rot).

---

## Grenzen (ehrlich)
- **n=2, beide display-only.** Die **APP-4-/Eltern-Chat-Schreibpfad-Strecke**
  (ein Buddy, dessen Bau den Eltern-Chat anfasst — geteilte `tasks.py`, hängt am
  offenen App-Installations-Mechanismus #296) ist **nie durch die Werft gelaufen**.
  Der erste Buddy mit Eltern-Chat-Beitrag wird F4/F5 hier am ehesten brechen —
  **nicht als gelöst behandeln.** *(Das ist NICHT der geparkte KI-Eltern-Katalog.)*

## Nach dem Lauf
- **Retro — Pflicht-Abschluss-Schritt.** Start/Stop/Continue + Flughöhe über die
  *Arbeitsweise* (was hakte/fehlte/wurde improvisiert, welches Dokument fehlte) —
  gemeinsames Format + Pfad: `~/.claude/contracts/retro.md` →
  `~/.claude/retros/JJJJ-MM-TT-werft.md`. Das härtet diesen Command.
