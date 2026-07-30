#!/usr/bin/env bash
# create-labels.sh — legt die Labels an, auf denen Lotses Status-Lifecycle läuft.
#
# Nutzung:
#   ./bootstrap/create-labels.sh <owner/repo>
#   ./bootstrap/create-labels.sh "$LOTSE_PROJECT_REPO"
#
# Idempotent: existierende Labels werden aktualisiert, nicht dupliziert.
set -euo pipefail

REPO="${1:-${LOTSE_PROJECT_REPO:-}}"
if [ -z "$REPO" ]; then
  echo "Usage: $0 <owner/repo>   (oder LOTSE_PROJECT_REPO setzen)" >&2
  exit 2
fi
command -v gh >/dev/null || { echo "gh CLI fehlt — https://cli.github.com/" >&2; exit 1; }

# name|color|description
LABELS=(
  "status:spec|c5def5|Ticket hat eine Spec, noch nicht reif"
  "status:spec-in-progress|bfd4f2|Prep-Lauf reift dieses Ticket gerade (transient)"
  "status:ready|0e8a16|Reif — der Mensch hat gestempelt, bereit zum Bau"
  "status:in-progress|fbca04|Wird gerade gebaut (Draft-PR offen)"
  "status:in-review|d93f0b|PR ready-for-review, wartet auf Review/Merge"
  "epic|5319e7|Initiative ohne eigenen status:* — Herzschlag statt Lifecycle"
  "in-werft|1d76db|Werft hält dieses Ticket aktiv (Design-Phase)"
  "type:docs|bfdadc|Spec-/Doku-/Prozess-PR (Refs statt Closes)"
)

echo "Lege Lotse-Labels in $REPO an …"
for row in "${LABELS[@]}"; do
  IFS='|' read -r name color desc <<< "$row"
  if gh label create "$name" --repo "$REPO" --color "$color" --description "$desc" 2>/dev/null; then
    echo "  + $name"
  else
    gh label edit "$name" --repo "$REPO" --color "$color" --description "$desc" >/dev/null
    echo "  ~ $name (aktualisiert)"
  fi
done
echo "✓ Fertig."
