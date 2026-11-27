# Task: build the website and parameter explorer

A self-contained brief for a separate session. Written 2026-11-27.

## Goal

Build the static website that is the repo's front door (VISION.md, "How: four layers", layers 2 and 3): an **overview chart that doubles as the parameter explorer**, one **page per card**, and the **scope cuts** listed alongside. It must be generated entirely from the repo's data and run with no server.

The site is the reader's first contact with the estimates. Readers are ML engineers, mostly **outside the United States**, deciding whether and where to work on AI safety.

## Read first

1. `CLAUDE.md`: hard rules, layout, how to run the package and tests.
2. `VISION.md`: especially "What 'interrogate' means", the scope decisions, and Modelling decisions 7 ("Estimates do not add up").
3. `docs/decisions.md`. These are binding:
   - **D4:** card structure
   - **D5:** quantile dotplots on cards; no violin or density plots
   - **D6:** overview chart = parameter explorer; a forest plot; baselines as reference lines
   - **D7:** grouping and filters
   - **D8:** static hosting, in-browser runtime
   - **D9:** no chatbot
   - **D10:** the site computes nothing the CLI cannot reproduce
   - **D11, D12:** tail-dominated flag, confidence
   - **D13:** mock data and banners
   - **D16:** baselines are global GBD risk factors

   If anything below conflicts with a decision, the decision wins: stop and tell the maintainer.
4. `docs/roadmap.md`: the nine cards, the scope cuts, and which cards exist.
5. Look at the built outputs before designing anything:
   - `results/data-centre-air-pollution/` (`card.md`, `card.json`, `dotplot.svg`)
   - `mock/build/bio-misuse/`
   - the output of `uv run aiwelfare show risk/bio-misuse --include-mock --json`

## What exists to build on

- **Per-card results:** `aiwelfare build card <risk>` writes `card.md`, `dotplot.svg` and `card.json`.
  - `card.json` holds everything the card shows: summary, all three counterfactuals, cruxes, confidence, variants, the breakdown, parameters, evidence, assumptions, kinds of work, leaves-out, provenance, changelog and the `mock` flag.
  - Real cards live in `results/<risk>/` (built through `datalad run`); mock cards in `mock/build/<risk>/`.
- **Models:** `models/<risk_id>.py` are plain Python and NumPy, with declared parameters (`aiwelfare model <risk> --json`).
  - Each parameter has a description, the claims behind it, its evidence basis and how it was fitted.
  - The engine (`src/aiwelfare/engine.py`) runs them with a fixed seed.
- **Baselines:** `baselines/<id>.yaml`. **None exist yet.** The six GBD risk factors are being downloaded by the maintainer (roadmap, "Now", item 1). Until they arrive, use the two mock baselines in `mock/baselines/`, labelled as invented.

## What to build

### 1. A site generator inside the package
Add `aiwelfare build site` (with `--json`, like every command, D10). It writes the static site to `site/` from the repo's data and is the only way the site is produced. `site/` is never hand-edited.

### 2. Overview chart = parameter explorer (D6)
- A **forest plot**, one row per card:
  - global DALYs, 2026–2031, on a log scale
  - a dot for the median, a bar for the 90% interval, a hollow diamond for the expected value
  - **dashed bars for tail-dominated rows** (D11)
  - risks and benefits in two colours on the same axis
  - rows grouped by International AI Safety Report category plus a benefits group (D7); within groups, sorted by expected value and re-sorted when parameters change
- **Baselines as labelled vertical reference lines**, not rows (D6, D16).
- **No total row.** Estimates overlap and are not summed (VISION.md, Modelling decisions 7). Say so in one line under the chart.
- **A counterfactual switch** with the three options; the selected one is always labelled. Where a card does not model a counterfactual, show that it is "not modelled" with the card's stated reason, never a blank or a zero.
- **Sliders generated from each model's declared parameters**, top cruxes first (`aiwelfare cruxes`). Categorical parameters (e.g. which study a variant uses) become selectors.
- **Guarding against misquotation (D6):**
  - a canonical default chart, always one click away
  - a visible banner whenever settings differ from the defaults
  - every setting encoded in the URL
- **Directly below the chart:**
  - the **scope cuts** from `docs/roadmap.md` (loss of control, health misinformation, financial disruption), with their reasons
  - the "not captured in DALYs" items

### 3. One page per card (D4)
Render each card in D4 order, from `card.json` and `card.md`, with its dotplot. Keep the "for checking" section collapsed. Each section's "dig deeper" CLI commands stay visible: they are how readers go further.

### 4. Which cards appear
- **Only global cards appear.** The air-pollution card is US only (`geography` in `card.json`). Exclude it from the overview and from the public pages; you may use it as a development fixture.
- **Mock cards appear only in a clearly separate demo build**, with the D13 banner on every page, chart and screenshot-able view. They must never sit next to real rows on the canonical chart.

## The explorer must not compute anything the CLI cannot reproduce (D10)

D8 allows Shinylive (Python in the browser) or Observable Framework. Choose with this constraint in mind:
- **Shinylive (recommended):** the browser runs the **same** model code and engine (NumPy runs in Pyodide), so every number the explorer shows is reproducible with `aiwelfare whatif`. Check load time and the draw count needed for interactive speed. A lower draw count in the browser is acceptable if the page says so and the canonical chart uses the CLI's results.
- **Observable Framework:** the models would have to be reimplemented in JavaScript (two implementations that can drift: avoid), or results **precomputed over a grid of parameter values** by the CLI and interpolated (D8). If you take this route, the grid must come from an `aiwelfare` command.

Whichever you choose, state it in `docs/decisions.md` (D8 currently leaves the choice open), in the same pull request.

## Acceptance tests

The site must let a reader answer these VISION.md questions at a glance:
1. the best estimate for a card and what it rests on
2. how it compares with the baselines
3. which risks the literature ranks largest (here, by expected value)
4. what you would have to believe for one card to exceed another (cruxes and sliders)
5. which harms are not captured, and which pathways are cut from scope

Plus:
- `uv run pytest` covers the generator:
  - every real card appears
  - no US-only or mock card appears on the canonical chart
  - the mock banner is present wherever mock data is
  - URL parameters round-trip
  - the explorer's default numbers equal the CLI's
- `uv run aiwelfare build site` from a clean checkout reproduces `site/` exactly (fixed seeds).
- The site works when served from a plain static file server (`python -m http.server` in `site/`), with no network calls beyond loading its own files and runtime.

## Ask the maintainer before

- **Publishing anywhere:**
  - GitHub Pages and a CI workflow to build the site are new external services (`CLAUDE.md`).
  - Build locally first and show the maintainer.
- **Adding heavy dependencies:** check before adding anything beyond the Shinylive or Observable toolchain.
- **Visual details D7 defers:** colours, row counts, layout. Propose them and show screenshots; don't settle them alone.

## Out of scope

- **New cards, models or claims:** this task presents what exists.
- **Tractability or neglectedness:** no ratings of any kind, including in the kinds-of-work tables (`CLAUDE.md`).
- **A chatbot** (D9).
- **A total-AI number** (VISION.md, Modelling decisions 7).

## Timing

The roadmap schedules this after the clinical-AI and real bio-misuse cards, so that the overview has real rows. You can build the generator, templates and explorer now against the existing outputs (air pollution as a fixture; mock bio misuse and mock baselines in the demo build), and switch to real rows as they land.
