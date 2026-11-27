# Roadmap

What we are working on **now**, and what we will **circle back to**. Update this file when a strand starts, finishes or changes status. Decisions themselves stay in `docs/decisions.md`; this file only tracks work.

Last updated: 2026-11-27.

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

Each card is built in its own session from the brief `docs/tasks/build-a-card.md`. The first net card (clinical AI) must first agree a design for harm and benefit components with the maintainer (see the brief).

---

## Now

### 1. Health baselines (GBD risk factors, D16): done for the six baselines
The six global baselines are in `baselines/` (GBD 2023, year 2023), generated from the GBD subdataset `baselines/gbd/`:

| GBD level-1 risk group | Risk factors |
|---|---|
| Environmental and occupational | Air pollution; unsafe water, sanitation and handwashing |
| Behavioural | Tobacco; child and maternal malnutrition |
| Metabolic | High systolic blood pressure; high fasting plasma glucose |

Still to do:
- check that the six sit at the same level of the GBD risk hierarchy (the download does not record it)

### 2. Clinical AI (net)
The first real benefit, so the overview does not show harms alone.

### 3. Biological misuse, real
Replaces the mock card, starting from Righetti's model (GovAI 2025).

### 4. Website and explorer (D6, D8)
With baselines and three cards (clinical AI, bio misuse, and the global environmental footprint if ready), the overview has a benefit, a tail-dominated risk and a steady harm, enough to test the forest plot, sliders and counterfactual switch on real data. Static site generated from `results/` (D8); nothing computed that the CLI cannot reproduce (D10). Task brief for a separate session: `docs/tasks/website-and-explorer.md`.

### 5. Remaining cards, in this order
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
