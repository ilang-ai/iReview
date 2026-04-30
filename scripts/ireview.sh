#!/usr/bin/env bash
set -euo pipefail

STATE_DIR=".ireview"
STATE_FILE="$STATE_DIR/state.json"
REVIEWS_DIR="$STATE_DIR/reviews"
CONFIG=".ireview.json"

mkdir -p "$STATE_DIR" "$REVIEWS_DIR"

get_diff_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    git diff HEAD 2>/dev/null | sha256sum | awk '{print $1}'
  else
    git diff HEAD 2>/dev/null | shasum -a 256 | awk '{print $1}'
  fi
}

cmd_cancel() {
  CURRENT_HASH="$(get_diff_hash)"
  cat > "$STATE_FILE" << EOF
{
  "phase": "cancelled",
  "diff_hash": "$CURRENT_HASH",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
  echo "iReview cancelled for current diff."
}

cmd_status() {
  if [ -f "$STATE_FILE" ]; then
    cat "$STATE_FILE"
  else
    echo '{"phase": "none"}'
  fi
}

cmd_result() {
  LATEST="$(ls -t "$REVIEWS_DIR"/*.json 2>/dev/null | head -1)"
  if [ -n "$LATEST" ]; then
    cat "$LATEST"
  else
    echo "No reviews found."
  fi
}

cmd_review() {
  local config="$CONFIG"
  local mode="standard"
  local diff_target="HEAD"
  local files=""
  
  # Parse arguments
  while [ $# -gt 0 ]; do
    case "$1" in
      --config) config="$2"; shift 2 ;;
      --full) mode="thorough"; shift ;;
      --base) diff_target="$2"; shift 2 ;;
      --adversarial) mode="adversarial"; shift ;;
      *) files="$files $1"; shift ;;
    esac
  done

  if [ ! -f "$config" ]; then
    echo "Error: config file $config not found. Run /ireview:setup" >&2
    exit 1
  fi

  # Build diff
  local diff_file="$STATE_DIR/tmp/current.diff"
  mkdir -p "$STATE_DIR/tmp"

  # Read exclude patterns from config
  local exclude_args=""
  if command -v python3 >/dev/null 2>&1; then
    exclude_args="$(python3 -c "
import json
with open('$config') as f:
    c = json.load(f)
for p in c.get('exclude', []):
    print(f':(exclude){p}')
" 2>/dev/null || true)"
  fi

  if [ -n "$files" ]; then
    git diff "$diff_target" -- $files > "$diff_file" 2>/dev/null
  elif [ -n "$exclude_args" ]; then
    eval git diff "$diff_target" -- . $exclude_args > "$diff_file" 2>/dev/null
  else
    git diff "$diff_target" > "$diff_file" 2>/dev/null
  fi

  local diff_lines
  diff_lines="$(wc -l < "$diff_file" | tr -d ' ')"

  if [ "$diff_lines" -eq 0 ]; then
    echo "No changes to review."
    exit 0
  fi

  # Diff size protection
  local max_chars=100000
  if command -v python3 >/dev/null 2>&1; then
    max_chars="$(python3 -c "import json; print(json.load(open('$config')).get('max_diff_chars', 100000))" 2>/dev/null || echo 100000)"
  fi
  local diff_chars
  diff_chars="$(wc -c < "$diff_file" | tr -d ' ')"

  if [ "$diff_chars" -gt "$max_chars" ]; then
    echo "Warning: diff is ${diff_chars} chars (limit: ${max_chars}). Truncating to file summary." >&2
    git diff "$diff_target" --stat > "$diff_file"
    echo "" >> "$diff_file"
    echo "# Full diff too large (${diff_chars} chars). Showing stat summary only." >> "$diff_file"
  fi

  # Call API
  local script_dir
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  python3 "$script_dir/call-api.py" \
    --config "$config" \
    --mode "$mode" \
    --diff-file "$diff_file"

  local exit_code=$?

  # Update state
  local review_id
  review_id="$(date -u +%Y%m%d-%H%M%S)"
  CURRENT_HASH="$(get_diff_hash)"

  if [ $exit_code -eq 0 ]; then
    cat > "$STATE_FILE" << EOF
{
  "phase": "passed",
  "diff_hash": "$CURRENT_HASH",
  "review_id": "$review_id",
  "mode": "$mode",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
  fi

  return $exit_code
}

# Main dispatcher
case "${1:-help}" in
  review)   shift; cmd_review "$@" ;;
  cancel)   cmd_cancel ;;
  status)   cmd_status ;;
  result)   cmd_result ;;
  *)        echo "Usage: ireview.sh {review|cancel|status|result}" ;;
esac
