# Landing page restyle: Play Store look

Date: 2026-11-24 · Status: approved

## Intent

The owner likes the current babegetthis.com homepage, but it looks AI-made: it follows
the same template as many generated app sites (onemoreplease.app is near-identical
apart from content). The goal is to keep the page and make it cleaner and less
template-like, using the visual language of the app's own Play Store graphics, so
people arriving from Google Play recognise it. The header also sits too close to the top
of the window.

## Goals

- Same sections, wording and app screenshots as today, restyled.
- Visual language from the Play Store graphics (`Babe-get-this/marketing/play-store`):
  Anton for headlines in capitals with two-tone lines, Nunito for everything else,
  cobalt blue, yellow highlights and dark navy.
- Remove the template tells (list below).
- Fix the review findings: contrast, focus states, heading wrap, stale privacy copy,
  header spacing, dead demo code.

## Non-goals

- New sections, new copy or reordering (apart from the privacy line fix).
- Changing the layout of the legal pages (privacy, terms, delete account); they only
  inherit fonts, colours and the header.
- iOS page (`ios.html`) layout changes beyond inheriting the shared styles.

## Anti-goals (would be a failure even if it works)

- Brown, beige or peach backgrounds. The owner rejected them outright.
- Cute or illustrated. The Pebbles mascot scenes were rejected as "too cute".
- Looking like a new site. It must still feel like the current one.

## Approaches considered

1. **Restyle in place (chosen).** Keep the structure, change the look. Least change,
   keeps what the owner likes.
2. Restyle and restructure: also reorder and merge sections. More distinctive, but
   moves away from the page the owner likes.
3. Use the 8 Play Store images directly as section art. Quickest, but the text is baked
   into the images (no SEO or accessibility, poor on phones). Ruled out.

Earlier rejected directions: Pebbles illustrated world (kitchen / chat / paper-list
heroes): too cute, and the beige palette.

## Decided design

**Palette.** Hero and final CTA: `#3A63B8` (the darker Play Store blue; `#4F7BD3`
fails contrast for white body text at 4.1:1, while `#3A63B8` gives 5.7:1 white and 4.05:1
yellow, which is fine for large headlines). Yellow `#FFD45C`, navy `#14254A`, light cool grey
`#EDF1F4` for alternating sections, white. Secondary text must reach 4.5:1 on its
background. No beige or brown anywhere.

**Type.** Anton (Google Fonts) for h1/h2 and big numerals, uppercase, two-tone (second
line in yellow on blue, in blue on light backgrounds). Nunito stays for body text, nav
and buttons. `text-wrap: balance` on headings.

**Header.** About 28px from the top, links about 30px apart, yellow "Get the app" button.
On the homepage it sits on the blue hero; on legal pages it sits on white.

**Sections (homepage, top to bottom):**

1. Hero, on blue. Anton headline "Say it once. / It's on both your phones." (second
   line yellow), existing sub copy, yellow Google Play button, one plain line under it:
   "Free · No ads · Private unless you share · On iPhone? Join the waitlist →". It keeps
   the original two phones (home in front, rotated 3°; list behind, rotated −7°) in navy
   frames. No radial glow, no callout on the hero.
2. "Ramble in. Tidy list out.", on grey. Two flat screenshots (voice, list) in navy
   frames, with yellow tags ("You", "Sorted by aisle") and a yellow outline highlight,
   like the Play Store graphics. Captions with Anton titles.
3. "What thing?" chat, on white, with an Anton headline. Chat and copy unchanged.
4. How it works: the three steps as a plain list with large Anton numerals next to the
   share screenshot, replacing the pastel cards.
5. Privacy: navy block, no 🔒 emoji. Copy corrected to match the privacy policy (guest
   lists stay on the phone; signed-in lists sync to the account; only shared lists are
   visible to others).
6. FAQ: clean rows with a custom +/− marker and hover state, replacing the default ▶.
7. Final CTA: solid blue block matching the hero, replacing the gradient.
8. Footer: unchanged apart from colours.

**Template tells removed.** Emoji pill badge, swoosh under "both", ✓ trust row, small
uppercase eyebrow labels above headings, radial glow behind phones, pastel numbered
step cards, 🔒 block, gradient CTA band.

**Fixes carried along.** Visible `:focus-visible` rings; nav icon `width`/`height` and
`alt=""`; emoji hidden from assistive tech where any remain; `aria-label` on the chat
only with a role; `theme-color` matching the hero; `color-scheme` declared; skip link.

**Correction to the review (found while planning).** The voice-demo JS and CSS are not
dead code: `ios.html` uses them (`#demo`, loaded via `assets/landing.js`). Keep them.

**`ios.html` (builder's call, confirmed while planning).** It shares `styles.css` and
uses classes the homepage drops (`.badge`, `.trust`, `.eyebrow`, `h1 em`, `.demo`,
`.band.final`, `.steps`). Those rules stay, restyled into the new palette (no beige or
peach), so the iOS page keeps its layout and picks up the new look. Only `index.html`
markup changes.

**Dark mode.** Kept, using navy surfaces with the same blue and yellow accents.

## Left to the builder

- Exact spacing, sizes and breakpoints (mobile layout must keep the two-phone hero
  readable and have no horizontal scroll).
- Exact yellow tag/highlight positions on the flat screenshots.
- Dark-mode values, as long as contrast passes.
- Mockup reference: `.superpowers/brainstorm/55463-1795493009/content/restyle-v4.html`
  (git-ignored, local only).
