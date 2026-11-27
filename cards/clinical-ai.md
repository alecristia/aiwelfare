---
# Hand-written prose for the clinical-AI card (D4), a net card (D17). Merged into the
# generated card by `aiwelfare build card`. No numbers here: every number on the card
# comes from the model and its claims.
id: clinical-ai
title: Clinical AI (net)
kind: net
one_line: >-
  AI that watches hospital patients for early signs of deterioration saves lives, while
  chatbots that give unsafe medical advice, and errors in AI medical devices, cost some.
group: malfunctions            # International AI Safety Report category (D7); benefit and harm share the card (D2)
scope_note: >-
  Global. Three components are modelled: hospital early warning (benefit), unsafe chatbot
  medical advice beyond what people's usual sources would cause (harm), and errors from AI
  medical devices (harm). AI diagnostics and screening, hallucinations entering clinical
  guidelines and biased clinical algorithms are not modelled yet.
neighbour_for_flip: null       # no neighbouring card has a real estimate yet
index_entries: []              # MIT AI Risk Repository mapping not done yet (D3)

cruxes:                        # plain-language reading of each parameter's low and high end
  coverage_2031:
    high: AI early warning spreads to a **much larger share** of the world's sepsis deaths by 2031
    low: AI early warning **barely spreads** beyond today's few hospital systems
  coverage_2026:
    high: AI early warning **already covers** a sizeable share of sepsis deaths in 2026
    low: AI early warning covers **almost none** of the world's sepsis deaths in 2026
  effect_transfer:
    high: early-warning tools work **as well everywhere** as at the hospitals that built them
    low: most of the measured effect **disappears** outside the hospitals that built them
  dalys_per_monitored_death:
    high: each death averted in hospital saves **many** years of healthy life
    low: deaths averted fall on **frail, older** patients with few years left
  dalys_per_chatbot_harm:
    high: harms from unsafe chatbot advice are often **serious or lasting**
    low: harms from unsafe chatbot advice are nearly all **minor and brief**
  harm_probability:
    high: unsafe chatbot answers **often** lead to real harm
    low: unsafe chatbot answers **rarely** lead to real harm, because people check or ignore them
  excess_share:
    high: chatbots cause **much more** harm than people's usual sources would
    low: chatbots cause **no more** harm than the search engines people would otherwise use
  conversations_per_user:
    high: people ask chatbots for clinical advice **many times** a year
    low: most health prompts are **not** requests for clinical advice
  chatbot_growth_2031:
    high: chatbot health use **triples** by 2031
    low: chatbot health use **stays at** its 2026 level
  other_providers:
    high: other chatbots together are **as big as** ChatGPT for health questions
    low: ChatGPT accounts for **most** chatbot health questions
  unsafe_rate:
    high: answers are as unsafe as the **least safe** chatbot tested
    low: answers are as safe as the **safest** chatbot tested
  sepsis_deaths:
    high: global sepsis deaths are at the **top** of GBD's uncertainty interval
    low: global sepsis deaths are at the **bottom** of GBD's uncertainty interval
  rr_chartwatch:
    high: CHARTwatch's effect was at the **weak** end of its confidence interval
    low: CHARTwatch's effect was at the **strong** end of its confidence interval
  reduction_composer:
    high: COMPOSER's effect was at the **strong** end of its confidence interval
    low: COMPOSER's effect was at the **weak** end of its confidence interval
  or_pooled:
    high: the pooled early-warning effect is at the **weak** end of its interval
    low: the pooled early-warning effect is at the **strong** end of its interval

kinds_of_work:
  - slug: human-user-testing
    name: Testing medical chatbots with real users before release, not only on benchmarks
    close_to_ml: "yes"
    where: AI labs (evaluation and health teams), academia
  - slug: medical-red-teaming
    name: Physician-led red-teaming of chatbot medical advice
    close_to_ml: "yes"
    where: AI labs, independent evaluators, academic clinicians
  - slug: early-warning-deployment
    name: Building, deploying and evaluating early-warning models in hospitals
    close_to_ml: "partly"
    where: Academic health systems, clinical-AI start-ups, EHR vendors
  - slug: postmarket-monitoring
    name: Post-market safety monitoring and incident reporting for AI medical devices
    close_to_ml: "no"
    where: Regulators (e.g. FDA), patient-safety organisations, health systems

not_captured:
  - slug: navigation-and-access
    text: Help with navigating care and insurance, and access outside clinic hours, beyond its health effects
  - slug: clinician-burden
    text: Alarm fatigue and burnout among clinicians from false alerts
  - slug: fairness
    text: Unequal performance of clinical algorithms across groups (a fairness harm even where it costs few DALYs)
  - slug: privacy
    text: Privacy of health conversations with chatbots
  - slug: after-2031
    text: Anything after 2031

limitations:
  - Diagnostics and screening (e.g. AI-supported mammography, computer-aided chest X-ray reading for tuberculosis) are not modelled yet, so the benefit side is incomplete; the evidence is strong on accuracy but no source read yet gives global screening volumes or turns extra detections into deaths averted.
  - Hallucinations entering clinical guidelines and biased clinical algorithms are not modelled; no DALY-convertible evidence was found.
  - No source gives global uptake of any clinical AI; how much of the world early warning reaches, and how much chatbot health use there is outside ChatGPT, are flagged assumptions, and they dominate the estimate.
  - All three mortality effects for early warning are non-randomised and measured at the hospitals that built the tools; the CONCERN cluster-randomised trial (Nature Medicine 2025) has not been read yet.
  - Effects measured on general medical wards (CHARTwatch, the meta-analysis) are applied to global sepsis deaths, the only global count of deaths these tools target; global sepsis deaths are from 2017 and held constant.
  - No study measures realised harm from chatbot medical advice; the chain from an unsafe answer to DALYs rests on assumptions. Unsafe-answer rates are for late-2024 chatbots.
  - Chatbot advice can also help (earlier care, better understanding); that benefit is not modelled, and the harm counts only the excess over people's usual sources.
  - AI-device harm starts from US voluntary reports, which miss most diagnostic errors.
---

## Is this big?

The benefit comes from many small improvements in hospital care, mostly in a few
well-resourced health systems, so its size depends above all on how far these tools spread.
The harm from chatbots is spread across hundreds of millions of people asking health
questions; whether it is large depends on how often unsafe advice is followed and how bad the
results are, which no study has yet measured. Errors from AI medical devices, as reported, are
far smaller than either.

## Which AI does it come from?

The two larger components come from very different AI. Hospital early-warning tools are
small, specialised models built into electronic health records, mostly not frontier models.
Chatbot advice comes from general-purpose frontier models served by API and in consumer apps,
with open-weight models also in use.
