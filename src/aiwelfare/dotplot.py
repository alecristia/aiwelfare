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
