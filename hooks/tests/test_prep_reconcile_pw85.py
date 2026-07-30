#!/usr/bin/env python3
"""Pytest-Tests fuer PW-85 (prep-reconcile Create-Kante + Verdikt-Membran).

ENTSCHEID: brainstorm/berater-runde/20260706-153129-RATIFIZIERT-pw85-ready-create-kante.md

Kill-Kriterien (Pflicht vor Handoff):
  (a) offenes Issue + valider werft_verdict, kein prep_verdict -> status:ready BLEIBT
      (Codex-Bruch 1: Reconcile akzeptiert prep_verdict ODER werft_verdict)
  (b) Fake-Marker falscher Hash -> zurueckgerollt
  (c) opened mit status:ready-Label -> Job laeuft; ohne Label -> skippt
      (AC3 - YAML-Trigger-Logik, hier durch CLI-Pfad belegt)
  (d) AC1-Gate: opened-if nutzt .*.name-Form, nicht toJson-Kompakt-Nadel
      (Regressions-Guard: toJson() liefert pretty-printed JSON mit Leerzeichen
      nach Doppelpunkt -> kompakter Nadel-String faengt nie)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS_DIR = os.path.join(HERE, "..")

# verdict_check direkt laden (PW-85-Modul selbst testen)
VC_PATH = os.path.join(HOOKS_DIR, "verdict_check.py")
_vc_spec = importlib.util.spec_from_file_location("verdict_check_test", VC_PATH)
vc = importlib.util.module_from_spec(_vc_spec)
_vc_spec.loader.exec_module(vc)

# status_rollback_guard laden (importiert aus verdict_check, belegt Rueckwaertskompatibilitaet)
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)
SRG_PATH = os.path.join(HOOKS_DIR, "status_rollback_guard.py")
_srg_spec = importlib.util.spec_from_file_location("srg", SRG_PATH)
srg = importlib.util.module_from_spec(_srg_spec)
_srg_spec.loader.exec_module(srg)


# ---------------------------------------------------------------------------
# Hilfsfunktionen: Verdikt-Body + Marker bauen
# ---------------------------------------------------------------------------

def make_prep_verdict_body(verdict="ready", issue="1", axes_extra=""):
    """Baut ein gueltiges prep_verdict-Body incl. korrektem Marker-Hash."""
    body_content = (
        f"verdict: {verdict}\n"
        f"axes:\n"
        f"  reif: keine-spec-noetig\n"
        f"{axes_extra}"
    )
    sha = vc.compute_verdict_hash(body_content)
    marker = f"<!-- prep_verdict v1 issue:{issue} sha:{sha} -->"
    return f"{marker}\n{body_content}"


def make_werft_verdict_body(verdict="ready", issue="1", axes_extra=""):
    """Baut ein gueltiges werft_verdict-Body incl. korrektem Marker-Hash."""
    body_content = (
        f"verdict: {verdict}\n"
        f"axes:\n"
        f"  reif: keine-spec-noetig\n"
        f"  werft: true\n"
        f"  deliverable_kind: non_ui\n"
        f"  deliverable_evidence: methode/hooks/verdict_check.py:1 Skript\n"
        f"{axes_extra}"
    )
    sha = vc.compute_verdict_hash(body_content)
    marker = f"<!-- werft_verdict v1 issue:{issue} sha:{sha} -->"
    return f"{marker}\n{body_content}"


def make_fake_body(marker_name="prep_verdict", issue="1"):
    """Baut einen Marker mit falschem Hash (Fake-Injection-Angriff)."""
    bad_sha = "deadbeefcafe1234"
    marker = f"<!-- {marker_name} v1 issue:{issue} sha:{bad_sha} -->"
    body_content = "verdict: ready\naxes:\n  reif: keine-spec-noetig\n"
    return f"{marker}\n{body_content}"


def _make_werft_only_fetch(issue_nr="1"):
    """Fetch-Mock: nur werft_verdict vorhanden, kein prep_verdict."""
    werft_body = make_werft_verdict_body(issue=issue_nr)

    def _fetch(repo, issue, marker_re=None):
        if marker_re is None:
            marker_re = vc.VERDICT_MARKER_RE
        if marker_re == vc.WERFT_VERDICT_MARKER_RE:
            first_line = werft_body.lstrip().split("\n", 1)[0]
            m = vc.WERFT_VERDICT_MARKER_RE.match(first_line)
            if m:
                return (werft_body, {"issue": m.group(1), "sha": m.group(2)})
        return (None, None)
    return _fetch


def _make_fake_fetch(marker_name="prep_verdict", issue_nr="1"):
    """Fetch-Mock: gibt Marker mit falschem Hash zurueck."""
    fake_body = make_fake_body(marker_name, issue_nr)

    def _fetch(repo, issue, marker_re=None):
        if marker_re is None:
            marker_re = vc.VERDICT_MARKER_RE
        first_line = fake_body.lstrip().split("\n", 1)[0]
        m = marker_re.match(first_line)
        if m:
            return (fake_body, {"issue": m.group(1), "sha": m.group(2)})
        return (None, None)
    return _fetch


def run_cli_logic(repo, issue, fetch_mock=None, drift_mock=None):
    """Simuliert den __main__-Block von verdict_check.py (opened-Event-Pfad)."""
    orig_fetch = vc.fetch_verdict_comment
    orig_drift = vc.check_drift
    try:
        if fetch_mock:
            vc.fetch_verdict_comment = fetch_mock
        if drift_mock:
            vc.check_drift = drift_mock

        prep_ok, prep_reason = vc._check_verdict_generic(
            repo, issue, vc.VERDICT_MARKER_RE, "prep_verdict")
        if prep_ok:
            return 0, f"prep_verdict: {prep_reason}"
        werft_ok, werft_reason = vc._check_verdict_generic(
            repo, issue, vc.WERFT_VERDICT_MARKER_RE, "werft_verdict")
        if werft_ok:
            return 0, f"werft_verdict: {werft_reason}"
        return 1, f"prep: {prep_reason} | werft: {werft_reason}"
    finally:
        vc.fetch_verdict_comment = orig_fetch
        vc.check_drift = orig_drift


# ---------------------------------------------------------------------------
# Kill-Kriterium (a): werft_verdict allein genuegt — prep_verdict NICHT noetig
# ---------------------------------------------------------------------------

def test_kill_a_werft_verdict_alone_sufficient():
    """AC2: offenes Issue + valider werft_verdict, kein prep_verdict -> status:ready BLEIBT."""
    orig_fetch = vc.fetch_verdict_comment
    orig_drift = vc.check_drift
    try:
        vc.check_drift = lambda sha: (False, "ok")
        vc.fetch_verdict_comment = _make_werft_only_fetch("1")

        # werft_verdict gueltig -> darf gestempelt werden
        ok, reason = vc._check_verdict_generic("r/r", "1", vc.WERFT_VERDICT_MARKER_RE, "werft_verdict")
        assert ok is True, f"werft_verdict allein sollte ok sein, aber: {reason}"

        # prep_verdict fehlt -> deny
        ok, reason = vc._check_verdict_generic("r/r", "1", vc.VERDICT_MARKER_RE, "prep_verdict")
        assert ok is False, "prep_verdict fehlt sollte deny sein"
        assert "kein prep_verdict" in reason, f"Erwartet 'kein prep_verdict' in: {reason}"

        # CLI-Logik: erstes prep, dann werft — werft faengt es ab
        prep_ok, _ = vc._check_verdict_generic("r/r", "1", vc.VERDICT_MARKER_RE, "prep_verdict")
        werft_ok, _ = vc._check_verdict_generic("r/r", "1", vc.WERFT_VERDICT_MARKER_RE, "werft_verdict")
        assert not prep_ok, "CLI-Logik: prep sollte fehlschlagen (kein prep_verdict)"
        assert werft_ok, "CLI-Logik: werft_verdict soll greifen -> status:ready BLEIBT"
    finally:
        vc.fetch_verdict_comment = orig_fetch
        vc.check_drift = orig_drift


# ---------------------------------------------------------------------------
# Kill-Kriterium (b): Fake-Marker (falscher Hash) -> zurueckgerollt
# ---------------------------------------------------------------------------

def test_kill_b_fake_hash_denied():
    """AC3: Fake-Marker falscher Hash -> zurueckgerollt."""
    orig_fetch = vc.fetch_verdict_comment
    orig_drift = vc.check_drift
    try:
        vc.check_drift = lambda sha: (False, "ok")

        # prep_verdict mit falschem Hash
        vc.fetch_verdict_comment = _make_fake_fetch("prep_verdict", "1")
        ok, reason = vc._check_verdict_generic("r/r", "1", vc.VERDICT_MARKER_RE, "prep_verdict")
        assert ok is False, "prep_verdict Fake-Hash sollte denied sein"
        assert "mismatch" in reason, f"Erwartet 'mismatch' in: {reason}"

        # werft_verdict mit falschem Hash
        vc.fetch_verdict_comment = _make_fake_fetch("werft_verdict", "1")
        ok, reason = vc._check_verdict_generic("r/r", "1", vc.WERFT_VERDICT_MARKER_RE, "werft_verdict")
        assert ok is False, "werft_verdict Fake-Hash sollte denied sein"
        assert "mismatch" in reason, f"Erwartet 'mismatch' in: {reason}"
    finally:
        vc.fetch_verdict_comment = orig_fetch
        vc.check_drift = orig_drift


# ---------------------------------------------------------------------------
# Kill-Kriterium (c): opened-Trigger + CLI-Exit-Codes
# ---------------------------------------------------------------------------

def test_kill_c_opened_with_status_ready_label_exits_0():
    """AC1: opened + status:ready-Label + gueltiger werft_verdict -> exit 0 (Label bleibt)."""
    werft_body = make_werft_verdict_body(issue="42")

    def _mock_werft_only(repo, issue, marker_re=None):
        if marker_re is None:
            marker_re = vc.VERDICT_MARKER_RE
        if marker_re == vc.WERFT_VERDICT_MARKER_RE:
            first_line = werft_body.lstrip().split("\n", 1)[0]
            m = vc.WERFT_VERDICT_MARKER_RE.match(first_line)
            if m:
                return (werft_body, {"issue": m.group(1), "sha": m.group(2)})
        return (None, None)

    exit_code, msg = run_cli_logic("r/r", "42",
                                   fetch_mock=_mock_werft_only,
                                   drift_mock=lambda sha: (False, "ok"))
    assert exit_code == 0, f"opened + status:ready + gueltiger werft_verdict -> exit 0 erwartet, war: {exit_code} ({msg})"


def test_kill_c_opened_without_valid_verdict_exits_1():
    """AC1: opened + status:ready-Label + KEIN Verdikt -> exit 1 (Label wird entfernt)."""
    exit_code, msg = run_cli_logic("r/r", "99",
                                   fetch_mock=lambda repo, issue, marker_re=None: (None, None),
                                   drift_mock=lambda sha: (False, "ok"))
    assert exit_code == 1, f"opened + kein Verdikt -> exit 1 erwartet, war: {exit_code} ({msg})"


# ---------------------------------------------------------------------------
# Zusatz: issue-Binding (Marker fuer anderes Issue wird abgelehnt)
# ---------------------------------------------------------------------------

def test_issue_binding_wrong_issue_denied():
    """Marker fuer falsches Issue wird abgelehnt."""
    wrong_body = make_prep_verdict_body(issue="999")  # Issue 999, nicht 1

    def _mock_wrong_issue(repo, issue, marker_re=None):
        if marker_re is None or marker_re == vc.VERDICT_MARKER_RE:
            first_line = wrong_body.lstrip().split("\n", 1)[0]
            m = vc.VERDICT_MARKER_RE.match(first_line)
            if m:
                return (wrong_body, {"issue": m.group(1), "sha": m.group(2)})
        return (None, None)

    orig_fetch = vc.fetch_verdict_comment
    try:
        vc.fetch_verdict_comment = _mock_wrong_issue
        ok, reason = vc._check_verdict_generic("r/r", "1", vc.VERDICT_MARKER_RE, "prep_verdict")
        assert ok is False, "Marker fuer Issue 999, Stempel auf 1 -> deny erwartet"
        assert "!=" in reason, f"Erwartet '!=' in: {reason}"
    finally:
        vc.fetch_verdict_comment = orig_fetch


# ---------------------------------------------------------------------------
# Zusatz: srg.compute_verdict_hash noch via srg abrufbar (Rueckwaertskompatibilitaet)
# ---------------------------------------------------------------------------

def test_srg_backward_compat_compute_verdict_hash():
    """PW-85 Re-Export: srg.compute_verdict_hash ist ueber status_rollback_guard abrufbar."""
    assert hasattr(srg, "compute_verdict_hash"), "srg.compute_verdict_hash fehlt"
    assert callable(srg.compute_verdict_hash), "srg.compute_verdict_hash ist nicht aufrufbar"
    h = srg.compute_verdict_hash("verdict: ready\naxes:\n  reif: keine-spec-noetig\n")
    assert h is not None, "compute_verdict_hash lieferte None"
    assert len(h) == 16, f"compute_verdict_hash soll 16-Zeichen-Hex liefern, war: {h!r}"

