"""Monte Carlo engine: declared parameters, simulation, summaries (VISION.md §3–4; D11, D12, D14).

A model module (models/<risk_id>.py) defines:
    RISK: str
    TITLE: str
    WINDOW: tuple[int, int]          years summed, inclusive
    COUNTERFACTUALS: dict[str, str]  supported counterfactual -> plain-language label
    NOT_MODELLED: dict[str, str]     counterfactual -> reason it is not modelled yet
    def params(ds) -> list[Param]    parameters fitted to claims
    def simulate(x, counterfactual) -> np.ndarray   DALYs per draw over WINDOW
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

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

    @property
    def risk(self) -> str:
        return self.module.RISK

    @classmethod
    def load(cls, ds, risk: str) -> Model:
        path = ds.root / "models" / f"{risk.replace('-', '_')}.py"
        if not path.exists():
            raise FileNotFoundError(f"no model for {risk} at {path}")
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
        return cls(mod, params, path)

    def draw(self, n: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED,
             fixed: dict[str, float | np.ndarray] | None = None) -> dict[str, np.ndarray]:
        rng = np.random.default_rng(seed)
        x = {p.name: p.sample(rng, n) for p in self.params}  # always draw all: stable streams
        for k, v in (fixed or {}).items():
            if k not in x:
                raise KeyError(f"unknown parameter {k}")
            x[k] = np.broadcast_to(np.asarray(v, dtype=x[k].dtype), (n,)).copy()
        return x

    def run(self, counterfactual: str, n: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED,
            fixed: dict | None = None) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        if counterfactual not in self.module.COUNTERFACTUALS:
            raise ValueError(f"{self.risk}: counterfactual {counterfactual} not modelled")
        x = self.draw(n, seed, fixed)
        return np.asarray(self.module.simulate(x, counterfactual), dtype=float), x


# ---- summaries ----------------------------------------------------------------

def summarise(y: np.ndarray) -> dict:
    y = np.asarray(y, dtype=float)
    ev = float(y.mean())
    q = np.quantile(y, [0.05, 0.5, 0.95])
    top = np.sort(y)[int(0.95 * len(y)):]
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


def cruxes(model: Model, counterfactual: str, n: int = 20_000, seed: int = DEFAULT_SEED) -> list[dict]:
    """One-at-a-time swing of each parameter, 5th → 95th percentile (D12).

    Categorical parameters swing between their lowest- and highest-EV variant.
    """
    base = model.draw(n, seed)
    out = []
    for p in model.params:
        if p.categorical:
            evs = {cat: model.run(counterfactual, n, seed, {p.name: i})[0].mean()
                   for i, cat in enumerate(p.categories)}
            lo_k, hi_k = min(evs, key=evs.get), max(evs, key=evs.get)
            lo, hi = evs[lo_k], evs[hi_k]
            settings = {"low": lo_k, "high": hi_k}
        else:
            v05, v95 = np.quantile(base[p.name], [0.05, 0.95])
            lo = model.run(counterfactual, n, seed, {p.name: v05})[0].mean()
            hi = model.run(counterfactual, n, seed, {p.name: v95})[0].mean()
            settings = {"low": float(v05), "high": float(v95)}
        a, b = sorted([lo, hi])
        swing = float(b / a) if a > 0 else float("inf")
        out.append({"param": p.name, "description": p.description, "basis": p.basis,
                    "claims": p.claims, "ev_low": float(lo), "ev_high": float(hi),
                    "settings": settings, "swing": swing})
    out.sort(key=lambda r: -r["swing"])
    return out


def confidence(summary: dict, crux_rows: list[dict]) -> dict:
    """D12: computed confidence, with its inputs."""
    logs = {r["param"]: np.log(r["swing"]) if np.isfinite(r["swing"]) else 50.0 for r in crux_rows}
    total = sum(logs.values()) or 1.0
    weak = sum(v for r, v in zip(crux_rows, logs.values())
               if r["basis"] in ("expert-judgement", "speculation")) / total
    measured = sum(v for r, v in zip(crux_rows, logs.values()) if r["basis"] == "measured") / total
    if summary["tail_dominated"] or weak > 0.5:
        level = "low"
    elif measured > 0.5:
        level = "high"
    else:
        level = "medium"
    return {"level": level, "tail_dominated": summary["tail_dominated"],
            "top5_share_of_ev": summary["top5_share_of_ev"],
            "swing_share_expert_or_speculation": weak, "swing_share_measured": measured}
