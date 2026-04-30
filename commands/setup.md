# /ireview:setup — Configure iReview

Interactive configuration. Creates or modifies `.ireview.json`.

## Steps

1. If `.ireview.json` missing: guide user to create one. Ask:
   - Model provider: DeepSeek (cheapest) / OpenRouter (any model) / OpenAI / Local Ollama
   - API key (or env var name)
   - Focus areas: bugs, security, performance, architecture
   - Auto review gate: on/off (default off)
2. If config exists: show current config, ask what to change.
3. Ensure `.ireview.json` is in `.gitignore`.
4. Verify API connectivity: test call with a simple prompt.

## Arguments

- `/ireview:setup` — interactive
- `/ireview:setup --enable-auto-review` — turn on stop gate
- `/ireview:setup --disable-auto-review` — turn off stop gate
- `/ireview:setup --model deepseek-chat` — quick switch
