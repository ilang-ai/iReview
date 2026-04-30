#!/bin/bash
# iReview config loader — runs on session start

CONFIG=".ireview.json"

if [ -f "$CONFIG" ]; then
  echo "## [iReview] Config loaded"
  MODEL=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('model','unknown'))" 2>/dev/null)
  AUTO=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('auto_review', False))" 2>/dev/null)
  echo "Model: $MODEL | Auto-review: $AUTO"

  # Check for unresolved reviews
  if [ -d ".ireview/reviews" ]; then
    UNRESOLVED=$(ls .ireview/reviews/*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNRESOLVED" -gt 0 ]; then
      echo "Unresolved reviews: $UNRESOLVED (see .ireview/reviews/)"
    fi
  fi
else
  echo "## [iReview] No config found"
  echo "Run: cp .ireview.example.json .ireview.json"
  echo "Then edit model and api_key."
fi
