#!/usr/bin/env python3
"""
Automated tests for the Password Tool.

Run with:  python test_password.py
Exit code 0 = all tests passed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import password as pw  # noqa: E402


PASS = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {extra}")
        sys.exit(1)


def test_generation() -> None:
    print("=== generation ===")
    pw1 = pw.generate(16, "symbols")
    check("symbols tier length correct", len(pw1) == 16, pw1)
    check("symbols tier has a symbol", any(c in pw.SYMBOLS for c in pw1), pw1)
    check("symbols tier has lower", any(c in pw.LOWERS for c in pw1), pw1)
    check("symbols tier has upper", any(c in pw.UPPERS for c in pw1), pw1)
    check("symbols tier has digit", any(c in pw.DIGITS for c in pw1), pw1)

    pin = pw.generate(6, "digits")
    check("digits tier length", len(pin) == 6, pin)
    check("digits tier only digits", all(c in pw.DIGITS for c in pin), pin)

    low = pw.generate(10, "lower")
    check("lower tier: no symbols/upper", all(c in (pw.LOWERS + pw.DIGITS) for c in low), low)

    # two outputs should differ (statistically) for a 16-char password
    pw2 = pw.generate(16, "symbols")
    check("two outputs differ", pw1 != pw2, f"{pw1} vs {pw2}")

    # random distribution sanity: uniqueness across a batch
    batch = {pw.generate(24, "symbols") for _ in range(200)}
    check("200x24-char batch all unique", len(batch) == 200, str(len(batch)))


def test_check() -> None:
    print("=== check ===")
    strong = pw.check_strength("aA1!xYz9#Qw@ErT5zZ0&")
    check("long mixed -> STRONG", strong["grade"] == "STRONG", str(strong))

    weak = pw.check_strength("12345")
    check("short digits -> WEAK", weak["grade"] == "WEAK", str(weak))

    fair = pw.check_strength("password123")
    check("dictionary-ish -> FAIR/GOOD not STRONG", fair["grade"] != "STRONG", str(fair))

    check("entropy formula 100 bits", abs(pw.entropy_bits(20, 32) - 100.0) < 0.001)

    tier = pw.tier_of_password("Ab3!xyz")
    check("tier detects symbols", tier == "symbols", str(tier))
    tier2 = pw.tier_of_password("abc123")
    check("tier detects lower+digits", tier2 == "lower", str(tier2))


def test_cli() -> None:
    print("=== CLI subprocess ===")
    import subprocess

    base = [sys.executable, str(Path(__file__).parent / "password.py")]
    r = subprocess.run([*base, "gen", "-t", "digits", "-l", "6"], capture_output=True, text=True)
    out = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    check("cli gen digits works", out and len(out) == 6 and out.isdigit(), (out, r.stderr))

    r = subprocess.run([*base, "gen"], capture_output=True, text=True)
    out = r.stdout.strip() if r.stdout.strip() else ""
    check("cli gen default 16 strong", len(out) == 16, (out, r.stderr))


def main() -> int:
    test_generation()
    test_check()
    test_cli()
    print(f"\nAll {PASS} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
