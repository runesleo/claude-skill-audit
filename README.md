# claude-skill-audit

English · [中文](README.zh-CN.md)

> A health check for your Claude Code skill tree. Find what's actually used, what's dead, what's stepping on each other, and which iron-rule skills you wrote but never fired.

## What you get

- **Inventory** — how many skills, hooks, aliases you have
- **Usage ranking** — real invocation counts (data source: `~/.claude/skill-usage.log`, written by a PreToolUse hook)
- **Dead skill detection** — 30 days of zero triggers + no hook binding + no `CLAUDE.md` reference → archive candidate
- **Rule-execution gap** — the killer feature: skills your iron rules say must fire, but never did. Writing rules and not running them is the same as not writing them.
- **Conflict diagnostics** — skill groups with overlapping trigger words

Doesn't auto-delete. Surfaces candidates, you decide. Suggested workflow: move to `_archived/`, observe for 30 days, then permanently remove.

## How it works

```
You: /skill-audit

AI:
📊 Skill Tree Audit — 2026-04-17

📈 Inventory: 61 skills / 4 hooks / 12 aliases
🔥 Top 5 by usage:
   session-end(262) / leo-style(182) / codex:rescue(119) / codex(112) / humanizer(92)
   — top 5 = 92% of total calls. Long tail of 40+ skills averages <10.

💀 Dead candidates (15):
   auto-dream / content-analyzer / design-review / graphify / mcp-builder /
   notebooklm / obsidian-sync / search-skill / skill-from-github /
   skill-from-masters / subagent-driven-development / tempo-request /
   video-auto / video-distribute / workflow-architect

⚠️ Rule-execution gap (6 skills, 0 calls despite rule references):
   systematic-debugging — P0 rule "trigger on 3 consecutive failures",
                          fired exactly 0 times in 1388 invocations
   planning-with-files / opensource-publish / leo-evolution /
   tg-review / video-editing-coach

🧹 Outdated patterns: 5 entries flagged, see patterns.md

🎯 Action items:
- [ ] Archive 15 dead candidates
- [ ] Investigate the gap — your rules say one thing, your runtime does another
- [ ] Clean outdated patterns
```

The dead skill count is not the interesting part. The interesting part is the **rule-execution gap**: skills your P0 rules require, with zero actual invocations. The gap between what you wrote down and what actually runs is real, and most people don't measure it.

## Setup

**Claude Code:**

```bash
git clone https://github.com/runesleo/claude-skill-audit ~/.claude/skills/skill-audit
```

Then trigger: `/skill-audit` or "run a skill tree health check".

**Other AI harnesses:**

`SKILL.md` is plain markdown with bash blocks. Port the logic — there's nothing Claude-specific about counting invocations or grepping for references.

## Requirements

- Claude Code with at least a handful of skills configured
- A PreToolUse hook writing to `~/.claude/skill-usage.log` (the audit is only as good as its data source — without auto-instrumentation, you're guessing)
- Standard skill directory at `~/.claude/skills/`

That's it. No API keys, no external services, no LLM calls — pure local file inspection.

## Design philosophy

- **No auto-delete** — skills are muscle memory. Some "dead" skills are seasonal (a weekly review fires once a week).
- **Archive over delete** — candidates go to `_archived/` with a 30-day window. Easy to revive if you missed something.
- **Human in the loop** — the audit identifies, you decide. No autonomous cleanup.
- **Data foundation first** — without the PreToolUse hook writing `skill-usage.log`, this skill is just printing vibes.

## Inspiration

Born from [@HiTw93](https://x.com/HiTw93)'s [Waza](https://github.com/tw93/Waza) (MIT). Waza decomposes engineering into 8 dimensions (think / design / hunt / check / read / write / learn / health) and turns each into a runnable Claude skill. When I mapped my 62 skills against those 8 dimensions, the `/health` slot was empty — nobody was auditing what was used, dead, or conflicting. This skill exists to fill that slot. **Without Waza, this skill wouldn't exist.**

The horizontal scanning logic (dead candidate detection, conflict diagnostics, expired pattern flagging, report formatting) is local implementation.

## Roadmap

**Detection**
- [ ] Orphan reference detection — hook references a skill that no longer exists in `~/.claude/skills/`
- [ ] Cross-machine audit — reconcile local Mac with remote VPS skill state
- [ ] Baseline diff — highlight what changed since the last audit

**Reporting**
- [ ] HTML dashboard with trend visualization over time
- [ ] Export to Obsidian Daily Note format
- [ ] Slack / Discord webhook for scheduled audits

## About the author

*Leo ([@runes_leo](https://x.com/runes_leo)) — AI × Crypto independent builder. Trading on [Polymarket](https://polymarket.com/?via=runes-leo&r=runesleo&utm_source=github&utm_content=claude-skill-audit), building data and trading systems with Claude Code and Codex.*

*[leolabs.me](https://leolabs.me) — writing · community · open-source tools · indie projects · all platforms.*

*[X Subscription](https://x.com/runes_leo/creator-subscriptions/subscribe) — paid content weekly, or just buy me a coffee 😁*

*Learn in public, Build in public.*

## License

MIT — fork freely. When you do, keep the credit to [@HiTw93's Waza](https://github.com/tw93/Waza) so the chain stays intact.
