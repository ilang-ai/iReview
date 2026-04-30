---
name: ireview
description: Universal AI-to-AI code review using external models for Claude Code outputs
version: 0.1.0
author: ilang-ai
license: MIT
tags:
  - code-review
  - ai-to-ai
  - multi-model
  - security
  - quality
---

# iReview

::GENE{ireview|v:0.1|spec:ilang-v3.0}
  T:review_with_external_model
  T:any_openai_compatible_api
  T:report_real_issues_only
  T:persist_findings_to_disk
  T:track_multi_round_resolution
  A:review_style_issues⇒noise
  A:review_without_changes⇒skip
  A:block_stop_on_lgtm⇒annoying
  A:hand_write_json_in_curl⇒use_script_instead

## How It Works

1. User says "review my code" or runs `/ireview:review`
2. AI gets the diff via `git diff HEAD`
3. AI saves diff to temp file
4. AI runs the API script:

```bash
git diff HEAD > /tmp/ireview-diff.txt
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py \
  --config .ireview.json \
  --mode standard \
  --diff-file /tmp/ireview-diff.txt
```

5. Script outputs JSON to stdout with findings
6. AI parses findings, saves to `.ireview/reviews/`, presents to user

## NEVER do this

Do NOT construct JSON payloads manually with curl. Diffs contain quotes, backslashes, newlines — manual JSON will break. Always use `scripts/call-api.py`.

## Config

`.ireview.json` in project root. See `/ireview:setup` for interactive creation.

## Review Modes

**Standard** (`--mode standard`): Find real bugs, security holes, logic errors.

**Adversarial** (`--mode adversarial`): Challenge design decisions, question assumptions, probe failure modes.

## Diff Size

The script auto-truncates diffs over `max_diff_chars` (default 100K chars). For very large changes, review file-by-file instead of full diff.

## Multi-Round Tracking

When running follow-up reviews:
1. Read latest review from `.ireview/reviews/`
2. Check if previous findings were addressed (files/lines changed)
3. Mark findings as resolved/still_open/new

## State Management

`.ireview/state.json` tracks current review phase:
- `requested` — stop gate detected changes, waiting for review
- `passed` — review completed, no critical issues
- `failed` — review completed, critical issues found
- `cancelled` — user skipped review

Stop gate uses `diff_hash` to prevent re-reviewing the same changes.

## Output

Save every review to `.ireview/reviews/YYYYMMDD-HHMMSS.json`:

```json
{
  "review_id": "20260430-153012",
  "model": "deepseek-chat",
  "mode": "standard",
  "diff_hash": "abc123...",
  "decision": "pass|fail",
  "findings": [
    {
      "severity": "critical|warning|info",
      "file": "src/auth.ts",
      "line": 42,
      "title": "JWT not validated",
      "fix": "Add token.verify()"
    }
  ]
}
```

Also save a human-readable `.md` version.

---

Powered by I-Lang v3.0 | ilang.ai
