"""The overview chart and parameter explorer (D6), shared by the site build and the browser.

This module runs in two places with the same code:
- in `aiwelfare build site`, which draws the canonical default chart from the CLI's results;
- in the reader's browser under Pyodide (D8), which reruns the repo's own models when a
  setting changes.

It imports only NumPy and the numpy-only parts of the package (engine, dotplot), so it loads
in Pyodide without the CLI's dependencies. Every number it shows is what
`aiwelfare whatif <risk> --set PARAM=VALUE --counterfactual CF` prints (D10): same model
code, same seed, same draw count.
"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, quote

import numpy as np

from . import engine
from .dotplot import fmt, fmt_net

DEFAULT_COUNTERFACTUAL = "frozen-2026"  # same as card.DEFAULT_COUNTERFACTUAL (card imports yaml)
COUNTERFACTUALS = {
    "no-ai": "No modern AI",
    "frozen-2026": "AI frozen at 2026 levels",
    "open-only": "Only open-weight / older models advance",
}
GROUPS = {  # International AI Safety Report categories plus benefits (D7), in display order
    "malicious-use": "Malicious use",
    "malfunctions": "Malfunctions and everyday use",
    "systemic-risks": "Systemic risks",
    "benefits": "Benefits",
}
FILTERS = {
    "tail": "Tail-dominated only (D11)",
    "ml": "Has kinds of work close to ML engineering",
}
COLOURS = {"harm": "#c0504d", "benefit": "#2e7d32"}  # as on the cards' dotplots (D5, D17)
BASELINE_COLOUR = "#7a7a7a"
NOT_SUMMED = (
    "Estimates overlap and are not summed: there is no total row "
    "(VISION.md, Modelling decisions 7)."
)


# ---- browser-side dataset ------------------------------------------------------


@dataclass
class BrowserDataset:
    """What `engine.Model.load` needs, without YAML or schemas (Pyodide, D8).

    `claims` holds only the fields models and the loader read: value, evidence basis and type.
    """

    root: Path
    include_mock: bool
    claims: dict[str, dict] = field(default_factory=dict)


# ---- state: counterfactual, fixed parameters, filters ----------------------------


@dataclass
class State:
    counterfactual: str = DEFAULT_COUNTERFACTUAL
    settings: dict[str, dict[str, str]] = field(default_factory=dict)  # risk -> param -> value
    filters: list[str] = field(default_factory=list)

    @property
    def is_canonical(self) -> bool:
        """No parameter fixed and no filter: a canonical chart under any of the three
        comparisons, all of which the cards report. Otherwise the "your settings" banner shows."""
        return not any(self.settings.values()) and not self.filters

    @property
    def is_default(self) -> bool:
        """The canonical chart under the default comparison: the page's plain address."""
        return self.is_canonical and self.counterfactual == DEFAULT_COUNTERFACTUAL

    def to_dict(self) -> dict:
        return {
            "counterfactual": self.counterfactual,
            "settings": {r: dict(s) for r, s in sorted(self.settings.items()) if s},
            "filters": sorted(self.filters),
        }


def canonical_number(v: float | str) -> str:
    """The text a numeric setting is written as, in the URL and in `whatif --set`."""
    # No "+" in exponents: in a query string "+" reads back as a space.
    return format(float(v), ".6g").replace("e+", "e")


def _param_spec(spec: dict, risk: str, name: str) -> dict | None:
    for card in spec["cards"]:
        if card["risk"] == risk:
            return next((p for p in card["params"] if p["name"] == name), None)
    return None


def normalise(state: State, spec: dict) -> tuple[State, list[str]]:
    """Drop settings the spec does not know; canonicalise numbers. Returns (state, problems)."""
    problems = []
    cf = state.counterfactual
    if cf not in COUNTERFACTUALS:
        problems.append(f"unknown counterfactual {cf!r}; using the default")
        cf = DEFAULT_COUNTERFACTUAL
    settings: dict[str, dict[str, str]] = {}
    for risk, ps in state.settings.items():
        for name, raw in ps.items():
            p = _param_spec(spec, risk, name)
            if p is None:
                problems.append(f"unknown parameter {risk}.{name}; ignored")
                continue
            if p["categorical"]:
                if raw not in p["categories"]:
                    problems.append(f"{risk}.{name} takes one of {p['categories']}; ignored")
                    continue
                value = raw
            else:
                try:
                    value = canonical_number(raw)
                except ValueError:
                    problems.append(f"{risk}.{name}={raw!r} is not a number; ignored")
                    continue
                if not math.isfinite(float(value)):
                    problems.append(f"{risk}.{name}={raw!r} is not finite; ignored")
                    continue
            settings.setdefault(risk, {})[name] = value
    filters = sorted({f for f in state.filters if f in FILTERS})
    problems += [f"unknown filter {f!r}; ignored" for f in state.filters if f not in FILTERS]
    return State(cf, settings, filters), problems


def encode(state: State) -> str:
    """Every setting in the URL (D6). Empty for the canonical default."""
    parts = []
    if state.counterfactual != DEFAULT_COUNTERFACTUAL:
        parts.append(("cf", state.counterfactual))
    for risk in sorted(state.settings):
        for name in sorted(state.settings[risk]):
            parts.append((f"{risk}.{name}", state.settings[risk][name]))
    parts += [("filter", f) for f in sorted(state.filters)]
    return "&".join(f"{quote(k, safe='.-_')}={quote(v, safe='.-_')}" for k, v in parts)


def describe(state: State) -> str:
    """The non-canonical settings, readable, for the banner inside the chart."""
    parts = [
        f"{r}: {k}={v}"
        for r in sorted(state.settings)
        for k, v in sorted(state.settings[r].items())
    ]
    parts += [f"filter: {f}" for f in sorted(state.filters)]
    return "; ".join(parts)


def decode(query: str, spec: dict) -> tuple[State, list[str]]:
    state = State()
    for k, v in parse_qsl(query.lstrip("?"), keep_blank_values=True):
        if k == "cf":
            state.counterfactual = v
        elif k == "filter":
            state.filters.append(v)
        elif "." in k:
            risk, name = k.split(".", 1)
            state.settings.setdefault(risk, {})[name] = v
    return normalise(state, spec)


def whatif_commands(state: State, spec: dict) -> list[str]:
    """The CLI commands that reproduce each row under these settings (D10)."""
    mock = " --include-mock" if spec["mock"] else ""
    out = []
    for card in spec["cards"]:
        r = card["risk"]
        cf = f" --counterfactual {state.counterfactual}"
        sets = state.settings.get(r, {})
        if state.counterfactual not in card["counterfactuals"]:
            continue
        if sets:
            args = " ".join(f"--set {_shell(f'{k}={v}')}" for k, v in sorted(sets.items()))
            out.append(f"aiwelfare whatif risk/{r} {args}{cf}{mock}")
        else:
            out.append(f"aiwelfare dist risk/{r}{cf}{mock}")
    return out


def _shell(s: str) -> str:
    return s if all(c.isalnum() or c in "=._-+" for c in s) else "'" + s.replace("'", "'\\''") + "'"


# ---- computing rows ----------------------------------------------------------------

_cache: dict = {}


def fixed_values(card: dict, sets: dict[str, str]) -> dict:
    """Settings as `whatif` passes them to the engine: variant index or float."""
    out = {}
    for name, v in sets.items():
        p = next(p for p in card["params"] if p["name"] == name)
        out[name] = p["categories"].index(v) if p["categorical"] else float(v)
    return out


def summarise_run(model, counterfactual: str, n: int, seed: int, fixed: dict) -> dict:
    """Exactly what `aiwelfare whatif` reports as "yours" (and `dist` with no settings):
    the net for net cards (D17), signed; the single quantity otherwise."""
    comps, _ = model.run_components(counterfactual, n, seed, fixed or None)
    return engine.summarise_model(model, comps)


def compute(models: dict, spec: dict, state: State) -> list[dict]:
    """One row per card under `state`, from the models themselves."""
    rows = []
    for card in spec["cards"]:
        r, cf = card["risk"], state.counterfactual
        if cf not in card["counterfactuals"]:
            rows.append(_row(card, None))
            continue
        sets = state.settings.get(r, {})
        key = (r, cf, tuple(sorted(sets.items())), spec["draws"], spec["seed"])
        if key not in _cache:
            _cache[key] = summarise_run(
                models[r], cf, spec["draws"], spec["seed"], fixed_values(card, sets)
            )
        rows.append(_row(card, _cache[key]))
    return rows


def canonical_rows(spec: dict, counterfactual: str) -> list[dict]:
    """Rows from the CLI's own results (card.json), for the static default chart."""
    return [_row(card, card["results"].get(counterfactual)) for card in spec["cards"]]


def _row(card: dict, summary: dict | None) -> dict:
    keep = ("expected_value", "median", "p05", "p95", "share_zero", "top5_share_of_ev")
    return {
        "risk": card["risk"],
        "title": card["title"],
        "kind": card["kind"],
        "group": card["group"],
        "href": card["href"],
        "close_to_ml": card["close_to_ml"],
        "modelled": summary is not None,
        "summary": {k: summary[k] for k in keep}
        | {"tail_dominated": summary["tail_dominated"]}
        | ({"share_net_harm": summary["share_net_harm"]} if "share_net_harm" in summary else {})
        if summary
        else None,
    }


def not_modelled_reason(card: dict, counterfactual: str) -> str:
    return card["not_modelled"].get(counterfactual, "No reason recorded.")


# ---- the forest plot (D6) -----------------------------------------------------------

W = 940
LABEL_W = 300
ZERO_X = LABEL_W + 22  # one-sided axis: the "nothing happens" column, left of the log axis
X0, X1 = LABEL_W + 56, W - 24
MID = (LABEL_W + 20 + X1) / 2  # mirrored axis (net cards, D17): the zero column's centre
COL = 16  # half-width of the mirrored axis's zero column
ROW_H = 36
GROUP_H = 26
HALO = ' paint-order="stroke" stroke="#fff" stroke-width="3" stroke-linejoin="round"'


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _wrap(s: str, width: int) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + ([cur] if cur else [])


def _axis_range(rows: list[dict], baselines: list[dict]) -> tuple[int, int]:
    vals = [b["dalys_window"] for b in baselines]
    for r in rows:
        if r["modelled"]:
            s = r["summary"]
            vals += [s[k] for k in ("expected_value", "median", "p05", "p95")]
    pos = [abs(v) for v in vals if v != 0]  # magnitudes: a mirrored axis shares its decades
    if not pos:
        return 3, 9
    lo, hi = math.floor(math.log10(min(pos))), math.ceil(math.log10(max(pos)))
    return lo, max(hi, lo + 1)


def visible_rows(rows: list[dict], filters: list[str]) -> list[dict]:
    out = []
    for r in rows:
        if "tail" in filters and not (r["modelled"] and r["summary"]["tail_dominated"]):
            continue
        if "ml" in filters and not r["close_to_ml"]:
            continue
        out.append(r)
    return out


def signed_axis(spec: dict) -> bool:
    """A mirrored log axis whenever a net card is on the chart (D17), so the axis does not
    change shape when a setting moves a net across zero."""
    return any(c["kind"] == "net" for c in spec["cards"])


def scale(lo: int, hi: int, signed: bool):
    """x position of a value. One-sided: 0 in its own column left of the log axis (D5).
    Mirrored: net benefit (negative) left of a central zero column, net harm right (D17)."""

    def x(v: float) -> float:
        if not signed:
            if v <= 0:
                return ZERO_X
            return X0 + (math.log10(max(v, 10.0**lo)) - lo) / (hi - lo) * (X1 - X0)
        if v == 0:
            return MID
        t = (math.log10(max(abs(v), 10.0**lo)) - lo) / (hi - lo)
        return MID + math.copysign(COL + t * (X1 - MID - COL), v)

    return x


def ordered(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    """Grouped (D7), groups in a fixed order; within each, by the size of the expected value
    (its magnitude, for net cards), largest first."""
    out = []
    groups = list(GROUPS) + sorted({r["group"] for r in rows} - set(GROUPS))
    for g in groups:
        members = [r for r in rows if r["group"] == g]
        if not members:
            continue
        members.sort(
            key=lambda r: (
                not r["modelled"],
                -(abs(r["summary"]["expected_value"]) if r["modelled"] else 0),
                r["title"],
            )
        )
        out.append((g, members))
    return out


def forest_svg(
    rows: list[dict],
    baselines: list[dict],
    spec: dict,
    state: State,
) -> str:
    """The overview chart. Everything needed to read or trace a screenshot is inside it."""
    cards = {c["risk"]: c for c in spec["cards"]}
    shown = visible_rows(rows, state.filters)
    groups = ordered(shown)
    lo, hi = _axis_range([r for r in shown if r["modelled"]], baselines)
    w0, w1 = spec["window"]
    signed = signed_axis(spec)
    x = scale(lo, hi, signed)
    zero_x = MID if signed else ZERO_X

    banners: list[tuple[str, str]] = []
    if spec["mock"]:
        banners.append(("#b00", "INVENTED (MOCK) DATA. FORMAT DEMONSTRATION ONLY. DO NOT QUOTE."))
    if spec.get("regional"):
        banners.append(("#b00", "DEVELOPMENT BUILD: INCLUDES NON-GLOBAL CARDS. NOT FOR CITING."))
    if not state.is_canonical:
        banners.append(("#8a5a00", "YOUR SETTINGS, NOT THE CANONICAL CHART: " + describe(state)))

    lines_top = 18 + 18 * len(banners) + 20  # title + banners + subtitle
    bl_sorted = sorted(baselines, key=lambda b: b["dalys_window"])
    label_h = 14 * len(bl_sorted) + 8
    plot_top = lines_top + label_h + 6
    body_h = sum(GROUP_H + ROW_H * max(len(m), 0) for _, m in groups)
    body_h += sum(ROW_H for _, m in groups for r in m if not r["modelled"])  # 2-line reasons
    if not shown:
        body_h = 60
    axis_y = plot_top + body_h + 6
    height = axis_y + 92 + (18 if spec["mock"] else 0)

    o: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height:.0f}" '
        f'width="{W}" height="{height:.0f}" font-family="system-ui, sans-serif" font-size="12" '
        f'role="img" aria-labelledby="forest-title" class="forest">',
        f'<title id="forest-title">Global DALYs {w0}–{w1} by card, compared with '
        f"{_esc(COUNTERFACTUALS[state.counterfactual])}</title>",
        f'<rect width="{W}" height="{height:.0f}" fill="#fff"/>',
        f'<text x="12" y="18" font-size="15" font-weight="600">Global DALYs, {w0}–{w1}, '
        f"compared with: {_esc(COUNTERFACTUALS[state.counterfactual])}</text>",
    ]
    y = 18
    for colour, text in banners:
        y += 18
        o.append(
            f'<text x="12" y="{y}" fill="{colour}" font-weight="700">{_esc(text[:150])}</text>'
        )
    y += 18
    o.append(
        f'<text x="12" y="{y}" fill="#555">Dot: median · bar: 90% of simulated futures · '
        f"◇: expected value · dashed bar: tail-dominated (D11) · "
        + ("log scale on each side of zero" if signed else "log scale")
        + "</text>"
    )

    # baselines: labelled vertical reference lines (D6, D16), labels stacked so none overlap
    # On a mirrored axis they are burdens, so they sit on the harm side, mirrored (unlabelled)
    # on the benefit side so DALYs averted can be read against them too.
    for i, b in enumerate(bl_sorted):
        bx = x(b["dalys_window"])
        ly = lines_top + 12 + 14 * i
        anchor = "end" if bx > ((MID + X1) / 2 if signed else (X0 + X1) / 2) else "start"
        dx = -4 if anchor == "end" else 4
        o.append(
            f'<line x1="{bx:.1f}" y1="{ly + 3}" x2="{bx:.1f}" y2="{axis_y}" '
            f'stroke="{BASELINE_COLOUR}" stroke-width="1" stroke-dasharray="1,2"/>'
        )
        if signed:
            mx = x(-b["dalys_window"])
            o.append(
                f'<line x1="{mx:.1f}" y1="{plot_top}" x2="{mx:.1f}" y2="{axis_y}" '
                f'stroke="{BASELINE_COLOUR}" stroke-opacity="0.5" stroke-width="1" '
                f'stroke-dasharray="1,2"/>'
            )
        o.append(
            f'<text x="{bx + dx:.1f}" y="{ly}" text-anchor="{anchor}" fill="#444" '
            f'font-size="11"{HALO}>{_esc(b["label"])} · {fmt(b["dalys_window"])}</text>'
        )

    # zero column (nothing happens / no net effect), as on the cards' dotplots (D5, D17)
    if signed:
        o.append(
            f'<rect x="{MID - COL}" y="{plot_top}" width="{2 * COL}" height="{axis_y - plot_top}" '
            f'fill="#f2f2f2"/>'
        )
    o.append(
        f'<line x1="{zero_x}" y1="{plot_top}" x2="{zero_x}" y2="{axis_y}" stroke="#ccc" '
        f'stroke-dasharray="3,3"/>'
    )

    y = plot_top
    if not shown:
        o.append(
            f'<text x="{X0}" y="{y + 30}" fill="#555" font-style="italic">'
            + (
                "No card matches the filters."
                if rows
                else "No card has a global estimate yet. The reference lines are the baselines."
            )
            + "</text>"
        )
    for g, members in groups:
        o.append(
            f'<rect x="0" y="{y}" width="{W}" height="{GROUP_H}" fill="#f3f3f1"/>'
            f'<text x="12" y="{y + 17}" font-weight="700" fill="#333">'
            f"{_esc(GROUPS.get(g, g.replace('-', ' ').capitalize()))}</text>"
        )
        y += GROUP_H
        for r in members:
            card = cards[r["risk"]]
            net = r["kind"] == "net"
            if net and r["modelled"]:  # net cards: coloured by the sign of the expected value
                colour = COLOURS["benefit" if r["summary"]["expected_value"] < 0 else "harm"]
            else:
                colour = COLOURS["benefit" if r["kind"] == "benefit" else "harm"]
            cy = y + ROW_H / 2
            o.append(f'<a href="{_esc(r["href"])}" target="_top">')
            o.append(
                f'<text x="12" y="{cy - 3}" fill="#111" text-decoration="underline">'
                f"{_esc(_short(r['title'], 44))}</text>"
            )
            if r["modelled"]:
                s = r["summary"]
                if net:
                    sub = (
                        f"net EV {fmt_net(s['expected_value'])} · 90%: {fmt_net(s['p05'])} – "
                        f"{fmt_net(s['p95'])} · net harm in {s['share_net_harm']:.0%}"
                    )
                else:
                    sub = f"EV {fmt(s['expected_value'])} · 90%: {fmt(s['p05'])} – {fmt(s['p95'])}"
                if s["tail_dominated"]:
                    sub += " · tail-dominated"
                o.append(f'<text x="12" y="{cy + 12}" fill="#666" font-size="11">{sub}</text>')
                o.append("</a>")
                dash = ' stroke-dasharray="5,3"' if s["tail_dominated"] else ""
                o.append(
                    f'<line x1="{x(s["p05"]):.1f}" y1="{cy}" x2="{x(s["p95"]):.1f}" y2="{cy}" '
                    f'stroke="{colour}" stroke-width="3"{dash}/>'
                )
                o.append(f'<circle cx="{x(s["median"]):.1f}" cy="{cy}" r="5" fill="{colour}"/>')
                ex = x(s["expected_value"])
                o.append(
                    f'<path d="M{ex:.1f} {cy - 7} L{ex + 7:.1f} {cy} L{ex:.1f} {cy + 7} '
                    f'L{ex - 7:.1f} {cy} Z" fill="#fff" fill-opacity="0.6" stroke="{colour}" '
                    f'stroke-width="2"/>'
                )
                if s["share_zero"] >= 0.5:
                    o.append(
                        f'<text x="{zero_x + 8}" y="{cy - 9}" fill="#666" font-size="10">'
                        f"nothing happens in {s['share_zero']:.0%} of futures</text>"
                    )
                y += ROW_H
            else:
                o.append("</a>")
                reason = not_modelled_reason(card, state.counterfactual)
                lines = _wrap("Not modelled under this comparison: " + reason, 95)[:3]
                if len(_wrap("Not modelled under this comparison: " + reason, 95)) > 3:
                    lines[-1] += " …"
                for i, line in enumerate(lines):
                    o.append(
                        f'<text x="{LABEL_W + 20}" y="{cy - 4 + 14 * i}" fill="#666" '
                        f'font-size="11" '
                        f'font-style="italic"{HALO}>{_esc(line)}</text>'
                    )
                y += 2 * ROW_H

    # axis
    sides = (-1, 1) if signed else (1,)
    for sign in sides:
        a, b = x(sign * 10.0**lo), x(sign * 10.0**hi)
        o.append(f'<line x1="{a:.1f}" y1="{axis_y}" x2="{b:.1f}" y2="{axis_y}" stroke="#333"/>')
        for e in range(lo, hi + 1):
            ex = x(sign * 10.0**e)
            o.append(
                f'<line x1="{ex:.1f}" y1="{axis_y}" x2="{ex:.1f}" y2="{axis_y + 5}" '
                f'stroke="#333"/><text x="{ex:.1f}" y="{axis_y + 18}" text-anchor="middle" '
                f'fill="#333" font-size="{10 if signed else 12}">{fmt(10.0**e)}</text>'
            )
    o.append(f'<text x="{zero_x}" y="{axis_y + 16}" text-anchor="middle" fill="#333">0</text>')
    if signed:
        o.append(
            f'<text x="{(LABEL_W + 20 + MID) / 2}" y="{axis_y + 36}" text-anchor="middle" '
            f'fill="{COLOURS["benefit"]}">◀ net benefit (DALYs averted)</text>'
            f'<text x="{(MID + X1) / 2}" y="{axis_y + 36}" text-anchor="middle" '
            f'fill="{COLOURS["harm"]}">harm (DALYs lost) ▶</text>'
        )
    else:
        o.append(
            f'<text x="{(X0 + X1) / 2}" y="{axis_y + 36}" text-anchor="middle" fill="#333">'
            f"DALYs over {w0}–{w1}, global (log scale)</text>"
        )
    legend_y = axis_y + 56
    o.append(
        f'<circle cx="18" cy="{legend_y - 4}" r="5" fill="{COLOURS["harm"]}"/>'
        f'<text x="28" y="{legend_y}">harm</text>'
        f'<circle cx="78" cy="{legend_y - 4}" r="5" fill="{COLOURS["benefit"]}"/>'
        f'<text x="88" y="{legend_y}">benefit'
        + (" (net cards: by the sign of the expected value)" if signed else "")
        + "</text>"
        f'<text x="{440 if signed else 154}" y="{legend_y}" fill="#555">'
        f"{_esc(NOT_SUMMED)}</text>"
    )
    o.append(
        f'<text x="12" y="{legend_y + 18}" fill="#555" font-size="11">Baselines: GBD 2023 '
        f"risk factors, attributable DALYs per year × {w1 - w0 + 1} years; they overlap and are "
        f"not additive (D16). Source: Institute for Health Metrics and Evaluation.</text>"
    )
    if spec["mock"]:
        o.append(
            f'<text x="12" y="{legend_y + 36}" fill="#b00" font-weight="700">'
            f"INVENTED (MOCK) DATA. DO NOT QUOTE.</text>"
        )
    o.append("</svg>")
    return "\n".join(o) + "\n"


def _short(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


# ---- the browser's entry points (called from explorer.js) ---------------------------


class Explorer:
    """Holds the spec and loaded models in the browser; JS calls `update` with a query string."""

    def __init__(self, spec: dict, claims: dict, root: str):
        self.spec = spec
        ds = BrowserDataset(Path(root), spec["mock"], claims)
        self.models = {c["risk"]: engine.Model.load(ds, c["risk"]) for c in spec["cards"]}

    def update(self, query: str) -> dict:
        state, problems = decode(query, self.spec)
        rows = compute(self.models, self.spec, state)
        return view(rows, self.spec, state, problems)

    def check_defaults(self) -> list[str]:
        """Differences between this runtime's default numbers and the CLI's (should be none)."""
        out = []
        for cf in COUNTERFACTUALS:
            state = State(counterfactual=cf)
            for mine, cli in zip(
                compute(self.models, self.spec, state), canonical_rows(self.spec, cf), strict=True
            ):
                if mine["modelled"] != cli["modelled"]:
                    out.append(f"{mine['risk']} {cf}: modelled differs")
                elif mine["modelled"]:
                    a, b = mine["summary"]["expected_value"], cli["summary"]["expected_value"]
                    if not np.isclose(a, b, rtol=1e-9, atol=0):
                        out.append(f"{mine['risk']} {cf}: expected value {a!r} vs CLI {b!r}")
        return out


def view(rows: list[dict], spec: dict, state: State, problems: list[str] | None = None) -> dict:
    return {
        "query": encode(state),
        "state": state.to_dict(),
        "is_default": state.is_default,
        "is_canonical": state.is_canonical,
        "svg": forest_svg(rows, spec["baselines"], spec, state),
        "commands": whatif_commands(state, spec),
        "not_modelled": [
            {
                "risk": r["risk"],
                "title": r["title"],
                "reason": not_modelled_reason(
                    next(c for c in spec["cards"] if c["risk"] == r["risk"]), state.counterfactual
                ),
            }
            for r in rows
            if not r["modelled"]
        ],
        "problems": problems or [],
    }
