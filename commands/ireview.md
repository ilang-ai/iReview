# /ireview — Standard Code Review

Run an independent code review using an external AI model.

## What to do

1. Read `.ireview.json` for model, api_key, base_url, and focus settings.
2. Determine what to review:
   - If user specified files: review those files only.
   - If user said "review my changes" or just "/ireview": run `git diff HEAD`.
   - If user said "review this branch": run `git diff main...HEAD`.
   - If no git changes and no files specified: tell user "Nothing to review."
3. If diff exceeds 500 lines: send only file names + key change summaries, not the full diff. Tell user you're summarizing due to size.
4. Call the external model:

```bash
curl -s "${base_url}/chat/completions" \
  -H "Authorization: Bearer ${api_key}" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${model}\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a senior code reviewer. Review the following code changes. Focus areas: ${focus}. Rules: report only real issues — bugs, security holes, logic errors, missing edge cases. Do NOT report style preferences or formatting. Each finding: [SEVERITY] file:line — description — suggested fix. Severities: CRITICAL (will break production), WARNING (potential issue), INFO (minor improvement). If no issues: respond with exactly LGTM.\"},
      {\"role\": \"user\", \"content\": \"<the diff or summary>\"}
    ],
    \"temperature\": 0.1
  }"
```

5. Parse the response from `data.choices[0].message.content`.
6. Save results to `.ireview/reviews/review-$(date +%s).md` with header:

```markdown
# iReview — [model] — [date]
## Files reviewed: [list]
## Findings:
[parsed results]
```

7. Present results:

```
═══ iReview ═══ [model-name] ═══

🔴 CRITICAL: file:line — description
   Fix: suggestion

🟡 WARNING: file:line — description
   Fix: suggestion

ℹ️  INFO: file:line — description

── or ──

✅ LGTM — no issues found

═══ end ═══
```

8. If critical or warning issues found, offer to fix them.

## Arguments

- `/ireview` — review uncommitted changes
- `/ireview src/auth.ts src/db.ts` — review specific files
- `/ireview --base main` — review current branch vs main
- `/ireview --config .ireview-security.json` — use alternate config
- `/ireview --full` — run ALL .ireview-*.json configs sequentially (multi-model review)
