#!/usr/bin/env python3
"""Fixtures fuer PW-82 (prep Body-Entscheidungs-Filter) + PW-83 (werft
deliverable_kind/werft_mockup_path am F5-Stempel).

ENTSCHEID: brainstorm/berater-runde/20260703-232716-RATIFIZIERT-membran-gate-am-akt.md
Prueft genau die dort formulierten Kill-Kriterien. gh-abhaengige Funktionen werden
gemockt (offline lauffaehig). Aufruf: python3 test_membran_gate_pw82_pw83.py
"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "..", "status_rollback_guard.py")
spec = importlib.util.spec_from_file_location("srg", GUARD)
srg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srg)

fails = []
def check(name, cond):
    print(f"[{'OK' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


# ---------- PW-82: Body-Entscheidungs-Filter ----------
def werft_verdict_stub(body):
    """Baut ein prep_verdict-Body-Fragment mit gegebenem body_decision."""
    return body

# Kill-Kriterium: Body mit Marker + verdict OHNE body_decision:geloest -> deny.
srg.fetch_issue_body = lambda repo, issue: "Nächster Schritt: /berater-runde zur Sicht-Frage."
ok, reason = srg.check_prep_body_decision("r", "1", "axes:\n  body_decision: offen\n")
check("PW-82 Marker + body_decision:offen -> deny", ok is False and "PW-82" in reason)

ok, reason = srg.check_prep_body_decision("r", "1", "axes:\n  reif: spec-gemergt\n")  # Feld fehlt
check("PW-82 Marker + body_decision fehlt -> deny", ok is False)

ok, reason = srg.check_prep_body_decision("r", "1", "axes:\n  body_decision: geloest\n")
check("PW-82 Marker + body_decision:geloest -> allow", ok is True)

# Marker-ABWESENHEIT ist kein Freibrief, aber der HOOK prueft nur den Positiv-Fall:
srg.fetch_issue_body = lambda repo, issue: "Ganz normales Ticket ohne offene Entscheidung."
ok, reason = srg.check_prep_body_decision("r", "1", "axes:\n  body_decision: kein-marker\n")
check("PW-82 kein Marker -> allow (Boden, nicht Decke)", ok is True and "kein Body" in reason)

# Body nicht lesbar -> optimistisch (Watchdog-Urteil traegt).
srg.fetch_issue_body = lambda repo, issue: None
ok, _ = srg.check_prep_body_decision("r", "1", "axes:\n  body_decision: offen\n")
check("PW-82 Body unlesbar -> optimistisch allow", ok is True)


# ---------- PW-83: werft_mockup_path-Formprobe ----------
with tempfile.TemporaryDirectory() as tmp:
    srg.XBUDDY_REPO_ROOT = tmp
    mockdir = os.path.join(tmp, "specs", "mockups", "demo")
    os.makedirs(mockdir)
    real = os.path.join(mockdir, "variante-b.html")
    with open(real, "w") as fh:
        fh.write("<html></html>")

    ok, _ = srg.validate_werft_mockup_path_value("specs/mockups/demo/variante-b.html")
    check("PW-83 gueltiger Mockup-Pfad -> ok", ok is True)

    ok, _ = srg.validate_werft_mockup_path_value("specs/mockups/demo/fehlt.html")
    check("PW-83 nicht-existent -> deny", ok is False)

    ok, _ = srg.validate_werft_mockup_path_value("/tmp/x.html")
    check("PW-83 /tmp/-Pfad -> deny", ok is False)

    ok, _ = srg.validate_werft_mockup_path_value("specs/other/demo.html")
    check("PW-83 falscher Prefix -> deny", ok is False)

    ok, _ = srg.validate_werft_mockup_path_value("specs/mockups/demo/variante-b")
    check("PW-83 kein .html-Suffix -> deny", ok is False)


# ---------- PW-83: deliverable_kind-Logik in check_werft_verdict ----------
def run_werft(axes_body):
    """Mockt _check_verdict_generic + fetch_verdict_comment, testet nur die
    PW-83-Zweige nach werft:true."""
    srg._check_verdict_generic = lambda repo, issue, mre, mn: (True, "ok")
    full = "<!-- werft_verdict v1 issue:1 sha:0000000000000000 -->\nverdict: ready\naxes:\n" + axes_body
    srg.fetch_verdict_comment = lambda repo, issue, mre=None: (full, {"issue": "1", "sha": "x"})
    return srg.check_werft_verdict("r", "1")

with tempfile.TemporaryDirectory() as tmp:
    srg.XBUDDY_REPO_ROOT = tmp
    mockdir = os.path.join(tmp, "specs", "mockups", "demo")
    os.makedirs(mockdir)
    with open(os.path.join(mockdir, "v.html"), "w") as fh:
        fh.write("x")

    ok, _ = run_werft("  werft: true\n  deliverable_kind: ui_build\n  werft_mockup_path: specs/mockups/demo/v.html\n")
    check("PW-83 ui_build + gueltiges Mockup -> allow", ok is True)

    ok, r = run_werft("  werft: true\n  deliverable_kind: ui_build\n")
    check("PW-83 ui_build ohne werft_mockup_path -> deny", ok is False and "werft_mockup_path fehlt" in r)

    ok, r = run_werft("  werft: true\n")
    check("PW-83 deliverable_kind fehlt -> deny", ok is False and "deliverable_kind fehlt" in r)

    # Kill-Kriterium (Codex): non_ui ohne Evidenz -> deny.
    ok, r = run_werft("  werft: true\n  deliverable_kind: non_ui\n")
    check("PW-83 non_ui ohne deliverable_evidence -> deny", ok is False and "deliverable_evidence" in r)

    ok, _ = run_werft("  werft: true\n  deliverable_kind: non_ui\n  deliverable_evidence: hoerspiel.py:88 kein UI\n")
    check("PW-83 non_ui + Evidenz -> allow", ok is True)


# ---------- Kill-Kriterium: deliverable_kind geht in den Hash ----------
h_ui = srg.compute_verdict_hash("verdict: ready\narchitecture_class: nachzeichnen\naxes:\n  werft: true\n  deliverable_kind: ui_build\n")
h_non = srg.compute_verdict_hash("verdict: ready\narchitecture_class: nachzeichnen\naxes:\n  werft: true\n  deliverable_kind: non_ui\n")
check("PW-83 Hash aendert sich bei deliverable_kind-Flip", h_ui is not None and h_ui != h_non)


print()
if fails:
    print(f"ROT — {len(fails)} Fehlschlag/Fehlschlaege: {fails}")
    sys.exit(1)
print("GRÜN — alle Kill-Kriterien erfuellt")
