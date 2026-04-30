# /ireview:review — Standard Code Review

Run an independent code review using an external AI model.
Communication between models uses I-Lang v3.0 protocol:
`[EVAL:@DIFF]=>[SCAN]=>[CLSF]=>[FMT|fmt=ilang]=>[OUT]`

## Steps

1. Read `.ireview.json` for model config. If missing, tell user to run `/ireview:setup`.
2. Determine review target:
   - No args: `git diff HEAD` (uncommitted changes)
   - `--base main`: `git diff main...HEAD` (branch diff)
   - Specific files: review those files only
3. If no changes found: "Nothing to review."
4. Run the review script:

```bash
mkdir -p .ireview/tmp
git diff HEAD > .ireview/tmp/current.diff

python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py \
  --config .ireview.json \
  --mode standard \
  --diff-file .ireview/tmp/current.diff
```

5. The script sends I-Lang instructions to the external model.
   Model returns I-Lang declarations: `::REVIEW{}`, `::FINDING{}`, `::END{REVIEW}`.
6. Parse findings. Save to `.ireview/reviews/`.
7. Update `.ireview/state.json`: phase=passed or phase=failed.
8. Present findings to user in human-readable format. Offer to fix critical issues.

## Arguments

- `/ireview:review` — uncommitted changes
- `/ireview:review src/auth.ts` — specific files
- `/ireview:review --base main` — branch vs main
- `/ireview:review --config .ireview-security.json` — alternate config
- `/ireview:review --full` — run ALL .ireview-*.json configs
