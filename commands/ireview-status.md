# /ireview:status — Review Status and History

Show review findings and track multi-round resolution.

## What to do

1. List all files in `.ireview/reviews/` sorted by date (newest first).
2. For the most recent review, show:
   - Date and model used
   - Number of findings by severity
   - Which findings are still unresolved (check if the mentioned files/lines have changed since the review)
3. If user asks about a specific review: show its full content.

## Multi-round tracking

When user runs `/ireview` again after fixing issues:
1. Read the most recent review from `.ireview/reviews/`.
2. Include previous findings in the system prompt: "Previous review found these issues: [list]. Check if they were addressed. Report: RESOLVED for fixed issues, STILL OPEN for unfixed, NEW for newly introduced problems."
3. Save new review with reference to previous: `previous: review-[id].md` in header.

## Presentation

```
═══ iReview Status ═══

Latest: review-1714300800.md (2026-04-28, deepseek-chat)
  🔴 1 critical (unresolved)
  🟡 2 warnings (1 resolved, 1 open)

Previous: review-1714214400.md (2026-04-27, gpt-4o)
  ✅ All 3 findings resolved

═══ end ═══
```

## Arguments

- `/ireview:status` — show latest
- `/ireview:status all` — show all reviews
- `/ireview:status clear` — archive all reviews to `.ireview/archive/`
