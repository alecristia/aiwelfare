"""Data-centre air pollution: deaths from electricity generated for AI in US data centres.

Model (per simulated future, per year t in WINDOW):

    AI electricity(t) = total US data-centre electricity(t) − non-AI electricity(t)
    deaths(t)         = AI electricity counted under the counterfactual(t)
                        × deaths per TWh (one study variant per future, D14)
                        × grid trend(t)
    DALYs             = Σ_t deaths(t) × DALYs per death

Counterfactuals (VISION.md, Modelling decisions §1):
    no-ai        all AI electricity counts
    frozen-2026  only AI electricity above its 2026 level counts
    open-only    not modelled yet (see NOT_MODELLED)

Scope: contiguous United States only. Every number comes from a claim in
claims/data-centre-air-pollution/; fitting choices are stated in each Param.fit.
"""

import numpy as np

from aiwelfare.engine import Param, choice, claim_value, fixed, lognormal_ci, uniform

RISK = "data-centre-air-pollution"
TITLE = "Air pollution from electricity for AI data centres"
GEOGRAPHY = "contiguous United States only"
WINDOW = (2027, 2031)  # "late 2026 to late 2031": five annual steps
STUDY_YEAR = 2023
COUNTERFACTUALS = {
    "no-ai": "No modern AI",
    "frozen-2026": "AI frozen at 2026 levels",
}
NOT_MODELLED = {
    "open-only": (
        "Needs the share of AI electricity driven by frontier versus open-weight or older "
        "models; no source read yet."
    ),
}
BREAKDOWN_NOT_MODELLED = (
    "No source read yet splits AI data-centre electricity by access mode "
    "(open-weight, API frontier, locally-run frontier)."
)
C = "data-centre-air-pollution-{:03d}".format

STUDIES = ["COBRA (Han et al.)", "GEOS-Chem (Chen et al.)", "AP4 (Muller)"]
AI_SHARE_SOURCES = ["LBNL server data (Shehabi et al.)", "IEA via Muller"]


def params(ds):
    v = lambda n: claim_value(ds, C(n))  # noqa: E731

    # Deaths per TWh, one variant per study.
    han = v(1)["interval"]
    han_twh = v(2)["point"]
    chen = v(9)["interval"]
    chen_twh = v(10)["point"]
    mul_twh = v(13)["point"]
    mul_lo, mul_hi = v(14)["point"], v(15)["point"]
    vsl = v(16)["point"]
    backup = v(7)["interval"]

    # Electricity.
    e23 = v(19)["point"]
    e28 = v(20)["interval"]
    ai23_lbnl = v(21)["point"] / v(22)["point"]
    ai23_iea = v(18)["point"]

    return [
        Param(
            "study",
            "Which study's deaths-per-TWh estimate this future uses",
            [C(1), C(9), C(14)],
            choice(3),
            "Equal-weight mixture of the three independent models (D14).",
            categories=STUDIES,
        ),
        Param(
            "rate_cobra",
            "Deaths per TWh, COBRA (Han et al.), incl. backup generators",
            [C(1), C(2), C(8)],
            uniform(han["low"] / han_twh, han["high"] / han_twh),
            "Uniform between the low and high CRF results for 2023 divided by 2023 TWh; "
            "the two CRFs are alternatives, not interval bounds.",
        ),
        Param(
            "rate_geoschem",
            "Deaths per TWh, GEOS-Chem (Chen et al.), grid only",
            [C(9), C(10)],
            lognormal_ci(chen["low"] / chen_twh, chen["high"] / chen_twh),
            "Lognormal through the 95% CI for 2023 divided by 2023 generation; the CI covers "
            "CRF uncertainty only, so this understates the spread.",
        ),
        Param(
            "rate_ap4",
            "Deaths per TWh, AP4 (Muller), grid only",
            [C(13), C(14), C(15), C(16), C(17)],
            uniform(mul_lo / vsl / mul_twh, mul_hi / vsl / mul_twh),
            "Local-air-pollution damages ÷ VSL ÷ TWh (AP4 counts mortality only); uniform "
            "between the default and high dose-response runs. Study year 2025, treated as 2023.",
        ),
        Param(
            "rate_backup",
            "Deaths per TWh from backup generators (added to grid-only studies)",
            [C(7)],
            uniform(backup["low"] / han_twh, backup["high"] / han_twh),
            "Han et al.'s scope-1 deaths (10% of permitted emissions) per 2023 TWh, uniform "
            "between CRF results. Added to GEOS-Chem and AP4, which exclude backup generators.",
        ),
        Param(
            "e2028",
            "Total US data-centre electricity in 2028 (TWh)",
            [C(20)],
            uniform(e28["low"], e28["high"]),
            "Uniform across LBNL's 2028 scenario range (no likelihood is given for the scenarios).",
        ),
        Param(
            "post_2028_growth_ratio",
            "Growth after 2028 as a fraction of 2023–28 growth",
            [C(27)],
            uniform(*_lh(v(27))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "ai_share_source",
            "Which estimate of AI's share of 2023 electricity this future uses",
            [C(18), C(21), C(22)],
            choice(2),
            "Equal-weight mixture of the two estimates (D14).",
            categories=AI_SHARE_SOURCES,
        ),
        Param(
            "conventional_growth",
            "Annual growth of non-AI data-centre electricity",
            [C(28), C(23)],
            uniform(*_lh(v(28))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "grid_trend_2031",
            "Deaths per TWh in 2031 relative to the study year",
            [C(26)],
            uniform(*_lh(v(26))),
            "Uniform over the assumption's range; linear in time from 1.0 in 2023.",
        ),
        Param(
            "dalys_per_death",
            "DALYs per premature death",
            [C(25)],
            uniform(*_lh(v(25))),
            "Uniform over the placeholder assumption's range.",
        ),
        Param(
            "e2023",
            "Total US data-centre electricity in 2023 (TWh)",
            [C(19)],
            fixed(e23),
            "Taken as stated.",
            fixed=True,
        ),
        Param(
            "ai_share_lbnl",
            "AI share of 2023 data-centre electricity, LBNL variant",
            [C(21), C(22)],
            fixed(ai23_lbnl),
            "AI-server ÷ all-server electricity; assumes cooling and other overheads scale "
            "with server load.",
            fixed=True,
        ),
        Param(
            "ai_share_iea",
            "AI share of 2023 data-centre electricity, IEA variant",
            [C(18)],
            fixed(ai23_iea),
            "Taken as stated (global share, applied to the US).",
            fixed=True,
        ),
    ]


def _lh(value):
    i = value["interval"]
    return i["low"], i["high"]


def electricity(x, years):
    """Total and AI electricity (TWh), arrays of shape (draws, years)."""
    e23 = x["e2023"]
    r = (x["e2028"] / e23) ** (1 / 5) - 1  # 2023–2028 annual growth
    r_post = r * x["post_2028_growth_ratio"]
    t = np.asarray(years)[None, :]
    pre = e23[:, None] * (1 + r[:, None]) ** np.minimum(t - 2023, 5)
    total = pre * (1 + r_post[:, None]) ** np.maximum(t - 2028, 0)
    share = np.where(x["ai_share_source"].astype(int) == 0, x["ai_share_lbnl"], x["ai_share_iea"])
    non_ai = (e23 * (1 - share))[:, None] * (1 + x["conventional_growth"][:, None]) ** (t - 2023)
    ai = np.maximum(total - non_ai, 0.0)
    return total, ai


def deaths_per_twh(x):
    rates = np.stack(
        [x["rate_cobra"], x["rate_geoschem"] + x["rate_backup"], x["rate_ap4"] + x["rate_backup"]],
        axis=1,
    )
    return rates[np.arange(len(rates)), x["study"].astype(int)]


def simulate(x, counterfactual):
    years = np.arange(WINDOW[0], WINDOW[1] + 1)
    _, ai = electricity(x, np.concatenate([[2026], years]))
    ai_2026, ai_window = ai[:, :1], ai[:, 1:]
    if counterfactual == "no-ai":
        counted = ai_window
    elif counterfactual == "frozen-2026":
        counted = np.maximum(ai_window - ai_2026, 0.0)
    else:
        raise ValueError(counterfactual)
    frac = (years - STUDY_YEAR) / (2031 - STUDY_YEAR)
    trend = 1 + (x["grid_trend_2031"][:, None] - 1) * frac[None, :]
    deaths = counted * deaths_per_twh(x)[:, None] * trend
    return deaths.sum(axis=1) * x["dalys_per_death"]


def deaths(x, counterfactual):
    """Deaths over the window (for display alongside DALYs)."""
    return simulate(x, counterfactual) / x["dalys_per_death"]
