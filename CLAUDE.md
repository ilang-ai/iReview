# iReview

Universal AI-to-AI code review. Read `skills/ireview/SKILL.md` for the full protocol.

When user asks to review code:

1. Read `.ireview.json` for model config. If missing, ask user to create one (copy from `.ireview.example.json`).
2. Get the diff: `git diff HEAD` for uncommitted, `git diff main...HEAD` for branch.
3. Save diff to temp file: `mkdir -p .ireview/tmp && git diff HEAD > .ireview/tmp/current.diff`
4. Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py --config .ireview.json --mode standard --diff-file .ireview/tmp/current.diff`
   If this repo was cloned directly (not installed as plugin): use `python3 scripts/call-api.py` instead.
4. Parse JSON output. Save to `.ireview/reviews/YYYYMMDD-HHMMSS.json` and `.md`.
5. Present findings. Offer to fix critical issues.

For adversarial review: use `--mode adversarial`.

Commands: `/ireview:review`, `/ireview:adversarial`, `/ireview:setup`, `/ireview:status`, `/ireview:result`, `/ireview:cancel`
