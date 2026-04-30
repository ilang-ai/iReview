# /ireview:cancel — Cancel Review

Cancel a pending or in-progress review and allow stop.

## Steps

1. Set `.ireview/state.json` phase to `cancelled`.
2. If auto_review was blocking stop: clear the block.
3. Confirm: "Review cancelled. You can stop the session now."
