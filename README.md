# Lotse

### ▶︎ Live walkthrough — **[lotse-demo.pages.dev](https://lotse-demo.pages.dev/)**  ·  [🇬🇧 English](https://lotse-demo.pages.dev/en.html) / [🇩🇪 Deutsch](https://lotse-demo.pages.dev/)

A 6-slide tour of what Lotse is and how it works (the three-swans model included).

---

**Disciplined orchestration of AI coding agents.** A file-based framework that
guides AI coding agents through a disciplined pipeline — from idea to merged
change — with adversarial review, a ratification ledger, and a retro learning
loop. Tool-agnostic in spirit; the reference implementation runs on Claude Code.

> A *Lotse* (German for *maritime pilot*) guides a ship through narrow waters
> without taking the helm. The mental model is systemic — inspired by *»The Third
> Swan«* (Bernd Schmid, isb Wiesloch): the same work happens at three altitudes at
> once. The image inspired us — with thanks to Bernd Schmid and the isb; mapping it
> onto this framework is our own reading.

### The three swans — the mental model

```
        one piece of work, three altitudes at once:

  3rd swan   →   /prozesswerkstatt · /berater-runde
  watches the watcher            change the working system itself

  2nd swan   →   /watchdog · hooks · contracts
  watches the doer               drift & quality, live, while building

  1st swan   →   /werft · /arbeitstag-prep · /arbeitstag
  flies, in the moment           the work itself, idea → done

  ────────── the ground it all flies over: your product ──────────
```

### The pipeline (commands)

| Command | What it does |
|---------|--------------|
| `/werft` | Carry an idea from framing to a hand-off-ready ticket (human gates: Spec · Design · Package). |
| `/arbeitstag-prep` | Ripen `spec` tickets to `ready` — the human is the only one who stamps. |
| `/arbeitstag` | Implement several tickets in parallel, conflict-free (git worktrees). |
| `/berater-runde` | One architecture round: an advisor proposes, an *adversary* (different head/model) tries to break it, landing on exactly one of three outcomes. |
| `/watchdog` | Architecture review of the diff before merge (optional cross-engine second opinion). |
| `/prozesswerkstatt` | Harvest session retros into process tickets → the sharpest ones back into `/berater-runde`. |

### Quickstart

**Adopting Lotse in a fresh project? → [`SETUP.md`](SETUP.md)** walks you from zero
to a working pipeline (env vars, labels, workflows, scaffold — templates included).

```bash
# Deploy the glue (agents/ commands/ contracts/ hooks/) to the harness runtime:
./deploy.sh                        # default source: origin/main
./deploy.sh --dry-run              # show what would change
./deploy.sh --verify-only          # drift check: runtime vs. versioned source
```

Lotse is a *layer of discipline* on an AI coding agent (reference harness:
Claude Code) pointed at your project — not a standalone app. It assumes your
project brings a GitHub repo, a handful of labels, two CI workflows and a
`specs/`·`decisions/`·`conventions/` scaffold; [`SETUP.md`](SETUP.md) ships
templates for all of them.

### Configuration (env vars, optional)

| Variable | Meaning | Default |
|----------|---------|---------|
| `LOTSE_PROJECT_ROOT` | Root of the project Lotse orchestrates | current dir |
| `LOTSE_PROJECT_REPO` | GitHub slug of that project (`owner/repo`) for `gh` calls | — |
| `LOTSE_PROCESS_REPO` | GitHub slug of the process/ticket repo | — |
| `CLAUDE_HOME` | Harness runtime / deploy target | `~/.claude` |
| `LOTSE_SCRATCH` | Scratch dir for drafts & round notes | `~/brainstorm` |

For anything beyond `--dry-run`, `LOTSE_PROJECT_ROOT` and `LOTSE_PROJECT_REPO`
are effectively **required** — the commands' `git`/`gh` calls have no target
without them. See [`SETUP.md`](SETUP.md).

> **Note on language:** the framework's *content* — commands, agents, contracts —
> is written in **German** (established technical terms stay English). The German
> reference below is the canonical text.

---

# Lotse — disziplinierte Orchestrierung von KI-Coding-Agenten

> **Lotse** ist ein dateibasiertes **Framework**, das KI-Coding-Agenten durch eine
> disziplinierte Strecke von der Idee bis zur gemergten Änderung führt — mit
> gegnerischer Review, einem Ratifizierungs-Ledger und einem Retro-Lernkreis.
> Werkzeug-agnostisch im Geist; die Referenz-Implementierung läuft auf Claude Code.
>
> Der Name ist Programm: Ein Lotse führt das Schiff durch enges Fahrwasser, ohne
> selbst das Steuer zu übernehmen. Das mentale Modell dahinter ist systemisch —
> inspiriert von »Der dritte Schwan« (Bernd Schmid, isb Wiesloch): dieselbe Arbeit
> läuft auf drei Flughöhen zugleich (Tun · Selbstbeobachtung · Beobachtung der
> Beobachtung). Das Bild hat uns inspiriert — mit Dank an Bernd Schmid und das isb;
> die Übertragung auf dieses Framework ist unsere eigene Lesart.

## Das Problem

KI-Agenten driften: sie übergeneralisieren auf Vorrat, re-litigieren längst
entschiedene Fragen, überspringen Review, und treffen Architektur-Entscheidungen
aus dem Bauch. Lotse legt Struktur drüber:

- Jede Änderung läuft **Idee → Spec → Bau → Review** — kein Code ohne Requirement.
- Jede Architektur-Entscheidung wird **gegnerisch geprüft und genau einmal
  ratifiziert** (kein Re-Litigieren).
- Prozess-Schmerz wird systematisch in Verbesserungen geerntet.

## Die Strecke (Commands)

| Command | Was es tut |
|---------|-----------|
| `/werft` | Eine Produkt-/Feature-Idee von der Rahmung bis zum übergabereifen Ticket führen (Mensch-Gates A Spec · B Design · C Paket). |
| `/arbeitstag-prep` | `spec`-Tickets bis `ready` reifen — der Mensch ist der einzige Stempel-Setzer. |
| `/arbeitstag` | Mehrere Tickets **parallel + konfliktfrei** umsetzen (git-Worktrees). |
| `/berater-runde` | **Eine** Architektur-Runde: Berater schlägt vor, Antiberater (anderer Kopf/Modell) widerlegt, Landung auf **genau einem** von drei Ausgängen — MACH ES / NOCH NICHT / ECHTE GABEL. |
| `/watchdog` (+ `/watchdog-codex`) | Architektur-Review des Diffs vor dem Merge (optional Cross-Engine-Vergleich). |
| `/prozesswerkstatt` | Session-Retros quer ernten → Prozess-Tickets → Top-Punkte an `/berater-runde`. |

## Kern-Ideen

- **Reversibilität sortiert.** Zwei-Wege-Tür (reversibel, klein) → die kühnere
  Form ist Default, das Tun ist das Experiment. Ein-Wege-Tür (Datenmodell,
  öffentliche Schnittstelle, irreversibel) → volle Schärfe, Experiment vor Commit.
- **Gegnerischer zweiter Kopf.** Rat wird *prüfbar*, indem ein anderes Modell ihn
  zu widerlegen versucht — nicht, indem man den Berater klüger macht.
- **Ratifizierungs-Ledger.** Entscheide einmal, halte es fest, re-litigiere nicht.
- **Contracts, die Hooks erzwingen.** Maschinen-lesbare Schemas + Guard-Hooks
  machen Disziplin mechanisch statt nur appellativ.
- **Retro → Verbesserung.** Jeder Lauf endet mit einer Retro über die
  *Arbeitsweise*; die Werkstatt verdichtet sie zu Schärfungen.

## Bausteine

| Ordner | Inhalt |
|--------|--------|
| `commands/` | Die Orchestrierungs-Commands (s. Tabelle oben). |
| `agents/` | Subagent-Rollen: `berater`, `antiberater`, `architecture-watchdog`, `watchdog-prep`. |
| `contracts/` | Maschinen-lesbare Schemas (`schemas.md`), Preflight-Vertrag, Retro-Format. |
| `hooks/` | Guard-Hooks: Dispatch-Status, Handoff-Check, Status-Rollback, Restart-Log. |

## Getting Started

Lotse wird **im Repo bearbeitet** (Review + CI-Sicht) und an den Laufzeit-Ort des
Agenten-Harness **deployt**:

```bash
# Deployt die Glue an den Harness-Lese-Ort (Default-Quelle: origin/main):
./deploy.sh

# Vor dem Merge gegen einen Feature-Branch testen:
./deploy.sh --source-ref <branch> --dry-run

# Drift-Probe: weicht der Laufzeit-Ort von der versionierten Quelle ab?
./deploy.sh --verify-only
```

**Modell: Repo = Source of Truth, Laufzeit-Ort = Deploy-Ziel.** Quelle ist immer
ein git-Objekt-Ref (`git archive`), nie der Working Tree — branch-flip-immun. Der
Deploy ist **additiv** (kein `rsync --delete`): aus der Quelle entfernte Dateien
müssen am Laufzeit-Ort von Hand gelöscht werden.

### Konfiguration (Env-Vars, optional)

| Variable | Bedeutung | Default |
|----------|-----------|---------|
| `LOTSE_PROJECT_ROOT` | Wurzel des Projekts, das Lotse orchestriert | aktuelles Verzeichnis |
| `LOTSE_PROJECT_REPO` | GitHub-Slug dieses Projekts (`owner/repo`) für `gh`-Befehle | — |
| `LOTSE_PROCESS_REPO` | GitHub-Slug des Prozess-/Ticket-Repos | — |
| `CLAUDE_HOME` | Laufzeit-Ort / Deploy-Ziel | `~/.claude` |
| `LOTSE_SCRATCH` | Scratch-Ort für Entwürfe & Runden-Notizen | `~/brainstorm` |

## Referenz-Projekt: xbuddy

Die Commands/Contracts hier sind in einem **echten Projekt** kampferprobt — *xbuddy*,
einem Familien-Software-Ökosystem. Im Text begegnen dir konkrete Verweise auf dessen
Ratifizierungs-Ledger (`RAT-N`), Prozess-Tickets (`PW-N`) und `specs/`/`conventions/`-
Pfade. **Das sind Beispiel-Projekt-Artefakte, keine Framework-Pflicht** — sie zeigen
die Methode an einem realen Codebase. Wer Lotse adaptiert, ersetzt Ledger, Specs und
Conventions durch die eigenen und setzt `LOTSE_PROJECT_ROOT` auf sein Repo.

## Mitarbeit & Lizenz

Siehe [`CONTRIBUTING.md`](CONTRIBUTING.md). Lizenz: **Apache-2.0** (siehe
[`LICENSE`](LICENSE)). Sprache der Methode ist Deutsch (etablierte Fachbegriffe
bleiben englisch).

## Quelle des Schwan-Bildes / Source of the swan image

Das mentale Modell ist inspiriert von Bernd Schmids »Der dritte Schwan —
Grundgedanken zur Transaktionsanalyse aus systemischer Sicht«. Mit Dank an Bernd
Schmid und das **isb – Institut für systemische Beratung**, Wiesloch
([isb-w.eu](https://www.isb-w.eu/de/das-isb/bernd-schmid.php)). Die Übertragung des
Bildes auf dieses Framework ist unsere eigene Lesart.

*The mental model is inspired by Bernd Schmid's essay »Der dritte Schwan«. With
thanks to Bernd Schmid and the isb (Wiesloch); mapping the image onto this
framework is our own reading.*
