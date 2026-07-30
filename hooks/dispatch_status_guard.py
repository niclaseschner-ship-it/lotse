#!/usr/bin/env python3
"""dispatch_status_guard — PreToolUse-Hook fuer Agent-Dispatch (RAT-15, PW-17).

Liest den Agent-Prompt, sucht parent_ticket: <owner>/<repo>#<nr> und prueft
per gh issue view, ob das Ticket auf status:in-progress steht. Wenn nicht
(oder kein parent_ticket vorhanden), wird der Dispatch mit permissionDecision
deny geblockt.

Begruendung: RAT-10/RECON-3 verbietet jedem Agent (auch dem Orchestrator) das
per-Shell-Setzen von status:*-Labels. Der ratifizierte Pfad (RAT-15) ist ein
leerer Draft-PR-at-pick, der ticket-status-flow.yml triggert. Dieser Hook ist
die negative Versicherung: ohne durchgefuehrte Mechanik kein Subagent-Dispatch.

Schema folgt cynthra_fence.py: stdin-JSON, permissionDecision-Antwort.

Verhalten:
  - kein parent_ticket im Prompt          -> deny (kein Bypass, Codex-R2-Befund)
  - parent_ticket ohne <owner>/<repo>#    -> deny (Repo-Marker Pflicht)
  - gh issue view scheitert               -> deny (kein blindes Durchlassen)
  - status:in-progress vorhanden          -> exit 0 (durchlassen)
  - status:ready                          -> deny (Claim-PR fehlt)
  - status:closed                         -> deny (Bug im Orchestrator)
  - andere status:* (in-review, blocked)  -> deny (Track sollte nicht starten)
"""
import json
import os
import re
import subprocess
import sys

# Pattern erfasst owner/repo#nr fuer parent_ticket.
PARENT_RE = re.compile(r"parent_ticket:\s*([A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+)#(\d+)")
# PW-54 V1 (2026-06-16 RATIFIZIERT; ENTSCHEID-File 20260616-1715-RATIFIZIERT-
# pw54-werft-mockup-anker.md Sektion "Konvergenz/Brueche/Reparatur" →
# "(B) stat()-Existenz-Check"): Werft setzt werft_mockup_path bei UI-Bau-
# Uebergaben. Hook stat()et den Pfad vor Dispatch — mechanische Mindestform
# statt Self-Attest. /tmp/- oder brainstorm/-Pfade sind verboten.
# Regex erfasst Wert (quoted/unquoted), Inline-YAML-Kommentar wird abgestreift.
# Codex-Pass-2-Befund: vorher matchte unquoted+Kommentar als ein Wert; quoted+
# Kommentar matchte gar nicht. Loesung: Wert greift bis vor # oder Zeilenende.
WERFT_MOCKUP_PATH_RE = re.compile(
    r"""^\s*werft_mockup_path:\s*
        (?:
            "(?P<quoted_dq>[^"]*)"
            |'(?P<quoted_sq>[^']*)'
            |(?P<unquoted>[^#\n\r]*?)
        )
        \s*(?:\#.*)?$""",
    re.MULTILINE | re.VERBOSE,
)
XBUDDY_REPO_ROOT = os.environ.get("LOTSE_PROJECT_ROOT") or os.environ.get("XBUDDY_REPO") or os.getcwd()
# PW-54 V1: Form-Pflicht — Pfad muss unter specs/mockups/ liegen und .html enden.
# (ENTSCHEID-File Sektion "(A) Mockup-Heimat ins xbuddy-Repo".)
MOCKUP_REQUIRED_PREFIX = "specs/mockups/"
MOCKUP_REQUIRED_SUFFIX = ".html"

# Skip-Marker fuer bewusste no-ticket-Dispatches (z. B. berater-runde-Spawns).
# PW-23-haerte (2026-06-09): muss erste nicht-leere Zeile des Prompts sein.
# Vorher: `in prompt` → jeder Prompt mit beilaeufig zitiertem Marker durchgewunken
# (Skill-Dateien und Vorschlags-Files zitieren den Marker haeufig).
SKIP_MARKER = "<!-- dispatch_status_guard:skip -->"

# PW-31 (xbuddy-prozess#30, 2026-06-09): Sub-Agent Contract Pflicht.
# Jeder Subagent-Prompt muss einen YAML-Schicht-2-Block tragen mit:
# - contract_kind: subagent  (Standard, mit parent_ticket)
# - contract_kind: subagent_no_ticket  (bewusster no-ticket-Pfad, mit SKIP_MARKER)
# Plus mode-Pflichtfeld aus {read, propose, build, formalize}.
# Schema: ~/.claude/contracts/schemas.md §2.
CONTRACT_KIND_RE = re.compile(r"^\s*contract_kind:\s*(subagent_no_ticket|subagent)\b", re.MULTILINE)
MODE_RE = re.compile(r"^\s*mode:\s*(read|propose|build|formalize)\b", re.MULTILINE)


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        # Nicht parsbares stdin -> nicht blockieren (defensiv wie cynthra_fence).
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Task", "Agent"):
        # Hook ist nur fuer Subagent-Dispatch zustaendig.
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    prompt = tool_input.get("prompt", "")
    if not isinstance(prompt, str):
        sys.exit(0)

    # PW-31: Mode-Feld ist Pflicht in JEDEM Subagent-Prompt (auch im Skip-Pfad).
    # Bestimmt Output-Sorte (handoff/read_report/proposal) und Scope.
    mode_match = MODE_RE.search(prompt)
    if not mode_match:
        deny(
            "PW-31: mode:-Feld fehlt im Subagent-Prompt. "
            "Erlaubte Werte: read | propose | build | formalize. "
            "Setze mode: build fuer arbeitstag-Subagenten, mode: read fuer reine "
            "Bestand-Aufgaben (R1 in /berater-runde), mode: propose fuer "
            "Loesungs-Vorschlaege (R2), mode: formalize fuer Spec-/Convention-Entwuerfe. "
            "Schema: ~/.claude/contracts/schemas.md §2."
        )

    # PW-31: contract_kind ist Pflicht — entweder subagent (mit parent_ticket)
    # oder subagent_no_ticket (mit SKIP_MARKER als erster Zeile).
    contract_match = CONTRACT_KIND_RE.search(prompt)
    if not contract_match:
        deny(
            "PW-31: contract_kind: subagent oder contract_kind: subagent_no_ticket "
            "fehlt im Prompt. Schicht-2-Block ist Pflicht (Sub-Agent Contract, "
            "siehe ~/.claude/contracts/schemas.md §2)."
        )
    contract_kind = contract_match.group(1)

    # PW-54 V1: werft_mockup_path-Existenz-Check.
    mockup_match = WERFT_MOCKUP_PATH_RE.search(prompt)
    if mockup_match:
        raw = (
            mockup_match.group("quoted_dq")
            or mockup_match.group("quoted_sq")
            or mockup_match.group("unquoted")
            or ""
        )
        mockup_path = raw.strip()
        # Leere/null/none-Werte werden als "nicht gesetzt" interpretiert.
        if mockup_path and mockup_path.lower() not in ("none", "null"):
            # /tmp/- oder brainstorm/-Pfade sind verboten (decisions/README.md:15-20).
            if mockup_path.startswith(("/tmp/", os.path.expanduser("~/brainstorm/"), "brainstorm/")):
                deny(
                    f"PW-54: werft_mockup_path zeigt auf nicht-durable Heimat "
                    f"({mockup_path}). Mockups muessen ins xbuddy-Repo nach "
                    f"{MOCKUP_REQUIRED_PREFIX}<slug>/ persistiert sein "
                    f"(werft.md F3-Ende, decisions/README.md:15-20)."
                )
            # Absolute Pfade: nur erlaubt, wenn unter xbuddy-Repo-Root. realpath
            # gegen Symlink-Tricks.
            if os.path.isabs(mockup_path):
                if not mockup_path.startswith(XBUDDY_REPO_ROOT + os.sep):
                    deny(
                        f"PW-54: werft_mockup_path absolut, aber ausserhalb "
                        f"xbuddy-Repo: {mockup_path}."
                    )
                check_path = mockup_path
                rel_path = mockup_path[len(XBUDDY_REPO_ROOT) + 1:]
            else:
                check_path = os.path.join(XBUDDY_REPO_ROOT, mockup_path)
                rel_path = mockup_path
            # Form-Pflicht: unter specs/mockups/ + .html.
            if not rel_path.startswith(MOCKUP_REQUIRED_PREFIX):
                deny(
                    f"PW-54: werft_mockup_path muss unter {MOCKUP_REQUIRED_PREFIX} "
                    f"liegen (angegeben: {mockup_path}). Werft-F3-Ende kopiert "
                    f"Mockup nach specs/mockups/<slug>/."
                )
            if not rel_path.endswith(MOCKUP_REQUIRED_SUFFIX):
                deny(
                    f"PW-54: werft_mockup_path muss auf {MOCKUP_REQUIRED_SUFFIX} "
                    f"enden (angegeben: {mockup_path}). Mockup ist Gate-B-HTML-"
                    f"Artefakt, kein Verzeichnis."
                )
            # realpath gegen Symlink-Ausbruch
            try:
                real_check = os.path.realpath(check_path)
                real_root = os.path.realpath(XBUDDY_REPO_ROOT) + os.sep
                if not real_check.startswith(real_root):
                    deny(
                        f"PW-54: werft_mockup_path realpath verlaesst xbuddy-Repo "
                        f"({real_check}). Symlink-Ausbruch nicht erlaubt."
                    )
            except OSError:
                pass
            if not os.path.exists(check_path):
                deny(
                    f"PW-54: werft_mockup_path existiert nicht: {check_path} "
                    f"(angegeben als {mockup_path}). Werft-F3-Ende soll Mockup "
                    f"nach specs/mockups/<slug>/ kopieren."
                )

    is_skip_path = prompt.lstrip().startswith(SKIP_MARKER)

    if is_skip_path:
        # Skip-Pfad: braucht eigenen Mini-Contract (subagent_no_ticket).
        # Schliesst die heutige Berater-Spawn-Luecke (vor PW-31: Skip umging
        # jegliche Vertragsform). Berater-Modes: read | propose | formalize,
        # niemals build.
        if contract_kind != "subagent_no_ticket":
            deny(
                "PW-31: Skip-Pfad braucht contract_kind: subagent_no_ticket "
                "(nicht subagent). Skip ist explizit der no-ticket-Pfad fuer "
                "/berater-runde-Spawns. Doku-Anker: berater-runde.md#dispatch-skip."
            )
        if mode_match.group(1) == "build":
            deny(
                "PW-31: Skip-Pfad (subagent_no_ticket) erlaubt mode: build NICHT. "
                "build erfordert parent_ticket (arbeitstag-Track). Nutze "
                "mode: read | propose | formalize fuer no-ticket-Dispatches."
            )
        sys.exit(0)

    # Standard-Pfad: parent_ticket + status:in-progress Pflicht.
    match = PARENT_RE.search(prompt)
    if not match:
        deny(
            "RAT-15: Agent-Dispatch ohne parent_ticket: <owner>/<repo>#<nr>. "
            "Setze parent_ticket im Schicht-3-Block oder markiere bewusst "
            "<!-- dispatch_status_guard:skip --> ALS ERSTE ZEILE des Prompts "
            "(no-ticket-Dispatch, Doku-Anker: berater-runde.md#dispatch-skip). "
            "Marker mitten im Text reicht nicht."
        )

    repo = match.group(1)
    issue = match.group(2)
    track_mode = mode_match.group(1)

    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue, "--repo", repo,
             "--json", "labels,state"],
            capture_output=True, text=True, timeout=15, check=False,
        )
    except subprocess.TimeoutExpired:
        deny(f"RAT-15: gh issue view {repo}#{issue} Timeout (>15s). "
             "Netz/Auth pruefen; Dispatch geblockt.")
        return  # unreachable, defensiv

    if result.returncode != 0:
        deny(
            f"RAT-15: gh issue view {repo}#{issue} fehlgeschlagen "
            f"(rc={result.returncode}). stderr: {result.stderr.strip()[:200]}"
        )

    try:
        view = json.loads(result.stdout)
    except json.JSONDecodeError:
        deny(f"RAT-15: gh issue view {repo}#{issue} lieferte kein JSON.")
        return  # unreachable

    state = view.get("state", "").upper()
    if state == "CLOSED":
        deny(
            f"RAT-15: Issue {repo}#{issue} ist CLOSED. "
            "Subagent-Dispatch auf geschlossenes Ticket = Orchestrator-Bug."
        )

    labels = {lbl.get("name", "") for lbl in (view.get("labels") or [])}

    # PW-33 (2026-06-09): Mode-aware Lifecycle-Check.
    # - mode: build         → status:in-progress Pflicht (RAT-15, Claim-PR-at-pick).
    # - mode: read|propose|formalize → status:spec-in-progress (PW-33-Lock)
    #                                  ODER status:in-progress akzeptiert.
    #                                  Lock-Semantik: prep claimt das Ticket vor Dispatch.
    if track_mode == "build":
        if "status:in-progress" in labels:
            sys.exit(0)
        status_labels = sorted(lbl for lbl in labels if lbl.startswith("status:"))
        current = ", ".join(status_labels) or "<keiner>"
        deny(
            f"RAT-15: Issue {repo}#{issue} hat status:in-progress NICHT "
            f"(aktuell: {current}). Claim-PR-at-pick-Schritt fehlt. "
            "Vor Dispatch: leerer Draft-PR mit Closes #<nr> (siehe "
            "arbeitstag.md CONTRACT-FIRST FLOW / Claim-PR-at-pick)."
        )
    else:
        # read | propose | formalize
        if "status:spec-in-progress" in labels or "status:in-progress" in labels:
            sys.exit(0)
        status_labels = sorted(lbl for lbl in labels if lbl.startswith("status:"))
        current = ", ".join(status_labels) or "<keiner>"
        deny(
            f"PW-33: Issue {repo}#{issue} hat weder status:spec-in-progress noch "
            f"status:in-progress (aktuell: {current}). "
            f"Fuer mode: {track_mode}-Dispatch muss vorher das Ticket geclaimt werden "
            f"(arbeitstag-prep.md: -status:spec +status:spec-in-progress per Skip-Marker)."
        )


if __name__ == "__main__":
    main()
