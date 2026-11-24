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
    detail = _check_contrast(tokens)
    extra = [f"--blue-light on {bg} {contrast(tokens['--blue-light'], tokens[bg]):.2f}<4.5"
             for bg in ("--white", "--grey") if contrast(tokens["--blue-light"], tokens[bg]) < 4.5]
    return ", ".join(filter(None, [detail] + extra)) or None


def check_fonts_loaded():
    bad = []
    for page in PAGES:
        links = re.findall(r'href="(https://fonts\.googleapis\.com/css2\?[^"]+)"', read(page))
        if not any("family=Anton" in l and "family=Nunito" in l and "display=swap" in l for l in links):
            bad.append(page)
    return f"missing Anton+Nunito link: {bad}" if bad else None


def section(html: str, cls: str) -> str:
    """Inner HTML of the first <section> whose class list contains cls."""
    m = re.search(r'<section class="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*>(.*?)</section>', html, re.S)
    return m.group(1) if m else ""


def main_html() -> str:
    m = re.search(r"<main\b.*?</main>", read("index.html"), re.S)
    return m.group(0) if m else ""


def check_hero_tells_removed():
    hero = section(read("index.html"), "hero")
    if not hero:
        return "no hero section"
    bad = [t for t in ['class="badge', 'class="trust', "<em>", "🛒", "📱"] if t in hero]
    return f"still present: {bad}" if bad else None


def check_hero_meta():
    hero = section(read("index.html"), "hero")
    metas = re.findall(r'<p class="meta ([^"]*)"[^>]*>(.*?)</p>', hero, re.S)
    kinds = sorted(k.strip() for k, _ in metas)
    if kinds != ["not-ios", "only-ios"]:
        return f"meta paragraphs: {kinds}"
    android = next(t for k, t in metas if k.strip() == "not-ios")
    if "Free · No ads · Private unless you share" not in re.sub(r"<[^>]+>", "", android):
        return "not-ios meta copy differs"
    return None


def check_theme_color():
    return None if '<meta name="theme-color" content="#3A63B8">' in read("index.html") else "theme-color not #3A63B8"


def check_skip_link():
    html = read("index.html")
    body = re.search(r"<body>\s*(<[^>]+>)", html)
    if not body or body.group(1) != '<a class="skip" href="#main">':
        return f"first body element is {body.group(1) if body else None}"
    return None if re.search(r'<main[^>]*id="main"', html) else "<main> has no id=main"


def check_nav_icon():
    img = re.search(r'<nav class="nav">\s*(<img[^>]+>)', read("index.html"))
    if not img:
        return "no nav img"
    tag = img.group(1)
    bad = [a for a in ['width="40"', 'height="40"', 'alt=""'] if a not in tag]
    return f"nav img missing {bad}" if bad else None


def check_header_spacing():
    css = read("styles.css")
    header = re.search(r"^header\s*\{([^}]*)\}", css, re.M)
    nav = re.search(r"^\.nav\s*\{([^}]*)\}", css, re.M)
    bad = []
    if not header or not re.search(r"padding:\s*28px\b", header.group(1)):
        bad.append("header padding not 28px")
    if not nav or not re.search(r"gap:\s*30px", nav.group(1)):
        bad.append(".nav gap not 30px")
    return ", ".join(bad) or None


def check_no_eyebrows_home():
    return 'class="eyebrow"' if 'class="eyebrow"' in read("index.html") else None


def check_h2_display():
    h2s = re.findall(r"<h2([^>]*)>", main_html())
    bad = [a for a in h2s if not re.search(r'class="[^"]*\bdisplay\b', a)]
    return f"{len(bad)} h2 without .display" if bad or not h2s else None


def check_ramble_callouts():
    sec = re.search(r'<section[^>]*id="how"[^>]*>(.*?)</section>', read("index.html"), re.S)
    if not sec:
        return "no #how section"
    body = sec.group(1)
    tags = [re.sub(r"<[^>]+>", "", t).strip() for t in re.findall(r'class="tag"[^>]*>(.*?)</span>', body, re.S)]
    bad = [t for t in ["You", "Sorted by aisle"] if t not in tags]
    for alt in ["Voice capture screen listening, with a 0:12 timer and a Stop button",
                "The resulting list, grouped into Bakery, Dairy and Fruit categories with quantities"]:
        if f'alt="{alt}"' not in body:
            bad.append(f"alt changed: {alt[:30]}")
    return f"missing {bad}" if bad else None


PRIVACY = ("Use it as a guest and your lists stay on your phone. Sign in and they sync to your account, "
           "so they come back on a new phone. Only lists you share can be seen by anyone else.")


def check_privacy_copy():
    html = read("index.html")
    if "never leave your phone" in html:
        return "stale 'never leave your phone' copy"
    band = re.search(r'class="band privacy-band".*?<p>(.*?)</p>', html, re.S)
    if not band or re.sub(r"\s+", " ", band.group(1)).strip() != PRIVACY:
        return f"privacy paragraph is {band.group(1).strip()[:60] if band else None!r}"
    return None


def check_no_lock_emoji():
    html = read("index.html")
    bad = [t for t in ["🔒", 'class="lock"'] if t in html]
    return f"found {bad}" if bad else None


def check_chat_role():
    m = re.search(r'<div class="chat"([^>]*)>', read("index.html"))
    if not m:
        return "no .chat"
    attrs = m.group(1)
    return None if 'role="img"' in attrs and "aria-label=" in attrs else f"chat attrs: {attrs.strip()}"


def check_faq_marker():
    css = read("styles.css")
    bad = []
    if not re.search(r"\.faq-item summary::-webkit-details-marker\s*\{[^}]*display:\s*none", css):
        bad.append("webkit marker not hidden")
    if not re.search(r"\.faq-item summary\s*\{[^}]*list-style:\s*none", css):
        bad.append("summary list-style not none")
    if ".faq-item[open] summary::after" not in css:
        bad.append("no open-state marker")
    return ", ".join(bad) or None


def check_final_solid():
    m = re.search(r"^\.final\s*\{([^}]*)\}", read("styles.css"), re.M)
    if not m:
        return "no .final rule"
    return "gradient in .final" if "linear-gradient" in m.group(1) else None


def check_focus_visible():
    css = read("styles.css")
    m = re.search(r"([^{}]*:focus-visible[^{}]*)\{([^}]*)\}", css)
    if not m:
        return "no :focus-visible rule"
    sel, body = m.group(1), m.group(2)
    missing = [t for t in ["a", "button", "summary", "input"] if not re.search(r"(^|[\s,])" + t + r":focus-visible", sel)]
    if missing:
        return f"first :focus-visible rule misses {missing}"
    return None if re.search(r"outline:\s*3px", body) else "outline not 3px"


def check_ios_classes_styled():
    css = read("styles.css")
    missing = [c for c in [".badge", ".trust", ".eyebrow", ".demo-card", ".list-group", ".android-card"]
               if not re.search(re.escape(c) + r"\s*[{,]", css)]
    return f"no rule for {missing}" if missing else None


def check_no_undefined_vars():
    css = read("styles.css")
    defined = set(css_tokens(root_block(css)))
    used = set(re.findall(r"var\((--[\w-]+)", css))
    missing = sorted(used - defined)
    return f"undefined {missing}" if missing else None


CHECKS = [
    ("tokens_light", check_tokens_light),
    ("no_beige", check_no_beige),
    ("contrast_light", check_contrast_light),
    ("contrast_dark", check_contrast_dark),
    ("fonts_loaded", check_fonts_loaded),
    ("hero_tells_removed", check_hero_tells_removed),
    ("hero_meta", check_hero_meta),
    ("theme_color", check_theme_color),
    ("skip_link", check_skip_link),
    ("nav_icon", check_nav_icon),
    ("header_spacing", check_header_spacing),
    ("no_eyebrows_home", check_no_eyebrows_home),
    ("h2_display", check_h2_display),
    ("ramble_callouts", check_ramble_callouts),
    ("privacy_copy", check_privacy_copy),
    ("no_lock_emoji", check_no_lock_emoji),
    ("chat_role", check_chat_role),
    ("faq_marker", check_faq_marker),
    ("final_solid", check_final_solid),
    ("focus_visible", check_focus_visible),
    ("ios_classes_styled", check_ios_classes_styled),
    ("no_undefined_vars", check_no_undefined_vars),
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
