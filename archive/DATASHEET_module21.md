# Datasheet — BBO Capstone Query Data Set

*Imperial College Professional Certificate in Machine Learning and Artificial Intelligence — Black-Box Optimisation capstone.*
*Maintained by Elias. Version 1.0, compiled 1 October 2026, after round 11 of 13 was submitted.*

This datasheet follows the structure introduced in Mini-lesson 21.1 (Gebru et al., *Datasheets for Datasets*). It documents the data set that my optimisation work has produced: not a data set I found, but one I bought, one query at a time, under a hard budget. That origin shapes every answer below, and the sections on composition and collection should be read as a description of a *biased by design* sample rather than a representative one.

---

## 1. Motivation

### Why was this data set created?

The capstone poses eight unknown objective functions. Each takes a vector of real numbers with every coordinate in the open unit interval, returns a single scalar, and reveals nothing else — no formula, no gradient, no uncertainty estimate, no indication of whether a reading was noisy. All eight are to be **maximised**. Each function allows one query per round, each round takes about a week to return, and the budget is **13 queries per function**. The data set exists because that is the only way to learn anything at all about these functions: every row in it was paid for with a week of latency and an irreplaceable slice of budget.

### What task does it support?

Directly, it supports surrogate modelling and sequential decision-making: fitting a probabilistic model to the observations so far, and using that model to decide which single point to buy next. Indirectly, it is the evidence base for the whole project — the artefact against which every strategic claim I make has to be checked. When I argue that one function depends on fewer inputs than its nominal dimensionality, or that another's measurement noise is far smaller than my model was assuming, the data set is where that argument is settled.

It is worth being explicit about what the data set is *not* for. It is not a benchmark suite. The functions are unknown, the sampling is adaptive and concentrated, and the sample sizes are tiny. It cannot be used to characterise these functions globally, and it cannot be used to compare optimisation algorithms, because the design was never randomised across methods.

### Who created it, and who funded it?

I generated it as an individual learner on the programme. The eight initial designs were supplied by the course; everything after them is mine. There was no external funding; the cost was paid in evaluation budget and elapsed time.

---

## 2. Composition

### What does an instance represent?

One instance is a single evaluation of one function: an input vector and the scalar that came back. Instances are grouped by function, and within a function they divide into two provenances that it is important not to conflate.

**Supplied initial design.** A space-filling sample provided before the first round, intended to cover the domain. These are immutable and are never modified.

**Bought trials.** One row per round, in the order submitted. These are the points my strategy chose, and they are where the interesting bias lives.

### Size and composition

| Function | Dimensions | Initial points (supplied) | Trials bought | Total | Observed output range (all observations) |
|---|---|---|---|---|---|
| F1 | 2 | 10 | 10 | 20 | −8.4e−3 … 1.04e−4 (magnitudes span ~10⁻¹¹⁷ to 10⁻²) |
| F2 | 2 | 10 | 10 | 20 | −0.139 … 0.629 |
| F3 | 3 | 15 | 10 | 25 | −0.399 … −0.0252 |
| F4 | 4 | 30 | 9 | 39 | −32.6 … 0.590 |
| F5 | 4 | 20 | 10 | 30 | 0.113 … 4643.17 |
| F6 | 5 | 20 | 10 | 30 | −2.571 … −0.2497 |
| F7 | 6 | 30 | 10 | 40 | 0.0027 … 2.5758 |
| F8 | 8 | 40 | 10 | 50 | 5.592 … 9.9731 |
| **Total** | — | **175** | **79** | **254** | — |

The whole data set is 254 rows. That number is the single most important fact about it: eight functions of up to eight dimensions, characterised by a few dozen points each. No amount of careful modelling makes 50 points sufficient to describe an eight-dimensional surface, and the strategy documented in `MODEL_CARD.md` is shaped around that scarcity rather than pretending it away.

### Format

Initial designs are NumPy `.npy` arrays of `float64` — `initial_inputs.npy` with shape *(n, d)* and `initial_outputs.npy` with shape *(n,)*. Bought trials are plain CSV, `new_trials.csv`, with a header of `x0 … x{d−1}, y`, appended one row per round and never edited in place. Keeping the supplied data in an immutable binary and the bought data in an append-only text file is deliberate: the model can be rebuilt from scratch at any point in the history, and a mistaken edit to the record is visible in a diff.

Both provenances are concatenated at load time; the code treats them identically once loaded, but the files stay separate so that provenance is always recoverable.

### Does it contain everything, or is it a sample?

It is a sample, and an aggressively non-random one. Each function's true domain is a continuum; the data set holds a few dozen points chosen to maximise information about where that function's maximum is, not to represent the domain. This is the right design for the task and the wrong design for almost anything else.

### Is any data missing?

Yes, and in three distinct senses, each worth separating.

**One missing trial, from an error of mine.** F4 has nine trials where every other function has ten. In round 3 I submitted F4's four-dimensional point to F5 instead. The mistake cost a trial that cannot be recovered; F4 is permanently one round behind, and the step is now part of the weekly routine as an explicit routing check. The incident is recorded in `WEEKLY_LOG.md` under Week 3. I have left the gap visible rather than tidied it away, because the alternative is a data set that quietly misrepresents how it was produced.

**No repeated measurements, except where bought deliberately.** Each input was evaluated once, so the data set contains no direct estimate of measurement noise. Where that mattered I spent a trial on it: a near-replicate on F3 revealed its fitted noise was roughly sixty times too large, and a single-variable test on F2 — moving one input while holding the rest fixed — established both that the second input is effectively inert and that the differences between nearby readings are real signal rather than noise. Those two readings cost two trials and changed two models.

**No metadata on the measurement itself.** The returned scalar is the entire feedback signal. There is no uncertainty, no flag for an unusual evaluation, no timing or provenance beyond the round number implied by row order. Anything I believe about noise is inferred, never read.

### Are there errors, noise, or redundancies?

One recorded value on F1 is exactly `0`, returned by a space-filling probe in a region where the function's magnitude is vanishingly small. It is almost certainly an underflow to zero rather than a true zero, and it broke the log-transform used on that function until the transform was floored. That row is kept — it is a real reading and it closed an open question about whether a second source existed elsewhere in the square — but any reuse of F1 should know it is there.

F1's outputs span more than a hundred orders of magnitude in absolute value, from around 10⁻¹¹⁷ up to around 10⁻². F5's span four. Any analysis that treats these columns on a linear scale will be dominated entirely by a handful of rows.

### Does it contain confidential, sensitive or personal data?

No. There are no human subjects, no personal data and no sensitive attributes. The functions are synthetic black boxes supplied for coursework. The only confidentiality consideration is competitive rather than ethical: the same eight functions are given to every learner on the cohort, and publishing my query history before the final round means publishing my positions. I have chosen to publish anyway, on the view that the documentation and reproducibility value of an open record outweighs the competitive cost, and because an argument that can only be assessed by people who cannot see the data is not much of an argument.

---

## 3. Collection process

### How were the queries generated?

Round 1 used only the supplied initial designs. Every round after it followed the same loop, and the loop is the collection mechanism:

1. Load the immutable initial design and append the trial log.
2. Refit the surrogate for that function — refitted from scratch each round, never updated incrementally.
3. Score the model by leave-one-out cross-validation (Q²: remove one point, refit, predict it, repeat; 1 is perfect, 0 is no better than always guessing the mean, negative is worse than that).
4. Generate candidate points by whichever proposal mechanism that function's evidence currently justifies, and select one.
5. Submit it, wait a week, record what came back.

Step 3 is what makes this a documented collection process rather than an ad-hoc one, because **the Q² score decides how much authority the model is given over the next query**. A function whose model predicts held-out points well is allowed to choose a location anywhere in a region. A function whose model is mediocre is allowed only to *rank* about a dozen small candidate steps away from the best known point — it can say which direction looks better, not where to go. A function whose model is no better than guessing the mean is not allowed to choose at all, and its queries are spent on measurement: space-filling, bracketing a sign change, or confirming its best reading. Promotion and demotion both follow the score, re-measured every round, so a function's tier is a measurement rather than a standing judgement about it.

The practical consequence for the data set is that the *process* that generated row *k* for a given function is not necessarily the process that generated row *k+1*. The proposal mechanism in force for every round is recorded in `WEEKLY_LOG.md`, and the current one per function in `STATUS.md`. Without those two files the trial logs are not interpretable as a design.

### What strategy guided the choices?

In summary, and in full in `MODEL_CARD.md`: deliberately exploratory early, deliberately exploitative late. Early rounds bought information — wide trust regions, optimism bonuses in the acquisition function, probes aimed at settling structural questions such as which inputs matter and how large the noise is. From round 10 onward, with the budget nearly spent, every function moved to pure exploitation: optimism weights to zero, proposals taken as the model's predicted best, because information has no value if there is no round left in which to use it.

Three decisions are worth flagging as collection events in their own right, because they produced rows that no automated policy would have produced. On F1, a sign-bracket search — stepping from the best positive reading toward the nearest negative one — replaced acquisition entirely, after the data revealed that the function's dominant feature is a *trough* and the maximum sits on the positive lobe beside it; that search gained roughly twelve orders of magnitude over four rounds. On F5, the surrogate's local slope contradicted four consecutive readings that were rising monotonically along one axis, so I overrode the model with an explicit probe past its highest reading; the probe set the project's largest improvement. On F4, I released the trust region for one round purely to test whether a better basin existed elsewhere; with the whole domain available the acquisition came back to the same neighbourhood, which answered the question at the cost of one trial.

### Over what time frame?

The supplied initial designs were issued on 23 July 2026. Rounds 1 to 10 returned between 30 July and 1 October 2026, one per week; round 11 was submitted on 1 October 2026 with its outputs pending. Two rounds remain after it. The collection window and the modelling window are therefore the same ten weeks: the data set and the strategy that produced it grew together, and neither can be read as fixed while the other varied.

### Who collected it, and were they compensated?

I generated every bought row. The evaluation oracle is operated by the course. There was no compensation and no third-party collection.

### Was there ethical review?

None was required or sought: synthetic functions, no human subjects, no personal data.

---

## 4. Preprocessing, cleaning and labelling

### What preprocessing was done?

Nothing is done to the stored data. All transformation happens at model-fitting time, which keeps the record raw and reproducible. Four transformations are applied in the fitting pipeline.

**Output standardisation.** Outputs are centred and scaled before the Gaussian process is fitted, which is standard practice and prevents the kernel's own scale parameters from having to absorb the output's units.

**Log transforms on two functions.** F1 is fitted on log₁₀|y| and F5 on log y, because their outputs span roughly 113 and 4 orders of magnitude respectively and no stationary model can describe that on a linear scale. The F1 transform is floored at 10⁻³⁰⁰ before taking the logarithm, which is not cosmetic: the exact zero described above produced a negative infinity and crashed the fit until the floor was added. I also tested and rejected a signed-log transform for F1 — it is monotone in *y*, which is all that matters for ranking, but the sign change is a discontinuity the model cannot smooth across, and the cross-validation score fell to roughly −0.29.

**Boundary clamping.** Proposed coordinates are clamped strictly inside the open unit interval with a margin of 10⁻⁶ and printed to six decimal places, so a submitted coordinate never reads as exactly 0 or 1. This is a submission-format requirement, but it has a visible effect on the data: several coordinates sit at 0.000001 or 0.999999, and those are boundary values, not interior ones.

**Nothing is removed.** No outlier rejection, no deduplication, no smoothing. The exact-zero row on F1 and the catastrophic −32.6 reading on F4's initial design are both still in the data. With 254 rows in total, discarding an observation that cost a week is a decision that needs a far better justification than "it looks wrong".

### Is the raw data available?

The raw data *is* the data set — the `.npy` files and `new_trials.csv` under each `function_i/` directory are exactly what the oracle returned. The supplied initial designs are additionally duplicated unmodified under `initial_data/`, so even an accidental overwrite of a working copy is recoverable.

### Intended uses

Within this project the data set supports surrogate fitting, model selection between candidate surrogate families by cross-validation, per-dimension sensitivity reasoning, noise estimation where replicates exist, and the audit trail behind every submitted query.

Beyond this project, its honest value is as a **worked case study in decision-making under a severe evaluation budget**. It pairs a complete query history with a written record of what I believed before each query and what the result did to that belief, including the occasions when the result refuted me. That pairing is rarer and more useful than the numbers themselves.

### Inappropriate uses

Several, and they follow directly from the collection process rather than from caution.

It should not be used to **benchmark optimisation algorithms**. The sampling is adaptive and the design is entangled with the method that produced it; any algorithm evaluated on this data would be evaluated on a sample chosen by a different algorithm.

It should not be used to **characterise the functions globally, or to claim global optima**. Later rounds cluster tightly around each function's best known point. Large regions of every domain were never sampled, and on the higher-dimensional functions most of the domain was never within reach of the budget. A second basin anywhere outside the sampled neighbourhoods would be invisible in this data, and nothing here can rule one out.

It should not be used to **fit a general-purpose predictive model** of any of these functions. A model fitted to this data will be accurate in a small neighbourhood and unconstrained everywhere else, and — as the model card documents in detail — a high cross-validation score on this data does not demonstrate otherwise, because cross-validation tests interpolation among points the model already has, not extrapolation to the point about to be bought.

It should not be read as an **unbiased sample for statistical inference** about the functions' typical behaviour. The sample was chosen to be unrepresentative on purpose.

---

## 5. Distribution and maintenance

### Where is it available, and under what terms?

In the public GitHub repository for this capstone, alongside the code that produced it, the weekly log that interprets it, and the model card that documents the strategy. The repository is public so that peers and facilitators on the programme can read and critique it.

The data and documentation are coursework and are shared for educational and review purposes. Anyone is welcome to read, cite or reuse them with attribution, subject to the restrictions on inappropriate use above and to one practical caveat: the underlying functions belong to the course, so the data set cannot be extended by anyone outside it. What is published is all there will ever be of it, apart from the two rounds still to come.

### How will it be maintained?

By me, for the remaining duration of the capstone. Two rounds remain; each will append one row per function to the trial logs, one dated entry to `WEEKLY_LOG.md`, and a refresh of `STATUS.md`. After the final round the data set is complete and frozen, and no further updates are expected. There is no versioning scheme beyond git history, which is sufficient at this size — the commit log *is* the change log, and because the trial files are append-only, a diff shows exactly which observation arrived when.

### Will errors be corrected?

Corrections to the *documentation* yes, promptly, and the git history will show them. The *observations* are never corrected, because there is nothing to correct them against — the oracle's output is the ground truth by definition. Where I made a mistake that affected the data, as with F4's misrouted trial, the mistake is documented in place rather than repaired.

### Known limitations, restated

The data set is small, adaptively and therefore non-randomly sampled, concentrated near each function's incumbent best, boundary-heavy on several coordinates, almost entirely unreplicated, missing one trial on F4 through my own routing error, and path-dependent in a way that is easy to understand but impossible to undo — each round's choice was conditioned on the previous best, so an early lucky or unlucky reading on any function steered everything that followed on it. It is a faithful record of a search, which is exactly what it is for, and it should not be mistaken for a description of the things searched.

---

## Related documents

- [`MODEL_CARD.md`](MODEL_CARD.md) — the optimisation approach that generated the bought rows.
- [`WEEKLY_LOG.md`](WEEKLY_LOG.md) — dated record of every round: what was submitted, what returned, what changed and why.
- [`STATUS.md`](STATUS.md) — current configuration for each function, with a note on which settings are live and which are inert.
- [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) — plain-language guide to the code and the weekly routine.
- [`bbo_toolkit.py`](bbo_toolkit.py) — the shared implementation.
