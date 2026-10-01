# BBO Capstone — Optimisation Strategy per Function

**Setting and constraints (these drive every choice below)**

Each function is a maximisation problem over the unit hypercube **[0, 1]^d**. What makes this hard is not the maths but the *budget*: submitting a point costs **one week** to get its output, and you have only **10 sequential trials** left per function. That is an extremely small evaluation budget, so every point has to earn its place. The one advantage you have is that the process is **sequential and adaptive** — you see each output before choosing the next point, and you can change the acquisition function (or even the surrogate) after a few weeks once the landscape reveals itself.

Two structural facts help. First, you already hold a reasonable batch of initial points per function (10 to 40), so the Gaussian Process (GP) is not starting cold — the 10 new trials *refine* an existing model rather than build one from scratch. Second, because you submit at most one point per function per week, each function is **fully sequential**: there is no need for batch/parallel acquisition (q-EI, Thompson batches) — plain sequential Expected Improvement is exactly the right tool, and you refit the GP every week as the dataset grows by one.

## The shared framework

Unless a function says otherwise, the default recipe is the same, and only the *tilt* between exploration and exploitation changes:

**Surrogate.** A GP with a **Matérn-5/2 kernel** and **ARD** (a separate lengthscale per input dimension). Matérn-5/2 is the standard BO default because it assumes a realistic, moderate smoothness rather than the unrealistically smooth RBF. ARD matters more as dimension grows: with only 10 new points in 6–8 dimensions you cannot afford to treat every input as equally important, and the fitted lengthscales tell you which dimensions actually move the output so you can effectively shrink the search.

**Output transform.** Standardise the output to zero mean and unit variance before every refit. Two functions need more than that: F5 (range ≈ 0.1 to 1089) and F4 (large negative range) have dynamic ranges that will distort a GP, so F5 in particular should be modelled on a **log scale**.

**Acquisition.** Expected Improvement (EI) is the workhorse; UCB is used where I want a single, tunable exploration knob (its β parameter). Because several of these functions are noisy or multimodal, EI should be computed against the **GP posterior mean** of the best point, not the single best raw observation — otherwise one lucky noisy read anchors the whole search.

**Explore-early / exploit-late schedule.** With 10 sequential trials, the natural arc is: spend the first 2–4 weeks reducing model uncertainty (more exploration), the middle weeks balanced, and the final 2–3 weeks in pure exploitation (EI with ξ → 0, or UCB with a small β) to squeeze out the best point in the most promising basin. The exact split depends on how rugged the function is — a unimodal function should start exploiting almost immediately, a sparse one cannot.

The rest of this document is the per-function version of that arc, with the justification for each.

---

## Summary table

| Fn | Dim | Landscape (from description + data) | Surrogate / transform | Acquisition | Tilt over 10 trials |
|----|-----|-------------------------------------|------------------------|-------------|---------------------|
| 1 | 2 | Sparse "needle-in-haystack"; 9/10 initial reads ≈ 0 | Matérn, **short-lengthscale prior** | **Uncertainty / high-β UCB** → EI once a signal appears | Explore hard, exploit only late |
| 2 | 2 | Noisy, multimodal (many local peaks) | Matérn + **WhiteKernel (noise)** | **Noisy-EI** or UCB (β≈2–3) | Explore → exploit, noise-aware |
| 3 | 3 | Costly; maximise −(side-effects); smooth-ish | Matérn ARD | EI | Slightly exploratory → exploit |
| 4 | 4 | Multimodal, dynamic, many local optima | Matérn ARD, standardise | **UCB (β≈2–3)** / EI with ξ>0 | Exploration-leaning |
| 5 | 4 | **Unimodal**, single peak; huge skewed range | Matérn, **log-transform output** | **EI (small ξ)** | Exploit from the start |
| 6 | 5 | Additive negative penalties → smooth/separable | **Additive** or Matérn ARD | EI | Balanced |
| 7 | 6 | ML tuning; literature/priors help | Matérn ARD + **input warping** | EI / UCB | Balanced, prior-guided |
| 8 | 8 | High-dim; only strong local maxima realistic | Matérn ARD, **trust region** | UCB/EI **within trust region (TuRBO)** | Local exploitation |

---

## Function 1 — Contamination-source detection (2-D, sparse)

**Strategy.** Treat the first several weeks as a **discovery phase, not an optimisation phase**. Use pure uncertainty sampling (maximum posterior variance) or UCB with a deliberately high β to place points in the least-explored parts of the 2-D square. Put a **prior favouring short lengthscales** on the kernel. Only once a trial returns a clearly non-zero reading do you switch to EI/UCB to climb that peak — and even then, keep one or two trials in reserve for exploration, because the description explicitly says there are **both strong and weak sources** and you don't want to lock onto the first one.

**Justification.** The initial data is the giveaway: nine of the ten points read essentially zero and one reads a tiny negative. The signal only appears near a source, so almost the entire domain is flat and carries no gradient information. A GP fitted to this data will, left alone, infer a very long lengthscale and a near-constant surface — which is why the short-lengthscale prior is essential, so the model expects sharp local structure rather than smoothing it away. Standard EI is nearly useless here because "improvement" over a flat-zero baseline is undefined everywhere; you first have to *find* signal, and that is an exploration problem. Two dimensions plus roughly twenty total points is enough to cover the space reasonably, so exploration is affordable. **Adaptation trigger:** the moment any trial returns a meaningful non-zero value, pivot that function to exploitation around it.

## Function 2 — Noisy log-likelihood (2-D, multimodal)

**Strategy.** Fit the GP with an explicit **noise term** (a WhiteKernel, or learn the likelihood variance), and drive the search with a **noise-aware acquisition** — noisy-EI, or UCB with a moderate β (≈ 2–3). Start moderately exploratory to map the competing peaks, then over the final trials collapse onto the best basin the posterior mean identifies.

**Justification.** The description flags two things — the output is **noisy** and the surface is **multimodal with many local peaks** — and the initial outputs bear this out, spreading from about −0.07 to 0.61 with no single dominating point. Noise is the key modelling decision: without a noise term the GP will interpolate every wobble and chase phantom peaks, and standard EI anchored to the single best raw observation will over-trust one lucky read. Computing improvement against the posterior mean, with the noise modelled, fixes both. Multimodality is why you don't exploit immediately: in 2-D with ~20 points you can afford to check two or three basins before committing.

## Function 3 — Drug discovery, maximise −(side-effects) (3-D)

**Strategy.** Standard sample-efficient BO: Matérn-5/2 with ARD, EI as the acquisition, a mild exploration tilt in the first two or three trials and exploitation thereafter. Nothing exotic.

**Justification.** The outputs are all negative (−0.40 to −0.03) because the true objective — number of adverse reactions — has been re-framed as maximising its negative, so "closer to zero" is better and the maximisation machinery applies unchanged. There is no modality or noise warning in the description, so the surface is presumably reasonably smooth, and EI is the most sample-efficient default for exactly that case. The emphasis in the description is on **cost** ("costly wet-lab experiments"), which is really just an argument for BO over any less sample-efficient method and for making each of your 10 picks maximally informative. Three dimensions with ~25 total points is comfortable for a GP.

## Function 4 — Warehouse placement (4-D, multimodal)

**Strategy.** Lean toward exploration: **UCB with a moderate-to-high β (≈ 2–3)**, or EI with a positive ξ so it doesn't tunnel into the nearest optimum. Standardise the output. Use ARD to find which of the four hyperparameters actually matter. Concretely, anchor most trials on the best basin found in the 30 initial points but spend two or three of them probing other promising regions, and validate a candidate before declaring it the winner.

**Justification.** The description stresses that the system is **dynamic and full of local optima** and needs **robust validation**, and the output — the difference from an expensive baseline — ranges widely (−32.6 to −4.0). With many local optima and only 10 new points, the risk is committing early to a local peak that isn't the global one, which is precisely what a greedy EI would do; UCB's explicit β lets you dial in enough exploration to hedge against that. The large output range is why standardising before each GP refit matters here. **Adaptation trigger:** if two or three consecutive trials fail to improve, that basin is likely exhausted — raise β / jump to the next most promising region.

## Function 5 — Chemical-process yield (4-D, unimodal) — *the easy one*

**Strategy.** **Exploit from the first trial.** Log-transform the output, fit a smooth GP (Matérn-5/2, or even RBF given the smoothness), and use EI with a small ξ — effectively local refinement that walks uphill toward the single peak. You do not need an exploration phase.

**Justification.** This is the one function the description calls **unimodal with a single peak**, and the data strongly supports it: the outputs are heavily right-skewed — most are small, a handful are large, and one is ~1089 — which is exactly the fingerprint of a single dominant optimum that some initial points already sit near. With a unimodal target there is no other basin to hedge against, so exploration would waste scarce trials; the sample-efficient move is to exploit the known peak region hard. The enormous, skewed dynamic range (0.1 to ~1089) is why the log-transform is not optional — on the raw scale the GP's error near the peak would dwarf everything else and destabilise the fit. Expect the **largest gain-per-trial** of any function here; if you want to bank an early win, this is where to spend your best modelling effort.

## Function 6 — Cake-recipe score (5-D, additive penalties)

**Strategy.** Matérn ARD with EI, balanced exploration, and — if you want to exploit structure — an **additive/separable kernel** that models the output as a sum of per-ingredient contributions.

**Justification.** The score is described as a **sum of negative penalties** across the five ingredients (flavour, consistency, calories, waste, cost), and the data matches: all outputs are negative (−2.57 to −0.71) with the goal of pushing the sum toward zero. Additive structure means the surface is relatively smooth and, importantly, *partly separable* — each ingredient contributes somewhat independently — which an additive GP kernel can exploit to learn faster from few points than a fully-coupled kernel would. Five dimensions with ~30 total points is moderate, so a balanced explore/exploit schedule is appropriate; there is no strong multimodality or noise warning forcing either extreme.

## Function 7 — ML hyperparameter tuning (6-D, priors help)

**Strategy.** Matérn ARD with EI (or UCB), plus **input warping / log-scaling** on the dimensions that are likely scale-sensitive (a learning-rate-like parameter should be searched in log-space, not linearly). Use the ARD lengthscales to prune dimensions the model finds irrelevant. Balanced schedule.

**Justification.** The description points out that this is a **common** ML-tuning setup and that **literature/priors can guide the search space** — the single most useful lever here. Hyperparameters like learning rate or regularisation strength span orders of magnitude and matter most on a log scale; warping the inputs so the GP sees them that way turns a very non-stationary surface into a smoother one the GP can actually model with few points. The outputs (≈ 0.003 to 1.37) behave like a performance score. Six dimensions with ~40 total points is workable for a GP as long as ARD is doing its job of concentrating the search on the few dimensions that matter.

## Function 8 — High-dimensional black box (8-D)

**Strategy.** Go **local, not global**: run a **trust-region BO** (TuRBO-style) — maintain a box centred on the current best point, run UCB/EI *inside that box*, and shrink or grow the box based on whether trials keep improving. Use ARD aggressively to detect whether the effective dimensionality is actually much lower than 8 (it often is), in which case ordinary BO on the important dimensions can work.

**Justification.** The description is explicit that in 8 dimensions **global optimisation is hard and identifying strong local maxima is the practical strategy**, and the arithmetic agrees: even with 40 initial + 10 new points, 50 samples cannot cover an 8-D space, so a global GP would be badly under-determined and global EI would mostly chase model artefacts. A trust region sidesteps this by only ever modelling and optimising a small, well-sampled neighbourhood — turning an impossible global problem into a tractable local one, which is what TuRBO was designed for. The outputs sit in a narrow band (5.6 to 9.6), consistent with a rugged surface where big jumps are rare and steady local climbing is the realistic path. ARD is the escape hatch: if only, say, three of the eight inputs actually move the output, the problem is really 3-D and you can drop the trust region.

---

## How to use the 10 weeks (schedule and adaptation)

Because all eight functions run in parallel — one point each per week — you can treat them as eight independent sequential BO runs sharing a weekly cadence. A sensible arc:

**Weeks 1–3 (learn).** Exploration-leaning on the rugged/sparse functions (F1 especially, then F2, F4, F8); straight exploitation on F5; balanced on the rest. The goal is to reduce uncertainty where the landscape is unknown while not wasting the easy wins.

**Weeks 4–7 (balance and adapt).** This is where the "change strategy after a few weeks" freedom pays off. Refit each GP weekly and read the ARD lengthscales and residuals. Concretely: if F1 has found a source, flip it to exploitation; if F2's noise estimate is large, lean harder on UCB and the posterior mean; if F4 or F8 keeps improving inside a basin, tighten around it, and if it stalls for 2–3 weeks, widen the search or move basins.

**Weeks 8–10 (exploit).** Pure exploitation everywhere — EI with ξ → 0 or low-β UCB — to convert everything you've learned into the best possible final point in the best-known basin of each function.

**General adaptation triggers, in one place:** switch a function toward *more* exploration when it plateaus (no improvement over 2–3 trials) or when the GP's uncertainty is still high across the domain; switch toward *more* exploitation when a clear leading basin has emerged and trials are consistently improving. F5 should exploit throughout; F1 and F8 will likely spend the longest in exploration/local-search mode.

*This is a starting map, meant to be revised as real outputs arrive — which is exactly what the sequential, adaptive setup is for.*
