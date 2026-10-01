# Bayesian Black-Box Optimisation — Capstone Project

Imperial College Professional Certificate in Machine Learning and Artificial Intelligence.

**Documentation:** [Datasheet](DATASHEET.md) · [Model card](MODEL_CARD.md) · [Weekly log](WEEKLY_LOG.md) · [Current status per function](STATUS.md) · [How it works](HOW_IT_WORKS.md)

---

## 1. Project overview

This repository documents my work on a black-box optimisation (BBO) challenge: a set of eight unknown functions that can only be interacted with by submitting an input and waiting for the value that comes back. There is no formula, no gradient and no source code — only the input/output pairs I have paid for.

The goal is to find the input producing the largest possible output for each function, using a strictly limited number of queries. The cost structure is what makes it interesting: each submitted point takes a week to return, so there is no trial and error and no restarting. Every query must be justified before it is spent.

This mirrors a large family of real ML problems — tuning models that take days to train, screening drug candidates, designing physical experiments — where the objective is costly, opaque and non-differentiable, and the skill tested is not "run more experiments" but "decide what is worth measuring next". That is the transferable part for my career: surrogate modelling, reasoning about what a model does *not* know, and defending an expensive decision before its outcome is known.

## 2. Inputs and outputs

Each function takes a fixed-length vector of real numbers, every coordinate inside the unit interval, and returns a single scalar. Dimensionality varies by function, from two up to eight.

A query and its response look like this:

```
input : [0.412703, 0.860114, 0.235990]
output: -0.047219
```

Coordinates must sit strictly inside the open unit interval, proposals are clipped away from the exact endpoints, and only one point per function may be submitted per round. The returned scalar is the entire feedback signal — no gradient, no uncertainty, no diagnostics, no indication of whether a reading was noisy. Each function stores its immutable initial observations plus an append-only trial log, so the model can be rebuilt from scratch at any time.

## 3. Challenge objectives

Every function is to be **maximised**. The binding constraints are a cap of 13 queries per function, a week of latency per query, a strictly sequential process with no batching, and completely unknown structure. The functions vary in character: some smooth with a single peak, some with many local optima, one almost entirely flat with the reward hidden in a tiny region, some returning values across several orders of magnitude. Success is the highest value found by the end of the budget — but also a defensible account of why each query was chosen, which matters more than any single lucky reading.

## 4. Technical approach

The backbone is Bayesian optimisation: a probabilistic surrogate fitted to every observation of a function, refitted from scratch after each returned value, and a proposal mechanism that turns the posterior into one point to buy next. A Gaussian process was chosen over regression or support-vector approaches deliberately — those return a point prediction, whereas on a budget this small the *uncertainty* is the more valuable output, because it is what identifies where a query could still teach you something.

What distinguishes the approach as it stands is that **the model does not automatically get to choose the next point.** Every round, each function's surrogate is scored by leave-one-out cross-validation, and that score decides how much authority it is given: a model that predicts held-out points well chooses a location freely within a trust region; a mediocre model is allowed only to rank about a dozen small candidate steps; a model no better than guessing the mean chooses nothing at all, and its queries go to measurement instead — space-filling, bracketing a sign change, or confirming its best reading. Promotion and demotion both follow the score, re-measured weekly, so a function's tier is a current measurement rather than a standing judgement.

Three surrogate families compete per function by that same score: a Matérn 5/2 Gaussian process with a lengthscale per dimension, an additive Gaussian process that forbids interactions between inputs, and a quadratic trend with a Gaussian process on the residual. The recurring finding, which ran against my expectations, is that **constrained models beat flexible ones under a tight budget** — a flexible model with thirty points spends its flexibility fitting noise.

The balance between exploration and exploitation was tilted deliberately: exploratory early, exploitative late. Early rounds bought information — wide trust regions, optimism bonuses, probes aimed at settling structural questions such as which inputs matter and how large the measurement noise is. From round 10 onward every exploration weight is zero, because information has no value if there is no round left in which to use it.

[`MODEL_CARD.md`](MODEL_CARD.md) gives the full account, including the version history, the performance across all eight functions, and the failure modes. All eight have improved on their supplied initial design; the two largest gains came from the two occasions when I overrode the surrogate rather than deferred to it, which is the most uncomfortable and probably the most instructive result in the project.

## 5. Repository contents

| Path | What it is |
|---|---|
| [`DATASHEET.md`](DATASHEET.md) | Datasheet for the query data set: motivation, composition, how the queries were generated, preprocessing, intended and inappropriate uses, maintenance. |
| [`MODEL_CARD.md`](MODEL_CARD.md) | Model card for the optimisation approach: intended use, strategy across the rounds, performance, assumptions, limitations, ethical considerations. |
| [`WEEKLY_LOG.md`](WEEKLY_LOG.md) | Dated record of every round — what was submitted, what came back, what changed and why. Newest week at the top. Includes the mistakes. |
| [`STATUS.md`](STATUS.md) | One reference card per function with its current configuration, and a table of which settings are live under which proposal mechanism. |
| [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) | Plain-language guide to the code, the weekly routine, every setting, and how to read the output. |
| [`bbo_toolkit.py`](bbo_toolkit.py) | Shared implementation: surrogates, acquisition functions, proposal mechanisms, cross-validation. |
| `function_1/` … `function_8/` | Per function: the optimiser notebook, the immutable initial design, and the append-only trial log. |
| `initial_data/` | Untouched duplicate of the supplied initial designs. |
| `surrogate_shootout.py` / `.csv` | The model comparison that selected the three surrogate families: eight candidate models scored against all eight functions by cross-validation. |
| `GP_surrogate_per_dimension.ipynb` | Surrogate visualisation — the fitted mean and uncertainty band along each input dimension, with partial dependence. |
| `reference/` | Problem descriptions and the initial exploratory analysis. |
| `WEEK4_PLAN.md` / `WEEK4_POINTS.md` | Round-specific working notes, kept because the weekly log references them. |
| `archive/` | Superseded notebooks and earlier strategy notes, kept for the record. |

## 6. Reproducing this

Python 3 with NumPy, SciPy, scikit-learn 1.8.0, pandas and matplotlib. Open any `function_i/F{i}_optimizer.ipynb` and run it top to bottom: it loads that function's data, fits the surrogate, scores it, and prints a proposal. The random seed is fixed at 0 throughout.

One caveat, stated because it is easy to be caught by: kernel hyperparameter fitting is a non-convex optimisation that can settle in different basins on different numerical libraries, so the *procedure* reproduces exactly while an individual proposed point may differ in its later decimals. Before reading a notebook's configuration, check [`STATUS.md`](STATUS.md) for which settings are actually live for that function — the configuration block is shared across all eight, and several of its values are inert depending on the proposal mechanism in force.
