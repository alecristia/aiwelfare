"""Tests for the static site and explorer (D6, D8, D10, D13; docs/tasks/website-and-explorer.md)."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aiwelfare import card as cardmod
from aiwelfare import data, explorer, site
from aiwelfare.cli import app

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site") / "site"
    site.build(ROOT, out)
    return out


@pytest.fixture(scope="module")
def global_fixture(tmp_path_factory) -> Path:
    """A copy of the repo in which the US-only air-pollution card claims to be global, and the
    clinical-AI net card (D17, work in progress) is generated, so the canonical build has real
    rows to show. Neither change touches the real repo."""
    root = tmp_path_factory.mktemp("repo")
    yaml_only = shutil.ignore_patterns("*.pdf", "*.csv", "*.zip", "gbd", "__pycache__")
    for d in ("sources", "claims", "models", "cards", "results", "baselines", "mock"):
        shutil.copytree(ROOT / d, root / d, ignore=yaml_only)
    (root / "docs").mkdir()
    for f in ("decisions.md", "roadmap.md"):
        shutil.copyfile(ROOT / "docs" / f, root / "docs" / f)
    shutil.copyfile(ROOT / "pyproject.toml", root / "pyproject.toml")
    cj = root / "results/data-centre-air-pollution/card.json"
    c = json.loads(cj.read_text())
    c["geography"] = "global"
    cj.write_text(json.dumps(c))
    cardmod.build(data.load(root), "clinical-ai")
    out = root / "site"
    site.build(root, out)
    return out


def _spec(out: Path) -> dict:
    return json.loads((out / "data/spec.json").read_text())


# ---- which cards appear ----------------------------------------------------------------


def test_every_real_global_card_appears(global_fixture):
    spec = _spec(global_fixture)
    risks = ["clinical-ai", "data-centre-air-pollution"]
    assert sorted(c["risk"] for c in spec["cards"]) == risks
    index = (global_fixture / "index.html").read_text()
    for r in risks:
        assert f'href="cards/{r}.html"' in index  # a row on the chart
        assert (global_fixture / f"cards/{r}.html").exists()
        for cf in explorer.COUNTERFACTUALS:
            assert r in (global_fixture / f"overview-{cf}.svg").read_text()


def test_net_card_gets_a_mirrored_axis(global_fixture):
    spec = _spec(global_fixture)
    assert explorer.signed_axis(spec)
    svg = (global_fixture / "overview-frozen-2026.svg").read_text()
    assert "net benefit (DALYs averted)" in svg and "net harm in" in svg
    net = next(c for c in spec["cards"] if c["risk"] == "clinical-ai")
    ev = net["results"]["frozen-2026"]["expected_value"]
    x = explorer.scale(3, 9, True)
    assert (x(ev) < explorer.MID) == (ev < 0)  # net benefit left of zero, net harm right
    assert x(-1e5) < x(0) < x(1e5) and x(1e5) - x(0) == x(0) - x(-1e5)  # mirrored


def test_one_sided_axis_without_net_cards(built):
    assert not explorer.signed_axis(_spec(built / "demo"))


def test_every_real_card_in_results_is_shown_or_explained(built):
    spec = _spec(built)
    shown = {c["risk"] for c in spec["cards"]}
    for p in (ROOT / "results").glob("*/card.json"):
        c = json.loads(p.read_text())
        assert (c["risk"] in shown) == (c["geography"] == "global" and not c["mock"])


def test_canonical_chart_has_no_us_only_or_mock_card(built):
    spec = _spec(built)
    assert not spec["mock"]
    assert all(c["geography"] == "global" and not c["mock"] for c in spec["cards"])
    assert all(not b["mock"] for b in spec["baselines"])
    for f in [built / "index.html", *built.glob("overview-*.svg"), *built.glob("cards/*")]:
        text = f.read_text()
        assert "data-centre-air-pollution.html" not in text, f
        assert "bio-misuse" not in text and "MOCK" not in text, f
    assert not (built / "cards/bio-misuse.html").exists()


def test_regional_build_cannot_overwrite_site(tmp_path):
    with pytest.raises(ValueError):
        site.build(ROOT, ROOT / "site", allow_regional=True)


# ---- mock banners (D13) -----------------------------------------------------------------


def test_mock_banner_wherever_mock_data_is(built):
    demo = built / "demo"
    assert _spec(demo)["mock"]
    assert any(c["mock"] for c in _spec(demo)["cards"])
    for f in demo.rglob("*.html"):
        assert f.read_text().count(site.MOCK_BANNER.replace("'", "&#x27;")) == 2, f  # top, bottom
    for f in demo.rglob("*.svg"):
        assert "INVENTED (MOCK) DATA" in f.read_text(), f
    view = explorer.forest_svg([], _spec(demo)["baselines"], _spec(demo), explorer.State("no-ai"))
    assert view.count("INVENTED (MOCK) DATA") == 2  # the explorer's own chart, top and bottom


def test_canonical_site_links_to_demo_but_has_no_banner(built):
    index = (built / "index.html").read_text()
    assert 'href="demo/index.html"' in index
    assert "INVENTED" not in index


# ---- URL state (D6) ---------------------------------------------------------------------


def _demo_spec(built):
    return _spec(built / "demo")


@pytest.mark.parametrize(
    "state",
    [
        explorer.State(),
        explorer.State("no-ai"),
        explorer.State("open-only", {"bio-misuse": {"severity": "1e06"}}),
        explorer.State(
            "frozen-2026",
            {"bio-misuse": {"evidence": "lab evaluation", "post_2026_share": "0.25"}},
            ["ml", "tail"],
        ),
    ],
)
def test_url_round_trip(built, state):
    spec = _demo_spec(built)
    q = explorer.encode(state)
    back, problems = explorer.decode(q, spec)
    assert problems == []
    assert back.to_dict() == state.to_dict()
    assert explorer.encode(back) == q
    assert (q == "") == state.is_default


def test_url_numbers_survive_query_string_parsing(built):
    spec = _demo_spec(built)
    s, _ = explorer.decode("bio-misuse.severity=1000000", spec)
    q = explorer.encode(s)
    assert "+" not in q  # "+" would read back as a space
    assert explorer.decode(q, spec)[0].settings == {"bio-misuse": {"severity": "1e06"}}


def test_url_rejects_unknown_settings(built):
    s, problems = explorer.decode(
        "cf=nope&bio-misuse.nope=1&bio-misuse.evidence=x", _demo_spec(built)
    )
    assert s.is_default and len(problems) == 3


# ---- the explorer computes what the CLI computes (D10) ----------------------------------

_BROWSER_CHECK = """
import json, sys
root = sys.argv[1]
sys.path.insert(0, root + "/py")
from aiwelfare import explorer as ex
assert ex.__file__.startswith(root), ex.__file__   # the site's copies, as the browser loads them
spec = json.load(open(root + "/data/spec.json"))
E = ex.Explorer(spec, json.load(open(root + "/data/claims.json")), root + "/py")
out = {"diffs": E.check_defaults(), "views": {}}
for q in sys.argv[2:]:
    state = ex.decode(q, spec)[0]
    out["views"][q] = {r["risk"]: r["summary"] for r in ex.compute(E.models, spec, state)}
print(json.dumps(out))
"""


def _browser(root: Path, *queries: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", _BROWSER_CHECK, str(root), *queries],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def test_explorer_defaults_equal_cli(built):
    res = _browser(built / "demo", "", "cf=no-ai")
    assert res["diffs"] == []
    for q, cf in (("", "frozen-2026"), ("cf=no-ai", "no-ai")):
        cli = json.loads(
            runner.invoke(
                app, ["dist", "risk/bio-misuse", "-c", cf, "--include-mock", "--json"]
            ).output
        )["summary"]
        mine = res["views"][q]["bio-misuse"]
        for k in ("expected_value", "median", "p05", "p95", "tail_dominated"):
            assert mine[k] == cli[k], (q, k)


def test_explorer_equals_cli_on_a_net_card(global_fixture):
    spec = _spec(global_fixture)
    p = next(c for c in spec["cards"] if c["risk"] == "clinical-ai")["params"][0]
    value = p["categories"][0] if p["categorical"] else explorer.canonical_number(p["max"])
    q = explorer.encode(explorer.State("no-ai", {"clinical-ai": {p["name"]: value}}))
    res = _browser(global_fixture, "", q)
    assert res["diffs"] == []
    cli = json.loads(
        runner.invoke(
            app,
            [
                "whatif",
                "risk/clinical-ai",
                "--set",
                f"{p['name']}={value}",
                "-c",
                "no-ai",
                "--json",
            ],
        ).output
    )["yours"]
    mine = res["views"][q]["clinical-ai"]
    for k in ("expected_value", "median", "p05", "p95", "share_net_harm"):
        assert mine[k] == cli[k], k


def test_explorer_settings_equal_whatif(built):
    q = "cf=no-ai&bio-misuse.severity=1e06&bio-misuse.evidence=lab%20evaluation"
    mine = _browser(built / "demo", q)["views"][q]["bio-misuse"]
    args = ["--set", "severity=1e06", "--set", "evidence=lab evaluation", "-c", "no-ai"]
    cli = json.loads(
        runner.invoke(app, ["whatif", "risk/bio-misuse", *args, "--include-mock", "--json"]).output
    )["yours"]
    for k in ("expected_value", "median", "p05", "p95"):
        assert mine[k] == cli[k], k


def test_whatif_commands_reproduce_settings(built):
    spec = _demo_spec(built)
    s, _ = explorer.decode("bio-misuse.evidence=lab%20evaluation&bio-misuse.severity=2e05", spec)
    cmds = explorer.whatif_commands(s, spec)
    assert cmds == [
        "aiwelfare whatif risk/bio-misuse --set 'evidence=lab evaluation' --set severity=200000 "
        "--counterfactual frozen-2026 --include-mock"
    ]


def test_static_chart_is_the_explorer_at_default(global_fixture):
    """The canonical chart (from card.json) and the explorer's default chart are identical."""
    spec = _spec(global_fixture)
    sys_path = str(global_fixture / "py")
    code = (
        "import json,sys; sys.path.insert(0, sys.argv[1]); from aiwelfare import explorer as ex;"
        "spec=json.load(open(sys.argv[2]+'/data/spec.json'));"
        "E=ex.Explorer(spec, json.load(open(sys.argv[2]+'/data/claims.json')), sys.argv[1]);"
        "print(json.dumps({cf: E.update('' if cf==ex.DEFAULT_COUNTERFACTUAL else 'cf='+cf)['svg']"
        " for cf in ex.COUNTERFACTUALS}))"
    )
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, sys_path, str(global_fixture)],
        capture_output=True,
        text=True,
        check=True,
    )
    svgs = json.loads(proc.stdout)
    assert spec["cards"]
    for cf, svg in svgs.items():
        assert svg == (global_fixture / f"overview-{cf}.svg").read_text(), cf
        assert "YOUR SETTINGS" not in svg  # a counterfactual is canonical; parameters are not


# ---- pages and reproducibility ----------------------------------------------------------


def test_card_page_follows_d4(built):
    page = (built / "demo/cards/bio-misuse.html").read_text()
    order = [
        "Is this big?",
        "Why it might be much bigger",
        "Which AI does it come from?",
        "What kinds of work target this risk?",
        "What this number leaves out",
        "For checking",
    ]
    pos = [page.index(h) for h in order]
    assert pos == sorted(pos)
    assert page.count('<pre class="cmd">') >= 6  # dig-deeper commands stay visible
    assert "<details>" in page and "<details open" not in page  # "for checking" collapsed
    assert 'src="bio-misuse-dotplot.svg"' in page


def test_overview_lists_scope_cuts_and_not_captured(built):
    index = (built / "index.html").read_text()
    for cut in ("Loss of control", "Health misinformation", "Disruption of financial institutions"):
        assert cut in index
    demo = (built / "demo/index.html").read_text()
    assert "Economic and social disruption beyond health loss" in demo
    assert explorer.NOT_SUMMED in index


def _tree(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_build_is_deterministic(built, tmp_path):
    again = tmp_path / "site"
    site.build(ROOT, again)
    assert _tree(again) == _tree(built)


def test_cli_build_site_json(tmp_path):
    res = runner.invoke(app, ["build", "site", "--out", str(tmp_path / "s"), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["mock"] is False and payload["demo"]["mock"] is True
    res = runner.invoke(app, ["build", "site", "--allow-regional", "--json"])
    assert res.exit_code == 1 and "error" in json.loads(res.output)


def test_refuses_to_clear_a_folder_it_did_not_write(tmp_path):
    (tmp_path / "mine.txt").write_text("keep me")
    with pytest.raises(FileExistsError):
        site.build(ROOT, tmp_path)
    assert (tmp_path / "mine.txt").exists()
