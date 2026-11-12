from __future__ import annotations

import argparse
import math

import cadquery as cq

from . import gridfinity as gf
from .config import load_inventory
from .export import export_stl, export_svg

# Hex across-corners / across-flats. key_mm is across-flats; the long arm is a hex
# rod whose widest span is across-corners, so the groove that cradles it is sized
# to across-corners or the corners ride up on the walls.
HEX_AC = 2.0 / math.sqrt(3.0)

# Arm lengths interpolated linearly in key_mm within each system, from Chris's four
# measured extremes (inch -> mm): (longest arm x shortest arm). Metric arms run much
# longer than SAE for the same across-flats, so the two systems interpolate apart.
METRIC_ARM = ((1.50, 57.2), (10.00, 190.5))    # long: 2.25" .. 7.5"
SAE_ARM = ((1.59, 50.8), (9.53, 120.65))        # long: 2"    .. 4.75"
METRIC_SHORT = ((1.50, 25.4), (10.00, 50.8))    # short: 1"   .. 2"
SAE_SHORT = ((1.59, 12.7), (9.53, 38.1))         # short: 0.5" .. 1.5"

GROOVE_CLEAR = 0.5     # added to across-corners so the rod drops in freely
BORE_EXTRA = 1.5       # short-arm bore cut this much deeper so the long arm seats first
BORE_FLOOR = 2.5       # material under the deepest short-arm bore
WALL = 2.0             # wall between adjacent grooves
END_WALL = 3.0         # outer margin left/right of the groove field
EDGE_WALL = 2.5        # min wall kept between a bore and the end face it sits near
# Clearance an arm tip needs past the end of its support before it meets open canyon,
# so it can rotate/lift out without jamming. Scales with key size: 0.5in for the
# smallest, 1in for the largest.
ARM_CLEAR_MIN = 8.0    # ~0.3" (trimmed from 0.5" to keep the box at 6u with head labels)
ARM_CLEAR_MAX = 11.0   # ~0.43"
KEY_MIN, KEY_MAX = 1.5, 10.0
# Short-arm swing: pressing the long tip down rotates the short arm up and toward the
# outboard face, so the bore is extended outboard to give it room. It is UNIFORM per
# side (sized to the largest key's need), so every bore sticks out the same amount --
# that keeps every head label the same distance from its slot. Smaller keys just get a
# little unused bore room, which is harmless (the neck still holds them).
SWING_K = 0.18
SWING_METRIC = SWING_K * METRIC_SHORT[1][1]   # sized to the 10mm short arm
SWING_SAE = SWING_K * SAE_SHORT[1][1]           # sized to the 3/8 short arm
# The outboard swing extension starts this far below the surface, so the top of the
# bore stays a tight round hole that holds a key against fore/aft shift.
NECK_DROP = 4.0
# Canyon: the front SUPPORT_FRAC of each arm rests in its channel; the back tip runs
# over a deep, wide cutout. All the back-tip cutouts merge into one smooth diagonal
# canyon (front and back walls follow the per-column support/tip points), opening a
# broad grasp with the arms cantilevered over it.
SUPPORT_FRAC = 2.0 / 3.0
CANYON_OVER = 2.0      # canyon runs this far past each tip
CANYON_FLOOR = 5.0     # material left under the canyon (thicker belly than the bores)
LABEL_SIZE = 3.5

# Companion sizing-gauge stick (a separate part). Hex holes sized to across-flats so a
# hex key seats on its flats -- a tight, positive fit -- with a large legible label.
GAUGE_CLEAR = 0.12     # added to across-flats; a hex key should seat snug, not rattle
GAUGE_DEPTH = 12.0
GAUGE_LABEL_SIZE = 6.0
GAUGE_LABEL_DEPTH = 0.6
GAUGE_PITCH = 15.0     # cell size along a row
GAUGE_ROW_GAP = 4.0
GAUGE_MARGIN = 6.0
GAUGE_THICK = 8.0

# Gauges integrated into the box side borders: metric down one side, SAE down the
# other, hex holes with the size engraved in the gap beside each.
BORDER_INSET = 7.5     # gauge hole center from the box side edge
BORDER_DEPTH = 12.0    # blind gauge-hole depth
BORDER_END = 16.0      # keep gauges this far from the Y ends
BORDER_LABEL = 6.0     # gauge label target size (shrunk per-label to fit the gap)
LABEL_DEPTH = 1.4      # engraving depth for all labels (deep + bold = easy to read)
LABEL_EDGE_MARGIN = 1.5   # keep any label at least this far from an outer edge
# Per-slot head labels: one uniform size, run along the slot (rotated), hugging each
# slot's own bore so they sit right at the slots. The end border is only as deep as
# each slot's bore plus its label needs.
HEAD_LABEL_SIZE = 4.5
HEAD_GAP = 1.2         # gap between a bore and its head label
HEAD_CHAR = 0.62       # per-char width factor (of size) for the rotated label length

# Spare slots: the SAE side is short 9 columns vs the metric side's 13. Fill the dead
# space behind the unpaired metric tips with small generic slots (sized to the 3rd
# smallest SAE key), packed at a fine pitch and clipped to the extrapolated SAE tip
# diagonal so the canyon wall stays smooth. They only hold small, short keys.
SPARE_RANK = 2         # 3rd-smallest SAE key (0-based index into the sorted sizes)
SPARE_MIN = 15.0       # skip a spare slot shorter than this
SPARE_WALL = 2.0       # wall between packed spare slots


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _arm_clear(g):
    frac = _clamp((g.key_mm - KEY_MIN) / (KEY_MAX - KEY_MIN), 0.0, 1.0)
    return ARM_CLEAR_MIN + (ARM_CLEAR_MAX - ARM_CLEAR_MIN) * frac


class Groove:
    __slots__ = ("key_mm", "label", "arm", "short", "gw", "system")

    def __init__(self, key_mm, label, arm, short, system):
        self.key_mm = key_mm
        self.label = label
        self.arm = arm
        self.short = short
        self.system = system            # 'm' or 's', selects the uniform swing
        self.gw = key_mm * HEX_AC + GROOVE_CLEAR


def _arm_len(key_mm, table):
    (k0, l0), (k1, l1) = table
    return l0 + (l1 - l0) * (key_mm - k0) / (k1 - k0)


def _mk(key_mm, label, system):
    """Build one Groove with arm/short interpolated. `system` is 'm' or 's'."""
    arm = _arm_len(key_mm, METRIC_ARM if system == "m" else SAE_ARM)
    short = _arm_len(key_mm, METRIC_SHORT if system == "m" else SAE_SHORT)
    return Groove(key_mm, label, arm, short, system)


def _columns():
    """Pair metric (front-loaded) with SAE (back-loaded), one column per metric key.
    The smallest metric arms pair with the LARGEST SAE arms so no column's combined
    reach exceeds the 190mm the 10mm metric already forces; the four longest metrics
    stay unpaired. Returns [(metric_groove, sae_groove_or_None)], sorted by metric
    size so the metric row reads small->large left to right."""
    inv = load_inventory()
    metric = sorted(next(t for t in inv.tiers if t.name == "metric_front").holes, key=lambda h: h.key_mm)
    sae = sorted(next(t for t in inv.tiers if t.name == "sae_back").holes, key=lambda h: h.key_mm)
    m = [Groove(h.key_mm, h.label, _arm_len(h.key_mm, METRIC_ARM), _arm_len(h.key_mm, METRIC_SHORT), "m") for h in metric]
    s = [Groove(h.key_mm, h.label, _arm_len(h.key_mm, SAE_ARM), _arm_len(h.key_mm, SAE_SHORT), "s") for h in sae]
    sae_desc = list(reversed(s))  # largest SAE first, to pair with the smallest metrics
    cols = []
    for i, mg in enumerate(m):
        cols.append((mg, sae_desc[i] if i < len(sae_desc) else None))
    return cols


def _layout(cols):
    """Assign each column an X center, packing max(metric,SAE) widths + walls.
    Returns (placed, field_width) where placed is [(x, metric, sae)]."""
    field = END_WALL
    placed = []
    for mg, sg in cols:
        cw = max(mg.gw, sg.gw if sg else 0.0)
        placed.append((field + cw / 2.0, mg, sg, cw))
        field += cw + WALL
    field += END_WALL - WALL
    x_shift = -field / 2.0
    return [(x + x_shift, mg, sg, cw) for x, mg, sg, cw in placed], field


def _long_groove(x, mouth_y, ydir, g, body_h):
    """The long-arm channel: a U-slot recessed into the TOP surface (round bottom +
    straight walls up to the rim) so the rod nestles with its top flush at the
    surface, like the reference. `ydir` is the direction the arm runs from the mouth:
    -1 into -Y (metric, front mouth) or +1 into +Y (SAE, back mouth)."""
    r = g.gw / 2.0
    zc = body_h - r                        # rod center one radius below the top -> flush
    start = mouth_y - ydir * 1.0           # begin just outside the mouth so it opens fully
    length = g.arm + 2.0
    cyl = cq.Solid.makeCylinder(r, length, cq.Vector(x, start, zc), cq.Vector(0, ydir, 0))
    y_lo = start if ydir > 0 else start - length
    top = cq.Solid.makeBox(g.gw, length, r + 0.1, cq.Vector(x - g.gw / 2.0, y_lo, zc))
    return cq.Workplane(obj=cyl).union(cq.Workplane(obj=top)).val()


def _swing(g):
    return SWING_METRIC if g.system == "m" else SWING_SAE


def _short_bore(x, mouth_y, out, g, body_h):
    """The short-arm bore, necked at the top and extended outboard into an obround slot
    below the neck. `out` is the sign toward the near end face (+1 metric/front, -1
    SAE/back). The top NECK_DROP is a tight round hole that holds the key against
    fore/aft shift; below it the outboard extension gives the short arm room to sweep
    out as the key rotates. Depth swallows the whole short arm so the tail hides."""
    r = g.gw / 2.0
    depth = g.short + BORE_EXTRA
    top = body_h + 0.5
    round_h = depth + 1.0
    round_bore = cq.Solid.makeCylinder(r, round_h, cq.Vector(x, mouth_y, top), cq.Vector(0, 0, -1))
    swing = _swing(g)
    ext_top = body_h - NECK_DROP
    ext_h = (ext_top + 0.5) - (top - round_h)      # from just below the neck to the bore bottom
    c2 = cq.Solid.makeCylinder(r, ext_h, cq.Vector(x, mouth_y + out * swing, ext_top), cq.Vector(0, 0, -1))
    y0 = min(mouth_y, mouth_y + out * swing)
    box = cq.Solid.makeBox(g.gw, swing, ext_h, cq.Vector(x - r, y0, ext_top - ext_h))
    return cq.Workplane(obj=round_bore).union(cq.Workplane(obj=c2)).union(cq.Workplane(obj=box)).val()


def _canyon_band(placed, side, front_mouth, back_mouth):
    """The (x, y_lo, y_hi, w) band for one group of arms: the y-span from each arm's
    support point (2/3 out) to just past its tip. `side` is 'metric' or 'sae'."""
    band = []
    for x, mg, sg, cw in placed:
        if side == "metric":
            g, mouth, ydir = mg, front_mouth, -1
        else:
            if sg is None:
                continue
            g, mouth, ydir = sg, back_mouth, +1
        tip_y = mouth + ydir * (g.arm + 1.0)
        support_y = mouth + ydir * (g.arm * SUPPORT_FRAC + 1.0)
        y_tip = tip_y + ydir * CANYON_OVER
        band.append((x, min(support_y, y_tip), max(support_y, y_tip), g.gw))
    return sorted(band, key=lambda b: b[0])


def _fit(xs, ys):
    """Least-squares line y = a + b*x."""
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    a = (sy - b * sx) / n
    return a, b


def _band_lines(band):
    """Two straight lines fitted to a band's tip (y_lo) and support (y_hi) points,
    plus the x range padded to cover the outer channels. Straight lines give the canyon
    clean diagonal walls instead of a faceted, divoted edge."""
    xs = [b[0] for b in band]
    lo = _fit(xs, [b[1] for b in band])
    hi = _fit(xs, [b[2] for b in band])
    xl = band[0][0] - band[0][3] / 2.0 - WALL
    xr = band[-1][0] + band[-1][3] / 2.0 + WALL
    return lo, hi, xl, xr


def _line_y(line, x):
    a, b = line
    return a + b * x


def _canyon(lo, hi, xl, xr, body_h):
    """Extrude one canyon as a straight-walled quadrilateral between the fitted support
    line (hi) and tip line (lo)."""
    pts = [
        (xl, _line_y(hi, xl)), (xr, _line_y(hi, xr)),
        (xr, _line_y(lo, xr)), (xl, _line_y(lo, xl)),
    ]
    h = (body_h + 0.2) - CANYON_FLOOR
    return cq.Workplane("XY").polyline(pts).close().extrude(h).translate((0, 0, CANYON_FLOOR)).val()


def _hex_blind(x, y, key_mm, top_z, depth):
    """A blind hex hole cut down from top_z, sized to across-flats."""
    circ = (key_mm + GAUGE_CLEAR) / math.cos(math.radians(30.0))
    return (
        cq.Workplane("XY", origin=(x, y, top_z - depth))
        .polygon(6, circ).extrude(depth + 0.6).val()
    )


def _border_gauges(w, d, body_h):
    """Hex sizing gauges down the two side borders: metric on +X, SAE on -X, each with
    its size engraved in the gap below it, sized to fit the gap and the border width so
    it never touches a hole or bleeds off the edge. Returns (holes, labels) where a
    label is (text, x, y, size)."""
    inv = load_inventory()
    metric = sorted(next(t for t in inv.tiers if t.name == "metric_front").holes, key=lambda h: h.key_mm)
    sae = sorted(next(t for t in inv.tiers if t.name == "sae_back").holes, key=lambda h: h.key_mm)
    holes, labels = [], []
    avail_w = 2.0 * (BORDER_INSET - LABEL_EDGE_MARGIN)   # label width the border allows

    def row(items, xc):
        span = d - 2.0 * BORDER_END
        pitch = span / len(items)
        y0 = -span / 2.0 + pitch / 2.0
        rad = [(h.key_mm + GAUGE_CLEAR) / math.cos(math.radians(30.0)) / 2.0 for h in items]
        for i, h in enumerate(items):
            y = y0 + i * pitch
            holes.append(_hex_blind(xc, y, h.key_mm, body_h, BORDER_DEPTH))
            r = rad[i]
            r_next = rad[i + 1] if i + 1 < len(items) else r
            gap = pitch - r - r_next - 2.0                # vertical room to the next hole
            size = _clamp(min(BORDER_LABEL, gap, avail_w / (len(h.label) * 0.62)), 2.2, BORDER_LABEL)
            labels.append((h.label, xc, y - r - 1.0 - size / 2.0, size))

    row(metric, w / 2.0 - BORDER_INSET)
    row(sae, -(w / 2.0 - BORDER_INSET))
    return holes, labels


def _label_len(text):
    return len(text) * HEAD_LABEL_SIZE * HEAD_CHAR


def _head_label_specs(placed, front_mouth, back_mouth):
    """One uniform-size label per slot head, run ALONG the slot (rotated) and hugging
    that slot's own bore, so each sits right at its slot. Returns (text, x, y_center)."""
    specs = []
    for x, mg, sg, cw in placed:
        bo = front_mouth + _swing(mg) + mg.gw / 2.0        # metric bore outboard edge (+Y)
        specs.append((mg.label, x, bo + HEAD_GAP + _label_len(mg.label) / 2.0))
        if sg is not None and sg.label:
            bo_s = back_mouth - _swing(sg) - sg.gw / 2.0    # SAE bore outboard edge (-Y)
            specs.append((sg.label, x, bo_s - HEAD_GAP - _label_len(sg.label) / 2.0))
    return specs


def _spares(sae_tip_line, back_mouth, body_h, x_lo, x_hi):
    """Small generic slots packed at a fine pitch across the dead SAE-side space, each
    running from the SAE end to the extrapolated SAE tip line (so they shrink toward
    the 10mm and lie under the same smooth canyon wall). Returns (channels, bores)."""
    inv = load_inventory()
    sae = sorted(next(t for t in inv.tiers if t.name == "sae_back").holes, key=lambda h: h.key_mm)
    key = sae[min(SPARE_RANK, len(sae) - 1)].key_mm
    channels, bores = [], []
    pitch = (key * HEX_AC + GROOVE_CLEAR) + SPARE_WALL
    x = x_lo
    while x <= x_hi:
        arm = _line_y(sae_tip_line, x) - back_mouth
        if arm >= SPARE_MIN:
            g = _mk(key, "", "s")
            g.arm = arm
            channels.append(_long_groove(x, back_mouth, +1, g, body_h))
            bores.append(_short_bore(x, back_mouth, -1, g, body_h))
        x += pitch
    return channels, bores


def build(labels: bool = True, cols=None):
    if cols is None:
        cols = _columns()
    placed, field_w = _layout(cols)

    max_short = max(
        [mg.short for _, mg, _, _ in placed] + [sg.short for _, _, sg, _ in placed if sg]
    )
    body_h = max_short + BORE_EXTRA + BORE_FLOOR

    # Bore mouths inset far enough that the widest bore at each end -- including its
    # outboard swing extension -- keeps EDGE_WALL to the end face. Metric bores sit at
    # the +Y face, SAE bores at the -Y face.
    # End borders are as deep as each end's worst (bore reach + its head label) needs,
    # plus a margin -- no more. Labels hug their bores, so this stays compact.
    front_inset = max(mg.gw / 2.0 + _swing(mg) + HEAD_GAP + _label_len(mg.label) for _, mg, _, _ in placed) + LABEL_EDGE_MARGIN
    back_inset = max(
        (sg.gw / 2.0 + _swing(sg) + HEAD_GAP + _label_len(sg.label) for _, _, sg, _ in placed if sg is not None and sg.label),
        default=EDGE_WALL,
    ) + LABEL_EDGE_MARGIN

    # Length must fit the deepest reach from either end. Each arm gets a clearance gap
    # past its tip so it can rotate out into open canyon without jamming; a paired
    # column carries both arms plus both clearances.
    reach = []
    for _, mg, sg, _ in placed:
        if sg is None:
            reach.append(mg.arm + _arm_clear(mg))
        else:
            reach.append(mg.arm + _arm_clear(mg) + _arm_clear(sg) + sg.arm)
    length_need = max(reach) + front_inset + back_inset

    nx = math.ceil((field_w + gf.OUTER_CLEARANCE) / gf.GRID)
    ny = math.ceil((length_need + gf.OUTER_CLEARANCE) / gf.GRID)
    w, d = gf.outer_dims(nx, ny)

    part = gf.base(nx, ny).union(gf.body_slab(nx, ny, body_h))

    front_mouth = d / 2.0 - front_inset   # metric bend sits here, tail drops down
    back_mouth = -d / 2.0 + back_inset     # SAE bend sits here

    # Real channels: metric from the front, SAE from the back (paired columns only).
    channels, bores = [], []
    for x, mg, sg, cw in placed:
        channels.append(_long_groove(x, front_mouth, -1, mg, body_h))
        bores.append(_short_bore(x, front_mouth, +1, mg, body_h))
        if sg is not None:
            channels.append(_long_groove(x, back_mouth, +1, sg, body_h))
            bores.append(_short_bore(x, back_mouth, -1, sg, body_h))

    # Straight support/tip lines. Metric over all 13; SAE over the 9 real slots, then
    # EXTRAPOLATED across the whole width so the canyon wall is one smooth diagonal.
    m_lo, m_hi, m_xl, m_xr = _band_lines(_canyon_band(placed, "metric", front_mouth, back_mouth))
    s_lo, s_hi, s_xl, s_xr = _band_lines(_canyon_band(placed, "sae", front_mouth, back_mouth))

    # Pack small spare slots into the dead space behind the unpaired metric tips.
    sp_channels, sp_bores = _spares(s_hi, back_mouth, body_h, s_xr + 3.0, m_xr - 3.0)
    channels += sp_channels
    bores += sp_bores

    # One smooth canyon from the SAE support line to the metric support line. Span the
    # widest channel at each end (metric vs SAE) so a wide SAE key like the 3/8 doesn't
    # poke past the canyon edge -- symmetric with the widest metric key at the far end.
    cxl = min(m_xl, s_xl)
    cxr = max(m_xr, s_xr)
    part = part.cut(cq.Compound.makeCompound(channels))
    part = part.cut(_canyon(s_lo, m_hi, cxl, cxr, body_h))
    part = part.cut(cq.Compound.makeCompound(bores))

    # Sizing gauges down the side borders, with big bold labels beside them.
    gauge_holes, gauge_labels = _border_gauges(w, d, body_h)
    part = part.cut(cq.Compound.makeCompound(gauge_holes))
    if labels:
        try:
            texts = []
            for text, lx, ly, size in gauge_labels:
                texts.extend(
                    cq.Workplane("XY").text(text, size, LABEL_DEPTH, kind="bold")
                    .translate((lx, ly, body_h - LABEL_DEPTH / 2.0)).vals()
                )
            for text, hx, hy in _head_label_specs(placed, front_mouth, back_mouth):
                texts.extend(
                    cq.Workplane("XY").text(text, HEAD_LABEL_SIZE, LABEL_DEPTH, kind="bold")
                    .rotate((0, 0, 0), (0, 0, 1), 90.0)
                    .translate((hx, hy, body_h - LABEL_DEPTH / 2.0)).vals()
                )
            part = part.cut(cq.Compound.makeCompound(texts))
        except Exception:  # noqa: BLE001
            pass

    return part, body_h, nx, ny


def _hex_hole(x, y, key_mm, thick):
    """A through hexagonal hole sized to across-flats, so a matching hex key seats on
    its flats. circumscribed (vertex) diameter = across-flats / cos(30)."""
    across_flats = key_mm + GAUGE_CLEAR
    circ = across_flats / math.cos(math.radians(30.0))
    return (
        cq.Workplane("XY", origin=(x, y, -0.5))
        .polygon(6, circ)
        .extrude(thick + 1.0)
        .val()
    )


def build_gauge_stick(labels: bool = True):
    """A separate sizing-gauge stick: two rows of hex holes (metric, SAE), each sized
    to across-flats for a snug hex fit, with a large legible size engraved beside it."""
    inv = load_inventory()
    metric = sorted((h for h in next(t for t in inv.tiers if t.name == "metric_front").holes), key=lambda h: h.key_mm)
    sae = sorted((h for h in next(t for t in inv.tiers if t.name == "sae_back").holes), key=lambda h: h.key_mm)

    ncol = max(len(metric), len(sae))
    width = ncol * GAUGE_PITCH + 2.0 * GAUGE_MARGIN
    row_h = 12.0 + GAUGE_LABEL_SIZE + 5.0
    depth = 2.0 * row_h + GAUGE_ROW_GAP + 2.0 * GAUGE_MARGIN

    part = cq.Workplane("XY").box(width, depth, GAUGE_THICK, centered=(True, True, False))

    holes, text_specs = [], []
    for row, cy in ((metric, (row_h + GAUGE_ROW_GAP) / 2.0), (sae, -(row_h + GAUGE_ROW_GAP) / 2.0)):
        x0 = -(len(row) - 1) * GAUGE_PITCH / 2.0
        for i, h in enumerate(row):
            x = x0 + i * GAUGE_PITCH
            holes.append(_hex_hole(x, cy + 4.5, h.key_mm, GAUGE_THICK))
            text_specs.append((h.label, x, cy - 8.0))

    part = part.cut(cq.Compound.makeCompound(holes))
    if labels:
        try:
            texts = []
            for text, tx, ty in text_specs:
                texts.extend(
                    cq.Workplane("XY").text(text, GAUGE_LABEL_SIZE, GAUGE_LABEL_DEPTH)
                    .translate((tx, ty, GAUGE_THICK - GAUGE_LABEL_DEPTH / 2.0)).vals()
                )
            part = part.cut(cq.Compound.makeCompound(texts))
        except Exception:  # noqa: BLE001
            pass
    return part, width, depth


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Single open-groove Gridfinity bin for the full key set.")
    parser.add_argument("--name", default="open-bin")
    parser.add_argument("--no-labels", action="store_true")
    parser.add_argument("--gauge", action="store_true", help="emit the companion sizing-gauge stick")
    args = parser.parse_args(argv)

    if args.gauge:
        part, gw, gd = build_gauge_stick(labels=not args.no_labels)
        name = args.name if args.name != "open-bin" else "gauge-stick"
        print(f"solids: {len(part.val().Solids())}  size: {gw:.0f}x{gd:.0f}x{GAUGE_THICK:.1f}")
        print(f"wrote {export_stl(part, name)}")
        print(f"wrote {export_svg(part, name, direction=(-0.1, -0.2, 0.97))}")
        return 0

    part, body_h, nx, ny = build(labels=not args.no_labels)
    solids = len(part.val().Solids())
    w, d = gf.outer_dims(nx, ny)
    print(f"solids: {solids}  grid: {nx}x{ny}  size: {w:.0f}x{d:.0f}x{body_h + gf.FOOT_H:.1f}")
    print(f"wrote {export_stl(part, args.name)}")
    print(f"wrote {export_svg(part, args.name, direction=(-0.6, -1.0, 0.6))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
