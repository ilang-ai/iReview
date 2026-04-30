# /ireview:adversarial — Adversarial Code Review

Devil's advocate review. The external model challenges design decisions, questions assumptions, and probes failure modes.

## Steps

Same as `/ireview:review` but pass `--mode adversarial` to the script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py \
  --config .ireview.json \
  --mode adversarial \
  --diff "$(git diff HEAD)"
```

## Output format

```
═══ iReview ═══ ADVERSARIAL ═══ [model] ═══

🔴 CRITICAL: will break production
⚔️  CHALLENGE: design decision that needs justification
🔄 ALTERNATIVE: simpler/safer approach to consider

═══ end ═══
```
