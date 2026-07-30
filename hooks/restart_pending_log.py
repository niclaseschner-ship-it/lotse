#!/usr/bin/env python3
"""restart_pending_log — PostToolUse-Hook fuer Bash-Calls, die `git pull` machen.

REFERENCE-OPS (projekt-spezifisch, KEIN Framework-Kern): mappt geaenderte Pfade
auf systemd-Service-Restarts eines konkreten Deploy-Modells. Fuer ein Fremd-
Projekt anpassen oder aus dem settings-Wiring weglassen — siehe SETUP.md.

Erkennt `git pull origin main` im Projekt-Repo, extrahiert die SHA-Range aus
stdout, zieht die geaenderten Pfade per `git log <pre>..<post> --name-only` und
mappt sie DATENGETRIEBEN gegen eine Projekt-Mappingtabelle (Pfad-Prefix ->
Restart-Befehl). Das Framework selbst kennt KEINE Service-Namen — die stehen
ausschliesslich in der Projekt-Tabelle (Default `deploy/systemd/README.md`, per
ENV `LOTSE_RESTART_MAPPING` umstellbar). Ein Prefix darf auf mehrere Befehle
zeigen (mehrere Tabellenzeilen mit demselben Prefix).

Output: ${CLAUDE_HOME}/logs/restart_pending.jsonl mit {ts, services,
commit_range, changed_paths, restart_done: false}.

Kein automatischer Restart (sudo-Antipattern in Hooks). Nur Sichtbarkeits-Log,
damit Orchestrator/Betreiber VOR dem naechsten Live-Test den richtigen Restart
ausfuehrt.

Default-Sicherheit: kennt die Mapping-Tabelle einen Pfad nicht, gibt es keinen
Log-Entry fuer den Pfad — nicht falsch-positiv warnen.
"""
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime

LOG_PATH = os.path.join(
    os.environ.get("CLAUDE_HOME", os.path.expanduser("~/.claude")),
    "logs",
    "restart_pending.jsonl",
)
PROJECT_ROOT = os.environ.get("LOTSE_PROJECT_ROOT") or os.environ.get("XBUDDY_REPO") or os.getcwd()
# Mapping-Tabelle (Pfad-Prefix -> Restart-Befehl) des Betreiberprojekts. Default
# folgt dem Referenz-Deploy-Modell; per ENV auf beliebige Datei umstellbar.
MAPPING_FILE = os.environ.get("LOTSE_RESTART_MAPPING") or os.path.join(PROJECT_ROOT, "deploy/systemd/README.md")

# Pattern: erkennt `git pull origin main` (mit oder ohne `-C <repo>` oder cwd-Wechsel).
GIT_PULL_RE = re.compile(
    r"\bgit\s+(?:-C\s+(\S+)\s+)?pull(?:\s+origin\s+main)?\b"
)
# SHA-Range aus stdout: "abc1234..def5678  main       -> origin/main"
SHA_RANGE_RE = re.compile(r"\b([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\b")
# Repo-Indikator aus dem Pull-Output ("From github.com:<owner>/<repo>").
# Cleanup laeuft evtl. im Projekt-CWD ohne -C/Pfad — Indikator kommt aus stdout.
# Slug aus LOTSE_PROJECT_REPO; unbekannt → jeder github-Remote matcht.
_project_slug = os.environ.get("LOTSE_PROJECT_REPO", "").strip()
PROJECT_REMOTE_RE = re.compile(
    rf"From\s+github\.com[:/]{re.escape(_project_slug)}\b" if _project_slug
    else r"From\s+github\.com[:/]\S+"
)
# Markdown-Tabellen-Zeile: | `pfad/` ... | `sudo systemctl restart svc` |
# Wir extrahieren nur den ersten Backtick-Pfad und den restart-Befehl.
MAPPING_ROW_RE = re.compile(
    r"^\|\s*`([^`]+?)`[^|]*\|\s*`(sudo\s+(?:systemctl\s+restart|nginx\s+-t)[^`]+)`",
    re.MULTILINE,
)


def load_mapping():
    """Parse Mapping-Tabelle aus MAPPING_FILE. Returns list of
    (path_prefix, restart_cmd) tuples. Bei Fehler: leere Liste (Default-
    Sicherheit, kein false-positive)."""
    try:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []
    rows = []
    for m in MAPPING_ROW_RE.finditer(content):
        path_token = m.group(1).strip()
        cmd = m.group(2).strip()
        rows.append((path_token, cmd))
    return rows


def services_for_paths(changed_paths, mapping):
    """Map changed_paths against mapping. Returns set of restart_cmd strings.

    Rein datengetrieben: die Zuordnung Pfad-Prefix -> Restart-Befehl kommt
    VOLLSTAENDIG aus der Projekt-Mappingtabelle (load_mapping). Das Framework
    kennt selbst KEINE Service-Namen. Ein Pfad-Prefix darf auf MEHRERE Befehle
    zeigen (mehrere Tabellenzeilen mit demselben Prefix) — dann werden alle
    zugehoerigen Services eingesammelt. Ein Projekt, dessen Datenmodell bei
    einem Repo-Touch mehrere Instanzen neu starten muss (z. B. eine Basis- plus
    pro-Instanz-Services), traegt dafuer schlicht mehrere Zeilen mit demselben
    Prefix ein.
    """
    services = set()
    for path in changed_paths:
        for path_token, cmd in mapping:
            # path_token kann ein reiner Prefix ("router/") oder eine Datei
            # ("deploy/nginx/origin.conf") sein, evtl. mit erklaerndem Suffix
            # hinter einem Space. Wir matchen den Prefix.
            clean_token = path_token.split(" ")[0]
            if path == clean_token or path.startswith(clean_token):
                services.add(cmd)
    return services


def log_entry(services, commit_range, changed_paths, raw_command):
    """Append entry to JSONL. Best-effort."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "services": sorted(services),
            "commit_range": commit_range,
            "changed_paths": sorted(changed_paths),
            "restart_done": False,
            "raw_command": raw_command[:200],
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command", "")
    if not isinstance(command, str):
        sys.exit(0)

    pull_match = GIT_PULL_RE.search(command)
    if not pull_match:
        sys.exit(0)

    # stdout zuerst extrahieren — wird sowohl fuer Repo-Indikator als auch
    # fuer SHA-Range gebraucht.
    response = data.get("tool_response") or ""
    stdout = ""
    if isinstance(response, str):
        stdout = response
    elif isinstance(response, dict):
        stdout = response.get("stdout", "") or response.get("output", "")
    elif isinstance(response, list):
        stdout = "\n".join(str(x) for x in response)

    # Pruefen, ob der Pull im Projekt-Repo war — drei Pfade:
    #   1) -C <projekt-pfad>  → explizit
    #   2) Command enthaelt PROJECT_ROOT  → cd ${LOTSE_PROJECT_ROOT} && git pull
    #   3) stdout enthaelt "From github.com:<owner>/<repo>"  → Operator im
    #      Projekt-CWD ohne -C oder cd (arbeitstag-Cleanup-Fall).
    repo_arg = pull_match.group(1)
    is_project_pull = False
    if (repo_arg and os.path.abspath(repo_arg).startswith(PROJECT_ROOT)) or PROJECT_ROOT in command or PROJECT_REMOTE_RE.search(stdout):
        is_project_pull = True

    if not is_project_pull:
        sys.exit(0)

    sha_match = SHA_RANGE_RE.search(stdout)
    if not sha_match:
        # Kein Range → entweder schon up-to-date oder Fehler. Nicht loggen.
        sys.exit(0)
    pre_sha, post_sha = sha_match.group(1), sha_match.group(2)

    # Diff-Pfade ziehen.
    try:
        result = subprocess.run(
            ["git", "-C", PROJECT_ROOT, "log",
             f"{pre_sha}..{post_sha}", "--name-only", "--pretty=format:"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except Exception:
        sys.exit(0)

    if result.returncode != 0:
        sys.exit(0)

    changed_paths = sorted({
        line.strip() for line in result.stdout.splitlines() if line.strip()
    })

    if not changed_paths:
        sys.exit(0)

    mapping = load_mapping()
    if not mapping:
        # SSoT-Lese-Fehler oder Tabelle leer → kein Log (Default-Sicherheit).
        sys.exit(0)

    services = services_for_paths(changed_paths, mapping)
    if not services:
        # Kein gemapptes Service betroffen → kein Log.
        sys.exit(0)

    log_entry(services, f"{pre_sha}..{post_sha}", changed_paths, command)
    sys.exit(0)


if __name__ == "__main__":
    main()
