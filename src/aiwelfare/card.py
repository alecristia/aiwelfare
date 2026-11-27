"""Risk cards (D4): analysis as data, then rendering to Markdown + a dotplot SVG.

`analyse()` computes everything a card shows and returns plain data, so the CLI's
--json output and the card always agree (D10). `render()` turns it into Markdown,
merging the hand-written prose from cards/<risk>.md. Cards are never hand-edited.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from . import dotplot, engine
from .dotplot import fmt

DEFAULT_COUNTERFACTUAL = "frozen-2026"
ALL_COUNTERFACTUALS = {
    "no-ai": "No modern AI",
    "frozen-2026": "AI frozen at 2026 levels",
    "open-only": "Only open-weight / older models advance",
}
MOCK_TOP = (
    "> ⚠️ **INVENTED NUMBERS: THIS CARD USES MOCK DATA.** It shows the format only. "
    "Do not quote any figure."
)
MOCK_BOTTOM = "> ⚠️ **INVENTED NUMBERS: THIS CARD USES MOCK DATA.**"
CLOSE_TO_ML = {
    "very": "✅ Very",
    "yes": "✅ Yes",
    "partly": "➖ Partly",
    "no": "❌ No",
    True: "✅ Yes",
    False: "❌ No",
}  # YAML reads bare yes/no as booleans
CONFIDENCE_ICON = {"low": "🔺 **Low**", "medium": "🔸 **Medium**", "high": "🟢 **High**"}


# ---- card source (hand-written prose) ------------------------------------------


@dataclass
class CardSource:
    meta: dict
    sections: dict[str, str]
    path: Path
    mock: bool


def load_card_source(ds, risk: str) -> CardSource:
    candidates = [(ds.root / "cards" / f"{risk}.md", False)]
    if ds.include_mock:
        candidates.insert(0, (ds.root / "mock" / "cards" / f"{risk}.md", True))
    for path, is_mock in candidates:
        if path.exists():
            text = path.read_text()
            _, front, body = text.split("---\n", 2)
            sections: dict[str, str] = {}
            current = None
            for line in body.splitlines():
                if line.startswith("## "):
                    current = line[3:].strip()
                    sections[current] = ""
                elif current:
                    sections[current] += line + "\n"
            return CardSource(
                yaml.safe_load(front), {k: v.strip() for k, v in sections.items()}, path, is_mock
            )
    raise FileNotFoundError(f"no card source for {risk}")


# ---- helpers -------------------------------------------------------------------


def _git(ds, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ds.root, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def risk_claims(ds, risk: str) -> list[dict]:
    return [c for c in ds.claims.values() if c["risk"] == risk]


def input_paths(ds, model, cs: CardSource, risk: str) -> list[str]:
    claims_dir = ("mock/" if cs.mock else "") + f"claims/{risk}"
    return [str(model.path.relative_to(ds.root)), str(cs.path.relative_to(ds.root)), claims_dir]


def changelog(ds, paths: list[str], limit: int = 10) -> list[dict]:
    out = _git(
        ds, "log", f"-{limit}", "--date=short", "--format=%h%x1f%ad%x1f%s%x1f%b%x1e", "--", *paths
    )
    rows = []
    for rec in out.split("\x1e"):
        parts = rec.strip().split("\x1f")
        if len(parts) >= 3:
            why = parts[3].strip().split("\n\n")[0].replace("\n", " ") if len(parts) > 3 else ""
            rows.append({"commit": parts[0], "date": parts[1], "change": parts[2], "why": why})
    return rows


def refs_for_tag(ds, risk: str, tag: str) -> list[dict]:
    rows = []
    for c in risk_claims(ds, risk):
        if tag in c.get("tags", []):
            src = ds.sources.get(c.get("source") or "", {})
            rows.append(
                {
                    "claim": c["id"],
                    "source": c.get("source"),
                    "locator": c.get("locator"),
                    "quote": c.get("quote"),
                    "source_title": src.get("title"),
                    "mock": bool(c.get("mock")),
                }
            )
    return rows


def _group_refs(refs: list[dict]) -> str:
    """`source` (p. 2, 10), one entry per source."""
    by: dict[str, set] = {}
    for r in refs:
        loc = r.get("locator") or {}
        where = (
            f"p. {loc['page']}" if "page" in loc else loc.get("section") or loc.get("table") or ""
        )
        by.setdefault(r["source"], set()).add(where)
    return ", ".join(
        f"`{s}`" + (f" ({', '.join(sorted(w for w in ws if w))})" if any(ws) else "")
        for s, ws in sorted(by.items())
    )


def param_table(model, x: dict[str, np.ndarray]) -> list[dict]:
    rows = []
    for p in model.params:
        v = x[p.name]
        if p.fixed:
            shown = fmt(float(v[0]))
        elif p.categorical:
            shown = " · ".join(p.categories) + " (equal weight)"
        else:
            lo, hi = np.quantile(v, [0.05, 0.95])
            shown = f"{fmt(lo)} – {fmt(hi)}"
        rows.append(
            {
                "param": p.name,
                "description": p.description,
                "value": shown,
                "fixed": p.fixed,
                "categorical": p.categorical,
                "basis": p.basis,
                "evidence_types": p.evidence_types,
                "claims": p.claims,
                "fit": p.fit,
            }
        )
    return rows


# ---- analysis ------------------------------------------------------------------


def analyse(
    ds,
    risk: str,
    counterfactual: str = DEFAULT_COUNTERFACTUAL,
    n: int = engine.DEFAULT_DRAWS,
    seed: int = engine.DEFAULT_SEED,
    with_changelog: bool = True,
) -> dict:
    model = engine.Model.load(ds, risk)
    cs = load_card_source(ds, risk)
    mod = model.module
    if counterfactual not in model.counterfactuals:
        raise ValueError(
            f"{risk}: counterfactual '{counterfactual}' is not modelled: "
            f"{getattr(mod, 'NOT_MODELLED', {}).get(counterfactual, 'unknown')}"
        )
    claims = risk_claims(ds, risk)
    by_cf = {}
    for cf, label in ALL_COUNTERFACTUALS.items():
        if cf in model.counterfactuals:
            y, _ = model.run(cf, n, seed)
            by_cf[cf] = {"label": label, "modelled": True, **engine.summarise(y)}
        else:
            by_cf[cf] = {
                "label": label,
                "modelled": False,
                "reason": getattr(mod, "NOT_MODELLED", {}).get(cf, ""),
            }
    y, x = model.run(counterfactual, n, seed)
    summary = engine.summarise(y)
    crux_rows = engine.cruxes(model, counterfactual, seed=seed)
    conf = engine.confidence(summary, crux_rows)
    years = mod.WINDOW[1] - mod.WINDOW[0] + 1

    baselines = []
    for b in ds.baselines.values():
        total = b["dalys_per_year"] * years
        baselines.append(
            {
                "id": b["id"],
                "label": b["label"],
                "geography": b["geography"],
                "dalys_window": total,
                "ratio": summary["expected_value"] / total,
                "source": b["source"],
                "mock": bool(b.get("mock")),
            }
        )

    used_sources = sorted({c["source"] for c in claims if c.get("source")})
    mock = bool(
        model.mock
        or cs.mock
        or any(c.get("mock") for c in claims)
        or any(b["mock"] for b in baselines)
        or any(ds.sources[s].get("mock") for s in used_sources)
    )

    work = []
    for w in cs.meta.get("kinds_of_work", []):
        work.append({**w, "refs": refs_for_tag(ds, risk, f"work/{w['slug']}")})
    not_captured = []
    for nc in cs.meta.get("not_captured", []):
        not_captured.append({**nc, "refs": refs_for_tag(ds, risk, f"not-captured/{nc['slug']}")})

    evidence = {}
    for c in claims:
        if c["claim_type"] == "qualitative":
            continue
        e = evidence.setdefault(
            c["evidence_type"], {"claims": [], "sources": set(), "basis": set()}
        )
        e["claims"].append(c["id"])
        if c.get("source"):
            e["sources"].add(c["source"])
        e["basis"].add(c["evidence_basis"])
    evidence = {
        k: {"claims": v["claims"], "sources": sorted(v["sources"]), "basis": sorted(v["basis"])}
        for k, v in sorted(evidence.items())
    }

    extras = {}
    if hasattr(mod, "deaths"):
        d = mod.deaths(x, counterfactual)
        extras["deaths"] = {
            "expected_value": float(d.mean()),
            "p05": float(np.quantile(d, 0.05)),
            "p95": float(np.quantile(d, 0.95)),
        }

    neighbour = cs.meta.get("neighbour_for_flip")
    flip_result = None
    if neighbour:
        try:
            flip_result = flip(ds, risk, neighbour, counterfactual, seed=seed)
        except (FileNotFoundError, ValueError) as e:
            flip_result = {"error": str(e)}

    paths = input_paths(ds, model, cs, risk)
    # The last commit that changed any input (not HEAD), so `datalad rerun` reproduces the card.
    commit = _git(ds, "log", "-1", "--format=%h", "--", *paths, "src/aiwelfare")
    dirty = bool(_git(ds, "status", "--porcelain", "--", *paths))

    return {
        "risk": risk,
        "title": cs.meta.get("title", mod.TITLE),
        "kind": cs.meta.get("kind", "risk"),
        "one_line": cs.meta.get("one_line", ""),
        "scope_note": cs.meta.get("scope_note", ""),
        "geography": getattr(mod, "GEOGRAPHY", "global"),
        "window": list(mod.WINDOW),
        "counterfactual": counterfactual,
        "counterfactual_label": ALL_COUNTERFACTUALS[counterfactual],
        "summary": summary,
        "confidence": conf,
        "by_counterfactual": by_cf,
        "cruxes": crux_rows,
        "variants": engine.variants(model, counterfactual, n, seed),
        "breakdown": engine.breakdown(model, counterfactual, n, seed),
        "breakdown_not_modelled": getattr(mod, "BREAKDOWN_NOT_MODELLED", ""),
        "baselines": baselines,
        "params": param_table(model, x),
        "evidence": evidence,
        "assumptions": [
            {
                "claim": c["id"],
                "description": c.get("description", ""),
                "rationale": c.get("rationale", ""),
                "replace_with": c.get("replace_with", ""),
            }
            for c in claims
            if c["claim_type"] == "assumption"
        ],
        "work": work,
        "not_captured": not_captured,
        "flip": flip_result,
        "neighbour": neighbour,
        "extras": extras,
        "limitations": cs.meta.get("limitations", []),
        "index_entries": cs.meta.get("index_entries", []),
        "sources": used_sources,
        "provenance": {
            "model": str(model.path.relative_to(ds.root)),
            "card_source": str(cs.path.relative_to(ds.root)),
            "commit": commit,
            "uncommitted_input_changes": dirty,
            "seed": seed,
            "draws": n,
        },
        "changelog": changelog(ds, paths) if with_changelog else [],
        "mock": mock,
    }


def flip(
    ds,
    a: str,
    b: str,
    counterfactual: str = DEFAULT_COUNTERFACTUAL,
    seed: int = engine.DEFAULT_SEED,
    n: int = 20_000,
) -> dict:
    """Which single parameter, moved to its 5th or 95th percentile, flips the EV ranking."""
    models = {r: engine.Model.load(ds, r) for r in (a, b)}
    ev = {r: float(m.run(counterfactual, n, seed)[0].mean()) for r, m in models.items()}
    hi_r, lo_r = (a, b) if ev[a] >= ev[b] else (b, a)
    flips = []
    for r, m in models.items():
        for c in engine.cruxes(m, counterfactual, n=n, seed=seed):
            # lowering the higher risk, or raising the lower one
            new = c["ev_low"] if r == hi_r else c["ev_high"]
            other = ev[lo_r] if r == hi_r else ev[hi_r]
            if (r == hi_r and new < other) or (r == lo_r and new > other):
                side = "low" if r == hi_r else "high"
                flips.append(
                    {
                        "risk": r,
                        "param": c["param"],
                        "description": c["description"],
                        "to": c["settings"][side],
                        "ev_after": new,
                    }
                )
    mock = any(
        m.mock or any(cl.get("mock") for cl in risk_claims(ds, r)) for r, m in models.items()
    )
    return {
        "counterfactual": counterfactual,
        "expected_values": ev,
        "higher": hi_r,
        "lower": lo_r,
        "ratio": ev[hi_r] / ev[lo_r] if ev[lo_r] > 0 else float("inf"),
        "single_parameter_flips": flips,
        "mock": mock,
    }


# ---- rendering -----------------------------------------------------------------


def _cmd(s: str, mock: bool) -> str:
    return s + (" --include-mock" if mock and s.startswith("aiwelfare ") else "")


def _commands(lines: list[tuple[str, str]], mock: bool) -> str:
    w = max(len(_cmd(c, mock)) for c, _ in lines) + 2
    body = "\n".join(f"{_cmd(c, mock):<{w}}# {why}" for c, why in lines)
    return f"```\n{body}\n```"


def _crux_rows(a: dict, cs: CardSource) -> list[str]:
    ev = a["summary"]["expected_value"]
    texts = cs.meta.get("cruxes", {})
    params = {p["param"]: p for p in a["params"]}
    rows = []
    for c in a["cruxes"][:3]:
        t = texts.get(c["param"], {})
        if params[c["param"]]["categorical"]:
            hi_txt = f"the **{c['settings']['high']}** estimate is the right one"
            lo_txt = f"the **{c['settings']['low']}** estimate is the right one"
        else:
            hi_txt = t.get(
                "high", f"{c['description']} is at the **high** end ({fmt(c['settings']['high'])})"
            )
            lo_txt = t.get(
                "low", f"{c['description']} is at the **low** end ({fmt(c['settings']['low'])})"
            )
        hi_ev, lo_ev = max(c["ev_low"], c["ev_high"]), min(c["ev_low"], c["ev_high"])
        rows.append(f"| {hi_txt[0].upper() + hi_txt[1:]} | ⬆ ×{hi_ev / ev:.2g} |")
        rows.append(f"| {lo_txt[0].upper() + lo_txt[1:]} | ⬇ ×{lo_ev / ev:.2g} |")
    return rows


def render(a: dict, cs: CardSource) -> str:
    s, rid, mock = a["summary"], a["risk"], a["mock"]
    w0, w1 = a["window"]
    ref = f"risk/{rid}"
    L: list[str] = []
    if mock:
        L += [MOCK_TOP, ""]
    L += [
        f"<!-- GENERATED by `aiwelfare build card {rid}`. Do not edit: change "
        f"{a['provenance']['card_source']}, the model or the claims, then rebuild. -->",
        "",
    ]
    L += [f"# {a['title']}", "", f"**In one line:** {a['one_line']}", ""]
    if a["scope_note"]:
        L += [f"*Scope: {a['scope_note']}*", ""]

    # 1. Header box
    harm = "Expected harm" if a["kind"] == "risk" else "Expected benefit"
    oom = int(np.floor(np.log10(s["expected_value"]))) if s["expected_value"] > 0 else 0
    if a["baselines"]:
        ratios = " · ".join(
            f"{b['ratio']:.2g}× {b['label']}"
            + (f" ({b['geography']})" if b["geography"] != a["geography"] else "")
            for b in a["baselines"]
        )
    else:
        ratios = "no sourced baselines yet"
    mag = f"order of 10^{oom} DALYs · {ratios}" if s["expected_value"] > 0 else "zero"
    conf = a["confidence"]
    conf_txt = CONFIDENCE_ICON[conf["level"]]
    conf_txt += (
        f". Tail-dominated: the top 5% of futures give {conf['top5_share_of_ev']:.0%} "
        "of the expected value"
        if conf["tail_dominated"]
        else f". Not tail-dominated (top 5% of futures give {conf['top5_share_of_ev']:.0%} "
        "of the expected value)"
    )
    if a["breakdown"]:
        comes = " · ".join(f"{r['label']} ({r['share_of_ev']:.0%})" for r in a["breakdown"]["rows"])
    else:
        comes = "not modelled yet"
    L += [
        "| | |",
        "|---|---|",
        f"| **{harm}, {w0}–{w1}** | **~{fmt(s['expected_value'])} DALYs** "
        f"(90% range: {fmt(s['p05'])} → {fmt(s['p95'])}) |",
        f"| **Magnitude** | {mag} |",
        f"| **Confidence** | {conf_txt} |",
        f"| **Mainly comes from** | {comes} |",
        f"| **Compared with** | {a['counterfactual_label']} |",
        "",
    ]
    other = [
        cf
        for cf, v in a["by_counterfactual"].items()
        if v["modelled"] and cf != a["counterfactual"]
    ]
    lines = [
        (f"aiwelfare show {ref} --counterfactual {cf}", "same card, different comparison")
        for cf in other
    ]
    if lines:
        L += [_commands(lines, mock), ""]
    L += ["---", ""]

    # 2. Is this big?
    L += ["## Is this big?", ""]
    if cs.sections.get("Is this big?"):
        L += [cs.sections["Is this big?"], ""]
    gen = (
        f"In the model, the median future has **{fmt(s['median'])} DALYs** over {w0}–{w1}, "
        f"and 90% of simulated futures fall between {fmt(s['p05'])} and {fmt(s['p95'])}."
    )
    if s["share_zero"] > 0:
        gen += f" In {s['share_zero']:.0%} of futures nothing happens."
    if "deaths" in a["extras"]:
        d = a["extras"]["deaths"]
        gen += (
            f" That is about **{fmt(d['expected_value'])} premature deaths** in expectation "
            f"({fmt(d['p05'])} → {fmt(d['p95'])})."
        )
    L += [gen, "", "![Quantile dotplot](dotplot.svg)", ""]
    cmds = [(f"aiwelfare dist {ref}", "quantile dotplot + percentiles in the terminal")]
    cmds += [
        (f"aiwelfare compare {ref} baseline/{b['id']}", "side by side, same window and units")
        for b in a["baselines"][:1]
    ]
    L += [_commands(cmds, mock), ""]

    # 3. Why it might be much bigger or smaller
    L += [
        "## Why it might be much bigger, or much smaller",
        "",
        "The parameters below move the estimate most when each moves alone from its 5th to its "
        "95th percentile.",
        "",
        "| If you believe… | …the estimate moves |",
        "|---|---|",
    ]
    L += _crux_rows(a, cs) + [""]
    f = a["flip"]
    if f and "error" not in f:
        if f["single_parameter_flips"]:
            items = "; ".join(
                f"`{x['param']}` ({x['risk']}) at {fmt(x['to']) if isinstance(x['to'], float) else x['to']}"
                for x in f["single_parameter_flips"][:3]
            )
            L += [
                f"**Ranking against** *{f['lower'] if f['higher'] == rid else f['higher']}*: "
                f"currently {f['higher']} is ×{f['ratio']:.2g} larger. A single parameter at its "
                f"extreme can flip this: {items}.",
                "",
            ]
        else:
            L += [
                f"**Ranking against** *{a['neighbour']}*: {f['higher']} is ×{f['ratio']:.2g} "
                "larger, and no single parameter at its 5th or 95th percentile flips the order.",
                "",
            ]
    else:
        L += [
            "**Ranking:** no neighbouring risk has a real estimate yet, so there is no ranking "
            "to flip.",
            "",
        ]
    top = a["cruxes"][0]["param"] if a["cruxes"] else "PARAM"
    cmds = [
        (f"aiwelfare cruxes {ref}", "full sensitivity analysis (all parameters)"),
        (f"aiwelfare whatif {ref} --set {top}=VALUE", "rerun with your own assumption"),
        (f"aiwelfare claims {ref} --param {top}", "every sourced claim behind the top crux"),
    ]
    if a["neighbour"]:
        cmds.insert(
            2,
            (
                f"aiwelfare flip {ref} risk/{a['neighbour']}",
                "what must change for the ranking to flip",
            ),
        )
    L += [_commands(cmds, mock), ""]

    # 4. Which AI does it come from?
    L += ["## Which AI does it come from?", ""]
    if cs.sections.get("Which AI does it come from?"):
        L += [cs.sections["Which AI does it come from?"], ""]
    if a["breakdown"]:
        L += ["| Deployment | Share of expected value | 90% range of share |", "|---|---|---|"]
        L += [
            f"| {r['label']} | {r['share_of_ev']:.0%} | {r['share_p05']:.0%} – {r['share_p95']:.0%} |"
            for r in a["breakdown"]["rows"]
        ] + [""]
    else:
        L += [f"*Breakdown not modelled yet:* {a['breakdown_not_modelled']}", ""]
    L += [
        _commands(
            [
                (f"aiwelfare breakdown {ref} --by access-mode", "shares with intervals"),
                (f"aiwelfare claims {ref} --tag access-mode", "the evidence behind each row"),
            ],
            mock,
        ),
        "",
    ]

    # 5. Kinds of work
    L += [
        "## What kinds of work target this risk?"
        if a["kind"] == "risk"
        else "## What kinds of work drive this benefit?",
        "",
        "*This section describes the work; it does not rate how much each kind helps "
        "(tractability is out of scope, see VISION.md).*",
        "",
        "| Kind of work | Close to ML engineering? | Where it's done | Sources |",
        "|---|---|---|---|",
    ]
    for w in a["work"]:
        refs = _group_refs(w["refs"]) or "*no source linked yet*"
        L.append(f"| {w['name']} | {CLOSE_TO_ML[w['close_to_ml']]} | {w['where']} | {refs} |")
    first = a["work"][0]["slug"] if a["work"] else "SLUG"
    L += [
        "",
        _commands(
            [
                (f"aiwelfare work {ref} --refs", "each kind of work + the sources linking it"),
                (f"aiwelfare refs {ref} --work {first}", "sources for one kind of work only"),
                (f"aiwelfare work --kind {first}", "every risk this kind of work targets"),
            ],
            mock,
        ),
        "",
    ]

    # 6. What this number leaves out
    L += [
        "## What this number leaves out",
        "",
        " · ".join(nc["text"] for nc in a["not_captured"]) + ".",
        "",
        _commands(
            [
                (
                    f"aiwelfare not-captured {ref} --refs",
                    "each excluded harm + the sources that discuss it",
                )
            ],
            mock,
        ),
        "",
        "---",
        "",
    ]

    # 7. For checking
    L += [
        "<details>",
        "<summary><b>For checking: model, evidence and provenance</b></summary>",
        "",
        "### All three comparisons",
        "",
        "| Compared with… | Median | 90% interval | Expected value |",
        "|---|---|---|---|",
    ]
    for v in a["by_counterfactual"].values():
        if v["modelled"]:
            L.append(
                f"| {v['label']} | {fmt(v['median'])} | {fmt(v['p05'])} – {fmt(v['p95'])} | "
                f"{fmt(v['expected_value'])} |"
            )
        else:
            L.append(f"| {v['label']} | *not modelled* | | {v['reason']} |")
    L += [
        "",
        "### Model",
        "",
        f"`{a['provenance']['model']}`. Parameters, with the 90% interval of each as simulated:",
        "",
        "| Parameter | What it is | Value | Evidence basis | Claims |",
        "|---|---|---|---|---|",
    ]
    for p in a["params"]:
        L.append(
            f"| `{p['param']}` | {p['description']} | {p['value']} | {p['basis']} | "
            f"{', '.join(c.rsplit('-', 1)[1] for c in p['claims'])} |"
        )
    L += [
        "",
        "### Evidence, by type",
        "",
        "| Evidence type | Basis | Sources | Claims |",
        "|---|---|---|---|",
    ]
    for et, e in a["evidence"].items():
        L.append(
            f"| {et} | {', '.join(e['basis'])} | {', '.join(f'`{x}`' for x in e['sources']) or '—'} "
            f"| {len(e['claims'])} |"
        )
    if a["variants"]:
        L += [
            "",
            "Results by source, where several estimate the same quantity (D14):",
            "",
            "| Parameter | Variant | Median | 90% interval | Expected value |",
            "|---|---|---|---|---|",
        ]
        for v in a["variants"]:
            L.append(
                f"| `{v['param']}` | {v['variant']} | {fmt(v['median'])} | {fmt(v['p05'])} – "
                f"{fmt(v['p95'])} | {fmt(v['expected_value'])} |"
            )
        L += ["", "The combined figures weight each variant equally (D14)."]
    if a["assumptions"]:
        L += ["", "### ⚠️ Assumptions (no source gives these values)", ""]
        L += [
            f"- **{x['claim']}**: {x['description']} *Would be replaced by:* {x['replace_with']}"
            for x in a["assumptions"]
        ]
    c = a["confidence"]
    L += [
        "",
        "### Confidence (D12)",
        "",
        f"{c['level'].capitalize()}. Top 5% of futures give {c['top5_share_of_ev']:.0%} of the "
        f"expected value (tail-dominated above 50%, D11). Share of crux swing from parameters "
        f"backed by measured evidence: {c['swing_share_measured']:.0%}; from expert judgement or "
        f"speculation only: {c['swing_share_expert_or_speculation']:.0%}.",
    ]
    L += ["", "### Known limitations", ""] + [f"- {x}" for x in a["limitations"]]
    pv = a["provenance"]
    idx = ", ".join(a["index_entries"]) or "MIT AI Risk Repository mapping not done yet (D3)"
    L += [
        "",
        "### Index and provenance",
        "",
        f"{idx} · model `{pv['model']}` · prose `{pv['card_source']}` · inputs as of commit "
        f"`{pv['commit']}`"
        + (" **with uncommitted input changes**" if pv["uncommitted_input_changes"] else "")
        + f" · seed {pv['seed']}, {pv['draws']:,} draws",
    ]
    if a["changelog"]:
        L += ["", "### Changelog", "", "| Date | Change | Why |", "|---|---|---|"]
        L += [f"| {r['date']} | {r['change']} | {r['why'][:160]} |" for r in a["changelog"]]
    L += [
        "",
        _commands(
            [
                (f"aiwelfare model {ref}", "print the model and its parameters"),
                (f"aiwelfare claims {ref} --evidence-type assumption", "the flagged assumptions"),
                (f"aiwelfare sources {ref}", "full bibliography, with pinned versions"),
                (f"aiwelfare rerun {ref}", "reproduce every number on this card"),
                (f"aiwelfare log {ref}", "full change history with reasons"),
            ],
            mock,
        ),
        "",
        "</details>",
        "",
    ]
    if mock:
        L += [MOCK_BOTTOM, ""]
    return "\n".join(L)


def output_dir(ds, risk: str, mock: bool) -> Path:
    return ds.root / ("mock/build" if mock else "results") / risk


def build(
    ds, risk: str, counterfactual: str = DEFAULT_COUNTERFACTUAL, seed: int = engine.DEFAULT_SEED
) -> tuple[Path, dict]:
    a = analyse(ds, risk, counterfactual, seed=seed)
    cs = load_card_source(ds, risk)
    out = output_dir(ds, risk, a["mock"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "card.md").write_text(render(a, cs))
    title = f"{a['title']}: DALYs {a['window'][0]}–{a['window'][1]}, vs {a['counterfactual_label']}"
    (out / "dotplot.svg").write_text(
        dotplot.svg(a["summary"]["dotplot_quantiles"], title, a["mock"])
    )
    (out / "card.json").write_text(
        json.dumps(a, indent=1, ensure_ascii=False, default=_jsonable) + "\n"
    )
    return out, a


def _jsonable(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, set):
        return sorted(o)
    return str(o)
