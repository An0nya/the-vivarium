#!/usr/bin/env python3
"""Regenerate all Vivarium figures from scan JSON — both dark and light palettes.
Spec: COLOR-MAP SPEC in geometry.html bottom comment.

Local paths: reads scan JSON from rys-tools/scans/data, writes SVGs to ./figures.
Run with any python3 (stdlib only):  python3 build_svgs.py
"""
import json, math, os

BASE = '/Users/anya/Projects/rys-tools/scans/data'
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(OUT, exist_ok=True)

def load(f): return json.load(open(f'{BASE}/{f}'))

# ── DARK palette (spec-exact) ─────────────────────────────────────────────────
D = dict(
    BG      = '#141D26',  # plate/ground — quiet heatmap cells recede here
    GRID    = '#27323D',  # grid/rule
    MUTED   = '#6F7C88',  # axis ticks
    LABEL   = '#8893A0',  # faint labels
    ZERO    = '#3A4650',  # zero line
    CYAN    = '#4FB2C2',  # primary cyan (same-sense, emotion)
    BRIGHT  = '#6FCBD8',  # bright cyan (igniting/payload)
    CITRON  = '#E3C24A',  # citron (abstract, long-range, injected cause)
    VIOLET  = '#B98AD6',  # violet (diff-sense, numeric)
    TEAL    = '#2E6F8E',  # deep teal
    SLATE   = '#6E92C4',  # slate-blue (concrete, short-range)
    INK2    = '#A4B0BC',  # secondary ink
)

# ── LIGHT palette ─────────────────────────────────────────────────────────────
L = dict(
    BG      = '#E6EBEF',
    GRID    = '#D2DAE0',
    MUTED   = '#69757F',
    LABEL   = '#7B8794',
    ZERO    = '#B4C0C8',
    CYAN    = '#4FB2C2',
    BRIGHT  = '#3A9AAA',  # darken for contrast on light
    CITRON  = '#9A7A12',  # darken citron for light bg
    VIOLET  = '#7A52A8',  # darken violet
    TEAL    = '#1E5575',
    SLATE   = '#2E7E94',  # darken slate
    INK2    = '#3A4853',
)

def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return s if s else '0'

# ─────────────────────────────────────────────────────────────────────────────
# LINE CHART SCAFFOLD
# ─────────────────────────────────────────────────────────────────────────────
def line_chart(series_dict, figid, p, W=900, H=300, y_range=None,
               x_label='layer', y_label='cosine similarity',
               skip_emb=False, zero_line=True, annotations=None):
    """p = palette dict"""
    L_m, R, T, B = 58, 20, 28, 46
    CW, CH = W - L_m - R, H - T - B

    all_x = sorted({x for s in series_dict.values() for x in s['x']})
    if skip_emb:
        all_x = [x for x in all_x if x != -1]
    n = len(all_x)
    x_idx = {x: i for i, x in enumerate(all_x)}

    all_y = [y for s in series_dict.values() for x, y in zip(s['x'], s['y'])
             if x in x_idx]
    if y_range is None:
        vmin, vmax = min(all_y), max(all_y)
        pad = (vmax - vmin) * 0.1
        ymin = math.floor((vmin - pad) * 4) / 4
        ymax = math.ceil((vmax + pad) * 4) / 4
    else:
        ymin, ymax = y_range

    px = lambda x: L_m + (x_idx[x] / (n - 1)) * CW if n > 1 else L_m + CW / 2
    py = lambda v: T + (ymax - v) / (ymax - ymin) * CH

    out = [f'<svg id="{figid}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']

    # y-axis grid — adaptive tick spacing
    span = ymax - ymin
    if span <= 1.5:
        ytick = 0.25
    elif span <= 6:
        ytick = 1.0
    elif span <= 25:
        ytick = 5.0
    elif span <= 60:
        ytick = 10.0
    else:
        ytick = 25.0
    y = round(math.ceil(ymin / ytick) * ytick, 4)
    while y <= ymax + 1e-9:
        yy = py(y)
        is_zero = abs(y) < 1e-9
        col = p['ZERO'] if is_zero else p['GRID']
        sw = '0.8' if is_zero else '0.4'
        out.append(f'<line x1="{L_m}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" '
                   f'stroke="{col}" stroke-width="{sw}"/>')
        out.append(f'<text x="{L_m-5}" y="{yy+3.5:.1f}" font-family="JetBrains Mono,monospace" '
                   f'font-size="9.5" fill="{p["MUTED"]}" text-anchor="end">'
                   f'{"+" if y > 0 else ""}{fmt(y)}</text>')
        y = round(y + ytick, 4)

    # y-axis label
    my = T + CH / 2
    out.append(f'<text x="11" y="{my:.0f}" font-family="JetBrains Mono,monospace" '
               f'font-size="9.5" letter-spacing="1" fill="{p["LABEL"]}" text-anchor="middle" '
               f'transform="rotate(-90 11 {my:.0f})">{y_label}</text>')

    # vertical annotations
    if annotations:
        for ann in annotations:
            if ann['x'] not in x_idx: continue
            xx = px(ann['x'])
            col = ann.get('color', p['MUTED'])
            out.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{T}" y2="{T+CH}" '
                       f'stroke="{col}" stroke-width="0.6" stroke-dasharray="2 3" opacity="0.6"/>')

    # series
    for key, s in series_dict.items():
        pts = [(x, y) for x, y in zip(s['x'], s['y']) if x in x_idx]
        if not pts: continue

        col = s['color']

        # band
        if 'band' in s:
            lo, hi = s['band']
            lo_pts = [(x, l) for x, l in zip(s['x'], lo) if x in x_idx]
            hi_pts = [(x, h) for x, h in zip(s['x'], hi) if x in x_idx]
            poly = ' '.join(f'{px(x):.1f},{py(h):.1f}' for x, h in hi_pts)
            poly += ' ' + ' '.join(f'{px(x):.1f},{py(l):.1f}' for x, l in reversed(lo_pts))
            out.append(f'<polygon points="{poly}" fill="{col}" fill-opacity="0.12" stroke="none"/>')

        # line
        dash = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        coords = ' '.join(f'{"M" if i == 0 else "L"}{px(x):.1f},{py(y):.1f}'
                          for i, (x, y) in enumerate(pts))
        out.append(f'<path d="{coords}" fill="none" stroke="{col}" '
                   f'stroke-width="{s.get("w", 1.6)}" stroke-linejoin="round"{dash}/>')

        # markers
        if s.get('marker', True):
            r = s.get('r', 1.8)
            step = max(1, len(pts) // 24)
            for x, y in pts[::step]:
                xx, yy = px(x), py(y)
                shape = s.get('shape', 'circle')
                if shape == 'square':
                    out.append(f'<rect x="{xx-r:.1f}" y="{yy-r:.1f}" width="{2*r}" '
                               f'height="{2*r}" fill="{col}"/>')
                elif shape == 'triangle':
                    out.append(f'<polygon points="{xx},{yy-r*1.3} {xx+r*1.1},{yy+r*0.8} '
                               f'{xx-r*1.1},{yy+r*0.8}" fill="{col}"/>')
                elif shape == 'diamond':
                    out.append(f'<polygon points="{xx},{yy-r*1.3} {xx+r},{yy} '
                               f'{xx},{yy+r*1.3} {xx-r},{yy}" fill="{col}"/>')
                else:
                    out.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{r}" fill="{col}"/>')

    # x-axis ticks
    for x in all_x:
        if x == -1 or x % 5 == 0 or x == all_x[-1]:
            out.append(f'<text x="{px(x):.1f}" y="{H-B+14}" font-family="JetBrains Mono,monospace" '
                       f'font-size="9.5" fill="{p["MUTED"]}" text-anchor="middle">'
                       f'{"emb" if x == -1 else x}</text>')

    out.append(f'<text x="{L_m + CW//2}" y="{H-2}" font-family="JetBrains Mono,monospace" '
               f'font-size="9.5" letter-spacing="1" fill="{p["LABEL"]}" text-anchor="middle">'
               f'{x_label}</text>')

    out.append('</svg>')
    return '\n'.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# HEATMAP
# ─────────────────────────────────────────────────────────────────────────────
def lerp_color(t, stops):
    """t=0 identical (recede to BG), t=1 diverged (ignite bright)"""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1 + 1e-9:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            f = max(0.0, min(1.0, f))
            r = int(c0[0] + f * (c1[0] - c0[0]))
            g = int(c0[1] + f * (c1[1] - c0[1]))
            b = int(c0[2] + f * (c1[2] - c0[2]))
            return f'#{r:02x}{g:02x}{b:02x}'
    return f'#{stops[-1][1][0]:02x}{stops[-1][1][1]:02x}{stops[-1][1][2]:02x}'

# Dark: identical→plate (#141D26), diverged→bright cyan (#6FCBD8)
# Cause column: diverged→citron (#E3C24A)
HEAT_DARK = [
    (0.0, (0x14, 0x1D, 0x26)),  # plate ground
    (0.4, (0x1E, 0x45, 0x5A)),
    (0.7, (0x28, 0x88, 0xA8)),
    (1.0, (0x6F, 0xCB, 0xD8)),  # bright cyan
]
HEAT_DARK_CAUSE = [
    (0.0, (0x14, 0x1D, 0x26)),
    (0.4, (0x3A, 0x35, 0x10)),
    (0.7, (0x88, 0x72, 0x18)),
    (1.0, (0xE3, 0xC2, 0x4A)),  # citron
]
# Light: identical→plate (#E6EBEF), diverged→dark teal (#1E5575)
HEAT_LIGHT = [
    (0.0, (0xE6, 0xEB, 0xEF)),
    (0.4, (0xA8, 0xC8, 0xD8)),
    (0.7, (0x4F, 0x90, 0xA8)),
    (1.0, (0x1E, 0x55, 0x75)),
]
HEAT_LIGHT_CAUSE = [
    (0.0, (0xE6, 0xEB, 0xEF)),
    (0.4, (0xD8, 0xC0, 0x80)),
    (0.7, (0xB8, 0x90, 0x20)),
    (1.0, (0x9A, 0x7A, 0x12)),
]

def heatmap_svg(matrix, row_labels, col_labels, figid, pal,
                divergent_cols=None, cause_cols=None, key_cols=None,
                band_lo=17, band_hi=27, W=580, show_colorbar=True):
    """
    matrix: cosine similarity (1=identical, low=diverged)
    divergence = 1 - cosine (so identical → low t → recedes to plate)
    cause_cols: columns to render with the citron ramp (injected token)
    show_colorbar: crane shows the ramp key; small-multiple specimens suppress it.
    """
    nr, nc = len(matrix), len(matrix[0])
    LM, TM, BM = 42, 80, 20  # TM enlarged for top labels; BM shrunk
    RM = 120 if show_colorbar else 16
    cw_total = W - LM - RM
    cell_w = cw_total / nc
    cell_h = min(11.0, 480 / nr)
    CH_heat = nr * cell_h
    H = int(TM + CH_heat + BM) + 1

    is_dark = (pal['BG'] == '#141D26')
    heat_ramp = HEAT_DARK if is_dark else HEAT_LIGHT
    cause_ramp = HEAT_DARK_CAUSE if is_dark else HEAT_LIGHT_CAUSE
    div_border = '#C86868' if is_dark else '#A84040'
    key_border = '#E3C24A' if is_dark else '#9A7A12'
    band_fill = '#6FCBD8' if is_dark else '#1E5575'
    band_label = pal['MUTED']

    out = [f'<svg id="{figid}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']

    # L17–27 band shading
    if band_lo is not None:
        by = TM + (band_lo + 1) * cell_h  # +1 for emb row offset
        bh = (band_hi - band_lo + 1) * cell_h
        out.append(f'<rect x="{LM}" y="{by:.1f}" width="{cw_total:.1f}" height="{bh:.1f}" '
                   f'fill="{band_fill}" fill-opacity="0.06" stroke="none"/>')
        out.append(f'<text x="{LM-3}" y="{by+3:.1f}" font-family="JetBrains Mono,monospace" '
                   f'font-size="7.5" fill="{band_label}" text-anchor="end">L17</text>')
        out.append(f'<text x="{LM-3}" y="{by+bh:.1f}" font-family="JetBrains Mono,monospace" '
                   f'font-size="7.5" fill="{band_label}" text-anchor="end">L27</text>')

    # cells
    for ri, row in enumerate(matrix):
        for ci, val in enumerate(row):
            x = LM + ci * cell_w
            y = TM + ri * cell_h
            v = 0.0 if val is None else val
            t = 1.0 - max(0.0, min(1.0, v))  # divergence: 0=identical, 1=fully diverged
            is_cause = cause_cols and ci in cause_cols
            fill = lerp_color(t, cause_ramp if is_cause else heat_ramp)
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w:.2f}" '
                       f'height="{cell_h:.2f}" fill="{fill}" stroke="none"/>')

    # divergent col borders
    for ci in (divergent_cols or []):
        x = LM + ci * cell_w
        out.append(f'<rect x="{x:.1f}" y="{TM}" width="{cell_w:.2f}" '
                   f'height="{CH_heat:.1f}" fill="none" stroke="{div_border}" '
                   f'stroke-width="0.8" opacity="0.8"/>')
    for ci in (key_cols or []):
        x = LM + ci * cell_w
        out.append(f'<rect x="{x:.1f}" y="{TM}" width="{cell_w:.2f}" '
                   f'height="{CH_heat:.1f}" fill="none" stroke="{key_border}" '
                   f'stroke-width="0.8" opacity="0.8"/>')

    # column labels — at top of cells, rotated -45° fanning upward
    for ci, lbl in enumerate(col_labels):
        x = LM + (ci + 0.5) * cell_w
        y = TM - 4
        is_div = divergent_cols and ci in divergent_cols
        is_key = key_cols and ci in key_cols
        color = div_border if is_div else (key_border if is_key else pal["INK2"])
        size = "9" if len(lbl) <= 8 else "7.5"
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" '
                   f'font-family="JetBrains Mono,monospace" font-size="{size}" '
                   f'fill="{color}" text-anchor="start" '
                   f'transform="rotate(-45 {x:.1f} {y:.1f})">{esc(lbl)}</text>')

    # y-axis labels
    show_rows = {0} | {i for i in range(1, nr) if (i - 1) % 5 == 0 or i - 1 == 0} | {nr - 1}
    for ri in show_rows:
        y = TM + (ri + 0.5) * cell_h
        lbl = row_labels[ri]
        out.append(f'<text x="{LM-4}" y="{y+3.2:.1f}" '
                   f'font-family="JetBrains Mono,monospace" font-size="8.5" '
                   f'fill="{pal["MUTED"]}" text-anchor="end">{esc(lbl)}</text>')

    # colorbar (crane only; specimens suppress)
    if show_colorbar:
        cb_x = W - RM + 18
        cb_w = 12
        cb_h = int(CH_heat * 0.6)
        cb_y = TM + int(CH_heat * 0.2)
        n_stops = 40
        for si in range(n_stops):
            t = si / n_stops  # bottom=0.0 (identical/quiet), top=1.0 (diverged/bright)
            fill = lerp_color(t, heat_ramp)
            ry = cb_y + (n_stops - 1 - si) * (cb_h / n_stops)
            rh = cb_h / n_stops + 0.5
            out.append(f'<rect x="{cb_x}" y="{ry:.1f}" width="{cb_w}" '
                       f'height="{rh:.1f}" fill="{fill}" stroke="none"/>')
        out.append(f'<rect x="{cb_x}" y="{cb_y}" width="{cb_w}" height="{cb_h}" '
                   f'fill="none" stroke="{pal["MUTED"]}" stroke-width="0.5"/>')
        # gradient runs diverged (bright) at TOP → identical (quiet) at BOTTOM,
        # so labels must match: diverged on top, identical on bottom.
        out.append(f'<text x="{cb_x+cb_w+4}" y="{cb_y+4}" font-family="JetBrains Mono,monospace" '
                   f'font-size="8" fill="{pal["INK2"]}">diverged</text>')
        out.append(f'<text x="{cb_x+cb_w+4}" y="{cb_y+cb_h+4}" font-family="JetBrains Mono,monospace" '
                   f'font-size="8" fill="{pal["INK2"]}">identical</text>')

    out.append('</svg>')
    return '\n'.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# LEGEND SVG
# ─────────────────────────────────────────────────────────────────────────────
def legend_svg(items, pal, W=900, item_h=16):
    cols = 2
    rows = math.ceil(len(items) / cols)
    H = rows * item_h + 8
    col_w = (W - 40) // cols
    out = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    for i, it in enumerate(items):
        col = i // rows
        row = i % rows
        x = 20 + col * col_w
        y = 4 + row * item_h + item_h // 2
        dash = f' stroke-dasharray="{it["dash"]}"' if it.get('dash') else ''
        out.append(f'<line x1="{x}" x2="{x+22}" y1="{y}" y2="{y}" stroke="{it["color"]}" '
                   f'stroke-width="1.6"{dash}/>')
        shape = it.get('shape', 'circle')
        r = 2.2
        if shape == 'square':
            out.append(f'<rect x="{x+9}" y="{y-r:.0f}" width="{2*r:.0f}" height="{2*r:.0f}" fill="{it["color"]}"/>')
        elif shape == 'triangle':
            out.append(f'<polygon points="{x+11},{y-r*1.3:.1f} {x+11+r*1.1:.1f},{y+r*0.8:.1f} '
                       f'{x+11-r*1.1:.1f},{y+r*0.8:.1f}" fill="{it["color"]}"/>')
        elif shape == 'diamond':
            out.append(f'<polygon points="{x+11},{y-r*1.3:.1f} {x+11+r},{y} '
                       f'{x+11},{y+r*1.3:.1f} {x+11-r},{y}" fill="{it["color"]}"/>')
        else:
            out.append(f'<circle cx="{x+11}" cy="{y}" r="{r}" fill="{it["color"]}"/>')
        out.append(f'<text x="{x+28}" y="{y+3.5}" font-family="JetBrains Mono,monospace" '
                   f'font-size="9.5" fill="{pal["INK2"]}">{it["label"]}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def write(name, svg):
    path = f'{OUT}/{name}'
    open(path, 'w').write(svg)
    print(f'  wrote {name} ({len(svg):,} chars)')


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD ALL FIGURES
# ═══════════════════════════════════════════════════════════════════════════════

print('Loading JSON data...')
cl  = load('gemma4_12b_mxfp4_centered_last.json')
dt  = load('gemma4_12b_mxfp4_delta.json')
cx  = load('gemma4_12b_crosslang_curves.json')
wic = load('gemma4_12b_wic_bands.json')
st  = load('gemma4_12b_staircase_series.json')
inf = load('gemma4_12b_inflection_series.json')

print('Building figures...')

# ── Fig 1: figConcept — centered cosine per layer ─────────────────────────────
def build_concept(pal, figid):
    # Series order as spec: floor/noise first, signal on top
    s = {}
    # floors (no markers, dashed)
    s['en_fact_vs_zh_poem'] = {
        'x': cl['en_fact_vs_zh_poem']['layers'],
        'y': cl['en_fact_vs_zh_poem']['cosine_sim'],
        'color': pal['VIOLET'], 'w': 1.2, 'dash': '3 2',
        'label': 'EN↔ZH diff-content (floor)', 'marker': False}
    s['zh_same'] = {
        'x': cl['zh_fact_vs_zh_poem']['layers'],
        'y': cl['zh_fact_vs_zh_poem']['cosine_sim'],
        'color': pal['MUTED'], 'w': 1.0, 'dash': '3 2',
        'label': 'ZH same-lang diff-content', 'marker': False}
    s['en_same'] = {
        'x': cl['en_fact_vs_en_poem']['layers'],
        'y': cl['en_fact_vs_en_poem']['cosine_sim'],
        'color': pal['MUTED'], 'w': 1.0, 'dash': '4 2',
        'label': 'EN same-lang diff-content', 'marker': False}
    # signals (with markers)
    s['en_fr'] = {
        'x': cl['en_fact_vs_fr_fact']['layers'],
        'y': cl['en_fact_vs_fr_fact']['cosine_sim'],
        'color': pal['SLATE'], 'w': 1.5, 'shape': 'square', 'r': 1.6,
        'label': 'EN↔FR fact (same content)', 'marker': True}
    s['en_zh_fact'] = {
        'x': cl['en_fact_vs_zh_fact']['layers'],
        'y': cl['en_fact_vs_zh_fact']['cosine_sim'],
        'color': pal['CYAN'], 'w': 1.8, 'shape': 'circle', 'r': 2.0,
        'label': 'EN↔ZH fact (same content)', 'marker': True}
    s['en_zh_poem'] = {
        'x': cl['en_poem_vs_zh_poem']['layers'],
        'y': cl['en_poem_vs_zh_poem']['cosine_sim'],
        'color': pal['CITRON'], 'w': 1.8, 'shape': 'diamond', 'r': 1.8,
        'label': 'EN↔ZH poem (same content)', 'marker': True}
    s['en_para'] = {
        'x': cl['en_fact_vs_en_para']['layers'],
        'y': cl['en_fact_vs_en_para']['cosine_sim'],
        'color': pal['BRIGHT'], 'w': 2.0, 'shape': 'circle', 'r': 2.0,
        'label': 'EN paraphrase (same-lang same-content)', 'marker': True}
    return line_chart(s, figid, pal, W=900, H=320, y_range=(-1.05, 0.95),
                      y_label='centered cosine similarity')

def legend_concept(pal):
    return legend_svg([
        {'label': 'EN↔ZH fact (same content)',       'color': pal['CYAN'],   'shape': 'circle'},
        {'label': 'EN↔ZH poem (same content)',        'color': pal['CITRON'], 'shape': 'diamond'},
        {'label': 'EN paraphrase (same-lang)',         'color': pal['BRIGHT'], 'shape': 'circle'},
        {'label': 'EN↔FR fact (same content)',         'color': pal['SLATE'],  'shape': 'square'},
        {'label': 'same-lang diff-content',            'color': pal['MUTED'],  'dash': '3 2'},
        {'label': 'EN↔ZH diff-content (floor)',        'color': pal['VIOLET'], 'dash': '3 2'},
    ], pal)


# ── Fig 2: figDelta — per-layer ‖Δh‖ ─────────────────────────────────────────
def build_delta(pal, figid):
    d_lo = [m - s for m, s in zip(dt['delta_mean'], dt['delta_std'])]
    d_hi = [m + s for m, s in zip(dt['delta_mean'], dt['delta_std'])]
    s = {'delta': {
        'x': dt['layers'], 'y': dt['delta_mean'],
        'color': pal['CYAN'], 'w': 1.8, 'marker': True, 'r': 1.6, 'shape': 'circle',
        'label': '‖Δh‖ mean ±1σ', 'band': (d_lo, d_hi)
    }}
    return line_chart(s, figid, pal, W=900, H=220,
                      y_range=(0, max(dt['delta_mean']) * 1.18),
                      y_label='‖Δh‖ (avg across tokens)', zero_line=False)


# ── Fig 3 (figCrossLang) — 4 type curves ─────────────────────────────────────
# Spec: abstract=citron●, emotion=cyan▲(dashed), concrete=slate■(dash-dot), numeric=violet◆(dotted)
def build_crosslang(pal, figid):
    cxl = cx['layers']
    TYPES = [
        ('abstract', 'Abstract (freedom, money…)',  pal['CITRON'], 'circle',   ''),
        ('emotion',  'Emotional (she cried…)',       pal['CYAN'],   'triangle', '4 2'),
        ('concrete', 'Concrete (sun rises…)',        pal['SLATE'],  'square',   '3 1 1 1'),
        ('numeric',  'Numeric (2+3=5)',              pal['VIOLET'], 'diamond',  '2 2'),
    ]
    s = {}
    for key, label, color, shape, dash in TYPES:
        m = cx['curves_mean'][key]
        sd = cx['curves_std'][key]
        lo = [v - d for v, d in zip(m, sd)]
        hi = [v + d for v, d in zip(m, sd)]
        s[key] = {'x': cxl, 'y': m, 'color': color, 'w': 1.8,
                  'dash': dash, 'label': label, 'marker': True,
                  'shape': shape, 'r': 1.8, 'band': (lo, hi)}
    return line_chart(s, figid, pal, W=900, H=300,
                      y_range=(-0.08, 0.72),
                      y_label='cross-lingual cosine (mean ±1σ)',
                      skip_emb=True)

def legend_crosslang(pal):
    TYPES = [
        ('Abstract (freedom, money…)',  pal['CITRON'], 'circle',   ''),
        ('Emotional (she cried…)',       pal['CYAN'],   'triangle', '4 2'),
        ('Concrete (sun rises…)',        pal['SLATE'],  'square',   '3 1 1 1'),
        ('Numeric (2+3=5)',              pal['VIOLET'], 'diamond',  '2 2'),
    ]
    return legend_svg([
        {'label': t[0], 'color': t[1], 'shape': t[2], 'dash': t[3]} for t in TYPES
    ], pal)


# ── Fig 4 (figWiC) — word-sense disambiguation ────────────────────────────────
# Spec: same=cyan■, diff=violet●
def build_wic(pal, figid):
    wl = wic['layers']
    lo_s = [m - s for m, s in zip(wic['same_mean'], wic['same_std'])]
    hi_s = [m + s for m, s in zip(wic['same_mean'], wic['same_std'])]
    lo_d = [m - s for m, s in zip(wic['diff_mean'], wic['diff_std'])]
    hi_d = [m + s for m, s in zip(wic['diff_mean'], wic['diff_std'])]
    s = {
        'diff': {'x': wl, 'y': wic['diff_mean'], 'color': pal['VIOLET'], 'w': 1.8,
                 'label': 'different senses', 'marker': True, 'shape': 'circle', 'r': 1.6,
                 'band': (lo_d, hi_d)},
        'same': {'x': wl, 'y': wic['same_mean'], 'color': pal['CYAN'], 'w': 1.8,
                 'label': 'same sense', 'marker': True, 'shape': 'square', 'r': 1.6,
                 'band': (lo_s, hi_s)},
    }
    return line_chart(s, figid, pal, W=900, H=280,
                      y_range=(0.05, 1.02),
                      y_label='cosine similarity (target word)')

def legend_wic(pal):
    return legend_svg([
        {'label': 'same sense (n=100)',        'color': pal['CYAN'],   'shape': 'square'},
        {'label': 'different senses (n=100)',  'color': pal['VIOLET'], 'shape': 'circle'},
    ], pal)


# ── Fig 5 (figStaircase) — two-gate staircase ────────────────────────────────
# Spec: short=slate, long=citron, global marks=#3A4650 (dark) / #B4C0C8 (light)
def build_staircase(pal, figid):
    sl = st['layers']
    globs = st['globals']
    global_color = '#3A4650' if pal['BG'] == '#141D26' else '#B4C0C8'
    anns = [{'x': g, 'color': global_color} for g in globs]
    s = {
        'short': {'x': sl, 'y': st['results']['short']['T_cos'],
                  'color': pal['SLATE'], 'w': 2.0, 'shape': 'circle', 'r': 1.8,
                  'label': 'short-range (within window)', 'marker': True},
        'long':  {'x': sl, 'y': st['results']['long']['T_cos'],
                  'color': pal['CITRON'], 'w': 2.0, 'shape': 'diamond', 'r': 1.8,
                  'label': 'long-range (1112 tokens, >window)', 'marker': True},
    }
    return line_chart(s, figid, pal, W=900, H=280,
                      y_range=(0.62, 1.04),
                      y_label='cosine at shared token T',
                      annotations=anns)

def legend_staircase(pal):
    global_color = '#3A4650' if pal['BG'] == '#141D26' else '#B4C0C8'
    return legend_svg([
        {'label': 'short-range (X and T within sliding window)', 'color': pal['SLATE'],  'shape': 'circle'},
        {'label': 'long-range (X and T 1112 tokens apart)',      'color': pal['CITRON'], 'shape': 'diamond'},
        {'label': 'global attention layers (5,11,17…)',           'color': global_color,  'dash': '2 3'},
    ], pal)


# ── Fig 6 (figCrane) — heatmap ────────────────────────────────────────────────
def build_crane(pal, figid):
    crane = inf['pairs']['crane']
    matrix = crane['matrix']
    labels = crane['labels']
    div_cols = set(crane['divergent_cols'])
    crane_col = labels.index('crane') if 'crane' in labels else None
    key_cols = {crane_col} if crane_col is not None else set()
    row_labels = ['emb'] + [str(i) for i in range(48)]
    return heatmap_svg(matrix, row_labels, labels, figid, pal,
                       divergent_cols=div_cols,
                       cause_cols=div_cols,   # harbor/marsh = injected/cause → citron
                       key_cols=key_cols,
                       W=600)


# ── Specimen gallery — 8 small-multiple heatmaps ──────────────────────────────
# (out_name, json_file, pair_key, tracked_token_substring | None)
# The injected/changed token(s) ignite citron (cause_cols); the tracked sense-token
# (the byte-identical word whose reading flips) gets the citron key-border.
SPECIMENS = [
    ('bank',     'gemma4_12b_inflection_series.json', 'bank',        'bank'),
    ('shoot',    'gemma4_12b_distance_series.json',   'shoot_short', 'shoot'),
    ('howdoyou', 'gemma4_12b_divergence_series.json', 'howdoyou',    'do'),
    ('novel',    'gemma4_12b_divergence_series.json', 'novel',       'novel'),
    ('fall',     'gemma4_12b_divergence_series.json', 'fall',        'fall'),
    ('late',     'gemma4_12b_divergence_series.json', 'late',        'late'),
    ('mean',     'gemma4_12b_divergence_series.json', 'mean',        'mean'),
    ('battery',  'gemma4_12b_divergence_series.json', 'battery',     'battery'),
]
_spec_cache = {}
def _spec_data(jf):
    if jf not in _spec_cache:
        _spec_cache[jf] = load(jf)
    return _spec_cache[jf]

def build_specimen(spec, pal, figid):
    out_name, jf, key, tracked = spec
    d = _spec_data(jf)
    pair = d['pairs'][key]
    matrix = pair['matrix']
    labels = pair['labels']
    div_cols = set(pair['divergent_cols'])
    key_cols = set()
    if tracked:
        for i, lbl in enumerate(labels):
            if i in div_cols:
                continue
            if lbl.strip().lower().lstrip('▁ ').startswith(tracked):
                key_cols = {i}
                break
    row_labels = ['emb'] + [str(i) for i in range(len(matrix) - 1)]
    return heatmap_svg(matrix, row_labels, labels, figid, pal,
                       divergent_cols=div_cols,
                       cause_cols=div_cols,
                       key_cols=key_cols,
                       W=460, show_colorbar=False)


# ── RENDER BOTH PALETTES ──────────────────────────────────────────────────────
for theme, pal, suffix in [('dark', D, ''), ('light', L, '.light')]:
    print(f'\n  [{theme}]')

    write(f'figConcept{suffix}.svg',   build_concept(pal, 'figConcept'))
    write(f'figConcept_legend{suffix}.svg', legend_concept(pal))

    write(f'figDelta{suffix}.svg',     build_delta(pal, 'figDelta'))

    write(f'figCrossLang{suffix}.svg', build_crosslang(pal, 'figCrossLang'))
    write(f'figCrossLang_legend{suffix}.svg', legend_crosslang(pal))

    write(f'figWiC{suffix}.svg',       build_wic(pal, 'figWiC'))
    write(f'figWiC_legend{suffix}.svg', legend_wic(pal))

    write(f'figStaircase{suffix}.svg', build_staircase(pal, 'figStaircase'))
    write(f'figStaircase_legend{suffix}.svg', legend_staircase(pal))

    write(f'figCrane{suffix}.svg',     build_crane(pal, 'figCrane'))

    for spec in SPECIMENS:
        try:
            write(f'specimen_{spec[0]}{suffix}.svg', build_specimen(spec, pal, f'spec_{spec[0]}'))
        except (KeyError, FileNotFoundError) as e:
            print(f'    SKIP specimen_{spec[0]}: {e}')

print('\nDone.')
