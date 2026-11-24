# Landing Page Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle babegetthis.com's homepage in the Play Store look (Anton headlines, cobalt, yellow, navy) without changing its structure, and remove the template tells.

**Architecture:** Plain static site, no build step. All styling is in `styles.css`, shared by `index.html`, `ios.html` and the three legal pages. Only `index.html` markup changes. Shared classes that `ios.html` still uses are kept and restyled. A stdlib Python check script pins the invariants (tokens, contrast, removed tells, copy); visual checks run in the browser at desktop and phone widths.

**Tech Stack:** HTML, CSS, Google Fonts (Anton, Nunito), vanilla JS (unchanged), Python 3 stdlib for checks, `npx serve .` for local preview.

**Spec:** `docs/superpowers/specs/2026-11-24-landing-restyle-design.md` (mockup: `.superpowers/brainstorm/55463-1795493009/content/restyle-v4.html`, local only)

## Global Constraints

- Colours: blue `#3A63B8` (hero and final CTA), yellow `#FFD45C`, navy `#14254A`, grey `#EDF1F4`, white `#FFFFFF`. No beige, brown or peach anywhere (no `#EAD8CB`, `#795548`, `#3E2723`, `#A1887F`, `#4A392E`).
- Contrast: body text ≥ 4.5:1 on its background; Anton headlines (large) ≥ 3:1.
- Fonts: Anton for h1/h2 and step numerals, uppercase; Nunito for everything else. Load both from one Google Fonts link with `display=swap` on every page.
- Header: top padding 28px, gap between nav items 30px.
- Keep all copy, CTAs, links, `.not-ios`/`.only-ios` pairs, FAQ JSON-LD and screenshots as they are, except the privacy-band paragraph (Task 4).
- Do not touch `assets/landing.js`, `assets/platform.js`, `assets/waitlist.js`, `assets/delete-account.js`.
- `ios.html` markup is not edited; it must still render correctly.
- No new dependencies. `scripts/` and `docs/` are never uploaded to Hostinger.

## Review Focus

- Phone width (375px): the two-phone hero must not cause horizontal scroll, and the headline must not overflow. Pinned in Task 2, Step 6.
- iPhone visitors (`html.is-ios`): the hero meta line and every CTA must show the iOS variant, with no empty gap where the Android one was. Pinned in Task 2, Step 6.
- Dark mode: yellow, blue and navy surfaces must still pass contrast, and grey sections must not stay light. Pinned in Task 1 (contrast pairs for dark tokens) and Task 5, Step 4.
- `ios.html` still uses `.badge`, `.trust`, `.eyebrow`, `h1 em`, `.demo`, `.band.final`, `.steps`; restyling them must not break that page. Pinned in Task 5, Step 4.
- Keyboard users: every link, button and FAQ summary shows a visible focus ring on blue, navy, grey and white. Pinned in Task 5, Step 4.

---

## File Structure

- Create `scripts/check_site.py`: invariant checks (tokens, contrast, removed tells, copy, fonts). Run with `python3 scripts/check_site.py`; exit 0 when all pass and print `FAIL <name>: <detail>` per failure.
- Modify `styles.css`: tokens, typography, header, every homepage section, shared rules kept for `ios.html`, dark mode, focus.
- Modify `index.html`: hero, section markup, privacy copy, head (font link, theme-color, skip link).
- Modify `ios.html`, `privacy-policy.html`, `terms.html`, `delete-account.html`: only the `<head>` font link (add Anton).
- Modify `README.md`: one line saying not to upload `scripts/` and `docs/`.

---

### Task 1: Check script, tokens and fonts

**Files:**
- Create: `scripts/check_site.py`
- Modify: `styles.css:4-48` (`:root` tokens and dark-mode tokens)
- Modify: `<head>` font link in `index.html:12`, `ios.html`, `privacy-policy.html:12`, `terms.html`, `delete-account.html`
- Modify: `README.md` (Deploy section)

**Interfaces:**
- Produces: CSS custom properties used by every later task: `--blue: #3A63B8`, `--blue-light: #4F7BD3` (accents only, never behind body text), `--yellow: #FFD45C`, `--navy: #14254A`, `--grey: #EDF1F4`, `--white: #FFFFFF`, `--text: #14254A`, `--text-2: #44516A`, `--on-blue: #FFFFFF`, `--on-blue-2: #E6EDFB`, `--display: "Anton", Impact, sans-serif`. Dark mode redefines `--white`, `--grey`, `--text`, `--text-2` (navy surfaces) and keeps `--blue`, `--yellow`, `--navy`.
- Produces: `check_site.py` with `contrast(fg: str, bg: str) -> float`, `css_tokens(block: str) -> dict[str, str]`, a `CHECKS` list of `(name, fn)` where `fn() -> str | None` (detail on failure), and `main()`. Later tasks append checks to `CHECKS`.

- [ ] **Step 1: Write the failing checks** in `scripts/check_site.py`:
  - `tokens_light`: `:root` in `styles.css` has every light token above with exactly those values.
  - `no_beige`: none of `#EAD8CB`, `#795548`, `#3E2723`, `#A1887F`, `#4A392E` appear in `styles.css` (case-insensitive).
  - `contrast_light`: `contrast(--on-blue, --blue) >= 4.5`, `contrast(--on-blue-2, --blue) >= 4.5`, `contrast(--yellow, --blue) >= 3`, `contrast(--text-2, --grey) >= 4.5`, `contrast(--text-2, --white) >= 4.5`, `contrast(--navy, --yellow) >= 4.5`.
  - `contrast_dark`: the same pairs using the dark-mode values of `--text-2`, `--grey` and `--white`.
  - `fonts_loaded`: each of the 5 HTML pages has a `fonts.googleapis.com/css2?` link containing `family=Anton` and `family=Nunito` and `display=swap`.

- [ ] **Step 2: Run it and confirm it fails**

  Run: `python3 scripts/check_site.py`
  Expected: exit 1, with `FAIL tokens_light`, `FAIL no_beige`, `FAIL fonts_loaded` among the lines.

- [ ] **Step 3: Replace the `:root` and dark-mode token blocks** in `styles.css` with the Interfaces tokens. Repoint every existing `var(--…)` use of a removed token (`--bg`, `--card`, `--primary*`, `--accent`, `--secondary-container`, `--tertiary*`, `--ink`, `--on-ink`) to the nearest new token, so nothing references an undefined variable. Remove all hard-coded beige/brown hexes. Add `color-scheme: light dark` to `:root`.

- [ ] **Step 4: Update the font link on all 5 pages** to `https://fonts.googleapis.com/css2?family=Anton&family=Nunito:wght@400;600;700;800;900&display=swap`.

- [ ] **Step 5: Add to the README Deploy section:** "Don't upload `scripts/` or `docs/`; they are development files."

- [ ] **Step 6: Run the checks**

  Run: `python3 scripts/check_site.py`
  Expected: exit 0, no `FAIL` lines.

- [ ] **Step 7: Commit**

  ```bash
  git add scripts/check_site.py styles.css index.html ios.html privacy-policy.html terms.html delete-account.html README.md
  git commit -m "style: Play Store palette tokens, Anton font, site check script"
  ```

---

### Task 2: Header and hero

**Files:**
- Modify: `index.html:20` (theme-color), `index.html:99-142` (skip link, header, hero)
- Modify: `styles.css` header, button, hero and phone-frame rules (currently lines 83-302)
- Modify: `scripts/check_site.py` (append checks)

**Interfaces:**
- Consumes: Task 1 tokens.
- Produces: classes later tasks reuse: `.display` (Anton, uppercase, `line-height: .98`, `text-wrap: balance`), `.hi` (second headline line: `--yellow` on blue surfaces, `--blue` on light ones), `.btn.yellow` (navy on yellow), `.btn.navy` (white on navy), `.frame` (navy 8px phone frame, radius 34px, image radius 27px), `.top` (blue surface wrapping header and hero on the homepage), `.skip` (skip link).

- [ ] **Step 1: Append the failing checks:**
  - `hero_tells_removed`: inside `index.html`'s `<section class="hero">`, there is no `class="badge`, no `class="trust`, no `<em>`, and no `🛒` or `📱`.
  - `hero_meta`: the hero contains exactly two `class="meta` paragraphs, one with `not-ios` and one with `only-ios`. The `not-ios` one contains `Free · No ads · Private unless you share`.
  - `theme_color`: `<meta name="theme-color" content="#3A63B8">` is in `index.html`.
  - `skip_link`: the first element in `<body>` is `<a class="skip" href="#main">`, and `<main` has `id="main"`.
  - `nav_icon`: the nav `<img>` has `width="40" height="40"` and `alt=""`.
  - `header_spacing`: `styles.css` has `header` top padding `28px` and `.nav` `gap: 30px`.

- [ ] **Step 2: Run** `python3 scripts/check_site.py`. Expected: the six new checks FAIL.

- [ ] **Step 3: Rewrite the header and hero markup** in `index.html`:
  - Wrap `<header>` and the hero in `<div class="top">`.
  - Remove both badges.
  - h1 becomes `<h1 class="display">Say it once. <span class="hi">It's on both your phones.</span></h1>`.
  - Hero buttons become `.btn.yellow.big`; the nav button becomes `.btn.yellow`.
  - Replace `<ul class="trust">` and both `.alt-link` paragraphs with two `<p class="meta …">` lines:
    - `not-ios`: "Free · No ads · Private unless you share · On iPhone? Join the waitlist →", linking to `ios.html`.
    - `only-ios`: "Free · No ads · Partner on Android? It's free on Google Play today.", linking to the Play URL.
  - Keep `.stage` with the two phones, each `.phone` getting `.frame`.
  - Keep `id="heroCta"` on the button row; `landing.js` needs it.

- [ ] **Step 4: Restyle in `styles.css`:**
  - `.top` has a `--blue` background, full-bleed (outside `.wrap`).
  - Header: padding `28px 0`; `.nav` gap `30px`; nav links `--on-blue` on `.top`, `--text-2` elsewhere.
  - Hero h1: `clamp(2.6rem, 7vw, 4.75rem)`.
  - Delete the `.stage::before` glow.
  - Phones stay rotated: front 3deg, back −7deg.
  - `.btn` radius `12px` (no pill); `.btn.big` without a coloured shadow.
  - Remove the `h1 em::after` swoosh only for the homepage. Scope it so `ios.html`'s `h1 em` still renders (restyle it in Task 5).

- [ ] **Step 5: Run** `python3 scripts/check_site.py`. Expected: exit 0.

- [ ] **Step 6: Visual check.** Run `npx serve .` and open `http://localhost:3000/` in the browser pane.
  - At 1280×900: matches the mockup's blue hero with two navy-framed phones and no glow.
  - At 375×812: `document.documentElement.scrollWidth === window.innerWidth`, and the headline fits.
  - Run `document.documentElement.classList.add('is-ios')`: the iOS meta line and waitlist buttons show, and no empty gap is left.

- [ ] **Step 7: Commit**

  ```bash
  git add index.html styles.css scripts/check_site.py
  git commit -m "style: Play Store header and blue hero"
  ```

---

### Task 3: "Ramble in" section and section headings

**Files:**
- Modify: `index.html:144-166` (Ramble section), and every `<span class="eyebrow">` in `index.html`
- Modify: `styles.css` section heading, `.shots`, `.lede` rules
- Modify: `scripts/check_site.py`

**Interfaces:**
- Consumes: `.display`, `.hi`, `.frame` from Task 2.
- Produces: `.sec-grey` (grey full-bleed section), `.sec-white`, `.callout` (yellow 3px outline, radius 12px, absolutely positioned over a `.frame`), `.tag` (navy text on yellow pill, 13px, weight 900).

- [ ] **Step 1: Append the failing checks:**
  - `no_eyebrows_home`: `index.html` has no `class="eyebrow"`.
  - `h2_display`: every `<h2` in `index.html`'s `<main>` has class `display`.
  - `ramble_callouts`: the Ramble section has at least one `class="tag"` containing `You` and one containing `Sorted by aisle`, and both screenshot images keep their current `alt` text.

- [ ] **Step 2: Run** the checks. Expected: the three new checks FAIL.

- [ ] **Step 3: Update the markup.**
  - Delete all eyebrow spans on the homepage.
  - Make every h2 `.display`, with its second clause in `.hi`. Exact splits:
    - "Ramble in. / Tidy list out."
    - "No more / “what thing?” texts."
    - "Three steps. / Zero “what else?” texts."
    - "Your lists are / your business."
    - "Questions, / answered"
    - "Your next shop, / sorted together."
  - In Ramble, mark the section `.sec-grey`. Put the figcaption titles ("You say it", "It's sorted") above the frames in Anton.
  - Add `.tag` "You" on the voice shot, and `.callout` plus `.tag` "Sorted by aisle" over the first category group on the list shot. Mark the tags and callouts `aria-hidden="true"`.

- [ ] **Step 4: Restyle** section headings: `clamp(2rem, 5vw, 3.4rem)`, centred where the section is centred. Remove the old `.eyebrow` rule from the homepage path only, leaving it for `ios.html`. On phones, keep callouts inside the frame (no overflow).

- [ ] **Step 5: Run** the checks. Expected: exit 0. In the browser pane at 1280 and 375: the callouts sit on the right rows, and there's no horizontal scroll.

- [ ] **Step 6: Commit**

  ```bash
  git add index.html styles.css scripts/check_site.py
  git commit -m "style: Anton section headings, flat screenshots with callouts"
  ```

---

### Task 4: Chat, steps, privacy, FAQ, final CTA

**Files:**
- Modify: `index.html:168-267`
- Modify: `styles.css` `.familiar`, `.chat`, `.steps`, `.step`, `.band`, `.privacy-band`, `.faq-*`, `.final` rules
- Modify: `scripts/check_site.py`

**Interfaces:**
- Consumes: `.display`, `.hi`, `.btn.yellow`, `.btn.navy`, `.frame`, `.sec-grey`, `.sec-white`.
- Produces: `.steps.numbered` (homepage variant: no card background or border; numeral in Anton at 64px in `--blue`). The base `.steps` and `.step` stay for `ios.html`.

- [ ] **Step 1: Append the failing checks:**
  - `privacy_copy`: `index.html` does not contain "never leave your phone". The privacy band paragraph is exactly: "Use it as a guest and your lists stay on your phone. Sign in and they sync to your account, so they come back on a new phone. Only lists you share can be seen by anyone else."
  - `no_lock_emoji`: `index.html` has no `🔒` and no `class="lock"`.
  - `chat_role`: the `.chat` element has `role="img"` and keeps its `aria-label`.
  - `faq_marker`: `styles.css` has `.faq-item summary::-webkit-details-marker` hidden, `list-style: none` on the summary, and a `.faq-item[open] summary::after` rule.
  - `final_solid`: the `.final` rule has no `linear-gradient`.

- [ ] **Step 2: Run** the checks. Expected: the five new checks FAIL.

- [ ] **Step 3: Update the markup.**
  - Chat section is `.sec-white`. Add `role="img"` to `.chat`. The CTA becomes `.btn.navy`.
  - Steps: `<ol class="steps numbered">`, with the share screenshot in a `.frame`.
  - Privacy: remove the lock div, set the new paragraph, keep the three list items and the policy link.
  - Final CTA: the buttons become `.btn.yellow.big`.

- [ ] **Step 4: Restyle.**
  - `.band` uses a `--navy` background with white text, radius 28px.
  - `.privacy-band` becomes one column, with ✓ in `--yellow`.
  - `.final` uses a solid `--blue` background.
  - FAQ rows are white on grey with a 1px `#DDE4EE` border and radius 14px. The marker is "+" (open: "−") in `--blue`, placed right. Summaries get a hover state.

- [ ] **Step 5: Run** the checks. Expected: exit 0. Visual pass at 1280 and 375 in the browser pane, compared against the spec's section list.

- [ ] **Step 6: Commit**

  ```bash
  git add index.html styles.css scripts/check_site.py
  git commit -m "style: restyle chat, steps, privacy, FAQ and final CTA"
  ```

---

### Task 5: Shared pages, focus, dark mode

**Files:**
- Modify: `styles.css` (focus rules, dark-mode overrides, `.page` header on white, rules `ios.html` uses: `.badge`, `.trust`, `.eyebrow`, `h1 em`, `.demo-card`, `.list-group`, `.android-card`, `.waitlist`)
- Modify: `scripts/check_site.py`

**Interfaces:**
- Consumes: all tokens and classes above.
- Produces: nothing new.

- [ ] **Step 1: Append the failing checks:**
  - `focus_visible`: `styles.css` has a `:focus-visible` rule covering `a`, `button`, `summary` and `input` with a 3px outline.
  - `ios_classes_styled`: each of `.badge`, `.trust`, `.eyebrow`, `.demo-card`, `.list-group`, `.android-card` still has a rule in `styles.css`.
  - `no_undefined_vars`: every `var(--x)` used in `styles.css` is defined in `:root`.

- [ ] **Step 2: Run** the checks. Expected: `focus_visible` FAILS (the other two may already pass; that's fine).

- [ ] **Step 3: Implement.**
  - Focus ring: `--yellow` on blue and navy surfaces, `--blue` on light ones (via `.top :focus-visible`, `.band :focus-visible`), with `outline-offset: 3px`.
  - Restyle the `ios.html` classes into the new palette: `.badge` yellow with navy text, no emoji styling needed; `.eyebrow` in `--blue`; `h1 em` coloured `--blue` with no swoosh.
  - Legal pages: the header sits on white with navy text and a `.btn.navy` if one is present.
  - Dark mode: the grey and white sections become navy shades; `.top` and `.final` stay `--blue`.

- [ ] **Step 4: Run the checks**, then do a full visual pass in the browser pane:
  - `index.html` at 1280 and 375, in light and dark (`resize_window` `colorScheme`).
  - `ios.html` at 1280 and 375: the demo still animates, and the waitlist form is still usable.
  - `privacy-policy.html` at 375.
  - Press Tab through `index.html`: the ring is visible on every stop, including the FAQ summaries and the blue and navy blocks.
  - On every page, `scrollWidth === innerWidth` at 375.

- [ ] **Step 5: Commit**

  ```bash
  git add styles.css scripts/check_site.py
  git commit -m "style: focus rings, dark mode and shared pages in new look"
  ```
