# Yantrakar design system

The theme and rules behind the new yantrakar.com, written so that product sites like **gitpro** can follow the same rules and look like part of one family. Source of truth for values: `styles.css` and `assets/brand/` in the yantrakar website repo.

---

## 1. Character

- **Look:** dark, quiet and technical, like an engineering drawing sheet. Light mode is a warm-paper version of the same thing.
- **Accent:** one warm signal orange (the colour of safety markings), used for at most one thing per screen.
- **Lines and labels:** thin 1px rules instead of shadows, square corners, and mono labels for every tag, button, nav item and figure title.
- **Type:** large headings set light and tight.
- **Figures:** diagrams that show a real mechanism, and move.
- **Never:** gradients, glow, glassmorphism, stock photos, emoji, purple "AI" styling, or icon sets. The only symbols are → ↗ $ × ◐.

## 2. Voice and content rules

- **Person:** first person "I" in running text. Product sites can use the product as subject ("gitpro sets…"). The company name, "Yantrakar AS", appears in the footer.
- **Tone:** plain, modest, specific. Use "So far I see" and "I would"; never sound authoritative or salesy.
- **Banned:**
  - em dashes (U+2014)
  - fragment openers ("The result?")
  - three-part punchlines
  - "It's not X, it's Y"
  - the words unlock, leverage, seamless, cutting-edge, empower, revolutionize, game-changer
- **Numbers:** no invented numbers, percentages or fake charts. Two or three facts go in a sentence or a table.
- **Clients:** no client names or client-specific details, and generic terms only in figures.
- **Repetition:** say each claim once per page, and keep repeats across pages to two.
- **Captions** say what the figure shows or does. They don't repeat the paragraph next to them.

## 3. Colour tokens

The page is dark-first: bare `:root` holds the dark palette. Light mode is defined under `@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) {…} }` and repeated under `:root[data-theme="light"]`. Components use tokens only, never literal colours.

| Token | Dark (default) | Light | Use |
|---|---|---|---|
| `--bg` | #0F1215 | #F3F2EF | Page |
| `--surface` | #14181C | #FFFFFF | Panels, tiles, figures |
| `--raised` | #1A1F25 | #ECEAE6 | Boxes inside figures |
| `--rule` | #262C33 | #D8D5CF | 1px borders and dividers |
| `--rule-strong` | #3A434D | #B5B0A7 | Hover borders, inputs |
| `--dot` | #20262D | #DCD8D1 | Hero dot grid |
| `--ink` | #E8EAEC | #15181B | Headings, strong text |
| `--ink-2` | #B3B8BE | #3F454C | Body text |
| `--muted` | #8A9199 | #61676E | Labels, captions |
| `--accent` | #F59E57 | #B54708 | The one highlight |
| `--accent-ink` | #FFB47A | #9A3B06 | Links, accent text |
| `--accent-tint` | #2B1C10 | #FBEBDD | Accent fills |
| `--accent-line` | #7A4A22 | #E3A06E | Accent borders |
| `--on-accent` | #1A0E05 | #FFFFFF | Text on solid accent |
| `--focus` | #7AA2FF | #2563EB | Focus ring |

**Contrast targets,** checked in both themes:

- ink on bg ≥ 12
- ink-2 on bg ≥ 7
- muted on bg, surface and raised ≥ 4.5
- accent-ink on bg and on accent-tint ≥ 4.5

## 4. Type

One Google Fonts request:
`family=Schibsted+Grotesk:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500`

| Role | Spec |
|---|---|
| H1 | Schibsted Grotesk 400, `clamp(2.1rem, 1.4rem + 2.6vw, 3.4rem)`, line-height 1.04, letter-spacing −0.025em, `text-wrap: balance` |
| H1 second sentence | same size, coloured `--ink-2` (two-tone headline) |
| H2 | 400, `clamp(1.6rem, 1.25rem + 1.4vw, 2.25rem)`, 1.12, −0.015em |
| H3 | 500, 1.125rem, 1.3 |
| Lead | 1.25rem, 1.5, `--ink-2` |
| Body | 1.0625rem, 1.6, `--ink-2`; `p` max 62ch, `text-wrap: pretty` |
| Labels, tags, nav, buttons, figure heads | IBM Plex Mono 400, 0.75rem, uppercase, letter-spacing .06–.08em, `--muted` |
| Code | Plex Mono 0.875rem |

Fallbacks: sans `"Helvetica Neue", Helvetica, Arial, sans-serif`; mono `ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace`.

## 5. Layout

- **Container:** max-width 1200px, centred, `padding-inline: max(16px, env(safe-area-inset-left))`.
- **Sections:** `padding-block: clamp(2.5rem, 1.5rem + 3vw, 4.5rem)`, separated by a 1px `--rule` line. No coloured bands, except the contact block.
- **Grids:**
  - Grids use `gap` and never sibling margins.
  - Two-column text/figure splits from 1100px.
  - Tiles go two-up from 760px.
  - Every text child of a grid gets `min-width: 0`.
- **Header:** sticky, 56px high, solid `--bg`, 1px bottom rule. Wordmark on the left, nav in the centre, theme toggle on the right. Under 720px the nav goes on its own row and scrolls sideways inside itself.
- **Hero:** a faint dot grid (`radial-gradient(var(--dot) 1px, transparent 1px)` at 20px), masked to fade out towards the bottom. Used in the hero only.
- **Phone width:** no sideways page scroll at 360px. Figures get a narrow variant instead of scrolling.

## 6. Components

- **Wordmark:** the Y mark (inline SVG, `--accent`, 18px) plus `YANTRAKAR` in Plex Mono 500, 0.85rem, letter-spacing .14em. A product uses its own lowercase name in mono (e.g. `gitpro`), followed by a small `by Yantrakar` link.
- **Buttons** (mono caps, 36px high, 0 14px padding, radius 2px):
  - **Primary:** `--accent-tint` fill, `--accent-ink` text, 1px `--accent-line` border.
  - **Secondary:** transparent, 1px `--rule-strong` border, `--ink-2` text.
- **Tags:** mono label in a 1px `--rule` box, radius 2px, 2px 6px padding. Accent text only for the highlighted category.
- **Panels and tiles:** `--surface`, 1px `--rule`, radius 4px, no shadows. Tiles have 24px padding and a footer pinned to the bottom, and the hover state changes only the border.
- **Proof list:** rows of mono tag + one line of text, divided by 1px rules.
- **Terminal box:** `--bg` fill, 1px rule, radius 2px, mono; the `$` prompt is in `--accent`.
- **Callout:** 2px left border in `--accent`, `--accent-tint` fill.
- **Table:** rules between rows only, mono header. It turns into stacked cards under 720px, with each cell labelled from `data-label`.
- **Links in text:** `--accent-ink`, 1px underline, 3px offset.
- **Theme toggle:** ◐ icon plus "Switch to light" or "Switch to dark". The choice is saved in localStorage (`yk-theme`) and set before paint by an inline head script. The button is hidden when JS is off.
- **Focus:** a 2px `--focus` outline with 2px offset on everything interactive.

## 7. Figures

**Frame:** a panel with a 36px header strip: `FIG. 01 │ TITLE` in mono caps, plus a `Pause` button on the right when the figure is animated. The caption sits under the drawing in `--muted`.

**SVG:**
- Hand-written inline SVG, coloured only through classes that use the tokens.
- Strokes 1.25px with `non-scaling-stroke`; corner radius 2.
- Boxes filled `--raised`; one focus element per figure, drawn in `--accent` over `--accent-tint`.
- Text in boxes: 13–14px sans. Small labels: 11–12px mono caps.
- Text sits inside its box with at least 8px padding and never overlaps other text.
- Every SVG has `role="img"`, `<title>` and `<desc>`.

**Motion:**
- One small vanilla `site.js` (≤ 16 KB) and a single `requestAnimationFrame` loop.
- A figure runs only while at least 35% of it is in view (IntersectionObserver) and stops when the tab is hidden.
- **Packets:** r=4 dots that travel along lines, never over text. Grey (`--ink-2`) means state or a reply; accent means a command or request.
- **Hit:** when a packet arrives, the box gets the accent border and tint for 600 ms.
- **Status:** a mono status line top-right says what is happening ("STATE UP", "SEND OUTSIDE?").
- **Blocked:** a packet that stops at a boundary makes the × next to "NOTHING LEAVES" flash.
- **Calm:** loops of about 8–11 s with a pause at the end. No bounce, glow or blur.
- `prefers-reduced-motion` and no-JS both show the static drawing.

**Narrow variants:** about 320 units wide, stacked vertically, switched by container query, with text at least 11px at a 360px viewport.

## 8. Brand assets

Everything is in `assets/brand/` in the yantrakar website repo, with a README listing sizes:

- the Y mark, plus versions for dark and light backgrounds
- horizontal logos
- square tiles
- favicon (SVG, ICO, 16/32/48 PNG)
- apple-touch-icon and 192/512 icons
- og-image 1200×630
- LinkedIn logo, cover and banner

SVG masters have outlined text, so they scale with no font dependency.

## 9. Technical rules

- Static HTML and one CSS file, no frameworks or build tools at runtime. A small Python generator is fine.
- The only scripts are the head theme bootstrap and `site.js`.
- Only external request: Google Fonts.
- **Head of every page:**
  - lang
  - viewport with `viewport-fit=cover`
  - `color-scheme: light dark`
  - meta description
  - Open Graph (title, description, image 1200×630)
  - `twitter:card` summary_large_image
  - favicon set
- **Accessibility:**
  - skip link
  - one H1 per page
  - landmarks
  - `aria-current` in the nav
  - real labels on form fields
  - visible focus everywhere
- **Print:** light colours, with nav, form and texture hidden.
- **Checks before shipping:**
  - no overflow at 360, 400 and 1280 in both themes
  - SVG geometry check
  - contrast table
  - a grep for em dashes, banned words and client terms
  - screenshots looked at by a person

---

## 10. Applying it to gitpro (open source)

Same family, with a different job. Keep every token, font, component and figure rule above. What changes:

- **Wordmark:** `gitpro` in Plex Mono 500 with a small `by Yantrakar ↗` link (the Y mark can sit before it). Favicon: the Y tile, or a simple mono "g" tile in the same colours.
- **Accent:** the same orange. Every product in the family shares it, so they read as one maker.
- **Page structure** (one page plus a docs page if needed):
  1. **Hero:** a one-sentence H1 about the problem it solves (wrong git name, email or SSH key per account), the install command in a terminal box with a copy button, and buttons for GitHub (primary), PyPI and Docs.
  2. **Figure, "How it works" (animated):** one config file maps each GitHub/GitLab account to a name, email and SSH key. As each repo is cloned or opened, a packet goes to the matching identity and the repo box gets that identity's label. A wrong-identity commit is stopped, and its packet is blocked with ×.
  3. **AI coding assistants:** a short section and a figure where Claude Code or Cursor tries to commit under the wrong identity and gitpro stops it.
  4. **Quickstart:** `pipx install gitpro`, then `gitpro setup`, then checking existing repos. Code blocks with copy buttons; Mac (`brew install pipx`) and Ubuntu (`sudo apt install pipx`) notes.
  5. **Commands:** a table of the main commands, mono and short.
  6. **FAQ:** where the config lives, what it changes in each repo, how to undo, and whether it sends anything anywhere.
  7. **Footer:** licence, GitHub, PyPI, a "Report an issue" link, "Made by Yantrakar AS" linking to yantrakar.com.
- **Copy:** take every fact from the README and `docs/guide.md` in the repo. No features that aren't there, no download counts or stars unless pulled live.
- **Hosting:** GitHub Pages from the gitpro repo (a `site/` folder plus a Pages workflow, like the yantrakar repo has). Use `gitpro.yantrakar.com` if you want your own domain.
- **On yantrakar.com:** the gitpro tile links to this site, and this site links back.
