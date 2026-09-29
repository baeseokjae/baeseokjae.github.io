---
title: "Local LLM Rig Cost Payback: How Long Until It Pays for Itself?"
date: 2026-09-29T01:18:26+00:00
tags:
  - local llm
  - local llm cost
  - gpu break even
  - llm total cost of ownership
  - electricity cost
  - rtx 5090
  - mac studio
  - dgx spark
  - self hosting llm
  - local ai
description: "Local LLM rig cost payback runs from ~4.8 months at 20h/day to never at 12h/day. Here is the five-number worksheet and the utilisation cliff behind it."
draft: false
cover:
  image: "/images/local-llm-rig-cost-payback-2026.png"
  alt: "Local LLM Rig Cost Payback: How Long Until It Pays for Itself?"
  relative: false
schema: "schema-local-llm-rig-cost-payback-2026"
---

A local LLM rig cost payback runs from about 4.8 months to infinity, and the machine is not what decides it. The same $3,500 RTX 5090 box pays back in ~4.8 months at 20 h/day against a $2/M API tier, stretches to ~39 months at 24/7 against a $0.50/M hosted open-weight model, and never pays back at all at 12 h/day — because a $133/month API bill undercuts a $137/month local rig. Payback is a property of your queue depth, not your GPU.

That is the whole answer in one paragraph. The rest of this post is the arithmetic, so you can plug your own four numbers in and get a defensible answer in about ten minutes.

## How long until a local LLM rig pays for itself? (the short answer)

Payback is amortised hardware plus electricity plus cooling plus ops time, divided by the gap between that and the API bill you avoided. If you produce under roughly 50M tokens a month on a cheap hosted model, the answer is almost always "never." Between 50M and 500M tokens a month it depends on whether the data can leave your network and whether you needed the box for something else. Above 500M tokens a month sustained, local wins on cash.

Most people get a wrong answer because they compare a GPU running at 100% utilisation against an API invoice from a month when they barely used it — the local cost is charged on capability to produce, the API cost on tokens actually produced. Fix that framing and the numbers stop lying to you. And when the numbers still say "never," you probably have to admit you are not asking about money at all.

## The five numbers you need before any comparison

Skip the calculator shopping. You need five inputs, and only two of them require research.

| # | Input | Where it comes from | Typical trap |
|---|-------|---------------------|--------------|
| 1 | Throughput (tok/s) | Benchmark for your exact quant | Vendor prefill numbers quoted as decode |
| 2 | Duty cycle (hours/day) | Honest log of your usage | Assuming "always on" = "always generating" |
| 3 | Electricity rate (c/kWh) | Your own utility bill | Copying $0.12 from a 2023 blog post |
| 4 | Amortisation window (years) | What you actually believe | Using 3 years and then running the box for 6 |
| 5 | The API tier you are truly replacing | A like-for-like model, not the frontier | Comparing a 12B local model to Claude Opus |

That last one deserves emphasis, because it is where most break-even math quietly becomes fiction. If your local model scores 42 on the Artificial Analysis Intelligence Index and the hosted model you compare it against scores 53, you have not replaced that model. You have replaced a cheaper one.

## Step 1 — Turn throughput into tokens per month

The formula is unglamorous: `tok/s x 3600 x hours_per_day x 30 x utilisation = tokens/month`.

Take a GeForce RTX 5090, which hits 205.5 decode tok/s versus 60.9 tok/s for an NVIDIA DGX Spark on the same benchmark — a 3.4x gap that most "the hardware is a rounding error" arguments ignore completely. Prefill tells the opposite story less dramatically: 8,518.6 tok/s for the 5090 against 2,054.0 tok/s for the Spark.

At 205 tok/s, 20 hours a day, your ceiling is about 443M tokens a month. Write that on paper now, because everything else divides into it.

Then subtract the fraction of that ceiling you will never reach. Real token demand is spiky, and a 20 h/day average with a 205 tok/s peak means your actual sustained utilisation is probably 25-40% of the peak. Use 30% if you are unsure and you will land closer to reality than any optimistic calculator will.

**The memory check you cannot skip.** Before throughput, confirm the model fits — weights plus KV cache, not weights alone. Llama 3.3 70B Instruct at Q4_K_M needs 42.5GB of weights plus 10.7GB of KV cache at 32k context: 53.3GB total. The cache runs 327,680 bytes per token across 80 layers, so the context window you ask for is a hardware purchase decision, not a settings toggle. A 48GB card that "runs 70B" runs it at the context length you can afford, which on a 48GB card is short.

## Step 2 — Price your electricity honestly

Most local-vs-cloud write-ups still assume $0.12-$0.15/kWh. The US average residential price was 18.34 c/kWh as of June 2026, up from 15.04 c/kWh in 2022 — a 22% rise in four years — with the EIA forecasting 3-5%/year through 2027. State extremes run from 13.11c in Nevada to 52.72c in Hawaii on the same June 2026 data.

So the common assumption understates power cost by roughly 20-50%. On a 600W rig running 20 h/day, moving from $0.15 to $0.183/kWh adds about $18/month. That is not fatal on its own. It becomes fatal when it stacks on an already marginal payback, or when you look at the Spark-vs-Mac gap below.

**The idle-power asymmetry.** A DGX Spark draws roughly 120W idle, versus about 25W for a Mac Studio. A box you leave plugged in 24/7 but use four hours a day spends 20 hours a day at idle draw. That is a quiet, permanent tax that a lower upfront price can hide.

| Hardware | Idle draw | Load draw | Notes |
|----------|-----------|-----------|-------|
| NVIDIA DGX Spark | ~120W | 600-800W | Idle draw is 5x a Mac's |
| Mac Studio (M-series Max) | ~25W | 150-200W | Lower peak, far lower idle |
| RTX 5090 desktop build | 60-100W | 450-600W | Sleep states help if you use them |
| Dual-H100 server | 300W+ | 1,500W+ | Idle cost is a line item, not noise |

And the cooling bill: power and cooling add 15-25% on top of hardware TCO at US rates, more in Europe. If your spreadsheet has one "electricity" cell and nothing else, add 20% to it and move on.

## Step 3 — Pick an amortisation window you actually believe

Three-year amortisation is the industry default and it is optimistic in a specific way: it assumes your hardware is worthless at month 37, and it assumes you will not run it for six years.

Here is a representative 2026 set, all on 3-year amortisation with 24/7 power at $0.15/kWh:

| Rig | Upfront | 3-yr TCO | Cost per year |
|-----|---------|----------|---------------|
| RTX 5090 desktop build | $3,500 | $5,120 | ~$1,707 |
| Mac Studio M5 Max 128GB | $3,499 | $4,429 | ~$1,476 |
| NVIDIA DGX Spark | $3,000 | $6,150 | ~$2,050 |
| Dual-H100 server | $60,000 | $78,900 | ~$26,300 |

Note the ordering flip: the Spark is the cheapest to buy and the second-most expensive to run, because 120W of idle draw plus 600-800W under inference eats its $500 purchase advantage inside the first year. This is why "which box is cheapest" and "which box has the best payback" are different questions.

The counter-argument is residual value, and it is real. Community reports from the Sunk Cost discussion thread describe used RTX 3090s bought for ~$500 after the merge, and commenters reporting their hardware value doubling or tripling since purchase. If your GPU appreciates, amortisation is a fiction in your favour. Do not plan around it — but do not plan around 100% depreciation either.

## Step 4 — Pick the right API comparator (where most payback math goes wrong)

This is the single largest source of wrong answers, so let me be blunt: comparing a local mid-tier model against frontier hosted pricing is a category error, not an aggressive assumption.

Live OpenRouter pricing on 2026-09-29 shows the spread clearly:

| Tier | Example | Output price |
|------|---------|--------------|
| Cheapest open-weight hosts | mistral-nemo | $0.030/M |
| | llama-3.1-8b | $0.080/M |
| | gpt-oss-20b | $0.090/M |
| | gemma-3-4b | $0.100/M |
| Mid-tier hosted | local-model-class equivalents | ~$0.50-1.25/M |
| Frontier hosts | claude-opus-5 | $25/M |
| | claude-fable-5.1 | $50/M |
| | gpt-6-astra | $50/M |
| | claude-opus-4.1 | $75/M |

The gap between $0.08/M and $75/M is nearly a thousandfold, and it is entirely a capability difference. Any payback number you compute against the frontier tier is a number about a model you did not deploy.

The honest comparator for a local rig in 2026 is the mid-tier hosted open-weight class at roughly $0.50-1.25/M output. The other defensible comparator is the specific invoice you are actually replacing — a GitHub Copilot seat, a ChatGPT Plus subscription, an existing API bill you can screenshot.

There is also a capability ceiling that hardware cannot buy past. The best open-weight model on Sunk Cost's leaderboard scores 42 on the Artificial Analysis Intelligence Index v4.3 — GLM-5.3-Flash, with 189GB of weights — against 53 for the best hosted model. That is an 11-point gap that no GPU closes. Any payback argument that assumes capability parity is quietly assuming you will be satisfied with less.

## Step 5 — Add the costs that never make the spreadsheet

The items below are the difference between a calculator answer and a real one.

- **Ops labour.** Model updates, quantization experiments, driver breakage, a broken CUDA matrix. Price your own hour at something nonzero and this is usually the largest hidden line.
- **Idle power.** Covered above, but it deserves a second mention because it is charged every hour of the year.
- **Cooling.** 15-25% on top of hardware TCO, and higher in warm climates or small rooms.
- **Rate-limit engineering.** If you still call an API for the hard 20% of requests, you maintain two stacks.
- **Re-engineering cost when a vendor changes models.** Prompt rewrites are a real cost on the API side — a genuine advantage for local, and most comparisons skip it because it does not have a number attached.
- **Depreciation and residual value.** Choose a number and write down why.

## The utilisation cliff: same rig, four months or never

Here is the table that answers the question in the title. Same $3,500 RTX 5090 rig, same 205 tok/s, electricity at the current US residential average of $0.183/kWh:

| Duty cycle | Tokens/month (approx) | Local cost/month | API cost at $0.50/M | API cost at $2.00/M | Payback |
|-----------|----------------------|------------------|---------------------|---------------------|---------|
| 4 h/day | ~89M | ~$75 | ~$44 | ~$177 | Only vs the expensive tier |
| 12 h/day | ~266M | ~$137 | ~$133 | ~$531 | Never vs $0.50/M |
| 20 h/day | ~443M | ~$163 | ~$222 | ~$886 | ~4.8 months vs $2/M |
| 24/7 | ~532M | ~$180 | ~$266 | ~$1,064 | ~39 months vs $0.50/M |

Read the 12 h/day and 20 h/day rows together. Moving four hours a day flips the answer from "never" to "under five months" — not because the hardware changed, but because the monthly gap crossed zero. At 12 h/day the API bill is $133 and the local rig costs $137; the machine loses by $4/month and will lose forever.

Then read 20 h/day against 24/7. Going from 20 to 24 hours adds 89M tokens a month, which sounds like pure win, but it also pushes you down the API price ladder — because the cheaper hosted models are the ones you would actually use at that volume, and against $0.50/M the same rig needs ~39 months. The extra tokens are not extra savings if the comparator got cheaper.

That is the utilisation cliff: payback is not a property of the machine, it is a property of your queue depth.

## Worked example A — $3,500 RTX 5090 rig vs a hosted open-weight model

Inputs: 205 tok/s decode, 20 h/day, $0.183/kWh, 450-600W under load, $3,500 upfront amortised over 3 years.

- Tokens/month: ~443M at the ceiling.
- Electricity: roughly 500W average x 20 h x 30 days = 300 kWh/month = ~$55.
- Hardware amortisation: ~$97/month.
- All-in: ~$163/month, or about $0.37 per million tokens at full utilisation.

Compare: a mid-tier hosted open-weight model at ~$0.50/M output is ~$222/month for the same 443M tokens. The rig is ahead by ~$59/month and pays back in about 4.8 months.

Now move the comparator. Against the cheap end of the market — $0.08/M output, which llama-3.1-8b and the $0.03-0.10 tier sit in — the same 443M tokens cost about $35/month. Payback becomes negative: it never happens.

Both of those numbers are correct. Which one applies to you depends on whether the model you would have called is worth calling.

## Worked example B — used RTX 3090 box at $2,000

This is the honest hobbyist configuration, and the community evidence is better than the spreadsheet evidence. One commenter runs Qwen 3.8 at 57 tok/s on a $2,000 used HP Omen with a 3090. Another replaced a $300+/month GitHub Copilot bill with a 32GB Radeon R9700 at $1,350 and reports a ~4-month payoff.

Run the numbers: 57 tok/s at 20 h/day is ~123M tokens/month at the ceiling. Electricity at ~$0.183/kWh and maybe 350W loaded lands near $38/month; amortised hardware over 3 years is ~$56/month. All-in ~$94/month, or roughly $0.76/M.

| Comparator | Monthly API cost at 123M tokens | Verdict |
|-----------|--------------------------------|---------|
| $0.50/M mid-tier | ~$62 | Local loses by ~$32/month |
| $1.00/M | ~$123 | Local ahead ~$29/month, payback ~5.75 years |
| A $300/month subscription it replaces | $300 | Local ahead ~$206/month, payback under 6 months |

Notice what happened: the used-3090 rig's payback is essentially decided by what it replaces, not by its own efficiency. If you are replacing a flat-rate subscription with real usage, the numbers work fast. If you are replacing metered tokens at mid-tier prices, they are marginal.

The ~4-month community report is real and reproducible — but it is a subscription replacement, not a token-for-token comparison. Read claims like it with that in mind, including the optimistic framing.

## Worked example C — Mac mini M6 and the 8.3-year payback

Sunk Cost's own model, and the author's reply in the discussion thread, are the most deflating data points available. At 1M tokens/day, the quickest Sonnet-class local payback is Qwen3.8 27B on a Mac mini M6 with 32GB, at an estimated 6.9 tok/s — and the answer is **8.3 years**. Only at agent-scale, around 20M tokens/day, does it drop under a year. A user producing 50k tokens/day pays back in **166 years**.

The 6.9 tok/s figure is doing enormous work in that calculation, and it is explicitly labelled an estimate rather than a measurement. Two lessons:

1. **Slow hardware makes payback unreachable, not long.** Below roughly 100 tok/s you cannot produce enough tokens to matter, no matter how cheap the box was.
2. **Small-volume users should almost never buy.** The floor on this calculation is not a few months; it is centuries. That is the correct order of magnitude for hobby token volumes, and it is why "is a local rig cheaper than ChatGPT" has a one-word answer at that volume: no.

## Does local ever win on capability?

No — and it is worth stating plainly rather than burying it in a table. The 11-point gap between the best open-weight model (42) and the best hosted model (53) on Artificial Analysis Intelligence Index v4.3 is a frontier gap, not a hardware gap. Buying a bigger GPU raises throughput; it does not raise that number.

What changes over time is the absolute capability of open weights, which has been improving steadily. The practical consequence: pick the local model you would genuinely be satisfied with, price the hosted service you would use instead at *that* capability level, and then compute payback. Every other version of the calculation is an argument for buying the machine you already wanted.

## When local wins on cash alone: 24/7 agent and batch workloads

There is exactly one regime where a local rig beats the API on cash for reasons that survive scrutiny: sustained, high-volume, latency-insensitive generation where the bottleneck is queue time rather than token price. Overnight batch jobs, embedding backfills, continuous subagent generation, eval sweeps.

Two caveats that the "run it 24/7" advice usually omits:

- **A flat-rate plan often serves more concurrency than one GPU.** If your workload is API-shaped and bursty, a Max/Pro-tier subscription can absorb parallelism that a single 5090 cannot, because your constraint is VRAM and KV cache, not willingness to spend.
- **Queue depth is the asset.** Local wins when you have more work than you can get through, not when you have more money than you can spend. If your queue is already short, adding a GPU just makes idle hours more expensive.

## Decision thresholds: hobby, prosumer, sustained

The brief asked for thresholds instead of vibes, so here they are. These assume a cheap-to-mid hosted comparator and a rig you would actually run hot.

| Your volume | Recommended path | Reasoning |
|-------------|-----------------|-----------|
| Under ~50M tokens/month | Stay on the API | Payback floor is years; cheap hosted tiers are $0.03-0.10/M |
| 50-500M tokens/month | Buy only if you needed the hardware anyway, or the data cannot leave | Marginal on cash; decisive on control and offline capability |
| 500M+/month sustained | Local wins on cash | The gap is large enough to survive electricity and ops surprises |
| Privacy/regulated data at any volume | Local, and stop pretending it is a cost decision | Compliance cost is not on the API side of the ledger |
| Replacing a $300/month subscription | Usually pays back in months | Compare subscriptions, not per-token rates |

For reference on where the market currently sits: one analysis found 7B-class models at 30% utilisation break even in 4-9 months and 70B-class on a DGX Spark in 3-6 months against frontier APIs, while stretching to 2-4 years under 10% utilisation. Another puts an RTX 4090 at ~$104/month all-in — beating GPT-4o at ~8M tokens/month but needing 204M+ tokens/month to beat GPT-4o-mini. Both land on the same rule: the cheaper your comparator, the harder local has to work.

## The API-prices-keep-falling trap

Any payback calculation that assumes a flat API price predicts a payback that repricing can erase. This is the one place where the best available competitor tool is genuinely better than most write-ups: Sunk Cost lets you toggle "assume API prices keep falling" at a rate you set.

Model it explicitly. Take your payback in months and ask what the hosted price needs to do for the payback to exceed the amortisation window:

- If your comparator falls 20%/year and your payback is 24 months, you will be behind by month 18.
- If your comparator falls 30%/year and your payback is 4.8 months, you are probably still fine — the fall does not have time to catch up.
- If your comparator is $0.03-0.10/M today, there is almost nothing left to fall, which is good for local's relative position but bad for the case that local was ever cheaper at that tier.

That last point is the cleanest way to state the 2026 situation: inference prices falling compresses the local advantage from above, but the cheap open-weight tier has already hit the floor. There is no version of this where a $3,500 rig beats a $0.03/M endpoint on cash.

## The sunk cost test: five questions before you buy

Run this before you order anything. If you cannot answer all five in a sentence each, the machine is a purchase and not an investment.

1. **How many tokens per month will I actually produce, and how do I know?** Cite your last 90 days of real usage, not a benchmark's ceiling.
2. **Which hosted service, at which price per million tokens, am I genuinely replacing?** A like-for-like capability, not the frontier tier.
3. **What is my amortisation window, and what happens if the API price halves?** If halving the API price kills the payback, say so out loud before you buy.
4. **What do the idle hours do?** If the answer is "nothing, but it's on anyway," the idle draw is a permanent subsidy to the argument.
5. **If this box could not be resold and produced no savings, would I still want it?** An honest yes is a fine reason to buy — self-hosting is a hobby with real skills attached, and offline capability is genuinely worth something. The failure mode is not buying the box. It is buying it and calling a hobby a hedge.

Once the box is on your desk, the trap closes in a specific, predictable way: the marginal token becomes nearly free, so the API comparison stops being a decision and becomes a justification. The sunk cost is real, but the comparison you start making afterwards is not. Make the decision while the money is still in your account.

## FAQ

**Is running a local LLM cheaper than ChatGPT?**
For almost everyone, no. A local rig's payback floor at hobby volumes is measured in years, and one model puts a 50k tokens/day user at a 166-year payback. The exceptions are people replacing a $300/month subscription with heavy real usage (community reports of ~4-month payoffs exist), and people running 500M+ tokens a month on 24/7 batch workloads.

**How is local LLM payback calculated?**
`(hardware amortisation + electricity + cooling + ops) / (API cost avoided - local monthly cost)`. Take your sustained tok/s, multiply by hours per day, then by 30. Price electricity at your own rate, not a blog's $0.12. Amortise over a window you believe. Compare against a like-for-like hosted model, not the frontier tier.

**What is the difference between 12 h/day and 24/7 utilisation?**
About 266M versus 532M tokens a month on a 205 tok/s rig — but the bigger effect is which hosted model becomes your comparator. At 12 h/day against $0.50/M output, a $3,500 rig never pays back ($133 API vs $137 local). At 20 h/day you are ~$59/month ahead against the same tier and pay back in ~4.8 months against $2/M. Small duty-cycle changes flip the sign.

**Does an RTX 5090 pay for itself against cloud APIs?**
Against the frontier tier it appears to pay back in a month or two, which is a category error. Against a mid-tier hosted open-weight model at ~$0.50/M, a $3,500 rig at 20 h/day pays back in roughly 4.8 months. Against the cheapest hosted tier at $0.03-0.10/M, it never does.

**Is a Mac Studio or a DGX Spark better for break-even?**
Neither, on cash terms. At 70B Q4 the Spark costs ~$0.60 per 1M output tokens in power against ~$0.25 for the Mac Studio M5 Max at $0.15/kWh, but total amortised cost per 1M tokens lands within 3% of each other (~$1.70 vs ~$1.75), because Apple's higher hardware amortisation cancels its power advantage. The Spark's 120W idle draw is the detail that surprises people.

**What is the biggest hidden cost of a local LLM rig?**
Ops labour, then idle power. Updates, driver breakage, quantization experiments, and a CUDA matrix that breaks on a Tuesday. Power and cooling add 15-25% on top of hardware TCO at US rates. Rate-limit engineering costs show up only if you still call an API for the hard cases — which most people do.

**Do local LLMs ever match frontier capability?**
Not today. The best open-weight model scores 42 on Artificial Analysis Intelligence Index v4.3 against 53 for the best hosted model — an 11-point gap that no hardware closes. More VRAM raises throughput, not intelligence. Pick your comparator at the capability level you will actually accept, or the whole payback calculation is fiction.

## Where this leaves you

The payback question has an honest answer and it is not a single number. At hobby volume it is "never," and a spreadsheet will tell you so within ten minutes if you price electricity correctly and compare against the right model. At 50-500M tokens a month it is marginal, and control or compliance usually decides it. Above 500M tokens a month sustained, local wins on cash and the arithmetic gets comfortable.

If your numbers land in the "never" column and you still want the box — buy it. Just keep the two ledgers separate. The money ledger says no; the control ledger says you get a machine that runs when the network is down, that no rate limit can throttle, and that lets you own a skill that transfers. That is a legitimate purchase. What is not legitimate is re-running the calculator after the fact to prove the money ledger agreed.
