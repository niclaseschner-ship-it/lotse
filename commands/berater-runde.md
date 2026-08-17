---
description: Eine Architektur-Runde — Berater schlägt vor, Antiberater (Codex) widerlegt, du baust das entscheidungsreife Paket für Nic. Für Architektur-/Design-Fragen und zum Formalisieren in specs/conventions/constitution.
argument-hint: "[die Architektur-Frage ODER 'diagnose <komponente>' ODER 'formalisiere <befund>']"
---

# /berater-runde — Architektur-Runde mit Gegenpol

Du (Orchestrator) führst **eine Runde** zwischen Berater und Antiberater und
bringst Nic ein **entscheidungsreifes Paket**. Du schreibst keinen Produktivcode
und landest nichts ohne Nic-Freigabe.

Grundsatz: Robustheit kommt nicht daher, den Berater klüger zu machen — sondern
den Rat **prüfbar** zu machen (anderer Kopf + billiges Experiment) und ihn dann
**scharf zu landen**.

## Das Gesetz: drei Landungen, keine vierte

Verwässerung entsteht, wenn Bremse und Vorschlag denselben Hebel teilen und einen
Mittelwert ausspucken. Jede Runde landet auf **genau einem** von drei Ausgängen:

- **MACH ES** — eine Richtung + Kill-Kriterium.
- **NOCH NICHT** — die Null-Option + Auslöser, der das Thema wieder aufmacht.
- **ECHTE GABEL** — zwei legitime Optionen, **mit Lean** (empfohlener Zweig +
  Konfidenz + Kill-Kriterium) + entscheidendes Experiment.

**Verboten:** der abgeschwächte Mittelweg, der nur entstand, damit beide einig
sind. Wird Einigkeit nur erreicht, weil der Anspruch vage/untestbar wurde, ist das
**keine** Konvergenz — dann NOCH NICHT oder echte GABEL.

Die drei Landungen gelten für `mode: propose` und `mode: formalize` — also für
jeden Lauf, der eine **Lösungsform** vorschlägt. `mode: read` (R1-Bestandskarte)
ist eine **Vorstufe** mit eigenem Verdikt-Vokabular (READY-FOR-PROPOSE /
NOT-READY / ECHTE-GABEL-IM-ANLASS) und beantwortet allein die Frage „darf R2
starten?". Ein READY-Verdikt ist **keine vierte Landung** — es ist die Erlaubnis,
**eine** der drei Landungen anzusteuern (PW-56 RATIFIZIERT 2026-06-21).

Zwei Werkzeuge entscheiden *für* dich, damit nicht jede Gabel bei Nic landet:

- **Reversibilität sortiert.** Zwei-Wege-Tür (reversibel, klein, in unter ~1 Tag
  rückbaubar) → die kühnere Form ist Default, das Tun ist das Experiment, MACH ES
  + Kill-Kriterium. Ein-Wege-Tür (Datenmodell, Constitution, Familie-1-Einbacken,
  Kind-Daten, öffentliche Schnittstelle) → volle Schärfe, Experiment vor Commit.
- **Constitution-Rang bricht Gleichstände.** Ist eine Gabel ein Trade-off
  zwischen zwei Qualitätsattributen, **gewinnt der höhere Rang aus
  `specs/constitution.md` — ohne Eskalation.** Nur als GABEL an Nic geben, wenn
  die Ränge *benachbart* sind oder die Reihenfolge selbst in Frage steht.

## Ablauf

**0. Anlass + Reversibilität klären.** Architektur-/Design-Frage, `diagnose
<komponente>`, oder `formalisiere <befund>`. Zwei Pflicht-Checks **vor** dem
R1-Spawn:

- **Anlass-Hygiene (PW-35 V1).** Enthält der Anlass eine **Lösungsform** ODER
  eine **Domänen-Annahme**, die Nic nicht explizit gesetzt hat → stopp (kein
  „mitlaufen lassen"): poste Nic-Wort wörtlich + deine Übersetzung + die 2
  konkurrierenden Formen (Lese- vs. Lösungs-Frage; Code- vs. Prozess-Domäne).
  Nic bestätigt eine, dann R1.
- **Reversibilitäts-Einstufung.** Stuf die Entscheidung als Zwei-Wege-Tür oder
  Ein-Wege-Tür ein und übergib das an den Berater. Im Zweifel: Ein-Wege-Tür. Bei
  klarer Zwei-Wege-Tür mit kleinem Blast Radius darfst du die Runde **leicht**
  fahren (R1 + kurzer Codex-Sanity, kein Voll-Pingpong) — das ist die Bremse, die
  *nicht* anzieht, wo sie nicht muss.
- **Re-Litigations-Check (PW-60, geschärft 2026-06-21).** Vier Quellen vor dem
  R1-Spawn greppen, je nach Anlass-Stichworten:
  - `gh issue list -R ${LOTSE_PROCESS_REPO} --state open --search "<stichwort>"`
    — offene Prozess-Tickets (z. B. zu Werft/prep/arbeitstag/overhead/berater-runde).
  - `ls ${LOTSE_SCRATCH}/berater-runde/*RATIFIZIERT*` + `grep -l "<stichwort>"`
    — schon ratifizierte Anlässe.
  - `ls ${LOTSE_SCRATCH}/berater-runde/*ENTSCHEID-OFFEN*` + `grep -l "<stichwort>"`
    — explizit als NOCH-NICHT / OPEN vertagte Anlässe (PW-49-Lehre 2026-06-21:
    Re-Litigation einer OPEN-Setzung ohne neuen n-Beleg ist Verschwendung).
  - `cat ${LOTSE_PROJECT_ROOT}/decisions/INDEX.md` — durables Ledger.

  Wenn ein **offener PW** den Anlass berührt → entweder **konsolidieren** (mehrere
  PW in einer Runde, dann pro PW Ergebnis-Kommentar) oder explizit benennen,
  warum getrennt. Wenn ein **ratifizierter Entscheid** den Anlass berührt → keine
  Re-Litigation, das geht zurück zur Werkstatt/Watchdog. Wenn ein
  **ENTSCHEID-OFFEN** mit Reopen-Trigger den Anlass berührt → vor R1-Spawn
  prüfen, ob der Trigger erfüllt ist (z. B. neuer n-Beleg, neuer
  Bestandsbefund). Wenn nicht: keine neue Runde — Werkstatts-Eintrag „wartet
  auf Reopen-Trigger".

**1. Berater-Lauf (R1, `mode: read`).** `Agent`-Tool, `subagent_type: "berater"`,
Subagent-Vertrag-Header anhängen (→ Anhang „Mechanik"). Übergib Anlass +
Reversibilitäts-Einstufung + Kontext. Ergebnis: **Bestandskarte** (Anker mit
`Datei:Zeile` zu Spec/Code/Convention, die der Anlass berührt) + **Reife-Verdikt**
(PW-56 RATIFIZIERT 2026-06-21) in einem von drei Werten:
- **READY-FOR-PROPOSE** — Anlass scharf, Anker tragen, R2 darf Vorschlag bauen.
- **NOT-READY** — Anlass unterspezifiziert ODER Anker widersprechen sich; nenne,
  was fehlt (Nic-Klärung, Bestands-Grep, fehlende RAT-Setzung).
- **ECHTE-GABEL-IM-ANLASS** — der Anlass enthält zwei legitime Lese-Formen, Nic
  muss vor R2 eine wählen.

R1 liefert **keine** Lösungs-Vorschläge, kein Kill-Kriterium, kein Experiment —
das ist R2-Sache (PW-29). **Bestands-Grep-Pflicht** vor jeder „einziger/erster
Konsument" / „trägt schon" / „schon erledigt"-Aussage (→ Anhang).

**2. Antiberater-Lauf (Codex primär).** Schreib den Vorschlag nach der
Vorschlag-Datei (→ Anhang), häng den Schutz-Rahmen-Header an (→ unten), dann starte
`antiberater-codex.sh` (→ Anhang). Lies die Reportdatei. Der Antiberater liefert
pro Punkt ein Verdikt mit Schweregrad — **BRICHT (falsifiziert)** vs. **RISKANT
(gewarnt)** — plus Minimal-Variante als Material (nicht als Urteil).

*Schutz-Rahmen-Header im Vorschlag-File* (schlanke PW-46-Nachfolge — die alte
„Min-Variante MUSS gewinnen"-Hartregel ist abgeschafft, sie hat verwässert; Details
im Anhang):

```
## Schutz-Rahmen (für Antiberater)
- **Von Nic gesetzte Invarianten:** <was diese Runde NICHT in Frage stellt —
  Anlass, Anker-Quellen, vorhandene RAT-Festlegungen>. Brüche daran melden, aber
  als „außerhalb Auftrag" kennzeichnen.
- **Stoßrichtung:** <der Erstwurf in einem Satz>.
- **Patch oder Gabel:** Pro Bruch entweder ein Patch ODER eine saubere Gabel
  (zwei legitime Optionen + entscheidendes Experiment). Brüche ohne
  verantwortbaren Patch werden zur Gabel, nicht weggepatcht.
- **Ausnahme Quellenwiderspruch:** Findet der Antiberater einen Beleg, der die
  Stoßrichtung falsifiziert, darf er sie verwerfen — der Rahmen schützt nicht vor
  Empirie.
```

**3. Runden-Deckel + R2 hält die Form.** Höchstens **zwei** Runden. Runde 2 =
**frischer Spawn**, kein Resume (→ Anhang), mit R1-Vorschlag + Antiberater-Report
inline.

> **Default in R2 ist: Form halten.** Der R2-Berater gibt die R1-Form nur auf,
> wenn der Antiberater **BRICHT (falsifiziert)** hat — *nicht* bei bloßem
> RISKANT. RISKANT wird zum Kill-Kriterium, das mitläuft, nicht zur Formänderung.
> Gibt der R2-Berater bei bloßem RISKANT nach, ist das Verwässerung → behandle es
> als **Divergenz**, nicht als Konvergenz. Nachgeben ist begründungspflichtig:
> nenne den BRICHT-Beleg.

Das dreht die alte Asymmetrie um, die R2 auf Kapitulation polte.

**4. Landen — das gelehnte Paket für Nic.** Erst die Tiebreaker anwenden
(Reversibilität sortiert, Constitution-Rang bricht Gleichstände), *dann* eines
der drei Templates wählen. Alles auf Management-Höhe.

**MACH ES** (ein testbarer Anspruch hat überlebt, oder reversibler Default):
```
## Entscheidung — MACH ES
<eine Richtung, in Nics Worten>
## Reversibilität
<Zwei-Wege-Tür | Ein-Wege-Tür — Halbsatz Begründung>
## Was sich ändert / Trade-off
## Kill-Kriterium  (wann wir zurückrudern)
## Experiment  (nur Ein-Wege-Tür: belegt/kippt es vor Commit)
## Wo es landet  (Genre + ID-Vorschlag)
```

**NOCH NICHT** (kein Schmerz drückt jetzt — vollwertige scharfe Landung):
```
## Entscheidung — NOCH NICHT
<warum jetzt kein Schmerz drückt>
## Auslöser  (was das Thema wieder aufmacht)
## Was wir uns sparen
```

**ECHTE GABEL — mit Lean** (Constitution-Rang bricht den Gleichstand nicht):
```
## Die Gabel — mit Lean
**Empfohlener Zweig:** <A | B> — Konfidenz <hoch | mittel | niedrig>
**Warum dieser Lean:** <Reversibilität + Constitution-Rang + Kosten-Asymmetrie>
**Stärkster Fall für den anderen Zweig:** <der ehrliche Gegenfall — nicht verstecken>
**Kill-Kriterium / entscheidendes Experiment:** <was die Gabel in der Realität auflöst>
## Wo es landet  (Genre + ID-Vorschlag)
```

Die Gabel kriegt **immer einen Lean** — eine nackte symmetrische Gabel maximiert
Nics Entscheidungslast und ist selbst eine Form von Nicht-Landen. Der Dissens
bleibt sichtbar (der Gegenfall), wird aber nicht zum Mittelwert.

**Prozess-/Skill-Schärfung** (Wortlaut-/Schema-Patch an Skill-/Process-File) — pro
Punkt sechs Felder, kein Vorgeplänkel:
```
## PW-XX — <Kurzname>
**Problem:** · **Idee:** · **Bedenken aus der Runde:** ·
**Verbesserte Idee:** · **Risiko:** · **Empfehlung:** <ja | nein | Variante>
```

**5. Nach Nic-Freigabe formalisieren (nur dann).** Der Berater schreibt den
Entwurf ins Genre (`specs/` / `conventions/` / `constitution.md`). Vorbedingung,
Anker-Verweis-Pflicht und Antiberater-Pass-2 → Anhang („Formalisierung").

**6. Spur festschreiben (Pflicht — jede Runde).** Eine Runde endet **nie** im
Chat allein. ENTSCHEID-File + Ticket-Verankerung + RATIFIZIERT-Grep → Anhang
(„Verankern"). Erfährt die nächste Session den Befund nur, weil Nic ihn
weitererzählt, war die Runde nicht fertig.

## Disziplin

- **Tiebreaker bei Uneinigkeit ist Nic** — beide Positionen vor ihm, kein
  „Berater trumpft Antiberater". Aber das gelehnte Paket *nimmt ihm Last ab*: du
  sortierst per Reversibilität und brichst Gleichstände per Constitution-Rang,
  bevor du eskalierst. Lean ≠ Autoritäts-Theater; Lean = du hast deine Arbeit
  gemacht.
- **Divergenz ist wertvoll** — versteck sie nicht, aber lehn sie.
- **Constitution bleibt bottom-up:** nur formalisieren, wo sich ein Muster über
  mehrere Befunde wiederholt hat. Kein Prinzip auf Vorrat.
- **Nummern nie nackt** (CLAUDE.md §7). Sprache Deutsch.
- Du startest **keine** Tracks/Tickets/PRs — Ausnahme: den fertigen Entscheid auf
  ein bereits angeschautes Ticket verankern (Verankern ≠ Starten).

## Retro — Pflicht-Abschluss

Nach dem Verankern eine kurze Start/Stop/Continue-Retro über die *Arbeitsweise*
(nicht den fachlichen Entscheid): Lief der Berater↔Antiberater-Takt? War der
Anlass scharf? War die Reversibilitäts-Einstufung richtig? Hat ein RISKANT sich
fälschlich als BRICHT ausgegeben (oder umgekehrt)? Format + Pfad:
`~/.claude/contracts/retro.md` → `~/.claude/retros/JJJJ-MM-TT-berater-runde.md`.

---

# Mechanik (Anhang) — Invarianten, die Hooks/Skripte parsen

Dieser Teil ist **Vertrag mit Code**, nicht Beratungsinhalt. Wortlaut/Format hier
**nicht ändern**, ohne den zugehörigen Hook/Skript mitzuziehen.

**Subagent-Vertrag-Header** (RAT-15 + PW-23 + PW-31). Jeder Berater-Prompt (R1 wie
R2) beginnt mit **drei** Pflicht-Zeilen:

```
<!-- dispatch_status_guard:skip -->
contract_kind: subagent_no_ticket
mode: read | propose | formalize
```

- *Zeile 1 — Skip-Marker als erste nicht-leere Zeile* (PW-23): Der Hook prüft
  `prompt.lstrip().startswith(...)`. Marker mitten im Text reicht NICHT. Grund:
  berater-runde-Spawns haben kein `parent_ticket`.
- *Zeile 2 — `contract_kind: subagent_no_ticket`* (PW-31): macht den Skip-Pfad zu
  einem eigenen Vertrag. Der Hook lehnt `contract_kind: subagent` im Skip-Pfad ab.
- *Zeile 3 — `mode:`* (PW-31): `read` = reines Bestand-Lesen ohne Lösungs-
  Vorschläge (R1-Disziplin, PW-29). `propose` = Lösungs-Vorschlag (R2). `formalize`
  = Spec-/Convention-Entwurf (Schritt 5 nach Nic-Freigabe). `build` ist hier
  **verboten** (erfordert `parent_ticket`, gehört in `/arbeitstag`).
- Es gibt **keine** maschinelle Beleg-Prüfung mehr (der Presence-Check-Hook ist
  mit RAT-36:100 gestorben): die Prüfung — auch die triviale „ist überhaupt ein
  Beleg da?" — liegt vollständig bei
  Berater + Antiberater.

**Bestands-Grep-Pflicht** (CLAUDE.md §7). Jede „erster/einziger Konsument" /
„trägt schon" / „schon erledigt"-Aussage, aus der eine Lokalitäts-,
Generalisierungs- oder Skip-Entscheidung folgt, braucht **vorher** einen Grep aufs
echte Artefakt (`grep -rn <feld> <konsumenten-dir>` / `git grep`), nicht eine
Ableitung aus der Spec. Der Grep belegt nur die **Faktenzahl** — die
Generalisierung bleibt am Sorten-/Drift-Test, nicht an der bloßen Konsumentenzahl.
(n=1: R1 behauptete „einziger Konsument", obwohl `panel_anlegen` längst `icons[]`
komponiert.)

**Antiberater-Aufruf.** Vorschlag-Datei:
`${LOTSE_SCRATCH}/berater-runde/<ts>-vorschlag-<slug>.md`. Dann:

```bash
~/bin/antiberater-codex.sh <vorschlag-datei> <slug>
```

Reportpfad steht in der letzten stdout-Zeile (per `Read` lesen).
**Fallback** wenn der Wrapper fehlschlägt (Codex nicht verfügbar):
`antiberater` als Opus-Subagent mit Vorschlag inline — und das Ergebnis
**ausdrücklich als Opus-Fallback kennzeichnen** (schwächer, Echo-Risiko), damit Nic
es einordnet. (Codex ist ein Shell-Skript, kein Agent-Dispatch — keine Marker
nötig.)

**R2 = frischer Spawn, kein Resume.** `SendMessage`/Agent-Continuation existiert in
diesem Harness nicht — die R1-agentId ist nicht weiterführbar. Für R2 einen
**neuen** `berater` starten mit **vollständigem R1-Vorschlag +
Antiberater-Report inline** (Memory `feedback_sendmessage_nicht_verfuegbar`).

**Abgeschaffte Hartregel (PW-46-Korrektur).** Die alte Klausel „bei `fängt ab: ja`
MUSS die Min-Variante die Empfehlung sein" ist **entfernt** — sie hat den
minimal-invasiven Weg per Dekret zum Sieger gemacht und so systematisch
verwässert. Die Min-Variante ist jetzt *Material* (Antiberater liefert sie); ob sie
empfohlen wird, entscheidet das Reversibilitäts-Gate (Schritt 0/4) und Nic. (Die
alte Klausel hatte ohnehin Sunset + `n=1`.)

**Formalisierung** (Schritt 5 im Detail).
- *Vorbedingung (PW-48):* Das ENTSCHEID-File ist **bereits angelegt** (zwischen
  Nic-Verdikt und Formalisierung), damit es als adressierbare Paket-Quelle
  vorliegt.
- *Anker-Verweis-Pflicht:* Jede **neu/inhaltlich geänderte** normative Klausel im
  Entwurf trägt einen Inline-Verweis aufs ratifizierte Paket — Granularität
  `ENTSCHEID-File Paket-Sektion "<Überschrift>" → <Stichwort>`, **nicht** pauschal
  „siehe Paket". Unveränderte Klauseln bleiben unangetastet. Klauseln ohne
  herleitbare Paket-Stelle gehören in `## Offene Fragen`, bis Nic sie nachzieht.
- *Antiberater-Pass-2:* Ein Pass auf den **geschriebenen Text** (sagt er, was
  vereinbart wurde? falsifizierbar? übergeneralisiert? jede neue Klausel mit
  Paket-Anker?). Bei Skill-/Schema-Edit-Wellen läuft Pass-2 auf den **tatsächlich
  geschriebenen Edits**, nicht nur dem Vorschlag — Pass-1 ist Diagnose, Pass-2 ist
  QS und findet erfahrungsgemäß mehr. Dann Nic-Gate vor dem Landen.

**Verankern** (Schritt 6 im Detail).
- *ENTSCHEID-File* als durables Archiv:
  `${LOTSE_SCRATCH}/berater-runde/<ts>-ENTSCHEID-<slug>.md` mit Kopf-Feldern
  `Anlass:` · `Frage:` · `Status:` (`OFFEN` bis Nic entscheidet) · `Ticket:` ·
  Links auf Vorschlag + Antiberater-Report. Inhalt = das Schritt-4-Paket
  (Landung), nicht das Rohmaterial. **Form der vier Glieder** (Problem →
  betrachtete Alternativen → wie entschieden/gemessen → Ergebnis):
  `contracts/entscheidung.md` — dort nachlesen, hier nicht duplizieren.
- *Ticket-Verankerung:* Nach Nics Verdikt einen kurzen Entscheid-Kommentar auf
  jedes angeschaute/benannte xbuddy-Ticket (Entscheidung + „Wo es landet" + Link
  zum Entscheid-File). Verankern ≠ neuer Track.
- *Verdikt nachtragen:* `Status:` → `RATIFIZIERT` / `VERWORFEN (Grund)` /
  `DIVERGENZ (offene Gabel)`. Bei Ratifizierung muss **`RATIFIZIERT` im
  Dateinamen** stehen (`mv` auf `<ts>-RATIFIZIERT-<slug>.md`), damit der Ledger-/
  Phase-0-Grep (`brainstorm/berater-runde/*RATIFIZIERT*`) ihn findet.
