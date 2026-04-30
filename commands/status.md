# /ireview:status — Review Status

Show review history and unresolved findings.

## Steps

1. Read `.ireview/state.json` for current phase.
2. List `.ireview/reviews/*.json` sorted newest first.
3. For latest review: show finding counts by severity, which are open/resolved.
4. For multi-round: compare current diff hash to review diff hash to detect if fixes were applied.

## Output

```
═══ iReview Status ═══

Current: review pending (3 files changed)

Latest: 20260430-153012 (deepseek-chat)
  🔴 1 critical (open)
  🟡 2 warnings (1 resolved, 1 open)

Previous: 20260429-091500 (gpt-4o)
  ✅ All resolved

═══ end ═══
```

## Arguments

- `/ireview:status` — latest
- `/ireview:status all` — full history
- `/ireview:status clean` — archive all to `.ireview/archive/`
