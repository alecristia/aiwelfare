"""Tests for milestone 1: schemas, engine, CLI contract (D10), mock labelling (D13), cards."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pytest
import yaml
from typer.testing import CliRunner

from aiwelfare import card, data, engine
from aiwelfare.cli import MOCK_BANNER, app

ROOT = Path(__file__).resolve().parents[1]
REAL = "risk/data-centre-air-pollution"
MOCK = "risk/bio-misuse"
runner = CliRunner()


# ---- validation ------------------------------------------------------------------


def test_repository_is_valid():
    assert data.validate(ROOT) == []


@pytest.fixture
def scratch(tmp_path):
    """A copy of the repo's data tree, safe to break."""
    for d in ("sources", "claims", "mock"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("*.pdf", "build"))
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "decisions.md").write_text("")
    (tmp_path / "pyproject.toml").write_text("")
    return tmp_path


def _edit(path: Path, **changes):
    d = yaml.safe_load(path.read_text())
    d.update(changes)
    path.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))


def test_rejects_long_quote(scratch):
    f = scratch / "claims/data-centre-air-pollution/data-centre-air-pollution-001.yaml"
    _edit(f, quote=" ".join(["word"] * 25))
    assert any("must be under 25" in p for p in data.validate(scratch))


def test_rejects_mock_outside_mock_tree(scratch):
    f = scratch / "claims/data-centre-air-pollution/data-centre-air-pollution-001.yaml"
    _edit(f, mock=True)
    assert any("D13" in p for p in data.validate(scratch))


def test_rejects_real_data_inside_mock_tree(scratch):
    f = scratch / "mock/claims/bio-misuse/bio-misuse-001.yaml"
    _edit(f, mock=False)
    assert any("D13" in p for p in data.validate(scratch))


def test_rejects_assumption_without_rationale(scratch):
    f = scratch / "claims/data-centre-air-pollution/data-centre-air-pollution-025.yaml"
    d = yaml.safe_load(f.read_text())
    del d["rationale"]
    f.write_text(yaml.safe_dump(d, sort_keys=False))
    assert any("rationale" in p for p in data.validate(scratch))


def test_rejects_unknown_source(scratch):
    f = scratch / "claims/data-centre-air-pollution/data-centre-air-pollution-001.yaml"
    _edit(f, source="no-such-source")
    assert any("unknown source" in p for p in data.validate(scratch))


def test_every_model_parameter_cites_existing_claims():
    ds = data.load(ROOT, include_mock=True)
    for risk in ("data-centre-air-pollution", "bio-misuse"):
        m = engine.Model.load(ds, risk)  # raises KeyError on unknown claims
        assert all(p.claims for p in m.params)


# ---- engine ----------------------------------------------------------------------


@pytest.mark.parametrize("risk,mock", [("data-centre-air-pollution", False), ("bio-misuse", True)])
def test_seeded_runs_are_reproducible(risk, mock):
    ds = data.load(ROOT, include_mock=mock)
    m = engine.Model.load(ds, risk)
    a, _ = m.run("frozen-2026", n=5000, seed=7)
    b, _ = m.run("frozen-2026", n=5000, seed=7)
    c, _ = m.run("frozen-2026", n=5000, seed=8)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_tail_flag_and_confidence():
    y = np.zeros(1000)
    y[-10:] = 1e6
    s = engine.summarise(y)
    assert s["tail_dominated"] and s["share_zero"] == 0.99
    assert engine.confidence(s, [])["level"] == "low"
    s2 = engine.summarise(np.full(1000, 5.0))
    assert not s2["tail_dominated"]


def test_frozen_is_below_no_ai_for_air_pollution():
    ds = data.load(ROOT)
    m = engine.Model.load(ds, "data-centre-air-pollution")
    assert m.run("frozen-2026", n=5000)[0].mean() < m.run("no-ai", n=5000)[0].mean()


def test_mock_model_needs_include_mock():
    with pytest.raises(FileNotFoundError):
        engine.Model.load(data.load(ROOT), "bio-misuse")


# ---- CLI contract ------------------------------------------------------------------

JSON_COMMANDS = [
    ["validate"],
    ["sources", REAL],
    ["claims", REAL],
    ["claims", REAL, "--param", "e2028"],
    ["show", REAL],
    ["dist", REAL],
    ["cruxes", REAL],
    ["whatif", REAL, "--set", "e2028=400"],
    ["breakdown", REAL],
    ["model", REAL],
    ["work", REAL, "--refs"],
    ["work", "--kind", "workload-scheduling"],
    ["refs", REAL, "--work", "workload-scheduling"],
    ["not-captured", REAL, "--refs"],
    ["log", REAL],
    ["show", MOCK, "--include-mock"],
    ["dist", MOCK, "--include-mock"],
    ["breakdown", MOCK, "--include-mock"],
    ["compare", MOCK, "baseline/malaria", "--include-mock"],
    ["compare", MOCK, REAL, "--include-mock"],
    ["flip", MOCK, REAL, "--include-mock"],
]


@pytest.mark.parametrize("args", JSON_COMMANDS, ids=lambda a: " ".join(a[:2]))
def test_every_command_supports_json(args):
    r = runner.invoke(app, [*args, "--json"])
    assert r.exit_code == 0, r.output
    payload = json.loads(r.output)
    assert isinstance(payload, dict)


@pytest.mark.parametrize(
    "args", [a for a in JSON_COMMANDS if "--include-mock" in a], ids=lambda a: " ".join(a[:2])
)
def test_mock_outputs_are_labelled(args):
    r = runner.invoke(app, args)
    assert r.exit_code == 0, r.output
    assert MOCK_BANNER in r.output or "INVENTED NUMBERS" in r.output
    assert json.loads(runner.invoke(app, [*args, "--json"]).output)["mock"] is True


@pytest.mark.parametrize("args", [["dist", REAL], ["cruxes", REAL], ["show", REAL]])
def test_real_outputs_are_not_labelled_mock(args):
    r = runner.invoke(app, args)
    assert MOCK_BANNER not in r.output and "INVENTED" not in r.output


def test_numeric_outputs_state_counterfactual():
    for cmd in (["dist", REAL], ["cruxes", REAL], ["whatif", REAL, "--set", "e2028=400"]):
        out = runner.invoke(app, cmd).output
        assert "Compared with: AI frozen at 2026 levels" in out


def test_unmodelled_counterfactual_is_refused():
    r = runner.invoke(app, ["dist", REAL, "--counterfactual", "open-only"])
    assert r.exit_code != 0 and "not modelled" in r.output


# ---- cards ---------------------------------------------------------------------------

D4_HEADINGS = [
    "## Is this big?",
    "## Why it might be much bigger, or much smaller",
    "## Which AI does it come from?",
    "## What kinds of work target this risk?",
    "## What this number leaves out",
    "For checking",
]


@pytest.mark.parametrize("risk,mock", [("data-centre-air-pollution", False), ("bio-misuse", True)])
def test_card_has_d4_sections_in_order_with_commands(risk, mock):
    ds = data.load(ROOT, include_mock=mock)
    a = card.analyse(ds, risk, with_changelog=False)
    text = card.render(a, card.load_card_source(ds, risk))
    pos = [text.index(h) for h in D4_HEADINGS]
    assert pos == sorted(pos)
    # every section ends with dig-deeper commands
    sections = text.split("\n## ")[1:]
    assert all("```\naiwelfare " in s for s in sections)
    assert text.startswith(card.MOCK_TOP) == mock
    assert text.rstrip().endswith(card.MOCK_BOTTOM) == mock


def test_committed_cards_are_current():
    """Generated cards are never hand-edited: committed outputs must match a fresh build."""
    for risk, mock, folder in (
        ("data-centre-air-pollution", False, "results"),
        ("bio-misuse", True, "mock/build"),
    ):
        path = ROOT / folder / risk / "card.json"
        if not path.exists():
            pytest.skip(f"{path} not built yet")
        ds = data.load(ROOT, include_mock=mock)
        fresh = card.analyse(ds, risk, with_changelog=False)
        stored = json.loads(path.read_text())["summary"]
        new = json.loads(json.dumps(fresh["summary"]))
        assert stored.pop("dotplot_quantiles") == pytest.approx(new.pop("dotplot_quantiles"))
        assert stored == pytest.approx(new)


# ---- net cards (D17) -------------------------------------------------------------------

NET_MODEL = '''
import numpy as np
from aiwelfare.engine import Param, uniform

RISK = "toy-net"
TITLE = "Toy net card"
WINDOW = (2027, 2031)
COUNTERFACTUALS = {"no-ai": "No modern AI"}
NOT_MODELLED = {}
COMPONENTS = {"good": ("benefit", "a benefit"), "bad": ("harm", "a harm")}

def params(ds):
    return [
        Param("gain", "benefit size", [], uniform(100, 1000), "toy"),
        Param("loss", "harm size", [], uniform(10, 2000), "toy"),
    ]

def simulate(x, counterfactual):
    return {"good": x["gain"], "bad": x["loss"]}
'''


@pytest.fixture
def net_model(tmp_path):
    path = tmp_path / "toy_net.py"
    path.write_text(NET_MODEL)
    import importlib.util

    spec = importlib.util.spec_from_file_location("toy_net", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return engine.Model(mod, mod.params(None), path)


def test_net_is_harms_minus_benefits(net_model):
    comps, x = net_model.run_components("no-ai", n=2000)
    y, _ = net_model.run("no-ai", n=2000)
    assert np.allclose(y, x["loss"] - x["gain"])
    assert np.allclose(net_model.run("no-ai", n=2000, component="good")[0], x["gain"])
    assert (y < 0).any() and (y > 0).any()  # straddles zero


def test_net_summary_reports_components_and_sign(net_model):
    comps, _ = net_model.run_components("no-ai", n=5000)
    s = engine.summarise_net(net_model, comps)
    assert set(s["components"]) == {"good", "bad"}
    assert s["components"]["good"]["role"] == "benefit"
    assert 0 < s["share_net_harm"] < 1
    assert s["p05"] < 0 < s["p95"]
    assert s["tail_dominated"] == any(c["tail_dominated"] for c in s["components"].values())


def test_net_cruxes_are_absolute_and_component_cruxes_are_ratios(net_model):
    rows = engine.cruxes(net_model, "no-ai", n=2000)
    assert all(r["swing_kind"] == "absolute" for r in rows)
    loss = next(r for r in rows if r["param"] == "loss")
    assert loss["swing"] == pytest.approx(loss["ev_high"] - loss["ev_low"])
    assert rows[0]["param"] == "loss"  # wider range, bigger absolute swing
    comp = engine.cruxes(net_model, "no-ai", n=2000, component="bad")
    assert all(r["swing_kind"] == "ratio" for r in comp)
    conf = engine.confidence(engine.summarise(np.ones(10)), rows)
    assert conf["level"] in {"low", "medium", "high"}


def test_net_component_must_be_magnitude(net_model):
    net_model.module.simulate = lambda x, cf: {"good": -x["gain"], "bad": x["loss"]}
    with pytest.raises(ValueError, match="magnitude"):
        net_model.run("no-ai", n=100)


def test_signed_dotplot_mirrors_log_axis():
    from aiwelfare import dotplot

    q = [-1e5, -1e4, -1e3, 0, 1e3, 1e4] + [-5e3] * 14
    zeros, neg, pos, (lo, hi) = dotplot._signed_layout(q, 2)
    assert zeros == 1 and sum(neg.values()) == 17 and sum(pos.values()) == 2
    assert (lo, hi) == (3, 5)
    svg = dotplot.svg_signed(q, "t")
    assert "net benefit" in svg and "net harm" in svg
    assert "net benefit" in dotplot.text_signed(q)
    assert dotplot.fmt_net(-33000) == "33k averted" and dotplot.fmt_net(1200) == "1.2k lost"
