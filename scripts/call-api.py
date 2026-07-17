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
        "[PROTOCOL:I-Lang|v=5.0]\n"
        "\n"
        "[EVAL:@DIFF|focus={focus}|depth=thorough]\n"
        "  =>[SCAN|whr=bugs,security,logic_errors]\n"
        "  =>[JUDGE|dims=consequence,reversibility,certainty,evidence]\n"
        "  =>[CLSF|typ=severity]\n"
        "  =>[FMT|fmt=ilang]\n"
        "  =>[OUT]\n"
        "\n"
        "::RULE{{report:bugs,security,logic_errors,edge_cases}}\n"
        "::RULE{{ignore:style,formatting,naming_conventions}}\n"
        "\n"
        "::JUDGE{{protocol:ilang-v5.0}}\n"
        "  # Do not assign severity by fixed keyword. Judge each finding across dimensions:\n"
        "  # consequence  = how bad is the worst realistic outcome if unfixed\n"
        "  # reversibility= how hard to recover once it hits (data loss = irreversible)\n"
        "  # certainty    = how sure you are this is a real defect, not a false positive\n"
        "  # evidence     = is it provable from the diff, or an assumption\n"
        "  # Then map the judgment to a severity band:\n"
        "  #   critical = high consequence AND (irreversible OR high certainty). Blocks the merge.\n"
        "  #   warning  = real risk but recoverable, or consequence is moderate\n"
        "  #   info     = minor; safe to ship, worth noting\n"
        "  # Low certainty or assumption-only: downgrade, and say so in the issue line.\n"
        "  # decision=fail ONLY if at least one critical stands on solid evidence.\n"
        "::RULE{{if:no_issues|then:decision=pass}}\n"
        "\n"
        "::FMT{{response}}\n"
        "  Respond ONLY in this exact format, no other text:\n"
        "\n"
        "  ::REVIEW{{id:TIMESTAMP|model:MODEL|decision:pass_or_fail}}\n"
        "  ::FINDING{{id:IR-001|severity:critical_or_warning_or_info|conf:0.0_to_1.0|file:path/to/file|line:N}}\n"
        "    issue: one line description\n"
        "    fix: one line suggestion\n"
        "  ::END{{REVIEW}}\n"
        "\n"
        "  conf is your certainty this finding is real (0.00-1.00). Below 0.50, prefer warning over critical.\n"
        "  If no issues: ::REVIEW{{id:TIMESTAMP|model:MODEL|decision:pass}} LGTM ::END{{REVIEW}}"
    ),
    "adversarial": (
        "[PROTOCOL:I-Lang|v=5.0]\n"
        "\n"
        "[EVAL:@DIFF|focus={focus}|depth=adversarial]\n"
        "  =>[SCAN|whr=assumptions,failure_modes,coupling,hidden_risks]\n"
        "  =>[JUDGE|dims=consequence,reversibility,certainty,evidence]\n"
        "  =>[CLSF|typ=severity]\n"
        "  =>[FMT|fmt=ilang]\n"
        "  =>[OUT]\n"
        "\n"
        "::RULE{{mode:adversarial}}\n"
        "::RULE{{challenge:design_decisions,assumptions,tradeoffs}}\n"
        "::RULE{{probe:10x_load,malicious_input,implicit_coupling,failure_without_recovery}}\n"
        "::RULE{{suggest:simpler_alternatives}}\n"
        "\n"
        "::JUDGE{{protocol:ilang-v5.0}}\n"
        "  # Judge each finding across dimensions, do not use fixed keywords:\n"
        "  # consequence (worst realistic outcome), reversibility (recoverability),\n"
        "  # certainty (real risk vs speculative), evidence (provable vs assumed).\n"
        "  # Map to a band:\n"
        "  #   critical    = will break production on solid evidence. Blocks merge.\n"
        "  #   challenge   = a design decision that needs justification (uncertain but material)\n"
        "  #   alternative = a simpler/safer approach exists\n"
        "  # Be adversarial but honest: speculative challenges carry low conf, not critical.\n"
        "  # decision=fail ONLY for a critical backed by evidence.\n"
        "::RULE{{if:genuinely_no_issues|then:decision=pass}}\n"
        "\n"
        "::FMT{{response}}\n"
        "  Respond ONLY in this exact format, no other text:\n"
        "\n"
        "  ::REVIEW{{id:TIMESTAMP|model:MODEL|mode:adversarial|decision:pass_or_fail}}\n"
        "  ::FINDING{{id:IR-001|severity:critical_or_challenge_or_alternative|conf:0.0_to_1.0|file:path/to/file|line:N}}\n"
        "    issue: one line description\n"
        "    fix: one line suggestion\n"
        "  ::END{{REVIEW}}\n"
        "\n"
        "  conf is your certainty this finding is real (0.00-1.00).\n"
        "  If no issues: ::REVIEW{{id:TIMESTAMP|model:MODEL|decision:pass}} LGTM ::END{{REVIEW}}"
    ),
}

def load_config(config_path):
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Config error: {e}"}))
        sys.exit(1)

def parse_ilang_response(content):
    """Parse I-Lang format response (::REVIEW, ::FINDING, ::END)."""
    import re

    result = {"findings": [], "decision": "unknown", "format": "ilang"}

    # Extract ::REVIEW header
    review_match = re.search(r'::REVIEW\{([^}]+)\}', content)
    if review_match:
        attrs = review_match.group(1)
        for pair in attrs.split('|'):
            if ':' in pair:
                k, v = pair.split(':', 1)
                if k.strip() == 'decision':
                    result["decision"] = v.strip()
                elif k.strip() == 'model':
                    result["review_model"] = v.strip()
                elif k.strip() == 'mode':
                    result["review_mode"] = v.strip()

    # Extract ::FINDING blocks
    finding_pattern = re.compile(
        r'::FINDING\{([^}]+)\}\s*\n(.*?)(?=::FINDING|::END|$)',
        re.DOTALL
    )
    for match in finding_pattern.finditer(content):
        attrs_str = match.group(1)
        body = match.group(2).strip()

        finding = {}
        for pair in attrs_str.split('|'):
            if ':' in pair:
                k, v = pair.split(':', 1)
                finding[k.strip()] = v.strip()

        # Parse body lines (issue: / fix:)
        for line in body.split('\n'):
            line = line.strip()
            if line.startswith('issue:'):
                finding['title'] = line[6:].strip()
            elif line.startswith('fix:'):
                finding['fix'] = line[4:].strip()

        if finding:
            result["findings"].append(finding)

    # LGTM check
    if not result["findings"] and 'LGTM' in content.upper():
        result["decision"] = "pass"

    # If we found a ::REVIEW but no explicit decision, judge from findings (v5.0):
    # a critical only forces fail when its confidence is solid. Low-conf criticals
    # (conf < 0.50) are treated as warnings for the pass/fail gate.
    if result["decision"] == "unknown" and result["findings"]:
        def solid_critical(f):
            if f.get("severity") != "critical":
                return False
            try:
                return float(f.get("conf", "1.0")) >= 0.50
            except (TypeError, ValueError):
                return True  # unspecified conf = treat as solid, fail-safe
        result["decision"] = "fail" if any(solid_critical(f) for f in result["findings"]) else "pass"

    return result if review_match else None


def call_api(config, system_prompt, diff_content):
    base_url = config.get("base_url", "https://api.deepseek.com/v1").rstrip("/")
    api_key = (
        os.environ.get("CLAUDE_PLUGIN_OPTION_API_KEY")
        or os.environ.get(config.get("api_key_env", ""), "")
        or os.environ.get("IREVIEW_API_KEY", "")
        or config.get("api_key", "")
    )
    model = config.get("model", "deepseek/deepseek-chat")
    timeout = config.get("timeout_sec", 120)

    if not api_key:
        return {"error": "No API key. Set api_key in config, IREVIEW_API_KEY env var, or use /ireview:setup."}

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

            # Try I-Lang format first (::REVIEW ... ::END)
            ilang_result = parse_ilang_response(content)
            if ilang_result:
                return ilang_result

            # Fallback: try JSON
            try:
                clean = content.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
                result = json.loads(clean)
                result["format"] = "json"
                return result
            except json.JSONDecodeError:
                pass

            # Fallback: plain text
            if "LGTM" in content.upper():
                return {"findings": [], "decision": "pass", "format": "text"}
            return {"raw_response": content, "decision": "unknown", "format": "text"}

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
