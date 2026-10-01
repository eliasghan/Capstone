# Model Card — Q²-Gated Bayesian Optimisation

*Imperial College Professional Certificate in Machine Learning and Artificial Intelligence — Black-Box Optimisation capstone.*
*Author: Elias. Version 4.0 (endgame configuration), 1 October 2026, after round 11 of 13 was submitted.*

This model card follows the framework introduced in Mini-lesson 21.2 (Mitchell et al., *Model Cards for Model Reporting*). The object being documented is not a single trained model but a **decision procedure**: the thing that turns the observations in [`DATASHEET.md`](DATASHEET.md) into one query per function per week. Eight surrogate models sit inside it, refitted from scratch every round. What is worth documenting is the policy that decides how much to believe them.

---

## 1. Overview

**Name.** Q²-Gated Bayesian Optimisation — "Q²-gated" because a leave-one-out cross-validation score, recomputed every round, is what determines how much authority each function's surrogate is given over the next query.

**Type.** Sequential model-based optimisation for expensive black-box objectives. A probabilistic surrogate is fitted to all observations of a function, and a proposal mechanism converts that posterior into a single point to evaluate. It is not a trained predictor with a fixed set of weights; it is re-derived from the data every round, which means its behaviour is a function of the data set as much as of the code.

**Version history.** The approach changed substantially four times, and the versions are the honest unit of description because the early version would not have produced the later queries.

| Version | Rounds | What characterised it |
|---|---|---|
| 1.0 | 1–2 | Textbook Bayesian optimisation. One Gaussian process per function with a Matérn 5/2 kernel, a lengthscale per dimension, a learned noise term. Expected Improvement or Upper Confidence Bound chosen from what each function's description implied about its shape. Uniform treatment of all eight. |
| 2.0 | 3–4 | Structure-driven. Fitted lengthscales revealed that several functions depend on far fewer inputs than their nominal dimensionality. Exploration was redirected onto the inputs carrying signal, and the first function whose readings contained no usable signal was taken off the surrogate entirely and given geometric space-filling instead. |
| 3.0 | 5–9 | Q²-gated and multi-surrogate. Leave-one-out cross-validation introduced as the governing metric; three surrogate families competed per function by that score; the authority tiering described below became the core of the method. |
| 4.0 | 10–13 | Endgame. Every exploration weight set to zero, every proposal taken as the model's predicted best, trust regions at their tightest. Functions whose models still cannot predict spend remaining trials confirming their best reading rather than hunting new ones. |

**Implementation.** One shared module, [`bbo_toolkit.py`](bbo_toolkit.py), about 690 lines, holding every surrogate, acquisition function and proposal mechanism. Eight per-function notebooks hold nothing but configuration, data loading and a call into that module. Python 3 with NumPy, SciPy, scikit-learn 1.8.0, pandas and matplotlib. Random seed fixed at 0 everywhere.

---

## 2. Intended use

### Suitable for

Problems with the specific shape this capstone has: a scalar objective that is expensive to evaluate, opaque, non-differentiable, evaluated strictly one point at a time, with a budget measured in tens of evaluations rather than thousands. Real instances of that shape include tuning a model that takes days to train, screening physical or chemical candidates, and designing laboratory experiments. The distinguishing feature is that the cost of *deciding* is negligible against the cost of *measuring*, which is what justifies spending hours of analysis on a single point.

It is also suitable, and perhaps most useful, as a worked example of **how to decide how much to trust a model you cannot validate properly** — because the honest answer, documented below, is that cross-validation does not tell you, and the method's main contribution is a set of cheap checks that partially substitute.

### Use cases to avoid

**Cheap objectives.** If an evaluation costs seconds, this is strictly worse than random search or an evolutionary method. Almost all of the machinery here exists to avoid wasting evaluations, and it pays for that with analysis time and with strong modelling assumptions that more data would make unnecessary.

**High dimensions.** It was pushed to eight dimensions and is already visibly straining there: on the largest function the model is confident, scores near-perfectly on cross-validation, and was wrong in the same direction on seven consecutive queries. Beyond a few dozen dimensions, Gaussian process surrogates on this little data have no basis for their uncertainty estimates.

**Anything requiring a guaranteed global optimum.** The method returns the best value it observed. It offers no bound on the gap to the true maximum and cannot be made to.

**Parallel or batch evaluation.** Every mechanism here assumes one point, then full information, then the next point. A batch version would need different acquisition logic entirely.

**Safety-critical or irreversible decisions.** The method deliberately buys points it expects to be poor when the information is worth more than the value. That is correct under a budget and unacceptable where a bad evaluation causes harm.

---

## 3. Details of the approach

### The surrogate layer

Three surrogate families compete for each function, and the winner is whichever predicts held-out points best:

**Matérn 5/2 Gaussian process** with a separate lengthscale per input dimension, a learned white-noise term and standardised outputs, refitted with ten restarts of the kernel optimiser. The default, and the most flexible.

**Additive Gaussian process** — a sum of one-dimensional kernels, which *forbids* interactions between inputs. This is a strong assumption, and the point is that on this little data a strong assumption is often worth more than flexibility. It more than doubled the predictive score on one function the round it was introduced, and is now the best-scoring family on two of the eight.

**Quadratic trend plus Gaussian process residual.** A polynomial trend captures global curvature; a Gaussian process on the residual supplies the uncertainty estimate a bare polynomial cannot. This wins on the two functions modelled on a log scale, where a peak of their shape is close to an exact quadratic.

The general lesson, and it ran against my expectations at the start, is that **constrained models beat flexible ones under a tight budget**. A flexible model with thirty points spends its flexibility fitting noise and arbitrary curvature; a constrained model spends its few degrees of freedom on the structure that is actually there.

### The gate: leave-one-out Q²

Every round, for every function, each candidate surrogate is scored by removing one observation, refitting, predicting the held-out point, and repeating across all observations. Q² of 1 is perfect prediction of points never seen; 0 is no better than always guessing the mean; negative is worse than that.

A challenger replaces the incumbent surrogate only on a clear margin of about 0.1, because below that the difference is cross-validation noise on samples this small, and churning the model family between rounds would make the record uninterpretable.

### The tiering: how much authority the model gets

This is the core of the method. The Q² score decides not what the next point is but **who chooses it**.

| Q² | Authority | Mechanism |
|---|---|---|
| above ~0.7 | the model chooses a location | Acquisition function maximised over a trust region around the best point. |
| ~0 to 0.7 | the model ranks, it does not choose | About a dozen small candidate steps are constructed geometrically from the best known point; the model only orders them. A wrong ordering costs a small step, not a wasted round. |
| ~0 or below | the model chooses nothing | Queries go to measurement: geometric space-filling, bracketing a sign change, or replicating the best reading. |

Promotion and demotion both follow the score, re-measured every round, so a tier is a current measurement rather than a standing verdict. One function was demoted to ranking-only and later promoted back to full control when its score roughly doubled; another scores 0.98 and is *still* restricted to ranking, for reasons in the limitations section that are the most important thing on this card.

### The proposal layer

**Acquisition.** Expected Improvement, `EI = imp·Φ(Z) + σ·φ(Z)` with knob `xi`, or Upper Confidence Bound, `μ + β·σ`, maximised over a box. With `β = 0`, UCB degenerates to the predicted mean — which is exactly what the endgame wants, and is how pure exploitation is expressed here rather than as a separate mode.

**Local.** A dozen or so bounded steps from the incumbent along each axis, with the step size set from the evidence about local curvature rather than from the fitted lengthscales. The model ranks them.

**Bracket.** Where the data shows a sign change, step from the best positive reading toward the nearest negative one. Purely geometric; used on the function whose dominant feature turned out to be a trough rather than a peak.

**Explore.** Maximin space-filling — the point furthest from every existing observation. No model involvement at all.

**Probe.** A manually specified point, queued in the notebook, that overrides the proposer for one round. Used three times, each time recorded with its reasoning in `WEEKLY_LOG.md`. The override exists because a documented disagreement with the model is more honest than quietly tuning parameters until the model produces the point I already wanted.

### How the approach evolved, and what forced each change

The changes were not refinements of a plan. Each was forced by a specific failure that the data made visible.

**Round 2 — lengthscales as structure.** The first real feedback made the refits informative, and per-dimension lengthscales showed several functions depending on a subset of their inputs. This was genuinely useful and also set up the method's most expensive recurring error, described below.

**Round 3 — abandoning the surrogate where it had nothing.** One function's readings contained no usable signal, and continuing to let its model choose points was spending trials on noise. Space-filling replaced it. Separately, the round-3 submission for one function was routed to the wrong function — a four-dimensional point sent to a different four-dimensional function — costing a trial permanently. A routing check is now step zero of every round.

**Rounds 4–5 — cross-validation introduced, and a surrogate shootout run.** Eight model variants scored against all eight functions. This produced the constrained-beats-flexible finding and the three-family line-up still in use.

**Round 6 — the sign-bracket discovery.** One function's largest-magnitude reading was *negative*: the source is a trough, and the maximum sits on the positive lobe beside it. No acquisition function was going to find that, because the model saw a minimum and correctly avoided it. Reframing the problem as a sign-bracketing search gained roughly twelve orders of magnitude over four rounds.

**Round 7 — noise measured rather than assumed.** A deliberate replicate showed one function's fitted noise was about sixty times larger than the truth. Real structure had been absorbed into a noise term for six rounds. Its noise bounds are now pinned near the measured value.

**Round 8 — step sizes taken off the lengthscales.** On one function the step size was nominally halved several times with no effect on the output, because the largest step was saturating against an internal cap and the model kept selecting the same large jump. On another, the lengthscales said the surface moved slowly near the optimum while the measured readings said it moved roughly fourteen times faster. Both were fixed by setting step sizes from measured local differences rather than from fitted hyperparameters.

**Round 9 — the saturated-lengthscale rule.** One function produced a false verdict of "this input is irrelevant" twice, and the second time cost two rounds of driving a coordinate toward zero while the output fell each time. A lengthscale pinned at its upper bound does not mean an input does nothing; it means the model cannot distinguish weak influence from none *at the ceiling it was given*. Lowering the ceiling is the test. Doing so left every lengthscale fitted rather than pinned and raised that function's score.

**Rounds 10 onward — conversion rather than acquisition of information.** Exploration bonuses exist to buy information. With a handful of rounds left there is no round in which to use it, so the weights went to zero across all eight functions. Six of eight now propose points their own models rate below the incumbent, which is what running out of local improvement looks like and is worth stating plainly rather than dressing up.

---

## 4. Performance

### Metrics

**Best observed value** is the primary metric, because it is the competition's metric. It is also a metric with an awkward property worth naming: it rewards a single lucky reading as much as a well-reasoned search, and on a noisy function repeated draws at a known peak are a rational play against it.

**Leave-one-out Q²** measures how well a surrogate predicts points it has not seen, and is the metric that governs the procedure.

**Prediction error on the realised point** — the gap between what the model predicted for the submitted point and what came back — is the calibration metric, and the only one that tests extrapolation. It is the metric that caught the failure described in the limitations, and Q² could not have.

**Improvement over the supplied initial design** is the attribution metric: how much of the final result is the search rather than the free sample.

### Results across the eight functions

Best value from the supplied initial design against best value after ten bought rounds (nine on F4):

| Fn | d | Best from initial design | Best now | Improvement | Q² | Surrogate | Proposal mechanism |
|---|---|---|---|---|---|---|---|
| F1 | 2 | 7.7e−16 | **1.039e−4** | ~11 orders of magnitude | 0.856 | quadratic on log₁₀\|y\| | bracket + probe |
| F2 | 2 | 0.6112 | **0.6291** | +0.018 | 0.608 | additive GP | local, EI, near-replicate steps |
| F3 | 3 | −0.03484 | **−0.02524** | +0.0096 | 0.059 | Matérn 5/2 | local, predicted mean |
| F4 | 4 | −4.0255 | **0.5895** | +4.615 | 0.984 | Matérn 5/2 | local, predicted mean, tiny steps |
| F5 | 4 | 1088.86 | **4643.17** | ×4.26 | 0.834 | quadratic on log y | local + explicit probe |
| F6 | 5 | −0.7143 | **−0.2497** | +0.4645 | 0.884 | additive GP | local, predicted mean |
| F7 | 6 | 1.3650 | **2.5758** | ×1.89 | 0.851 | Matérn 5/2 | acquisition, UCB β=0, trust region |
| F8 | 8 | 9.5985 | **9.9731** | +0.3746 | 0.994 | Matérn 5/2 | acquisition, UCB β=0, trust region |

**All eight improved on their supplied design.** The two largest gains came from the two occasions when I overrode the surrogate rather than deferred to it — the sign-bracket reframing on F1 and the explicit probe past the highest reading on F5 — which is the most uncomfortable and probably the most informative result in the project.

### Where the method worked, and where it did not

It worked where the data let a *constrained* model be fitted and where the evidence was read as evidence rather than as a hyperparameter. F5's four-fold gain came from recognising that its output spans four orders of magnitude, modelling it on a log scale, noticing that the model's local slope contradicted four consecutive rising readings, and backing the readings. F1's eleven orders came from noticing that the biggest number in the data had the wrong sign. Neither was an acquisition function doing its job; both were diagnosis.

It struggled on F3, where no surrogate family gets past a Q² of about 0.13 and the honest position is that after ten bought trials I still cannot predict that function. It is held on short steps and small gains, which is the right response to not knowing, but it is not a success.

The most instructive case is F4. It scores 0.984 on cross-validation and is the worst-behaved function here. Its surface moves roughly eighteen units per unit of distance near the optimum while its fitted lengthscales report values near 1.3 — an underestimate of local curvature by more than tenfold. Tightening the kernel makes the cross-validation score *worse*, falling to about 0.85, because the smooth background is real too: this is a narrow spike on a smooth surface, and one lengthscale cannot describe both. Six consecutive attempts failed to beat its very first trial. The seventh succeeded, once the step size was set from measured differences instead of from the model's own hyperparameters.

---

## 5. Assumptions and limitations

### Assumptions

**That the surrogate's uncertainty is meaningful.** This is the load-bearing assumption and everything inherits it — which candidate to choose, how far to step, when to stop exploring, when to stop entirely. It has been violated at least twice in ways the data could show. On F8, every prediction the model ever made came in high: seven queries, seven over-predictions, averaging about 0.09. That is bias, not noise, and a cross-validation score of 0.99 cannot detect it. On F5, the model was confident about a region where the sign of its local slope was simply wrong.

**That a model validated globally is reliable locally.** Demonstrably false on F4. A cross-validation score is dominated by the bulk of the data; the search operates in a tight cluster that contributes a handful of folds. The score certifies interpolation among points the model has, not extrapolation to the point about to be bought — and the point about to be bought is always, by construction, outside the data.

**That a long lengthscale means an unimportant input.** False, and expensive. It means the model cannot distinguish weak influence from none at the ceiling it was given. Acting on the raw verdict cost trials twice on the same function.

**That the recorded value is the function's value.** On at least one function this is false — readings at nearly identical points differ by far more than their separation justifies.

**That smoothness and stationary noise hold well enough.** The Matérn kernel assumes a particular smoothness, and a single noise term assumes the noise is the same everywhere. Neither was tested beyond the two deliberate replicates.

### Limitations and failure modes

**The budget, and the local search it forces.** This is the decisive limitation and every other choice is downstream of it. With thirteen evaluations per function, the only defensible strategy on most of them is refinement around the best point found, which means the results are local optima with no guarantee of being global. Large regions of every domain were never sampled; on the higher-dimensional functions most of the domain was never within reach. The honest claim is that the method finds good values efficiently and documents why each query was chosen. It is not a claim to have found the global maximum, and the data could not support that claim for any function here.

**Cross-validation cannot detect extrapolation bias.** The method's own governing metric is blind to its most consequential failure mode. The partial remedy — tracking the prediction error on each realised point, round by round — is a diagnostic I added only after it had already cost me, and it is the single change I would make earliest if I started again.

**Path dependence.** Each round conditions on the previous best, so an early lucky or unlucky reading steers everything after it on that function. There is no mechanism in the method that recovers from a bad early commitment, and no way to measure whether one happened.

**The human in the loop is load-bearing and unaudited.** Three of the project's most valuable decisions were manual overrides of the model. That is a strength in outcome and a weakness in method: the procedure as written does not generate those decisions, and a reviewer cannot tell from the code when an override was right and when it was me pattern-matching on noise. The log records the reasoning, which is the best mitigation available, but it is not the same as a rule.

**Hyperparameter fitting is not bit-reproducible across machines.** Kernel fitting involves a non-convex optimisation that can settle in different basins on different numerical libraries. The procedure reproduces exactly; individual proposals may not.

---

## 6. Ethical considerations

There are no human subjects here and no personal data, so the ethical content of this card is about **the honesty of a documented decision process**, which is where it belongs for a method whose entire output is expensive, irreversible decisions.

### Transparency and reproducibility

A reviewer who clones the repository has the immutable initial designs; the append-only trial logs; a dated weekly log recording, for every round, what was submitted, what came back, what changed and why; per-function status cards stating the current configuration; a plain-language guide to the code; one shared library rather than eight divergent copies; and a fixed random seed. Every setting in every notebook carries a dated comment explaining why it holds its current value, so a reader encountering an unusual number sees the evidence that produced it rather than having to guess.

Three things a reviewer would additionally need, and I would rather state them than let someone discover them. **Pinned package versions**, because of the non-determinism noted above — a reviewer can reproduce the *procedure* exactly while not reproducing every *point*, and that distinction should be stated rather than glossed over. **The reasoning behind the manual overrides**, which is in the log and is the part I would expect a careful reader to interrogate hardest. And **the knowledge that `STATUS.md` exists**, because the configuration blocks contain settings that are inert under the current proposal mechanism, and reading a value that is not live is the easiest way to misunderstand what a function is doing — which is exactly why that file leads with a table of which settings are live in which mode.

### Why this matters beyond the coursework

A method like this is used in settings where the evaluations are drug candidates, physical prototypes or production experiments, and where the decision to spend one is reviewed by people who will not refit the model themselves. In those settings the artefact that matters is not the proposal but the **argument for the proposal**, and an argument that cannot be audited is not fit for the purpose. Recording failures is the specific thing that makes the record trustworthy: a log that only contains successes gives a reviewer no way to calibrate how much to believe the successes. The two false "irrelevant input" verdicts, the misrouted trial, the noise term that was wrong by a factor of sixty for six rounds, and the guardrail that silently filtered out every candidate better than the incumbent are in the log for that reason, and they are the most useful entries in it.

There is also a straightforward adaptation point. Because the authority tiering is driven by a measured score rather than by my judgement of each function, the policy transfers to a new problem without my having to transfer my intuitions about these eight surfaces. That is a deliberate design choice and the main thing I would carry forward.

### Would more detail improve this card?

In two places, yes. A fully specified environment lock would turn "reproducible in procedure" into "reproducible in output", and that is a real gap rather than a stylistic one. And a per-round table of predicted against realised values for all eight functions — the calibration record — would let a reader assess the models' trustworthiness independently rather than taking my account of it; the raw material is in the logs but it is not assembled.

Beyond those, I think additional detail would reduce clarity rather than add to it. The card's job is to let a reader decide whether to trust the method and understand when it fails. The per-function minutiae — exact step sizes, lengthscale bounds, noise bounds, which guardrail was raised in which round — already live in `STATUS.md` and `WEEKLY_LOG.md`, where they are indexed by function and by date and can be consulted when a specific question arises. Duplicating them here would make the card longer and the argument harder to follow, and a model card that is not read is worse than a short one that is. The structure is layered on purpose: this card for the reasoning and the failure modes, the status file for the current state, the log for the history, the code for the ground truth.

---

## Related documents

- [`DATASHEET.md`](DATASHEET.md) — the data set this approach generated and consumes.
- [`WEEKLY_LOG.md`](WEEKLY_LOG.md) — dated record of every round, including the failures referenced above.
- [`STATUS.md`](STATUS.md) — current configuration per function, and which settings are live.
- [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) — plain-language guide to the code and the weekly routine.
- [`bbo_toolkit.py`](bbo_toolkit.py) — the shared implementation.
