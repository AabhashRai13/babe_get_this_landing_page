#!/usr/bin/env python3
"""Invariant checks for the static site (stdlib only).

Run from the repo root:  python3 scripts/check_site.py
Prints "FAIL <name>: <detail>" for each failing check and exits 1 if any fail.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "ios.html", "privacy-policy.html", "terms.html", "delete-account.html"]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def luminance(hex_colour: str) -> float:
    h = hex_colour.strip().lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def css_tokens(block: str) -> dict:
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", block)}


def root_block(css: str) -> str:
    m = re.search(r"^:root\s*\{(.*?)^\}", css, re.S | re.M)
    return m.group(1) if m else ""


def dark_root_block(css: str) -> str:
    m = re.search(r"@media \(prefers-color-scheme: dark\)\s*\{\s*:root\s*\{(.*?)\}", css, re.S)
    return m.group(1) if m else ""


LIGHT = {
    "--blue": "#3A63B8", "--blue-light": "#4F7BD3", "--yellow": "#FFD45C", "--navy": "#14254A",
    "--grey": "#EDF1F4", "--white": "#FFFFFF", "--text": "#14254A", "--text-2": "#44516A",
    "--on-blue": "#FFFFFF", "--on-blue-2": "#E6EDFB",
}
BEIGE = ["#EAD8CB", "#795548", "#3E2723", "#A1887F", "#4A392E"]


def check_tokens_light():
    tokens = css_tokens(root_block(read("styles.css")))
    bad = [f"{k}={tokens.get(k)}" for k, v in LIGHT.items() if (tokens.get(k) or "").upper() != v.upper()]
    if '"Anton"' not in tokens.get("--display", ""):
        bad.append(f"--display={tokens.get('--display')}")
    return ", ".join(bad) or None


def check_no_beige():
    css = read("styles.css").upper()
    found = [c for c in BEIGE if c in css]
    return f"found {found}" if found else None


def _contrast_pairs(tokens: dict):
    t = lambda k: tokens[k]
    return [
        ("--on-blue on --blue", contrast(t("--on-blue"), t("--blue")), 4.5),
        ("--on-blue-2 on --blue", contrast(t("--on-blue-2"), t("--blue")), 4.5),
        ("--yellow on --blue", contrast(t("--yellow"), t("--blue")), 3.0),
        ("--text-2 on --grey", contrast(t("--text-2"), t("--grey")), 4.5),
        ("--text-2 on --white", contrast(t("--text-2"), t("--white")), 4.5),
        ("--text on --white", contrast(t("--text"), t("--white")), 4.5),
        ("--navy on --yellow", contrast(t("--navy"), t("--yellow")), 4.5),
    ]


def _check_contrast(tokens: dict):
    try:
        low = [f"{n} {r:.2f}<{need}" for n, r, need in _contrast_pairs(tokens) if r < need]
    except (KeyError, ValueError) as e:
        return f"missing/invalid token {e}"
    return ", ".join(low) or None


def check_contrast_light():
    return _check_contrast(css_tokens(root_block(read("styles.css"))))


def check_contrast_dark():
    css = read("styles.css")
    tokens = css_tokens(root_block(css))
    dark = css_tokens(dark_root_block(css))
    if not dark:
        return "no dark-mode :root block"
    tokens.update(dark)
    return _check_contrast(tokens)


def check_fonts_loaded():
    bad = []
    for page in PAGES:
        links = re.findall(r'href="(https://fonts\.googleapis\.com/css2\?[^"]+)"', read(page))
        if not any("family=Anton" in l and "family=Nunito" in l and "display=swap" in l for l in links):
            bad.append(page)
    return f"missing Anton+Nunito link: {bad}" if bad else None


CHECKS = [
    ("tokens_light", check_tokens_light),
    ("no_beige", check_no_beige),
    ("contrast_light", check_contrast_light),
    ("contrast_dark", check_contrast_dark),
    ("fonts_loaded", check_fonts_loaded),
]


def main() -> int:
    failures = 0
    for name, fn in CHECKS:
        detail = fn()
        if detail:
            failures += 1
            print(f"FAIL {name}: {detail}")
    print(f"{len(CHECKS) - failures}/{len(CHECKS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
