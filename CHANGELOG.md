# Changelog

## v0.0.1 — 2026-11-12

First formal tagged release of the existing `claude-skill-audit` repository.

- Retained the original AI-guided Skill inventory, usage heat, rule–execution gap, trigger conflict and outdated-pattern review.
- Added a Python 3.9+ standard-library-only, offline **read-only** CLI for observed usage and cross-executor source visibility. Explicitly reported missing event sources as `unknown` instead of claiming zero real use.
- Added six end-to-end tests, synthetic event/Skill fixtures, a copyable no-install AI audit prompt, and a real-task Skill ON/OFF effectiveness comparison template.
- Replaced historical personal-use counts in public examples with clearly labeled synthetic data; consolidated Chinese docs and clarified limitations and privacy boundaries.
- Changed guided Skill report persistence from an automatic write to read-only output by default; ask for an explicit report destination before saving a baseline.
- Added a first-success agent guide and release notes; ensured the synthetic Hook log fixture is included despite the general `*.log` ignore rule.

No automatic Skill/config changes, event collection, network transmission, deletion, or publishing to social platforms.
