#!/bin/bash
# iReview stop gate — lightweight check, blocks stop if review needed
# Exit 0 = allow stop, Exit 2 = block stop for review

CONFIG=".ireview.json"
STATE_DIR=".ireview"
STATE_FILE="$STATE_DIR/state.json"

# No config = no review
if [ ! -f "$CONFIG" ]; then
  exit 0
fi

# Check auto_review flag
AUTO=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG'))
    print(c.get('auto_review', False))
except:
    print(False)
" 2>/dev/null)

if [ "$AUTO" != "True" ]; then
  exit 0
fi

# Check for git changes
CHANGED=$(git diff HEAD --name-only 2>/dev/null | head -1)
if [ -z "$CHANGED" ]; then
  exit 0
fi

# Changes found + auto_review on → block stop for review
mkdir -p "$STATE_DIR"
cat > "$STATE_FILE" << EOF
{
  "status": "pending",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "files_changed": $(git diff HEAD --name-only 2>/dev/null | wc -l | tr -d ' ')
}
EOF

exit 2
