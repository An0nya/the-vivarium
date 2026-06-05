# The Vivarium

An observation notebook — sibling to [The Vivisection Lab](https://github.com/An0nya/vivisection-lab).
Where the lab cuts the living model open (intervention), the Vivarium keeps it intact under glass and
watches it think (observation): hidden-state scans of small language models, run locally on a 16 GB Mac Mini.

**First specimen:** [Gemma-4-12B, day zero](geometry.html) — six hidden-state probes, one mid-stack concept
zone (L18–27) where all six independently find the meaning.

## Status (MVP)

- Page, copy, design system, both themes — done.
- `figCrane` heatmap — faithful (real geometry).
- Figs 1,2,4,5,6 + the 8 specimen heatmaps — **palette-remapped stand-ins**; regenerate from the scan JSON
  (in `rys-tools/`) with the SVG generator from the lab repo. See `COMPLETION.md` for the full checklist.

## Build

Static HTML + hand-authored SVG, no build step. Figures live in `figures/` as `figX.svg` (dark) +
`figX.light.svg` (light), swapped on the `.light` class. Source notes: `gemma4-12b-day-zero.md`.
