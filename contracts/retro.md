# Session-Retro — gemeinsamer Abschluss-Schritt

Jeder substanzielle „Worker"-Command schreibt als **letzten Schritt** eine kurze
Retro über die *Arbeitsweise* — die eine zentrale Quelle für Pfad + Format, damit
es nicht in jedem Command driftet. Commands verweisen hierauf statt zu duplizieren.

## Gemeinsamer Pfad (verbindlich)

```
~/.claude/retros/JJJJ-MM-TT-<command>.md
```

- `<command>` = der Command/die Spur (`arbeitstag`, `werft`, `arbeitstag-prep`,
  `berater-runde`, …). Mehrere Läufe am selben Tag: Suffix `-session2`, `-<thema>`.
- **Ein gemeinsames Verzeichnis** `~/.claude/retros/` — kein zweiter Ablageort,
  nicht mehr in `brainstorm/` o. ä. verstreuen.

## Format — Start / Stop / Continue + eine Flughöhe höher

Eine Flughöhe über dem Tun: **was ist hier passiert, was geht besser** — auf
*Arbeitsweise & Reibung*, **kein** Activity-Log („8 PRs gemergt" gehört nicht rein).

- **Start** — was sollten wir anfangen (neue Praxis, fehlendes Werkzeug, Lücke).
- **Stop** — was kostet/reibt und sollte weg (Anti-Pattern, Umweg, Fehlannahme).
- **Continue** — was lief gut und soll bleiben.
- **Flughöhe** — 1–3 Sätze: das Muster *hinter* den Punkten; was hat die Session
  über unsere Arbeitsweise gelehrt, das die nächste besser macht.

Knapp und ehrlich. Nenne Reibung beim Namen (Datei/Schritt), wo es hilft.

## Sub-Klassen für Beobachtungs-Tracks (optional)

Wenn die Retro einen Beobachtungs-Track aus einer aktuellen Berater-Runde mitsammeln soll, kommt das als eigene Sektion mit ratifizierter Klassen-ID — `/prozesswerkstatt` aggregiert sie quer (n=3-Schwelle).

### `PW-58-Beobachtung` (Sichtbarkeit, R2-Fall-2, PW-58 RATIFIZIERT 2026-06-17; ENTSCHEID-File `20260617-2330-RATIFIZIERT-pw58-pw52-disziplin-mechanik-katalog.md` Sektion „R2-Empfehlung → Fall 2")

Eine Sektion pro arbeitstag-Lauf, Form-Schnipsel:

```markdown
### PW-58-Beobachtung (Sichtbarkeit)
- Session: 2026-MM-DD-arbeitstag
- Letztes Retro vorhanden: ja|nein
- Nic explizit gefragt "hast du Liste X (Halt-zu-Nic / Stand für Nic) gesehen?": ja|nein
- Antwort: gesehen|übersehen|nicht-gefragt
```

Eskalations-Schwelle: n=2/3 „übersehen" innerhalb 7 Tagen. Trigger-Mechanik liegt beim **Operator** (PW-58-Beobachtung ist heute keine `/prozesswerkstatt`-Standard-Klasse — Codex-Pass-2-Befund: prozesswerkstatt nutzt generische `Vorkommen ≥3`-Probe, kein klassen-spezifisches Aggregat). Wenn n=2/3 erreicht: Operator legt manuell ein `xbuddy-prozess`-Ticket an mit Mechanik-Frage „Phase-0-Pflicht-Lese-Schritt in arbeitstag.md?" und führt `/berater-runde` aus.

## Wer schreibt eine

Jeder Command, der eine substanzielle Session fährt — als **Pflicht-Abschluss-Schritt**:
`arbeitstag`, `werft`, `arbeitstag-prep`, `berater-runde`. Kurze read-only-Einzelläufe
(`watchdog`/`watchdog-codex` als Schritt innerhalb eines Laufs) brauchen keine eigene.

## Wozu

Die Retros sind der Input für den Flow `Retro → Berater → Steuer-Dateien anpassen`
(arbeitstag.md): geballte Reibungs-Befunde härten die Commands/Conventions weiter.
Deshalb am gemeinsamen Pfad — auffindbar, vergleichbar über Sessions.
