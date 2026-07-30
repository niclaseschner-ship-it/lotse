---
description: Mehrdimensionales Produkt-Verkaufsreife-Audit des xbuddy-Repos — parallele read-Subagenten, konsolidiertes Urteil, optionaler Epic-Prep mit Pflicht-Re-Litigations-Check. Beantwortet „verkaufswürdig oder KI-zusammengedengelt?".
---

# /audit — Produkt-Verkaufsreife-Audit

Du prüfst das xbuddy-Repo (`${LOTSE_PROJECT_ROOT}`) über mehrere Qualitäts-
Dimensionen parallel und lieferst ein **konsolidiertes Urteil mit Handlungs-
leitfaden**. Leitfrage: *„Ist das ein verkaufswürdiges Produkt oder nur mit KI
zusammengedengeltes?"* — mit der harten Trennung **„ok fürs eigene Zuhause" vs.
„Blocker für Verkauf an fremde Familien"**.

Read-only in den Analyse-Phasen. Nichts anlegen/labeln ohne Nic-Freigabe.

## Phase 0 — Orientierung (selbst, kurz)
Repo-Größe, Service-Verzeichnisse, Test-Zahl, CI-Workflows, `git log`-Kopf. Nur
so viel, dass du die Subagenten präzise briefen kannst. `.claude/` ignorieren.

## Phase 1 — Parallele Dimensions-Prüfungen (read-Subagenten, im Hintergrund)
Sechs Standard-Dimensionen, je ein `Agent` (`run_in_background: true`), damit sie
nebenläufig laufen. Passe Zahl/Zuschnitt an den Anlass an:

1. **Architektur & Code-Qualität** — Service-Schnitt, Duplikation, God-Module, Fehlerbehandlung, Typing, Spec↔Code-Deckung.
2. **Tests & CI** — Test-Substanz vs. Happy-Path, Abdeckungslöcher, **echtes Merge-Gate** (läuft pytest/ruff in CI oder nur Prozess-Guards?), main grün?
3. **Security & Secrets** — Auth-Oberfläche, Funnel-Exposition, initData/HMAC, Prompt-Injection-Fläche, Secrets im Working-Tree, systemd-Härtung.
4. **Betrieb & Deploy** — reproduzierbarer zweiter Pi (Dependency-Manifest, Bootstrap), Persistenz-Robustheit, Monitoring/Health, Release-/Update-Pfad.
5. **Datenmodell & Privacy** — kanonisches Modell, echte Familien-/Kinderdaten im Repo/Historie, LLM-Datenabfluss (Kinder-Audio!), Lösch-/Export-Pfad (DSGVO).
6. **Doku & Onboarding** — Bus-Faktor, Getting-Started für Dritte, specs/conventions-Substanz, LICENSE.

**Jeder Subagent-Prompt beginnt mit drei Pflichtzeilen** (sonst PW-31/RAT-15-
Reject beim Dispatch):
```
<!-- dispatch_status_guard:skip -->
contract_kind: subagent_no_ticket
mode: read
```
Jeder Prompt verlangt: Befund **mit `Datei:Zeile`-Beleg** + Schweregrad
(kritisch/hoch/mittel/niedrig/positiv) + die „Zuhause vs. Verkauf"-Trennung + am
Ende (a) 3-Satz-Gesamturteil, (b) 3 wichtigste Maßnahmen. Deutsch.

## Phase 2 — Konsolidierung (selbst)
Warte alle Befunde ab. Dann EIN Gesamturteil: ist es Substanz oder Gedengel,
wo genau liegt die Lücke zu „verkaufbar". Dimensions-Tabelle (Urteil je Achse +
Kernbefund). **Führe den gefährlichsten Einzelbefund oben** (in dieser Übung:
„main ist seit Wochen rot, kein Test-Gate"). Handlungsleitfaden in Phasen
(Sofort / betreibbar für Fremde / verkaufbar), Aufwand-vs-Wirkung sortiert.

## Phase 3 — Epic-Prep (optional, auf Nic-Wunsch)
Befunde zu Epic-Kandidaten bündeln und Nic als Wahl-Karten vorlegen:
- **HTML-Karten-Loop** über `${LOTSE_PROJECT_ROOT}/tools/prep-karten/` (Wahl-Karten in
  `cards.json` schreiben, `python3 server.py` bindet auf Tailnet-IP:8765,
  `fuser -k 8765/tcp` zum Beenden; Runde-Karten vorher sichern).
  **Fallstrick:** kein `*/` und keine geraden ASCII-`"` **im Kartentext** —
  `cards.json` wird auch in einen JS-Kommentar injiziert; `*/` schließt ihn
  vorzeitig → leere Seite. Immer `node --check` + DOM-Stub gegen den gerenderten
  `<script>` fahren, bevor die Seite an Nic geht.
- Verdikt-Vokabular pro Karte: treiben / halten-mit-Trigger / verwerfen.

## Phase 4 — ⚠️ Pflicht-Re-Litigations-Check VOR dem Anlegen
**Die teuerste Lehre der ersten Übung:** ein spürbarer Teil der Audit-Befunde
trifft auf bereits getroffene Entscheidungen. Vor JEDEM Epic/Ticket, das aus
einem Befund entstehen soll, die vier Quellen greppen:
```
cat ${LOTSE_PROJECT_ROOT}/decisions/INDEX.md | grep -i <stichwort>
ls ~/brainstorm/berater-runde/*RATIFIZIERT* | xargs grep -il <stichwort>
gh issue list -R ${LOTSE_PROCESS_REPO} --state open --search <stichwort>
grep -rn <stichwort> ${LOTSE_PROJECT_ROOT}/specs/platform/
```
Berührt ein **ratifizierter Entscheid** den Befund → **kein neues Ticket/keine
Runde**, sondern nur Trigger-Feststellung / Ledger-Lücke benennen. (Beispiele
erste Übung: Herzschlag-Kadenz war in xbuddy-prozess#81 bewusst vertagt; die
gesamte Auth-Strategie lag in RAT-18/auth.md — beide hätten sonst re-litigiert.)

## Phase 5 — Anlegen (nur nach Nic-Freigabe pro Runde)
- **Audit-Dach-Epic** (`gh issue create --label epic`, KEIN `status:*`) als
  Referenz-Anker: Gesamturteil, Verdikt-Tabelle, empfohlene Reihenfolge,
  **liegengebliebene/entschiedene Themen** (damit später referenzierbar).
- Kinder-Tickets `Part of #<dach>` mit type/area/priority-Labels.
- **WIP-Disziplin:** höchstens 2–3 Epics gleichzeitig aktiv „treiben" (realer
  Durchsatz-Engpass ist Nics Entscheidungs-Bandbreite, nicht die Bau-Kapazität);
  Rest „halten mit datiertem Re-Visit-Trigger". Keine verschachtelten Epics.
- Reife-Übergabe an /arbeitstag nur, was nach PREP-1 wirklich reif ist (Spec auf
  main ODER reines Chore ohne Spec-Anker). Nic bleibt Stempel-Setzer.

## Optional — Pipeline-Belastungs-Check
Wenn viele Epics entstehen: prüfen, ob die Umsetzungs-Pipeline sie trägt und bis
LIVE bringt (nicht nur bis „gemergt"). Drei Achsen: Epic-Herzschlag (versacken?),
Durchsatz arbeitstag/prep (Nic-Nadelöhr), Endstrecke CI→Merge→Deploy
(Runner-SPOF, „gemergt ≠ live", manueller Deploy). Der wahre letzte Meter ist
Deploy, nicht Merge.

## Abschluss
Alles Wichtige in die finale Nachricht (Outcome zuerst). Bei Änderungen am Ledger
(Epics/Tickets) die Nummern nennen. Sprache Deutsch, Nummern nie nackt.
