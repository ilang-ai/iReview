# iReview

Universal AI-to-AI code review.

When user asks to review code, check this code, or get a second opinion:

1. Read `.ireview.json` for model, api_key, base_url, focus settings.
   If missing: tell user to copy `.ireview.example.json` to `.ireview.json` and set api_key.
2. Get the diff: `git diff HEAD` (or specific files if user specified).
3. Save diff to file:
   ```bash
   mkdir -p .ireview/tmp
   git diff HEAD > .ireview/tmp/current.diff
   ```
4. Run the review script:
   If installed as plugin: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py --config .ireview.json --mode standard --diff-file .ireview/tmp/current.diff`
   If repo cloned directly: `python3 scripts/call-api.py --config .ireview.json --mode standard --diff-file .ireview/tmp/current.diff`
   For adversarial review (user says "challenge my code"): use `--mode adversarial`
5. Parse JSON output. Present findings to user.
6. Save results to `.ireview/reviews/` directory.
7. If critical issues found, offer to fix them.

Do NOT manually construct curl JSON payloads with diffs. Always use the call-api.py script.
