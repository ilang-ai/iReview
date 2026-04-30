# /ireview:adversarial — Adversarial Code Review

Devil's advocate review via I-Lang protocol. The external model challenges design decisions, questions assumptions, and probes failure modes.

Protocol: `[EVAL:@DIFF|depth=adversarial]=>[SCAN|whr=assumptions,failure_modes]=>[CLSF]=>[OUT]`

## Steps

Same as `/ireview:review` but pass `--mode adversarial` to the script:

```bash
mkdir -p .ireview/tmp
git diff HEAD > .ireview/tmp/current.diff

python3 ${CLAUDE_PLUGIN_ROOT}/scripts/call-api.py \
  --config .ireview.json \
  --mode adversarial \
  --diff-file .ireview/tmp/current.diff
```

## Output format

```
═══ iReview ═══ ADVERSARIAL ═══ [model] ═══

🔴 CRITICAL: will break production
⚔️  CHALLENGE: design decision that needs justification
🔄 ALTERNATIVE: simpler/safer approach to consider

═══ end ═══
```
