# Model Card — Q²-Gated Bayesian Optimisation

*BBO capstone project. Completed from the Module 25 model card template, finalising the version first drafted in Module 21.*
*Author: Elias. Version 4.0, record final at 12 bought trials per function.*

The object documented here is not one trained model but a **decision procedure**: the thing that turns the observations described in [`datasheets/`](datasheets/) into one query per function per week. Eight surrogate models sit inside it, refitted from scratch every round. What is worth documenting is the policy that decides how much to believe them.

---

## Model Description

**Input.** The complete observation history for one function: a design matrix of every input vector evaluated so far, with every coordinate in the open unit interval, and the corresponding vector of scalar outputs. Dimensionality is 2, 3, 4, 5, 6 or 8 depending on the function; history size runs from 22 to 52 observations. There is no other input — no gradient, no uncertainty from the oracle, no metadata, no indication of whether a reading was noisy.

**Output.** A single input vector to evaluate next, clamped strictly inside the unit interval with a margin of 10⁻⁶ and reported to six decimal places. Alongside it the procedure emits the diagnostics that justify the choice: the surrogate's predicted mean and standard deviation at that point, its leave-one-out cross-validation score, the fitted lengthscale per input, and the ranked table of candidates that were considered and rejected.

**Model Architecture.** Three layers.

*The surrogate layer* fits three model families to the history and scores each by leave-one-out cross-validation (Q²: remove one observation, refit, predict it, repeat; 1 is perfect, 0 is no better than always guessing the mean, negative is worse than that).

- **Matérn 5/2 Gaussian process** with a separate lengthscale per input, a learned white-noise term, standardised outputs and ten restarts of the kernel optimiser. The flexible default.
- **Additive Gaussian process** — a sum of one-dimensional kernels, which *forbids* interactions between inputs. A strong assumption, and the point is that on this little data a strong assumption is often worth more than flexibility.
- **Quadratic trend plus Gaussian-process residual.** A polynomial captures global curvature; a GP on the residual supplies the uncertainty a bare polynomial cannot.

Two functions are fitted on a transformed output — log₁₀|y| and log y — because their raw outputs span roughly a hundred and four orders of magnitude respectively. A challenger family replaces the incumbent only on a margin of about 0.1, below which the difference is cross-validation noise at these sample sizes.

*The gating layer* is the distinctive part. **The Q² score decides not what the next point is but who chooses it:**

| Q² | Authority | Mechanism |
|---|---|---|
| above ~0.7 | the model chooses a location | acquisition function maximised over a trust region around the best point |
| ~0 to 0.7 | the model ranks, it does not choose | about a dozen small candidate steps are built geometrically from the best point; the model only orders them |
| ~0 or below | the model chooses nothing | queries go to measurement: space-filling, bracketing a sign change, or replicating the best reading |

Promotion and demotion both follow the score, re-measured every round, so a tier is a current measurement rather than a standing verdict about a function.

*The proposal layer* implements four mechanisms — **acquisition** (Expected Improvement, `imp·Φ(Z) + σ·φ(Z)`, or Upper Confidence Bound, `μ + β·σ`; with β = 0 the latter degenerates to the predicted mean, which is how pure exploitation is expressed), **local** (bounded steps from the incumbent, sized from measured local differences rather than from fitted lengthscales), **bracket** (step from the best positive reading toward the nearest negative one, used where the data shows a sign change), and **explore** (maximin space-filling, no model involvement). A fifth path, **probe**, serves a manually specified point that overrides the proposer for one round; it was used five times and every use is recorded with its reasoning in the weekly log.

Implementation: one shared module, [`bbo_toolkit.py`](bbo_toolkit.py), about 690 lines, plus eight notebooks holding only configuration and data. Python 3, NumPy, SciPy, scikit-learn 1.8.0, pandas, matplotlib. Random seed fixed at 0.

---

## Performance

**How performance is measured.** Four metrics, each answering a different question.

- **Best observed value** — the competition's metric, and the one reported below. It has an awkward property worth naming: it rewards a single lucky reading as much as a well-reasoned search, which on a noisy function makes repeated drawing a rational play.
- **Leave-one-out Q²** — how well a surrogate predicts points it has not seen. This is the metric that governs the procedure.
- **Prediction error on the realised point** — the gap between what the model predicted for the submitted point and what came back. This is the calibration metric and the only one that tests extrapolation.
- **Improvement over the supplied initial design** — the attribution metric: how much of the result is the search rather than the free sample.

**Results.** Best from the supplied design against best after twelve bought trials (eleven on Function 4, whose round-3 query was misrouted):

| Fn | Dim | From supplied design | Final | Change | Final Q² | Surrogate in use |
|---|---|---|---|---|---|---|
| 1 | 2 | 7.71e−16 | **1.05167e−4** | ~11 orders of magnitude | 0.915 | quadratic on log₁₀\|y\| |
| 2 | 2 | 0.611205 | **0.689468** | +0.078 | 0.689 | additive GP |
| 3 | 3 | −0.034835 | **−0.025235** | +0.0096 | 0.130 | Matérn 5/2 |
| 4 | 4 | −4.0255 | **0.602754** | +4.63 | 0.980 | Matérn 5/2 |
| 5 | 4 | 1088.86 | **8662.405** | ×7.95 | 0.803 | quadratic on log y |
| 6 | 5 | −0.714265 | **−0.249746** | +0.465 | 0.901 | additive GP |
| 7 | 6 | 1.364968 | **2.748654** | ×2.01 | 0.944 | Matérn 5/2 |
| 8 | 8 | 9.598482 | **9.974458** | +0.376 | 0.996 | Matérn 5/2 |

![Best value found by trial, for all eight functions](image.png)

**All eight improved on their supplied design.** The two largest gains came from the two occasions when the surrogate was *overridden* rather than followed — a sign-bracket reframing on Function 1 and an explicit probe past the model's predicted peak on Function 5 — which is the most uncomfortable and probably the most informative result here.

**What the numbers conceal.** The headline metric is best-observed, and on at least one function that is a draw from a distribution with a standard deviation of about 0.046, so a better method can lose to a luckier reading. Ranking strategies by final value is ranking them on one noisy observation each.

---

## Limitations

**The budget, and the local search it forces.** This is the decisive limitation and every other choice is downstream of it. With thirteen evaluations per function, the only defensible strategy on most of them is refinement around the best point found, which means the results are local optima with no guarantee of being global. Large regions of every domain were never sampled; on the higher-dimensional functions most of the domain was never within reach. The honest claim is that the method finds good values efficiently and documents why each query was chosen. It is not a claim to have found a global maximum, and the data could not support that claim for any function here.

**Cross-validation cannot detect extrapolation bias.** The procedure's own governing metric is blind to its most consequential failure mode. Function 8 scored 0.99 while over-predicting its own proposal on seven consecutive rounds — a systematic bias, not noise, that no Q² could see, because cross-validation tests interpolation among points the model already holds while every query is an extrapolation to a point it does not. Function 4 scored 0.98 while over-smoothing its own peak more than tenfold.

**Load-bearing assumptions, two of them demonstrably violated.** That the surrogate's uncertainty is meaningful — violated on Function 8 as above, and on Function 5 where the sign of the model's local slope was simply wrong. That a long fitted lengthscale means an unimportant input — false, and expensive: it means the model cannot distinguish weak influence from none at the ceiling it was given, and acting on the raw verdict cost trials twice on the same function. That the recorded value is the function's value — false on Function 2. And smoothness and stationary noise throughout, tested only by the two deliberate replicates.

**Dimensionality.** Pushed to eight inputs and visibly straining there. Beyond a few dozen, a Gaussian process on this little data has no basis for its uncertainty estimates.

**The human in the loop is load-bearing and unaudited.** Five of the project's most valuable decisions were manual overrides of the model. That is a strength in outcome and a weakness in method: the procedure as written does not generate those decisions, and a reviewer cannot tell from the code alone when an override was right and when it was pattern-matching on noise. The weekly log records the reasoning, which is the best mitigation available but is not the same as a rule.

**Path dependence and sampling bias.** Each round conditions on the previous best, so an early lucky or unlucky reading steers everything after it, and nothing in the method recovers from a bad early commitment. The resulting data set is dense in one small neighbourhood per function and sparse everywhere else.

**Reproducibility is procedural, not bit-exact.** Kernel fitting is a non-convex optimisation that can settle in different basins on different numerical libraries. The procedure reproduces exactly; individual proposals may differ in their later decimals.

---

## Trade-offs

**Exploration against exploitation, governed by budget rather than taste.** Optimism is only worth paying for if a later round exists in which to use what it buys. The schedule was therefore exploratory early — wide trust regions, uncertainty bonuses, whole trials spent on structural questions — and exploitative late, with every exploration weight set to zero from round 10. On the final trial it inverted completely: because the score is the best value ever observed, a failed probe costs nothing, so on functions where refinement was worth essentially zero a long shot strictly dominates. The last round was the most exploratory of the sequence.

**Flexibility against constraint.** A flexible model with thirty observations spends its flexibility fitting noise; a constrained model spends its few degrees of freedom on structure that is actually there. Constrained families won on half the functions. The cost is that the constraint can be wrong — the additive kernel is simply false if interactions matter, and nothing in the cross-validation score would reveal that if the design never varied two inputs together.

**Model authority against measurement.** The hardest trade-off, resolved by the tiering above plus a standing rule: when a model's local gradient contradicts a direct measurement taken with everything else held fixed, the measurement wins. Applying it produced the project's two largest gains. Over-applying it would reduce the method to one-at-a-time hill climbing.

**Breadth against interpretability.** Moving one axis per round tells you what caused a change; moving several captures more per trial but a failure cannot say which axis caused it. Axes were combined only in the final rounds, when there was no round left in which to diagnose a failure anyway — and the one combined move came back slightly worse and was duly uninterpretable.

**Information against conversion.** Five trials across the project were spent answering questions rather than chasing values — measuring noise, testing whether an input was inert, probing for a better basin. All five looked like wasted readings at the time and all five changed the strategy.

---

## Where performance degrades

The procedure is unsuitable, and will perform worse than simpler alternatives, in these circumstances:

- **Cheap objectives.** If an evaluation costs seconds, random search or an evolutionary method beats this comfortably. Nearly all the machinery exists to avoid wasting evaluations and pays for that in analysis time and strong assumptions.
- **High dimensions**, beyond a few dozen inputs, where the uncertainty estimates stop meaning anything.
- **Parallel or batch evaluation.** Every mechanism assumes one point, then full information, then the next.
- **Problems requiring a guaranteed global optimum.** The method returns the best value it observed and offers no bound on the gap to the true maximum.
- **Safety-critical or irreversible decisions.** The method deliberately buys points it expects to be poor when the information is worth more than the value — correct under a budget, unacceptable where a bad evaluation causes harm.
- **Functions whose structure the surrogate families cannot represent**, as on Function 3, where no family exceeded a score of about 0.13 and the method degenerated to careful small steps around the best point found.

---

## Ethical considerations

There are no human subjects and no personal data here, so the ethical content of this card is about **the honesty of a documented decision process** — which is where it belongs for a method whose entire output is expensive, irreversible decisions.

A reviewer who clones this repository has the immutable initial designs, the append-only trial logs, a dated weekly log recording for every round what was submitted, what came back, what changed and why, per-function status cards, a plain-language guide to the code, one shared library rather than eight divergent copies, and a fixed random seed. Every setting in every notebook carries a dated comment explaining why it holds its current value.

Three things a reviewer would additionally need, stated rather than left to be discovered: **pinned package versions**, because of the non-determinism noted above; **the reasoning behind the five manual overrides**, which is in the log and is the part a careful reader should interrogate hardest; and the knowledge that **[`STATUS.md`](STATUS.md) exists**, because the shared configuration block contains settings that are inert under the current proposal mechanism, and reading a value that is not live is the easiest way to misunderstand what a function is doing.

Recording failures is the specific thing that makes the record trustworthy. A log containing only successes gives a reviewer no way to calibrate how much to believe the successes. The two false "irrelevant input" verdicts, the misrouted trial, the noise term that was wrong by a factor of sixty for six rounds, and the guardrail that silently filtered out every candidate better than the incumbent are all in the log for that reason, and they are the most useful entries in it.

Methods like this are used where the evaluations are drug candidates, physical prototypes or production experiments, and where the decision to spend one is reviewed by people who will not refit the model themselves. In those settings the artefact that matters is not the proposal but the **argument for the proposal**, and an argument that cannot be audited is not fit for purpose. Because the authority tiering is driven by a measured score rather than by my judgement of each function, the policy transfers to a new problem without my having to transfer my intuitions about these eight surfaces — which is the main thing worth carrying forward.

---

## Related documents

- [`README.md`](README.md) — project overview and non-technical summary.
- [`datasheets/`](datasheets/) — one datasheet per function, plus a dataset-level overview.
- [`WEEKLY_LOG.md`](WEEKLY_LOG.md) — dated record of every round, including the failures referenced above.
- [`STATUS.md`](STATUS.md) — final configuration per function, and which settings are live.
- [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) — plain-language guide to the code and the weekly routine.
