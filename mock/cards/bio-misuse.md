---
# MOCK card source (D13): invented prose for the format demonstration.
id: bio-misuse
title: AI-assisted biological misuse (MOCK)
kind: risk
one_line: >-
  MOCK: AI models help someone cause a disease outbreak they couldn't otherwise have caused.
group: malicious-use
scope_note: ""
neighbour_for_flip: data-centre-air-pollution
index_entries: []
cruxes:
  severity:
    high: a **pandemic-scale** outcome is plausible within five years
    low: outcomes are capped at a **local** epidemic
  post_2026_share:
    high: most of the risk comes from capabilities **after** 2026
    low: much of the risk is **already** present in 2026 models
kinds_of_work:
  - slug: dangerous-capability-evals
    name: Dangerous-capability evaluations
    close_to_ml: "very"
    where: AI labs, government AI security institutes, independent evaluators
  - slug: misuse-classifiers
    name: Misuse classifiers and monitoring for API models
    close_to_ml: "very"
    where: AI labs
  - slug: tamper-resistant-safeguards
    name: Safeguards that survive fine-tuning (for open-weight models)
    close_to_ml: "very"
    where: Research labs, academia
  - slug: dna-synthesis-screening
    name: DNA-synthesis screening and other biosecurity
    close_to_ml: "partly"
    where: Biosecurity organisations, governments
not_captured:
  - slug: disruption
    text: Economic and social disruption beyond health loss
  - slug: trust
    text: Loss of trust in science and public health
  - slug: after-2031
    text: Anything after 2031
limitations:
  - MOCK. Every input is invented; this card shows the format only.
---

## Is this big?

MOCK prose. Probably not in most worlds, but possibly very big in a few: the expected value is
driven by a small chance of a very large outbreak.

## Which AI does it come from?

MOCK prose. Open-weight models cannot be withdrawn once released and their safeguards can be
removed; API models can be monitored.
