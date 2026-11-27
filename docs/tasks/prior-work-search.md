# Task brief: prior-work search

**Run this as a separate task**, in its own Claude Code session on its own branch (e.g. `git switch -c prior-work-search`), or with a dedicated research tool. It is literature research, not engineering. Do not touch code, models, claims or cards.

## Why

`VISION.md` claims that no one has yet produced a near-term, risk-by-risk, DALY-denominated estimate of AI's effects on human health, covering both harms and benefits and comparing them with established health burdens. A first, quick search (November 2026) did not find one. It did find several partial precedents. This task tests that claim properly and catalogues everything the repo can build on.

## The question

> What work has already **quantified** the effects of AI (harms and/or benefits) on human health, mortality or welfare? How close does each piece come to this repo's question: near-term (≈2026–2031), risk by risk, in DALYs or convertible units, harms and benefits, compared against health baselines?

"Quantified" means the work gives numbers for **effects on people** (deaths, DALYs, QALYs, WELLBYs, cases, monetised welfare), or probabilities of events with stated human consequences. Qualitative risk lists and taxonomies are out of scope, except as entries in tier D.

## Tiers

Classify every relevant item into exactly one tier.

| Tier | What it is | Example already known |
|---|---|---|
| **A: Multi-risk quantification** | Estimates welfare/health effects across *several* AI risks or benefits on a common scale | Rethink Priorities, Cross-Cause Cost-Effectiveness Model (2023) |
| **B: Single-pathway quantification** | A health or welfare estimate for *one* AI pathway | UC Riverside / Caltech estimate of premature deaths from US data-centre air pollution (2024); cost-effectiveness reviews of clinical AI tools in QALYs |
| **C: Probability forecasts usable as inputs** | Forecasts of AI events with stated human consequences, but no burden estimate | FRI Existential Risk Persuasion Tournament (2022); FRI LEAP waves on risks and benefits (2025–26) |
| **D: Methods and frameworks** | Approaches to quantifying AI harm severity or impact, without population-level estimates | Harm-severity scales in probabilistic risk assessment for AI; marginal-risk framework for open models (Kapoor, Bommasani et al., 2024) |

## Seeds

Start from the examples in the table. For each seed, follow **backward citations** (what it cites) and **forward citations** (what cites it).

Also check, at minimum:
- the International AI Safety Report 2026 and its references on harm magnitudes
- the MIT AI Risk Repository (v4) and its linked documents
- Epoch AI, METR, and FRI publications
- Rethink Priorities' CURVE sequence

## Where to search

- **Academic:** Google Scholar, arXiv (cs.CY, cs.AI), medRxiv, PubMed, SSRN, *The Lancet*, *BMJ Global Health*, *Nature Medicine*
- **Research organisations and think tanks:** Rethink Priorities, Founders Pledge, Forecasting Research Institute, Epoch AI, RAND, CSET, GovAI, Centre for the Study of Existential Risk, Future of Humanity Institute (archived), AI Impacts
- **Health institutions:** IHME, WHO, OECD (including the OECD AI Incidents Monitor)
- **Community forums:** EA Forum, LessWrong, Alignment Forum. These are often where partial models appear first. Treat them as tier B–D candidates and record their evidence basis honestly.
- **Interactive models:** Guesstimate, Squiggle Hub, and similar public model repositories

## Search terms (combine and vary)

- `AI` / `artificial intelligence` / `large language models` / `generative AI` / `frontier AI`
- × `DALY` / `QALY` / `WELLBY` / `burden of disease` / `mortality` / `deaths` / `health impact` / `welfare` / `cost-effectiveness` / `expected value` / `lives saved`
- × `risk` / `harm` / `benefit` / `catastrophe` / `misuse` / `forecast` / `quantification` / `Monte Carlo`
- Pathway-specific: chatbots + suicide / mental health; autonomous vehicles + fatalities; clinical AI + adverse events; data centres + air pollution; AI + biosecurity + expected deaths; AI + cyberattacks + hospitals; AI + labour displacement + mortality

Log every query (see Outputs).

## Inclusion rules

- **Open and read each item before including it.** Never include an item from a search snippet or from memory alone. If it can't be accessed, list it under "not accessed", with the reason.
- **Do not invent or guess citations.** Every entry needs a working link or DOI.
- **Any date is acceptable, but record it.** Flag items from before November 2022 (pre-ChatGPT) as such.
- **Quotes stay under 25 words**, at most one per item. Paraphrase everything else.

## Stopping rule

Stop when **two consecutive rounds of searching and citation-following turn up no new tier A or tier B items**. Report how many rounds that took.

## Outputs (only these files)

1. **`related_work/catalog.yaml`**: one entry per item, with these fields:
   - `id`, `title`, `authors`, `year`, `url_or_doi`, `tier`
   - `what_is_quantified` (one sentence)
   - `units` (DALYs / deaths / QALYs / probability / $ / other)
   - `time_horizon`, `geography`
   - `harms_benefits_or_both`
   - `method` (Monte Carlo / expert elicitation / epidemiological / forecasting tournament / other)
   - `evidence_basis` (measured / modelled / expert judgement / speculation)
   - `author_interests` (e.g. an AI developer, a funder with a stated cause priority)
   - `closeness_to_this_repo`: 0–3, with one line of justification
   - `usable_as`: `precedent` / `claim source for card X` / `baseline` / `method` / `none`
   - `candidate_new_card`: a risk or benefit pathway this item suggests that we haven't listed, if any
   - `pre_chatgpt`: true/false
   - `short_quote` (optional, under 25 words)
2. **`related_work/search_log.md`**: every query and source searched, with the date, the number of results screened, and the number included. Also the citation-following rounds and the point where the stopping rule was met.
3. **`docs/related-work.md`**: a human-readable summary of 1–2 pages:
   - **Verdict:** does the gap claimed in `VISION.md` hold, partly hold, or not hold? Give the closest existing work and exactly how it differs.
   - **Tier by tier:** the most important items, in two or three sentences each.
   - **Candidate new risk cards** surfaced by the search, checked against the D2 criteria in `docs/decisions.md`.
   - **Not accessed:** items that looked relevant but could not be read.
   - **Limitations of this search:** languages covered, paywalls, grey literature not reachable.

## Done when

- All three files exist and are consistent with each other.
- Every catalogue entry links to a source that was actually opened.
- The summary states a clear verdict on the gap claim.
- Changes are committed on the `prior-work-search` branch and opened as a pull request. Do not merge it; the maintainer reviews it.
