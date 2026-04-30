---
name: ireview
description: "Universal AI-to-AI code review. Send code to any model for independent review. Supports manual review command and automatic review gate on session stop."
version: 1.0.0
---

# iReview

::GENE{ireview|v:1.0|spec:ilang-v3.0}
  T:review_with_external_model
  T:zero_dependencies
  T:any_openai_compatible_api
  T:report_real_issues_only
  A:review_style_issues⇒noise
  A:review_without_diff⇒pointless
  A:block_stop_on_lgtm⇒annoying

## Config

iReview reads `.ireview.json` from project root:

```json
{
  "model": "deepseek/deepseek-chat",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1",
  "focus": ["bugs", "security"],
  "auto_review": false
}
```

Fallback: environment variables `IREVIEW_MODEL`, `IREVIEW_API_KEY`, `IREVIEW_BASE_URL`.

### Model examples

Users can use ANY OpenAI-compatible API. Common setups:

**OpenRouter (recommended — one key, all models):**
```json
{
  "model": "deepseek/deepseek-chat",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1"
}
```

**DeepSeek direct:**
```json
{
  "model": "deepseek-chat",
  "api_key": "sk-xxx",
  "base_url": "https://api.deepseek.com/v1"
}
```

**OpenAI direct:**
```json
{
  "model": "gpt-4o",
  "api_key": "sk-xxx",
  "base_url": "https://api.openai.com/v1"
}
```

**Google Gemini (via OpenRouter):**
```json
{
  "model": "google/gemini-2.5-pro",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1"
}
```

**Local Ollama:**
```json
{
  "model": "llama3",
  "api_key": "ollama",
  "base_url": "http://localhost:11434/v1"
}
```

### Focus options

`focus` array controls what the reviewer looks for:

| Focus | What it checks |
|---|---|
| `bugs` | Logic errors, off-by-one, null refs, race conditions |
| `security` | Injection, auth bypass, secrets in code, unsafe deserialization |
| `performance` | N+1 queries, unnecessary allocations, missing indexes |
| `architecture` | Separation of concerns, coupling, API design |
| `types` | Type safety, missing null checks, implicit conversions |
| `tests` | Missing test coverage, untested edge cases |

Default: `["bugs", "security"]`

## Manual Review

When user says "review this", "check my code", "review the diff", or similar:

1. Read `.ireview.json` for config.
2. Get the diff:
   - If user specifies files: review those files only.
   - If user says "review my changes": run `git diff HEAD`.
   - If user says "review this branch": run `git diff main...HEAD`.
3. Call the external model:

```bash
curl -s "${base_url}/chat/completions" \
  -H "Authorization: Bearer ${api_key}" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${model}\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a senior code reviewer. Review the following code diff. Focus on: ${focus}. Rules: report only real issues, not style preferences. Be concise. Each issue: file, line, severity (critical/warning/info), description, suggested fix. If no issues: respond with exactly LGTM.\"},
      {\"role\": \"user\", \"content\": \"${diff}\"}
    ],
    \"temperature\": 0.1
  }"
```

4. Parse and present results. If issues found, offer to fix them.

## Auto Review Gate

When `auto_review: true` in config, the Stop hook triggers automatically:

- Gets `git diff HEAD` on every stop.
- If no changes: skip silently.
- If changes exist: send to configured model for review.
- If `LGTM`: allow stop.
- If issues found: report them, suggest fixes, continue session.

Warning: auto_review can increase API costs. Use for important sessions only.

## Output Format

Review results are presented as:

```
═══ iReview ═══ [model-name]

🔴 CRITICAL: [file:line] description
   Fix: suggestion

🟡 WARNING: [file:line] description
   Fix: suggestion

🟢 LGTM — no issues found

═══ end ═══
```

## Multi-Model Review

Users can create multiple config files for different reviewers:

```bash
# Security review with GPT
cat > .ireview-security.json << EOF
{"model":"gpt-4o","api_key":"sk-xxx","base_url":"https://api.openai.com/v1","focus":["security"]}
EOF

# Performance review with DeepSeek
cat > .ireview-perf.json << EOF
{"model":"deepseek-chat","api_key":"sk-xxx","base_url":"https://api.deepseek.com/v1","focus":["performance"]}
EOF
```

User says "review security with .ireview-security.json" → use that config.
User says "full review" → run all .ireview-*.json configs sequentially.

---

Powered by I-Lang v3.0 | ilang.ai
