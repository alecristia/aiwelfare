# Roadmap

What we are working on **now**, and what we will **circle back to**. Update this file when a strand starts, finishes or changes status. Decisions themselves stay in `docs/decisions.md`; this file only tracks work.

Last updated: 2026-11-27 (end of the session that ran milestone 1, the prior-work review and the baselines).

---

## The cards

Nine cards, defined from the top down (D2, amended 2026-11-27). The pathways listed under each card are **components of its model**, not separate cards. Harms and benefits of the same technology share a card and are shown as a net effect.

| Group (D7) | Card | Components | Status |
|---|---|---|---|
| Malicious use | **Biological misuse** | AI-assisted design or synthesis of pathogens | Mock card built; real card next |
| | **Cyberattacks on health and critical infrastructure** | AI-enabled cyberattacks, ransomware on hospitals; AI malfunctions in critical infrastructure | Not started |
| | **Conflict and power concentration** | Autonomous weapons and AI targeting; AI-driven escalation, incl. nuclear; AI-enabled autocratisation and repression; mass political deepfakes | Not started. The card must say that the measured health effects of autocratisation build up over about ten years (Wigley et al. 2020), so most of them fall after 2031 |
| Malfunctions and everyday use | **Clinical AI (net)** | Benefit: diagnostics and monitoring. Harm: errors in clinical care, hallucinations entering clinical guidelines, consumer chatbot medical-advice errors, biased clinical algorithms | Not started; first in line |
| | **Chatbots and mental health (net)** | Harm: worse mental health from heavy use. Benefit: therapy chatbots | Not started |
| | **Autonomous vehicles (net)** | Road injuries averted and caused | Not started |
| Systemic | **Environmental footprint** | Air pollution from data-centre electricity (more components possible, e.g. water) | US-only version built; needs a global estimate before it can be shown |
| | **Labour displacement** | Job loss → mortality | Not started |
| Benefits | **Faster biomedical research** | AI-accelerated drug discovery and research | Not started; evidence within 2026–2031 is thin (prior-work review) |

### Not covered: scope cuts

The repo does not estimate these for now. Every output that lists the cards should list them too, so readers see what is and is not covered.

| Not covered | Why |
|---|---|
| **Loss of control** (misaligned autonomous AI) | Within 2026–2031 it is almost entirely a tail risk. The *Lancet* Commission treats it as one of three AI pathways, so it is the most important cut for readers deciding whether to work in AI safety |
| **Health misinformation** (e.g. vaccine misinformation at scale) | Cut to keep the number of cards manageable; evidence not yet searched |
| **Disruption of financial institutions** | Reaches health only indirectly, through recessions |

Harms that fall inside a card but outside DALYs (e.g. loss of rights under autocracy) are listed on each card under "What this number leaves out".

---

## Task briefs (launch each in its own session)

| Brief | Use |
|---|---|
| `docs/tasks/build-a-card.md` | Build one card end to end. Launch once per card: "Read `docs/tasks/build-a-card.md` and build the card **<name>**." |
| `docs/tasks/website-and-explorer.md` | Build the static site and parameter explorer |
| `docs/tasks/prior-work-search.md` | The literature search (done; kept for reference and for follow-up rounds) |

---

## Done

- **Milestone 1 (2026-11-27):** schemas, `aiwelfare` package and CLI (every command, all with `--json`), Monte Carlo engine, card builder with quantile dotplots, tests. Two demonstration cards: data-centre air pollution (real data, US only, built through `datalad run`) and bio misuse (invented data, `mock/`).
- **Prior-work search, rounds 1–5** (PRs #1, #2): catalogue, search log and summary in `related_work/` and `docs/related-work.md`. The *Lancet* Commission main text and appendix are registered as sources.
- **Card list:** nine cards defined top-down, and three scope cuts (D2, amended 2026-11-27).
- **Baselines (D16):** six global GBD 2023 risk factors in `baselines/`, all at level 2 of the GBD risk hierarchy (checked against GBD's published naming: their level-3 children, e.g. particulate matter pollution and smoking, carry different names; the two metabolic risks are the same at levels 2 and 3), from the GBD subdataset `baselines/gbd/` (every file annexed, never pushed). Cards show their size against each one ("about 1/35,000 of air pollution"). Global deaths and DALYs from ambient particulate matter are recorded as claims for the environmental-footprint card.
- **VISION.md:** global scope (scope decision 5) and "estimates do not add up" (modelling decision 7).

---

## Now

### 1. Clinical AI (net)
The first real benefit, so the overview does not show harms alone. Launch with `docs/tasks/build-a-card.md`.
**Prerequisite:** it is the first net card, and the engine and card format cannot yet show harm and benefit components or a net that may be negative (D5 dotplots use a log axis). The session first proposes a design, the maintainer agrees it, and it is recorded as a decision before the card is built (see the brief).

### 2. Biological misuse, real
Replaces the mock card, starting from Righetti's model (GovAI 2025). The mock files stay in `mock/` as the format demonstration.

### 3. Website and explorer (D6, D8)
With baselines and three cards (clinical AI, bio misuse, and the global environmental footprint if ready), the overview has a benefit, a tail-dominated risk and a steady harm, enough to test the forest plot, sliders and counterfactual switch on real data. Static site generated from `results/` (D8); nothing computed that the CLI cannot reproduce (D10). Brief: `docs/tasks/website-and-explorer.md`. **Built (branch `website-explorer`, not yet merged or published):** `aiwelfare build site` writes `site/` (real, global cards only) and `site/demo/` (adds the mock card, with D13 banners); explorer on Pyodide (D8, amended). The canonical chart has no rows yet because no real card is global; it shows the six baselines. Still open:
- **Net cards (D17):** the forest plot's axis is log-only. Once net cards land, it needs signed values, and `explorer.summarise_run` should use the engine's net summary.
- **Maintainer to settle (D7, deferred):** colours, layout, row counts, from the screenshots.
- **Not built:** D7's group summary rows and expand/collapse (no group has more than one card yet), and the access-mode filter (its meaning on the overview needs a decision). The tail-dominated and close-to-ML filters are built.
- **Publishing:** GitHub Pages and a CI build need the maintainer's go-ahead (new external services).

### 4. Remaining cards, in this order (one session each)
1. Chatbots and mental health (net)
2. Cyberattacks on health and critical infrastructure
3. Autonomous vehicles (net)
4. Labour displacement
5. Conflict and power concentration
6. Environmental footprint, global
7. Faster biomedical research

The order mixes how much evidence is ready with having harms and benefits early. It is not a judgement of importance.

---

## Circle back to

### Literature review (prior-work search)
Rounds 1–5 are done and merged (PRs #1, #2). Open items:
- Read the *Lancet* Commission appendix, section 3.11 (AI method). Registered on 2026-11-27 as `lancet-2026-commission-21-health-appendix`; not yet read in full.
- Extract Saeri et al.'s subdomain figures (power centralisation, weapons).
- Retry the items under "Not accessed" in `docs/related-work.md`.
- Targeted searches each card will need: therapy chatbots, global data-centre electricity and health.
- Known blind spots: non-English literature.

### D3: map the MIT AI Risk Repository to the cards
Every entry goes to a card, a card's "leaves out" list, or the scope cuts above. Unmapped entries are coverage gaps.

### Environmental footprint: from US to global
The built card covers the contiguous US only, and is not shown until a global estimate exists. Its other known gaps (the `open-only` counterfactual, the access-mode breakdown, a source for energy-efficient ML) are listed on the card. GBD 2023 deaths and DALYs attributable to ambient particulate matter (global) are now claims 036–037: about 25 DALYs per death globally, against the US model's assumed 8–15. The global card should use the GBD ratio; the US model keeps its assumption, since a global ratio does not fit a US population.

### Overview chart details (D7)
Row counts, colours and layout: deferred by D7 until real estimates exist.
