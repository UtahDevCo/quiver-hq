"""Flat leather liner panels for the inside of the TPU sleeve, as a printable PDF.

Reads the sleeve's skin-side surface from `build/cord-brace/sleeve-local.stl`
(local frame: x left/right, y up toward the chin, z anterior). Each section
perpendicular to the neck axis is sampled by rays from the axis; the nearest
wall hit is the skin-side surface. The C-shaped surface is split into panels
along meridians (constant angle), with the front panel centred on the throat so
no seam sits there. Each panel is unrolled strip by strip: across the panel by
arc length along its section, and up the panel by arc length along its centre
meridian. The report gives each panel's worst length error along its edges,
which is the stretch the leather has to take up. The panel count is the
smallest whose seam edges stay under 2 percent; the two edges at the rear
opening are folded over, and are reported separately.

Panels butt together at the seams. A fold allowance runs past both rims and
past the two ends at the rear opening, to wrap onto the outside and glue there.
Perforations sit on a staggered grid clear of every edge.

Writes `build/sleeve-liner/sleeve-liner-pattern.pdf` (US Letter, 1:1, with a
50 mm check square) and `liner.json`.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.backends.backend_pdf import PdfPages
from shapely.geometry import Point, Polygon

from .config import PROJECT_ROOT

PANEL_COUNTS = range(3, 10)  # smallest count whose seam edges stretch less than MAX_STRAIN
MAX_STRAIN = 0.02  # the opening edges are folded over and judged separately
RIM_INSET_MM = 0.4  # sample just inside each rim so sections are clean
LEVEL_STEP_MM = 0.5
RAY_STEP_DEG = 0.25
FOLD_ALLOWANCE_MM = 6.0  # wraps over the rims and opening ends onto the outside
HOLE_DIA_MM = 1.6  # Craftool round drive punch size 00
HOLE_PITCH_MM = 8.0
HOLE_MARGIN_MM = 4.0
PAGE_MM = (215.9, 279.4)
PAGE_MARGIN_MM = 12.0


def _section_segments(mesh: trimesh.Trimesh, y: float) -> np.ndarray:
    section = mesh.section(plane_origin=[0.0, y, 0.0], plane_normal=[0.0, 1.0, 0.0])
    if section is None:
        raise RuntimeError(f"no sleeve section at y = {y:.2f}")
    segs = []
    for path in section.discrete:
        xz = path[:, [0, 2]]
        segs.extend(zip(xz[:-1], xz[1:]))
    return np.asarray(segs)


def _inner_radius(segs: np.ndarray, thetas: np.ndarray) -> np.ndarray:
    """Distance from the axis to the nearest wall along each ray (nan where open)."""
    a, b = segs[:, 0], segs[:, 1]
    d = b - a
    out = np.full(len(thetas), np.nan)
    for i, t in enumerate(thetas):
        u = np.array([math.cos(t), math.sin(t)])
        den = u[0] * d[:, 1] - u[1] * d[:, 0]
        ok = np.abs(den) > 1e-12
        r = np.where(ok, (a[:, 0] * d[:, 1] - a[:, 1] * d[:, 0]) / np.where(ok, den, 1), np.inf)
        s = np.where(ok, (a[:, 0] * u[1] - a[:, 1] * u[0]) / np.where(ok, den, 1), -1)
        hit = ok & (r > 0) & (s >= 0) & (s <= 1)
        if hit.any():
            out[i] = r[hit].min()
    return out


def _surface(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Skin-side surface as points[level, angle] (nan in the rear opening)."""
    y0, y1 = mesh.bounds[0][1] + RIM_INSET_MM, mesh.bounds[1][1] - RIM_INSET_MM
    ys = np.arange(y0, y1 + 1e-9, LEVEL_STEP_MM)
    # Angles run from the rear (-z, theta = -90 deg) round through the front.
    thetas = np.radians(np.arange(-90.0, 270.0, RAY_STEP_DEG))
    pts = np.full((len(ys), len(thetas), 3), np.nan)
    for i, y in enumerate(ys):
        r = _inner_radius(_section_segments(mesh, y), thetas)
        pts[i, :, 0] = r * np.cos(thetas)
        pts[i, :, 1] = y
        pts[i, :, 2] = r * np.sin(thetas)
    return ys, thetas, pts


def _arc(points: np.ndarray) -> np.ndarray:
    steps = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(steps)])


def _covered(row: np.ndarray) -> tuple[int, int]:
    """First and last sampled angle with wall, going round from the opening."""
    idx = np.flatnonzero(~np.isnan(row[:, 0]))
    return int(idx[0]), int(idx[-1])


def _seams(pts: np.ndarray, count: int) -> list[int]:
    """Seam angle indices: equal arc length at the narrowest level."""
    widths = []
    for row in pts:
        a, b = _covered(row)
        widths.append(_arc(row[a : b + 1])[-1])
    waist = int(np.argmin(widths))
    row = pts[waist]
    a, b = _covered(row)
    s = _arc(row[a : b + 1])
    targets = np.linspace(0.0, s[-1], count + 1)[1:-1]
    return [a + int(np.searchsorted(s, t)) for t in targets]


def _flatten(pts: np.ndarray, lo: int | None, hi: int | None) -> dict:
    """Unroll the strip between angle indices lo and hi (None = opening edge)."""
    rows = []
    centre = None
    for row in pts:
        a, b = _covered(row)
        i0 = a if lo is None else lo
        i1 = b if hi is None else hi
        rows.append((i0, i1))
    mids = [(i0 + i1) // 2 for i0, i1 in rows]
    centre = int(np.median(mids))
    cpts = pts[:, centre]
    s = _arc(cpts)
    left, right = [], []
    for k, (row, (i0, i1)) in enumerate(zip(pts, rows)):
        seg = row[min(i0, centre) : max(i1, centre) + 1]
        arc = _arc(seg)
        c = centre - min(i0, centre)
        left.append((arc[i0 - min(i0, centre)] - arc[c], s[k]))
        right.append((arc[i1 - min(i0, centre)] - arc[c], s[k]))
    left, right = np.asarray(left), np.asarray(right)
    # The opening edge is found level by level, which steps; smooth it.
    for edge, is_open in ((left, lo is None), (right, hi is None)):
        if is_open:
            k = 9
            padded = np.pad(edge[:, 0], k // 2, mode="edge")
            edge[:, 0] = np.convolve(padded, np.ones(k) / k, mode="valid")

    def strain(edge2d: np.ndarray, idx: list[int]) -> float:
        edge3d = np.asarray([pts[k, i] for k, i in enumerate(idx)])
        flat, real = _arc(edge2d)[-1], _arc(edge3d)[-1]
        return abs(flat - real) / real

    left_s, right_s = strain(left, [r[0] for r in rows]), strain(right, [r[1] for r in rows])
    seam = max([v for v, edge in ((left_s, lo), (right_s, hi)) if edge is not None], default=0.0)
    opening = max([v for v, edge in ((left_s, lo), (right_s, hi)) if edge is None], default=0.0)
    return {
        "left": left, "right": right, "strain": seam, "opening_strain": opening,
        "open_left": lo is None, "open_right": hi is None,
    }


def _cut_outline(p: dict) -> tuple[np.ndarray, np.ndarray]:
    """Panel outline and cut outline (fold allowance past rims and opening ends)."""
    left, right = p["left"], p["right"]
    panel = np.vstack([left, right[::-1]])
    f = FOLD_ALLOWANCE_MM
    cl = left + np.array([-f if p["open_left"] else 0.0, 0.0])
    cr = right + np.array([f if p["open_right"] else 0.0, 0.0])
    cut = np.vstack(
        [[cl[0] - [0, f]], cl, [cl[-1] + [0, f]], [cr[-1] + [0, f]], cr[::-1], [cr[0] - [0, f]]]
    )
    return panel, cut


def _holes(panel: np.ndarray) -> list[tuple[float, float]]:
    safe = Polygon(panel).buffer(-HOLE_MARGIN_MM)
    if safe.is_empty:
        return []
    x0, y0, x1, y1 = safe.bounds
    holes = []
    row = 0
    y = y0
    while y <= y1:
        x = x0 + (HOLE_PITCH_MM / 2 if row % 2 else 0.0)
        while x <= x1:
            if safe.contains(Point(x, y)):
                holes.append((x, y))
            x += HOLE_PITCH_MM
        y += HOLE_PITCH_MM * math.sqrt(3) / 2
        row += 1
    return holes


def _names(count: int) -> list[str]:
    """Panels run from one side of the rear opening, round the front, to the other."""
    return [f"P{i + 1}" for i in range(count)]


INSTRUCTIONS = """Collar sleeve liner: shopping list and steps

SHOPPING (Tandy Leather)
  [ ] Veg-Tan Lambskin, 1-2 oz (0.4-0.8 mm). Pick the thinnest, softest hide and ask
      staff to gauge it: aim for 1 oz (0.4 mm). The {count} panels need only {area:.1f} sq ft,
      so any hide (6-8 sq ft) leaves plenty for a test scrap and remakes.
      Do NOT buy Mirrabella lambskin: it is chrome-tanned (skin-allergy risk with sweat).
  [ ] Barge All-Purpose Cement, 2 fl oz.
  [ ] Craftool Round Drive Punch, size 00 (1.6 mm). Only if perforating.
  [ ] Poly punch board and a poly mallet, if you don't have a hard surface and mallet.
  [ ] Glue spreaders or a small disposable brush.
  [ ] Rotary cutter or sharp craft knife, and a cutting mat.
  At home or a hardware store: 220-grit sandpaper, isopropyl alcohol, painter's tape,
  scissors, and a bone folder or the back of a spoon for pressing.

STEPS
  1. Print the panel pages at 100%. Check the 50 mm square with a ruler.
  2. Patch test: tape a scrap of the leather to Melissa's neck for a day.
  3. Cut the paper panels on the solid line and test-fit them inside the sleeve: P{front}
     centred on the throat, chin arrows up, edges butting, dashed lines on the rims.
  4. Trace each panel onto the grain (smooth) side. Pencil the panel number on the back.
  5. Optional: punch the holes on the punch board, then cut the panels out.
  6. Scuff the inside of the sleeve and the rim lips with 220-grit. Wipe with alcohol.
     Test the glue on a scrap of TPU first (a failed print works).
  7. Thin coat of Barge on the sleeve and the back of one panel. Wait until tacky
     (about 10-15 minutes, dry to a light touch). Place P{front} first, centred on the
     throat, pressing from the middle outward. Then the panels either side, butting
     the edges, then the end panels at the rear opening.
  8. Fold the allowances over the rims and the opening ends and glue them to the
     outside. Snip small V-notches in the allowance where it puckers on the flares.
  9. Let it air out for 24-48 hours before Melissa wears it.

FIT: 0.4 mm leather uses about a fifth of the sleeve's 2 mm skin clearance. If the
hide is closer to 0.8 mm, the sleeve can be regenerated with more clearance first.
"""


def _instructions_page(pdf: PdfPages, count: int, area: float) -> None:
    w, h = PAGE_MM
    fig = plt.figure(figsize=(w / 25.4, h / 25.4))
    fig.text(
        PAGE_MARGIN_MM / w, 1 - PAGE_MARGIN_MM / h,
        INSTRUCTIONS.format(count=count, area=area, front=count // 2 + 1),
        family="monospace", fontsize=8.2, va="top", linespacing=1.45,
    )
    pdf.savefig(fig)
    plt.close(fig)


def _draw_page(pdf: PdfPages, panels: list[dict], title: str) -> None:
    w, h = PAGE_MM
    fig = plt.figure(figsize=(w / 25.4, h / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(PAGE_MARGIN_MM, h - PAGE_MARGIN_MM, title, fontsize=10, va="top", weight="bold")
    ax.text(
        PAGE_MARGIN_MM, h - PAGE_MARGIN_MM - 6,
        "Print at 100% (no fit-to-page). The square must measure 50 mm.\n"
        "Solid line = cut. Dashed line = fold onto the outside of the sleeve.\n"
        "Drawn as seen from the skin side: trace onto the grain (smooth) side.\n"
        "Small circles = 1.6 mm holes (optional). Ticks mark where panels butt together.",
        fontsize=7, va="top", linespacing=1.5,
    )
    sq = PAGE_MARGIN_MM
    ax.add_patch(plt.Rectangle((w - sq - 50, h - sq - 50), 50, 50, fill=False, lw=0.6))
    ax.text(w - sq - 25, h - sq - 25, "50 mm", ha="center", va="center", fontsize=7)
    for p in panels:
        ox, oy = p["origin"]
        panel, cut = p["panel_xy"], p["cut_xy"]
        ax.plot(*np.vstack([cut, cut[:1]]).T + np.array([[ox], [oy]]), "k-", lw=0.8)
        # fold lines: the rims, and the opening edge where present
        L, R = p["left"] + [ox, oy], p["right"] + [ox, oy]
        ax.plot([L[-1, 0], R[-1, 0]], [L[-1, 1], R[-1, 1]], "k--", lw=0.5)
        ax.plot([L[0, 0], R[0, 0]], [L[0, 1], R[0, 1]], "k--", lw=0.5)
        if p["open_left"]:
            ax.plot(*L.T, "k--", lw=0.5)
        if p["open_right"]:
            ax.plot(*R.T, "k--", lw=0.5)
        for hx, hy in p["holes"]:
            ax.add_patch(plt.Circle((hx + ox, hy + oy), HOLE_DIA_MM / 2, fill=False, lw=0.35))
        cx = (L[:, 0].mean() + R[:, 0].mean()) / 2
        cy = (L[0, 1] + L[-1, 1]) / 2
        ax.text(cx, cy, p["name"], ha="center", va="center", fontsize=14, weight="bold", alpha=0.35)
        if p.get("front"):
            ax.text(cx, cy - 7, "front (throat)", ha="center", va="center", fontsize=7, alpha=0.6)
        ax.annotate(
            "", xy=(cx, L[-1, 1] - 3), xytext=(cx, L[-1, 1] - 13),
            arrowprops=dict(arrowstyle="->", lw=0.6),
        )
        ax.text(cx + 1.5, L[-1, 1] - 8, "chin", fontsize=6, va="center")
        for side, edge, nb in (("left", L, p["left_neighbour"]), ("right", R, p["right_neighbour"])):
            if nb:
                mid = edge[len(edge) // 2]
                dx = -1 if side == "left" else 1
                ax.plot([mid[0], mid[0] + 3 * dx], [mid[1], mid[1]], "k-", lw=0.6)
                ax.text(mid[0] - 2 * dx, mid[1] + 3, f"to {nb}", fontsize=5, ha="center")
    pdf.savefig(fig)
    plt.close(fig)


def _layout(panels: list[dict]) -> list[list[dict]]:
    """Pack panels left to right, then onto new pages."""
    w, h = PAGE_MM
    usable_w = w - 2 * PAGE_MARGIN_MM
    top = h - PAGE_MARGIN_MM - 62  # below the title and check square
    pages, page, x, y_row, row_h = [], [], PAGE_MARGIN_MM, top, 0.0
    for p in panels:
        cut = p["cut_xy"]
        pw, ph = np.ptp(cut[:, 0]), np.ptp(cut[:, 1])
        if x + pw > PAGE_MARGIN_MM + usable_w:
            x, y_row, row_h = PAGE_MARGIN_MM, y_row - row_h - 8, 0.0
        if y_row - ph < PAGE_MARGIN_MM:
            pages.append(page)
            page, x, y_row, row_h = [], PAGE_MARGIN_MM, top, 0.0
        p["origin"] = (x - cut[:, 0].min(), y_row - cut[:, 1].max())
        page.append(p)
        x += pw + 8
        row_h = max(row_h, ph)
    pages.append(page)
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sleeve", type=Path, default=PROJECT_ROOT / "build" / "cord-brace" / "sleeve-local.stl")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build" / "sleeve-liner")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    mesh = trimesh.load_mesh(args.sleeve)
    ys, thetas, pts = _surface(mesh)

    for count in PANEL_COUNTS:
        seams = _seams(pts, count)
        bounds = [None, *seams, None]
        flats = [_flatten(pts, lo, hi) for lo, hi in zip(bounds[:-1], bounds[1:])]
        if max(f["strain"] for f in flats) < MAX_STRAIN:
            break
    names = _names(count)
    panels = []
    for i, f in enumerate(flats):
        panel, cut = _cut_outline(f)
        f.update(
            name=names[i],
            panel_xy=panel,
            cut_xy=cut,
            holes=_holes(panel),
            left_neighbour=names[i - 1] if i > 0 else None,
            right_neighbour=names[i + 1] if i < count - 1 else None,
            front=i == count // 2,
        )
        panels.append(f)

    pages = _layout(panels)
    area = sum(Polygon(p["cut_xy"]).area for p in panels) / 92903.04
    with PdfPages(args.output / "sleeve-liner-pattern.pdf") as pdf:
        _instructions_page(pdf, count, area)
        for n, page in enumerate(pages):
            _draw_page(
                pdf, page,
                f"Collar sleeve liner panels, page {n + 2} of {len(pages) + 1}",
            )

    report = {
        "panels": [
            {
                "name": p["name"],
                "width_mm": round(float(np.ptp(p["panel_xy"][:, 0])), 1),
                "height_mm": round(float(np.ptp(p["panel_xy"][:, 1])), 1),
                "seam_edge_stretch_pct": round(100 * p["strain"], 2),
                "opening_edge_stretch_pct": round(100 * p["opening_strain"], 2),
                "holes": len(p["holes"]),
                "cut_area_mm2": round(Polygon(p["cut_xy"]).area, 0),
            }
            for p in panels
        ],
        "seam_angles_deg": [round(math.degrees(thetas[s]), 1) for s in seams],
        "total_cut_area_sqft": round(sum(Polygon(p["cut_xy"]).area for p in panels) / 92903.04, 2),
        "pages": len(pages),
    }
    (args.output / "liner.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
