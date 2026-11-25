# Related work: has anyone already quantified AI's health effects?

Summary of the prior-work search set out in [`docs/prior-work-search.md`](prior-work-search.md). It was run on 2026-11-25 and took 57 queries in 4 rounds. It produced 53 catalogue entries: 3 in tier A, 23 in B, 11 in C and 16 in D.

- Every item: [`related_work/catalog.yaml`](../related_work/catalog.yaml)
- Every query, and how the stopping rule was applied: [`related_work/search_log.md`](../related_work/search_log.md)

## Verdict: the gap claim holds, with one near-miss that `VISION.md` should name

`VISION.md` says no one has produced a near-term, risk-by-risk, DALY-denominated estimate of AI's effects on health that:
- covers harms and benefits, and
- compares them with established burdens.

**That still holds.** No item found does all of these.

**Closest existing work: the *Lancet* Commission on 21st Century Global Threats to Health (Murray, Kanem et al., October 2026).**
- It is the only work found that puts an AI risk in DALYs next to established health threats, using a GBD-based method.
- It estimates about **10.4 billion "amenable" DALYs for malicious use of AI over 2025–2100**. Coverage gives a range of 0 to 15.6 billion. The other threats it scores include obesity, air pollution and antimicrobial resistance.

It differs from this repo in five ways:
1. **Horizon:** 2025–2100, not 2026–2031.
2. **Granularity:** AI is a single "malicious use" row, not risk by risk. Misuse pathways are not split, and malfunctions and systemic risks are absent.
3. **Benefits:** no AI benefit is quantified.
4. **Quantity:** "amenable" DALYs are the gap between a best-case and a worst-case future. They are not an expected burden against a counterfactual.
5. **Evidence:** the AI figure rests on expert and superforecaster judgement, and coverage says the method is not described in detail.

We could read this item only through press material: the journal blocked access. Its appendix should be read before the repo cites the figure.

**Other near-misses:**
- **Rethink Priorities' Cross-Cause Model (2023) and its follow-up on short horizons** are the methodological precedent. They differ in what they estimate: intervention cost-effectiveness rather than risk size, generic existential risk rather than AI pathways, and centuries rather than five years.
- **Saeri et al.'s Delphi study of 272 experts (2026)** matches the window (2025–2030) and covers all 24 MIT risk subdomains, with death-thresholded severity bands. It is the closest thing to a complete set of *probability* inputs. However, it stops at expert severity distributions and never converts them into DALYs.

**In short:** the pieces exist and the synthesis does not.

The pieces that exist:
- at least one ready-made model for a single pathway, where the estimate is already expected deaths per year;
- probability forecasts for 2030;
- measured effects for several benefits.

The synthesis that does not exist is all of these combined, risk by risk, on one DALY scale over 2026–2031, against GBD baselines.

**Suggested edit to `VISION.md` (not made here):** cite the *Lancet* Commission as the nearest DALY-denominated precedent alongside the CCM, and say how this repo differs from it.

## Tier by tier: the items that matter most

**Tier A (multi-risk).**
- **The *Lancet* Commission:** see above.
- **Rethink Priorities' CCM:** Monte Carlo over user-adjustable parameters, with output in DALY-equivalents per $1,000. It found that x-risk value is driven by tail parameters.
- **Duffy's follow-up ("count only the next few generations"):** reruns the CCM over 120–180 years. A generic x-risk project comes out between roughly AMF-level and two orders of magnitude above it, depending on assumptions.

Neither RP item is AI-specific.

**Tier B (single pathway).** Three clusters stand out.

1. **Bio-misuse: Righetti (GovAI, December 2025).**
   - This is already a probability × severity Monte Carlo model in deaths per year:
     - baseline lone-wolf epidemic risk: about 2,000 expected deaths a year;
     - with "AI lab and ops coach" capabilities: about 14,000;
     - adding virus discovery: about 50,000.
   - All three have very wide 90% intervals.
   - It also has a public calculator. It could become the core of `bio-misuse` almost directly, once the access-mode and counterfactual splits are added.
2. **Data-centre air pollution:** three independent US estimates.
   - Chen et al. 2026: about 650 deaths in 2023.
   - Muller (NBER, 2026): $25B a year in damages.
   - Han et al.: more than $20B a year by 2028.
   - All are US-only and cover all data centres, not only AI.
3. **Measured clinical and consumer effects.**
   - Benefits:
     - the MASAI randomised trial (AI-supported mammography);
     - ChartWatch and COMPOSER (in-hospital mortality down about 17–26% at single sites);
     - the Therabot RCT.
   - Harms:
     - FDA adverse-event analyses;
     - Danish psychiatric case records;
     - the association between daily generative-AI use and depression in 20,847 US adults.
   - These are measured effects. None is scaled to a population.

Also relevant to tier B:
- IIHS (2026) measured Waymo crash rates 68% lower and injury crashes 81% lower than human drivers.
- Two non-AI analogues supply severity terms:
  - McGlave et al.: ransomware raises in-hospital mortality for patients already admitted by about 1.3–1.9 percentage points.
  - O'Brien et al.: industrial automation raised mortality at ages 45–54.

**Tier C (forecasts).**
- **FRI's LEAP Wave 9 (June 2026)** gives the most usable 2030 numbers. Median expert probability of an AI catastrophe killing more than 10% of people by 2030:
  - 0.08% under slow progress;
  - 1% under rapid progress.

  The split between slow and rapid progress maps onto the repo's AI trajectories.
- **LEAP Wave 10** is a rare benefit forecast. Median expert TB, HIV and malaria deaths in 2050: 1.65 million under slow AI progress, 0.5 million under rapid.
- **Williams et al. (FRI/GovAI 2025)** gives annual epidemic probabilities (100,000+ deaths): 0.3% baseline, 1.5% with certain LLM capabilities, 0.4% with safeguards.
- **Older, longer-horizon sources:** the XPT (2022, before ChatGPT), the adversarial collaboration, and the AI Impacts survey.
- **Prediction-market compilations (Ånestrand 2025):** the only exceedance curve found for AI-caused deaths before 2029, but they are thin and internally inconsistent.

**Tier D (methods).**
- SaferAI's quantitative risk-modelling method, with its companion cyber models (economic harm only).
- Kapoor, Bommasani et al.'s marginal-risk framework, which underlies the "open models only" counterfactual.
- PRA for AI.
- The OECD and MIT incident trackers, which are possible future anchors for observed harms but give no counts of deaths.
- The International AI Safety Report 2026, which states that systematic data on how common harms are, and how severe, remain limited.

## Candidate new risk cards, checked against D2

Adding cards needs the maintainer's approval (`CLAUDE.md`). These are proposals only.

D2 criteria: (1) a distinct causal pathway, (2) its own evidence, (3) a different kind of work.

| Candidate | (1) | (2) | (3) | Assessment |
|---|---|---|---|---|
| **Data-centre air pollution** (compute emissions → PM2.5/ozone deaths) | yes | yes: three studies | yes: energy, siting, grid work | **Passes.** Well evidenced. Needs an AI share and a global extension. |
| **Autonomous vehicles** (road injuries averted or caused) | yes | yes: IIHS, LEAP adoption | yes: AV safety engineering | **Passes.** A benefit card that can also carry harms. |
| **AI-enabled cyberattacks on health and critical infrastructure** | yes | yes: SaferAI, McGlave, Longterm Wiki, GovAI grid | yes: security work | **Passes.** Check for overlap with any cyber card already planned. |
| **Clinical-AI diagnostics and monitoring benefit** | yes | yes: MASAI, reviews, ChartWatch, COMPOSER | yes: clinical ML deployment | **Passes.** The counterweight to `clinical-errors`. |
| **Chatbot mental-health harm** | yes | yes: Perlis, Olsen, Fang | yes: model behaviour and safety tuning | **Passes.** |
| **Chatbot mental-health benefit** | yes | partly: one RCT | yes: therapeutic product work | **Borderline on (2).** Could be the benefit side of the harm card if the maintainer prefers. |
| **Consumer chatbot medical-advice errors** | partly | partly: Draelos red-teaming | same work as `clinical-errors` | **Probably merge** into `clinical-errors`, with a consumer-facing component. |
| **Labour displacement → mortality** | yes | yes: O'Brien (analogue), LEAP | yes: economic policy, not ML | **Passes D2.** Most of its harm is "not captured in DALYs", and it is far from ML engineering. |
| **AI-accelerated biomedical research** | yes | weak within the window: LEAP Wave 10 is dated 2050; no AlphaFold-to-lives estimate | yes | **Fails (2) for 2026–2031 at present.** Keep as a register entry. |
| **AI errors in critical infrastructure** (malfunction) | yes | weak: LEAP cites it as a common route to catastrophe | yes | **Fails (2) for now.** Revisit when LEAP wave reports are extracted. |

## Not accessed

These items looked relevant but could not be read. None is in the catalogue, except the *Lancet* Commission, which is catalogued from press material because it is the closest item found.

| Item | Why not read |
|---|---|
| *Lancet* Commission full text and appendix (doi:10.1016/S0140-6736(26)01714-9) and the accompanying comment | HTTP 403. Catalogued from press material only (see the catalogue entry). |
| Oxford randomised study of LLM medical advice, *Nature Medicine* (February 2026) | University page returned 403; Europe PMC lookup timed out |
| Samotsvety, "probabilities for potential precursors of existential risk" (2024) | Host refused connection |
| Open Philanthropy (now Coefficient Giving), "AI Reference Classes" (Freitas-Groff, 2023) | HTTP 403 after redirect |
| Metaculus question 7814 (AI malfunction ≥100 deaths or $1B before 2032) | HTTP 403 |
| Jayatunga et al. 2024, *Drug Discovery Today* (AI-discovered drug success rates) | Not found in Europe PMC; the BCG summary was not opened |
| AI-enabled precision medicine value-for-money review (PMC12848305) | CAPTCHA page |
| FBI IC3 2025 AI-related scam losses (via AARP) | HTTP 403 |
| Society of Actuaries AI longevity essays (2025) | DNS failure |
| UN-backed scientific report on AI and health (cited by MobiHealthNews) | HTTP 403, so the report could not be identified |
| Kusano et al., Waymo crash rates at 56.7M miles, *Traffic Injury Prevention* 2025 | PubMed cookie wall. IIHS's independent study was used instead. |
| Benzell & Ye 2024, global macro-simulation of transformative AI with mortality | Identified in round 4, not opened |
| Full texts of the LEAP wave reports and Williams et al. 2025 | Summary pages read only. The full reports should be read when claims are extracted. |

## Limitations of this search

- **Language and index.** English-language queries on a US-indexed web search engine, plus Europe PMC. Non-English work, notably Chinese-language work on AI in health, was not searched.
- **Paywalls and bot blocking.** Several items, including the most important one (the *Lancet* Commission), were read only through press releases, abstracts or summary pages. The catalogue's `accessed` field records this for every item. Numbers taken from summaries should be checked against full texts before they become claims.
- **The clinical literature was sampled, not exhausted.**
  - The stopping rule was applied at the level of pathways (see the search log).
  - Hundreds of single-tool clinical AI evaluations exist, and only representative ones and two systematic reviews were catalogued.
- **Grey literature.** Forum posts, prediction markets and wiki pages were included where they give numbers, and their weak evidence basis is recorded. Some forum and forecasting sites rate-limited or refused automated access.
- **Single searcher, single day.** All screening was done by one agent in one session, with no second screener and no reference-manager deduplication. Forward-citation searches used web search rather than a citation index (e.g. Google Scholar "cited by"), so forward coverage is incomplete.
- **Recency.** Items published in the weeks before 2026-11-25 may not yet be indexed.
