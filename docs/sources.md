# How sources are integrated

This is the procedure behind decision D15. It describes how a piece of evidence travels from a publisher's website to a number on a risk card, and what each step must record. The worked example throughout is the data-centre air-pollution card.

```
publisher ──► sources/<id>/          what the evidence is, where it came from, pinned version
          ──► claims/<risk>/<n>.yaml what one passage of it says (no judgement)
          ──► models/<risk>.py       how claims become distributions and combine (judgement)
          ──► cards, CLI, site       generated, never hand-edited
```

## 1. Find the primary source

- News coverage, blog posts and summaries are for **finding** sources only. Follow them to the paper, dataset or report they describe.
  - Example: the UC Riverside news release (Dec 2024) cites "as many as 1,300 premature deaths a year by 2030". The paper it describes, arXiv:2412.06288, has since been revised: v4 (June 2026) gives **1,262 deaths in 2028** under the high-growth scenario (Table 1). The card cites v4, Table 1, not the release.
- Look for **independent estimates of the same quantity**. Disagreement is kept (VISION.md, Design principles), so a single source is a weakness to flag, not a convenience.
  - Example: the air-pollution card has three independent models of the same quantity, deaths from US data-centre electricity: COBRA (Han et al.), GEOS-Chem (Chen et al.) and AP4 (Muller).
- Read the source before extracting anything from it. Never add a source from a snippet or from memory.

## 2. Register the source

Create `sources/<source-id>/source.yaml` (schema: `src/aiwelfare/schema/source.schema.yaml`), then add the file:

```
datalad download-url -d . -O sources/<source-id>/ <url>
```

- **`id`**: `<first-author>-<year>-<short-slug>`, kebab-case. It never changes, even if the source is retitled.
- **`version`**: the exact version read (e.g. `arXiv v4, 2026-06-08`). If a new version appears, add it as a **new source** with its own ID and mark the old one `superseded_by`. Never silently swap the file under an existing ID: published claims point to it.
- **`redistribution`** controls what DataLad does with the file:
  - `open` (e.g. CC BY): the file is downloaded, annexed and mirrored.
  - `url-only` (most papers, "all rights reserved", arXiv's default licence): `download-url` records the URL and checksum. The content stays in the local annex and is never pushed to a public remote.
- **`type`**, **`evidence_date`**, **`author_interests`**: see VISION.md, Sources. Record interests factually ("funded by X", "authors operate data centres"), with no verdict.

## 3. Extract claims

One file per claim in `claims/<risk-id>/`, named `<risk-id>-<nnn>.yaml` (schema: `src/aiwelfare/schema/claim.schema.yaml`).

A claim records **what one passage of the source says**, in the source's own units, scope and conditions:

- **Atomic:** one quantity, one value or range, one condition set. A table row with a midpoint and a range is one claim. Two scenarios are two claims.
- **Locator:** page, section, table or figure, precise enough for someone to find the passage in under a minute.
- **Quote:** under 25 words, verbatim. If the number sits in a table, quote the row label and describe the cells in `notes`.
- **Value:** `point`, `interval` (with its `kind`: a 95% CI, a scenario range or a range across models are not the same thing) or `quantiles`. Never convert units or rescale in a claim.
- **Scope fields** (`geography`, `time_window`, `counterfactual`, `conditions`): state what the source covers, even when it doesn't match the repo's scope. Mismatches are resolved in the model, where they are visible.
- **Second-hand values:** if source A reports a number from source B, the claim belongs to A and names B in `derived_from`. Prefer extracting from B directly when it can be read.
- **Assumptions:** where a model needs a value no source gives, write a claim with `claim_type: assumption`, `source: null` and a `rationale`. It is flagged on the card and counts as speculation for the confidence rating (D12) unless its evidence basis says otherwise. Each assumption should say what source would replace it.

## 4. Use claims in a model

Each model parameter cites the claims it is fitted to. The model, not the claim, decides:

- **which distribution to fit**: e.g. a lognormal through a stated low and high, with the interpretation of the range written in the parameter description
- **how to reconcile scope**: e.g. dividing deaths by TWh to get a rate per TWh, or a source's 2023 estimate applied to 2026–2031 electricity scenarios
- **how to combine sources**: one variant per source, mixed with equal weights by default (D14)

Run `aiwelfare validate` before committing. It checks every file against its schema, that every claim's `source` exists, that every model parameter's claims exist, and the quote length.

## 5. Commit

The commit message says **why** the evidence changed, e.g. "Add Chen et al. 2026 (GEOS-Chem): third independent estimate; higher than COBRA-based Han et al." The changelog digest is generated from these messages.

## Worked example: data-centre air pollution

| Step | What was done |
|---|---|
| Found | UC Riverside news release → arXiv:2412.06288 (read v4). The paper's discussion and an MIT news item → Chen et al. 2026 and Muller 2026. |
| Registered | `han-2026-health-informed-computing` (arXiv v4, url-only) · `chen-2026-data-center-air-quality` (ERL, CC BY 4.0, open) · `muller-2026-data-center-damages` (NBER WP 35100, url-only) · `shehabi-2024-us-data-center-energy` (LBNL report) |
| Extracted | deaths and TWh per study and year; LBNL's 2028 electricity scenarios; the AI-server share of server electricity; Chen's comparison of the three estimates |
| Model | deaths per TWh, one variant per study × US data-centre TWh 2026–2031 × AI share × DALYs per death (assumption, pending a GBD-derived source) |
| Gaps logged | no global estimate (US only), no AI-specific attribution from the health studies themselves, DALYs per death not yet sourced |
