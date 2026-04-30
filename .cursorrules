# iReview

AI-to-AI code review powered by I-Lang v3.0 protocol.

When user asks to review code, check this code, or get a second opinion:

1. Read `.ireview.json` for model, api_key, base_url, focus settings.
   If missing: tell user to copy `.ireview.example.json` to `.ireview.json` and set api_key.

2. Get the diff:
   ```bash
   mkdir -p .ireview/tmp
   git diff HEAD > .ireview/tmp/current.diff
   ```

3. Run the review script (sends I-Lang instructions to external model):
   If installed as plugin: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py --config .ireview.json --mode standard --diff-file .ireview/tmp/current.diff`
   If repo cloned directly: `python3 scripts/call-api.py --config .ireview.json --mode standard --diff-file .ireview/tmp/current.diff`

   The script sends I-Lang protocol: `[EVAL:@DIFF]=>[SCAN]=>[CLSF]=>[OUT]`
   Model returns I-Lang declarations: `::REVIEW{}`, `::FINDING{}`, `::END{REVIEW}`

   For adversarial review (user says "challenge my code"): use `--mode adversarial`

4. Parse response. Present findings to user. Save to `.ireview/reviews/`.
5. If critical issues found, offer to fix them.

Do NOT manually construct curl JSON payloads with diffs. Always use the call-api.py script.

Read `skills/ireview/SKILL.md` for the full I-Lang review protocol definition.
