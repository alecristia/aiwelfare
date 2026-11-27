"""MOCK MODEL: AI-assisted biological misuse. ALL INPUTS ARE INVENTED (D13).

It exists to exercise the card format end to end, with the features real risks will
need: a zero mass (nothing happens), a tail-dominated result, evidence-type variants
(D14), all three counterfactuals, and an access-mode breakdown.

Model (per simulated future):
    outbreak happens   with probability p (one evidence-type variant per future, D14)
    DALYs if it does   lognormal severity
    counterfactual     no-ai: all of it · frozen-2026: the share from post-2026 capability
                       open-only: the share that remains if only open-weight models advance
"""

import numpy as np

from aiwelfare.engine import Param, choice, claim_value, lognormal_ci, uniform

RISK = "bio-misuse"
TITLE = "AI-assisted biological misuse (MOCK)"
GEOGRAPHY = "global"
WINDOW = (2027, 2031)
STOCHASTIC = True
COUNTERFACTUALS = {
    "no-ai": "No modern AI",
    "frozen-2026": "AI frozen at 2026 levels",
    "open-only": "Only open-weight / older models advance",
}
NOT_MODELLED: dict = {}
ACCESS_MODES = {
    "open-weight": "Open-weight models",
    "api": "API-served frontier models",
    "local-frontier": "Frontier models run locally / on-premises",
}
C = "bio-misuse-{:03d}".format
EVIDENCE = ["expert forecast", "lab evaluation", "independent evaluation"]


def params(ds):
    v = lambda n: claim_value(ds, C(n))["interval"]  # noqa: E731
    p = [v(1), v(2), v(3)]
    return [
        Param(
            "evidence",
            "Which evidence type sets the outbreak probability in this future",
            [C(1), C(2), C(3)],
            choice(3),
            "Equal weight per evidence type (D14).",
            categories=EVIDENCE,
        ),
        Param(
            "p_forecast",
            "P(outbreak), expert-forecast variant",
            [C(1)],
            lognormal_ci(p[0]["low"], p[0]["high"], 1.644854),
            "Lognormal through the 90% interval.",
        ),
        Param(
            "p_lab",
            "P(outbreak), lab-evaluation variant",
            [C(2)],
            lognormal_ci(p[1]["low"], p[1]["high"], 1.644854),
            "Lognormal through the 90% interval.",
        ),
        Param(
            "p_independent",
            "P(outbreak), independent-evaluation variant",
            [C(3)],
            lognormal_ci(p[2]["low"], p[2]["high"], 1.644854),
            "Lognormal through the 90% interval.",
        ),
        Param(
            "severity",
            "DALYs if an outbreak happens",
            [C(5)],
            lognormal_ci(v(5)["low"], v(5)["high"], 1.644854),
            "Lognormal through the 90% interval.",
        ),
        Param(
            "post_2026_share",
            "Share of the risk from capabilities after 2026",
            [C(6)],
            uniform(v(6)["low"], v(6)["high"]),
            "Uniform over the interval.",
        ),
        Param(
            "open_only_share",
            "Share that remains if only open-weight models advance",
            [C(7)],
            uniform(v(7)["low"], v(7)["high"]),
            "Uniform over the interval.",
        ),
        Param(
            "share_open_weight",
            "Share of the risk via open-weight models",
            [C(8)],
            uniform(v(8)["low"], v(8)["high"]),
            "Uniform over the interval.",
        ),
        Param(
            "share_local_frontier",
            "Share via locally-run frontier models",
            [C(9)],
            uniform(v(9)["low"], v(9)["high"]),
            "Uniform over the assumption's range.",
        ),
    ]


def probability(x):
    ps = np.stack([x["p_forecast"], x["p_lab"], x["p_independent"]], axis=1)
    return np.clip(ps[np.arange(len(ps)), x["evidence"].astype(int)], 0, 1)


def simulate(x, counterfactual, rng):
    u = rng.random(len(x["severity"]))
    harm = np.where(u < probability(x), x["severity"], 0.0)
    if counterfactual == "no-ai":
        return harm
    if counterfactual == "frozen-2026":
        return harm * x["post_2026_share"]
    if counterfactual == "open-only":
        return harm * x["open_only_share"]
    raise ValueError(counterfactual)


def access_shares(x, counterfactual):
    ow = x["share_open_weight"]
    lf = x["share_local_frontier"]
    if counterfactual == "open-only":
        return {
            "open-weight": np.ones_like(ow),
            "api": np.zeros_like(ow),
            "local-frontier": np.zeros_like(ow),
        }
    return {"open-weight": ow, "api": 1 - ow - lf, "local-frontier": lf}
