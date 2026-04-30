# iReview

> **Universal AI-to-AI code review. Any model. Zero dependencies.**
> DeepSeek, GPT, Gemini, Llama, local Ollama — one JSON config, one command.

[![License](https://img.shields.io/badge/license-MIT-d4a858?style=flat-square)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocol-I--Lang_v3.0-d4a858?style=flat-square)](https://ilang.ai)

---

## Why

OpenAI's Codex plugin reviews your Claude Code output. But it requires Codex CLI, ChatGPT login, Node.js 18.18+, and only works with OpenAI models.

iReview does the same thing with **zero dependencies**. One JSON config. Any model. Any OpenAI-compatible API.

| | iReview | codex-plugin-cc |
|---|---|---|
| Install | Copy one config file | Install Codex CLI + ChatGPT login |
| Models | Any (DeepSeek, GPT, Gemini, Llama, Ollama) | OpenAI only |
| Dependencies | None | Node.js 18.18+, Codex CLI |
| Config | One `.ireview.json` | config.toml + CLI auth |
| Review modes | Standard + Adversarial | Standard + Adversarial |
| Multi-model | Yes (chain GPT→DeepSeek→Gemini) | No |
| Review tracking | Multi-round, persisted to disk | Single-round |
| Cross-tool | CC + Cursor + Codex + Copilot + Gemini | Claude Code only |

## Install (seconds)

```bash
/plugin marketplace add ilang-ai/iReview
/plugin install ireview@ilang-plugins
```

Then create your config:

```bash
cp .ireview.example.json .ireview.json
# Edit: set your model and api_key
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

| Setup | model | base_url |
|---|---|---|
| OpenRouter (one key, all models) | `deepseek/deepseek-chat` | `https://openrouter.ai/api/v1` |
| DeepSeek direct (cheapest) | `deepseek-chat` | `https://api.deepseek.com/v1` |
| OpenAI direct | `gpt-4o` | `https://api.openai.com/v1` |
| Gemini via OpenRouter | `google/gemini-2.5-pro` | `https://openrouter.ai/api/v1` |
| Local Ollama (free, private) | `llama3` | `http://localhost:11434/v1` |

**Change model = change one line.** That's it.

Or use `/ireview:setup` for interactive configuration.

## Commands

### `/ireview` — Standard Review

```bash
/ireview                     # Review uncommitted changes
/ireview src/auth.ts         # Review specific files
/ireview --base main         # Review branch vs main
/ireview --config .ireview-security.json   # Use alternate config
/ireview --full              # Run ALL .ireview-*.json configs (multi-model)
```

Output:

```
═══ iReview ═══ deepseek-chat ═══

🔴 CRITICAL: src/auth.ts:42 — JWT not validated before use
   Fix: Add token.verify() before accessing claims

🟡 WARNING: src/db.ts:18 — SQL built with string concat
   Fix: Use parameterized queries

═══ 2 findings saved to .ireview/reviews/ ═══
```

### `/ireview:adversarial` — Devil's Advocate

Same as `/ireview` but the reviewer actively challenges your design decisions, questions assumptions, and probes failure modes.

```
═══ iReview ═══ ADVERSARIAL ═══ gpt-4o ═══

⚔️  CHALLENGE: src/cache.ts:15 — LRU cache has no TTL
   Question: What happens when stale data is served for 24h?

🔄 ALTERNATIVE: src/api.ts:30 — REST endpoint for batch ops
   Consider: GraphQL would handle N+1 at the protocol level

═══ end ═══
```

### `/ireview:status` — Track Multi-Round Fixes

iReview tracks findings across review rounds. Fix issues, run `/ireview` again, and it checks whether previous findings were addressed:

```
Round 1: 6 issues found
Round 2: 4 resolved, 2 still open, 1 new regression
Round 3: Clean ✅
```

### `/ireview:setup` — Configure

```bash
/ireview:setup                        # Interactive setup
/ireview:setup --enable-auto-review   # Auto-review on stop
/ireview:setup --disable-auto-review  # Turn off auto-review
/ireview:setup --model deepseek-chat  # Quick model switch
```

## Auto Review Gate

Set `"auto_review": true` in config. Every time the session stops, iReview automatically reviews your changes before allowing exit. If critical issues found, the stop is blocked until you address them.

Use for important sessions. Disable for quick tasks.

## Multi-Model Review

Create specialized configs for different reviewers:

```bash
echo '{"model":"gpt-4o","api_key":"sk-xxx","base_url":"https://api.openai.com/v1","focus":["security"]}' > .ireview-security.json
echo '{"model":"deepseek-chat","api_key":"sk-xxx","base_url":"https://api.deepseek.com/v1","focus":["performance"]}' > .ireview-perf.json
```

Run `/ireview --full` — security expert checks security, performance expert checks performance. Two models, two perspectives, one command.

## Focus Options

| Focus | What it checks |
|---|---|
| `bugs` | Logic errors, off-by-one, null refs, race conditions |
| `security` | Injection, auth bypass, secrets in code, SSRF |
| `performance` | N+1 queries, unnecessary allocations, blocking I/O |
| `architecture` | Coupling, responsibility leaks, API surface |
| `types` | Type safety, null checks, implicit conversions |
| `tests` | Missing coverage, untested edge cases |

## Works Across Tools

| Tool | Auto-reads | Hook support |
|---|---|---|
| Claude Code | `CLAUDE.md` | Full (stop gate, slash commands) |
| Cursor | `.cursorrules` | Manual review only |
| Codex | `AGENTS.md` | Manual review only |
| Copilot | `.github/copilot-instructions.md` | Manual review only |
| Gemini CLI | `GEMINI.md` | Manual review only |

Non-CC tools don't have hook support, but manual `/ireview` commands work via natural language: "review my changes using the config in .ireview.json".

## Privacy

Your code is sent to whatever API you configure. iReview itself collects nothing, stores nothing, phones home to nowhere. If privacy matters, use local Ollama — your code never leaves your machine.

## License

MIT

---

<sub>Built by <a href="https://ilang.ai">I-Lang Protocol</a> · The native language of artificial intelligence</sub>
