"""The `aiwelfare` command-line interface (D10).

Every command supports --json. Commands not yet implemented exit with code 2
and say so, in text or JSON.
"""

from __future__ import annotations

import json
import sys
from typing import Annotated

import typer

from . import data

app = typer.Typer(no_args_is_help=True, add_completion=False,
                  help="Interrogate AI health-impact estimates (DALYs, 2026–2031).")

JsonOpt = Annotated[bool, typer.Option("--json", help="Machine-readable output.")]
MockOpt = Annotated[bool, typer.Option("--include-mock",
                                       help="Overlay invented data from mock/ (D13).")]

MOCK_BANNER = "⚠️  INCLUDES INVENTED (MOCK) DATA. Do not quote any figure."


def _emit(payload: dict, as_json: bool, text: str) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        typer.echo(text)


def _risk_id(ref: str) -> str:
    return ref.removeprefix("risk/")


@app.command()
def validate(as_json: JsonOpt = False) -> None:
    """Check every source and claim against its schema and the cross-file rules."""
    problems = data.validate(include_mock=True)
    ok = not problems
    text = "All sources and claims are valid." if ok else "\n".join(problems)
    _emit({"ok": ok, "problems": problems}, as_json, text)
    raise typer.Exit(0 if ok else 1)


@app.command()
def sources(risk: Annotated[str | None, typer.Argument(help="e.g. risk/data-centre-air-pollution")] = None,
            include_mock: MockOpt = False, as_json: JsonOpt = False) -> None:
    """List sources, optionally only those cited by one risk's claims."""
    ds = data.load(include_mock=include_mock)
    ids = sorted(ds.sources)
    if risk:
        rid = _risk_id(risk)
        ids = sorted({c["source"] for c in ds.claims.values() if c["risk"] == rid and c.get("source")})
    rows = [ds.sources[i] for i in ids]
    lines = [f"{s['id']}  [{s['type']}, {s['version']}]\n    {s['title']}\n    {s['url']}" for s in rows]
    if ds.touches_mock:
        lines.insert(0, MOCK_BANNER)
    _emit({"sources": rows, "mock": ds.touches_mock}, as_json, "\n".join(lines) or "No sources.")


@app.command()
def claims(risk: Annotated[str, typer.Argument(help="e.g. risk/data-centre-air-pollution")],
           quantity: Annotated[str | None, typer.Option(help="Only claims about this quantity.")] = None,
           tag: Annotated[str | None, typer.Option(help="Only claims with this tag (prefix match).")] = None,
           evidence_type: Annotated[str | None, typer.Option()] = None,
           include_mock: MockOpt = False, as_json: JsonOpt = False) -> None:
    """List the sourced claims behind a risk."""
    ds = data.load(include_mock=include_mock)
    rid = _risk_id(risk)
    rows = [c for c in ds.claims.values() if c["risk"] == rid]
    if quantity:
        rows = [c for c in rows if c["quantity"] == quantity]
    if tag:
        rows = [c for c in rows if any(t.startswith(tag) for t in c.get("tags", []))]
    if evidence_type:
        rows = [c for c in rows if c["evidence_type"] == evidence_type]

    def fmt(c: dict) -> str:
        v = c.get("value", {})
        val = (v.get("point") if "point" in v else
               "{low}–{high} ({kind})".format(**v["interval"]) if "interval" in v else v)
        head = f"{c['id']}  {c['quantity']} = {val} {c['units']}"
        src = c.get("source") or "ASSUMPTION (no source)"
        loc = ", ".join(f"{k} {x}" for k, x in c.get("locator", {}).items())
        out = [head, f"    {src}  {loc}"]
        if c.get("quote"):
            out.append(f'    "{c["quote"]}"')
        if c.get("rationale"):
            out.append(f"    rationale: {c['rationale']}")
        return "\n".join(out)

    text = "\n".join(fmt(c) for c in rows) or "No claims match."
    if ds.touches_mock:
        text = MOCK_BANNER + "\n" + text
    _emit({"risk": rid, "claims": rows, "mock": ds.touches_mock}, as_json, text)


def _not_yet(name: str, as_json: bool) -> None:
    msg = f"`aiwelfare {name}` is not implemented yet (milestone 1 in progress)."
    _emit({"error": "not-implemented", "command": name, "message": msg}, as_json, msg)
    raise typer.Exit(2)


def _stub(name: str, doc: str):
    def cmd(args: Annotated[list[str] | None, typer.Argument()] = None,
            as_json: JsonOpt = False) -> None:
        _not_yet(name, as_json)
    cmd.__doc__ = doc + " [not implemented yet]"
    app.command(name=name, context_settings={"allow_extra_args": True,
                                             "ignore_unknown_options": True})(cmd)


for _name, _doc in {
    "show": "Show a risk card in the terminal.",
    "dist": "Quantile dotplot and percentiles of a risk's distribution.",
    "compare": "Compare a risk with another risk or a baseline.",
    "cruxes": "Sensitivity analysis: which parameters drive the estimate.",
    "whatif": "Rerun a model with your own parameter values.",
    "flip": "What must change for the ranking of two risks to flip.",
    "breakdown": "Break a risk down by access mode.",
    "work": "Kinds of work that target a risk, with sources.",
    "refs": "Sources behind one kind of work for a risk.",
    "not-captured": "Harms a risk's DALY number leaves out, with sources.",
    "model": "Print a risk's model and its declared parameters.",
    "rerun": "Reproduce every number on a card (via datalad run).",
    "log": "Change history of a risk, with reasons.",
}.items():
    _stub(_name, _doc)


def main() -> None:  # pragma: no cover
    sys.exit(app())
