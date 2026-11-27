"""Clinical AI (net): AI early warning in hospitals (benefit) against unsafe chatbot medical
advice and errors from AI medical devices (harms). A net card (D17).

Model (per simulated future, per year t in WINDOW; every component is a magnitude in DALYs):

    monitoring (benefit)
        deaths averted(t) = global sepsis-related deaths
                            × share of them under AI early warning, counted(t)
                            × relative mortality reduction (one study variant per future, D14)
                            × share of that effect retained outside developer sites
        DALYs             = Σ_t deaths averted(t) × DALYs per death

    chatbot advice (harm)
        harms(t) = weekly chatbot health users, counted(t)
                   × clinical-advice conversations per user per year
                   × unsafe-answer rate × P(an unsafe answer causes a harm)
                   × share of that harm in excess of people's usual sources
        DALYs    = Σ_t harms(t) × DALYs per harm

    device errors (harm)
        events(t) = FDA-reported injuries or deaths per year × AI-related share
                    × under-reporting × world/US ratio × use growth, counted(t)
        DALYs     = Σ_t injuries(t) × DALYs per injury + deaths(t) × DALYs per death

Counterfactuals (VISION.md, Modelling decisions §1):
    no-ai        all use counts
    frozen-2026  only use above its 2026 level counts (as on the air-pollution card)
    open-only    not modelled yet (see NOT_MODELLED)

Components agreed with the maintainer on 2026-11-27. Diagnostics and screening,
hallucinations entering clinical guidelines and biased clinical algorithms are not
modelled yet (see the card's limitations). Every number comes from a claim in
claims/clinical-ai/; fitting choices are stated in each Param.fit.
"""

import numpy as np

from aiwelfare.engine import Z90, Param, choice, claim_value, fixed, lognormal_ci, uniform

RISK = "clinical-ai"
TITLE = "Clinical AI (net)"
GEOGRAPHY = "global"
WINDOW = (2027, 2031)  # "late 2026 to late 2031": five annual steps
BASE_YEAR = 2026
COUNTERFACTUALS = {
    "no-ai": "No modern AI",
    "frozen-2026": "AI frozen at 2026 levels",
}
NOT_MODELLED = {
    "open-only": (
        "Needs the share of chatbot health use served by frontier versus open-weight or older "
        "models; no source read yet. Hospital early-warning tools mostly do not use frontier "
        "models at all."
    ),
}
BREAKDOWN_NOT_MODELLED = (
    "Access-mode breakdowns are not yet supported for net cards (D17), and no source read yet "
    "splits chatbot health use by model or deployment."
)
COMPONENTS = {
    "monitoring": ("benefit", "AI early warning in hospitals"),
    "chatbot-advice": ("harm", "unsafe chatbot medical advice, beyond usual sources"),
    "device-errors": ("harm", "errors from AI medical devices"),
}
C = "clinical-ai-{:03d}".format

STUDIES = [
    "COMPOSER sepsis alert (Boussina et al.)",
    "CHARTwatch early warning (Verma et al.)",
    "Meta-analysis of five early-warning studies (Yuan et al.)",
]


def _iv(value):
    i = value["interval"]
    return i["low"], i["high"]


def params(ds):
    v = lambda n: claim_value(ds, C(n))  # noqa: E731

    composer = v(1)["interval"]
    composer_expected = v(2)["interval"]["mid"]

    return [
        # ---- monitoring ----
        Param(
            "study",
            "Which study's mortality effect of AI early warning this future uses",
            [C(1), C(3), C(5)],
            choice(3),
            "Equal-weight mixture of the three estimates (D14). They overlap: the meta-analysis "
            "includes CHARTwatch.",
            categories=STUDIES,
        ),
        Param(
            "reduction_composer",
            "Relative fall in in-hospital sepsis mortality with COMPOSER",
            [C(1), C(2)],
            lambda rng, n: (
                rng.normal(
                    composer["mid"], (composer["high"] - composer["low"]) / (2 * 1.959964), n
                )
                / composer_expected
            ),
            "Normal through the 95% CI of the absolute reduction (percentage points), divided by "
            "the expected mortality without COMPOSER (11.4%).",
        ),
        Param(
            "rr_chartwatch",
            "Relative risk of non-palliative death with CHARTwatch",
            [C(3)],
            lognormal_ci(*_iv(v(3))),
            "Lognormal through the 95% CI of the adjusted relative risk (primary analysis). The "
            "difference-in-differences estimate (claim 004) is wider and is not used.",
        ),
        Param(
            "or_pooled",
            "Pooled odds ratio of in-hospital death with ML early warning",
            [C(5)],
            lognormal_ci(*_iv(v(5))),
            "Lognormal through the 95% CI of the random-effects odds ratio; read as a relative "
            "risk, since in-hospital death is uncommon in these cohorts.",
        ),
        Param(
            "effect_transfer",
            "Share of the developer-site effect retained in typical deployments",
            [C(12)],
            uniform(*_iv(v(12))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "sepsis_deaths",
            "Global sepsis-related deaths per year",
            [C(7)],
            lognormal_ci(*_iv(v(7))),
            "Lognormal through the 95% uncertainty interval for 2017, held constant over "
            "2027–2031 (age-standardised sepsis mortality has been falling).",
        ),
        Param(
            "coverage_2026",
            "Share of global sepsis deaths under AI early warning, 2026",
            [C(10)],
            lognormal_ci(*_iv(v(10)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        Param(
            "coverage_2031",
            "Share of global sepsis deaths under AI early warning, 2031",
            [C(11)],
            lognormal_ci(*_iv(v(11)), z=Z90),
            "Lognormal through the assumption's range (90%); the model uses the larger of this "
            "and the 2026 draw, so coverage never falls. Linear in time from 2026.",
        ),
        Param(
            "dalys_per_monitored_death",
            "DALYs per death averted by early warning",
            [C(13)],
            uniform(*_iv(v(13))),
            "Uniform over the assumption's range.",
        ),
        # ---- chatbot advice ----
        Param(
            "other_providers",
            "Chatbot health users across all providers ÷ ChatGPT's",
            [C(22)],
            uniform(*_iv(v(22))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "chatbot_growth_2031",
            "Weekly chatbot health users in 2031 ÷ 2026",
            [C(23)],
            uniform(*_iv(v(23))),
            "Uniform over the assumption's range; linear in time from 2026.",
        ),
        Param(
            "conversations_per_user",
            "Clinical-advice conversations per weekly health user per year",
            [C(24)],
            lognormal_ci(*_iv(v(24)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        Param(
            "unsafe_rate",
            "Share of chatbot answers that could harm if acted on",
            [C(16)],
            uniform(*_iv(v(16))),
            "Uniform across the range of the four chatbots tested (late-2024 versions); the "
            "rate in use depends on the market share of each, which no source gives.",
        ),
        Param(
            "harm_probability",
            "P(an unsafe answer is acted on and causes a harm)",
            [C(25)],
            lognormal_ci(*_iv(v(25)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        Param(
            "excess_share",
            "Share of that harm beyond what people's usual sources would cause",
            [C(27)],
            uniform(*_iv(v(27))),
            "Uniform over the assumption's range. Its rationale draws on Bean et al. "
            "(claims 018, 019), which compare decisions, not health outcomes.",
        ),
        Param(
            "dalys_per_chatbot_harm",
            "DALYs per harm from unsafe chatbot advice",
            [C(26)],
            lognormal_ci(*_iv(v(26)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        # ---- device errors ----
        Param(
            "ai_related_share",
            "Share of AI-device safety reports in which AI plausibly contributed",
            [C(31), C(32)],
            uniform(v(31)["point"], v(31)["point"] + v(32)["point"]),
            "Uniform from the share judged potentially AI-related (25.2%) to that share plus "
            "every report that could not be judged (34.5%).",
        ),
        Param(
            "reporting_window",
            "Years over which reported AI-device harms accrued",
            [C(34)],
            uniform(*_iv(v(34))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "underreporting",
            "Actual AI-device harms per harm reported",
            [C(35)],
            lognormal_ci(*_iv(v(35)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        Param(
            "world_to_us",
            "Global AI-device harm ÷ US",
            [C(36)],
            uniform(*_iv(v(36))),
            "Uniform over the assumption's range.",
        ),
        Param(
            "device_growth_2031",
            "AI-device use in 2031 ÷ the rate behind the reported harms",
            [C(37)],
            uniform(*_iv(v(37))),
            "Uniform over the assumption's range; the reported rate is treated as the 2026 rate, "
            "linear in time to 2031.",
        ),
        Param(
            "dalys_per_device_injury",
            "DALYs per AI-device injury",
            [C(38)],
            lognormal_ci(*_iv(v(38)), z=Z90),
            "Lognormal through the assumption's range, read as a 90% range.",
        ),
        Param(
            "dalys_per_device_death",
            "DALYs per AI-device death",
            [C(39)],
            uniform(*_iv(v(39))),
            "Uniform over the assumption's range.",
        ),
        # ---- fixed inputs ----
        Param(
            "chatgpt_users",
            "ChatGPT regular (weekly) users",
            [C(15)],
            fixed(v(15)["point"]),
            "Taken as stated ('more than 800 million').",
            fixed=True,
        ),
        Param(
            "chatgpt_health_share",
            "Share of ChatGPT users prompting about healthcare weekly",
            [C(14)],
            fixed(v(14)["point"]),
            "Taken as stated ('one in four').",
            fixed=True,
        ),
        Param(
            "reported_injuries",
            "Injuries reported to the FDA for AI/ML devices (cumulative)",
            [C(28)],
            fixed(v(28)["point"]),
            "Taken as stated.",
            fixed=True,
        ),
        Param(
            "reported_deaths",
            "Deaths reported to the FDA for AI/ML devices (cumulative)",
            [C(29)],
            fixed(v(29)["point"]),
            "Taken as stated.",
            fixed=True,
        ),
    ]


def _years():
    return np.arange(WINDOW[0], WINDOW[1] + 1)


def _ramp(start, end, years):
    """Linear from `start` in BASE_YEAR to `end` in 2031; shape (draws, years)."""
    frac = (years - BASE_YEAR) / (2031 - BASE_YEAR)
    return start[:, None] + (end - start)[:, None] * frac[None, :]


def _counted(level, base, counterfactual):
    if counterfactual == "no-ai":
        return level
    if counterfactual == "frozen-2026":
        return np.maximum(level - base[:, None], 0.0)
    raise ValueError(counterfactual)


def relative_reduction(x):
    """Relative fall in mortality, per draw, from the chosen study; floored at zero."""
    r = np.stack(
        [x["reduction_composer"], 1 - x["rr_chartwatch"], 1 - x["or_pooled"]],
        axis=1,
    )
    chosen = r[np.arange(len(r)), x["study"].astype(int)]
    return np.maximum(chosen, 0.0)  # a component is a magnitude (D17); harm here is not modelled


def monitoring(x, counterfactual):
    years = _years()
    c26 = x["coverage_2026"]
    c31 = np.maximum(x["coverage_2031"], c26)
    covered = _counted(_ramp(c26, c31, years), c26, counterfactual)
    deaths = (
        x["sepsis_deaths"][:, None]
        * covered
        * (relative_reduction(x) * x["effect_transfer"])[:, None]
    )
    return deaths.sum(axis=1) * x["dalys_per_monitored_death"]


def chatbot_advice(x, counterfactual):
    years = _years()
    u26 = x["chatgpt_users"] * x["chatgpt_health_share"] * x["other_providers"]
    users = _counted(_ramp(u26, u26 * x["chatbot_growth_2031"], years), u26, counterfactual)
    per_user = (
        x["conversations_per_user"]
        * x["unsafe_rate"]
        * x["harm_probability"]
        * x["excess_share"]
        * x["dalys_per_chatbot_harm"]
    )
    return users.sum(axis=1) * per_user


def device_errors(x, counterfactual):
    years = _years()
    one = np.ones_like(x["device_growth_2031"])
    use = _counted(_ramp(one, x["device_growth_2031"], years), one, counterfactual).sum(axis=1)
    scale = x["ai_related_share"] * x["underreporting"] * x["world_to_us"] / x["reporting_window"]
    injuries = x["reported_injuries"] * scale * use
    deaths = x["reported_deaths"] * scale * use
    return injuries * x["dalys_per_device_injury"] + deaths * x["dalys_per_device_death"]


def simulate(x, counterfactual):
    return {
        "monitoring": monitoring(x, counterfactual),
        "chatbot-advice": chatbot_advice(x, counterfactual),
        "device-errors": device_errors(x, counterfactual),
    }
