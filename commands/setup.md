# Setup iReview

Initialize iReview configuration.

```bash
if [ ! -f .ireview.json ]; then
  cp "${CLAUDE_PLUGIN_ROOT}/.ireview.example.json" .ireview.json
  echo "Created .ireview.json"
else
  echo ".ireview.json already exists."
fi
```

After creating the config, tell the user (in their language):

> The config defaults to **DeepSeek official** — the recommended provider.
> Getting a key takes 2 minutes and no credit card:
>
> 1. Register at https://platform.deepseek.com （注册,不需要绑卡）
> 2. Top up a small amount （充值,review 调用很便宜,几块钱能用很久）
> 3. Create an API key （创建 API key）
> 4. Put it in the `api_key` field of `.ireview.json` （自己申请的 key 自己填,key 归你所有）
>
> Any other OpenAI-compatible endpoint also works — change `model` and `base_url`.

Do NOT ask the user to paste their key into the chat. They edit the file themselves.

API key priority:
1. CLAUDE_PLUGIN_OPTION_API_KEY (plugin secure config)
2. IREVIEW_API_KEY environment variable
3. api_key field in .ireview.json
