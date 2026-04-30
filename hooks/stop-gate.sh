#!/bin/bash
# iReview stop gate — lightweight, fast, deterministic
# Exit 0 = allow stop | Exit 2 = block stop (message via stderr)
set -uo pipefail

CONFIG=".ireview.json"
STATE_DIR=".ireview"
STATE_FILE="$STATE_DIR/state.json"

# Not a git repo → allow
git rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

# No config → allow
[ -f "$CONFIG" ] || exit 0

# Check auto_review (pure bash, no python)
grep -q '"auto_review"[[:space:]]*:[[:space:]]*true' "$CONFIG" 2>/dev/null || exit 0

# Check for changes (tracked + staged)
CHANGED=$(git diff HEAD --name-only 2>/dev/null | wc -l | tr -d ' ')
[ "$CHANGED" -eq 0 ] && exit 0

# Compute diff hash
DIFF_HASH=$(git diff HEAD 2>/dev/null | sha256sum | awk '{print $1}')

# Check if this exact diff was already reviewed and passed
if [ -f "$STATE_FILE" ]; then
  PREV_HASH=$(grep -o '"diff_hash"[[:space:]]*:[[:space:]]*"[^"]*"' "$STATE_FILE" 2>/dev/null | grep -o '"[^"]*"$' | tr -d '"')
  PREV_PHASE=$(grep -o '"phase"[[:space:]]*:[[:space:]]*"[^"]*"' "$STATE_FILE" 2>/dev/null | grep -o '"[^"]*"$' | tr -d '"')

  # Same diff already passed → allow stop
  if [ "$PREV_HASH" = "$DIFF_HASH" ] && [ "$PREV_PHASE" = "passed" ]; then
    exit 0
  fi

  # Same diff already reviewing or cancelled → allow stop
  if [ "$PREV_HASH" = "$DIFF_HASH" ] && [ "$PREV_PHASE" = "cancelled" ]; then
    exit 0
  fi
fi

# Block stop — write state atomically
mkdir -p "$STATE_DIR"
TMP=$(mktemp)
cat > "$TMP" << EOF
{
  "phase": "requested",
  "diff_hash": "$DIFF_HASH",
  "files_changed": $CHANGED,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
mv "$TMP" "$STATE_FILE"

# Tell Claude what to do
echo "iReview: $CHANGED files changed. Run /ireview:review before stopping, or /ireview:cancel to skip." >&2
exit 2
