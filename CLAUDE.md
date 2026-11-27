# CLAUDE.md

Guidance for coding agents (Claude Code and others) working in this repository.

## What this project is

This repo estimates the health impact of AI over the next five years (2026–2031), in DALYs, risk by risk and benefit by benefit, with every number traceable to its sources. Its readers are ML engineers deciding whether, and where, to work on AI safety.

## Read before working

1. **`VISION.md`.** The question, scope, sources, modelling approach, and the limitations of each choice. Read it before any change that touches scope, sources or method.
2. **`docs/decisions.md`.** Binding implementation decisions (D1, D2, …). Follow them. If a task conflicts with a decision, **stop and say so**: propose an edit to `docs/decisions.md` instead of working around it.
3. **`docs/examples/risk-card-bio-misuse.md`.** The reference format for risk cards and the proposed `aiwelfare` CLI commands.

Do not copy content from these files into this one; point to them.

## Current status

**Milestone 1 done (2026-11-27).** The package, schemas and CLI exist. One real card (data-centre air pollution, US only) and one mock card (bio misuse, `mock/`) are built end to end. Run `uv run aiwelfare --help`; run `uv run pytest` and `uv run aiwelfare validate` before committing.

## Layout

```
sources/<id>/       source.yaml + the file, tracked by DataLad (D1, D15; procedure: docs/sources.md)
claims/<risk-id>/   Atomic claims as YAML, one file per claim
baselines/          Health baselines as <id>.yaml (none real yet; GBD/WHO to come as DataLad subdatasets)
models/<risk_id>.py One model per card (snake_case module, kebab-case risk ID), declared parameters
cards/<risk-id>.md  Hand-written prose for each card (frontmatter + plain-language sections)
results/<risk-id>/  Generated card.md, dotplot.svg, card.json. Only via `aiwelfare rerun` (datalad run)
mock/               Invented data mirroring the tree above (D13); mock/build/ holds generated mock cards
src/aiwelfare/      Python package and CLI (schema/, data.py, engine.py, card.py, dotplot.py, cli.py)
site/               Generated static website (not started). Never hand-edited; built in CI
docs/               VISION-level docs, decisions, examples, related work
related_work/       Prior-work catalogue and search log
tests/
```

## Hard rules

### Numbers and evidence
- **Never invent a number.** Every numeric input traces to one or more claim IDs.
- If a model needs a value that no source gives, record it as a claim of type `assumption` with a written rationale. It shows up flagged on the card.
- **Mock data** (fixtures, examples, demos) must be labelled as invented, both in the data and in any rendered output.
- **Claims are atomic.** Each claim records:
  - source ID and an exact locator (page, section, table)
  - a short supporting quote **under 25 words**; paraphrase anything longer
  - value or distribution, units, conditions, time window
  - evidence type, evidence basis (measured / modelled / expert judgement / speculation) and author interests (see VISION.md, Sources)
- **Extraction separate from judgement.** Claims record what a source *says*. How claims are combined lives in models, never in claim files.

### Provenance and reproducibility (D1)
- **Add sources with `datalad download-url`**, which records the URL and checksum.
- **Do not commit content the repo may not redistribute** (most papers, IHME data). Track it by URL and checksum only.
- **Anything that produces published numbers runs through `datalad run`.** Use fixed random seeds.
- **Never hand-edit generated files** (cards, site, results). Change the inputs and regenerate.

### Modelling (VISION.md, Modelling decisions)
- Models use Monte Carlo uncertainty propagation in NumPy: probability × severity, with distributions fitted to claims. **No Bayesian inference** in v1.
- Every model declares its parameters: name, distribution, claim IDs, description. Sliders and the `cruxes` command are generated from these declarations.
- Every result is labelled with its counterfactual (no modern AI / frozen at 2026 / only open models advance).
- **Scope:** DALYs only, 2026–2031, and scale only. **No tractability or neglectedness judgements**, including in the "kinds of work" sections, which describe work and never rate it.

### Interfaces
- Risk cards follow D4 exactly. Every section ends with "dig deeper" CLI commands.
- Every CLI command supports `--json`. The website must not compute anything the CLI cannot reproduce (D10).
- The site is static, with no server (D8). There is no built-in chatbot (D9).

## Ask the maintainer before

- adding, merging or splitting a risk card (check the D2 criteria first)
- changing counterfactual definitions, the time window, or the unit
- changing any decision in `docs/decisions.md`
- adding a heavy dependency or a new external service
- modifying a source file or claim that has already been published

## Conventions

- Python ≥ 3.11, managed with `uv`. Lint and format with `ruff`. Test with `pytest`.
- Claim, source and baseline files are YAML, validated against the schemas in `src/aiwelfare/schema/`.
- Commit messages say *why* an estimate changed, not just what. Cards' changelogs and `aiwelfare log` are generated from them.
