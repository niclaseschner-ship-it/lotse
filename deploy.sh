#!/usr/bin/env bash
# deploy.sh — deployt die Lotse-Glue (agents/ commands/ contracts/ hooks/) aus
# diesem Repo an den Laufzeit-Ort, den der Agenten-Harness liest (Default
# ~/.claude/). Repo = Source of Truth (Edit + Review + CI-Sicht),
# Laufzeit-Ort = Deploy-Ziel.
#
# Quelle ist IMMER ein git-Objekt-Ref (`git archive`), NIE der Working Tree —
# objektbasiert und immun gegen Branch-Wechsel im Checkout. Der Deploy ist
# ADDITIV (kein `rsync --delete`): aus der Quelle entfernte Dateien müssen am
# Laufzeit-Ort von Hand gelöscht werden (der Drift-Wächter meldet „neu/geändert",
# nicht „entfernt bleibt liegen").
#
# Nutzung:
#   deploy.sh [--source-ref <sha|branch>] [--dry-run] [--verify-only]
#
#   --source-ref REF   Quelle. Default: origin/main.
#   --dry-run          Zeigt, was sich änderte, ohne zu schreiben.
#   --verify-only      Schreibt nichts; vergleicht den Laufzeit-Ort gegen den
#                      Ref (sha256) und meldet Drift.
#
# Konfiguration (Env-Vars, optional):
#   CLAUDE_HOME   Laufzeit-Ort / Deploy-Ziel (Default: ~/.claude)
set -euo pipefail

# Quell-Repo = das Repo, in dem dieses Skript liegt (branch-flip-immun via Objekt-Ref).
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$SELF_DIR" rev-parse --show-toplevel)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
SORTEN=(agents commands contracts hooks)
SOURCE_REF="origin/main"
DRY_RUN=0
VERIFY_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --source-ref) SOURCE_REF="$2"; shift 2;;
    --dry-run)    DRY_RUN=1; shift;;
    --verify-only) VERIFY_ONLY=1; shift;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "Unbekanntes Argument: $1" >&2; exit 2;;
  esac
done

command -v git >/dev/null || { echo "git fehlt" >&2; exit 1; }

# Bei Remote-Ref aktuell halten (lokale Refs/SHAs unangetastet lassen).
if printf '%s' "$SOURCE_REF" | grep -q '^origin/'; then
  git -C "$REPO" fetch origin --quiet
fi

# Prüfen, dass der Ref die Glue-Ordner trägt.
if ! git -C "$REPO" cat-file -e "${SOURCE_REF}:commands" 2>/dev/null; then
  echo "FEHLER: '${SOURCE_REF}' trägt kein commands/ — falscher Ref?" >&2
  exit 1
fi

# Die vier Glue-Ordner aus dem Objekt-Tree des Ref extrahieren (NICHT Working Tree).
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git -C "$REPO" archive "$SOURCE_REF" "${SORTEN[@]}" | tar -x -C "$TMP"
SRC="$TMP"

sha() { sha256sum "$1" | cut -d' ' -f1; }

drift=0
changed=0
for sorte in "${SORTEN[@]}"; do
  [ -d "$SRC/$sorte" ] || continue
  while IFS= read -r -d '' f; do
    rel="${f#"$SRC/$sorte/"}"
    target="$DEST/$sorte/$rel"
    if [ ! -f "$target" ]; then
      echo "  [NEU]    $sorte/$rel"
      changed=1; drift=1
    elif [ "$(sha "$f")" != "$(sha "$target")" ]; then
      echo "  [DIFF]   $sorte/$rel"
      changed=1; drift=1
    fi
  done < <(find "$SRC/$sorte" -type f -print0)
done

if [ "$VERIFY_ONLY" -eq 1 ]; then
  if [ "$drift" -eq 1 ]; then
    echo "✗ DRIFT: $DEST weicht von ${SOURCE_REF} ab (s.o.)." >&2
    exit 1
  fi
  echo "✓ Kein Drift: $DEST == ${SOURCE_REF} (alle Sorten)."
  exit 0
fi

if [ "$changed" -eq 0 ]; then
  echo "✓ Bereits aktuell — nichts zu deployen (${SOURCE_REF})."
  exit 0
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "(dry-run) — obige Änderungen würden nach $DEST/ geschrieben."
  exit 0
fi

for sorte in "${SORTEN[@]}"; do
  [ -d "$SRC/$sorte" ] || continue
  mkdir -p "$DEST/$sorte"
  rsync -a --checksum "$SRC/$sorte/" "$DEST/$sorte/"
done
# Hooks ausführbar halten.
chmod +x "$DEST"/hooks/*.py 2>/dev/null || true
echo "✓ Deployed ${SOURCE_REF} → $DEST/ ($(printf '%s ' "${SORTEN[@]}"))."
