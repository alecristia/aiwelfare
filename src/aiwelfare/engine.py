"""Monte Carlo engine: declared parameters, simulation, summaries (VISION.md §3–4; D11, D12, D14).

A model module (models/<risk_id>.py) defines:
    RISK: str
    TITLE: str
    WINDOW: tuple[int, int]          years summed, inclusive
    COUNTERFACTUALS: dict[str, str]  supported counterfactual -> plain-language label
    NOT_MODELLED: dict[str, str]     counterfactual -> reason it is not modelled yet
    def params(ds) -> list[Param]    parameters fitted to claims (fixed inputs included)
    def simulate(x, counterfactual) -> np.ndarray   DALYs per draw over WINDOW

Optional:
    STOCHASTIC = True                simulate(x, counterfactual, rng) also gets a generator for
                                     event draws (e.g. whether an outbreak happens); it is
                                     seeded separately so parameter draws stay comparable
    ACCESS_MODES: dict[str, str]     access mode -> label (D4 "Which AI does it come from?")
    def access_shares(x, counterfactual) -> dict[str, np.ndarray]   share per draw, sums to 1
    BREAKDOWN_NOT_MODELLED: str      why there is no access-mode breakdown yet

Net cards (D17): a model whose card has both harm and benefit components declares
    COMPONENTS: dict[str, tuple[str, str]]   name -> ("harm" | "benefit", plain-language label)
and its simulate() returns a dict name -> DALYs per draw, each a magnitude (>= 0). The engine
reports each component and the net, harms − benefits, in DALYs lost: positive is net harm,
negative is net benefit (DALYs averted). Models without COMPONENTS are unchanged.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DEFAULT_DRAWS = 100_000
DEFAULT_SEED = 20261125
Z95 = 1.959964  # two-sided 95%
Z90 = 1.644854  # two-sided 90%

BASIS_RANK = {"measured": 0, "modelled": 1, "expert-judgement": 2, "speculation": 3}


@dataclass
class Param:
    name: str
    description: str
    claims: list[str]
    sample: Callable[[np.random.Generator, int], np.ndarray]
    fit: str  # how the claims became this distribution, in words
    categories: list[str] | None = None  # for categorical parameters (variant choice)
    fixed: bool = False  # a single value taken from a claim; shown, but not a crux
    basis: str = ""  # filled from claims by Model.load
    evidence_types: list[str] = field(default_factory=list)

    @property
    def categorical(self) -> bool:
        return self.categories is not None


# ---- distribution helpers (fitting choices are stated in each Param.fit) ----


def uniform(low: float, high: float):
    return lambda rng, n: rng.uniform(low, high, n)


def lognormal_ci(low: float, high: float, z: float = Z95):
    """Lognormal whose central interval (±z) runs from low to high."""
    mu = (np.log(low) + np.log(high)) / 2
    sigma = (np.log(high) - np.log(low)) / (2 * z)
    return lambda rng, n: rng.lognormal(mu, sigma, n)


def fixed(value: float):
    """A single value taken straight from a claim (declare with Param(..., fixed=True))."""
    return lambda rng, n: np.full(n, float(value))


def choice(n_options: int):
    """Equal-weight choice among variants (D14)."""
    return lambda rng, n: rng.integers(0, n_options, n)


def claim_value(ds, claim_id: str) -> dict:
    return ds.claims[claim_id]["value"]


# ---- model loading and running ---------------------------------------------


@dataclass
class Model:
    module: object
    params: list[Param]
    path: Path
    mock: bool = False

    @property
    def risk(self) -> str:
        return self.module.RISK

    @classmethod
    def load(cls, ds, risk: str) -> Model:
        name = f"{risk.replace('-', '_')}.py"
        candidates = [(ds.root / "models" / name, False)]
        if ds.include_mock:
            candidates.insert(0, (ds.root / "mock" / "models" / name, True))
        found = [(p, m) for p, m in candidates if p.exists()]
        if not found:
            hint = "" if ds.include_mock else " (add --include-mock for invented risks)"
            raise FileNotFoundError(f"no model for {risk}{hint}")
        path, is_mock = found[0]
        spec = importlib.util.spec_from_file_location(f"aiwelfare_models.{path.stem}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        params = mod.params(ds)
        for p in params:
            missing = [c for c in p.claims if c not in ds.claims]
            if missing:
                raise KeyError(f"{risk}: parameter {p.name} cites unknown claims {missing}")
            bases = [ds.claims[c]["evidence_basis"] for c in p.claims]
            # A parameter is as strong as its strongest claim (measured < modelled < …).
            p.basis = min(bases, key=BASIS_RANK.__getitem__)
            p.evidence_types = sorted({ds.claims[c]["evidence_type"] for c in p.claims})
        return cls(mod, params, path, mock=is_mock)

    @property
    def counterfactuals(self) -> dict[str, str]:
        return self.module.COUNTERFACTUALS

    @property
    def components(self) -> dict[str, tuple[str, str]]:
        """Net models (D17): name -> (role, label); empty for single-quantity models."""
        return dict(getattr(self.module, "COMPONENTS", {}))

    @property
    def is_net(self) -> bool:
        return bool(self.components)

    def draw(
        self,
        n: int = DEFAULT_DRAWS,
        seed: int = DEFAULT_SEED,
        fixed: dict[str, float | np.ndarray] | None = None,
    ) -> dict[str, np.ndarray]:
        rng = np.random.default_rng(seed)
        x = {p.name: p.sample(rng, n) for p in self.params}  # always draw all: stable streams
        for k, v in (fixed or {}).items():
            if k not in x:
                raise KeyError(f"unknown parameter {k}")
            x[k] = np.broadcast_to(np.asarray(v, dtype=x[k].dtype), (n,)).copy()
        return x

    def run_components(
        self,
        counterfactual: str,
        n: int = DEFAULT_DRAWS,
        seed: int = DEFAULT_SEED,
        fixed: dict | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
        """DALYs per draw for each component (magnitudes); single-quantity models give "total"."""
        if counterfactual not in self.module.COUNTERFACTUALS:
            raise ValueError(f"{self.risk}: counterfactual {counterfactual} not modelled")
        x = self.draw(n, seed, fixed)
        if getattr(self.module, "STOCHASTIC", False):
            events = np.random.default_rng([seed, 1])  # same event draws in every run (cruxes)
            y = self.module.simulate(x, counterfactual, events)
        else:
            y = self.module.simulate(x, counterfactual)
        if not self.is_net:
            return {"total": np.asarray(y, dtype=float)}, x
        if set(y) != set(self.components):
            raise ValueError(f"{self.risk}: simulate() must return exactly {list(self.components)}")
        out = {k: np.asarray(y[k], dtype=float) for k in self.components}
        for k, v in out.items():
            if (v < 0).any():
                raise ValueError(f"{self.risk}: component {k} must be a magnitude (>= 0)")
        return out, x

    def net(self, comps: dict[str, np.ndarray]) -> np.ndarray:
        """Harms − benefits, in DALYs lost (D17)."""
        if not self.is_net:
            return comps["total"]
        sign = {"harm": 1.0, "benefit": -1.0}
        return sum(sign[self.components[k][0]] * v for k, v in comps.items())

    def run(
        self,
        counterfactual: str,
        n: int = DEFAULT_DRAWS,
        seed: int = DEFAULT_SEED,
        fixed: dict | None = None,
        component: str | None = None,
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """DALYs per draw: the net for net models (signed), or one component if named."""
        comps, x = self.run_components(counterfactual, n, seed, fixed)
        if component is not None:
            if component not in comps or not self.is_net:
                raise KeyError(f"{self.risk} has no component {component}")
            return comps[component], x
        return self.net(comps), x


# ---- summaries ----------------------------------------------------------------


def summarise(y: np.ndarray) -> dict:
    y = np.asarray(y, dtype=float)
    ev = float(y.mean())
    q = np.quantile(y, [0.05, 0.5, 0.95])
    top = np.sort(y)[int(0.95 * len(y)) :]
    tail_share = float(top.sum() / y.sum()) if y.sum() > 0 else 0.0
    return {
        "expected_value": ev,
        "median": float(q[1]),
        "p05": float(q[0]),
        "p95": float(q[2]),
        "share_zero": float((y <= 0).mean()),
        "top5_share_of_ev": tail_share,
        "tail_dominated": tail_share > 0.5,  # D11
        "dotplot_quantiles": [float(v) for v in np.quantile(y, (np.arange(20) + 0.5) / 20)],
    }


def summarise_net(model: Model, comps: dict[str, np.ndarray]) -> dict:
    """D17: the net (signed) plus each component summarised as a harm card would be.

    D11 is defined for non-negative outcomes, so it is computed per component; the net is
    tail-dominated if any component is, and its tail share is the largest component's.
    """
    y = model.net(comps)
    q = np.quantile(y, [0.05, 0.5, 0.95])
    parts = {
        k: {"role": model.components[k][0], "label": model.components[k][1], **summarise(v)}
        for k, v in comps.items()
    }
    return {
        "expected_value": float(y.mean()),
        "median": float(q[1]),
        "p05": float(q[0]),
        "p95": float(q[2]),
        "share_zero": float((y == 0).mean()),
        "share_net_harm": float((y > 0).mean()),
        "top5_share_of_ev": max(p["top5_share_of_ev"] for p in parts.values()),
        "tail_dominated": any(p["tail_dominated"] for p in parts.values()),
        "tail_dominated_components": [k for k, p in parts.items() if p["tail_dominated"]],
        "dotplot_quantiles": [float(v) for v in np.quantile(y, (np.arange(20) + 0.5) / 20)],
        "components": parts,
        "signed": True,
    }


def summarise_model(model: Model, comps: dict[str, np.ndarray]) -> dict:
    return summarise_net(model, comps) if model.is_net else summarise(comps["total"])


def cruxes(
    model: Model,
    counterfactual: str,
    n: int = 20_000,
    seed: int = DEFAULT_SEED,
    component: str | None = None,
) -> list[dict]:
    """One-at-a-time swing of each parameter, 5th → 95th percentile (D12).

    Categorical parameters swing between their lowest- and highest-EV variant.
    The swing is a ratio (EV high ÷ EV low), except for the net of a net model (D17),
    whose expected value can cross zero: there it is the absolute change in DALYs.
    """
    absolute = model.is_net and component is None
    base = model.draw(n, seed)

    def ev(fixed):
        return float(model.run(counterfactual, n, seed, fixed, component)[0].mean())

    out = []
    for p in model.params:
        if p.fixed:
            continue
        if p.categorical:
            evs = {cat: ev({p.name: i}) for i, cat in enumerate(p.categories)}
            lo_k, hi_k = min(evs, key=evs.get), max(evs, key=evs.get)
            lo, hi = evs[lo_k], evs[hi_k]
            settings = {"low": lo_k, "high": hi_k}
        else:
            v05, v95 = np.quantile(base[p.name], [0.05, 0.95])
            lo, hi = ev({p.name: v05}), ev({p.name: v95})
            settings = {"low": float(v05), "high": float(v95)}
        a, b = sorted([lo, hi])
        if absolute:
            swing = float(b - a)
        else:
            swing = float(b / a) if a > 0 else (1.0 if b == a else float("inf"))
        out.append(
            {
                "param": p.name,
                "description": p.description,
                "basis": p.basis,
                "claims": p.claims,
                "ev_low": float(lo),
                "ev_high": float(hi),
                "settings": settings,
                "swing": swing,
                "swing_kind": "absolute" if absolute else "ratio",
            }
        )
    out.sort(key=lambda r: -r["swing"])
    return out


def confidence(summary: dict, crux_rows: list[dict]) -> dict:
    """D12: computed confidence, with its inputs."""

    def weight(r):  # log of a ratio swing; absolute swings (net, D17) are used as they are
        if r.get("swing_kind") == "absolute":
            return r["swing"]
        return np.log(r["swing"]) if np.isfinite(r["swing"]) else 50.0

    logs = {r["param"]: weight(r) for r in crux_rows}
    total = sum(logs.values()) or 1.0
    weak_bases = ("expert-judgement", "speculation")
    weak = sum(logs[r["param"]] for r in crux_rows if r["basis"] in weak_bases) / total
    measured = sum(logs[r["param"]] for r in crux_rows if r["basis"] == "measured") / total
    if summary["tail_dominated"] or weak > 0.5:
        level = "low"
    elif measured > 0.5:
        level = "high"
    else:
        level = "medium"
    return {
        "level": level,
        "tail_dominated": summary["tail_dominated"],
        "top5_share_of_ev": summary["top5_share_of_ev"],
        "swing_share_expert_or_speculation": weak,
        "swing_share_measured": measured,
    }


def variants(
    model: Model, counterfactual: str, n: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED
) -> list[dict]:
    """Result per variant of each categorical parameter (one source each, D14)."""
    out = []
    for p in model.params:
        if not p.categorical:
            continue
        for i, cat in enumerate(p.categories):
            comps, _ = model.run_components(counterfactual, n, seed, {p.name: i})
            s = summarise_model(model, comps)
            s.pop("components", None)
            out.append({"param": p.name, "variant": cat, **s})
    return out


def breakdown(
    model: Model, counterfactual: str, n: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED
) -> dict | None:
    """Share of the expected value by access mode, with a 90% interval across draws."""
    mod = model.module
    if not hasattr(mod, "access_shares") or model.is_net:  # net models: per component, later
        return None
    y, x = model.run(counterfactual, n, seed)
    shares = mod.access_shares(x, counterfactual)
    rows = []
    for k, label in mod.ACCESS_MODES.items():
        s = np.asarray(shares[k], dtype=float)
        ev_share = float((y * s).sum() / y.sum()) if y.sum() > 0 else 0.0
        q = np.quantile(s, [0.05, 0.95])
        rows.append(
            {
                "mode": k,
                "label": label,
                "share_of_ev": ev_share,
                "share_p05": float(q[0]),
                "share_p95": float(q[1]),
            }
        )
    return {"counterfactual": counterfactual, "rows": rows}
