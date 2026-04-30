#!/bin/bash
# iReview config loader — pure bash, no python dependency
CONFIG=".ireview.json"

if [ -f "$CONFIG" ]; then
  MODEL=$(grep -o '"model"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG" 2>/dev/null | head -1 | grep -o '"[^"]*"$' | tr -d '"')
  AUTO=$(grep -q '"auto_review"[[:space:]]*:[[:space:]]*true' "$CONFIG" 2>/dev/null && echo "on" || echo "off")
  echo "## [iReview] ${MODEL:-unknown} | auto-review: $AUTO"

  # Check unresolved findings
  if [ -d ".ireview/reviews" ]; then
    REVIEWS=$(ls .ireview/reviews/*.json 2>/dev/null | wc -l | tr -d ' ')
    [ "$REVIEWS" -gt 0 ] && echo "Previous reviews: $REVIEWS (run /ireview:status)"
  fi
else
  echo "## [iReview] No config. Run /ireview:setup"
fi
