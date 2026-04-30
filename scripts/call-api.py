#!/usr/bin/env python3
"""iReview API caller — safely constructs JSON and calls review API.

Usage:
    python3 call-api.py --config .ireview.json --mode standard --diff-file /tmp/diff.txt
    python3 call-api.py --config .ireview.json --mode adversarial --diff-file /tmp/diff.txt

Output: JSON to stdout with findings.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

SYSTEM_PROMPTS = {
    "standard": (
        "You are a senior code reviewer. Review the following code changes. "
        "Focus areas: {focus}. "
        "Rules: report only real issues — bugs, security holes, logic errors, "
        "missing edge cases. Do NOT report style preferences or formatting. "
        "Respond in JSON format only, no markdown, no preamble: "
        '{{"findings": [{{"severity": "critical|warning|info", "file": "path", '
        '"line": 0, "title": "short description", "fix": "suggestion"}}], '
        '"decision": "pass|fail"}}'
    ),
    "adversarial": (
        "You are an adversarial code reviewer — a skeptical senior engineer "
        "who has seen production outages caused by code exactly like this. "
        "Your job is to BREAK. For every change, ask: What assumption could "
        "be wrong? What happens under 10x load? Is there a simpler approach? "
        "Where is the implicit coupling? Focus areas: {focus}. "
        "Respond in JSON format only, no markdown, no preamble: "
        '{{"findings": [{{"severity": "critical|challenge|alternative", '
        '"file": "path", "line": 0, "title": "short description", '
        '"fix": "suggestion"}}], "decision": "pass|fail"}}'
    ),
}

def load_config(config_path):
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Config error: {e}"}))
        sys.exit(1)

def call_api(config, system_prompt, diff_content):
    base_url = config.get("base_url", "https://openrouter.ai/api/v1").rstrip("/")
    api_key = config.get("api_key") or os.environ.get("IREVIEW_API_KEY", "")
    model = config.get("model", "deepseek/deepseek-chat")
    timeout = config.get("timeout_sec", 120)

    if not api_key:
        return {"error": "No API key. Set api_key in .ireview.json or IREVIEW_API_KEY env var."}

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": diff_content},
        ],
        "temperature": 0.1,
    }, ensure_ascii=False).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    extra_headers = config.get("headers", {})
    headers.update(extra_headers)

    url = f"{base_url}/chat/completions"

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Try to parse as JSON
            try:
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0]
                return json.loads(content)
            except json.JSONDecodeError:
                # Model returned non-JSON, wrap it
                if "LGTM" in content.upper():
                    return {"findings": [], "decision": "pass"}
                return {"raw_response": content, "decision": "unknown"}

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return {"error": f"HTTP {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

def main():
    parser = argparse.ArgumentParser(description="iReview API caller")
    parser.add_argument("--config", default=".ireview.json", help="Config file path")
    parser.add_argument("--mode", choices=["standard", "adversarial"], default="standard")
    parser.add_argument("--diff-file", help="File containing the diff (use - for stdin)")
    parser.add_argument("--diff", help="Diff content as string (for small diffs)")
    args = parser.parse_args()

    config = load_config(args.config)

    # Get diff content
    if args.diff_file:
        if args.diff_file == "-":
            diff_content = sys.stdin.read()
        else:
            with open(args.diff_file) as f:
                diff_content = f.read()
    elif args.diff:
        diff_content = args.diff
    else:
        diff_content = sys.stdin.read()

    if not diff_content.strip():
        print(json.dumps({"findings": [], "decision": "pass", "note": "Empty diff"}))
        return

    # Truncate if too large
    max_chars = config.get("max_diff_chars", 100000)
    if len(diff_content) > max_chars:
        diff_content = diff_content[:max_chars] + f"\n\n[TRUNCATED — original was {len(diff_content)} chars]"

    # Build system prompt
    focus = ", ".join(config.get("focus", ["bugs", "security"]))
    system_prompt = SYSTEM_PROMPTS[args.mode].format(focus=focus)

    # Call API
    result = call_api(config, system_prompt, diff_content)
    result["model"] = config.get("model", "unknown")
    result["mode"] = args.mode

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
