# v0.0.1 — Read-only cross-executor Skill Audit

First formal tagged release of the existing Claude Skill Audit repository.

## Highlights

- Keep the original guided inventory, usage heat, rule–execution-gap, trigger-conflict and outdated-pattern workflow.
- Add a Python 3.9+ standard-library-only CLI for local Skill inventory and **recorded** calls across explicitly supplied Claude TSV and generic executor CSV events.
- Make missing executor logs `unknown`, not invented zeros; a log being present never proves full-window coverage.
- Ship synthetic examples, six CLI tests, an AI prompt, an A/B task-effectiveness template and bilingual documentation.

## Behavior change / migration

The guided `SKILL.md` now returns read-only findings by default rather than automatically writing a dated report into the user's configuration directory. If you previously depended on automatic baseline files, explicitly ask your assistant to save the report to a chosen location after reviewing it.

## Privacy and limitations

No network upload, automatic log collection, install hook, account operation, deletion or settings change. Published examples are synthetic; share any real report only after reviewing Skill names and content for sensitive details. Python 3.9 compatibility is a supported syntax target; local test evidence in this release was on Python 3.12.14.

See [CHANGELOG.md](CHANGELOG.md) and [install.md](install.md).
