# Roadmap

What we are working on **now**, and what we will **circle back to**. Update this file when a strand starts, finishes or changes status. Each item says where its details live. Decisions themselves stay in `docs/decisions.md`; this file only tracks work.

Last updated: 2026-11-27.

---

## Risk and benefit register

The single list of risks and benefits being considered, with their status. A card is added only with the maintainer's approval, after checking D2. Evidence for each candidate: `docs/related-work.md` ("Candidate new risk cards") and `related_work/catalog.yaml`. D2 expects 15–30 cards in total, so this list is incomplete. The D3 mapping (below) is the systematic way to complete it.

| Risk or benefit | Kind | Status | Notes |
|---|---|---|---|
| Data-centre air pollution | risk | **Built** (real data, US only) | `results/data-centre-air-pollution/card.md` |
| AI-assisted biological misuse | risk | **Built with mock data** | `mock/build/bio-misuse/card.md`. Real version planned: Righetti (GovAI 2025) is a ready-made model |
| AI errors in clinical care (`clinical-errors`) | risk | Planned | Named in the example card. Consumer chatbot medical-advice errors probably merge into it |
| Autonomous vehicles | benefit (and harm) | Approved 2026-11-27 | |
| AI-enabled cyberattacks on health and critical infrastructure | risk | Approved 2026-11-27 | |
| Clinical-AI diagnostics and monitoring | benefit | Approved 2026-11-27 | |
| Chatbot mental-health harm | risk | Approved 2026-11-27 | |
| Labour displacement → mortality | risk | Approved 2026-11-27 | Most harm likely "not captured in DALYs"; far from ML engineering |
| Chatbot mental-health benefit | benefit | Candidate, awaiting decision | Borderline on D2 (2): one RCT. Could be the benefit side of the harm card |
| AI-enabled power concentration / autocratisation | risk | Candidate, awaiting decision | Borderline on D2 (2). Found in prior-work round 5 |
| AI in armed conflict | risk | Candidate, fails D2 (2) for now | Revisit once Saeri et al.'s weapons subdomain is extracted |
| AI errors in critical infrastructure (malfunction) | risk | Candidate, fails D2 (2) for now | Revisit once LEAP wave reports are extracted |
| AI-accelerated biomedical research | benefit | Candidate, fails D2 (2) within 2026–2031 | Register entry only, for now |

---

## Now

### 1. Health baselines (GBD / WHO)
**Why now:** every card's magnitude line needs baselines (D4, D6), and the air-pollution card currently says "no sourced baselines yet". The same data would replace that card's placeholder DALYs-per-death assumption.
**Work:** GBD as a DataLad subdataset (approved 2026-11-27), tracked by URL and checksum only under IHME's terms (D1). Six baselines, two per GBD level-1 cause group, as causes rather than risk factors, global and US values, latest GBD year held constant over the window:
- non-communicable: neoplasms, diabetes mellitus
- communicable, maternal, neonatal and nutritional: malaria, nutritional deficiencies
- injuries: road injuries, interpersonal violence

**Needs the maintainer:** confirm the adjustments proposed on 2026-11-27 (causes not risk factors; interpersonal violence rather than conflict; US values alongside global). GBD exports need an IHME login, so the maintainer may need to download the files.

### 2. First cards, through the milestone-1 pipeline
Each card: register sources → extract claims → model → prose → `aiwelfare rerun`. Order confirmed 2026-11-27:
1. **Clinical-AI diagnostics and monitoring benefit**: puts a benefit on the chart, so harms are not shown alone.
2. **Bio-misuse, real**: replaces the mock card, starting from Righetti's model.

### 3. Website and explorer (D6, D8), after bio misuse
**Why here:** with three real cards (air pollution, clinical-AI benefit, bio misuse), the overview has a benefit, a tail-dominated risk and a steady harm to show, enough to test the forest plot, sliders and counterfactual switch on real data. Later cards then appear on the site as they are built.
**Work:** static site generated from `results/` (D8, D10: nothing computed that the CLI cannot reproduce); forest-plot overview with baselines as reference lines (D6); in-browser explorer (Shinylive or Observable Framework, D8).

### 4. Remaining cards, continuing the order above
3. **Chatbot mental-health harm**
4. **AI-enabled cyberattacks on health and critical infrastructure**
5. **Autonomous vehicles**
6. **Labour displacement → mortality**
7. **`clinical-errors`**

The criterion for this order is a mix of how much evidence is ready and having both harms and benefits early. It is not a judgement of importance.

---

## Circle back to

### Literature review (prior-work search)
Status: rounds 1–5 done and merged (PRs #1, #2). Open items:
- Read the *Lancet* Commission appendix (AI method, pp 109–14); the main text is read.
- Extract Saeri et al.'s subdomain figures (power centralisation, weapons) from the full text.
- Decide on the round-5 candidate cards (register above).
- Retry the items under "Not accessed" in `docs/related-work.md`.
- Known blind spots: non-English literature; pathways the brief did not name (the D3 mapping below is the check).

### D3: map the MIT AI Risk Repository to cards
Every entry goes to a card or to the "not captured in DALYs" register; unmapped entries are coverage gaps. This is how the register above gets completed. Cards currently say "mapping not done yet".

### Air-pollution card: known gaps
Listed under the card's "Known limitations": global extension beyond the US, the DALYs-per-death source (see baselines, above), the `open-only` counterfactual, the access-mode breakdown, and a source for energy-efficient ML.

### Overview chart details (D7)
Row counts, colours and layout: deferred by D7 until real estimates exist.
