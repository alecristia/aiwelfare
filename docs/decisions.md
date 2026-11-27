# Design decisions

This file records decisions made while designing the repo, so that implementation (including by coding agents such as Claude Code) follows them. `VISION.md` says *what* the repo is for; this file says *how* specific parts must work.

Each decision has a status:
- **Decided:** implement as written.
- **Deferred:** revisit once real estimates exist.

To change a decision, edit it here in the same pull request as the code change, and say why.

---

## D1. Data provenance: DataLad

**Status:** Decided

- The repo is a DataLad dataset. Large external datasets (GBD extracts, IHME forecasts, WHO estimates) are DataLad subdatasets.
- Sources are added with `datalad download-url`, which records the origin URL and checksum. A source whose content changes at the same URL is detected by checksum mismatch.
- Every model run that produces published numbers goes through `datalad run`, so each result is linked to the exact command, inputs and outputs. `datalad rerun` must reproduce it.
- **Licensing:** sources the repo may not redistribute (most papers; IHME data under its terms of use) are tracked by URL and checksum only. Users fetch them from the publisher with `datalad get`. Openly licensed sources are also mirrored to guard against broken links.
- Contributors should not need to learn git-annex: common operations are wrapped in documented commands (see D10).

## D2. What gets a risk card

**Status:** Decided

A risk or benefit gets its own card only if **all three** hold:
1. **It has a distinct causal pathway to DALYs**, with its own probability × severity model.
2. **It needs its own evidence.** If two candidates would be modelled from the same sources, they share one card.
3. **It matters for the reader's decision.** If two candidates would be addressed by different kinds of work, they get separate cards.

The expected total is **15–30 cards**, risks and benefits combined.

## D3. External taxonomies are indexes, not cards

**Status:** Decided

- Every entry in the MIT AI Risk Repository (1,600+ risks from 65 frameworks as of v4, December 2025) is mapped to **either** a card **or** the "not captured in DALYs" register.
- An entry that maps to neither is a coverage gap and must be logged as an issue.
- The International AI Safety Report's categories (malicious use, malfunctions, systemic risks) are used to group cards (see D7).

## D4. Risk card structure

**Status:** Decided. Reference implementation: `docs/examples/risk-card-bio-misuse.md`

Cards are organised around the reader's decision, not the model's internals. They are modelled on formats the audience already knows: Hugging Face model cards (summary first, limitations prominent), security advisories (severity, affected versions and change history in the header), and 80,000 Hours problem profiles (what would change my mind; what next).

**Order of sections (fixed):**

1. **Header box:**
   - one-line description
   - expected harm with range
   - magnitude relative to baselines: the order of magnitude and the ratio to each baseline (e.g. "~3×10⁵ DALYs · 0.004× malaria"). Size bands are deferred until real estimates exist.
   - confidence (computed, D12), with a tail-dominated flag where it applies (D11)
   - share by access mode (open-weight / API / locally-run frontier)
   - selected counterfactual
2. **Is this big?** In plain language, with a quantile dotplot (D5).
3. **Why it might be much bigger or smaller:** cruxes as "if you believe… the estimate moves…", plus what it would take for the ranking against a named neighbour to flip.
4. **Which AI does it come from?** The breakdown by access mode.
5. **What kinds of work target this risk?** Descriptive only, with no tractability judgement (out of scope per `VISION.md`). Includes a "close to ML engineering?" column and where the work is done.
6. **What this number leaves out:** harms not captured in DALYs, and harms after 2031.
7. **For checking** (collapsed by default):
   - all three counterfactuals
   - model components
   - evidence shown separately by type
   - known limitations
   - index entries (D3)
   - provenance (D1)
   - changelog

**Rules:**
- **Every section ends with "dig deeper" CLI commands** that return the underlying data and references for that section (D10). In particular, the kinds-of-work section has a command listing the sources that link each kind of work to the risk.
- **Cards are generated from the data and models, never hand-edited.** Hand-written prose (one-line description, plain-language explanations) lives in the card's source file and is merged in at build time.
- **Mock-ups and examples carry a visible "invented numbers" banner** at the top and bottom.

## D5. Distributions on cards: quantile dotplots

**Status:** Decided

- Risk cards show each distribution as a **quantile dotplot** (e.g. 20 dots, each 5% of simulated futures). Evidence from visualisation research (Kay, Hullman et al.) suggests non-specialists read these more accurately than densities or intervals.
- Outcomes of "nothing happens" (zero DALYs) are shown in **a separate column left of the log axis**, so the point mass at zero stays visible.
- **No violin or density plots.** On a log scale they cannot show the zero mass, and would misrepresent exactly the tail-dominated risks that matter most.
- Dotplots appear on cards only. The overview chart stays simpler (D6).

## D6. Overview chart and parameter explorer: one interface

**Status:** Decided

- **They are merged.** The overview chart is the parameter explorer at default settings. Changing a parameter visibly moves a risk within the overall ranking.
- **The chart is a forest plot**, one row per risk or benefit:
  - global DALYs, 2026–2031, on a **log scale**
  - a dot for the median, a bar for the 90% interval, a hollow diamond for the expected value
  - **dashed interval bars** for tail-dominated rows
  - risks and benefits in two colours, on the same axis
  - rows sorted by expected value, and re-sorted when parameters change
  - clicking a row opens its risk card
- **The baselines (malaria, TB, road injuries…) are labelled vertical reference lines**, not rows, so every risk is read directly against them.
- **A counterfactual switch** offers the three options from `VISION.md`, with the selected one always labelled.
- **Sliders** are generated automatically from each model's declared parameters, starting with the top cruxes.
- **A "not captured in DALYs" list sits directly below the chart**, so non-health harms are not silently missing from the overview.
- **Guarding against misquotation:**
  - A canonical static default chart is always available for citing.
  - A visible banner appears whenever settings differ from the defaults (e.g. "Your assumptions: bio uplift 3×").
  - All parameters are encoded in the URL, so any screenshot can be traced to its settings.

## D7. Handling many rows

**Status:** Decided (principles); deferred (visual details)

- **Grouping:** rows are grouped by International AI Safety Report category (malicious use, malfunctions, systemic risks) plus a benefits group. Each group has a summary row and can be expanded.
- **Default view:** the top 10 by expected value under the current settings, with "show all".
- **Filters that match the reader's decision:**
  - close to ML engineering (from the D4 kinds-of-work data)
  - tail-dominated only
  - by access mode
- **Deferred until real estimates exist:** exact row counts, whether a compact dotplot fits in the overview, colours, and layout details.

## D8. Hosting: static, no server

**Status:** Decided

- The website (cards, chart, explorer) is a static site, e.g. on GitHub Pages. It must not depend on a running server.
- The interactive explorer uses an in-browser runtime: **Shinylive** (Python Shiny compiled to run in the browser) or **Observable Framework**. Classic Shiny and Streamlit are rejected because they need a server.
- If a model is too heavy to run in the browser, its results are **precomputed over a grid of parameter values** and interpolated in the browser.

## D9. No built-in chatbot

**Status:** Decided (see `VISION.md`, layer 4)

The repo ships no AI question-answering interface. It is made agent-ready instead:
- structured data
- a documented CLI with `--json` output (D10)
- an agent guide (`CLAUDE.md`)

Readers bring their own agents.

## D10. CLI: `aiwelfare`

**Status:** Decided (principles); command names provisional

- One CLI is the shared backbone for readers, agents and the website build. The website and cards must not compute anything the CLI cannot reproduce.
- **Every risk-card section maps to at least one command** (see the example card for the proposed set: `show`, `dist`, `compare`, `cruxes`, `whatif`, `flip`, `claims`, `breakdown`, `work`, `refs`, `not-captured`, `model`, `sources`, `rerun`, `log`).
- **Every command supports `--json`** for agents and scripts. Human-readable output is the default.
- Every output that contains a number states the counterfactual and the parameter settings used.
- DataLad operations that contributors need are exposed as subcommands, so they don't have to learn git-annex.

## D11. Tail-dominated flag

**Status:** Decided

- A result is **tail-dominated** if the top 5% of simulated outcomes contribute more than 50% of the expected value, under the selected counterfactual.
- The flag is computed, never set by hand. Cards and the overview chart show it (D4, D6), together with the share of the expected value coming from the top 5%.

## D12. Confidence rating

**Status:** Decided (first approach; revisit once several cards exist)

Confidence is computed from the model, never set by hand:
- **Low** if the result is tail-dominated (D11), **or** if more than 50% of the crux swing comes from parameters whose claims are all expert judgement or speculation.
- **High** if the result is not tail-dominated **and** more than 50% of the crux swing comes from parameters backed by at least one measured claim.
- **Medium** otherwise.

Definitions:
- **Crux swing** of a parameter: the factor by which the expected value changes when that parameter alone moves from its 5th to its 95th percentile, others held at their full distributions. Shares are computed on the log of the swing.
- `assumption` claims count as speculation unless their evidence basis says otherwise.
- The card prints the inputs behind the rating (tail share, swing shares by evidence basis), not just the label.

## D13. Mock data

**Status:** Decided

- Invented data lives only under `mock/`, which mirrors the real layout (`mock/sources`, `mock/claims`, `mock/models`, `mock/cards`). Every mock file also carries `mock: true`; the validator rejects `mock: true` outside `mock/` and `mock: false` inside it.
- The CLI reads the real tree by default. `--include-mock` overlays `mock/` on top of it. Any output that touches a mock file carries the "invented numbers" banner (D4), whatever the template says.
- Mock runs do **not** go through `datalad run` (they produce no published numbers). Their outputs are committed and pushed under `mock/build/`, so the git history keeps a log of them.

## D14. Combining evidence

**Status:** Decided for v1 (see the limitation in `VISION.md`, Modelling decisions, point 5)

- Where several sources estimate the same quantity, the model keeps one variant per source. Variants are **mixed** (each simulated future draws from one variant), not averaged, so disagreement stays visible as spread.
- The card shows the result separately for each evidence type and, within a type, for each source when there are few of them.
- The default combined figure gives **equal weight to each evidence type**, and equal weight to each source within a type. Readers can change the weights (`whatif --weights`); any combined figure states the weights it used.

## D15. How sources enter the repo

**Status:** Decided. Procedure: `docs/sources.md`

- A source enters through one path: `sources/<source-id>/source.yaml` plus the file, added with `datalad download-url` (D1), then atomic claims in `claims/<risk-id>/`, then model parameters that cite claim IDs.
- **The primary source is cited, not its press coverage.** News articles may be used to find a source, never as one.
- **Versions are pinned:** for preprints, the arXiv (or equivalent) version that was read; for living documents, the access date.
- Values a model derives from claims (unit conversions, ratios, extrapolations) are computed in the model, not stored as claims. A value another source derives from a third source is recorded as a claim of the citing source, with the original source noted.
