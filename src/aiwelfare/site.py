"""The static website (VISION.md layers 2–3; D6, D8, D10, D13).

`aiwelfare build site` is the only way the site is produced. It reads:
- the CLI's results: results/<risk>/card.json (real) and mock/build/<risk>/card.json (mock);
- the hand-written card sources and the models, for groups, filters and sliders;
- baselines/ (and mock/baselines/ in the demo);
- docs/roadmap.md, for the scope cuts and the list of planned cards.

It writes two separate builds:
- site/        the canonical site: real, global cards only;
- site/demo/   the format demonstration: adds the mock cards, with the D13 banner everywhere.

Numbers on the canonical chart come from card.json, i.e. from the CLI. The explorer reruns
the same model files in the browser (Pyodide) with the same seed and draw count, so every
number it shows is what `aiwelfare whatif` prints (D10). Output is deterministic.
"""

from __future__ import annotations

import html
import json
import re
import shutil
from importlib import resources
from pathlib import Path

import numpy as np

from . import card as cardmod
from . import data, engine, explorer

PYODIDE_VERSION = "314.0.8"  # bundles NumPy 2.4.6
PYODIDE_URL = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"
PYODIDE_SRI = "sha384-0Tw0jFeRF+UzB1HbzjzDi5ZNMyMclQPHmYkEquv9V+lAj/rZBHxu1c35Uq28kDPo"
MARKER = ".generated-by-aiwelfare"
PY_PACKAGE_FILES = ("__init__.py", "engine.py", "dotplot.py", "explorer.py")  # numpy-only
CLOSE_TO_ML = {"very", "yes", True}
DEFAULT_WINDOW = (2027, 2031)  # used only when no card exists yet; models sum late 2026–2031
MOCK_BANNER = (
    "⚠️ INVENTED NUMBERS: this is a format demonstration built from mock data (D13). "
    "Do not quote any figure."
)
REGIONAL_BANNER = (
    "⚠️ DEVELOPMENT BUILD: includes cards that are not global. Not for citing or sharing."
)


# ---- which cards appear ------------------------------------------------------------


def select_cards(root: Path, demo: bool, allow_regional: bool = False) -> tuple[list, list]:
    """(included, excluded) card.json dicts. Real cards need a global estimate; mock cards
    appear only in the demo build (D13)."""
    found = [json.loads(p.read_text()) for p in sorted((root / "results").glob("*/card.json"))]
    if demo:
        found += [
            json.loads(p.read_text()) for p in sorted((root / "mock/build").glob("*/card.json"))
        ]
    included, excluded = [], []
    for c in found:
        if c["mock"] and not demo:
            excluded.append({"risk": c["risk"], "reason": "mock data: demo build only (D13)"})
        elif c["geography"] != "global" and not allow_regional:
            excluded.append(
                {"risk": c["risk"], "reason": f"not global ({c['geography']}); global only"}
            )
        else:
            included.append(c)
    return included, excluded


# ---- the explorer's spec ------------------------------------------------------------


def _slider(p: engine.Param, values: np.ndarray) -> dict:
    lo, med, hi = (float(v) for v in np.quantile(values, [0.01, 0.5, 0.99]))
    log = lo > 0 and hi / lo >= 20
    return {"min": lo, "max": hi, "median": med, "log": bool(log)}


def build_spec(ds, cards: list[dict], demo: bool, allow_regional: bool) -> dict:
    draws = {c["provenance"]["draws"] for c in cards} or {engine.DEFAULT_DRAWS}
    seeds = {c["provenance"]["seed"] for c in cards} or {engine.DEFAULT_SEED}
    windows = {tuple(c["window"]) for c in cards} or {DEFAULT_WINDOW}
    if len(draws) > 1 or len(seeds) > 1 or len(windows) > 1:
        raise ValueError(f"cards disagree on draws {draws}, seeds {seeds} or windows {windows}")
    window = windows.pop()
    years = window[1] - window[0] + 1
    out_cards = []
    for c in cards:
        model = engine.Model.load(ds, c["risk"])
        cs = cardmod.load_card_source(ds, c["risk"])
        if c["counterfactual"] != explorer.DEFAULT_COUNTERFACTUAL:
            raise ValueError(f"{c['risk']}: card.json built for {c['counterfactual']}, not default")
        x = model.draw(20_000, c["provenance"]["seed"])
        crux_order = [r["param"] for r in c["cruxes"]]
        swing = {r["param"]: r["swing"] for r in c["cruxes"]}
        shown = {r["param"]: r["value"] for r in c["params"]}
        params = []
        for p in model.params:
            if p.fixed:
                continue
            entry = {
                "name": p.name,
                "description": p.description,
                "categorical": p.categorical,
                "categories": p.categories,
                "basis": p.basis,
                "claims": p.claims,
                "distribution": shown.get(p.name, ""),
                "swing": swing.get(p.name),
            }
            if not p.categorical:
                entry.update(_slider(p, x[p.name]))
            params.append(entry)
        params.sort(key=lambda e: crux_order.index(e["name"]) if e["name"] in crux_order else 1e9)
        out_cards.append(
            {
                "risk": c["risk"],
                "title": c["title"],
                "kind": c["kind"],
                "group": cs.meta.get("group", "other"),
                "geography": c["geography"],
                "href": f"cards/{c['risk']}.html",
                "mock": c["mock"],
                "close_to_ml": any(w["close_to_ml"] in CLOSE_TO_ML for w in c["work"]),
                "counterfactuals": [k for k, v in c["by_counterfactual"].items() if v["modelled"]],
                "not_modelled": {
                    k: v["reason"] for k, v in c["by_counterfactual"].items() if not v["modelled"]
                },
                "results": {
                    k: {kk: v[kk] for kk in _SUMMARY_KEYS}
                    for k, v in c["by_counterfactual"].items()
                    if v["modelled"]
                },
                "not_captured": [{"slug": n["slug"], "text": n["text"]} for n in c["not_captured"]],
                "params": params,
                "model_path": str(model.path.relative_to(ds.root)),
            }
        )
    baselines = [
        {
            "id": b["id"],
            "label": b["label"],
            "dalys_window": b["dalys_per_year"] * years,
            "year": b["year"],
            "mock": bool(b.get("mock")),
        }
        for b in sorted(ds.baselines.values(), key=lambda b: b["id"])
    ]
    return {
        "mock": demo,
        "regional": allow_regional,
        "draws": draws.pop(),
        "seed": seeds.pop(),
        "window": list(window),
        "default_counterfactual": explorer.DEFAULT_COUNTERFACTUAL,
        "counterfactuals": explorer.COUNTERFACTUALS,
        "filters": explorer.FILTERS,
        "baselines": baselines,
        "cards": out_cards,
        "pyodide": {"url": PYODIDE_URL, "version": PYODIDE_VERSION},
    }


_SUMMARY_KEYS = (
    "expected_value",
    "median",
    "p05",
    "p95",
    "share_zero",
    "top5_share_of_ev",
    "tail_dominated",
)


def claims_for_browser(ds, spec: dict) -> dict:
    """Only what models and Model.load read (D8): values, evidence basis and type."""
    risks = {c["risk"] for c in spec["cards"]}
    return {
        k: {f: v[f] for f in ("value", "evidence_basis", "evidence_type") if f in v}
        for k, v in sorted(ds.claims.items())
        if v["risk"] in risks
    }


# ---- Markdown (the subset card.render and roadmap tables use) -----------------------


def _inline(s: str) -> str:
    codes: list[str] = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep, s)
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def markdown(text: str) -> str:
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
        elif s.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            body = "\n".join(lines[i + 1 : j])
            cls = ' class="cmd"' if body.lstrip().startswith("aiwelfare ") else ""
            out.append(f"<pre{cls}><code>{html.escape(body)}</code></pre>")
            i = j + 1
        elif s.startswith("<"):
            out.append(s)  # raw HTML from the card template: comments, <details>, <summary>
            i += 1
        elif m := re.match(r"(#{1,4}) (.*)", s):
            n = len(m.group(1))
            anchor = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append(f'<h{n} id="{anchor}">{_inline(m.group(2))}</h{n}>')
            i += 1
        elif s == "---":
            out.append("<hr>")
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(_cells(lines[i]))
                i += 1
            head, body = (
                rows[0],
                [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)],
            )
            t = ["<table>"]
            if any(head):
                t.append(
                    "<thead><tr>"
                    + "".join(f"<th>{_inline(c)}</th>" for c in head)
                    + "</tr></thead>"
                )
            t.append(
                "<tbody>"
                + "".join(
                    "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in body
                )
                + "</tbody></table>"
            )
            out.append("".join(t))
        elif s.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(buf))}</blockquote>")
        elif s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
        else:
            buf = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"(```|<|#{1,4} |---$|\||> |- )", lines[i].strip())
            ):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{_inline(' '.join(buf))}</p>")
    return "\n".join(out)


def roadmap_table(root: Path, heading: str) -> list[dict]:
    """The first Markdown table under a heading of docs/roadmap.md, as dicts."""
    text = (root / "docs/roadmap.md").read_text()
    m = re.search(rf"^#+ {re.escape(heading)}\s*$", text, re.M)
    if not m:
        raise ValueError(f"docs/roadmap.md has no heading {heading!r}")
    rows = []
    for line in text[m.end() :].splitlines():
        if line.startswith("|"):
            rows.append(_cells(line))
        elif rows:
            break
    head = rows[0]
    return [
        dict(zip(head, r, strict=False))
        for r in rows[1:]
        if not all(re.fullmatch(r":?-+:?", c) for c in r)
    ]


# ---- pages -----------------------------------------------------------------------


def _page(title: str, body: str, spec: dict, depth: int, scripts: str = "") -> str:
    up = "../" * depth
    banners = ""
    if spec["mock"]:
        banners += f'<div class="banner mock">{html.escape(MOCK_BANNER)}</div>'
    if spec["regional"]:
        banners += f'<div class="banner mock">{html.escape(REGIONAL_BANNER)}</div>'
    nav = (
        f'<nav><a href="{up}index.html">Overview</a>'
        + (
            f' · <a href="{up}../index.html">Canonical site (real data)</a>'
            if spec["mock"]
            else f' · <a href="{up}demo/index.html">Format demo (invented data)</a>'
        )
        + "</nav>"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}{" (INVENTED DATA)" if spec["mock"] else ""}</title>
<link rel="stylesheet" href="{up}assets/style.css">
<!-- GENERATED by `aiwelfare build site`. Do not edit: change the data, then rebuild. -->
</head>
<body{' class="mock"' if spec["mock"] else ""}>
{f'<div class="banners top">{banners}</div>' if banners else ""}
<header>{nav}</header>
<main>
{body}
</main>
<footer>
<p>Generated by <code>aiwelfare build site</code> from the repository's claims, models and results.
Every number here can be reproduced with the <code>aiwelfare</code> CLI (D10).
Baselines: Source: Institute for Health Metrics and Evaluation.</p>
</footer>
{f'<div class="banners">{banners}</div>' if banners else ""}
{scripts}
</body>
</html>
"""


def _table(rows: list[dict], cols: list[str]) -> str:
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = "".join(
        "<tr>" + "".join(f"<td>{_inline(r.get(c, ''))}</td>" for c in cols) + "</tr>" for r in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def index_page(root: Path, spec: dict, excluded: list[dict]) -> str:
    cf = spec["default_counterfactual"]
    default = explorer.State()
    svg = explorer.forest_svg(explorer.canonical_rows(spec, cf), spec["baselines"], spec, default)
    cf_radios = "".join(
        f'<label><input type="radio" name="cf" value="{k}"{" checked" if k == cf else ""} disabled> '
        f"{html.escape(v)}</label>"
        for k, v in spec["counterfactuals"].items()
    )
    filters = "".join(
        f'<label><input type="checkbox" name="filter" value="{k}" disabled> {html.escape(v)}</label>'
        for k, v in spec["filters"].items()
    )
    not_captured = (
        "".join(
            f"<li><strong>{html.escape(c['title'])}</strong>: "
            + " · ".join(html.escape(n["text"]) for n in c["not_captured"])
            + f' (<a href="{c["href"]}#what-this-number-leaves-out">card</a>)</li>'
            for c in spec["cards"]
        )
        or "<li>No card exists yet; each card lists what its number leaves out.</li>"
    )
    cuts = roadmap_table(root, "Not covered: scope cuts")
    planned = roadmap_table(root, "The cards")
    group = ""
    for r in planned:  # the roadmap leaves the group cell blank under its first row
        group = r["Group (D7)"] or group
        r["Group (D7)"] = group
    cards_on_site = {c["risk"] for c in spec["cards"]}
    commands = "\n".join(explorer.whatif_commands(default, spec)) or "aiwelfare --help"
    mock_note = (
        '<p class="mock-note">Rows marked MOCK are invented. The demo exists to show the format '
        "and the explorer working; it shows nothing about AI's real health impact.</p>"
        if spec["mock"]
        else ""
    )
    excluded_note = ""
    if excluded and not spec["mock"]:
        excluded_note = (
            "<p class='small'>Built but not shown: "
            + "; ".join(f"{html.escape(e['risk'])} ({html.escape(e['reason'])})" for e in excluded)
            + ".</p>"
        )
    body = f"""
<h1>The health impact of AI, 2026–2031, card by card</h1>
<p class="lede">Global DALYs that each AI pathway may cause or avert over the next five years, with
uncertainty, against the burden of familiar health risks. Every number traces to its sources;
each row opens a card that shows what it rests on. This repository rates scale only, not how
tractable or neglected the work is.</p>
{mock_note}
<section id="explorer">
<div class="controls">
  <fieldset><legend>Compared with (counterfactual)</legend>{cf_radios}</fieldset>
  <fieldset><legend>Filters</legend>{filters}</fieldset>
  <p><a class="reset" href="index.html">Canonical default chart</a></p>
</div>
<div id="settings-banner" class="banner settings" hidden></div>
<div id="status" class="status">Showing the canonical default chart. The explorer is loading
Python in your browser (about 10&nbsp;MB, once).</div>
<figure id="chart">{svg}</figure>
<p class="not-summed">{html.escape(explorer.NOT_SUMMED)}</p>
<div id="not-modelled"></div>
<details class="reproduce" open>
<summary>Reproduce this chart with the CLI</summary>
<pre class="cmd"><code id="commands">{html.escape(commands)}</code></pre>
<p class="small">The explorer runs the repository's own model files in your browser (Pyodide
{PYODIDE_VERSION}), with the CLI's seed ({spec["seed"]}) and draw count ({spec["draws"]:,}),
so it shows the same numbers as these commands. The default chart above is drawn from the CLI's
results. Every setting is in the page address.</p>
</details>
<div id="sliders" class="sliders"></div>
</section>

<section id="not-covered">
<h2>Not covered: scope cuts</h2>
<p>These pathways have no card. They are not estimated here, so they are not on the chart.</p>
{_table(cuts, list(cuts[0].keys()))}
</section>

<section id="not-captured">
<h2>Not captured in DALYs</h2>
<p>Harms that fall inside a card but that its DALY number leaves out.</p>
<ul>{not_captured}</ul>
</section>

<section id="planned">
<h2>The cards</h2>
<p>Nine cards are planned (docs/roadmap.md). {len(cards_on_site)} {"is" if len(cards_on_site) == 1 else "are"} on this chart.</p>
{_table(planned, ["Group (D7)", "Card", "Components", "Status"])}
{excluded_note}
</section>
"""
    scripts = (
        f'<script src="{PYODIDE_URL}pyodide.js" integrity="{PYODIDE_SRI}" '
        'crossorigin="anonymous" defer></script>\n'
        '<script src="assets/explorer.js" defer></script>'
    )
    return _page("AI and health: overview", body, spec, 0, scripts)


def card_page(root: Path, c: dict, spec: dict, src_dir: Path) -> str:
    md = (src_dir / "card.md").read_text()
    md = md.replace(
        "![Quantile dotplot](dotplot.svg)", f"![Quantile dotplot]({c['risk']}-dotplot.svg)"
    )
    body = markdown(md)
    w0, w1 = c["window"]
    body = (
        f'<p class="small">Card built by <code>aiwelfare build card risk/{c["risk"]}</code>; '
        f"DALYs {w0}–{w1}, compared with {html.escape(c['counterfactual_label'])}. "
        f'Switch the comparison or change assumptions on the <a href="../index.html">overview</a>.</p>\n'
        + body
    )
    return _page(c["title"], f'<article class="card">{body}</article>', spec, 1)


# ---- build ---------------------------------------------------------------------------


def _clean(out: Path) -> None:
    if out.exists():
        if not (out / MARKER).exists() and any(out.iterdir()):
            raise FileExistsError(
                f"{out} exists and was not generated by aiwelfare; not touching it"
            )
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARKER).write_text("Generated by `aiwelfare build site`. Never edit by hand.\n")


def _write_assets(out: Path) -> None:
    (out / "assets").mkdir()
    for name in ("style.css", "explorer.js"):
        text = resources.files("aiwelfare.site_assets").joinpath(name).read_text()
        (out / "assets" / name).write_text(text)


def _write_python(ds, out: Path, spec: dict) -> list[str]:
    files = []
    pkg = resources.files("aiwelfare")
    for name in PY_PACKAGE_FILES:
        dest = out / "py/aiwelfare" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(pkg.joinpath(name).read_text())
        files.append(f"aiwelfare/{name}")
    for c in spec["cards"]:
        dest = out / "py" / c["model_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text((ds.root / c["model_path"]).read_text())
        files.append(c["model_path"])
    return files


def build_one(root: Path, out: Path, demo: bool, allow_regional: bool = False) -> dict:
    ds = data.load(root, include_mock=demo)
    cards, excluded = select_cards(root, demo, allow_regional)
    spec = build_spec(ds, cards, demo, allow_regional)
    _clean(out)
    _write_assets(out)
    spec["py_files"] = _write_python(ds, out, spec)
    (out / "data").mkdir()
    (out / "data/spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    (out / "data/claims.json").write_text(
        json.dumps(claims_for_browser(ds, spec), indent=1, ensure_ascii=False) + "\n"
    )
    (out / "index.html").write_text(index_page(root, spec, excluded))
    (out / "cards").mkdir()
    for c in cards:
        src_dir = cardmod.output_dir(ds, c["risk"], c["mock"])
        shutil.copyfile(src_dir / "dotplot.svg", out / "cards" / f"{c['risk']}-dotplot.svg")
        (out / "cards" / f"{c['risk']}.html").write_text(card_page(root, c, spec, src_dir))
    for cf in explorer.COUNTERFACTUALS:  # the canonical charts, one per comparison, for citing
        svg = explorer.forest_svg(
            explorer.canonical_rows(spec, cf), spec["baselines"], spec, explorer.State(cf)
        )
        (out / f"overview-{cf}.svg").write_text(svg)
    return {
        "output": str(out),
        "cards": [c["risk"] for c in cards],
        "excluded": excluded,
        "mock": demo,
        "regional": allow_regional,
    }


def build(root: Path, out: Path | None = None, allow_regional: bool = False) -> dict:
    """site/ (real, global cards) and site/demo/ (adds mock cards, D13)."""
    out = out or root / "site"
    if allow_regional and out.resolve() == (root / "site").resolve():
        raise ValueError("a build with non-global cards must go elsewhere than site/ (use --out)")
    real = build_one(root, out, demo=False, allow_regional=allow_regional)
    demo = build_one(root, out / "demo", demo=True, allow_regional=allow_regional)
    return {"site": real, "demo": demo, "counterfactual_default": explorer.DEFAULT_COUNTERFACTUAL}
