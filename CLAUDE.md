# iReview — AI-to-AI Code Review

If installed as Claude Code plugin: use `${CLAUDE_PLUGIN_ROOT}/scripts/ireview.sh`
If this repo is cloned into your project: use `./scripts/ireview.sh`

## Quick Start
```bash
# Setup
cp .ireview.example.json .ireview.json  # edit model + API key

# Review
bash scripts/ireview.sh review

# Review specific files
bash scripts/ireview.sh review src/auth.ts

# Adversarial review
bash scripts/ireview.sh review --adversarial

# Cancel pending review
bash scripts/ireview.sh cancel
```

See `skills/ireview/SKILL.md` for the full I-Lang review protocol.
