# /ireview:setup — Configure iReview

Help user set up or modify their iReview configuration.

## What to do

1. Check if `.ireview.json` exists.

2. If it doesn't exist:
   - Copy `.ireview.example.json` to `.ireview.json` (the example file is in the plugin directory: `${CLAUDE_PLUGIN_ROOT}/.ireview.example.json`)
   - Ask user: "Which model do you want for code reviews?" and suggest:
     - **DeepSeek** (cheapest): `deepseek-chat` at `api.deepseek.com/v1`
     - **OpenRouter** (any model, one key): pick from `deepseek/deepseek-chat`, `google/gemini-2.5-pro`, `openai/gpt-4o`, etc. at `openrouter.ai/api/v1`
     - **OpenAI direct**: `gpt-4o` at `api.openai.com/v1`
     - **Local Ollama** (free, private): `llama3` at `localhost:11434/v1`
   - Ask for API key.
   - Write config.
   - Add `.ireview.json` to `.gitignore` if not already there.

3. If config exists, show current config and ask what to change:
   - `model` — which model to use
   - `focus` — what to look for (bugs, security, performance, architecture, types, tests)
   - `auto_review` — enable/disable auto review gate on stop
   - `api_key` — update API key

4. Arguments:
   - `/ireview:setup` — interactive setup
   - `/ireview:setup --enable-auto-review` — turn on auto review gate
   - `/ireview:setup --disable-auto-review` — turn off auto review gate
   - `/ireview:setup --model deepseek-chat` — quick model switch
