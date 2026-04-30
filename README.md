# iReview

> **Universal AI-to-AI code review. Any model. Zero CLI installs.**
> DeepSeek, GPT, Gemini, Llama, local Ollama — one JSON config, one command.

[![License](https://img.shields.io/badge/license-MIT-d4a858?style=flat-square)](LICENSE)
[![Protocol](https://img.shields.io/badge/protocol-I--Lang_v3.0-d4a858?style=flat-square)](https://ilang.ai)

---

## Why

OpenAI's Codex plugin reviews Claude Code output. But it requires Codex CLI, ChatGPT login, Node.js 18.18+, and only works with OpenAI models.

iReview does the same thing with **one JSON config file**. Any model. Any OpenAI-compatible API.

| | iReview | codex-plugin-cc |
|---|---|---|
| Install | One config file | Codex CLI + ChatGPT login |
| Models | Any OpenAI-compatible API | OpenAI only |
| Dependencies | python3 (pre-installed everywhere) | Node.js 18.18+, Codex CLI |
| Review modes | Standard + Adversarial | Standard + Adversarial |
| Multi-model | Yes (chain security→perf→arch) | No |
| Review tracking | Multi-round, persisted JSON | Single-round |
| Cross-tool | CC + Cursor + Codex + Copilot + Gemini | Claude Code only |
| Stop gate | Diff-hash aware (no infinite loop) | Can loop indefinitely |

## Requirements

- `python3` (for reliable JSON handling in API calls)
- `git`
- `curl` or `urllib` (Python stdlib)

## Install (seconds)

```bash
/plugin marketplace add ilang-ai/iReview
/plugin install ireview@ilang-plugins
```

Create your config:

```bash
cp .ireview.example.json .ireview.json
# Set model and api_key — two fields, done
```

Or run `/ireview:setup` for interactive configuration.

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

| Provider | model | base_url |
|---|---|---|
| OpenRouter (any model) | `deepseek/deepseek-chat` | `https://openrouter.ai/api/v1` |
| DeepSeek direct | `deepseek-chat` | `https://api.deepseek.com/v1` |
| OpenAI direct | `gpt-4o` | `https://api.openai.com/v1` |
| Local Ollama | `llama3` | `http://localhost:11434/v1` |

**Change model = change one line.**

## Commands

```bash
/ireview:review                    # Review uncommitted changes
/ireview:review --base main        # Review branch vs main
/ireview:review --full             # Run all .ireview-*.json configs
/ireview:adversarial               # Devil's advocate review
/ireview:setup                     # Interactive configuration
/ireview:status                    # Review history and unresolved findings
/ireview:result                    # Show latest review details
/ireview:cancel                    # Cancel pending review, allow stop
```

## Auto Review Gate

Set `"auto_review": true` in config. When the session stops:

1. Stop hook detects file changes and computes diff hash
2. If this diff wasn't reviewed yet: blocks stop with instructions
3. You run `/ireview:review` — review executes, results saved
4. On next stop: diff hash matches passed review — stop allowed

**No infinite loops.** Diff-hash tracking ensures the same changes aren't re-reviewed.

## Multi-Model Review

```bash
echo '{"model":"gpt-4o","api_key":"sk-xxx","base_url":"https://api.openai.com/v1","focus":["security"]}' > .ireview-security.json
echo '{"model":"deepseek-chat","api_key":"sk-xxx","base_url":"https://api.deepseek.com/v1","focus":["performance"]}' > .ireview-perf.json
```

`/ireview:review --full` — runs all configs. Each produces its own review file.

## Architecture

```
hooks/stop-gate.sh     ← Fast. Checks diff, computes hash, blocks or allows. No API calls.
scripts/call-api.py    ← Reliable. Constructs JSON safely, calls API, returns structured results.
commands/*.md           ← Slash commands. Tell Claude what to do step by step.
skills/ireview/SKILL.md ← Protocol. I-Lang behavioral rules for the review process.
```

API calls go through `call-api.py`, never through hand-written curl JSON. Diffs contain quotes, backslashes, and newlines that break manual JSON construction.

## Works Across Tools

| Tool | File | Hook support |
|---|---|---|
| Claude Code | `CLAUDE.md` | Full (stop gate + commands) |
| Cursor | `.cursorrules` | Manual review only |
| Codex | `AGENTS.md` | Manual review only |
| Copilot | `.github/copilot-instructions.md` | Manual review only |
| Gemini CLI | `GEMINI.md` | Manual review only |

## Privacy

Your code goes to whatever API you configure. iReview collects nothing. For private code, use local Ollama.

Add `.ireview.json` to `.gitignore` — it contains your API key.

## License

MIT

---

<sub>Built by <a href="https://ilang.ai">I-Lang Protocol</a> · The native language of artificial intelligence</sub>
