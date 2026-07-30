#!/usr/bin/env python3
"""status_rollback_guard — PreToolUse-Hook fuer Status-Lifecycle-Schreibversuche (PW-18, Klasse 1).

Abfangbereich:
  Bash-Aufrufe der Form `gh issue edit … --add-label status:*`
  oder `gh issue edit … --remove-label status:*`
  oder `gh issue close … --reason …` (nur wenn auf offenes Ticket angewandt).

Begruendung (PW-18 ENTSCHEID, RECON-3 conventions/reconcile.md#recon-3):
  RECON-3 verbietet Agenten den Shell-Statusuebergang auf `status:*`-Labels.
  Lifecycle wird durch `ticket-status-flow.yml` / `prep-reconcile.yml` aus
  PR-Events getrieben. Jeder Agent-Shell-Aufruf auf `status:*` ist bereits
  heute RECON-3-widrig — der Hook setzt die Konvention mechanisch durch.

  RECON-3 Z. 49-54 nimmt Property-Labels (z. B. `blocked`) ausdruecklich
  aus. Diese Klasse 2 wird deferred (PW-18-RATIFIZIERT, Reopen-Trigger).

Filter-Detail (Codex-R1-Bruch 3 adressiert):
  `tool_input.command` ist freier String. shlex + Argv-Tokenizer + `=`-Normalisierung
  erkennen alle Bash-Formen (--add-label status:spec, --add-label=status:spec,
  -R owner/repo, Issue-URL als Positional, Shell-Variable als Label-Argument).

Skip (PW-23-haerte, 2026-06-09):
  Vorher: `# status_rollback_guard:skip` matchte irgendwo im Bash-String →
  jede status:*-Mutation mit beilaeufig zitiertem Token wurde durchgewunken.
  Jetzt: Skip-Marker greift NUR, wenn die parsierten Label-Mutationen exakt
  dem dokumentierten Nic-Stempel-Pfad entsprechen (`--remove-label status:spec
  --add-label status:ready`, nichts anderes). Alle anderen status:*-Mutationen
  werden gedenied, auch wenn der Token-String im Bash-Material vorkommt
  (Vorschlags-Files, Sessions, Logs zitieren ihn ohnehin haeufig).
  Quelle: `arbeitstag-prep.md` Nic-Block.

Schema folgt dispatch_status_guard.py (RAT-15): stdin-JSON,
permissionDecision-Antwort, exit 0 bei Durchlass.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from urllib.parse import urlparse

# PW-85 RATIFIZIERT 2026-07-06: Verdikt-Pruef-Logik in geteiltes Modul extrahiert
# (Duplikations-Gegenmittel — prep-reconcile.yml nutzt verdict_check.py direkt,
# brainstorm/berater-runde/20260706-153129-RATIFIZIERT-pw85-ready-create-kante.md).
# sys.path-Erweiterung: beim importlib-Ladeweg (z. B. Tests) ist das Hook-
# Verzeichnis nicht automatisch in sys.path.
# isort: off
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verdict_check import (
    VERDICT_MARKER_RE,
    WERFT_VERDICT_MARKER_RE,
    _check_verdict_generic,
    _extract_axis_value,
    compute_verdict_hash,  # noqa: F401 — re-exportiert; Tests greifen via srg.compute_verdict_hash
    fetch_verdict_comment,
)
# isort: on

# Lifecycle-Labels, deren Schreiben/Entfernen durch Agent RECON-3-widrig ist.
# PW-33 (2026-06-09): `status:spec-in-progress` als prep-Lock neu hinzu — der
# Skill /arbeitstag-prep setzt ihn vor Watchdog-Dispatch (Lock-Semantik:
# "jemand prept gerade an diesem Ticket, niemand sonst anfassen"), entfernt
# ihn nach Verdict (zurueck auf status:spec, oder weiter auf status:ready).
STATUS_RE = re.compile(r"^status:(spec|spec-in-progress|ready|in-progress|in-review|blocked)$")

# Skip-Marker im Bash-Befehl (Kommentar-Form).
SKIP_RE = re.compile(r"#\s*status_rollback_guard:skip\b")

# Dokumentierte Skill-Pfade, die per Skip-Marker explizit erlaubt sind.
# Andere Lifecycle-Mutationen werden gedenied, auch wenn der Token-String im
# cmd vorkommt (Vorschlags-Files zitieren ihn).
# Pfad 1: Nic-Block in arbeitstag-prep.md (PW-18).
NIC_STAMP_REMOVES = frozenset({"status:spec"})
NIC_STAMP_ADDS = frozenset({"status:ready"})
# Pfad 2: prep-Claim/Release in arbeitstag-prep.md (PW-33).
PREP_CLAIM_REMOVES = frozenset({"status:spec"})
PREP_CLAIM_ADDS = frozenset({"status:spec-in-progress"})
PREP_RELEASE_REMOVES = frozenset({"status:spec-in-progress"})
PREP_RELEASE_ADDS_SPEC = frozenset({"status:spec"})      # zurueck (kein Stempel)
PREP_RELEASE_ADDS_READY = frozenset({"status:ready"})    # weiter (Nic stempelt)

# PW-30 (xbuddy-prozess#31, 2026-06-09): prep_verdict-Comment-Pflicht vor jedem
# status:ready-Stempel. PW-43 RATIFIZIERT 2026-06-21: werft_verdict-Pendant fuer
# Werft-F5-Stempel. VERDICT_MARKER_RE + WERFT_VERDICT_MARKER_RE: importiert aus
# verdict_check (PW-85).
# PW-25 + PW-43 RATIFIZIERT 2026-06-21: Werft-Stempel-Pfad.
# Werft-F5 entfernt im selben gh-edit `status:spec` + `in-werft`, setzt `status:ready`.
WERFT_STAMP_REMOVES = frozenset({"status:spec", "in-werft"})
WERFT_STAMP_ADDS = frozenset({"status:ready"})

# PW-83 RATIFIZIERT 2026-07-03 (ENTSCHEID 20260703-232716-RATIFIZIERT-membran-gate-
# am-akt.md, „Fix B"): der PW-54-werft_mockup_path-stat()-Check sass bisher NUR
# konsumenten-seitig (dispatch_status_guard, konditional auf Feld-Praesenz — fehlt
# das Feld ganz, feuerte nichts). Hier wird er an den bereits existierenden
# PRODUZENTEN-Stempel (Werft-F5) gezogen: bei deliverable_kind=ui_build ist
# werft_mockup_path unbedingt Pflicht. Form gespiegelt aus dispatch_status_guard PW-54.
XBUDDY_REPO_ROOT = os.environ.get("LOTSE_PROJECT_ROOT") or os.environ.get("XBUDDY_REPO") or os.getcwd()
WERFT_MOCKUP_REQUIRED_PREFIX = "specs/mockups/"
WERFT_MOCKUP_REQUIRED_SUFFIX = ".html"

# PW-82 RATIFIZIERT 2026-07-03 (ENTSCHEID …„Fix A"): mechanischer Negativ-Filter
# (RAT-11-konform — gatet INS Urteil, entscheidet nicht). Traegt der Ticket-BODY
# einen Vorwaerts-Entscheidungs-Marker, darf status:ready nur fallen, wenn das
# prep_verdict axes.body_decision: geloest traegt. Marker-ABWESENHEIT ist kein
# Freibrief (das semantische Urteil bleibt beim Watchdog, Default=wahl) — der Hook
# prueft nur den Marker-POSITIV-Fall.
BODY_DECISION_MARKER_RE = re.compile(
    r"(/berater-runde"
    r"|spec-mandatiert"
    r"|Architektur-(?:Frage|Entscheidung|Wahl)"
    r"|Option\s+[AB]\b[^\n]{0,80}?\bvs\.?\b"
    r"|RAT-\d+[^\n]{0,80}?(?:Delta|Anwendung|offen))",
    re.IGNORECASE,
)
# PW-26-RATIFIZIERT 2026-06-09: arch_choice-Marker am Issue erlaubt Spec-PR-Merge
# fuer architecture_class=wahl-Karten. Hook prueft erste Zeile eines Comments,
# Format `<!-- arch_choice v1 issue:NR choice:A -->` (A/B/halt sind moegliche
# Werte; halt blockt weiter).
ARCH_CHOICE_MARKER_RE = re.compile(
    r"^<!--\s*arch_choice\s+v1\s+issue:(\d+)\s+choice:(\w+)\s*-->",
    re.MULTILINE,
)
# MIGRATION_CUTOFF_ISO, XBUDDY_REPO_PATH, DRIFT_PATHS,
# SPEC_NONBINDING_HEADINGS, SPEC_NONBINDING_ID_PREFIX: importiert aus verdict_check (PW-85).


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


SPEC_BRANCH_RE = re.compile(r"^spec/(\d+)-")


def parse_gh_pr_merge(command_str: str):
    """Parst `gh pr merge <pr-or-url> --merge|--squash|--rebase --repo X`-Aufrufe.

    Liefert (pr_nr, repo) wenn erkannt, sonst None.

    PW-26-RATIFIZIERT 2026-06-09: Spec-PR-Merge ist neuer Hook-Eingriffspunkt
    (Komponente B `wahl`-Sperre + Komponente A Cross-Spec-Probe).
    """
    try:
        toks = shlex.split(command_str, posix=True, comments=False)
    except ValueError:
        return None
    if not toks or "gh" not in toks or "pr" not in toks or "merge" not in toks:
        return None

    norm = []
    for t in toks:
        if t.startswith("--") and "=" in t:
            k, v = t.split("=", 1)
            norm += [k, v]
        else:
            norm.append(t)

    pr_nr, repo = None, None
    i = 0
    while i < len(norm):
        t = norm[i]
        if t in ("--repo", "-R") and i + 1 < len(norm):
            repo = norm[i + 1]
            i += 2
            continue
        if t.startswith("https://github.com/"):
            try:
                p = urlparse(t).path.strip("/").split("/")
                if len(p) >= 4 and p[2] == "pull" and p[3].isdigit():
                    repo = f"{p[0]}/{p[1]}"
                    pr_nr = p[3]
            except Exception:
                pass
        elif t.isdigit() and pr_nr is None:
            pr_nr = t
        i += 1
    return (pr_nr, repo)


def fetch_pr_meta(repo: str, pr_nr: str) -> dict | None:
    """Liefert {headRefName, files: [paths], body, ...} oder None.
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_nr, "--repo", repo,
             "--json", "headRefName,files,body,number,title"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def check_arch_choice_for_issue(repo: str, issue: str) -> bool:
    """Prueft, ob ein gueltiger arch_choice-Marker am Issue liegt (A oder B,
    NICHT halt). PW-26 Komponente B.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue, "--repo", repo, "--json", "comments"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    if result.returncode != 0:
        return False
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False
    for comment in reversed(data.get("comments") or []):
        body = comment.get("body", "")
        if not isinstance(body, str):
            continue
        first_line = body.lstrip().split("\n", 1)[0]
        m = ARCH_CHOICE_MARKER_RE.match(first_line)
        if m and m.group(1) == issue and m.group(2).lower() in ("a", "b"):
            return True
    return False


def check_spec_path_exclusive(repo: str, exclude_issue: str,
                                spec_paths: list[str]) -> tuple[bool, str]:
    """PW-26-RATIFIZIERT 2026-06-09 (Codex-Bruch 3): Pre-Merge-Probe gegen
    andere offene Tickets, die einen der Spec-Pfade als `reif_spec_path` in
    ihrem prep_verdict-Comment zitieren.

    exclude_issue: das aktuelle Ticket (dessen Spec-PR gerade gemergt wird) —
    nicht gegen sich selbst pruefen.

    Pragmatischer Scope: nur status:in-progress und status:ready (aktive Tracks),
    nicht status:spec (noch nicht claimed).

    Liefert (ok, reason). ok=True = darf gemergt werden.
    """
    if not spec_paths:
        return (True, "keine spec-Pfade im Diff")
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--repo", repo,
             "--label", "status:in-progress",
             "--state", "open", "--limit", "100",
             "--json", "number,title,comments"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return (True, "gh nicht verfuegbar — cross-spec optimistisch")
    if result.returncode != 0:
        return (True, "gh-issue-list failed — cross-spec optimistisch")
    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        return (True, "gh-output unparsbar — cross-spec optimistisch")
    conflicts = []
    for issue in issues:
        if str(issue.get("number")) == str(exclude_issue):
            continue
        for comment in (issue.get("comments") or []):
            body = comment.get("body", "")
            if not isinstance(body, str):
                continue
            first_line = body.lstrip().split("\n", 1)[0]
            if not VERDICT_MARKER_RE.match(first_line):
                continue
            other_spec_path = _extract_axis_value(body, "reif_spec_path")
            if other_spec_path and other_spec_path in spec_paths:
                conflicts.append((issue.get("number"), issue.get("title"), other_spec_path))
                break
    if conflicts:
        first = conflicts[0]
        return (False, f"Cross-Spec-Konflikt: Spec-Pfad '{first[2]}' wird auch von "
                       f"#{first[0]} '{first[1]}' (status:in-progress) konsumiert. "
                       f"cross-spec-koord-Karte vorlegen (arbeitstag-prep.md Komponente A) "
                       f"oder Spec-PR zuruecknehmen, bis #{first[0]} fertig ist.")
    return (True, "ok")


def parse_gh_edit(command_str: str):
    """Robustes Parsing eines `gh issue edit/close/reopen`-Aufrufs.

    Liefert (issue_nr, repo, adds, removes) wenn ein gh-issue-Aufruf erkannt,
    sonst None.
    """
    try:
        toks = shlex.split(command_str, posix=True, comments=False)
    except ValueError:
        # Unparsbar (z. B. unschliessende Quotes) — caller exit 0 lassen,
        # weil der Bash-Befehl ohnehin failen wird.
        return None
    if not toks or "gh" not in toks or "issue" not in toks:
        return None
    subcommands = ("edit", "close", "reopen")
    if not any(t in toks for t in subcommands):
        return None

    # --flag=value → --flag value normalisieren.
    norm = []
    for t in toks:
        if t.startswith("--") and "=" in t:
            k, v = t.split("=", 1)
            norm += [k, v]
        else:
            norm.append(t)

    adds, removes, repo, issue = [], [], None, None
    i = 0
    while i < len(norm):
        t = norm[i]
        if t == "--add-label" and i + 1 < len(norm):
            adds.append(norm[i + 1])
            i += 2
            continue
        if t == "--remove-label" and i + 1 < len(norm):
            removes.append(norm[i + 1])
            i += 2
            continue
        if t in ("--repo", "-R") and i + 1 < len(norm):
            repo = norm[i + 1]
            i += 2
            continue
        if t.startswith("https://github.com/"):
            try:
                p = urlparse(t).path.strip("/").split("/")
                if len(p) >= 4 and p[2] == "issues" and p[3].isdigit():
                    repo = f"{p[0]}/{p[1]}"
                    issue = p[3]
            except Exception:
                pass
        elif t.isdigit() and issue is None:
            issue = t
        i += 1

    return (issue, repo, adds, removes)


def is_lifecycle(label: str) -> bool:
    """Klasse 1: status:*-Labels. RECON-3-gesperrt fuer Agent."""
    return bool(STATUS_RE.match(label))


def is_nic_stamp(adds, removes) -> bool:
    """Nic-Stempel-Pfad: genau -status:spec +status:ready, keine weiteren Labels.

    Andere Lifecycle-Mutationen (auch wenn legitim erscheinend) muessen explizit
    in den Hook eingetragen werden — keine offene Bypass-Klasse.
    """
    return (
        frozenset(adds) == NIC_STAMP_ADDS
        and frozenset(removes) == NIC_STAMP_REMOVES
    )


def is_prep_claim(adds, removes) -> bool:
    """prep-Lock: -status:spec +status:spec-in-progress (PW-33)."""
    return (
        frozenset(adds) == PREP_CLAIM_ADDS
        and frozenset(removes) == PREP_CLAIM_REMOVES
    )


def is_werft_stamp(adds, removes) -> bool:
    """Werft-Stempel-Pfad (PW-25 + PW-43 RATIFIZIERT 2026-06-21):
    -status:spec -in-werft +status:ready in einem gh-edit.

    Werft entfernt das Held-Marker-Label `in-werft` synchron mit dem Stempel —
    der Hook unterscheidet so Werft-Stempel vom Nic-Stempel (der `in-werft`
    nicht anfasst) und vom prep-Release (der `status:spec-in-progress`
    entfernt).
    """
    return (
        frozenset(adds) == WERFT_STAMP_ADDS
        and frozenset(removes) == WERFT_STAMP_REMOVES
    )


def is_prep_release(adds, removes) -> bool:
    """prep-Release: -status:spec-in-progress +status:spec ODER +status:ready (PW-33).

    Variante +status:ready ist nur erlaubt zusammen mit prep_verdict-Pflicht
    (die main()-Logik prueft das gesondert, weil ready-Stempel ein
    durable Artefakt ist).
    """
    rem = frozenset(removes)
    add = frozenset(adds)
    return rem == PREP_RELEASE_REMOVES and add in (PREP_RELEASE_ADDS_SPEC, PREP_RELEASE_ADDS_READY)


# ---------------------------------------------------------------------------
# compute_verdict_hash, fetch_verdict_comment, _extract_axis_value,
# check_spec_binding, _check_reif_structured, _check_chore_evidence,
# check_drift, _check_verdict_generic: importiert aus verdict_check (PW-85).
# ---------------------------------------------------------------------------


def fetch_issue_body(repo: str, issue: str) -> str | None:
    """Liest den reinen Issue-BODY (nicht Comments) via gh. PW-82: der
    Body-Entscheidungs-Filter prueft die Frame-Prosa des Tickets, nicht die
    Verdikt-/Werft-Comments."""
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue, "--repo", repo, "--json", "body"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    try:
        return (json.loads(result.stdout) or {}).get("body")
    except json.JSONDecodeError:
        return None


def validate_werft_mockup_path_value(mockup_path: str) -> tuple[bool, str]:
    """PW-83: Form-/Existenz-Probe fuer werft_mockup_path am F5-Stempel.
    Spiegelt dispatch_status_guard.py PW-54 (specs/mockups/<slug>/*.html, kein
    /tmp//brainstorm/, realpath im Repo, stat()-Existenz), aber produzenten-seitig
    beim Werft-Stempel statt konsumenten-seitig beim Dispatch."""
    if not mockup_path or mockup_path.lower() in ("none", "null"):
        return (False, "werft_mockup_path leer/null")
    if mockup_path.startswith(("/tmp/", os.path.expanduser("~/brainstorm/"), "brainstorm/")):
        return (False,
                f"werft_mockup_path zeigt auf nicht-durable Heimat ({mockup_path}) — "
                f"Mockup muss nach {WERFT_MOCKUP_REQUIRED_PREFIX}<slug>/ ins xbuddy-Repo "
                "(werft.md F3-Ende, decisions/README.md:15-20).")
    if os.path.isabs(mockup_path):
        if not mockup_path.startswith(XBUDDY_REPO_ROOT + os.sep):
            return (False, f"werft_mockup_path absolut, ausserhalb xbuddy-Repo: {mockup_path}")
        check_path = mockup_path
        rel_path = mockup_path[len(XBUDDY_REPO_ROOT) + 1:]
    else:
        check_path = os.path.join(XBUDDY_REPO_ROOT, mockup_path)
        rel_path = mockup_path
    if not rel_path.startswith(WERFT_MOCKUP_REQUIRED_PREFIX):
        return (False, f"werft_mockup_path muss unter {WERFT_MOCKUP_REQUIRED_PREFIX} liegen ({mockup_path})")
    if not rel_path.endswith(WERFT_MOCKUP_REQUIRED_SUFFIX):
        return (False, f"werft_mockup_path muss auf {WERFT_MOCKUP_REQUIRED_SUFFIX} enden ({mockup_path})")
    try:
        real_check = os.path.realpath(check_path)
        real_root = os.path.realpath(XBUDDY_REPO_ROOT) + os.sep
        if not real_check.startswith(real_root):
            return (False, f"werft_mockup_path realpath verlaesst xbuddy-Repo ({real_check})")
    except OSError:
        pass
    if not os.path.exists(check_path):
        return (False, f"werft_mockup_path existiert nicht: {check_path} (angegeben als {mockup_path})")
    return (True, "ok")


def check_prep_body_decision(repo: str, issue: str, verdict_body: str | None) -> tuple[bool, str]:
    """PW-82 RATIFIZIERT 2026-07-03: mechanischer Negativ-Filter (RAT-11-konform).

    Traegt der Ticket-BODY einen Vorwaerts-Entscheidungs-Marker (/berater-runde,
    Architektur-Frage, Option A vs B, RAT-N Delta/Anwendung), darf status:ready nur
    fallen, wenn das prep_verdict axes.body_decision: geloest traegt. Der Filter
    ENTSCHEIDET nichts — er erzwingt nur, dass das Urteil eine im Body sichtbare
    offene Entscheidung adressiert hat, statt sie als nachzeichnen zu ueberspringen.

    Marker-ABWESENHEIT ist KEIN Freibrief fuer geloest (Codex-RISKANT): das
    semantische Urteil bleibt beim Watchdog (Default=wahl). Der Hook prueft nur den
    Marker-POSITIV-Fall — der Boden, nicht die Decke.
    """
    body_text = fetch_issue_body(repo, issue)
    if body_text is None:
        # Best-effort: kein Body lesbar → Filter optimistisch (Watchdog-Urteil traegt).
        return (True, "issue-body nicht lesbar — Filter optimistisch")
    marker = BODY_DECISION_MARKER_RE.search(body_text)
    if not marker:
        return (True, "kein Body-Entscheidungs-Marker")
    bd = _extract_axis_value(verdict_body, "body_decision") if verdict_body else None
    if bd == "geloest":
        return (True, "body_decision: geloest belegt")
    return (False,
            f"PW-82: Ticket-Body traegt Entscheidungs-Marker '{marker.group(0).strip()}', "
            f"aber prep_verdict.axes.body_decision != geloest (gefunden: {bd!r}). "
            "Ein Ticket mit offener Architektur-/Anwendungs-Entscheidung im Body ist NICHT "
            "entscheidungsrein. /arbeitstag-prep neu urteilen: body_decision: offen => "
            "architecture_class: wahl (nicht ready); ODER body_decision: geloest mit "
            "body_decision_evidence (welcher Beschluss/PR die Frage schloss).")


def check_prep_verdict(repo: str, issue: str) -> tuple[bool, str]:
    """PW-30-Pflicht-Check: prep_verdict-Comment am Ticket (Default-Marker)."""
    return _check_verdict_generic(repo, issue, VERDICT_MARKER_RE, "prep_verdict")


def check_werft_verdict(repo: str, issue: str) -> tuple[bool, str]:
    """PW-43-Pflicht-Check: werft_verdict-Comment am Ticket fuer Werft-F5-Stempel.

    Zusaetzlich zum generischen Check (Marker + Hash + verdict:ready + Drift):
    pruefe `werft: true` unter axes: — das geht in compute_verdict_hash ein
    (nicht faelschbar), markiert Provenienz Werft vs. prep eindeutig.
    """
    ok, reason = _check_verdict_generic(repo, issue, WERFT_VERDICT_MARKER_RE, "werft_verdict")
    if not ok:
        return (ok, reason)
    # Body nochmal holen fuer werft-axes-Probe (kostet 1 weiteren gh-call, akzeptabel)
    body, _ = fetch_verdict_comment(repo, issue, WERFT_VERDICT_MARKER_RE)
    if body is None:
        return (False, "werft_verdict-Body nicht erneut lesbar — pruefe gh issue view")
    # axes.werft: true ist Pflicht (Provenienz-Sperre gegen prep-Pfad-Verwechslung)
    werft_axis = _extract_axis_value(body, "werft")
    if werft_axis != "true":
        return (False,
                f"PW-43: axes.werft != true (gefunden: {werft_axis!r}). "
                "Werft-F5-Verdikt MUSS axes.werft: true tragen — geht in "
                "compute_verdict_hash, schuetzt vor prep-Verwechslung.")
    # PW-83 RATIFIZIERT 2026-07-03: deliverable_kind + werft_mockup_path am F5-Stempel
    # erzwingen (produzenten-seitiges Gate am Akt, nicht erst downstream beim Dispatch).
    # deliverable_kind geht unter axes: in compute_verdict_hash (Codex-Haertung: kein
    # ungehashter Top-Level-Proxy).
    deliverable = _extract_axis_value(body, "deliverable_kind")
    if deliverable is None:
        return (False,
                "PW-83: axes.deliverable_kind fehlt (ui_build | non_ui). Werft-F5 MUSS "
                "den Track klassifizieren: ui_build => werft_mockup_path Pflicht, "
                "non_ui => deliverable_evidence Pflicht (werft.md F5).")
    if deliverable == "ui_build":
        mockup = _extract_axis_value(body, "werft_mockup_path")
        if mockup is None:
            return (False,
                    "PW-83: deliverable_kind=ui_build, aber axes.werft_mockup_path fehlt. "
                    "UI-Bau-Uebergabe ohne persistiertes Mockup ist nicht uebergabereif "
                    "(specs/mockups/<slug>/*.html, werft.md F3-Ende/F5).")
        mok_ok, mok_reason = validate_werft_mockup_path_value(mockup)
        if not mok_ok:
            return (False, f"PW-83: {mok_reason}")
    elif deliverable == "non_ui":
        if _extract_axis_value(body, "deliverable_evidence") is None:
            return (False,
                    "PW-83: deliverable_kind=non_ui verlangt axes.deliverable_evidence "
                    "(konkrete Datei:Zeile/Body-Stelle, warum kein UI gebaut wird) — sonst "
                    "ist non_ui ein ungeprueftes Selbst-Attest (Codex-Haertung).")
    else:
        return (False,
                f"PW-83: axes.deliverable_kind='{deliverable}' unbekannt (erlaubt: ui_build | non_ui).")
    return (True, "ok")


def handle_gh_pr_merge(cmd: str) -> None:
    """PW-26-RATIFIZIERT 2026-06-09: Spec-PR-Merge auf Branch `spec/<nr>-…`
    bekommt zwei Sperren:
      - Komponente B `architecture_class: wahl` ohne `arch_choice`-Marker → deny.
      - Komponente A Cross-Spec-Probe: andere offene Tickets, die einen der
        Spec-Pfade als reif_spec_path zitieren → deny.

    PRs, die kein `spec/<nr>-…`-Branch tragen, durchlaufen den Hook als no-op.
    """
    parsed = parse_gh_pr_merge(cmd)
    if parsed is None:
        return
    pr_nr, repo = parsed
    if not pr_nr or not repo:
        return
    meta = fetch_pr_meta(repo, pr_nr)
    if not meta:
        return
    branch = meta.get("headRefName", "")
    m = SPEC_BRANCH_RE.match(branch)
    if not m:
        # Kein spec/<nr>-…-Branch → Hook nicht zustaendig (z. B. revert/, fix/, …).
        return
    issue = m.group(1)

    # B-Sperre: architecture_class=wahl braucht arch_choice-Marker.
    verdict_body, _ = fetch_verdict_comment(repo, issue)
    if verdict_body:
        arch_m = re.search(r"^architecture_class:\s*(\S+)\s*$",
                           verdict_body, re.MULTILINE)
        if arch_m and arch_m.group(1) == "wahl" and not check_arch_choice_for_issue(repo, issue):
            deny(
                f"PW-26 Komponente B: Spec-PR-Merge fuer architecture_class=wahl "
                f"(#{issue}) blockiert — kein arch_choice-Marker am Issue. "
                f"Mini-Wahl-Karte vorlegen, Nic waehlt, dann mergen. "
                f"Marker-Form erste Zeile eines Comments: "
                f"`<!-- arch_choice v1 issue:{issue} choice:A -->` (A oder B)."
            )

    # A-Probe: Cross-Spec-Konflikt.
    files = meta.get("files") or []
    spec_paths = [f.get("path") for f in files
                  if isinstance(f.get("path"), str)
                  and (f["path"].startswith("specs/") or f["path"].startswith("conventions/"))]
    if spec_paths:
        ok, reason = check_spec_path_exclusive(repo, issue, spec_paths)
        if not ok:
            deny(f"PW-26 Komponente A: {reason}")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    cmd = tool_input.get("command", "")
    if not isinstance(cmd, str) or not cmd:
        sys.exit(0)

    # PW-26: gh-pr-merge-Pfad (Spec-PR-Merge-Sperren) zuerst — separater Tool-Aufruf.
    if "gh" in cmd and "pr" in cmd and "merge" in cmd:
        handle_gh_pr_merge(cmd)  # deniert intern bei Bruch; sonst weiter.

    parsed = parse_gh_edit(cmd)
    if parsed is None:
        # Kein gh-issue-edit/close/reopen → nicht zustaendig.
        # Skip-Marker hier irrelevant (vor PW-23: anywhere-Match → Bypass).
        sys.exit(0)
    issue, repo, adds, removes = parsed

    # Klasse 1: jedes status:*-Schreiben/Entfernen durch Agent ist RECON-3-widrig.
    bad_lifecycle = [lbl for lbl in (adds + removes) if is_lifecycle(lbl)]
    if not bad_lifecycle:
        # Keine status:*-Beruehrung → Klasse 2 (blocked, defer) erreicht den
        # Hook hier nicht. Durchlassen.
        sys.exit(0)

    # PW-23-haerte: Skip-Marker greift NUR auf dokumentierten Skill-Pfaden.
    # Andere Lifecycle-Mutationen werden gedenied, auch wenn der Token-String
    # im cmd vorkommt (Vorschlags-Files zitieren ihn).

    # Pfad 1: Nic-Stempel-Pfad (-spec +ready) — PW-30-prep_verdict-Pflicht.
    if is_nic_stamp(adds, removes) and SKIP_RE.search(cmd):
        verdict_ok, verdict_reason = check_prep_verdict(repo, issue)
        if not verdict_ok:
            deny(
                f"PW-30: status:ready ohne gueltigen prep_verdict-Comment am Ticket. "
                f"Grund: {verdict_reason} "
                f"Schritt: /arbeitstag-prep durchlaufen, Verdikt-YAML als Comment posten "
                f"(arbeitstag-prep.md#nic-stamp Schritt 2), DANN Label setzen."
            )
        # PW-82: Body-Entscheidungs-Filter (Marker-Positiv-Fall) VOR dem Stempel.
        vbody, _ = fetch_verdict_comment(repo, issue)
        bd_ok, bd_reason = check_prep_body_decision(repo, issue, vbody)
        if not bd_ok:
            deny(bd_reason)
        sys.exit(0)

    # Pfad 2: prep-Claim (-spec +spec-in-progress) — PW-33.
    # Erlaubt dem /arbeitstag-prep-Skill, ein Ticket als "in prep-Bearbeitung"
    # zu markieren vor Watchdog-Dispatch (Lock-Semantik).
    if is_prep_claim(adds, removes) and SKIP_RE.search(cmd):
        sys.exit(0)

    # Pfad 3: prep-Release (-spec-in-progress +spec ODER +ready) — PW-33.
    # +spec = zurueck (kein Stempel). +ready = Nic stempelt — prep_verdict Pflicht.
    if is_prep_release(adds, removes) and SKIP_RE.search(cmd):
        if frozenset(adds) == PREP_RELEASE_ADDS_READY:
            verdict_ok, verdict_reason = check_prep_verdict(repo, issue)
            if not verdict_ok:
                deny(
                    f"PW-30/33: prep-Release auf status:ready ohne gueltigen prep_verdict-Comment. "
                    f"Grund: {verdict_reason} "
                    f"Schritt: prep_verdict-Comment posten (arbeitstag-prep.md#nic-stamp), DANN Label setzen."
                )
            # PW-82: Body-Entscheidungs-Filter (Marker-Positiv-Fall) VOR dem Stempel.
            vbody, _ = fetch_verdict_comment(repo, issue)
            bd_ok, bd_reason = check_prep_body_decision(repo, issue, vbody)
            if not bd_ok:
                deny(bd_reason)
        sys.exit(0)

    # Pfad 4: Werft-Stempel (-spec -in-werft +ready) — PW-25 + PW-43 RATIFIZIERT 2026-06-21.
    # Werft-F5 entfernt status:spec UND in-werft synchron, setzt status:ready.
    # Skip-Marker `werft-stamp` + werft_verdict-Comment-Pflicht (mit axes.werft: true).
    if is_werft_stamp(adds, removes) and SKIP_RE.search(cmd):
        verdict_ok, verdict_reason = check_werft_verdict(repo, issue)
        if not verdict_ok:
            deny(
                f"PW-43: Werft-Stempel auf status:ready ohne gueltigen werft_verdict-Comment. "
                f"Grund: {verdict_reason} "
                f"Schritt: Werft-F5 dispatcht watchdog-prep mit werft_gate_b_done=true, "
                f"postet werft_verdict v1 mit axes.werft: true (werft.md F5), DANN Label tauschen."
            )
        sys.exit(0)

    target = f"{repo}#{issue}" if repo and issue else "<unknown>"
    deny(
        f"PW-18 / RECON-3: Agent-Shell-Statusuebergang verboten. "
        f"Versucht: {bad_lifecycle} auf {target}. "
        f"Lifecycle-Labels (status:*) werden durch GitHub-Actions getrieben "
        f"(ticket-status-flow.yml / prep-reconcile.yml), nicht per gh-Shell. "
        f"Konvention: conventions/reconcile.md (RECON-3-Block). "
        f"Skip-Marker fuer dokumentierten Sonderpfad (Nic-Block, siehe "
        f"~/.claude/commands/arbeitstag-prep.md#nic-stamp — nur "
        f"--remove-label status:spec --add-label status:ready, NICHTS anderes): "
        f"Kommentar `# status_rollback_guard:skip <grund>` in dieselbe Bash-Tool-Eingabe."
    )


if __name__ == "__main__":
    main()
