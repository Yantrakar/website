# Yantrakar brand assets

SVG files are the masters. They scale to any size, and all text in them is outlined (IBM Plex Mono, Schibsted Grotesk; both SIL OFL), so they look the same everywhere without fonts installed. PNG and ICO files in `png/` are exports for places that need a bitmap.

## Colours
| Use | Hex |
|---|---|
| Background (dark) | #0F1215 |
| Text on dark | #E8EAEC |
| Secondary text on dark | #B3B8BE |
| Muted / labels | #8A9199 |
| Orange on dark | #F59E57 |
| Background (light) | #F3F2EF |
| Text on light | #15181B |
| Orange on light | #B54708 |

## Files
| File | Use |
|---|---|
| logo-mark.svg | The Y mark, orange, transparent. For dark backgrounds. |
| logo-mark-on-light.svg | The Y mark in darker orange. For light backgrounds. |
| logo-horizontal-dark.svg | Mark + YANTRAKAR, for dark backgrounds (site header, slides). |
| logo-horizontal-light.svg | Mark + YANTRAKAR, for light backgrounds (documents, invoices). |
| logo-tile-dark.svg / -light.svg | Square tile. Avatars, app icons. |
| favicon.svg | Browser tab icon (rounded tile). |
| og-image.svg | Generic link preview image, 1200 × 630. Each page now has its own, see below. |
| linkedin-company-cover.svg | LinkedIn company page cover, 1128 × 191. Text kept right of the logo overlay. |
| linkedin-profile-banner.svg | LinkedIn personal banner, 1584 × 396. Text kept right of the profile photo. |

## PNG / ICO exports (`png/`)
| File | Size | Use |
|---|---|---|
| linkedin-logo-400.png | 400 × 400 | LinkedIn company logo |
| linkedin-company-cover.png (@2x) | 1128 × 191 (2256 × 382) | LinkedIn company cover |
| linkedin-profile-banner.png | 1584 × 396 | LinkedIn personal banner |
| og-image.png | 1200 × 630 | `og:image` / link previews |
| favicon.ico, favicon-16/32/48.png | 16–48 | Browser tabs |
| apple-touch-icon.png | 180 × 180 | iOS home screen |
| icon-192.png, icon-512.png | 192, 512 | Android / web app manifest |
| logo-horizontal-dark/light(.png, @2x) | 48 / 96 high | Email signatures, documents |
| logo-mark-512.png, logo-mark-on-light-512.png | 512 | Transparent mark |
| logo-tile-dark-512.png, logo-tile-light-512.png | 512 | Square tiles |

## Page link previews (`../og/`)
One 1200 × 630 image per page, all in the article preview's layout: wordmark, mono label, three-line headline with the last line dimmed, byline, and a small diagram from that page on the right.
Sources are in `tools/og/` (shared `og.css`, one HTML file per page); each file names its render command. The article's own image comes from `tools/article_figs/<slug>/og.html`.

## Rules
- Keep clear space around the logo of at least the mark's width.
- Don't stretch, recolour or add effects. Use the light versions on light backgrounds.
- The older files in `assets/` are still used by the live site and stay until the new site goes live.
