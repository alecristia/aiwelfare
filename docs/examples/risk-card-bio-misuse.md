> ⚠️ **ILLUSTRATIVE MOCK-UP: ALL NUMBERS ARE INVENTED.** This card shows the *format* only. Do not quote any figure. The `aiwelfare` commands are a proposed CLI specification and do not exist yet.

# AI-assisted biological misuse

**In one line:** AI models help someone cause a disease outbreak they couldn't otherwise have caused.

| | |
|---|---|
| **Expected harm, 2026–31** | **~290,000 DALYs** (range: almost zero → millions) |
| **Size class** | 🟠 **Large but uncertain**: in the same band as *[baseline cause]*; well below malaria |
| **Confidence** | 🔺 **Low.** Most of the number comes from rare, catastrophic scenarios |
| **Mainly comes from** | Open-weight models (55%) · API frontier models (35%) · locally-run frontier models (10%) |
| **Compared with** | AI frozen at 2026 levels ([change](#)) |

```
aiwelfare show risk/bio-misuse --counterfactual no-ai      # same card, different comparison
```

---

## Is this big?

Probably not in most worlds, but possibly very big in a few. In about 95% of simulated futures nothing happens in the next five years. The expected value is high because a small chance of a pandemic-scale event carries a very large number of DALYs.

*[Quantile dotplot: 20 dots, each 5% of simulated futures. Dots for "nothing happens" sit in their own column left of the log axis.]*

```
aiwelfare dist risk/bio-misuse                        # quantile dotplot + percentiles in the terminal
aiwelfare compare risk/bio-misuse baseline/malaria    # side by side, same window and units
```

## Why it might be much bigger, or much smaller

The estimate hinges on three questions. Your answers to them matter more than anything else on this card.

| If you believe… | …the estimate moves |
|---|---|
| AI helps with the **hardest** steps of making a biological weapon, not just information already online | ⬆ ~20× |
| A **pandemic-scale** outcome is plausible within five years | ⬆ ~15× |
| **Safeguards on API models** work well against determined actors | ⬇ ~3× |

**To rank this below** *AI errors in clinical care*, you'd have to believe that AI gives little end-to-end help **and** that outcomes are capped at a local epidemic. [Try your own assumptions →](#)

```
aiwelfare cruxes risk/bio-misuse                              # full sensitivity analysis (all parameters)
aiwelfare whatif risk/bio-misuse --set end_to_end_uplift=0.2  # rerun with your own assumption
aiwelfare flip risk/bio-misuse risk/clinical-errors           # what must change for the ranking to flip
aiwelfare claims risk/bio-misuse --param end_to_end_uplift    # every sourced claim behind one crux
```

## Which AI does it come from?

This is the "affected versions" view: which kinds of deployment the risk mainly flows through.

| Deployment | Share | Why |
|---|---|---|
| Open-weight models | 55% | Safeguards can be removed; no monitoring; can't be withdrawn once released |
| API-served frontier models | 35% | Most capable models; filters and monitoring reduce the risk but don't remove it |
| Frontier models run locally / on-premises | 10% | Weights are controlled, but the developer can't see how they're used |

```
aiwelfare breakdown risk/bio-misuse --by access-mode            # shares with intervals
aiwelfare claims risk/bio-misuse --tag access-mode/open-weight  # the evidence behind one row
```

## What kinds of work target this risk?

*This section describes the work; it does not rate how much each kind helps (tractability is out of scope, see VISION.md).*

| Kind of work | Close to ML engineering? | Where it's done |
|---|---|---|
| Dangerous-capability evaluations | ✅ Very | AI labs, government AI security institutes, independent evaluators |
| Misuse classifiers and monitoring for API models | ✅ Very | AI labs |
| Safeguards that survive fine-tuning (for open-weight models) | ✅ Very | Research labs, academia |
| Unlearning hazardous knowledge | ✅ Yes | Academia, AI labs |
| DNA-synthesis screening and other biosecurity | ➖ Partly | Biosecurity organisations, governments |

```
aiwelfare work risk/bio-misuse --refs                          # each kind of work + the sources linking it to this risk
aiwelfare refs risk/bio-misuse --work tamper-resistant-safeguards  # sources for one kind of work only
aiwelfare work --kind dangerous-capability-evals               # every risk this kind of work targets
```

## What this number leaves out

Economic and social disruption beyond health loss · loss of trust in science and public health · pressure to restrict open research · anything after 2031.

```
aiwelfare not-captured risk/bio-misuse --refs   # each excluded harm + the sources that discuss it
```

---

<details>
<summary><b>For checking: model, evidence and provenance</b></summary>

### All three comparisons

| Compared with… | Median | 90% interval | Expected value |
|---|---|---|---|
| No modern AI | 2,000 | 0 – 3.1M | 410,000 |
| AI frozen at 2026 levels | 1,200 | 0 – 2.4M | 290,000 |
| Only open-weight / older models advance | 300 | 0 – 0.9M | 95,000 |

### Model

`P(AI-assisted attack causes an outbreak, 2026–31)` × `DALYs if it happens`

| Component | 90% interval | Main evidence |
|---|---|---|
| Probability | 0.1% – 4% | Expert forecasts; lab evaluations |
| DALYs if it happens | 1,000 – 80M (lognormal) | Historical outbreaks; epidemiological models |

### Evidence, by type

| Evidence type | Implies | Sources |
|---|---|---|
| Lab capability evaluations | Some uplift on sub-tasks | System cards *(interested parties)* |
| Independent evaluations | *[claim IDs]* | AI security institutes; independent evaluators |
| Expert forecasts | *[claim IDs]* | FRI LEAP; Metaculus |
| Consensus synthesis | Recognised, not quantified | International AI Safety Report 2026 |
| Observed incidents | None recorded | AI incident databases |

The combined figures weight all evidence types equally. You can change the weights in the explorer or in `models/bio_misuse.py`.

### Known limitations

No historical base rate exists. Lab evaluations are published selectively. The severity distribution is borrowed from natural outbreaks.

### Index and provenance

MIT AI Risk Repository *[entry IDs]* · International AI Safety Report 2026, malicious use section · model `models/bio_misuse.py` · DataLad run `a1b2c3d`

### Changelog

| Date | Change | Why |
|---|---|---|
| 2026-11-20 | Probability upper bound 2% → 4% | New expert forecast wave |
| 2026-10-02 | Severity distribution refitted | New WHO health baseline |

```
aiwelfare model risk/bio-misuse                        # print the model and its parameters
aiwelfare claims risk/bio-misuse --evidence-type expert-forecast
aiwelfare sources risk/bio-misuse                      # full bibliography, with pinned versions
aiwelfare rerun risk/bio-misuse                        # reproduce every number on this card
aiwelfare log risk/bio-misuse                          # full change history with reasons
```

</details>

> ⚠️ **ILLUSTRATIVE MOCK-UP: ALL NUMBERS ARE INVENTED.**
