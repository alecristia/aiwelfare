---
# Hand-written prose for the data-centre air-pollution card (D4). Merged into the
# generated card by `aiwelfare build card`. No numbers here: every number on the
# card comes from the model and its claims.
id: data-centre-air-pollution
title: Air pollution from electricity for AI data centres
kind: risk
one_line: >-
  Power plants and backup generators that supply AI data centres emit fine particles and
  ozone precursors, which cause premature deaths downwind.
group: systemic-risks          # International AI Safety Report category (D7)
scope_note: >-
  Contiguous United States only. The three health studies cover all data centres; the AI
  share is attributed by the model.
neighbour_for_flip: null       # no neighbouring risk has a real estimate yet
index_entries: []              # MIT AI Risk Repository mapping not done yet (D3)

cruxes:                        # plain-language reading of each parameter's low and high end
  e2028:
    high: US data-centre electricity reaches the **top** of LBNL's 2028 scenario range
    low: US data-centre electricity stays at the **bottom** of LBNL's 2028 range
  dalys_per_death:
    high: each air-pollution death costs **many** years of healthy life
    low: these deaths fall mostly on the **very old**, costing few years each
  study:
    high: the **GEOS-Chem** model (Chen et al.) is the right one
    low: the **COBRA** model (Han et al.) is the right one
  post_2028_growth_ratio:
    high: data-centre growth after 2028 continues **at full pace**
    low: data-centre growth **halves** after 2028
  grid_trend_2031:
    high: the US grid gets **no cleaner** per TWh by 2031
    low: the US grid gets **much cleaner** per TWh by 2031
  rate_ap4:
    high: the **high** dose-response function holds (AP4 variant)
    low: the **default** dose-response function holds (AP4 variant)
  conventional_growth:
    high: non-AI data-centre demand grows **fast**, so less of the growth is AI
    low: non-AI data-centre demand **stays flat**, so more of the growth is AI

kinds_of_work:
  - slug: energy-efficient-ml
    name: More energy-efficient training and inference (hardware, models, serving)
    close_to_ml: "very"
    where: AI labs, chip makers, academia
  - slug: workload-scheduling
    name: Shifting AI workloads in time to cleaner hours
    close_to_ml: "yes"
    where: AI labs and cloud providers (scheduling and serving teams)
  - slug: health-informed-siting-and-load-shifting
    name: Health-informed siting of data centres and shifting load between regions
    close_to_ml: "partly"
    where: Cloud providers, academia (computing systems), grid operators
  - slug: clean-energy-procurement
    name: Clean-energy procurement for data centres
    close_to_ml: "no"
    where: Cloud providers, utilities
  - slug: cleaner-backup-generation
    name: Cleaner backup generation (newer-tier diesel, alternatives to diesel)
    close_to_ml: "no"
    where: Data-centre operators, state air regulators
  - slug: health-impact-reporting
    name: Reporting air pollutants and health impacts alongside energy use
    close_to_ml: "no"
    where: AI companies' sustainability teams, regulators

not_captured:
  - slug: climate
    text: Climate damage from the same electricity's greenhouse-gas emissions
  - slug: morbidity
    text: Asthma symptoms and other illness, which the DALY conversion treats as small
  - slug: near-facility-and-equity
    text: Local exposure near facilities, and who bears it
  - slug: outside-us
    text: Data centres outside the United States
  - slug: after-2031
    text: Anything after 2031

limitations:
  - US only; no source read yet gives a global estimate.
  - None of the three health studies is AI-specific; AI's share of data-centre electricity is attributed in the model, from two estimates that disagree.
  - The conversion from deaths to DALYs is a placeholder assumption until a GBD-derived source is added.
  - No source projects US data-centre electricity beyond 2028; 2029–2031 extrapolates under an assumption.
  - The GEOS-Chem interval covers concentration-response uncertainty only.
---

## Is this big?

The harm is spread over many people downwind of power plants, a little at a time, rather than
coming from rare events. Most of the uncertainty is about how fast data-centre electricity
grows and how many years of life each death costs, not about whether harm happens at all.

## Which AI does it come from?

Electricity use is not yet split by how models are accessed. Training and serving of large
models run in large data centres whichever way their weights are distributed.
