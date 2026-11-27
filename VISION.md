# Vision

## Who this is for

ML engineers and people in adjacent roles. You know how modern AI systems are built and deployed, and you are weighing whether to move into AI safety and, if so, which problems matter most.

The AI safety literature does not make that decision easy. It is full of taxonomies (risk domains, harm categories, release gradients, governance capacities) but rarely gives magnitudes. A taxonomy can tell you that "AI-enabled biological misuse" and "labour displacement" are both risks. It cannot tell you which one is larger over the next few years, by how much, or how either compares with malaria.

This open-source repo tries to close that gap.

## The question

**Over the next five years (2026–2031), what is the expected impact of AI on human health, measured in DALYs, broken down by risk (and benefit), and how confident can we be in each estimate?**

The repo should let a reader **interrogate** the literature instead of reading all of it. That means asking a question (in code, through a chart, or in plain language through their own AI agent) and getting back an answer that is quantified, sourced at every step and honest about uncertainty and disagreement.

## Scope decisions (and what they cost)

These choices are deliberate. Each one makes the question answerable, and each one leaves something important out. They are stated up front so that no reader mistakes the output for more than it is.

### 1. Scale only: no tractability or neglectedness (yet)

In the common *importance × tractability × neglectedness* framing, this repo addresses **importance (scale) only**. The largest risk by DALYs is not necessarily the best one to work on: it may already be crowded, or there may be little anyone can do about it. A reader choosing a career should treat these estimates as one input, not as a ranking of where to work. Tractability and neglectedness may be added later as separate layers.

### 2. DALYs as the unit, and why that is a significant limitation

Disability-adjusted life years (DALYs) are the standard unit of global health. They let AI-related harms be compared like-for-like with well-measured burdens such as malaria, tuberculosis or road injuries. That comparability is the main reason for choosing them.

DALYs, however, capture only **health loss: early death and time lived with illness or disability**. They encode a narrow, aggregative view of what matters, close in spirit to a *harm- and suffering-focused* welfarism. Much of what people care about, and much of what AI could affect, falls outside them:

- **Fairness and distribution.** A DALY counts the same no matter who bears it. Harms concentrated on already-disadvantaged groups, or discrimination that causes no measurable health loss, barely register.
- **Autonomy and freedom.** Manipulation, surveillance and erosion of meaningful choice.
- **Rights and dignity.** Violations of privacy, consent or due process that may not show up as ill health.
- **Democratic legitimacy and concentration of power.** AI-enabled entrenchment of states or companies, weakened accountability, a degraded information ecosystem.
- **Truth and epistemic health.** Erosion of a shared understanding of facts, and of trust in institutions.
- **Positive wellbeing beyond health.** Meaning, purpose, relationships and life satisfaction. Job loss, for example, may cost far more in these terms than in DALYs. (Wellbeing-year measures such as WELLBYs try to capture this.)
- **Future generations and the long-term future.** Catastrophic or existential risks are counted only by the deaths they would cause within the window, multiplied by their probability. On many moral views, this badly understates their importance.
- **Non-human beings.** Animals, and possibly AI systems themselves, if they turn out to have morally relevant experiences.

The repo will record such harms wherever the literature discusses them and flag them as **"not captured in DALYs"**, so they stay visible even though they are excluded from the numbers.

### 3. Short horizon: up to five years

All estimates cover **late 2026 to late 2031**. This keeps the models grounded in systems that exist or are about to, and in observable trends. The cost: risks whose expected harm sits mostly beyond 2031 (including most loss-of-control and existential-risk scenarios) will look small here even if they dominate on longer horizons. The repo reports what probability those scenarios get within the window, and leaves later years out of its numbers rather than ignoring them silently.

### 4. Net effects

Welfare is net. AI also *reduces* DALYs, through diagnostics, drug discovery, health-care access and more. Benefits are estimated in the same format as harms, so that no risk looks large or small for lack of a counterweight.

## Sources

Every estimate in this repo rests on four bodies of evidence. They differ a lot in maturity, so they are kept separate and treated differently.

| | **Today** | **Next five years** |
|---|---|---|
| **AI** | A. AI risks as currently understood | C. How AI is likely to evolve |
| **World health** | B. The current burden of disease | D. How world health is likely to evolve |

World health (B, D) is measured with decades of standardised data and published uncertainty intervals. AI (A, C) is young, fast-moving and mostly unmeasured. That asymmetry is itself a finding, and the repo should make it visible rather than hide it.

### General rules for all sources

- **Peer review is not required.** In AI especially, peer review lags months or years behind the field. Preprints, technical reports, evaluation results and lab disclosures are admitted. In exchange, every source is tagged with:
  - **type**: peer-reviewed / preprint / intergovernmental report / technical evaluation / lab disclosure / forecast aggregate / expert survey / incident report / commentary
  - **date** of the evidence, not just of publication
  - **author interests**: notably when an AI developer reports on its own models
  - **evidence basis**: measured / modelled / expert judgement / speculation
- **Prefer primary sources.** Use the dataset or paper itself, not a news article or blog summary of it. Aggregators (e.g. Our World in Data) are a convenient way to access data, but the original is what gets cited.
- **Pin versions.** Datasets and living documents (GBD rounds, the MIT repository, METR's benchmarks) change. Every claim records the version or access date it came from.

### A. AI risks today

The aim is to capture a decade of work on what can go wrong, and the growing evidence of what already has.

- **Consensus syntheses (starting point):** the *International AI Safety Report*, an annual assessment chaired by Yoshua Bengio. The 2026 edition is its second, written by over 100 experts with an advisory panel nominated by more than 30 countries and international organisations, including the EU, OECD and UN. It groups risks into malicious use, malfunctions and systemic risks.
- **Taxonomies as indexes:** the *MIT AI Risk Repository*, now in its fourth version, with over 1,600 risks extracted from 65 published frameworks. It is used to check coverage ("have we missed a category?"), not as a source of magnitudes.
- **Technical evidence:** preprints, plus results from independent evaluation organisations (e.g. METR, Epoch AI) and government AI safety/security institutes.
- **Lab disclosures:** model/system cards and frontier safety frameworks from AI developers. Often the only source for dangerous-capability evaluations, but authored by interested parties, and tagged accordingly.
- **Observed harms:** incident databases (e.g. the AI Incident Database, the OECD AI Incidents Monitor). These are the main empirical anchor for harms that are happening now rather than hypothetical.
- **Deployment and access:** the literature on open versus closed release and on structured access (e.g. Solaiman; Kapoor, Bommasani et al.; Reuel, Bucknall et al.), needed to separate risks by how a model is distributed.

### B. World health today

The main concern here is choosing one internally consistent source rather than mixing incompatible estimates.

- **Primary: the Global Burden of Disease study (GBD, IHME).** The most comprehensive and widely used source. The GBD 2023 round, published in *The Lancet* in October 2025, estimates DALYs for 375 diseases and injuries and the burden attributable to 88 risk factors, with uncertainty intervals throughout. All baseline comparisons use GBD unless there is a reason not to.
- **Cross-check: WHO Global Health Estimates (GHE).** The latest release, from October 2026, covers 2000–2023. GHE and GBD are not fully independent (WHO draws in part on GBD work), and they disagree for some causes. Where they differ materially, the repo shows both.
- **Disease-specific reports**, for causes used as headline comparisons: e.g. WHO's *World Malaria Report* and *Global Tuberculosis Report*, and UNAIDS for HIV.

### C. How AI is likely to evolve (2026–2031)

This is the weakest and most consequential input. The repo draws on several kinds of forecast and does not privilege any single one.

- **Measured trends:** Epoch AI (compute, training runs, the Epoch Capabilities Index) and METR's time-horizon measurements (how long a task, in human expert time, AI agents can complete). Both are empirical and both have been updated recently. Epoch found in 2026 that progress on most of its metrics has sped up relative to the post-2023 trend.
- **Structured expert and forecaster judgement:** the Forecasting Research Institute's *Longitudinal Expert AI Panel* (LEAP), which asks hundreds of experts and superforecasters monthly for AI forecasts, including on catastrophic risks and on benefits; prediction platforms such as Metaculus; and large expert surveys such as AI Impacts'.
- **Scenario models:** explicit models such as the AI Futures Project's (*AI 2027*, the AI Futures Model). These are useful because their assumptions can be inspected and varied.
- **Calibration warning:** both experts and forecasters have recently tended to *underestimate* AI progress on several measures, while some industry leaders predict much faster change than expert panels do. The repo carries a range of AI trajectories (e.g. slow, trend and fast) through every model rather than picking one.

### D. How world health is likely to evolve (2026–2031)

This determines what AI-attributable DALYs are compared against in 2031, not just today.

- **Primary: IHME's *Future Health Scenarios*** (GBD forecasting), which provides reference ("most likely") and alternative scenarios for disease burden to 2050 for all countries. They are published in *The Lancet*.
- **Population denominators:** UN *World Population Prospects*.
- **Caveat:** these forecasts do not explicitly model AI. They extrapolate historical drivers, which already include past technological progress. How the repo handles this is set out under *Modelling decisions*, point 2.

Over a five-year horizon, world health is expected to change slowly and predictably, while AI may change fast and unpredictably. In most models, uncertainty about AI will dominate.

## What "interrogate" means

### The questions

A reader should be able to answer questions like these in minutes rather than weeks:

1. *What is the best estimate of the DALYs caused by risk X between 2026 and 2031? What assumptions does it rest on, and who disagrees?*
2. *How does that compare with malaria, or with road injuries, over the same period?*
3. *Which risks does the literature rank as largest, and which does it merely discuss most? Are they the same?*
4. *How does the picture change across open-weight models, locally deployed frontier models and API-served models?*
5. *What would I have to believe for risk X to be larger than risk Y?*
6. *Which important harms does this repo **not** capture, and why?*
7. *Where is the evidence thinnest relative to how much might be at stake?*
8. *What changed since I last looked, and why?*

Every answer should be traceable to the claims behind it, and every claim to a specific passage in a specific source. These questions double as **acceptance tests**: each interface layer below must answer some of them, and together they must answer all of them.

### How: four layers built from one dataset

There is a single source of truth: the claims, models and results in the repo. Every interface is generated from it, so no layer can drift from the others or from the sources.

**1. Code-first access: the foundation.** The data and models are installable as a Python package and queryable with tools readers already use (pandas, DuckDB, notebooks). Every model can be rerun with different parameters. Disagreeing with an assumption has a clear path: change it, rerun, open a pull request. *Answers questions 1, 4, 5 and 7 in full detail.*

**2. Risk cards and an overview chart: the front door.** A static website generated from the data contains:
- **One overview chart.** All risks *and benefits* on a single logarithmic scale with uncertainty intervals, next to baseline burdens (malaria, tuberculosis, road injuries), with a switch between the three counterfactuals. Tail-dominated estimates are visibly marked, so the ranking is not read as more precise than it is.
- **One risk card per risk or benefit**, modelled on the *model cards* ML engineers already know: the estimate and interval; its probability and severity components; key sources and evidence types; harms not captured in DALYs; known limitations; date of last change.
*Answers questions 1, 2, 3 and 6 at a glance.*

**3. Parameter explorer and crux views: for the most important risks.**
- **Parameter explorer:** sliders for each model's key inputs, with results updating live. This is the *contested choices become parameters* principle made usable.
- **Crux views:** sensitivity analysis showing which few assumptions drive each estimate, and which assumption would flip the ranking between any two risks. For a career decision, knowing *what you would have to believe* is often more useful than the ranking itself.
*Answers question 5 directly, and question 7 by showing where evidence is weak but influential.*

**4. Agent-ready by design: instead of a built-in chatbot.** The repo does not ship its own AI question-answering interface. A built-in chatbot would add a layer that cannot be verified or versioned on top of a project whose value is traceability, and its audience already uses coding agents. Instead, the repo is structured so that *any* agent (Claude Code or otherwise) can work with it reliably: structured data, a documented command-line tool, and an agent guide (`CLAUDE.md`). Readers who want to ask questions in plain language bring their own agent, which answers by running the repo's own queries and models and cites what it ran. *Answers any of the questions, in plain language.*

**Plus: a changelog digest.** Periodic release notes on which estimates moved and why, generated from the commit history. *Answers question 8.*

The detailed decisions for these layers (risk card structure, the merged chart and explorer, hosting, the CLI) are recorded in [`docs/decisions.md`](docs/decisions.md).

### Deliberately not built

- **A personalised "your ranking" quiz.** It is engaging, but it risks turning a serious question into a game and hiding the assumptions behind a single answer. The parameter explorer covers the same need more transparently.
- **A hosted chatbot.** See layer 4.

## What success looks like

1. **Atomic, sourced claims.** Sources are broken into small, machine-readable claims ("Source S estimates P(event E by 2030) at 0.1–5%, conditional on C"), each linked to the source, page and quote. Existing taxonomies (e.g. the MIT AI Risk Repository) act as *indexes* into these claims, not as the end product.
2. **Explicit models instead of vibes.** Every DALY estimate comes from a small, readable model (a script or notebook) that combines claims into a probability distribution. Change an input and the estimate updates. Disagreement shows up as competing models or parameter ranges, not as an average.
3. **Baselines in the same format.** Established burdens (from sources such as GBD and WHO) are stored the same way, over the same 2026–2031 window, so comparisons are like-for-like.
4. **Readable at every zoom level.** The overview chart, then a risk card per risk or benefit, then the model and its underlying claims, then the raw sources. No reader should have to open a 777-row spreadsheet to get oriented.
5. **Version-controlled reasoning.** Every change to an estimate has a commit, a diff and a reason, so you can see how and why the picture shifted when a new paper came out.

## Design principles

- **Questions first.** The structure serves the questions readers actually ask, not the categories that authors happened to use.
- **Extraction separate from judgement.** What a source *says* is recorded apart from how much we *trust* it and how we *combine* it.
- **Uncertainty is the product, not a caveat.** Wide ranges, conditional estimates and "unknown" are first-class outputs.
- **Disagreement is kept.** When credible sources differ by orders of magnitude, the repo shows the disagreement and what drives it.
- **Contested choices become parameters.** Where an answer depends on values or framing (which counterfactual, how to weigh evidence), the options are modelled side by side and the reader chooses, instead of the repo choosing silently.
- **Limitations are visible.** Harms outside DALYs or beyond the time window are flagged where they arise, not just in this document.
- **AI agents are tools, not authorities.** Agents help maintainers extract, link and model, and help readers query. Every output an agent produces must point back to queries, models and sources that a human can check.

## Non-goals

- Not a recommendation of what to work on: tractability and neglectedness are out of scope for now.
- Not a complete moral accounting of AI: see the DALY limitations above.
- Not a single "official" number for AI risk.
- Not policy advocacy, and not written for policymakers. Its readers build AI systems, or could. They shape how AI is made: what gets trained, how it is evaluated, how it is released and deployed. The repo should help them see where their own technical work could reduce harm, not tell governments what to do.

## Modelling decisions

Each methodological question has a decision and a stated limitation. Where the right answer depends on the reader's values or on the question they are asking, the decision is to **model each option separately and let the reader choose**, rather than for the repo to choose for them.

### 1. What AI is compared against (the counterfactual)

To say AI *causes* N DALYs, the real world has to be compared with an imagined one. That imagined world is a measuring tool, not a forecast. Different comparisons answer different questions.

**Decision:** model three counterfactuals separately, as a reader-selectable parameter, and label every result with the one it uses:

- **No modern AI.** Gives the total health effect of AI, including systems already deployed.
- **AI capabilities stay at 2026 levels.** Gives the effect of the next five years of progress specifically.
- **Only open-weight or older models advance.** Gives the marginal effect of frontier development.

**Limitation:** none of these worlds can be observed. Attributing a harm to AI (e.g. how many scam losses would have happened anyway, without AI) relies on explicit but contestable assumptions, which every model must state.

### 2. The health baseline

**Decision:** IHME's reference forecast is the health baseline for all three counterfactuals. It is treated as containing no AI effects beyond those already present in its historical input data (to 2023).

**Limitation:** if AI already affects health trends, the baseline may partly double-count or miss those effects. Over five years this is judged small next to the uncertainty in the AI estimates, but the judgement is ours, not IHME's.

### 3. Turning scenarios into DALYs

**Decision:** every risk and benefit is modelled as *probability of the event within the window × DALYs if it happens*. Both terms are wide distributions, not point values, and are combined by Monte Carlo simulation. Results are reported as a median and a 90% interval, and the probability and severity components are always shown separately as well as combined.

**Limitation:** for rare, severe events, the expected value is driven by the assumed tail of the distribution, which the evidence barely constrains. Such results are flagged as **tail-dominated**, and their headline numbers should be read as illustrations of the assumptions, not as measurements.

### 4. Modelling approach: uncertainty propagation, not Bayesian inference

**Decision:** models propagate uncertainty forward; they do not update on data. This puts the repo in the same family as GiveWell-style cost-effectiveness analysis (and tools such as Guesstimate or Squiggle):
- Each model parameter is a probability distribution fitted to what the sources say (e.g. a lognormal through a source's stated 5th and 95th percentiles).
- The distributions are combined by Monte Carlo simulation with fixed random seeds, so every run is reproducible.
- Every parameter, its distribution and the claims behind it are visible and changeable.

The closest methodological precedent is Rethink Priorities' [Cross-Cause Cost-Effectiveness Model](https://rethinkpriorities.org/publications/rethink-priorities-cross-cause-cost-effectiveness-model-introduction-and-overview) (2023). It puts work on existential risk, global health and animal welfare on a common scale (DALY-equivalents per $1,000 spent), using Monte Carlo simulation over parameters that users can adjust: the same approach this repo takes. Its authors found that the expected value of existential-risk work is driven mostly by the "tail-end" values of a few deeply uncertain parameters, which is the problem the tail-dominated flag (decision 3) addresses. This repo differs in three ways: it estimates the size of risks, not the cost-effectiveness of interventions (so no tractability); it works risk by risk over 2026–2031 instead of focusing on long-run extinction; and it includes near-term harms and benefits.

This is the simplest approach that still represents uncertainty honestly. It also runs fast enough to power the in-browser parameter explorer.

**Limitation:** the approach does not *learn*. A Bayesian approach would treat each source's claim as a noisy observation of an underlying quantity, model the biases of different kinds of evidence, and update estimates as new observations arrive. In the future that may be desirable, for example for risks where incidents start to be recorded systematically. It is not adopted here because, for most of these risks, **there are simply no actual observations to update on**. An AI-assisted pandemic, or a loss-of-control event, has not happened. Bayesian machinery would add complexity while its results would still be driven almost entirely by the priors, that is, by the same expert judgements this approach already uses directly. One consequence is that the inputs are only as good as the judgements they come from. They are not corrected for, say, forecasters' known tendency to underestimate AI progress, except where a model does so explicitly and visibly.

### 5. Weighing different kinds of evidence

**Decision:** there is no hidden weighting. Where evidence types disagree (e.g. measured incidents versus expert forecasts versus a lab's own evaluations), the result is shown separately for each (*"from incident data: X; from expert forecasts: Y"*). Readers may set their own weights; any combined figure states the weights it used.

**Limitation:** this leaves more synthesis to the reader and makes for less tidy headlines. It is the price of not baking in our own judgement. Headlines still need one number, so the default combined figure weights every evidence type equally. Equal weighting is itself a judgement, not a neutral choice: it gives a developer's evaluation of its own model, an expert forecast and an independent measurement the same pull, and it lets the number of evidence types a risk happens to have shape its estimate.

### 6. Units beyond DALYs

**Decision:** version 1 uses DALYs only. Harms that DALYs miss are recorded qualitatively and flagged "not captured in DALYs" (see *Scope decisions*). A second unit (e.g. WELLBYs) is not planned for version 1.

**Limitation:** see the DALY limitations above. Risks whose harm is mostly non-health (concentration of power, loss of autonomy, epistemic harm) will appear small in every quantitative output.
