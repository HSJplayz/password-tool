#!/usr/bin/env python3
"""
Password Tool
=============
A security-focused CLI with two halves:
  1. Generate cryptographically strong, predictable passwords (pure stdlib random).
  2. Check the strength of any password using the same entropy-based model.

Built to be transparent: uses Python's `secrets` module (not `random`) so the
output is cryptographically secure. No password is ever stored or sent anywhere.

Used as Day 3 of the daily projects streak.
"""

from __future__ import annotations

import argparse
import math
import secrets
import string
import sys
from typing import Iterable

# --------------------------------------------------------------------------- #
# Character sets & entropy estimation
# --------------------------------------------------------------------------- #
LOWERS = string.ascii_lowercase
UPPERS = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"

# Human-readable description for each complexity tier.
TIERS: list[tuple[str, str]] = [
    ("symbols", "upper + lower + digits + symbols"),
    ("upper",   "upper + lower + digits"),
    ("lower",   "lower + digits"),
    ("digits",  "digits only"),
]


# --------------------------------------------------------------------------- #
# Entropy calculations
# --------------------------------------------------------------------------- #
def alphabet_size_for(tier: str) -> int:
    """Number of possible characters in a given tier's pool."""
    mapping = {
        "digits": len(DIGITS),
        "lower": len(LOWERS) + len(DIGITS),
        "upper": len(UPPERS) + len(LOWERS) + len(DIGITS),
        "symbols": len(UPPERS) + len(LOWERS) + len(DIGITS) + len(SYMBOLS),
    }
    return mapping[tier]


def entropy_bits(length: int, pool_size: int) -> float:
    """Entropy in bits = length * log2(pool_size)."""
    if length <= 0 or pool_size <= 0:
        return 0.0
    return length * math.log2(pool_size)


def tier_of_password(password: str) -> str:
    """Classify an existing password into the highest tier it satisfies."""
    has_lower = any(c in LOWERS for c in password)
    has_upper = any(c in UPPERS for c in password)
    has_digit = any(c in DIGITS for c in password)
    has_symbol = any(c in SYMBOLS for c in password)
    if has_upper and has_lower and has_digit and has_symbol:
        return "symbols"
    if has_upper and has_lower and has_digit:
        return "upper"
    if (has_lower or has_upper) and has_digit:
        return "lower"
    return "digits"


def check_strength(password: str) -> dict:
    """Assess a password and return a report dict."""
    length = len(password)
    pool = alphabet_size_for(tier_of_password(password))
    bits = entropy_bits(length, pool)

    if bits < 40:
        grade, color = "WEAK", "red"
    elif bits < 60:
        grade, color = "FAIR", "yellow"
    elif bits < 80:
        grade, color = "GOOD", "cyan"
    else:
        grade, color = "STRONG", "green"

    # Human-readable "crack time" estimate at 1e9 guesses/sec.
    seconds = (2 ** bits) / 1e9 * 0.5
    crack = _human_duration(seconds)

    return {
        "length": length,
        "pool": pool,
        "bits": bits,
        "grade": grade,
        "color": color,
        "crack_time": crack,
        "tier": tier_of_password(password),
    }


def _human_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds*1000:.1f} milliseconds"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    if seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    if seconds < 86400 * 365:
        return f"{seconds/86400:.1f} days"
    if seconds < 86400 * 365 * 1e6:
        return f"{seconds/(86400*365):.0f} years"
    return f"{seconds/(86400*365*1e6):.1f} million years"


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #
def generate(length: int, tier: str) -> str:
    """Generate a random password of the requested length and tier."""
    if length < 4:
        raise ValueError("length must be at least 4")

    # Our tiers: symbols (default/strongest) | upper | lower | digits
    if tier == "upper":
        pool = UPPERS + LOWERS + DIGITS
    elif tier == "lower":
        pool = LOWERS + DIGITS
    elif tier == "digits":
        pool = DIGITS
    else:  # symbols
        pool = UPPERS + LOWERS + DIGITS + SYMBOLS

    # Guarantee at least one char from each required class (if it fits).
    required: list[str] = []
    if tier == "symbols":
        required = [LOWERS, UPPERS, DIGITS, SYMBOLS]
    elif tier == "upper":
        required = [LOWERS, UPPERS, DIGITS]
    elif tier == "lower":
        required = [LOWERS, DIGITS]
    elif tier == "digits":
        required = [DIGITS]

    if length < len(required):
        required = required[:length]

    chars = [secrets.choice(r) for r in required]
    remaining = length - len(chars)
    chars += [secrets.choice(pool) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_many(count: int, length: int, tier: str) -> Iterable[str]:
    for _ in range(count):
        yield generate(length, tier)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def format_report(r: dict) -> str:
    return (
        f"  Length       : {r['length']} chars\n"
        f"  Character set: {r['pool']} possibilities\n"
        f"  Entropy      : {r['bits']:.1f} bits\n"
        f"  Grade        : {r['grade']}\n"
        f"  Est. crack   : {r['crack_time']} (brute force @1e9/s)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="password",
        description="Generate secure passwords and check password strength.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("gen", help="Generate secure passwords")
    gen.add_argument("-n", "--count", type=int, default=1, help="How many to generate")
    gen.add_argument("-l", "--length", type=int, default=16, help="Password length")
    gen.add_argument("-t", "--tier", choices=["symbols", "upper", "lower", "digits"],
                     default="symbols", help="Complexity tier (default: symbols)")
    gen.add_argument("--show-check", action="store_true",
                     help="Also print a strength check for each generated password")

    chk = sub.add_parser("check", help="Check a password's strength")
    chk.add_argument("password", nargs="?", help="Password to check (omit for prompt)")
    chk.add_argument("--strength", action="store_true",
                     help="Force a strict grade even for short inputs")

    args = parser.parse_args(argv)

    if args.command == "gen":
        try:
            for pw in generate_many(args.count, args.length, args.tier):
                print(pw)
                if args.show_check:
                    print(format_report(check_strength(pw)))
                    print("-" * 40)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2

    elif args.command == "check":
        pw = args.password
        if pw is None:
            pw = input("Enter password to check: ")
        r = check_strength(pw)
        print(format_report(r))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
