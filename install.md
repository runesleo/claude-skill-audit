# Install / first success (AI-agent friendly)

This repository has **two complementary entry points**. Start with the offline CLI if you only want a verified sample report; install the guided Claude Code Skill only if you want qualitative rule/conflict review.

## No-install, read-only demo (Python 3.9+)

From the repository root:

```bash
python3 cli/skill_audit.py \
  --skills-root cli/examples/skills \
  --claude-log cli/examples/claude.log \
  --event-csv cli/examples/events.csv \
  --expect-executor Gemini \
  --as-of 2026-11-12T00:00:00Z
```

Expected for **synthetic** fixtures: 2 Skills, 3 recorded calls, Gemini marked `unknown`. This is the read-only self-check: it never reads personal Skill definitions or logs.

## Guided Skill in Claude Code

```bash
git clone https://github.com/runesleo/claude-skill-audit "$HOME/.claude"/skills/skill-audit
```

Then ask Claude Code to run `/skill-audit`. If the directory already exists, review it before reinstalling; do not overwrite a local Skill. The guided audit must first establish actual paths and data provenance, then report inventory, observed usage, possible rule–execution gaps, conflicts and outdated instructions without changing installed Skills.

## Copyable instruction for any AI assistant

“Read [cli/PROMPT.md](cli/PROMPT.md) and perform a **read-only** Skill audit. First discover which executors and event sources actually exist. Never infer real zero usage from missing logs. Keep verified facts, open evidence gaps and recommendations separate. Ask before writing reports or changing configs.”

No credentials, account operations, new hooks, background schedulers, or publishing are part of installation. More details: [English README](README.md) / [中文说明](README.zh.md).
