# claude-skill-audit

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue) ![License MIT](https://img.shields.io/badge/License-MIT-green)

English · [简体中文](README.zh.md)

> A read-only health check for AI Skills: what was **observed** in your logs, what might overlap, and which mandatory rules may not have been executed. Missing logs never prove non-usage.

## What you get

- **Inventory** — installed Skill definitions, with hooks and aliases inspected separately by the AI-guided audit
- **Usage heat** — observed invocation counts from logs you explicitly provide; never total real usage without complete instrumentation
- **Zero-observation review** — potential unused Skills, checked against hook bindings and rule references before any decision
- **Rule–execution gap** — mandatory Skill triggers with no supporting execution evidence; these are **investigation candidates**, not proven failures
- **Conflict diagnostics** — overlapping trigger wording and obsolete patterns for human review
- **Cross-executor companion CLI** — local, offline counts for Claude and other event sources, with explicit `unknown` coverage and a Skill ON/OFF comparison template

Nothing is installed, deleted, moved, or reconfigured by the CLI. No automated cleanup is performed. The AI-guided `SKILL.md` process also defaults to read-only review; any changes require your approval.

## How it works

```
You: /skill-audit

AI (SYNTHETIC EXAMPLE — not personal usage data):
Inventory: 3 Skills; logs: Claude present, Codex unknown
Observed in supplied log: research(3), review(1), incident-response(0)
Possible rule-execution gap: incident-response is referenced by a rule,
  but there are no recorded calls in this limited source.
Next: verify event coverage and inspect a real applicable task.
Conflict candidate: research / review share trigger terms; inspect descriptions.
Recommendation: keep, repair triggers, or monitor — no auto-delete.
```

The useful discovery is not a dramatic “dead Skill” count. It is whether **instructions, actual triggers, logs, and task outcomes** agree. A zero in a single Hook log is an observation, not proof that a Skill never ran.

## Setup

**Claude Code:**

```bash
git clone https://github.com/runesleo/claude-skill-audit "$HOME/.claude"/skills/skill-audit
```

Then trigger: `/skill-audit` or "run a skill tree health check".

**Any harness: run the read-only CLI.** Python 3.9+ (standard library; no installation):

```bash
python3 cli/skill_audit.py \
  --skills-root cli/examples/skills \
  --claude-log cli/examples/claude.log \
  --event-csv cli/examples/events.csv \
  --expect-executor Claude \
  --expect-executor Codex \
  --expect-executor Gemini \
  --as-of 2026-11-12T00:00:00Z
```

This uses **synthetic data** and works offline. For your own inventory, replace `--skills-root` with your real Skill directory; only pass log paths that actually exist. A custom Claude Hook TSV may be supplied with `--claude-log`; a generic CSV uses `timestamp,executor,skill` with `--event-csv`. Instrumentation is not installed by this tool.

See [CLI usage](cli/README.md), [copy-and-run AI prompt](cli/PROMPT.md), and [task effectiveness A/B template](cli/AB_TEMPLATE.md). The CLI covers inventory, recorded use and missing coverage; `SKILL.md` provides the human-guided **rule gap, overlap, and obsolete-pattern review**. Neither component claims it can automatically prove that a Skill is safe to delete.

## Requirements

- For the Claude skill: Claude Code with Skills configured; usage counts require an actual, validated event source
- For the CLI: Python 3.9+, a local Skill directory and optional existing log files
- `~/.claude/skill-usage.log` is an **optional custom-hook convention**, not a default Claude Code log

No API keys, external services, network upload, or auto-installation. The CLI reads only explicitly provided inputs and prints a report.

## Verified (local release-candidate checks)

- On 2026-11-12, **6/6 end-to-end tests passed** with Python **3.12.14**; the CLI compiled, and the source repository passed the project's security preflight with exit code 0.
- The committed **synthetic** demo finds 2 Skills and 3 recorded invocations; Claude/Codex have supplied example event sources and Gemini is reported as `unknown`.
- These checks do **not** prove continuous real-world event coverage, Python 3.9 runtime testing, or actual performance gains on user projects.

Try the same checks yourself:

```bash
python3 -m unittest discover -s cli/tests -v
python3 cli/skill_audit.py --skills-root cli/examples/skills \
  --claude-log cli/examples/claude.log --event-csv cli/examples/events.csv \
  --expect-executor Gemini --as-of 2026-11-12T00:00:00Z
```

## Privacy and known limitations (v0.0.1)

- This CLI reads only explicitly provided local Skill directory metadata and event files. It does **not** read or execute Skill bodies, write files, install hooks, connect to X or contact any service.
- Skill folder names can themselves be private. Review any report before sharing. All committed fixtures are synthetic.
- Inventory is one Skill-directory level below each root; duplicate names across roots cannot be reliably attributed to distinct log events.
- Only supplied log rows can be counted. Log files may be incomplete, missing or misformatted; the CLI never claims complete coverage. Rule–execution gaps, trigger conflicts and stale patterns still require the guided `SKILL.md` review.
- File creation timestamps may be unavailable and are **not** proof of when a Skill was installed. No automatic decisions to archive or delete are made.

## Design philosophy

- **No auto-delete** — skills are muscle memory. Some "dead" skills are seasonal (a weekly review fires once a week).
- **Review before archive** — even an archive move is a separate, user-approved action; seasonal Skills may be rarely triggered.
- **Human in the loop** — investigate candidates against real tasks, then decide whether to keep, improve triggering or observe.
- **Evidence before claims** — missing instrumentation is `unknown`, not a measured zero; even supplied logs may have gaps.

## Inspiration

Inspired by [@HiTw93](https://x.com/HiTw93)'s [Waza](https://github.com/tw93/Waza) (MIT), especially its `/health` dimension, and by the broader Skill review discussion around [darwin-skill](https://github.com/alchaincyf/darwin-skill). Waza's eight dimensions made it obvious that the Skill collection itself also needs ongoing inspection. **Waza deserves the original conceptual credit.**

The horizontal scanning logic (dead candidate detection, conflict diagnostics, expired pattern flagging, report formatting) is local implementation.

## Roadmap

**Detection**
- [ ] Orphan reference detection — hook references a Skill that no longer exists in the configured Skill directory
- [ ] Cross-machine audit — reconcile local Mac with remote VPS skill state
- [ ] Baseline diff — highlight what changed since the last audit
- [x] Offline, cross-executor event import (explicitly provided CSV, not automatic instrumentation)

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
