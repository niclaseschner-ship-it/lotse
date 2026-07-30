#!/usr/bin/env python3
"""handoff_check — PostToolUse-Hook fuer Subagent-Output-Verifikation (PW-32, xbuddy-prozess#32, 2026-06-09).

Liest tool_response von Task/Agent-Calls und prueft mode-abhaengig, ob die
erwartete Vertrags-Sorte als YAML-Block enthalten ist:

- mode: build       → contract_kind: handoff erwartet. Fehlt → handoff_missing.
- mode: read        → contract_kind: handoff NICHT erwartet.
                      Wenn doch da → handoff_in_read_mode (PW-29-R1-Bruch-Klasse).
- mode: propose     → Presence-Check: irgendwo im Output muss MINDESTENS ein
                      Grep-Treffer `Datei:Zeile` ODER eine markierte Ableitung
                      `(Ableitung aus PW-N/REQ-N, nicht gegript)` vorkommen.
                      Fehlt komplett → propose_without_beleg (PW-10 V2). Der
                      Hook erkennt KEINE Per-Statement-Belege und KEINE
                      Ableitung-als-Entscheidungsgrund-Brüche — das fängt der
                      Antiberater (vgl. berater.md Pflicht-Reflex 1).
- mode: formalize   → kein Output-Schema in dieser Welle.

Stop-Hooks koennen nicht hart blockieren — daher Soft-Warning ueber
~/.claude/logs/handoff_misses.jsonl. /arbeitstag-Retro liest die letzten N
Eintraege und macht sie als Sektion „Handoff-Luecken" sichtbar.

Whitelist EXPECTED_BY_MODE ist die Erweiterungs-Stelle: Folge-Welle
read_report/proposal-Schemata = eine Zeile.

Schema: ~/.claude/contracts/schemas.md §2 (mode), §3 (handoff).
"""
import json
import os
import re
import sys
from datetime import UTC, datetime

LOG_PATH = os.path.join(
    os.environ.get("CLAUDE_HOME", os.path.expanduser("~/.claude")),
    "logs",
    "handoff_misses.jsonl",
)
EXCERPT_LEN = 200

MODE_RE = re.compile(r"^\s*mode:\s*(read|propose|build|formalize)\b", re.MULTILINE)
PARENT_RE = re.compile(r"parent_ticket:\s*([A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+#\d+)")
HANDOFF_RE = re.compile(r"^\s*contract_kind:\s*handoff\b", re.MULTILINE)
# PW-52/PW-58-Fall-3a (2026-06-17 RATIFIZIERT; ENTSCHEID-File
# 20260617-2330-RATIFIZIERT-pw58-pw52-disziplin-mechanik-katalog.md Sektion
# "R2-Empfehlung -> Fall 3"): Handoff-Inhalt muss als LETZTER yaml-Fence-Block
# erscheinen (schemas.md:160-164 + :536-545 "Handoff-Fence als letzten Block").
# Wir extrahieren ALLE ```ya?ml ... ```-Bloecke (yaml-Fence kann ` enthalten,
# deshalb non-greedy ohne [^`]-Klassen) und pruefen ob der LETZTE einen
# contract_kind: handoff traegt.
YAML_FENCE_RE = re.compile(
    r"```ya?ml\s*\n(.*?)\n\s*```",
    re.DOTALL,
)
HANDOFF_IN_FENCE_RE = re.compile(r"^\s*contract_kind:\s*handoff\b", re.MULTILINE)


def has_handoff_as_last_yaml_fence(response_str: str) -> bool:
    """True wenn der LETZTE yaml-Fence in response_str contract_kind: handoff
    traegt UND nach diesem Fence keine substantielle Prosa mehr kommt.
    Codex-Pass-2-Befund: 'irgendwo' reichte nicht — Spec verlangt 'letzter
    inhaltlicher Block' (schemas.md:160-164). Schwelle: <50 Zeichen Tail-Prosa
    sind ok (z.B. Abschluss-Zeilen, Whitespace)."""
    matches = list(YAML_FENCE_RE.finditer(response_str))
    if not matches:
        return False
    last_match = matches[-1]
    if not HANDOFF_IN_FENCE_RE.search(last_match.group(1)):
        return False
    tail = response_str[last_match.end():].strip()
    return not len(tail) > 50
# PW-54 V1 (2026-06-16 RATIFIZIERT; ENTSCHEID-File 20260616-1715-RATIFIZIERT-
# pw54-werft-mockup-anker.md Sektion "Konvergenz/Brueche/Reparatur" →
# "(C) mockup_visual_probe-Slot"): Wenn werft_mockup_path im Subagent-Prompt
# stand (Werft-UI-Bau-Track), MUSS der Output mockup_visual_probe tragen.
# Soft-Warning ins Log; Hard-Reject ist Sache des Antiberater-Pass-2.
WERFT_MOCKUP_PATH_PROMPT_RE = re.compile(
    r"""^\s*werft_mockup_path:\s*
        (?:
            "(?P<quoted_dq>[^"]*)"
            |'(?P<quoted_sq>[^']*)'
            |(?P<unquoted>[^#\n\r]*?)
        )
        \s*(?:\#.*)?$""",
    re.MULTILINE | re.VERBOSE,
)
# Codex-Pass-2-Befund: Wort-Presence reicht nicht — leerer Block "mockup_visual_probe: {}"
# passte durch. Wir erzwingen beide Pflicht-Sub-Keys mit nicht-leerem Wert.
VISUAL_PROBE_URL_RE = re.compile(r"\bprobe_url\s*:\s*[^\s{},\"']+|\bprobe_url\s*:\s*[\"'][^\"']+[\"']")
VISUAL_PROBE_SHOT_RE = re.compile(r"\bprobe_screenshot_path\s*:\s*[^\s{},\"']+|\bprobe_screenshot_path\s*:\s*[\"'][^\"']+[\"']")
# PW-10 V2 — ENTSCHEID-File (2026-06-16-RATIFIZIERT-pw10-r1-belege-vs-
# ableitung) Sektion „Konvergenz/Brueche/Reparatur" → „Patch A (Mechanik)".
# Presence-Check fuer mode:propose-Output. Stille = Bruch. Es muss
# MINDESTENS EIN Marker im gesamten Response auftauchen — entweder ein Grep-
# Treffer als `<pfad-mit-punkt-oder-slash>:<zeile>` in Backticks ODER eine
# als-Ableitung-Markierung in der vorgeschriebenen Pflicht-Form
# `(Ableitung aus <ID>, nicht gegript)`. Per-Statement-Pruefung ist NICHT
# Aufgabe des Hooks (das macht der Antiberater) — vgl. ENTSCHEID-File
# Sektion „Konvergenz/Brueche/Reparatur" → „R2-Begruendung Doppelmechanik".
# Bekannte Limitierungen (akzeptiert): Extension-lose Datei-Namen wie
# `Makefile:12` ohne Punkt/Slash fallen durch — selten in xbuddy-Konsumenten,
# fuer den Bedarf akzeptabel.
BELEG_RE = re.compile(
    r"`[^`]*[./][^`]*:\d+`"
    r"|\(Ableitung aus [A-Z]{2,8}-\d+[A-Za-z]*, nicht gegript\)"
)

# Whitelist: was wird pro mode erwartet?
# None = kein Output-Schema in dieser Welle definiert → kein Check.
EXPECTED_BY_MODE = {
    "build": "handoff",
    "read": None,
    "propose": "belege",  # PW-10 V2, 2026-06-16
    "formalize": None,
}


def log_miss(klass: str, mode: str, parent_ticket: str, response_excerpt: str) -> None:
    """Schreibt einen Eintrag in handoff_misses.jsonl. Best-effort, kein Fail."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "class": klass,
            "mode": mode,
            "parent_ticket": parent_ticket,
            "response_excerpt": response_excerpt,
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Hook bleibt non-blocking auch bei Disk-Fail


def extract_excerpt(response) -> str:
    """Erste/letzte EXCERPT_LEN Zeichen des Subagent-Outputs, robust gegen
    verschachtelte Strukturen."""
    if isinstance(response, str):
        text = response
    else:
        try:
            text = json.dumps(response, ensure_ascii=False)[:4000]
        except Exception:
            text = str(response)[:4000]
    if len(text) <= 2 * EXCERPT_LEN:
        return text
    return text[:EXCERPT_LEN] + " ... " + text[-EXCERPT_LEN:]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name", "") not in ("Task", "Agent"):
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    prompt = tool_input.get("prompt", "")
    if not isinstance(prompt, str):
        sys.exit(0)

    mode_match = MODE_RE.search(prompt)
    if not mode_match:
        # PW-31-Hook (PreToolUse) hat das schon gefangen — wenn wir hier sind,
        # ist der Dispatch durchgegangen, also bestand vermutlich Skip-Marker
        # oder anderer Pfad ohne mode. Stillschweigend zurueck.
        sys.exit(0)
    mode = mode_match.group(1)
    expected = EXPECTED_BY_MODE.get(mode)
    if expected is None and mode not in EXPECTED_BY_MODE:
        # Unbekannter mode-Wert — Whitelist-Defense.
        log_miss("unknown_mode_in_post_check", mode, "<unknown>", "")
        sys.exit(0)

    parent_match = PARENT_RE.search(prompt)
    parent_ticket = parent_match.group(1) if parent_match else "<no-ticket>"

    response = data.get("tool_response") or ""
    response_str = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
    has_handoff = bool(HANDOFF_RE.search(response_str))

    if expected == "handoff":
        if not has_handoff:
            log_miss("handoff_missing", mode, parent_ticket, extract_excerpt(response))
        elif not has_handoff_as_last_yaml_fence(response_str):
            # PW-52/PW-58-Fall-3a: Inhalt da, aber NICHT als letzter yaml-Fence
            # (entweder gar kein Fence, oder Fence ist nicht der letzte
            # inhaltliche Block, oder mehrere Fences und der letzte enthaelt
            # contract_kind: handoff nicht).
            log_miss("fence_missing", mode, parent_ticket, extract_excerpt(response))
    elif expected == "belege" and not BELEG_RE.search(response_str):
        # PW-10 V2: propose-Output ohne Bestands-Belege (Grep-Treffer ODER
        # markierte Ableitung). Soft-Warning, /berater-runde-Retro liest mit.
        log_miss("propose_without_beleg", mode, parent_ticket, extract_excerpt(response))
    elif expected is None and has_handoff and mode == "read":
        # PW-29-R1-Klasse: Berater im read-Modus hat Loesungs-/Handoff-Form geliefert.
        log_miss("handoff_in_read_mode", mode, parent_ticket, extract_excerpt(response))

    # PW-54 V1: werft_mockup_path im Prompt → mockup_visual_probe-Pflicht-Sub-Keys
    # (probe_url + probe_screenshot_path) im Output. Wort-Presence reicht nicht
    # (Codex-Pass-2-Befund: "mockup_visual_probe: {}" wuerde sonst durchgehen).
    mockup_in_prompt = WERFT_MOCKUP_PATH_PROMPT_RE.search(prompt)
    if mockup_in_prompt:
        raw = (
            mockup_in_prompt.group("quoted_dq")
            or mockup_in_prompt.group("quoted_sq")
            or mockup_in_prompt.group("unquoted")
            or ""
        )
        mockup_path = raw.strip()
        if mockup_path and mockup_path.lower() not in ("none", "null"):
            has_url = bool(VISUAL_PROBE_URL_RE.search(response_str))
            has_shot = bool(VISUAL_PROBE_SHOT_RE.search(response_str))
            if not (has_url and has_shot):
                log_miss("mockup_visual_probe_missing", mode, parent_ticket, extract_excerpt(response))

    # PW-7 RATIFIZIERT 2026-06-21: Blast-Radius-Whitelist-Extension-Check.
    # Erster Cross-Block-Branch — Parsing zweier YAML-Subblöcke statt Regex auf
    # Top-Level. Wenn analysis_plan.blast_radius_probe.whitelist_delta.additional_files
    # non-empty UND Top-Level files_changed enthaelt Pfade aus dieser Liste
    # OHNE dass Whitelist im Orchestrator-Re-Dispatch erweitert wurde → Miss.
    # Pflicht-Sub-Keys nicht-leer (Codex-Pass-2-Pattern: leerer Block darf nicht
    # durchgehen, analog mockup_visual_probe_missing).
    try:
        wl_delta_m = re.search(
            r"^\s*whitelist_delta:\s*\n\s*additional_files:\s*\[(.+?)\]",
            response_str,
            re.MULTILINE | re.DOTALL,
        )
        if wl_delta_m:
            raw_files = wl_delta_m.group(1)
            # einfacher Parse: kommagetrennte quoted strings
            delta_files = [
                m.group(1) for m in re.finditer(r"['\"]([^'\"]+)['\"]", raw_files)
            ]
            if delta_files:
                # files_changed Top-Level parsen (YAML-Liste oder JSON-Array)
                fc_block = re.search(
                    r"^files_changed:\s*\n((?:\s*-\s*.+\n?)+)",
                    response_str,
                    re.MULTILINE,
                )
                if fc_block:
                    changed_files = [
                        m.group(1).strip()
                        for m in re.finditer(r"-\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fc_block.group(1), re.MULTILINE)
                    ]
                    overlap = set(delta_files) & set(changed_files)
                    if overlap:
                        # Heuristik: wenn whitelist_delta.additional_files ⊆ files_changed
                        # gemerged wurde OHNE Re-Dispatch-Confirm, ist es ein Miss.
                        # Confirm-Marker: "whitelist_extended_by_orchestrator: true"
                        # (Operator-Skill setzt diesen im Re-Dispatch-Brief).
                        confirmed = bool(
                            re.search(
                                r"^whitelist_extended_by_orchestrator:\s*true",
                                response_str,
                                re.MULTILINE,
                            )
                        )
                        if not confirmed:
                            log_miss(
                                "whitelist_extension_unaddressed",
                                mode,
                                parent_ticket,
                                extract_excerpt(response),
                            )
    except (re.error, AttributeError):
        # Best-effort: bei Parsing-Fehler kein Miss loggen (Soft-Pattern)
        pass

    # PW-7 RATIFIZIERT 2026-06-21: combined-Trigger-Check.
    # Bei mode: combined ist blast_radius_probe Top-Level + triggerbasiert.
    # Wenn files_changed Hinweise auf Trigger enthält (config.example.json,
    # deploy/, *.service, *.tpl, *.conf) UND blast_radius_probe fehlt oder
    # "not_applicable" sagt → Miss mit Trigger-Vermerk.
    if mode == "combined":
        try:
            fc_block = re.search(
                r"^files_changed:\s*\n((?:\s*-\s*.+\n?)+)",
                response_str,
                re.MULTILINE,
            )
            if fc_block:
                fc_text = fc_block.group(1)
                trigger_patterns = [
                    (r"config\.example\.json", "default_change"),
                    (r"deploy/", "deploy_config_touch"),
                    (r"\.service\b", "deploy_config_touch"),
                    (r"\.tpl\b", "deploy_config_touch"),
                    (r"nginx.*\.conf\b", "deploy_config_touch"),
                ]
                triggers_hit = [
                    name for pat, name in trigger_patterns if re.search(pat, fc_text)
                ]
                if triggers_hit:
                    has_probe = bool(
                        re.search(
                            r"^blast_radius_probe:\s*(?:'?\"?not_applicable\"?'?|\n\s*trigger:)",
                            response_str,
                            re.MULTILINE,
                        )
                    )
                    if not has_probe:
                        log_miss(
                            "blast_radius_probe_missing_with_trigger",
                            mode,
                            parent_ticket,
                            extract_excerpt(response),
                        )
        except (re.error, AttributeError):
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
