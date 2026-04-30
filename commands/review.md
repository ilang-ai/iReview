# /ireview:review — Standard Code Review

Run an independent code review using an external AI model.

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

5. Read the script output (JSON). Parse findings.
6. Save results to `.ireview/reviews/YYYYMMDD-HHMMSS.json` and `.md`.
7. Update `.ireview/state.json`: set phase to `passed` or `failed`.
8. Present findings:

```
═══ iReview ═══ [model] ═══

🔴 CRITICAL: file:line — description
   Fix: suggestion

🟡 WARNING: file:line — description
   Fix: suggestion

✅ LGTM — no issues found

═══ [saved to .ireview/reviews/] ═══
```

9. If critical issues found, offer to fix them.

## Arguments

- `/ireview:review` — uncommitted changes
- `/ireview:review src/auth.ts` — specific files
- `/ireview:review --base main` — branch vs main
- `/ireview:review --config .ireview-security.json` — alternate config
- `/ireview:review --full` — run ALL .ireview-*.json configs
