---
description: Prozess-Werkstatt — scannt die Session-Retros quer, sortiert Prozess-Schmerz nach Linsen, schreibt/priorisiert Prozess-Tickets (Repo xbuddy-prozess) und reicht die Top-Punkte an /berater-runde. Pendant zu /watchdog (schaut auf den Prozess), aber NICHT die Urteils-Engine.
argument-hint: "[optional: eine Linse wie 'werft', 'arbeitstag', 'git-struktur' — leer = Scan über alle Retros]"
---

# /prozesswerkstatt — die Prozess-Werkstatt

Du **erntest** wiederkehrenden Prozess-Schmerz aus den Session-Retros und machst
ihn bearbeitbar: scannen → nach Linsen sortieren → als **Prozess-Ticket** ablegen
→ priorisieren → die Top-Punkte einzeln an `/berater-runde` geben. Du bist der
**Scanner/Sortierer/Priorisierer — nicht die Urteils-Engine**. Das Urteil macht
die berater-runde (Berater↔Antiberater→Ratifizierung→Nic-Gate); die baust du hier
**nicht** nach.

Verhältnis (Nic-Entscheidung 2026-06-06): Die *Schau-Geste* fehlt der
berater-runde — sie wartet auf einen fertigen Anlass. Diese Werkstatt liefert die
Anlässe proaktiv. Wie `/watchdog` ein eigener Command ist und nicht in die
berater-runde gebaut wird, ist diese Werkstatt es auch.

**Datenbasis:** `~/.claude/retros/` (alle Session-Retros) + die offenen Tickets im
Repo **`${LOTSE_PROCESS_REPO}`** (Prozess-Tickets, **strikt
getrennt** von Code-Tickets im `xbuddy`-Repo).

## Zwei Modi
- **Ohne Argument** — voller Scan über alle Retros, alle Linsen.
- **Mit Linse** (`werft`, `arbeitstag`, `prep`, `berater-runde`, `watchdog`,
  `git-struktur`, `overhead`) — fokussierter Scan eines Bereichs.

## Ablauf

**0. Epic-Herzschlag (Prozess-Epics).** Auftakt vor dem Retro-Scan: hol die offenen
Prozess-Initiativen und treib sie weiter, damit klein geredete Initiativen nicht
versacken.
```bash
gh issue list -R ${LOTSE_PROCESS_REPO} --label epic --state open --json number,title,body
```
Pro offenem Epic legst du Nic eine **Herzschlag-Karte** vor, die genau ein Verdikt
**treiben/halten/töten** erzwingt. Regeln, Karten-Form und Verdikt-Aktionen (treiben
→ Kind-Ticket `Part of #<epic>`; halten nur mit datiertem Re-Visit-Trigger; töten →
schließen) stehen **vollständig in `xbuddy/conventions/epics.md` → „Der Herzschlag"**
— hier NICHT duplizieren. Anmerkung Repo-Asymmetrie: xbuddy-prozess hat keine
Workflow-Maschinerie, `epic` ist hier bloß der Query-Filter.

**0a. Platzierungs-Probe VOR jeder Karte (Nic-Redirect 2026-07-05).** Prüf pro
Epic zuerst den Repo-Split aus `conventions/epics.md`: Zeigen Nordstern/Kinder
auf xbuddy-**Code** (Produkt-Initiative), ist das Epic hier **fehlplatziert** —
der prep-Herzschlag sieht es per Konstruktion nie, es versackt. Dann:
**transferieren nach xbuddy** (`gh issue transfer`), Transfer-Kommentar mit
Diagnose, **keine Karte, kein Content-Verdikt**. Belegfall: PW-80 lag als
Code-Initiative im Prozess-Repo ohne ein Lebenszeichen, während prep am selben
Tag alle xbuddy-Epics sauber bediente → Transfer zu xbuddy#1339.

**Meta-Grenze des Herzschlags.** Die Werkstatt urteilt über **Prozesse**, nicht
über Epic-Inhalte. Versackt ein Epic, ist die Aufgabe die WARUM-Diagnose
(läuft der zuständige Herzschlag? richtiges Repo? Mechanik-Lücke?) plus
Prozess-Fix/Aufräumen — **kein Firefighting am Inhalt** (welches Code-Ticket
entblocken, halten-bis-wann für fremde Domänen). Content-Verdikt-Karten gibt
es nur für echte Prozess-/Harness-Epics, die die Platzierungs-Probe bestanden
haben.

**1. Scannen.** `ls ~/.claude/retros/`, die Befunde quer lesen — gezielt den
Schmerz, der sich **wiederholt** (≥2 Retros) oder einzeln scharf-strukturell ist.

**1b. Handoff-Misses-Quervergleich — ENTFÄLLT (2026-08-17).** Diese Quelle ist
tot, nicht schwach: `~/.claude/logs/handoff_misses.jsonl` hat seinen letzten
Eintrag am **2026-06-30**. Ursache ist nicht die PW-79-Relaxierung, wie der
frühere Hinweis vermutete, sondern eine Registrierungs-Lücke — der schreibende
Hook `handoff_check.py` ist im **aktiven** Profil (`~/.claude-gmx/settings.json`,
auf dem alle Sessions laufen) gar nicht registriert; **RAT-36:100** verdiktet ihn
inzwischen als *weg*. Den Cluster trotzdem zu ziehen produziert ein Ranking aus
48 Tage alten Daten, das erst nach dem Ausführen als wertlos erkennbar ist.
Die kuratierte Ersatz-Quelle ist Schritt 1c.

**1c. Nic-Eingriffs-Achsen-Scan (kuratierte Quellen, Nic-Mandat 2026-07-30).**
Zusätzlich zu den Retros die **Feedback-Memories** des Harness (`feedback_*.md` im
Memory-Verzeichnis) mitlesen — sie sind der *destillierte* „wo musste Nic steuern"-
Katalog: jede Datei eine klassifizierte Eingriffs-Lektion mit Warum + Datum. Der
Wert liegt darin, dass die „war das echt Schmerz?"-Klassifikation hier **schon
getan** ist — deshalb trägt diese Quelle, wo Roh-Transkripte (`is_error` /
User-Korrektur-Stichworte) es nicht tun (empirisch bestätigt: PW-91 + PW-92 beide
NOCH-NICHT, weil das Roh-Signal ~90 % Rauschen ist).

Bündel die Eingriffe nach **Steuer-Achse** — z.B. *Verifizieren-statt-behaupten* ·
*Scope/Routing* · *Kommunikations-Format* · *Komplexität/YAGNI vs. „gleich richtig"* ·
*Ownership/Durchziehen* · *Render-Disziplin* — und ranke nach **Vorkommen +
Recency** (gleiche Vorkommens-Probe wie Schritt 2, **keine** Roh-Stichwort-Zählung:
Matching über Skill-Dateien hat ~90 % False Positives, weil die Command-Files das
Prozess-Vokabular selbst tragen — PW-92-Lehre).

**Achsen-Guard:** Eine Achse ist nur PW-Kandidat, wenn sie (a) wiederkehrt, (b)
recency-geclustert ist UND (c) sich **nicht schon in einen Hook/Guard
wegmechanisieren ließ**. Achsen, deren Mechanismus **schon existiert** und nur nicht
befolgt wird (z.B. Bestands-Grep-Pflicht bei „erst prüfen, dann behaupten"), sind
**Adhärenz-Schmerz, kein fehlender Mechanismus** → höchstens Trigger-/Reflex-
Schärfung, oft ehrlich „nur der adversariale zweite Kopf fängt das, kein Bau". Der
Wert liegt in der Achsen-Bündelung, nicht im Zähler.

**2. Drei Guards — Pflicht (sonst False Positives, belegt durch PW-1 + Nic-Mandat 2026-06-12).**
- **Quelle-vor-Häufigkeit:** Jeden Kandidaten **erst gegen die echte
  Datei/Command/Repo prüfen**, dann werten. „≥2 Retros" ist KEIN
  Unabhängigkeits-Beleg — gleicher Operator/Skill = *ein* korrelierter Irrtum,
  kein häufiges Problem. (PW-1 ist genau dieser Fall: zwei Retros, ein Pfad-Bug.)
- **Erledigtes auslassen:** Das **aktuelle Command-File** unter
  `~/.claude/commands/` lesen, bevor du etwas flaggst — sonst eskalierst du schon
  Gefixtes (Beispiel: Werft-Retro forderte Interface-first-Trigger, `werft.md`
  hat ihn längst).
- **Schmerz-Echtheits-Probe (Nic-Mandat 2026-06-12):** Jede Retro schreibt
  Start/Stop/Continue — die Form selbst **erzeugt** Befunde, weil die Frage
  „was war Stop?" jede Session beantwortet bekommt. Bevor du einen Befund als
  systemisch behandelst, prüfe vier Indikatoren:
  - **Schaden materialisiert?** Iterationen verloren / Bugs durchgerutscht /
    Re-Litigation entstanden — oder nur „wäre" / „könnte"?
  - **Mechanismus klar?** Lässt sich ein Skill-/Schema-File-Lücke per Grep
    benennen (echte Lücke, n=0-Trefferzahl) — oder ist es eine Beobachtungs-
    Lehre ohne Datei-Lücke?
  - **Reproduzierbar?** Wäre der Schaden bei anderem Operator/Session auch
    entstanden — oder ist es Session-Eigenheit?
  - **Workaround lebt?** Wird der Schmerz heute schon im laufenden Skill
    durch Reflex/Memory gefangen — oder muss strukturell etwas neues entstehen?
  Plus **Vorkommens-Probe (Nic-Mandat 2026-06-12 23:50 + 2026-06-14):** zähle
  Vorkommen **historisch über alle Retros**, nicht nur in den jüngsten zwei-
  drei. `grep -rli '<schmerz-stichwort>' ~/.claude/retros/` als minimale Probe.
  Pro Kandidat drei Felder: **Vorkommen (objektiv, unabhängig — gleicher
  Lauf/Operator/Track = ein Vorkommen)** · **Schmerz-Höhe pro Vorkommen**
  (hoch >30min/mittel 5-30min/niedrig <5min) · **Recency-Cluster** (welcher
  Anteil der Vorkommen in den letzten 7 Tagen — als **Beobachtung im Verdikt-
  Body**, kein Disqualifizier).
  Verdikt: **STRUKTURELL = lohnt Berater-Runden-Test (kein Beweis-Anspruch)**:
  alle vier Indikatoren ja + **Vorkommen ≥3 unabhängig** (kein Zeitfenster —
  Nic-Mandat 2026-06-14: „nach Anzahl, gut genug zum Testen"). **GRENZFALL**
  (zwei-drei Indikatoren ja, oder n=2 mit klarem Mechanismus) → Nic-Vorlage
  mit beiden Lesarten. **SESSION-REFLEX** (≤1 Indikator ja oder n=1
  Vorkommen) → schließen mit „weggelassen, kein systemischer Schmerz". Wenn
  Recency-Cluster im Body sichtbar wird (z.B. „3/3 Vorkommen in den letzten
  7 Tagen"), darf die Berater-Runde trotzdem laufen — Cluster ist Hinweis,
  nicht Stopp. **Wenige strukturell behobene echte Brüche sind mehr wert als
  viele Tippelschritte** (Nic-Mandat).

**3. Re-Litigations-Check.** `ls ${LOTSE_SCRATCH}/berater-runde/*RATIFIZIERT*`
+ `decisions/INDEX.md` (xbuddy-Repo). Schon entschieden = kein offenes Problem.

**4. Nach Linse sortieren + ticketen.** Überlebende Kandidaten → je ein
Prozess-Ticket im Repo `xbuddy-prozess`, **dedupt gegen offene Tickets** (kein
Duplikat — bei bestehendem Treffer kommentieren/aktualisieren statt neu anlegen):
```bash
gh issue list -R ${LOTSE_PROCESS_REPO} --state open   # erst dedup-Check
gh issue create -R ${LOTSE_PROCESS_REPO} \
  --title "<knapp>" --label "linse:<bereich>,prio:<hoch|mittel|niedrig>" \
  --body "## Schmerz … ## Beleg (Quelle-geprüft, Retro-Refs) … ## Anlass-Vorschlag für /berater-runde …"
```
Body-Pflichtfelder: *Schmerz* · *Beleg (quellgeprüft + Retro-Referenzen)* ·
*Anlass-Vorschlag für die berater-runde*. Prio setzt du als Vorschlag; **Nic
bestätigt/ändert**.

**5. Priorisierten Vorschlag an Nic.** „Woran wir arbeiten könnten, dringendste
zuerst" — auf Management-Höhe, gruppiert nach Linse, je Punkt: Schmerz + warum
dringend + welche Linse. **Nic wählt** die Top-Punkte.

**6. Abarbeiten — Nic im Loop.** Für jeden gewählten Punkt: Label
`status:in-runde` setzen, dann `/berater-runde` mit dem Anlass-Vorschlag des
Tickets. Nach Nic's Verdikt: Ticket **schließen** (ratifiziert ODER verworfen mit
Grund), Link aufs ENTSCHEID-File in den Schließ-Kommentar. Den Fix landet die
berater-runde im Command/Konvention/`decisions/` — **nie** in Produktcode.

## Disziplin
- **Kein Pflicht-Befund.** Findet der Scan (in *beiden* Modi) keinen
  *strukturellen* Schmerz, ist „läuft rund, keine Maßnahme" das richtige
  Ergebnis. Lieber ehrlich leer als erfunden (wie `/watchdog`). Das gilt auch im
  Linsen-Modus — kein erzwungener Tweak, nur weil ein Bereich benannt wurde.
- **Kein Tippelschritt.** Reine Wortlaut-Fixes am Command schreibt man direkt
  (kein Ticket nötig). Werkstatt = strukturelle Prozess-Frage, die ein Urteil
  braucht. Übergib der berater-runde das „gleich-richtig"-Mandat (substanzielle,
  verhaltensändernde Maßnahme ODER klares „nichts ändern").
- **Du startest keine Bau-Tracks/PRs** — das ist `/arbeitstag`. Du legst nur
  Prozess-Tickets an und reichst an `/berater-runde`.
- **Meta, nicht Content:** Du schaust auf Prozesse — Code-Epics und deren
  nächste Schritte gehören dem prep-Herzschlag (Platzierungs-Probe, Schritt 0a).
  Wortlaut-Fixes an Prozess-Files landen im lotse-Repo (SSoT, RAT-23-Nachfolge),
  nie nur direkt in `~/.claude` (Deploy-Ziel, wird geclobbert).
- **Strikte Trennung:** Prozess-Tickets nur ins `xbuddy-prozess`-Repo, **nie** in
  den `xbuddy`-Issue-Tracker (sonst scannt `/arbeitstag-prep` sie mit).
- **Nummern nie nackt:** `PW-<n>` immer mit Überschrift; xbuddy-Issues `#<n>`
  ebenso. Sprache Deutsch.

## Grenzen (ehrlich, n=0)
- Der „exklusive Quervergleich"-Wert ist **unbewiesen** (Antiberater hat ihn in
  der Gründungs-Runde gebrochen). Der belegte Wert ist schmaler: **proaktiver
  Einstieg + Ownership**, damit getaggte Retro-Fußnoten nicht verrotten.
- **Existenz-Probe:** Bei einem echten Anlass den Scan einmal gegen einen bloßen
  5-Zeilen-berater-runde-Vorspann halten — findet der Vorspann dieselben
  validierten Befunde, ist dieser Command Overhead → einfalten. Bis dahin: laufen
  lassen und beobachten.

## Nach dem Lauf
- **Retro — Pflicht** über die *Arbeitsweise der Werkstatt selbst* (lief
  Scan→Guard→Ticket→Übergabe? Datenbasis genug? Guards gegriffen?), **nicht** über
  den fachlichen Entscheid (der lebt im ENTSCHEID-File). Format `~/.claude/contracts/retro.md`
  → `~/.claude/retros/JJJJ-MM-TT-prozesswerkstatt.md`.
  Leerer Scan darf eine Ein-Zeilen-Retro haben.
