---
name: ireview
description: "Universal AI-to-AI code review. Route reviews to any OpenAI-compatible model. Standard and adversarial modes, multi-round tracking, auto review gate."
version: 1.0.0
author: ilang-ai
license: MIT
metadata:
  hermes:
    tags: [code-review, ai-to-ai, multi-model, security, quality]
    platforms: [claude-code, cursor, codex, copilot, gemini]
---

# iReview

::GENE{ireview|v:1.0|spec:ilang-v3.0}
  T:review_with_external_model
  T:zero_dependencies
  T:any_openai_compatible_api
  T:report_real_issues_only
  T:persist_findings_to_disk
  T:track_multi_round_resolution
  A:review_style_issues⇒noise
  A:review_without_changes⇒skip
  A:block_stop_on_lgtm⇒annoying
  A:send_diff_over_500_lines⇒summarize_instead
  A:lose_review_results⇒always_save_to_file

## Config

`.ireview.json` in project root:

```json
{
  "model": "deepseek/deepseek-chat",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1",
  "focus": ["bugs", "security"],
  "auto_review": false
}
```

Fallback: env vars `IREVIEW_MODEL`, `IREVIEW_API_KEY`, `IREVIEW_BASE_URL`.

### Model quick reference

| Provider | model | base_url | Cost |
|---|---|---|---|
| OpenRouter (any model) | `deepseek/deepseek-chat` | `https://openrouter.ai/api/v1` | Varies |
| DeepSeek direct | `deepseek-chat` | `https://api.deepseek.com/v1` | Cheapest |
| OpenAI direct | `gpt-4o` | `https://api.openai.com/v1` | $$$ |
| Google Gemini | `google/gemini-2.5-pro` | `https://openrouter.ai/api/v1` | $$ |
| Local Ollama | `llama3` | `http://localhost:11434/v1` | Free |

Change model = change one line. That's it.

### Focus options

| Focus | Looks for |
|---|---|
| `bugs` | Logic errors, off-by-one, null refs, race conditions |
| `security` | Injection, auth bypass, secrets in code, SSRF |
| `performance` | N+1 queries, unnecessary allocations, blocking I/O |
| `architecture` | Coupling, responsibility leaks, API surface issues |
| `types` | Type safety, missing null checks, implicit conversions |
| `tests` | Missing coverage, untested edge cases, flaky patterns |

Default: `["bugs", "security"]`

## API Call Pattern

For all review types, construct and execute:

```bash
curl -s "${base_url}/chat/completions" \
  -H "Authorization: Bearer ${api_key}" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${model}\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"${SYSTEM_PROMPT}\"},
      {\"role\": \"user\", \"content\": \"${DIFF_OR_SUMMARY}\"}
    ],
    \"temperature\": 0.1
  }"
```

Response is in `data.choices[0].message.content`.

If API call fails (timeout, auth error, rate limit): report the error clearly, do NOT retry automatically, suggest user check their config.

## Diff Size Protection

- Under 500 lines: send full diff.
- 500-2000 lines: send file-by-file, skip test files and generated files.
- Over 2000 lines: send only file names + change stats (`git diff --stat`), ask user which files to review in detail.

## Review Persistence

ALL review results saved to `.ireview/reviews/`:

```markdown
# iReview — [model] — [YYYY-MM-DD HH:MM]
## Mode: standard | adversarial
## Files: [list]
## Previous: [reference to prior review if multi-round]
## Findings:
- [CRITICAL] file:line — description — fix
- [WARNING] file:line — description — fix
- LGTM
```

## Multi-Round Tracking

When running a follow-up review:
1. Read most recent review from `.ireview/reviews/`.
2. Add to system prompt: "Previous review found: [findings]. Check if each was addressed. Mark as RESOLVED, STILL_OPEN, or NEW."
3. Save new review referencing the previous one.

## Multi-Model Review

User can create `.ireview-{name}.json` files for specialized reviewers:

```bash
# .ireview-security.json → GPT for security
# .ireview-perf.json → DeepSeek for performance
# .ireview-arch.json → Gemini for architecture
```

`/ireview --full` runs all configs sequentially. Each produces its own review file.

## Output Format

```
═══ iReview ═══ [model-name] ═══

🔴 CRITICAL: file:line — description
   Fix: suggestion

🟡 WARNING: file:line — description
   Fix: suggestion

ℹ️  INFO: file:line — description

── or ──

✅ LGTM — no issues found

═══ [N findings saved to .ireview/reviews/] ═══
```

## Transparency

When presenting review results:
- Always show which model performed the review.
- Always show how many lines/files were reviewed.
- If diff was summarized due to size, say so.
- Never claim the review is exhaustive. Say "external review" not "complete audit".

---

Powered by I-Lang v3.0 | ilang.ai
