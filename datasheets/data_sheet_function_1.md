# Datasheet - Function 1: Contamination source detection

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 1 - Contamination source detection.

**2. What real-world scenario does this function simulate?**
Detecting likely contamination sources in a two-dimensional area, such as a radiation field, where only proximity to a source yields a non-zero reading. The output is the strength of the reading at the sampled location.

**3. What is the dimensionality of the input?**
2-D.

**4. How many initial data points were provided?**
10, supplied as `initial_inputs.npy` with shape (10, 2) and `initial_outputs.npy` with shape (10,).

**5. What does the output represent?**
Signal strength at the sampled point. Readings are vanishingly small away from a source and can be either sign.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (10, 2), outputs (10,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_1/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 22 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
Deterministic. Readings at points a thousandth apart sit on a smooth curve with no scatter, and a peer who took repeat readings reported them identical. Nothing in the strategy had to allow for measurement noise here.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
Neither unimodal nor multimodal in the usual sense: the function is **zero almost everywhere**, to the limit of floating-point representation, with one tiny active region. Observed magnitudes span from about 1e-117 up to about 1e-2. Within the active region the structure is a **trough** - the largest-magnitude reading is negative - with a thin positive lobe beside it. A space-filling probe elsewhere in the square returned *exactly* zero, which closed the question of a second source.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation for the first rounds; then a **sign-bracketing search**, which is not a standard BO method at all. Once the data showed a negative trough with a positive lobe beside it, each trial stepped from the best positive reading a fixed fraction of the way toward the nearest negative one. The final rounds used explicit probes at the vertex of a parabola fitted through the three readings sitting on the lobe.

**2. Why did you choose this method for this particular function?**
An acquisition function was never going to find the maximum here. The model saw a deep minimum and correctly avoided it, while the reward sits on its shoulder. The problem had to be reframed from 'maximise a surface' to 'locate a sign change', after which progress was immediate - roughly eleven orders of magnitude over four rounds.

**3. How did you balance exploration and exploitation?**
Exploration was settled empirically rather than scheduled. One trial was spent on a maximin space-filling probe; it returned exactly zero, which proved the function underflows to nothing away from the source and made further exploration provably worthless. Every remaining trial went to exploitation inside the lobe.

**4. Did your strategy change over the weeks? Why?**
Substantially. Rounds 1-3 used standard EI on a Matern GP and made no progress. Round 6 introduced the sign bracket. Round 8 cut the bracket step after bisection converged on the zero crossing itself rather than the lobe peak. Rounds 12-13 replaced the bracket with explicit parabola-vertex probes once three readings straddled the peak.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No rescaling of inputs - all coordinates already lie in [0,1]. The **output** was transformed to log10|y|, which was essential: no stationary model can describe a range of a hundred orders of magnitude on a linear scale. The transform is floored at 1e-300 before taking the logarithm, because the exact-zero reading produced a negative infinity and crashed the fit until the floor was added. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Quadratic trend plus a Gaussian process on the residual, fitted to log10|y|.**

Final scores: **Q2 = 0.915 (quadratic, in use) - Matern 0.595, additive 0.136**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [0.051, 0.069]

**3. What preprocessing did the surrogate require?**
Matern 5/2 with a lengthscale per input was the starting kernel; the lengthscale ceiling was lowered from 10.0 to 0.5 for this function because the active structure lives on a scale of about 0.001. A signed-log transform was tested and rejected: it is monotone in y, but the sign change is a discontinuity the model cannot smooth across and the cross-validation score fell to about -0.29.

**4. Did you handle outliers or unusual data points?**
One reading is exactly 0, returned by the space-filling probe. It is almost certainly an underflow rather than a true zero. It was **kept** - it is a real reading and it answered a real question - but it broke the log transform until that was floored.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
The decisive moment was noticing that the largest number in the data set had the wrong sign. Until then I had been treating the problem as a search for a peak in a flat landscape; afterwards it was a search for the edge of a known feature, which is a far easier problem.

**2. Did you encounter local optima? How did you detect them?**
Not local optima in the usual sense. The trap here is the trough: a model fitted to the raw output treats it as the worst place in the square, when the reward sits immediately beside it. It was detected by sorting the readings by magnitude rather than by value.

**3. Which queried inputs were most informative, and why?**
The space-filling probe that returned exactly zero, because a negative result that is this unambiguous closes a question permanently. And the pair of readings straddling the sign change, which located the lobe to within a thousandth.

**4. If you restarted, what would you do differently?**
Sort the readings by magnitude, not by value, in the very first round. That one habit would have revealed the structure nine rounds earlier. I would also vary the second input at least once on the lobe - every reading on it inherited the same value from the point that found it, so that axis was never tested.

---

## Performance and results

**1. What is the best output value you achieved?**
**1.05167e-04**, against **7.71e-16** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.582509, 0.681526]`

**3. How confident are you that this is near the global maximum?**
Reasonably confident this is the maximum **of this lobe**: three readings straddle it and the parabola through them puts the vertex within about one ten-thousandth of the incumbent. Much less confident it is the global maximum, for one specific reason - the second input was never varied anywhere on the lobe, so I have optimised along a single slice through a two-dimensional feature.

**4. Did your results align with expectations for this function?**
Yes. The description says only proximity yields a non-zero reading, and that is exactly what the data shows: a vast dead zone and one small active region. What the description did not prepare me for was that the strongest signal would be the wrong sign.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Source localisation from sparse sensor readings - radiation surveys, gas-leak detection, pollution tracing. The defining feature is a signal that is undetectable until you are nearly on top of it, which makes uninformed search almost useless.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Anyone analysing this function should check the **sign** of the readings before the magnitude, and should expect any model fitted on a linear scale to be dominated entirely by a handful of points.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
