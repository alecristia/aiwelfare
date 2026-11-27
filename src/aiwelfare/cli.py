"""The `aiwelfare` command-line interface (D10).

Every command supports --json. Every output that contains a number states the
counterfactual and the settings used, and any output that touches invented data
from mock/ carries the mock banner (D13).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Annotated

import numpy as np
import typer

from . import card as cardmod
from . import data, dotplot, engine
from .dotplot import fmt, fmt_ratio

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Interrogate AI health-impact estimates (DALYs, 2026–2031).",
)
build_app = typer.Typer(no_args_is_help=True, help="Generate outputs (cards, site).")
app.add_typer(build_app, name="build")

JsonOpt = Annotated[bool, typer.Option("--json", help="Machine-readable output.")]
MockOpt = Annotated[
    bool, typer.Option("--include-mock", help="Overlay invented data from mock/ (D13).")
]
CfOpt = Annotated[
    str, typer.Option("--counterfactual", "-c", help="no-ai | frozen-2026 | open-only")
]
SeedOpt = Annotated[int, typer.Option(help="Random seed.")]
RiskArg = Annotated[str, typer.Argument(help="e.g. risk/data-centre-air-pollution")]
ComponentOpt = Annotated[
    str | None,
    typer.Option(help="Net cards (D17): one component instead of the net; see `model`."),
]

MOCK_BANNER = "⚠️  INCLUDES INVENTED (MOCK) DATA. Do not quote any figure."
DEFAULT_CF = cardmod.DEFAULT_COUNTERFACTUAL


def _emit(payload: dict, as_json: bool, text: str) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False, default=cardmod._jsonable))
    else:
        if payload.get("mock"):
            text = f"{MOCK_BANNER}\n\n{text}\n\n{MOCK_BANNER}"
        typer.echo(text)


def _fail(msg: str, as_json: bool, code: int = 1) -> None:
    _emit({"error": msg}, as_json, f"Error: {msg}")
    raise typer.Exit(code)


def _risk_id(ref: str) -> str:
    return ref.removeprefix("risk/")


def _load_model(ds, risk: str, as_json: bool) -> engine.Model:
    try:
        return engine.Model.load(ds, risk)
    except FileNotFoundError as e:
        _fail(str(e), as_json)


def _risk_mock(ds, model: engine.Model) -> bool:
    return bool(model.mock or any(c.get("mock") for c in cardmod.risk_claims(ds, model.risk)))


def _settings(cf: str, seed: int, n: int, fixed: dict | None = None) -> dict:
    return {
        "counterfactual": cf,
        "counterfactual_label": cardmod.ALL_COUNTERFACTUALS.get(cf, cf),
        "seed": seed,
        "draws": n,
        "fixed_parameters": fixed or {},
    }


def _settings_line(s: dict) -> str:
    out = f"Compared with: {s['counterfactual_label']} · seed {s['seed']} · {s['draws']:,} draws"
    if s["fixed_parameters"]:
        out += " · your settings: " + ", ".join(
            f"{k}={v}" for k, v in s["fixed_parameters"].items()
        )
    return out


def _check_component(model: engine.Model, component: str | None, as_json: bool) -> None:
    if component is not None and component not in model.components:
        known = ", ".join(model.components) or "none (not a net card)"
        _fail(f"{model.risk} has no component {component}; components: {known}", as_json)


def _summarise(model: engine.Model, cf: str, seed: int, fixed=None, component=None):
    """(draws, summary): the net (signed, D17), one component, or a single-quantity risk."""
    if component is not None:
        y, _ = model.run(cf, seed=seed, fixed=fixed, component=component)
        return y, engine.summarise(y)
    comps, _ = model.run_components(cf, seed=seed, fixed=fixed)
    return model.net(comps), engine.summarise_model(model, comps)


def _label(model: engine.Model, component: str | None) -> str:
    if component is None:
        return model.module.TITLE + (" (net: harms − benefits)" if model.is_net else "")
    role, label = model.components[component]
    return f"{model.module.TITLE}: {label} ({role}, DALYs {'averted' if role == 'benefit' else 'lost'})"


def _check_cf(model: engine.Model, cf: str, as_json: bool) -> None:
    if cf not in model.counterfactuals:
        reason = getattr(model.module, "NOT_MODELLED", {}).get(cf, "unknown counterfactual")
        _fail(f"{model.risk}: counterfactual '{cf}' is not modelled: {reason}", as_json)


# ---- data commands -------------------------------------------------------------


@app.command()
def validate(as_json: JsonOpt = False) -> None:
    """Check every source, claim and baseline against its schema and the cross-file rules."""
    problems = data.validate(include_mock=True)
    ok = not problems
    text = "All sources and claims are valid." if ok else "\n".join(problems)
    _emit({"ok": ok, "problems": problems}, as_json, text)
    raise typer.Exit(0 if ok else 1)


@app.command()
def sources(
    risk: Annotated[str | None, typer.Argument(help="e.g. risk/data-centre-air-pollution")] = None,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """List sources, optionally only those cited by one risk's claims."""
    ds = data.load(include_mock=include_mock)
    ids = sorted(ds.sources)
    if risk:
        rid = _risk_id(risk)
        ids = sorted(
            {c["source"] for c in ds.claims.values() if c["risk"] == rid and c.get("source")}
        )
    rows = [ds.sources[i] for i in ids]
    lines = [
        f"{s['id']}  [{s['type']}, {s['version']}, {s['redistribution']}]\n    {s['title']}\n"
        f"    {s['url']}"
        for s in rows
    ]
    mock = any(s.get("mock") for s in rows)
    _emit({"sources": rows, "mock": mock}, as_json, "\n".join(lines) or "No sources.")


@app.command()
def claims(
    risk: RiskArg,
    param: Annotated[
        str | None, typer.Option(help="Only claims behind this model parameter.")
    ] = None,
    quantity: Annotated[str | None, typer.Option(help="Only claims about this quantity.")] = None,
    tag: Annotated[
        str | None, typer.Option(help="Only claims with this tag (prefix match).")
    ] = None,
    evidence_type: Annotated[str | None, typer.Option()] = None,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """List the claims behind a risk."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    rows = cardmod.risk_claims(ds, rid)
    if param:
        model = _load_model(ds, rid, as_json)
        p = next((p for p in model.params if p.name == param), None)
        if p is None:
            _fail(f"{rid} has no parameter {param}; see `aiwelfare model {risk}`", as_json)
        rows = [ds.claims[c] for c in p.claims]
    if quantity:
        rows = [c for c in rows if c["quantity"] == quantity]
    if tag:
        rows = [c for c in rows if any(t.startswith(tag) for t in c.get("tags", []))]
    if evidence_type:
        rows = [c for c in rows if c["evidence_type"] == evidence_type]

    def show(c: dict) -> str:
        v = c.get("value") or {}
        val = (
            v["point"]
            if "point" in v
            else "{low}–{high} ({kind})".format(**v["interval"])
            if "interval" in v
            else v.get("quantiles", "(qualitative)")
        )
        head = f"{c['id']}  {c['quantity']} = {val} {c['units']}"
        if c["claim_type"] == "assumption":
            head = "⚠️ ASSUMPTION  " + head
        src = c.get("source") or "no source"
        loc = ", ".join(f"{k} {x}" for k, x in (c.get("locator") or {}).items())
        out = [head, f"    {src}  {loc}".rstrip()]
        if c.get("description"):
            out.append(f"    {c['description']}")
        if c.get("quote"):
            out.append(f'    "{c["quote"]}"')
        if c.get("rationale"):
            out.append(f"    rationale: {c['rationale']}")
        return "\n".join(out)

    text = "\n\n".join(show(c) for c in rows) or "No claims match."
    _emit({"risk": rid, "claims": rows, "mock": any(c.get("mock") for c in rows)}, as_json, text)


# ---- results commands ------------------------------------------------------------


@app.command()
def show(
    risk: RiskArg,
    counterfactual: CfOpt = DEFAULT_CF,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Show a risk card in the terminal."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    model = _load_model(ds, rid, as_json)
    _check_cf(model, counterfactual, as_json)
    a = cardmod.analyse(ds, rid, counterfactual, seed=seed)
    text = cardmod.render(a, cardmod.load_card_source(ds, rid))
    plot = dotplot.text_signed if model.is_net else dotplot.text
    text = text.replace(
        "![Quantile dotplot](dotplot.svg)",
        "```\n" + plot(a["summary"]["dotplot_quantiles"]) + "\n```",
    )
    for k, c in a["summary"].get("components", {}).items():
        text = text.replace(
            f"![{c['label']}](dotplot-{k}.svg)",
            f"{c['label']} ({c['role']}):\n```\n" + dotplot.text(c["dotplot_quantiles"]) + "\n```",
        )
    if as_json:
        _emit(a, True, "")
    else:
        typer.echo(text)  # the rendered card carries its own mock banners


@app.command()
def dist(
    risk: RiskArg,
    counterfactual: CfOpt = DEFAULT_CF,
    component: ComponentOpt = None,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Quantile dotplot and percentiles of a risk's distribution (net cards: the net, D17)."""
    ds = data.load(include_mock=include_mock)
    model = _load_model(ds, _risk_id(risk), as_json)
    _check_cf(model, counterfactual, as_json)
    _check_component(model, component, as_json)
    y, s = _summarise(model, counterfactual, seed, component=component)
    signed = model.is_net and component is None
    pct = {
        f"p{int(q * 100):02d}": float(np.quantile(y, q))
        for q in (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
    }
    st = _settings(counterfactual, seed, len(y))
    if signed:
        tails = s["tail_dominated_components"]
        last = (
            f"expected value: {dotplot.fmt_net(s['expected_value'])} · net harm in "
            f"{s['share_net_harm']:.0%} of futures · tail-dominated components (D11): "
            + (", ".join(tails) if tails else "none")
        )
        fv = dotplot.fmt_net
    else:
        last = (
            f"expected value: {fmt(s['expected_value'])} · nothing happens in "
            f"{s['share_zero']:.0%} of futures · top 5% give {s['top5_share_of_ev']:.0%} of the "
            "expected value" + (" (TAIL-DOMINATED, D11)" if s["tail_dominated"] else "")
        )
        fv = fmt
    text = "\n".join(
        [
            f"{_label(model, component)}: DALYs {model.module.WINDOW[0]}–{model.module.WINDOW[1]}",
            _settings_line(st),
            "",
            (dotplot.text_signed if signed else dotplot.text)(s["dotplot_quantiles"]),
            "",
            "  ".join(f"{k}: {fv(v)}" for k, v in pct.items()),
            last,
        ]
    )
    _emit(
        {
            "risk": model.risk,
            "component": component,
            "settings": st,
            "summary": s,
            "percentiles": pct,
            "mock": _risk_mock(ds, model),
        },
        as_json,
        text,
    )


@app.command()
def cruxes(
    risk: RiskArg,
    counterfactual: CfOpt = DEFAULT_CF,
    component: ComponentOpt = None,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Sensitivity analysis: which parameters drive the estimate (one at a time, 5th → 95th).

    Swings are ratios, except for the net of a net card (D17): there they are absolute
    changes in DALYs, since the net can change sign.
    """
    ds = data.load(include_mock=include_mock)
    model = _load_model(ds, _risk_id(risk), as_json)
    _check_cf(model, counterfactual, as_json)
    _check_component(model, component, as_json)
    _, s = _summarise(model, counterfactual, seed, component=component)
    rows = engine.cruxes(model, counterfactual, seed=seed, component=component)
    conf = engine.confidence(s, rows)
    st = _settings(counterfactual, seed, 20_000)
    lines = [
        _label(model, component),
        _settings_line(st),
        "",
        f"{'parameter':26s} {'swing':>8s}  {'EV low':>12s} {'EV high':>12s}  basis",
    ]
    for r in rows:
        sw = fmt(r["swing"]) if r["swing_kind"] == "absolute" else f"×{r['swing']:.2f}"
        lines.append(
            f"{r['param']:26s} {sw:>8s}  {fmt(r['ev_low']):>12s} {fmt(r['ev_high']):>12s}  "
            f"{r['basis']}"
        )
    if model.is_net and component is None:
        lines += ["", "EV in DALYs lost (negative = net benefit); swing = |EV high − EV low|."]
    lines += [
        "",
        f"confidence (D12): {conf['level']} · measured share of swing "
        f"{conf['swing_share_measured']:.0%} · expert/speculation share "
        f"{conf['swing_share_expert_or_speculation']:.0%}",
    ]
    _emit(
        {
            "risk": model.risk,
            "component": component,
            "settings": st,
            "cruxes": rows,
            "confidence": conf,
            "mock": _risk_mock(ds, model),
        },
        as_json,
        "\n".join(lines),
    )


@app.command()
def whatif(
    risk: RiskArg,
    set_: Annotated[
        list[str],
        typer.Option(
            "--set",
            help="PARAM=VALUE; repeatable. Categorical parameters take a variant name or index.",
        ),
    ],
    counterfactual: CfOpt = DEFAULT_CF,
    component: ComponentOpt = None,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Rerun a model with your own parameter values."""
    ds = data.load(include_mock=include_mock)
    model = _load_model(ds, _risk_id(risk), as_json)
    _check_cf(model, counterfactual, as_json)
    _check_component(model, component, as_json)
    params = {p.name: p for p in model.params}
    fixed: dict = {}
    for item in set_:
        if "=" not in item:
            _fail(f"--set expects PARAM=VALUE, got {item}", as_json)
        k, v = item.split("=", 1)
        if k not in params:
            _fail(f"unknown parameter {k}; known: {', '.join(params)}", as_json)
        p = params[k]
        if p.categorical:
            idx = p.categories.index(v) if v in p.categories else int(v) if v.isdigit() else None
            if idx is None or not 0 <= idx < len(p.categories):
                _fail(f"{k} takes one of: {p.categories}", as_json)
            fixed[k] = idx
        else:
            fixed[k] = float(v)
    new, n = _summarise(model, counterfactual, seed, fixed, component)
    _, b = _summarise(model, counterfactual, seed, None, component)
    signed = model.is_net and component is None
    fv = dotplot.fmt_net if signed else fmt
    st = _settings(
        counterfactual, seed, len(new), {k: set_[i].split("=", 1)[1] for i, k in enumerate(fixed)}
    )
    text = "\n".join(
        [
            _label(model, component),
            _settings_line(st),
            "",
            f"{'':16s} {'default':>14s} {'yours':>14s}",
            *[
                f"{lab:16s} {fv(b[k]):>14s} {fv(n[k]):>14s}"
                for lab, k in (
                    ("expected value", "expected_value"),
                    ("median", "median"),
                    ("5th percentile", "p05"),
                    ("95th percentile", "p95"),
                )
            ],
            "",
            (
                f"expected value moves {dotplot.fmt_net(n['expected_value'] - b['expected_value'])}"
                if signed
                else f"expected value ×{n['expected_value'] / b['expected_value']:.2g}"
            )
            if b["expected_value"]
            else "",
        ]
    )
    _emit(
        {
            "risk": model.risk,
            "component": component,
            "settings": st,
            "default": b,
            "yours": n,
            "mock": _risk_mock(ds, model),
        },
        as_json,
        text,
    )


@app.command()
def compare(
    a: Annotated[str, typer.Argument(help="risk/<id>")],
    b: Annotated[str, typer.Argument(help="risk/<id> or baseline/<id>")],
    counterfactual: CfOpt = DEFAULT_CF,
    component: ComponentOpt = None,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Compare a risk with another risk or a baseline.

    For a net card (D17) the first row is the net in DALYs lost (negative = net benefit),
    and the ratio compares sizes (|net|), or use --component for one component.
    """
    ds = data.load(include_mock=include_mock)
    ma = _load_model(ds, _risk_id(a), as_json)
    _check_cf(ma, counterfactual, as_json)
    _check_component(ma, component, as_json)
    ya, sa = _summarise(ma, counterfactual, seed, component=component)
    years = ma.module.WINDOW[1] - ma.module.WINDOW[0] + 1
    rows = [
        {
            "id": a,
            "label": _label(ma, component),
            "geography": getattr(ma.module, "GEOGRAPHY", "global"),
            **{k: sa[k] for k in ("expected_value", "median", "p05", "p95")},
        }
    ]
    mock = _risk_mock(ds, ma)
    if b.startswith("baseline/"):
        bid = b.removeprefix("baseline/")
        if bid not in ds.baselines:
            _fail(
                f"unknown baseline {bid}; known: {', '.join(ds.baselines) or 'none'}"
                + ("" if include_mock else " (mock baselines need --include-mock)"),
                as_json,
            )
        bl = ds.baselines[bid]
        v = bl["dalys_per_year"] * years
        rows.append(
            {
                "id": b,
                "label": bl["label"],
                "geography": bl["geography"],
                "expected_value": v,
                "median": v,
                "p05": None,
                "p95": None,
                "source": bl["source"],
            }
        )
        mock = mock or bool(bl.get("mock"))
    else:
        mb = _load_model(ds, _risk_id(b), as_json)
        _check_cf(mb, counterfactual, as_json)
        _, sb = _summarise(mb, counterfactual, seed)
        rows.append(
            {
                "id": b,
                "label": mb.module.TITLE,
                "geography": getattr(mb.module, "GEOGRAPHY", "global"),
                **{k: sb[k] for k in ("expected_value", "median", "p05", "p95")},
            }
        )
        mock = mock or _risk_mock(ds, mb)
    ratio = (
        abs(rows[0]["expected_value"]) / abs(rows[1]["expected_value"])
        if rows[1]["expected_value"]
        else None
    )
    st = _settings(counterfactual, seed, len(ya))
    lines = [
        f"DALYs {ma.module.WINDOW[0]}–{ma.module.WINDOW[1]} · {_settings_line(st)}",
        "",
        f"{'':44s} {'EV':>8s} {'median':>8s} {'90% interval':>16s}  geography",
    ]
    for r in rows:
        iv = f"{fmt(r['p05'])} – {fmt(r['p95'])}" if r["p05"] is not None else "(point value)"
        lines.append(
            f"{r['label'][:44]:44s} {fmt(r['expected_value']):>8s} {fmt(r['median']):>8s} "
            f"{iv:>16s}  {r['geography']}"
        )
    if ratio:
        lines += [
            "",
            f"{rows[0]['label']} is {fmt_ratio(ratio)}"
            + ("" if ratio >= 1 else " of")
            + f" {rows[1]['label']} (expected values)",
        ]
    if rows[0]["geography"] != rows[1]["geography"]:
        lines.append("note: the two rows cover different geographies.")
    _emit({"rows": rows, "ratio": ratio, "settings": st, "mock": mock}, as_json, "\n".join(lines))


@app.command()
def flip(
    a: RiskArg,
    b: RiskArg,
    counterfactual: CfOpt = DEFAULT_CF,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """What must change for the ranking of two risks to flip (one parameter at a time)."""
    ds = data.load(include_mock=include_mock)
    for r in (a, b):
        _check_cf(_load_model(ds, _risk_id(r), as_json), counterfactual, as_json)
    f = cardmod.flip(ds, _risk_id(a), _risk_id(b), counterfactual, seed=seed)
    st = _settings(counterfactual, seed, 20_000)
    lines = [
        _settings_line(st),
        "",
        f"{f['higher']} is {fmt_ratio(f['ratio'])} larger than {f['lower']} in expected value.",
    ]
    if f["single_parameter_flips"]:
        lines.append("Any one of these, at its 5th/95th-percentile value, flips the order:")
        lines += [
            f"  {x['risk']}: {x['param']} → "
            f"{fmt(x['to']) if isinstance(x['to'], float) else x['to']}  ({x['description']})"
            for x in f["single_parameter_flips"]
        ]
    else:
        lines.append(
            "No single parameter at its 5th or 95th percentile flips the order; "
            "try `whatif` with several at once."
        )
    _emit({**f, "settings": st}, as_json, "\n".join(lines))


@app.command()
def breakdown(
    risk: RiskArg,
    by: Annotated[str, typer.Option(help="Only access-mode for now.")] = "access-mode",
    counterfactual: CfOpt = DEFAULT_CF,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Break a risk down by access mode."""
    if by != "access-mode":
        _fail("only --by access-mode is supported", as_json)
    ds = data.load(include_mock=include_mock)
    model = _load_model(ds, _risk_id(risk), as_json)
    _check_cf(model, counterfactual, as_json)
    bd = engine.breakdown(model, counterfactual, seed=seed)
    st = _settings(counterfactual, seed, engine.DEFAULT_DRAWS)
    if bd is None:
        msg = getattr(model.module, "BREAKDOWN_NOT_MODELLED", "not modelled")
        _emit(
            {
                "risk": model.risk,
                "breakdown": None,
                "reason": msg,
                "settings": st,
                "mock": _risk_mock(ds, model),
            },
            as_json,
            f"Breakdown not modelled yet: {msg}",
        )
        return
    lines = [_settings_line(st), ""] + [
        f"{r['label']:44s} {r['share_of_ev']:>5.0%}   "
        f"(90% range {r['share_p05']:.0%} – {r['share_p95']:.0%})"
        for r in bd["rows"]
    ]
    _emit(
        {"risk": model.risk, "breakdown": bd, "settings": st, "mock": _risk_mock(ds, model)},
        as_json,
        "\n".join(lines),
    )


@app.command()
def model(risk: RiskArg, include_mock: MockOpt = False, as_json: JsonOpt = False) -> None:
    """Print a risk's model and its declared parameters."""
    ds = data.load(include_mock=include_mock)
    m = _load_model(ds, _risk_id(risk), as_json)
    x = m.draw(20_000)
    rows = cardmod.param_table(m, x)
    lines = [
        f"{m.path.relative_to(ds.root)}",
        "",
        (m.module.__doc__ or "").strip(),
        "",
        "Parameters (value = 90% interval as simulated):",
    ]
    for r in rows:
        lines += [
            f"  {r['param']}: {r['description']}",
            f"      value {r['value']} · basis {r['basis']} · claims {', '.join(r['claims'])}",
            f"      fit: {r['fit']}",
        ]
    lines += ["", "Counterfactuals: " + ", ".join(m.counterfactuals)]
    for cf, why in getattr(m.module, "NOT_MODELLED", {}).items():
        lines.append(f"  not modelled: {cf}: {why}")
    _emit(
        {
            "risk": m.risk,
            "path": str(m.path.relative_to(ds.root)),
            "doc": m.module.__doc__,
            "parameters": rows,
            "counterfactuals": m.counterfactuals,
            "not_modelled": getattr(m.module, "NOT_MODELLED", {}),
            "mock": _risk_mock(ds, m),
        },
        as_json,
        "\n".join(lines),
    )


# ---- prose-backed commands -------------------------------------------------------


def _all_card_sources(ds) -> list[cardmod.CardSource]:
    ids = {p.stem for p in (ds.root / "cards").glob("*.md")}
    if ds.include_mock:
        ids |= {p.stem for p in (ds.root / "mock" / "cards").glob("*.md")}
    return [cardmod.load_card_source(ds, i) for i in sorted(ids)]


def _ref_lines(refs: list[dict]) -> list[str]:
    out = []
    for r in refs:
        loc = ", ".join(f"{k} {v}" for k, v in (r.get("locator") or {}).items())
        out.append(f"      {r['source']} ({loc}) [{r['claim']}]")
        if r.get("quote"):
            out.append(f'        "{r["quote"]}"')
    return out


@app.command()
def work(
    risk: Annotated[str | None, typer.Argument(help="risk/<id>")] = None,
    kind: Annotated[
        str | None, typer.Option(help="List every risk this kind of work targets.")
    ] = None,
    refs: Annotated[bool, typer.Option("--refs", help="Include sources.")] = False,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Kinds of work that target a risk, with sources (descriptive only; no ratings)."""
    ds = data.load(include_mock=include_mock)
    if kind:
        hits = []
        for cs in _all_card_sources(ds):
            for w in cs.meta.get("kinds_of_work", []):
                if w["slug"] == kind:
                    hits.append(
                        {
                            "risk": cs.meta["id"],
                            "name": w["name"],
                            "mock": cs.mock,
                            "refs": cardmod.refs_for_tag(ds, cs.meta["id"], f"work/{kind}"),
                        }
                    )
        lines = [f"risk/{h['risk']}: {h['name']}" for h in hits] or [f"No card lists {kind}."]
        _emit(
            {"kind": kind, "risks": hits, "mock": any(h["mock"] for h in hits)},
            as_json,
            "\n".join(lines),
        )
        return
    if not risk:
        _fail("give a risk, or --kind", as_json)
    rid = _risk_id(risk)
    cs = cardmod.load_card_source(ds, rid)
    rows = [
        {**w, "refs": cardmod.refs_for_tag(ds, rid, f"work/{w['slug']}")}
        for w in cs.meta.get("kinds_of_work", [])
    ]
    lines = ["Descriptive only: no tractability ratings (out of scope, VISION.md).", ""]
    for w in rows:
        lines.append(f"{w['slug']}: {w['name']}  [close to ML: {w['close_to_ml']}; {w['where']}]")
        if refs:
            lines += _ref_lines(w["refs"]) or ["      (no source linked yet)"]
    _emit({"risk": rid, "kinds_of_work": rows, "mock": cs.mock}, as_json, "\n".join(lines))


@app.command()
def refs(
    risk: RiskArg,
    work_: Annotated[str, typer.Option("--work", help="Kind-of-work slug.")],
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Sources behind one kind of work for a risk."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    rows = cardmod.refs_for_tag(ds, rid, f"work/{work_}")
    text = "\n".join(_ref_lines(rows)).strip() or f"No source linked to {work_} for {rid} yet."
    _emit(
        {"risk": rid, "work": work_, "refs": rows, "mock": any(r["mock"] for r in rows)},
        as_json,
        text,
    )


@app.command(name="not-captured")
def not_captured(
    risk: RiskArg,
    refs: Annotated[bool, typer.Option("--refs", help="Include sources.")] = False,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Harms a risk's DALY number leaves out, with sources."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    cs = cardmod.load_card_source(ds, rid)
    rows = [
        {**nc, "refs": cardmod.refs_for_tag(ds, rid, f"not-captured/{nc['slug']}")}
        for nc in cs.meta.get("not_captured", [])
    ]
    lines = []
    for nc in rows:
        lines.append(f"{nc['slug']}: {nc['text']}")
        if refs:
            lines += _ref_lines(nc["refs"]) or ["      (no source linked)"]
    _emit({"risk": rid, "not_captured": rows, "mock": cs.mock}, as_json, "\n".join(lines))


@app.command()
def log(risk: RiskArg, include_mock: MockOpt = False, as_json: JsonOpt = False) -> None:
    """Change history of a risk, with reasons (from commit messages)."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    m = _load_model(ds, rid, as_json)
    cs = cardmod.load_card_source(ds, rid)
    rows = cardmod.changelog(ds, cardmod.input_paths(ds, m, cs, rid), limit=200)
    lines = [
        f"{r['date']}  {r['commit']}  {r['change']}" + (f"\n    {r['why']}" if r["why"] else "")
        for r in rows
    ]
    _emit(
        {"risk": rid, "log": rows, "mock": cs.mock}, as_json, "\n".join(lines) or "No history yet."
    )


# ---- build and rerun ---------------------------------------------------------------


@build_app.command("card")
def build_card(
    risk: RiskArg,
    counterfactual: CfOpt = DEFAULT_CF,
    seed: SeedOpt = engine.DEFAULT_SEED,
    include_mock: MockOpt = False,
    as_json: JsonOpt = False,
) -> None:
    """Generate a card: results/<risk>/ (real) or mock/build/<risk>/ (mock, D13)."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    _check_cf(_load_model(ds, rid, as_json), counterfactual, as_json)
    out, a = cardmod.build(ds, rid, counterfactual, seed=seed)
    rel = out.relative_to(ds.root)
    _emit(
        {
            "risk": rid,
            "output": str(rel),
            "files": ["card.md", "dotplot.svg", "card.json"],
            "mock": a["mock"],
        },
        as_json,
        f"Wrote {rel}/card.md, dotplot.svg, card.json",
    )


@build_app.command("site")
def build_site(
    out: Annotated[
        str | None, typer.Option(help="Output folder (default: site/ in the repository).")
    ] = None,
    allow_regional: Annotated[
        bool,
        typer.Option(
            "--allow-regional",
            help="Development only: also show non-global cards. Needs --out outside site/.",
        ),
    ] = False,
    as_json: JsonOpt = False,
) -> None:
    """Generate the static website: site/ (real, global cards) and site/demo/ (mock, D13)."""
    from pathlib import Path

    from . import site

    root = data.repo_root()
    try:
        res = site.build(root, Path(out).resolve() if out else None, allow_regional)
    except (ValueError, FileExistsError) as e:
        _fail(str(e), as_json)
    s, d = res["site"], res["demo"]
    lines = [
        f"Wrote {s['output']}: {len(s['cards'])} card(s) on the canonical chart"
        + (f" ({', '.join(s['cards'])})" if s["cards"] else ""),
        *[f"  not shown: {e['risk']}: {e['reason']}" for e in s["excluded"]],
        f"Wrote {d['output']}: format demo with {len(d['cards'])} card(s), invented data marked (D13)",
        "Serve locally: python -m http.server --directory " + s["output"],
    ]
    # The canonical site holds no mock data; the demo build is reported separately.
    _emit({**res, "mock": False}, as_json, "\n".join(lines))


@app.command()
def rerun(risk: RiskArg, include_mock: MockOpt = False, as_json: JsonOpt = False) -> None:
    """Reproduce every number on a card. Real risks run through `datalad run` (D1)."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    m = _load_model(ds, rid, as_json)
    cs = cardmod.load_card_source(ds, rid)
    if _risk_mock(ds, m) or cs.mock:
        # D13: mock runs do not go through datalad run; outputs are committed as a log.
        out, _ = cardmod.build(ds, rid)
        _emit(
            {"risk": rid, "output": str(out.relative_to(ds.root)), "datalad": False, "mock": True},
            as_json,
            f"Rebuilt {out.relative_to(ds.root)} (mock: not run through datalad, D13). "
            "Commit it to keep a record.",
        )
        return
    if not shutil.which("datalad"):
        _fail("datalad is not installed", as_json)
    # Inputs: the risk's model, prose and claims, the engine, and the baselines cards compare against.
    inputs = [*cardmod.input_paths(ds, m, cs, rid), "src/aiwelfare", "baselines"]
    outdir = f"results/{rid}"
    cmd = [
        "datalad",
        "run",
        "--explicit",  # save only the declared outputs; unrelated work in progress is left alone
        "-m",
        f"Rebuild card {rid}",
        *[a for p in inputs for a in ("--input", p)],
        "--output",
        outdir,
        f"uv run aiwelfare build card {rid}",  # uv: the recorded command works on any clone
    ]
    proc = subprocess.run(cmd, cwd=ds.root, capture_output=True, text=True)
    ok = proc.returncode == 0
    _emit(
        {
            "risk": rid,
            "command": cmd,
            "ok": ok,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
            "mock": False,
        },
        as_json,
        (proc.stdout + proc.stderr).strip() or ("done" if ok else "failed"),
    )
    raise typer.Exit(0 if ok else 1)


def main() -> None:  # pragma: no cover
    sys.exit(app())


if __name__ == "__main__":  # pragma: no cover
    main()
