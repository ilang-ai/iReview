# iReview

> **Universal AI-to-AI code review for Claude Code.**
> Any model reviews your code. DeepSeek, GPT, Gemini, Llama, or any OpenAI-compatible API.

[![License](https://img.shields.io/badge/license-MIT-d4a858?style=flat-square)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocol-I--Lang_v3.0-d4a858?style=flat-square)](https://ilang.ai)

---

## Why

OpenAI's Codex plugin lets Codex review Claude Code's output. But it requires Codex CLI installation, ChatGPT login, and only works with OpenAI models.

iReview does the same thing with **zero dependencies**. One JSON config file. Any model. Any API.

| | iReview | codex-plugin-cc |
|---|---|---|
| Install | Copy config file | Install Codex CLI + login |
| Models | Any (DeepSeek, GPT, Gemini, Llama, Ollama...) | OpenAI only |
| Dependencies | None | Node.js 18.18+, Codex CLI |
| Config | One JSON file | config.toml + CLI auth |
| Cost | Your API key, your rates | ChatGPT subscription or API key |
| Auto review gate | Yes | Yes |
| Multi-model review | Yes (security→GPT, perf→DeepSeek) | No |

## Install (seconds)

```bash
# Add marketplace
/plugin marketplace add ilang-ai/iReview

# Install
/plugin install ireview@ilang-plugins

# Create config
cp .ireview.example.json .ireview.json
# Edit .ireview.json — set your API key and model
```

Add `.ireview.json` to `.gitignore` (it contains your API key).

## Config

```json
{
  "model": "deepseek/deepseek-chat",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1",
  "focus": ["bugs", "security"],
  "auto_review": false
}
```

### Pick your reviewer

**OpenRouter (one key → all models):**
```json
{ "model": "deepseek/deepseek-chat", "base_url": "https://openrouter.ai/api/v1" }
```

**DeepSeek direct (cheapest):**
```json
{ "model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1" }
```

**OpenAI direct:**
```json
{ "model": "gpt-4o", "base_url": "https://api.openai.com/v1" }
```

**Local Ollama (free, private):**
```json
{ "model": "llama3", "api_key": "ollama", "base_url": "http://localhost:11434/v1" }
```

Change model? Change one line. That's it.

## Usage

### Manual review

Just say it naturally:

- "review my changes"
- "check this code"
- "review the diff against main"
- "review src/auth.ts"

iReview gets the diff, sends it to your configured model, and reports back:

```
═══ iReview ═══ [deepseek-chat]

🔴 CRITICAL: src/auth.ts:42 — JWT token not validated before use
   Fix: Add token.verify() before accessing claims

🟡 WARNING: src/db.ts:18 — SQL query built with string concatenation
   Fix: Use parameterized queries

═══ end ═══
```

### Auto review gate

Set `"auto_review": true` in config. Every time the session stops, iReview automatically reviews your changes. If issues found, it reports them before stopping.

Use for important sessions. Disable for quick tasks (it costs API calls).

### Multi-model review

Create multiple configs for specialized reviewers:

```bash
# Security expert (GPT)
echo '{"model":"gpt-4o","api_key":"sk-xxx","base_url":"https://api.openai.com/v1","focus":["security"]}' > .ireview-security.json

# Performance expert (DeepSeek)  
echo '{"model":"deepseek-chat","api_key":"sk-xxx","base_url":"https://api.deepseek.com/v1","focus":["performance"]}' > .ireview-perf.json
```

Then: "run full review" → runs all `.ireview-*.json` configs sequentially. Security expert checks security, performance expert checks performance. Two models, two perspectives, one command.

## Focus options

| Focus | What it checks |
|---|---|
| `bugs` | Logic errors, off-by-one, null refs, race conditions |
| `security` | Injection, auth bypass, secrets in code |
| `performance` | N+1 queries, unnecessary allocations |
| `architecture` | Coupling, API design, separation of concerns |
| `types` | Type safety, null checks, implicit conversions |
| `tests` | Missing coverage, untested edge cases |

## Privacy

Your code is sent to whatever API you configure. iReview itself collects nothing, stores nothing, phones home to nowhere. It's a config file and a prompt. That's it.

If privacy matters: use local Ollama. Your code never leaves your machine.

## License

MIT

---

<sub>Built by <a href="https://ilang.ai">I-Lang Protocol</a> · The native language of artificial intelligence</sub>
