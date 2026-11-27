"""Quantile dotplots (D5): 20 dots, each 5% of simulated futures, on a log axis.

Dots for "nothing happens" (zero DALYs) sit in their own column left of the axis,
so the point mass at zero stays visible.
"""

from __future__ import annotations

import math

N_DOTS = 20


def fmt(v: float) -> str:
    """Two significant figures, with k/M/B suffixes (e.g. 33,000 → '33k')."""
    if v == 0:
        return "0"
    v = float(f"{v:.2g}")  # two significant figures, before choosing the suffix
    suf, div = "", 1.0
    for d, s in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(v) >= d:
            div, suf = d, s
            break
    x = v / div
    digits = max(1 - int(math.floor(math.log10(abs(x)))), 0)
    return f"{x:.{digits}f}{suf}"


def fmt_ratio(r: float) -> str:
    """A ratio people can read: '2.3×', '45%', or '1/36,000' (two significant figures)."""
    if r <= 0:
        return "0"
    if r >= 1:
        return f"{fmt(r)}×"
    if r >= 0.01:
        return f"{float(f'{r * 100:.2g}'):g}%"
    return f"1/{float(f'{1 / r:.2g}'):,.0f}"


def ratio_phrase(r: float, label: str) -> str:
    """'about 1/36,000 of air pollution', '45% of tobacco', '2.3× air pollution'."""
    return f"{fmt_ratio(r)} {label}" if r >= 1 else f"about {fmt_ratio(r)} of {label}"


def power_of_ten(v: float) -> str:
    """'10⁴' for 33,000."""
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return "10" + str(int(math.floor(math.log10(v)))).translate(sup)


def _layout(quantiles: list[float], bins_per_decade: int = 8):
    zeros = sum(1 for q in quantiles if q <= 0)
    pos = [q for q in quantiles if q > 0]
    if not pos:
        return zeros, {}, (0, 1)
    lo = math.floor(math.log10(min(pos)))
    hi = math.ceil(math.log10(max(pos)))
    if hi == lo:
        hi += 1
    stacks: dict[int, int] = {}
    for q in pos:
        b = int((math.log10(q) - lo) * bins_per_decade)
        stacks[b] = stacks.get(b, 0) + 1
    return zeros, stacks, (lo, hi)


def svg(quantiles: list[float], title: str, mock: bool = False, width: int = 560) -> str:
    bpd = 8
    zeros, stacks, (lo, hi) = _layout(quantiles, bpd)
    r = 7
    d = 2 * r + 2
    left_col = 70  # zero column
    x0, x1 = left_col + 30, width - 20
    top_n = max([zeros, *stacks.values(), 1])
    base_y = 40 + top_n * d
    height = base_y + 50
    nbins = (hi - lo) * bpd

    def bx(b: float) -> float:
        return x0 + (b + 0.5) / nbins * (x1 - x0)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="sans-serif" font-size="11" role="img" aria-label="{title}">',
        f'<text x="{width / 2}" y="16" text-anchor="middle" font-size="12">{title}</text>',
    ]
    if mock:
        out.append(
            f'<text x="{width / 2}" y="30" text-anchor="middle" fill="#b00" '
            f'font-weight="bold">INVENTED (MOCK) DATA</text>'
        )
    # zero column
    out.append(
        f'<line x1="{left_col + 15}" y1="36" x2="{left_col + 15}" y2="{base_y + 4}" '
        f'stroke="#bbb" stroke-dasharray="3,3"/>'
    )
    out.append(
        f'<text x="{left_col / 2 + 10}" y="{base_y + 18}" text-anchor="middle">nothing</text>'
    )
    out.append(
        f'<text x="{left_col / 2 + 10}" y="{base_y + 30}" text-anchor="middle">happens</text>'
    )
    for i in range(zeros):
        out.append(
            f'<circle cx="{left_col / 2 + 10}" cy="{base_y - r - i * d}" r="{r}" fill="#888"/>'
        )
    # log axis
    out.append(f'<line x1="{x0}" y1="{base_y + 2}" x2="{x1}" y2="{base_y + 2}" stroke="#333"/>')
    for e in range(lo, hi + 1):
        x = x0 + (e - lo) / (hi - lo) * (x1 - x0)
        out.append(f'<line x1="{x}" y1="{base_y + 2}" x2="{x}" y2="{base_y + 7}" stroke="#333"/>')
        out.append(f'<text x="{x}" y="{base_y + 20}" text-anchor="middle">{fmt(10.0**e)}</text>')
    out.append(
        f'<text x="{(x0 + x1) / 2}" y="{base_y + 36}" text-anchor="middle">'
        f"DALYs (log scale) · each dot = 5% of simulated futures</text>"
    )
    for b, k in sorted(stacks.items()):
        for i in range(k):
            out.append(
                f'<circle cx="{bx(b):.1f}" cy="{base_y - r - i * d}" r="{r}" fill="#c0504d"/>'
            )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def text(quantiles: list[float], bins_per_decade: int = 4) -> str:
    """Terminal version: one column per bin, dots stacked upwards."""
    zeros, stacks, (lo, hi) = _layout(quantiles, bins_per_decade)
    nbins = (hi - lo) * bins_per_decade
    rows = max([zeros, *stacks.values(), 1])
    cell = 3
    lines = []
    for level in range(rows, 0, -1):
        z = " ● " if zeros >= level else "   "
        body = "".join(" ● " if stacks.get(b, 0) >= level else "   " for b in range(nbins))
        lines.append(f"{z} │{body}")
    lines.append("────┼" + "─" * (nbins * cell))
    labels = [" "] * (nbins * cell + 8)
    for e in range(lo, hi + 1):
        s = fmt(10.0**e)
        p = (e - lo) * bins_per_decade * cell
        for i, ch in enumerate(s):
            if p + i < len(labels):
                labels[p + i] = ch
    lines.append(" 0  │" + "".join(labels).rstrip())
    lines.append(
        "     DALYs, log scale; each ● = 5% of simulated futures; '0' column = nothing happens"
    )
    return "\n".join(lines)


# ---- signed dotplots for net cards (D17, D5 as amended) ----------------------------
#
# A mirrored log axis: net benefit (negative values) on the left, log scale of |value|
# growing leftwards; a central column for zero; net harm (positive values) on the right.
# Both sides share the same decades, so equal distances mean equal ratios on either side.


def fmt_net(v: float) -> str:
    """'33k averted', '1.2k lost', '0'."""
    if v == 0:
        return "0"
    return f"{fmt(abs(v))} {'averted' if v < 0 else 'lost'}"


def _signed_layout(quantiles: list[float], bins_per_decade: int):
    zeros = sum(1 for q in quantiles if q == 0)
    mags = [abs(q) for q in quantiles if q != 0]
    if not mags:
        return zeros, {}, {}, (0, 1)
    lo = math.floor(math.log10(min(mags)))
    hi = math.ceil(math.log10(max(mags)))
    if hi == lo:
        hi += 1
    neg: dict[int, int] = {}
    pos: dict[int, int] = {}
    for q in quantiles:
        if q == 0:
            continue
        b = min(int((math.log10(abs(q)) - lo) * bins_per_decade), (hi - lo) * bins_per_decade - 1)
        side = pos if q > 0 else neg
        side[b] = side.get(b, 0) + 1
    return zeros, neg, pos, (lo, hi)


def svg_signed(quantiles: list[float], title: str, mock: bool = False, width: int = 640) -> str:
    bpd = 4
    zeros, neg, pos, (lo, hi) = _signed_layout(quantiles, bpd)
    r = 6
    d = 2 * r + 2
    mid = width / 2
    half = mid - 50  # each side's axis length
    col = 22  # half-width of the zero column
    top_n = max([zeros, *neg.values(), *pos.values(), 1])
    base_y = 44 + top_n * d
    height = base_y + 56
    nbins = (hi - lo) * bpd

    def side_x(b: float, sign: int) -> float:
        return mid + sign * (col + (b + 0.5) / nbins * (half - col))

    def tick_x(e: int, sign: int) -> float:
        return mid + sign * (col + (e - lo) / (hi - lo) * (half - col))

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="sans-serif" font-size="11" role="img" aria-label="{title}">',
        f'<text x="{mid}" y="16" text-anchor="middle" font-size="12">{title}</text>',
    ]
    if mock:
        out.append(
            f'<text x="{mid}" y="30" text-anchor="middle" fill="#b00" '
            f'font-weight="bold">INVENTED (MOCK) DATA</text>'
        )
    out.append(
        f'<rect x="{mid - col}" y="36" width="{2 * col}" height="{base_y - 34}" fill="#f2f2f2"/>'
    )
    for sign in (-1, 1):
        a, b = tick_x(lo, sign), tick_x(hi, sign)
        out.append(f'<line x1="{a}" y1="{base_y + 2}" x2="{b}" y2="{base_y + 2}" stroke="#333"/>')
        for e in range(lo, hi + 1):
            x = tick_x(e, sign)
            out.append(
                f'<line x1="{x}" y1="{base_y + 2}" x2="{x}" y2="{base_y + 7}" stroke="#333"/>'
            )
            out.append(
                f'<text x="{x}" y="{base_y + 20}" text-anchor="middle">{fmt(10.0**e)}</text>'
            )
    out += [
        f'<text x="{mid}" y="{base_y + 20}" text-anchor="middle">0</text>',
        f'<text x="{mid - half / 2}" y="{base_y + 36}" text-anchor="middle" fill="#2e7d32">'
        "◀ net benefit (DALYs averted)</text>",
        f'<text x="{mid + half / 2}" y="{base_y + 36}" text-anchor="middle" fill="#c0504d">'
        "net harm (DALYs lost) ▶</text>",
        f'<text x="{mid}" y="{base_y + 50}" text-anchor="middle">'
        "log scale on each side of zero · each dot = 5% of simulated futures</text>",
    ]
    for i in range(zeros):
        out.append(f'<circle cx="{mid}" cy="{base_y - r - i * d}" r="{r}" fill="#888"/>')
    for stacks, sign, colour in ((neg, -1, "#2e7d32"), (pos, 1, "#c0504d")):
        for b, k in sorted(stacks.items()):
            for i in range(k):
                out.append(
                    f'<circle cx="{side_x(b, sign):.1f}" cy="{base_y - r - i * d}" r="{r}" '
                    f'fill="{colour}"/>'
                )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def text_signed(quantiles: list[float], bins_per_decade: int = 2) -> str:
    """Terminal version of the mirrored log axis: ◀ benefit | 0 | harm ▶."""
    zeros, neg, pos, (lo, hi) = _signed_layout(quantiles, bins_per_decade)
    nbins = (hi - lo) * bins_per_decade
    rows = max([zeros, *neg.values(), *pos.values(), 1])
    cell = 3
    lines = []
    for level in range(rows, 0, -1):
        left = "".join(" ● " if neg.get(b, 0) >= level else "   " for b in range(nbins - 1, -1, -1))
        z = " ● " if zeros >= level else "   "
        right = "".join(" ● " if pos.get(b, 0) >= level else "   " for b in range(nbins))
        lines.append(f"{left}│{z}│{right}")
    lines.append("─" * (nbins * cell) + "┼───┼" + "─" * (nbins * cell))

    def labels(reverse: bool) -> str:
        cells = [" "] * (nbins * cell)
        for e in range(lo, hi + 1):
            s = fmt(10.0**e)
            p = (e - lo) * bins_per_decade * cell
            if reverse:
                p = nbins * cell - p - len(s)
            for i, ch in enumerate(s):
                if 0 <= p + i < len(cells):
                    cells[p + i] = ch
        return "".join(cells)

    lines.append(labels(True) + "  0  " + labels(False))
    lines.append(
        "◀ net benefit (DALYs averted) · net harm (DALYs lost) ▶ · log scale each side; "
        "each ● = 5% of simulated futures"
    )
    return "\n".join(lines)
