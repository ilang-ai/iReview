# iReview

Universal AI-to-AI code review. Read `skills/ireview/SKILL.md` for the full review protocol.

When user asks to review code, read `.ireview.json` for model config, get the diff, call the external API per SKILL.md, and present findings. Save results to `.ireview/reviews/`.

Commands: `/ireview`, `/ireview:adversarial`, `/ireview:setup`, `/ireview:status`
