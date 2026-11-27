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

### 1. Clinical AI (net): in progress, paused 2026-11-27 on branch `clinical-ai-card`
The first real benefit, so the overview does not show harms alone. Resume with `docs/tasks/build-a-card.md`, section "In progress: Clinical AI", which lists exactly what is done and what is next.
- **Done:**
  - the net-card prerequisite (D17, agreed with the maintainer; D5 amended for a mirrored log axis)
  - nine sources registered and read
  - 41 claims, all quotes checked mechanically
  - the model `models/clinical_ai.py`
  - the prose `cards/clinical-ai.md`
- **Not done:**
  - the generated card (`aiwelfare rerun`) and its `datalad rerun` check
  - tests for the card
  - the search-log section
  - `CLAUDE.md` status
  - the pull request
- **Waiting on the maintainer:** papers behind bot checks or paywalls, listed below under "Items for the maintainer to fetch".

### 2. Biological misuse, real
Replaces the mock card, starting from Righetti's model (GovAI 2025). The mock files stay in `mock/` as the format demonstration.

### 3. Website and explorer (D6, D8)
With baselines and three cards (clinical AI, bio misuse, and the global environmental footprint if ready), the overview has a benefit, a tail-dominated risk and a steady harm, enough to test the forest plot, sliders and counterfactual switch on real data. Static site generated from `results/` (D8); nothing computed that the CLI cannot reproduce (D10). Brief: `docs/tasks/website-and-explorer.md`. It can start now against the existing outputs, in parallel with the cards. Once net cards exist, the overview needs an axis that can show signed values.

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

### Items for the maintainer to fetch (bot checks, paywalls)
Agents cannot pass bot checks or paywalls, so these wait for the maintainer to download them; save each into its `sources/<id>/` with `datalad save` and record its URL with `git annex registerurl` (pattern: the *Lancet* sources).
- **Rossetti et al. 2025, *Nature Medicine* 31:1895, CONCERN cluster-randomised trial** (doi:10.1038/s41591-025-03609-7; PMC12818231; medRxiv 10.1101/2024.06.04.24308436). PMC and medRxiv both blocked. The only randomised trial for the clinical-AI monitoring benefit; would add a fourth effect variant and replace part of the `early_warning_effect_transfer` assumption.
- **Bean et al. 2026, *Nature Medicine*, "Reliability of LLMs as medical assistants for the general public"**: the published version of arXiv:2504.18919v1, which the clinical-AI card cites for now.
- **Escobar et al. 2020, *NEJM*, Kaiser Permanente automated early warning (19 hospitals)**: a large independent estimate; today it enters only through the Yuan meta-analysis.
- **Wong et al. 2021, *JAMA Internal Medicine*, external validation of the Epic Sepsis Model**: evidence for how much of the effect transfers beyond developer sites.
- Not tried yet, likely paywalled: **Nong et al. 2025, *Health Affairs***, on US hospitals' use of predictive models (an uptake anchor for the coverage assumptions).

### Clinical AI: components not modelled in v1
Agreed with the maintainer on 2026-11-27: diagnostics and screening (AI mammography, TB chest X-ray CAD), hallucinations entering clinical guidelines, and biased clinical algorithms are listed on the card as not modelled. Diagnostics is the one to add next: it needs global screening volumes and a detection-to-death chain.

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
