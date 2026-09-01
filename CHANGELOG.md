# Changelog

All notable changes to the Password Tool.

## [1.0.0] - 2026-08-29 (Day 3)
### Added
- `gen` command: cryptographically secure password generation via `secrets`.
- Guaranteed character-class coverage in generated passwords (lower/upper/digit/symbol).
- Complexity tiers: `symbols` (default), `upper`, `lower`, `digits`; custom length and count.
- `check` command: entropy-based strength grading (WEAK / FAIR / GOOD / STRONG).
- Human-readable brute-force crack-time estimates.
- Local-only evaluation — passwords never leave the machine.
- Automated test suite (`test_password.py`, 18 checks).
- Full README, MIT license, `.gitignore`, dependencies manifest.