# The Probing Notebook — design system & decisions

Reference for future tweaks. This bucket (geometry / probing) is a **sibling imprint** to
the Vivisection Lab, not a clone and not a stranger. Shared skeleton, different skin.

---

## 1. The thesis that drives every visual choice

Two research notebooks, one program. The split is real and load-bearing:

- **Vivisection Lab = intervention.** "What happens when you cut." Scalpel. **Warm** —
  cream paper, terracotta, wine, sage. Anatomical.
- **Probing Notebook = observation.** "What does the model already know, and *when* does it
  know it." Lens / scanner. **Cool** — slate-blue ground, cyan, citron. Imaging.

Everything downstream is "warm = you cut it / cool = you scanned it." Keep the bones shared
(typography, section rhythm, marginalia, honest-negative voice, dark-default + light
toggle, slim hand-authored static SVG) so the portfolio reads as one program; diverge only
on palette, governing metaphor, and chart idiom.

---

## 2. Palette (the one decision everything hangs off)

Cool "imaging" palette. Cividis-adjacent on purpose: it reads as scan/heatmap **and** it's
colorblind-safe on the protan axis (no red–green load-bearing pair anywhere).

| token | DARK (default) | LIGHT |
|---|---|---|
| `--bg` | `#0E141A` | `#EDF1F4` |
| `--bg2` (panels / scan-plate / fig ground) | `#141D26` | `#E3E9EE` |
| `--ink` | `#DCE4EC` | `#16222C` |
| `--ink2` | `#A4B0BC` | `#3A4853` |
| `--muted` | `#6F7C88` | `#69757F` |
| `--rule` / `--rule2` | `#1C2630` / `#27323D` | `#CBD5DD` / `#D8E0E6` |
| `--acc` (primary cyan) | `#4FB2C2` | `#2E7E94` |
| `--acc2` (bright cyan / igniting payload) | `#6FCBD8` | `#2E7E94` |
| `--citron` (the *intervention* / cause accent) | `#E3C24A` | `#9A7A12` |
| `--violet` (4th series / "this failed") | `#B98AD6` | `#7A52A8` |

**Accent logic:** cyan = the thing observed; **citron = an injected cause / intervention** —
the one warm pop, which doubles as a portfolio in-joke (warm = intervention, even inside an
observation chart). Violet is the safe fourth hue and the "broken on purpose" color.

---

## 3. Typography

Inherited from the lab (shared bones):
- **Newsreader** (serif) — body, headlines, dek, pull-quotes, drop-caps. Headlines weight
  400–500, tight tracking (`-0.02em`).
- **JetBrains Mono** — all labels, kickers, sec-labels, figure captions, stats, nav, data.
- Scale: h1 `clamp(2.3–3.7rem)`, h2 `1.55rem`, body `17px/1.76`. Mono labels `.62–.72rem`,
  uppercase, letter-spaced `.08–.14em`.
- Drop-caps in `--acc2`; first-person reactive voice (day-zero freshness), not the formal
  lab register.

---

## 4. Chart system (the heart of the bucket)

**Scan-plate.** Figures sit on `var(--bg2)` panels, bordered `var(--rule2)`. No baked
backgrounds. Quiet regions equal the ground so the chart blends into the page; the signal
is the only thing that pops.

**Two palettes, swapped by theme.** Every figure = `figX.svg` + `figX.light.svg`, toggled
on `.light` via `.fig-plate img.fig-dark/.fig-light`. **Never CSS-invert** — it mangles
cyan/citron and breaks colorblind-safety.

**Governing rule:** *identical/quiet → ground; divergence/signal → max contrast.* Bright on
dark, dark on light.

**Heatmaps (crane + 8 specimens):**
- Orientation: **tokens across the top, depth increasing downward** (emb→L47). Each column
  reads as a token "falling" through the stack — the reading direction matches the
  computation. (This was a deliberate reorientation from the first draft.)
- Ramp keyed to **divergence, not raw cosine**: identical recedes to ≈ground; diverged
  **ignites**. Default bright = cyan. The single injected/cause column ignites **citron**,
  so cause-vs-effect read as warm-vs-cool inside one chart.
- Mark the tracked column; shade the **L17–27** band.

**Line charts — CB-safe series set** (markers + dash patterns are load-bearing, colour is
secondary):
- abstract / long-range / different-sense families: citron `#E3C24A` (●, solid)
- emotion / same-sense: cyan `#4FB2C2` (▲, dashed)
- concrete / short-range: slate `#6E92C4` (■, dash-dot)
- numeric / 4th: violet `#B98AD6` (◆, dotted)
- global-layer marks / zero line: thin `--zero` verticals.

---

## 5. Components & layout

- **Hero**: topbar (specimen ID + scan stats) · mono kicker · serif headline w/ italic
  accent · dek · 5-cell `stats-strip` · `marginalia` ("the question").
- **`col-side`**: main prose + a right `aside` (teal left-rule; becomes a top-rule lead-in
  on mobile). Used for every analytical section.
- **`marginalia`**: label/body two-column for framing & colophon.
- **Specimen gallery = small multiples, all visible.** Rationale: the *recurrence* of the
  "cold-early / hot-mid" shape across pairs **is** the finding — only a grid shows it.
  Toggle/accordion would destroy the gestalt. Counterexample sits in the same grid, flagged
  violet, as the punchline. Interactivity = hover/tap-zoom enhancement, never gating.
- **Pull-quotes**: serif italic, hairline top/bottom rules. Reserved for the 1–2 lines that
  carry the section ("Commitment lags the cue.").
- **`zone-note`**: citron mono one-liner above a figure, orienting the eye before the chart.
- **Footer**: one byte-identical legal line (© · as-is/no-warranty · CC BY · cookieless
  analytics) — the only chrome that must not drift across pages.

---

## 6. Favicon family — one gesture per bucket

One glyph, recolored + re-gestured per bucket; 32×32, rounded dark tile. Copy-paste data
URIs (geometry is already live in the page):

**Geometry — divergence fork** (observe; two readings split at a commit point):
```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230E141A'/%3E%3Cpath d='M6 16 H15' stroke='%236F7C88' stroke-width='2.6' fill='none' stroke-linecap='round'/%3E%3Cpath d='M15 16 L26 9' stroke='%236FCBD8' stroke-width='2.6' fill='none' stroke-linecap='round'/%3E%3Cpath d='M15 16 L26 23' stroke='%23E3C24A' stroke-width='2.6' fill='none' stroke-linecap='round'/%3E%3Ccircle cx='15' cy='16' r='2.6' fill='%23ECEFF3'/%3E%3C/svg%3E">
```

**Vivisection Lab — the incision** (intervene; warm; one stroke with a clean cut/gap):
```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%231A1410'/%3E%3Cpath d='M6 16 H14' stroke='%23D77955' stroke-width='2.6' fill='none' stroke-linecap='round'/%3E%3Cpath d='M18 16 H26' stroke='%23D77955' stroke-width='2.6' fill='none' stroke-linecap='round'/%3E%3Cpath d='M16 9 L16 23' stroke='%23B85F5F' stroke-width='1.4' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
```

**Duologue — the loop** (two models in feedback; two hues mirroring):
```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230E141A'/%3E%3Cpath d='M11 11 A7 7 0 1 1 11 21' stroke='%236FCBD8' stroke-width='2.4' fill='none' stroke-linecap='round'/%3E%3Cpath d='M21 21 A7 7 0 1 1 21 11' stroke='%23C98AD6' stroke-width='2.4' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
```

**mem0-processor — the pipeline** (systems; nodes + flow; the odd one out, engineering-feel):
```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230E141A'/%3E%3Cline x1='7' y1='16' x2='25' y2='16' stroke='%236F7C88' stroke-width='2' /%3E%3Ccircle cx='7' cy='16' r='3' fill='%236FCBD8'/%3E%3Ccircle cx='16' cy='16' r='3' fill='%236FCBD8'/%3E%3Crect x='22' y='13' width='6' height='6' rx='1' fill='%23E3C24A'/%3E%3C/svg%3E">
```

Same two-stroke DNA; opposite gesture (split / cut / loop / flow). Recolor per bucket
palette and the favicon does the "complementary but unique" job by itself.

---

## 7. Decisions log

- **Cool over warm** — driven by the observe/intervene thesis; cividis doubles as the
  protan-safe fix for the colorblind-critical cross-lingual chart. Functional, not
  decorative — which is why it survives scrutiny.
- **Divergence ignites (not "bright = identical")** — salience must match the finding; the
  chart's thesis is "when does it split," so the split is what glows.
- **Citron = the injected cause** — gives a two-accent system (observe vs intervene) inside
  one chart and ties back to the portfolio thesis.
- **Tokens-on-top heatmaps** — reading direction matches the computation (token falls
  through the stack).
- **Two-file figures over CSS-invert or inline-vars** — invert breaks hues/CB; per-cell
  heatmap colors can't be CSS-vars; two files keep the main HTML lean and match the
  Claude-Code `figures/` regen workflow.
- **Small multiples for the gallery** — recurrence is the finding.
- **External figures + constant page-ground plate** — figures blend into the page instead
  of floating on black; theme-aware in both modes.
- **Lab pages stay slim** — ~1KB JS (theme toggle only), all charts hand-authored static
  SVG, no chart libraries. (Inherited doctrine; keep it.)
