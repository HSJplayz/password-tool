# 🔑 Password Tool

> Generate cryptographically strong passwords and check password strength — a transparent, no-dependency CLI built on Python's `secrets` module. Nothing is ever stored or sent anywhere.

## Table of Contents
- [Description](#description)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)
- [Future Scope](#future-scope)
- [License](#license)

## Description
This tool is two things in one:
1. **`gen`** — produces secure, random passwords with guaranteed character-class coverage (lower/upper/digit/symbol). It uses Python's **[`secrets`](https://docs.python.org/3/library/secrets.html)** module, which is cryptographically secure — unlike the built-in `random` module.
2. **`check`** — estimates a password's strength from **Shannon entropy** (bits = length × log₂(alphabet)) and shows a human-readable brute-force crack-time estimate.

Every evaluation is done **locally** — passwords are never logged, saved, or transmitted.

Built as **Day 3** of the [daily projects streak](https://github.com/HSJplayz/streak).

## Tech Stack
- **Python 3.10+** (standard library only — `secrets`, `string`, `math`, `argparse`)

## Features
### Generate (`gen`)
- `-n/--count` — generate multiple passwords at once.
- `-l/--length` — control length (default 16, min 4).
- `-t/--tier` — complexity tier: `symbols` (default) | `upper` | `lower` | `digits`.
- `--show-check` — print a full strength report under each generated password.
- **Guaranteed coverage** — each required character class is represented in the output.

### Check (`check`)
- Grade: `WEAK` / `FAIR` / `GOOD` / `STRONG` based on entropy.
- Reports length, alphabet size, entropy bits, and an estimated brute-force crack time.
- Accepts a direct argument or an interactive (non-echo-free) prompt.

## Installation
No install needed — Python 3.10+ is the only requirement.
```bash
git clone https://github.com/HSJplayz/password-tool.git
cd password-tool
```

## Usage
```bash
# Generate a 16-char password with full symbol set
python password.py gen

# Generate 5 strong passwords of length 20, with strength checks
python password.py gen -n 5 -l 20 --show-check

# Digits-only PIN generator (e.g. 6-digit)
python password.py gen -t digits -l 6

# Check a password's strength directly
python password.py check "MyP@ssw0rd2026!"

# Or via interactive prompt (omit the argument)
python password.py check
```

## Example
```bash
$ python password.py gen -n 2 -l 12 --show-check
k3#Fv9!pQzL@
  Length       : 12 chars
  Character set: 88 possibilities
  Entropy      : 77.5 bits
  Grade        : GOOD
  Est. crack   : 3.4 million years (brute force @1e9/s)
9@Yt&u2mXc$Q
  Length       : 12 chars
  Character set: 88 possibilities
  Entropy      : 77.5 bits
  Grade        : GOOD
  Est. crack   : 3.4 million years (brute force @1e9/s)

$ python password.py check "password123"
  Length       : 11 chars
  Character set: 36 possibilities
  Entropy      : 56.9 bits
  Grade        : FAIR
  Est. crack   : 2 years (brute force @1e9/s)

$ python password.py gen -t digits -l 6
979483
```

## Project Structure
```
password-tool/
  password.py    ← generator + checker (+ CLI)
  test_password.py
  README.md
  LICENSE        ← MIT
  .gitignore
```

## Security Notes
- Uses `secrets` for generation — cryptographically strong on the system entropy pool.
- **Do not rely on any crack-time estimate as absolute truth** — it assumes 10⁹ guesses/sec and ignores dictionary/pattern attacks. Real-world attackers use hybrid wordlists. Strength ratings are a heuristic to encourage *long, high-entropy* passwords.
- Recommendations: use length ≥ 16, enable a password manager, and enable 2FA.
- Nothing in this tool sends data over the network.

## Future Scope
- **Breach-check integration** — hash locally and check against a public HaveIBeenPwned k-anonymity API (still no password ever leaves the machine in full form).
- **Passphrase generator** — Diceware-style (EFF wordlist) with pronounceable output.
- **Entropy with dictionary/pattern awareness** — count common-password penalties.
- **`--clip`** — copy result to the clipboard (no echo to terminal history).
- **Interactive strength meter** — real-time typed-input grading.
- **Colorized TUI output** for grades/crack times.

## License
[MIT](LICENSE)
