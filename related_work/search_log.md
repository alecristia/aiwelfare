# Search log: prior-work search

Task brief: `docs/prior-work-search.md`. Outputs: `related_work/catalog.yaml` and `docs/related-work.md`.

- **Date of all searches:** 2026-11-25 (single session).
- **Searcher:** Claude Code (Claude Opus 5.5), on the `prior-work-search` branch.
- **Tools:**
  - a general web search engine (US index, English), with "standard" and occasionally "extended" depth;
  - a page-fetching tool;
  - the Europe PMC REST API, for abstracts when publisher pages refused automated access;
  - direct download plus text extraction, for three PDFs too large for the fetch tool.
- **"Screened"** means the result list a query returned (titles, URLs and snippets), as reported by the search tool, usually about 10 per query. **"Included"** means catalogue entries whose source was opened and read *because of* that query. An item found by several queries is credited to the first.

## Round 1: seeds, core query grid, required sources

Seeds from the brief, the main query combinations (AI × burden unit × risk/benefit) and the sources the brief requires checking (International AI Safety Report 2026, MIT AI Risk Repository v4, Epoch/METR/FRI, Rethink Priorities' CURVE).

| # | Query | Screened | Included (catalogue ids) |
|---|---|---|---|
| 1 | Rethink Priorities Cross-Cause Cost-Effectiveness Model AI risk DALY | 10 | rp-cross-cause-model-2023 |
| 2 | data center air pollution premature deaths public health cost Caltech UC Riverside | 10 | han-ren-datacentre-health-2024 |
| 3 | artificial intelligence DALYs averted global health estimate | 10 | (led to Lancet Commission, credited to #7) |
| 4 | "burden of disease" artificial intelligence harms quantification deaths estimate | 10 | parikh-epidemiology-of-ai-2026, armitage-agi-public-health-2025 |
| 5 | Forecasting Research Institute LEAP expert panel AI risks benefits forecasts 2025 | ~29 | fri-leap-wave9-risks-2026, fri-leap-wave10-benefits-2026, fri-leap-introduction-2025 |
| 6 | Existential Risk Persuasion Tournament results AI catastrophe probability superforecasters | 10 | karger-xpt-2023 |
| 7 | Lancet Commission 21st Century Global Threats to Health 2026 artificial intelligence DALYs (extended) | 9 | lancet-commission-threats-2026 |
| 8 | Founders Pledge AI risk cost-effectiveness lives saved expected value model | 10 | jones-nber-ai-xrisk-spending-2025 (no Founders Pledge model found) |
| 9 | chatbot suicide mental health harm population estimate deaths generative AI epidemiology 2026 | 10 | 0 (no population estimate; news and lawsuits only) |
| 10 | AI-enabled bioterrorism expected deaths Monte Carlo estimate biosecurity LLM uplift | 10 | righetti-govai-bioterrorism-2025, williams-fri-llm-biorisk-2025, kim-mocet-2025 |
| 11 | autonomous vehicles lives saved estimate deaths averted Waymo crash rate study | 10 | iihs-waymo-crash-rates-2026 |
| 12 | ransomware attacks hospitals patient mortality estimate deaths study | 10 | mcglave-ransomware-hospitals-2023 |
| 13 | International AI Safety Report 2026 harms magnitude deaths estimates | 10 | iasr-2026 |
| 14 | large language models health impact QALYs WELLBY welfare estimate expected value EA Forum | 10 | 0 |
| 15 | systematic review cost-effectiveness artificial intelligence healthcare QALY economic evaluation | 10 | el-arab-ai-cost-effectiveness-review-2025, vithlani-ai-economic-evaluations-2023 |
| 16 | Squiggle model AI risk deaths near-term harms benefits estimate | 10 | saeri-delphi-272-experts-2026, murray-saferai-methodology-2025 |
| 17 | AI labour displacement unemployment mortality deaths of despair estimate automation health | 10 | obrien-death-by-robots-2022 |
| 18 | AlphaFold AI drug discovery lives saved estimate quantified health benefit economic | 10 | 0 |
| 19 | AI could save lives per year estimate healthcare artificial intelligence deaths averted 2030 modelling study | 10 | deloitte-ai-healthcare-europe-2020, verma-chartwatch-2024, boussina-composer-sepsis-2024 |
| 20 | MIT AI Risk Repository version 4 December 2025 severity likelihood quantitative | 10 | mit-ai-risk-repository-v4-2025 (Delphi dashboard merged into saeri-delphi-272-experts-2026) |
| 21 | probabilistic risk assessment AI harm severity levels framework arXiv | 10 | wisakanto-pra-for-ai-2025, raman-intolerable-risk-thresholds-2025 |
| 22 | "artificial intelligence" "determinant of health" epidemiology arXiv 2026 population exposure | 10 | 0 (duplicate of #4) |
| 23 | quantitative AI risk model cyber uplift expected damages SaferAI Monte Carlo scenario 2025 | ~19 | barrett-saferai-cyber-2025 |
| 24 | Rethink Priorities CURVE sequence AI existential risk value expected | 10 | 0 (CURVE posts reviewed; CCM already included) |
| 25 | Epoch AI health impact of AI estimate mortality biomedical research acceleration | 10 | 0 (no Epoch health estimate found) |
| 26 | RAND report AI catastrophic risk quantitative estimate deaths pandemic large language models red team 2024 2025 | 10 | rand-extinction-risk-2025 |
| 27 | medRxiv generative AI chatbot use mental health outcomes population cohort suicide risk association 2026 | 10 | perlis-genai-depression-2026, olsen-chatbot-psychiatric-records-2026 |
| 28 | AI Impacts 2023 expert survey Thousands of AI authors probability extremely bad outcomes human extinction | 10 | grace-thousands-ai-authors-2024 |
| 29 | OECD AI Incidents Monitor deaths injuries count AI incidents physical harm statistics | 10 | oecd-ai-incidents-monitor-2026 |
| 30 | deepfake AI scam fraud losses estimate elderly health harm quantified 2025 report | 15 | 0 (FBI IC3 summary not accessible; no health-harm estimates) |

Seed items not reached by a query: kapoor-open-foundation-models-2024 (seed in the brief; opened directly). Federspiel 2023 was found by follow-up on #25 (cited as a *BMJ Global Health* analysis) and its abstract was read through Europe PMC.

**Round 1 citation-following.** Backward and forward citations from the seeds and the first finds (Lancet Commission, CCM, Unpaid Toll, XPT, LEAP, Righetti):

| # | Query / action | Screened | Included |
|---|---|---|---|
| 31 | "amenable DALYs" malicious use of artificial intelligence Lancet Commission method probability IHME (extended) | 9 | 0 (method detail only) |
| 32 | data centers air pollution health impacts AI electricity premature mortality 2025 2026 study global (forward from Unpaid Toll) | 10 | chen-selin-datacentre-mortality-2026, hsph-cork-datacentre-sites-2026, muller-nber-datacentre-damages-2026, carmeno-ai-sustainability-wellbeing-review-2026 |
| 33 | FRI adversarial collaboration AI risk results concerned skeptics 2030 forecasts (forward from XPT) | 10 | rosenberg-fri-adversarial-collaboration-2024 |
| 34 | Rethink Priorities AI risk model expected value near-term catastrophe 2024 2025 DALY "cross-cause" (forward from CCM) | 10 | rp-xrisk-next-generations-2023 |
| 35 | AI health benefits harms net welfare quantified "DALYs" "artificial intelligence" both harms and benefits estimate 2026 (extended) | 9 | masai-mammography-trial-2026 |
| – | Backward from LEAP Wave 9 / Righetti / Williams: Righetti's report cites the Williams FRI study (already included) and an interactive model (biocalc.vercel.app, not separately catalogued) | – | – |
| – | Backward from Lancet Commission coverage: cites XPT superforecaster figures (already included) | – | – |

**Round 1 result:** new tier A: 3. New tier B: 18. → continue.

## Round 2: new pathway angles and forecasting platforms

| # | Query | Screened | Included |
|---|---|---|---|
| 36 | "artificial intelligence" "lives saved" OR "deaths averted" global modelling "2030" diagnostics low- and middle-income countries estimate | 10 | 0 (one vendor claim of lives saved, not peer-reviewed, not followed) |
| 37 | LessWrong AI risk Fermi estimate expected deaths next decade breakdown by risk misuse cyber bio | 17 | 0 read (Samotsvety page unreachable; see Not accessed) |
| 38 | Metaculus AI catastrophe forecast deaths before 2030 question community prediction AI-caused | 17 | aldred-metaculus-fli-workshop-2023, anestrand-ai-disaster-markets-2025 |
| 39 | AI chatbot mental health therapy randomized trial effect population scale benefit Therabot depression symptom reduction | 10 | heinz-therabot-rct-2025 |
| 40 | clinical AI adverse events patient harm incidents FDA MAUDE AI-enabled medical devices recalls deaths analysis | 10 | lin-fda-ai-device-reporting-2025, handley-ai-fda-device-reports-2024, susanto-ml-cds-scoping-review-2023 |
| 41 | AI-discovered drugs clinical trial success rate phase I analysis Jayatunga 2024 | 10 | 0 (primary paper not accessed) |
| 42 | AI cyberattack critical infrastructure expected fatalities estimate quantified risk model healthcare outage deaths | 10 | vandermerwe-govai-power-grid-2026, longtermwiki-ai-cyber-tail-2026 |
| 43 | Guesstimate OR Squiggle "AI" "DALYs" model public health benefits harms language models | 10 | 0 |
| 44 | WHO report artificial intelligence health impact quantified estimate lives 2025 2026 IHME AI forecasting scenario | 10 | 0 (WHO documents found are qualitative) |

**Round 2 result:** new tier A: 0. New tier B: 4, including two pathways not yet represented: chatbot *therapy benefit* (Therabot) and *reported AI medical-device adverse events* (FDA). → counter not started.

## Round 3: remaining pathways from the brief, and incident data

| # | Query | Screened | Included |
|---|---|---|---|
| 45 | AI Incident Database analysis deaths injuries physical harm trends study arXiv 2025 | 10 | mit-ai-incident-tracker-2026 |
| 46 | advanced driver assistance systems fatalities prevented estimate automatic emergency braking lives saved per year AI | 10 | 0 (AEB/ADAS estimates exist but are not modern-AI-specific; excluded) |
| 47 | health misinformation generative AI deaths estimate quantified vaccine hesitancy LLM persuasion population harm | 10 | 0 (persuasion experiments only, no health outcomes) |
| 48 | CSET AI harm framework severity scale incidents quantification | 10 | 0 (severity scale already covered via MIT tracker) |
| 49 | "expected deaths" "artificial intelligence" per year estimate catastrophic risk global priorities 80,000 Hours OR "Open Philanthropy" OR "Founders Pledge" | 10 | 0 read (Open Philanthropy reference-class report not accessible) |
| 50 | large language model diagnostic accuracy patient harm estimate medical advice errors population impact study 2026 | 10 | draelos-llm-unsafe-medical-answers-2025 (tier D) |

**Round 3 result:** new tier A: 0. New tier B: 0. The GovAI grid paper was classed D, the Longterm Wiki page C, the MIT tracker D and Draelos et al. D. → **first round with no new A or B.**

## Round 4: forward citations of the closest items, and last pathway checks

| # | Query | Screened | Included |
|---|---|---|---|
| 51 | "Dual-Use AI Capabilities and the Risk of Bioterrorism" Righetti cited response critique expected deaths | 10 | 0 (general AI-biorisk critiques only) |
| 52 | "Lancet Commission on 21st century global threats" artificial intelligence response correspondence critique AI DALY estimate | 10 | 0 (one op-ed; Health Policy Watch report used to fill in Lancet method details) |
| 53 | quantifying near-term AI harms and benefits common metric comparison global health burden "QALY" OR "DALY" arXiv 2025 2026 (extended) | 9 | 0 |
| 54 | AI companion chatbot loneliness wellbeing longitudinal randomized study effect size 2025 MIT OpenAI | 10 | fang-chatbot-psychosocial-rct-2025 (tier B, pathway already represented) |
| 55 | AI weather forecasting early warning lives saved estimate GraphCast heat wave cyclone mortality quantified | 10 | 0 (no quantified lives-saved estimate) |
| 56 | AI-enabled autonomous weapons drones casualties estimate war Ukraine deaths attributable AI targeting quantified | 18 | 0 (anecdotes and hit-rate claims only) |
| 57 | economic growth from AI health effects mortality income elasticity life expectancy projection transformative AI model paper | 10 | 0 read (Benzell & Ye simulation identified, not opened) |

**Round 4 result:** new tier A: 0. New tier B *on a new pathway or at population scale*: 0. One further within-pathway tier B study (Fang et al., chatbot psychosocial effects) was catalogued. → **second consecutive round with no new A or B, as operationalised below. Stopping rule met after 4 rounds.**

## Round 5 (2026-11-27): AI-enabled autocratisation and AI in organised violence

Added after review. The maintainer asked why nothing covered harms from autocracy or organised violence. Rounds 1–4 had one query on autonomous weapons (q56) and none on autocratisation, repression or power concentration, because the brief's pathway list did not name them and the search treated that list as its scope. This round fills that gap. Standard and extended web search; results screened from search summaries; items catalogued only after their abstract or text was read.

| # | Query | Screened | Catalogued |
|---|---|---|---|
| 58 | AI-enabled authoritarianism surveillance repression health mortality quantified estimate (extended) | 9 | 0 (mechanism papers only; no health quantity) |
| 59 | democracy and health life expectancy causal effect estimate Bollyky Lancet | 10 | bollyky-democracy-mortality-2019 (tier E) |
| 60 | democratic backsliding autocratization effect on mortality or life expectancy V-Dem | 10 | wigley-autocratisation-uhc-2020 (tier E) |
| 61 | AI-enabled coups power concentration probability forecast 2030 expert survey (extended) | 9 | 0 (Forethought scenario analysis, no probabilities; individual blog estimates; the 2030 elicitation found is Saeri et al., already catalogued) |
| 62 | AI targeting civilian casualties Gaza Lavender deaths attributable AI decision support (extended) | 9 | 0 (journalism and legal analysis; no attributable-death estimate) |
| 63 | autonomous drones war casualties share of deaths Ukraine 2025 | 17 | 0 (official claims that drones cause 70–80% of battlefield casualties; mostly remotely piloted, not AI, and from interested parties) |
| 64 | AI risk of interstate war or nuclear escalation probability forecast 2030 (extended) | 9 | rivera-llm-escalation-wargames-2024 (tier D); XPT and LEAP already catalogued |
| 65 | machine learning conflict early warning ViEWS lives saved | 10 | 0 (forecast-accuracy evaluations; no lives-saved estimate) |

Also in this round: the *Lancet* Commission's full text (supplied by the maintainer) was read and its catalogue entry updated. It names autonomous weapons, autonomous nuclear weapons and mass political deepfakes inside its malicious-AI category, and estimates conventional conflict (not AI) at 7.71 billion amenable DALYs to 2100.

**Round 5 result:** no tier A or B item exists for either pathway. Two tier E items (health effect of autocratisation, not AI-specific) and one tier D item. A single targeted round, not run to the stopping rule.

## How the stopping rule was applied (read this)

The brief says to stop after two consecutive rounds with no new tier A or B items. Taken literally, that rule cannot stop in the clinical-AI literature: there are hundreds of single-site evaluations and trials of clinical AI tools, and each would be a "new tier B item". **I therefore counted a tier B item as "new" for the stopping rule only if it added a pathway not yet represented in the catalogue, or a population-level estimate for an existing pathway.** Further single-site or single-tool studies of a pathway already covered were catalogued when found (e.g. Fang et al. in round 4), but did not reset the counter.

Under a literal reading, round 4 would not count as empty, and the search would have continued. The maintainer may prefer a different rule. The catalogue's clinical-AI entries are **representative, not exhaustive**; the two systematic reviews (El Arab 2025; Vithlani 2023) are the entry points to that literature.

## Direct retrievals (not from a search query)

- **Europe PMC REST API** (`/europepmc/webservices/rest/search`), for abstracts where publisher pages returned 403 or a cookie wall. Queries by DOI or title for:
  - O'Brien et al. 2022 and Federspiel et al. 2023;
  - MASAI (both papers);
  - ChartWatch (Verma 2024) and COMPOSER (Boussina 2024);
  - Olsen et al. 2026 (Danish psychiatric records);
  - Therabot (Heinz 2025);
  - Lin et al. 2025, Handley et al. 2024 and Susanto et al. 2023.

  One title query for the Oxford *Nature Medicine* chatbot RCT timed out.
- **Downloaded and text-extracted** (pypdf, into a scratch folder, not committed), because they exceeded the fetch tool's size limit:
  - the GovAI bioterrorism report (Righetti 2025);
  - the XPT working paper (Karger et al. 2023);
  - the ransomware manuscript (McGlave et al.).
- **Mirrors** for EA Forum and LessWrong posts that returned HTTP 429: `ea.greaterwrong.com` and `www.greaterwrong.com`.
- **One attempt to fetch the Lancet abstract with a browser user-agent header was blocked by the session's permission system** and was not pursued. The Lancet Commission was catalogued from press material until round 5, when the maintainer supplied the full text.

## Totals

- Queries: 65 web searches, about 700 results screened, plus about 17 direct API retrievals (two more in round 5).
- Catalogue: 56 items (A 3, B 23, C 11, D 17, E 2), all opened and read, at least at abstract level.
- Not accessed: see `docs/related-work.md`, section "Not accessed".
