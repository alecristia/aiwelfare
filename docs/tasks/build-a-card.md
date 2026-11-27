# Task: build one card

A self-contained brief for a separate session that builds **one** card end to end: sources → claims → model → prose → generated card. Launch it once per card, naming the card in the prompt, e.g.:

> Read `docs/tasks/build-a-card.md` and build the card **Clinical AI (net)**.

Written 2026-11-27. Work on a branch named after the card (`git switch -c card/<risk-id>`) and open a pull request; do not merge it.

## Read first

1. `CLAUDE.md`: hard rules (never invent a number, atomic claims, quotes under 25 words, DataLad provenance, mock labelling).
2. `VISION.md`: the question, the scope decisions (DALYs, 2026–2031, **global**, net effects, scale only), and the modelling decisions. In particular:
   - the three counterfactuals
   - probability × severity with Monte Carlo
   - no hidden weighting of evidence
   - estimates are never summed
3. `docs/decisions.md`. These are binding:
   - **D2:** cards are defined top-down; finer pathways are *components* of a card, and harm and benefit of one technology share a card
   - **D4:** card structure
   - **D11, D12:** tail flag and confidence, both computed
   - **D13:** mock data
   - **D14:** combining evidence
   - **D15:** how sources enter
   - **D16:** baselines
4. `docs/roadmap.md`: your card's row in "The cards" table gives its components; check its status and the scope cuts.
5. `docs/sources.md`: the step-by-step procedure for sources and claims, with a worked example.
6. **The worked example:** the data-centre air-pollution card. Read its source records (`sources/han-2026-*`, `chen-2026-*`, `muller-2026-*`, `shehabi-2024-*`), its claims (`claims/data-centre-air-pollution/`), its model (`models/data_centre_air_pollution.py`), its prose (`cards/data-centre-air-pollution.md`) and its output (`results/data-centre-air-pollution/card.md`). Copy its shape.

## Starting points per card

From the prior-work catalogue (`related_work/catalog.yaml`; read each entry's `accessed` field, since several were read only at abstract level). Treat these as a starting list, not as complete: search further for your card (see step 1).

| Card | Risk ID | Catalogue entries to start from | Notes |
|---|---|---|---|
| Clinical AI (net) | `clinical-ai` | Benefit: `masai-mammography-trial-2026`, `verma-chartwatch-2024`, `boussina-composer-sepsis-2024`, `el-arab-ai-cost-effectiveness-review-2025`, `vithlani-ai-economic-evaluations-2023`, `deloitte-ai-healthcare-europe-2020` (upper bound only). Harm: `lin-fda-ai-device-reporting-2025`, `handley-ai-fda-device-reports-2024`, `susanto-ml-cds-scoping-review-2023`, `draelos-llm-unsafe-medical-answers-2025`. Both: `fri-leap-wave10-benefits-2026` | Per-patient effects need an uptake figure (how many patients actually get the tool, globally) to become population DALYs |
| Biological misuse | `bio-misuse` | `righetti-govai-bioterrorism-2025` (already an expected-deaths Monte Carlo model), `williams-fri-llm-biorisk-2025`, `saeri-delphi-272-experts-2026`, `fri-leap-wave9-risks-2026`, `lancet-commission-threats-2026` | Replaces the mock card in `mock/`; leave the mock files in place |
| Chatbots and mental health (net) | `chatbots-mental-health` | Harm: `perlis-genai-depression-2026`, `olsen-chatbot-psychiatric-records-2026`. Benefit: `heinz-therabot-rct-2025`. Both: `fang-chatbot-psychosocial-rct-2025`, `fri-leap-introduction-2025` (exposure) | The prior-work search did not search therapy chatbots: do so |
| Cyberattacks on health and critical infrastructure | `cyber-health-infrastructure` | `barrett-saferai-cyber-2025`, `murray-saferai-methodology-2025`, `mcglave-ransomware-hospitals-2023`, `longtermwiki-ai-cyber-tail-2026` (weak), `saeri-delphi-272-experts-2026` | |
| Autonomous vehicles (net) | `autonomous-vehicles` | `iihs-waymo-crash-rates-2026`, `fri-leap-introduction-2025` (adoption) | Global deployment is small within the window; say so |
| Labour displacement | `labour-displacement` | `obrien-death-by-robots-2022`, `fri-leap-wave9-risks-2026` | Most harm is "not captured in DALYs"; list it there |
| Conflict and power concentration | `conflict-power` | `saeri-delphi-272-experts-2026` (weapons, power-centralisation subdomains), `wigley-autocratisation-uhc-2020`, `bollyky-democracy-mortality-2019`, `lancet-commission-threats-2026`, `rivera-llm-escalation-wargames-2024`, `karger-xpt-2023` | The card must say that autocratisation's measured health effects build up over about ten years, so most fall after 2031 |
| Environmental footprint | `environmental-footprint` | The existing US card's sources and claims; GBD claims 036–037 (global deaths and DALYs from ambient PM: use the GBD ratio, about 25 DALYs per death); `hsph-cork-datacentre-sites-2026` | Must be **global**. Decide with the maintainer whether to rename/move the existing `data-centre-air-pollution` files or start a new risk ID that cites them |
| Faster biomedical research | `biomedical-research` | `fri-leap-wave10-benefits-2026` | Evidence within the window is thin (roadmap); say so rather than stretch |

Risk IDs above are proposals; confirm with the maintainer if unsure.

## Prerequisite for net cards (the first one builds it)

Four cards are **net** (D2): clinical AI, chatbots and mental health, autonomous vehicles, and any other card with both a harm and a benefit component. The engine and card format do not support this yet: a model returns one quantity (DALYs lost), and the dotplot uses a log axis that cannot show a negative or zero-straddling net.

The first session that builds a net card must:
1. **Propose a design** to the maintainer before implementing. A suggested starting point:
   - Models may declare `COMPONENTS` (name → harm or benefit), and `simulate()` returns one array per component.
   - The engine reports each component and the net (harms − benefits), all in DALYs.
   - The card shows every component's distribution separately (each on its own log-scale dotplot) and the net as a signed figure with its interval.
   - The overview row is the net (D6 will need a symmetric-log or split axis; flag it for the website task).
2. **Record the agreed design** as a new decision in `docs/decisions.md`, and update the D5 text if the dotplot rule changes.
3. **Implement and test it** (`src/aiwelfare/engine.py`, `card.py`, `cli.py`, `tests/`) in the same pull request, with the existing cards still building unchanged.

## Steps

### 1. Find and read the evidence
- Start from the table above, then search for what it misses. In particular:
  - population-scale estimates
  - global (not single-country) figures
  - uptake or exposure numbers
  - independent estimates of the same quantity
- Log what you searched, as in `related_work/search_log.md`: add a short section for this card.
- **Read every source before extracting from it.** Cite the primary source, never press coverage (D15). Pin versions.
- If a key source is paywalled or blocked, **ask the maintainer to supply the PDF** (that is how the *Lancet* Commission was obtained). Do not work around access controls.

### 2. Register sources (D15, `docs/sources.md` §2)
- Use `datalad download-url` where the source can be downloaded; record `redistribution` honestly (most papers are `url-only`).
- For files the maintainer supplies, save them with `datalad save` and record the URL with `git annex registerurl`. See the *Lancet* sources for the pattern.
- **Never** commit IHME data, or anything else that may not be redistributed, into git. GBD lives in the `baselines/gbd/` subdataset, where every file is annexed.

### 3. Extract claims (`docs/sources.md` §3)
- **Atomic:** one quantity, one value or range, one condition set. Record units, geography, time window and conditions as the source states them; never convert in a claim.
- **Quote:** verbatim, under 25 words. Check every quote mechanically against the source text: extract the PDF text (e.g. with PyMuPDF, into the scratchpad, not the repo) and search for the quote, allowing only line-break hyphenation and whitespace differences.
- **Assumptions:** where no source gives a needed value (e.g. extrapolating a national figure to the world), write an `assumption` claim with a rationale and `replace_with`. Assumptions show up flagged on the card.
- **Tags:**
  - `work/<slug>` for passages that link a kind of work to the card
  - `not-captured/<slug>` for harms the DALY number leaves out
  - `access-mode/<mode>` for evidence on open-weight, API or locally-run frontier models

### 4. Write the model (`models/<risk_id>.py`)
- Follow the module contract at the top of `src/aiwelfare/engine.py`: `RISK`, `TITLE`, `GEOGRAPHY` (must be `"global"`), `WINDOW`, `COUNTERFACTUALS`, `NOT_MODELLED` (with a reason for each counterfactual you cannot model), `params(ds)`, `simulate(...)`. Optional: `ACCESS_MODES` and `access_shares()`, `STOCHASTIC`, `deaths()`.
- **Every parameter cites claims.** State in its `fit` text how the claims became a distribution. Fixed inputs are declared parameters too (`fixed(...)`, `fixed=True`), never hidden constants.
- **Probability × severity**, with distributions, not point values.
- **Where several sources estimate the same quantity**, keep one variant per source and mix them with equal weight (D14). Do not average them.
- **Keep it small and readable** (VISION.md: "a small, readable model"). Components are the card's sub-pathways; don't add a component the evidence cannot support. Say so in the card's limitations instead.

### 5. Write the prose (`cards/<risk-id>.md`)
Copy the frontmatter keys of `cards/data-centre-air-pollution.md`: `one_line`, `group` (D7), `scope_note`, `neighbour_for_flip`, `index_entries`, `cruxes` (plain-language high/low readings of the main parameters), `kinds_of_work` (descriptive only: **no tractability or neglectedness ratings**), `not_captured`, `limitations`. Plain-language sections: "Is this big?" and "Which AI does it come from?".

**Put no numbers in the prose:** every number on the card is generated. Quote `close_to_ml` values (`"yes"`, `"no"`): YAML reads bare yes/no as booleans.

### 6. Build and check
- `uv run aiwelfare validate`, `uv run pytest`, `uv run ruff check src tests models`.
- Commit the inputs, then build through DataLad: `uv run aiwelfare rerun risk/<risk-id>`. It records a `datalad run` commit with the card in `results/<risk-id>/`. Then check that `datalad rerun <that commit>` reproduces it with no changes.
- Read the generated card top to bottom as a reader would:
  - Does every section make sense?
  - Are the cruxes plausible?
  - Is the tail flag right?
  - Do the "dig deeper" commands work?
- Add tests for anything new you built (e.g. the net-card support).

### 7. Update the docs
- `docs/roadmap.md`: the card's status; anything you are parking goes under "Circle back to".
- `CLAUDE.md` "Current status", briefly.
- Commit messages say **why** the estimate is what it is (they feed the card's changelog).

## Ask the maintainer before

- **Changing the card's components or scope** (D2): e.g. dropping a component, or wanting to split the card.
- **Adding a decision or changing one:** the net-card design above, for instance.
- **Renaming or moving existing files** (e.g. the US air-pollution card when building the environmental-footprint card).
- **Adding a dependency or external service.**
- **Modifying a source file or claim that has already been published.** Add a new source or claim instead and supersede the old one.

## Done when

- The card builds through `aiwelfare rerun`, with every number traceable to claims and every assumption flagged.
- Its estimate is global and labelled with its counterfactual.
- Tests, validation and lint pass.
- The pull request explains what drives the estimate, what the main assumptions are, and what is parked.
