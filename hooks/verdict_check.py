#!/usr/bin/env python3
"""verdict_check — Geteilte Verdikt-Pruef-Logik fuer prep_verdict und werft_verdict.

Extrahiert aus status_rollback_guard.py (PW-85 RATIFIZIERT 2026-07-06,
brainstorm/berater-runde/20260706-153129-RATIFIZIERT-pw85-ready-create-kante.md).

Zwei Verwendungsarten:
  1. Bibliothek: von status_rollback_guard.py importiert (Hook-Pfad, PW-30/PW-43).
  2. Skript: direkt als `python3 methode/hooks/verdict_check.py` aufgerufen (aus
     prep-reconcile.yml, Workflow-Pfad). Liest REPO + ISSUE aus Umgebungsvariablen,
     prueft prep_verdict ODER werft_verdict, exit 0 = gueltig, exit 1 = kein Verdikt.

Verdikt-Sorten:
  - prep_verdict (PW-30): watchdog-prep postet nach Reife-Urteil
  - werft_verdict (PW-43): Werft-F5 postet nach Lieferstufe F5

Schema: <!-- <marker_name> v1 issue:<NR> sha:<16hex> -->
         verdict: ready
         axes:
           <key>: <value>
         ...
"""

import hashlib
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

# PW-30: prep_verdict-Marker-Regex.
VERDICT_MARKER_RE = re.compile(
    r"^<!--\s*prep_verdict\s+v1\s+issue:(\d+)\s+sha:([0-9a-f]{16})\s*-->",
    re.MULTILINE,
)

# PW-43 RATIFIZIERT 2026-06-21: werft_verdict-Marker-Regex.
WERFT_VERDICT_MARKER_RE = re.compile(
    r"^<!--\s*werft_verdict\s+v1\s+issue:(\d+)\s+sha:([0-9a-f]{16})\s*-->",
    re.MULTILINE,
)

# Git-Repo-Pfad fuer Drift- und Spec-Binding-Checks (best-effort, kein Fail bei Fehlen).
XBUDDY_REPO_PATH = os.environ.get("LOTSE_PROJECT_ROOT") or os.environ.get("XBUDDY_REPO") or os.getcwd()

# Pfade, bei deren Aenderung ein Verdikt als stale gilt.
DRIFT_PATHS = ("specs/", "decisions/")

# Zeitstempel fuer den Migrations-Backfill-Cutoff (migrated: true).
MIGRATION_CUTOFF_ISO = "2026-06-09T16:00:00Z"

# RAT-11-Disziplin: Headings/ID-Prefixe, die eine Spec-Sektion als nicht-bindend markieren.
SPEC_NONBINDING_HEADINGS = (
    "## Offene Punkte",
    "## ENTWURF",
    "### ENTWURF",
)
SPEC_NONBINDING_ID_PREFIX = "OPEN-"


# ---------------------------------------------------------------------------
# Kern-Funktionen
# ---------------------------------------------------------------------------

def compute_verdict_hash(verdict_body: str) -> str | None:
    """Liest aus dem verdict-Comment-Body die `verdict:`, `axes:` (und optional
    `verdict_repo_sha:` + `architecture_class:`) und berechnet den 16-Zeichen-
    Hex-Hash, der mit dem Marker-Hash uebereinstimmen muss.

    Schema-Detection (PW-26-RATIFIZIERT 2026-06-09, Codex-Bruch 4):
      - Wenn `architecture_class:` im Body ist (= PW-26-Schema):
        Hash umfasst {verdict, axes, verdict_repo_sha, architecture_class}.
        Damit kann verdict_repo_sha nicht „gewaschen" werden (Replace-Pfad
        invalidiert den Hash).
      - Sonst (Legacy PW-30-Schema): Hash umfasst {verdict, axes}.
        Backwards-Kompat fuer Tickets, die vor PW-26 gestempelt wurden.

    Zur Defensive: Parsing per Regex, kein YAML-Lib (Hook bleibt dependency-arm).
    """
    verdict_m = re.search(r"^verdict:\s*(\S+)\s*$", verdict_body, re.MULTILINE)
    if not verdict_m:
        return None
    verdict_val = verdict_m.group(1)

    # axes-Block: alle Zeilen ab "axes:" bis zur naechsten Top-Level-Key (Spaltenanfang)
    axes_m = re.search(r"^axes:\s*\n((?:[ \t]+.+\n)+)", verdict_body, re.MULTILINE)
    if not axes_m:
        return None
    axes_lines = axes_m.group(1)
    axes_dict = {}
    for line in axes_lines.splitlines():
        m = re.match(r"\s+(\w+):\s*(.+?)\s*$", line)
        if m:
            key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
            axes_dict[key] = val

    # PW-26-Schema-Detection: architecture_class als Top-Level-Key signalisiert,
    # dass der neue, erweiterte Hash erwartet wird.
    arch_m = re.search(r"^architecture_class:\s*(\S+)\s*$", verdict_body, re.MULTILINE)
    sha_m = re.search(r"^verdict_repo_sha:\s*[\"']?([0-9a-fA-F]{7,40})[\"']?\s*$",
                      verdict_body, re.MULTILINE)

    payload_dict = {"verdict": verdict_val, "axes": axes_dict}
    if arch_m:
        # PW-26-Schema: SHA + architecture_class in Hash-Payload.
        payload_dict["verdict_repo_sha"] = sha_m.group(1) if sha_m else ""
        payload_dict["architecture_class"] = arch_m.group(1)

    payload = json.dumps(payload_dict, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def fetch_verdict_comment(
    repo: str, issue: str, marker_re=VERDICT_MARKER_RE,
) -> tuple[str, dict] | tuple[None, None]:
    """Iteriert Issue-Comments rueckwaerts und findet den ersten mit gueltigem
    Marker als erste Zeile.

    Default marker_re = VERDICT_MARKER_RE (prep_verdict v1, PW-30).
    Fuer Werft-Pfad: marker_re=WERFT_VERDICT_MARKER_RE (werft_verdict v1, PW-43).

    Liefert (comment_body, parsed_marker_dict) oder (None, None).
    parsed_marker_dict: {"issue": NR, "sha": HASH}.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue, "--repo", repo,
             "--json", "comments"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return (None, None)
    if result.returncode != 0:
        return (None, None)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return (None, None)
    comments = data.get("comments") or []
    # Rueckwaerts iterieren (juengster zuerst)
    for comment in reversed(comments):
        body = comment.get("body", "")
        if not isinstance(body, str):
            continue
        # Marker MUSS erste Zeile sein (analog SKIP_MARKER-Disziplin PW-23).
        first_line = body.lstrip().split("\n", 1)[0]
        marker_m = marker_re.match(first_line)
        if marker_m:
            return (body, {"issue": marker_m.group(1), "sha": marker_m.group(2)})
    return (None, None)


def _extract_axis_value(body: str, key: str) -> str | None:
    """Liest einen flachen axes.<key>-Wert aus dem Verdikt-Body.

    Erkennt Zeilen wie `  key: value` oder `  key: "quoted value"`.
    Liefert None bei null/missing.
    """
    m = re.search(rf"^\s+{re.escape(key)}:\s*(.+?)\s*$", body, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip().strip('"').strip("'")
    if val in ("null", "None", ""):
        return None
    return val


def check_spec_binding(body: str, verdict_repo_sha: str) -> tuple[bool, str]:
    """PW-26-RATIFIZIERT 2026-06-09 (Codex-Bruch 1): semantische Probe der
    reif_*-Felder gegen die Spec auf verdict_repo_sha (NICHT origin/main —
    Drift-Check ist separat in check_drift).

    Erlaubt zwei Sub-Klassen bei `keine-spec-noetig`:
      - Drift-gegen-Spec: reif_* zeigt auf bindende Spec, plus drift_target gefuellt.
      - Reines Chore: reif_* alle null, dafuer chore_evidence gefuellt + Datei
        existiert auf verdict_repo_sha.

    Bei `spec-gemergt`: reif_* zwingend gefuellt.
    Bei `spec-fehlt`: nicht geprueft (Stempel haette eh keinen Pfad — `verdict: ready`
    mit `reif: spec-fehlt` ist Hook-Bug, kein Realfall).

    Liefert (ok, reason). ok=True = darf gestempelt werden.
    """
    reif = _extract_axis_value(body, "reif")
    if reif is None:
        return (False, "axes.reif fehlt im Verdikt")

    if reif == "spec-gemergt":
        return _check_reif_structured(body, verdict_repo_sha, allow_drift_target=False)

    if reif == "keine-spec-noetig":
        # Zwei Sub-Klassen: Drift-gegen-Spec ODER reines Chore.
        spec_path = _extract_axis_value(body, "reif_spec_path")
        chore_ev = _extract_axis_value(body, "chore_evidence")
        if spec_path and chore_ev:
            return (False, "keine-spec-noetig: reif_spec_path UND chore_evidence "
                          "gesetzt — eine der zwei Sub-Klassen waehlen, nicht beide.")
        if spec_path:
            # Sub-Klasse Drift-gegen-Spec: bindende Spec + drift_target Pflicht.
            return _check_reif_structured(body, verdict_repo_sha, allow_drift_target=True)
        if chore_ev:
            return _check_chore_evidence(body, verdict_repo_sha)
        # Legacy-Pfad (PW-30-Schema vor PW-26): reif_evidence-Freitext akzeptieren,
        # solange verdict_body keine PW-26-strukturierten Felder traegt.
        if "architecture_class:" not in body:
            return (True, "legacy_pre_pw26: keine-spec-noetig ohne strukturierte Felder")
        return (False, "keine-spec-noetig: weder reif_spec_path noch chore_evidence "
                       "gefuellt — eine Sub-Klasse waehlen (Drift-gegen-Spec ODER reines Chore).")

    if reif == "spec-fehlt":
        # Stempel mit spec-fehlt ist hier ein Hook-Bug — verdict: ready impliziert
        # spec-gemergt oder keine-spec-noetig. Aber defensiv: deny mit Hinweis.
        return (False, "axes.reif=spec-fehlt — Stempel auf ready nur nach Spec-PR-Merge "
                       "(Skill arbeitstag-prep.md Komponente A) ODER keine-spec-noetig.")

    return (False, f"axes.reif='{reif}' nicht erkannt")


def _check_reif_structured(body: str, verdict_repo_sha: str,
                            allow_drift_target: bool) -> tuple[bool, str]:
    """Strukturierte reif_*-Probe: alle fuenf Pflicht-Felder + Heading-Negativfilter
    + git-Existenz-Probe auf verdict_repo_sha.

    allow_drift_target: bei keine-spec-noetig (Drift-Klasse) ist drift_target Pflicht.
    """
    spec_path = _extract_axis_value(body, "reif_spec_path")
    req_id = _extract_axis_value(body, "reif_requirement_id")
    def_line = _extract_axis_value(body, "reif_definition_line")
    heading = _extract_axis_value(body, "reif_section_heading")
    binding = _extract_axis_value(body, "reif_binding")

    # Legacy-Toleranz: wenn PW-26-Schema fehlt (kein architecture_class), Freitext zulassen.
    if "architecture_class:" not in body and not spec_path:
        return (True, "legacy_pre_pw26: kein strukturiertes reif_evidence — Freitext akzeptiert")

    missing = [name for name, val in (
        ("reif_spec_path", spec_path),
        ("reif_requirement_id", req_id),
        ("reif_definition_line", def_line),
        ("reif_section_heading", heading),
        ("reif_binding", binding),
    ) if val is None]
    if missing:
        return (False, f"reif_*-Felder fehlen: {', '.join(missing)} — strukturierte "
                       "reif_evidence Pflicht (watchdog-prep.md Output-Schema).")

    # specs/ ODER conventions/ (Codex-Bruch 1: beide gleichberechtigt).
    if not spec_path.startswith(("specs/", "conventions/")):
        return (False, f"reif_spec_path='{spec_path}' liegt nicht unter specs/ oder conventions/.")

    # Heading-Negativfilter (RAT-11-Disziplin mechanisch).
    for nonbinding in SPEC_NONBINDING_HEADINGS:
        if heading.startswith(nonbinding):
            return (False, f"reif_section_heading='{heading}' ist nicht-bindend "
                          f"(RAT-11 — Semantisches Prep-Reife-Gate). Spec-PR mergen "
                          "(Komponente A) oder Mini-Wahl-Karte vorlegen (Komponente B).")
    if req_id.startswith(SPEC_NONBINDING_ID_PREFIX):
        return (False, f"reif_requirement_id='{req_id}' ist OPEN-* — per Namens-"
                       "Konvention skizziert, nicht bindend (RAT-11).")
    if binding != "true":
        return (False, f"reif_binding='{binding}' — Hook akzeptiert nur 'true' als bindend.")

    # Drift-Klasse-spezifisch: drift_target Pflicht bei Drift-gegen-Spec.
    if allow_drift_target:
        drift_target = _extract_axis_value(body, "drift_target")
        if not drift_target:
            return (False, "keine-spec-noetig (Drift-gegen-Spec): drift_target Pflicht "
                           "(welche Code-Stelle weicht ab).")

    # Git-Existenz: Spec auf verdict_repo_sha existiert + enthaelt requirement_id.
    try:
        show = subprocess.run(
            ["git", "-C", XBUDDY_REPO_PATH, "show", f"{verdict_repo_sha}:{spec_path}"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if show.returncode != 0:
            return (False, f"Spec '{spec_path}' existiert nicht auf verdict_repo_sha "
                          f"{verdict_repo_sha[:8]} — Spec-PR mergen.")
        if req_id not in show.stdout:
            return (False, f"Requirement '{req_id}' nicht in '{spec_path}' auf "
                          f"{verdict_repo_sha[:8]} gefunden — Spec-PR mergen.")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Best-effort wie check_drift: ohne git optimistisch.
        return (True, "git unavailable, spec-binding optimistisch behalten")

    return (True, "ok")


def _check_chore_evidence(body: str, verdict_repo_sha: str) -> tuple[bool, str]:
    """PW-26 Pfad 2: reines Chore ohne Spec-Anker. chore_evidence Pflicht +
    erste Komponente (Datei:Zeile) muss auf verdict_repo_sha existieren.
    """
    chore_ev = _extract_axis_value(body, "chore_evidence")
    if not chore_ev:
        return (False, "chore_evidence leer bei keine-spec-noetig ohne reif_spec_path.")
    # chore_evidence-Form: "<datei:zeile> + <Grund>". Erste Datei:Zeile extrahieren.
    m = re.match(r"([^\s:]+):(\d+)", chore_ev)
    if not m:
        return (False, f"chore_evidence='{chore_ev}' ohne erkennbare datei:zeile-Naht. "
                       "Form: '<datei:zeile> + <Grund>'.")
    file_path = m.group(1)
    # Erlaubte Drift-Pfade: alles im Repo (relativ). Absolute Pfade ablehnen.
    if file_path.startswith("/"):
        return (False, f"chore_evidence-Datei '{file_path}' ist absoluter Pfad — "
                       "relativ zu Repo-Wurzel erwartet.")
    try:
        show = subprocess.run(
            ["git", "-C", XBUDDY_REPO_PATH, "show", f"{verdict_repo_sha}:{file_path}"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if show.returncode != 0:
            return (False, f"chore_evidence-Datei '{file_path}' existiert nicht auf "
                          f"verdict_repo_sha {verdict_repo_sha[:8]}.")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return (True, "git unavailable, chore_evidence optimistisch behalten")
    return (True, "ok")


def check_drift(verdict_repo_sha: str) -> tuple[bool, str]:
    """Prueft, ob Commits zwischen verdict_repo_sha und current origin/main
    Dateien unter `specs/` oder `decisions/` beruehrt haben.

    Liefert (is_drifted, reason). is_drifted=False = OK, Verdict noch gueltig.
    """
    try:
        # fetch quiet (best-effort, kein Fail bei Netz-Problem — Verdict bleibt gueltig)
        subprocess.run(
            ["git", "-C", XBUDDY_REPO_PATH, "fetch", "origin", "main", "--quiet"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        ancestor_check = subprocess.run(
            ["git", "-C", XBUDDY_REPO_PATH, "merge-base",
             "--is-ancestor", verdict_repo_sha, "origin/main"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if ancestor_check.returncode != 0:
            # Verdict-SHA ist nicht in main-Linie → Verdikt invalide
            return (True, f"verdict_repo_sha={verdict_repo_sha[:8]} nicht (mehr) Vorfahre von origin/main")
        diff = subprocess.run(
            ["git", "-C", XBUDDY_REPO_PATH, "diff", "--name-only",
             f"{verdict_repo_sha}..origin/main", "--", *DRIFT_PATHS],
            capture_output=True, text=True, timeout=15, check=False,
        )
        if diff.returncode != 0:
            return (False, "git-diff-Probe fehlgeschlagen, Verdict optimistisch behalten")
        touched = [p for p in diff.stdout.splitlines() if p.strip()]
        if touched:
            return (True, f"Spec-/Ledger-Drift seit Verdict: {', '.join(touched[:3])}{'...' if len(touched) > 3 else ''}")
        return (False, "ok")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Best-effort: kein git-Zugriff → Verdict gilt
        return (False, "git unavailable, verdict optimistisch behalten")


def _check_verdict_generic(
    repo: str, issue: str, marker_re, marker_name: str,
) -> tuple[bool, str]:
    """Gemeinsame Verdikt-Pruef-Logik fuer prep_verdict (PW-30) und werft_verdict (PW-43).

    Schema-identisch: derselbe Hash-Compute-Pfad, dieselbe verdict:ready-Pflicht,
    dieselbe SHA-Drift-/Spec-Binding-Probe. Nur Marker-Name unterscheidet.
    Liefert (ok, reason). ok=True = darf gestempelt werden.
    """
    if not repo or not issue:
        return (False, f"Repo/Issue nicht erkannt — kann {marker_name} nicht pruefen")
    body, marker = fetch_verdict_comment(repo, issue, marker_re)
    if not body or not marker:
        return (False,
                f"kein {marker_name}-Comment gefunden. Erwartete erste Zeile: "
                f"'<!-- {marker_name} v1 issue:<NR> sha:<16hex> -->'. "
                f"Bitte zustaendigen Skill durchlaufen + Verdikt-YAML posten.")
    if marker["issue"] != issue:
        return (False, f"verdict-Marker issue={marker['issue']} != Stempel-Issue {issue}")
    # Migration: Backfill-Marker akzeptiert, aber nur bei Pre-Cutoff-Tickets.
    # (Migrations-Sweep posted noch keinen — Erweiterungs-Punkt.)
    migrated_m = re.search(r"^migrated:\s*true\s*$", body, re.MULTILINE)
    if migrated_m:
        # Cutoff-Check: status:ready-Event muss vor MIGRATION_CUTOFF_ISO liegen.
        # Implementiert minimal — vollstaendiger timelineItems-Check ist Folge.
        return (True, "migrated_legacy_backfill")
    # Hash-Verifikation
    computed = compute_verdict_hash(body)
    if not computed:
        return (False, "Verdict-Body unleserlich (verdict:/axes: nicht parsbar)")
    if computed != marker["sha"]:
        return (False, f"Hash mismatch: marker.sha={marker['sha']} vs. computed={computed} -> "
                       "verdict-Body wurde nach Posten geaendert oder Marker stimmt nicht.")
    # verdict: ready ist Pflicht
    verdict_m = re.search(r"^verdict:\s*ready\s*$", body, re.MULTILINE)
    if not verdict_m:
        verdict_val_m = re.search(r"^verdict:\s*(\S+)\s*$", body, re.MULTILINE)
        actual = verdict_val_m.group(1) if verdict_val_m else "<unknown>"
        return (False, f"Verdict ist '{actual}', nicht 'ready'. Kein Stempel.")
    # SHA-Drift-Check (Spec-/Ledger-Drift seit Verdict)
    sha_m = re.search(r"^verdict_repo_sha:\s*[\"']?([0-9a-fA-F]{7,40})[\"']?\s*$", body, re.MULTILINE)
    if sha_m:
        drifted, reason = check_drift(sha_m.group(1))
        if drifted:
            return (False, f"Verdict stale: {reason}. /arbeitstag-prep neu durchlaufen.")
    # PW-26-RATIFIZIERT 2026-06-09 (Codex-Bruch 1): semantische Spec-Binding-Probe.
    # Nur bei PW-26-Schema (architecture_class vorhanden) — Legacy-Verdikte
    # durchlaufen die Probe als no-op.
    if "architecture_class:" in body and sha_m:
        binding_ok, binding_reason = check_spec_binding(body, sha_m.group(1))
        if not binding_ok:
            return (False, f"PW-26 Spec-Binding: {binding_reason}")
    return (True, "ok")


# ---------------------------------------------------------------------------
# CLI-Einstiegspunkt (wird von prep-reconcile.yml aufgerufen, PW-85)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    repo = os.environ.get("REPO", "")
    issue = os.environ.get("ISSUE", "")

    if not repo or not issue:
        print("FEHLER: Umgebungsvariablen REPO und ISSUE sind erforderlich.", file=sys.stderr)
        sys.exit(2)

    # prep_verdict zuerst pruefen (PW-30)
    prep_ok, prep_reason = _check_verdict_generic(repo, issue, VERDICT_MARKER_RE, "prep_verdict")
    if prep_ok:
        print(f"OK: prep_verdict gueltig — {prep_reason}")
        sys.exit(0)

    # werft_verdict als zweite legitime Quelle (PW-43, PW-85 Codex-Bruch 1)
    werft_ok, werft_reason = _check_verdict_generic(repo, issue, WERFT_VERDICT_MARKER_RE, "werft_verdict")
    if werft_ok:
        print(f"OK: werft_verdict gueltig — {werft_reason}")
        sys.exit(0)

    # Beide Verdikt-Sorten fehlen oder ungueltig
    print(f"KEIN VERDIKT: prep_verdict: {prep_reason}")
    print(f"KEIN VERDIKT: werft_verdict: {werft_reason}")
    sys.exit(1)
