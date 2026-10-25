# Datasheet - Function 5: Chemical process yield - four variables

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 5 - Chemical process yield - four variables.

**2. What real-world scenario does this function simulate?**
The yield of a chemical process in a factory, controlled by four variables. The description states the function is typically unimodal, with a single peak where yield is maximised.

**3. What is the dimensionality of the input?**
4-D.

**4. How many initial data points were provided?**
20, supplied as `initial_inputs.npy` with shape (20, 4) and `initial_outputs.npy` with shape (20,).

**5. What does the output represent?**
Process yield. Observed values span four orders of magnitude.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (20, 4), outputs (20,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_5/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 32 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
Deterministic, as far as the data show. The readings along the final ridge lie on a smooth, monotone curve with no scatter.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
**Unimodal, as advertised - but the peak is at a corner of the domain, not inside it.** The output spans from about 0.11 to 8662, four orders of magnitude, which is why the model is fitted on a log scale. On that scale a peak of this shape is close to an exact quadratic, which is why a polynomial trend beats the Gaussian process here. Three of the four inputs settled on the upper boundary early, leaving a one-dimensional search along the fourth.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation with a quadratic trend plus Gaussian-process residual, fitted to log y - and then, decisively, **manual override of the model** on the basis of direct readings.

**2. Why did you choose this method for this particular function?**
The transform is the whole reason anything worked: no stationary model can describe four orders of magnitude on a linear scale. The polynomial trend captures the global curvature and the GP residual supplies the uncertainty a bare polynomial cannot. The override was necessary because the model, being a quadratic on a log scale, is *structurally obliged* to predict a fall beyond its own vertex - so its prediction at the far corner was a property of the model family, not evidence about the function.

**3. How did you balance exploration and exploitation?**
Exploratory early across all four inputs, then almost pure exploitation along the single free axis. The final rounds were exploitative in intent and aggressive in step size, which is unusual and was justified by the measured gradient.

**4. Did your strategy change over the weeks? Why?**
Yes - this function produced the two most consequential decisions of the project. In round 11 the model predicted a peak *below* the incumbent and mispredicted its own measured point by 126, while three direct readings rose monotonically. I overrode the model with an explicit probe past the highest reading, and it set a new best. In round 12 I did it again and went all the way to the corner. Five readings along that axis ran 4451.7, 4478.9, 4554.8, 4643.2, 4998.3, with a log-slope that doubled every 0.097 of travel. The corner returned 8662.41.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling. The output is fitted on **log y**, which is essential. A guardrail on implausible predictions had to be raised twice as the best value grew - set against an old scale it silently discarded every candidate the model rated above the incumbent, which is a failure mode worth knowing about. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Quadratic trend plus Gaussian process on the residual, fitted to log y.**

Final scores: **Q2 = 0.803 (quadratic, in use) - additive 0.685, Matern 0.662**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [0.438, 0.296, 0.010, 0.010] on the residual - the last two pinned at the floor, consistent with those inputs being fixed at the boundary

**3. What preprocessing did the surrogate require?**
Standard kernel settings on the residual; the heavy lifting is done by the transform and the polynomial trend.

**4. Did you handle outliers or unusual data points?**
None removed. The low-yield readings are genuine and define the shape of the ridge.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
The data told a consistent story that the model kept contradicting: every step toward the corner improved the yield, and the rate of improvement was accelerating. Learning to read that directly off the readings, rather than through the surrogate, is what produced the project's largest result.

**2. Did you encounter local optima? How did you detect them?**
None found - consistent with the description. The surface rises monotonically toward one corner from everywhere that was sampled.

**3. Which queried inputs were most informative, and why?**
The two boundary probes. Each was a deliberate decision to disbelieve a model that scored above 0.8, and both set records.

**4. If you restarted, what would you do differently?**
Transform the output in round one. On a linear scale this function tells you nothing at all, and I lost several rounds to that. I would also test boundary points much earlier: three of four inputs ended on the boundary, and the sooner that is known the sooner the search collapses to one dimension.

---

## Performance and results

**1. What is the best output value you achieved?**
**8662.405**, against **1088.86** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.999999, 0.999999, 0.999999, 0.999999]`

**3. How confident are you that this is near the global maximum?**
High, unusually so. The maximum is a **vertex of the feasible box**, so there is nowhere further to go, and a peer independently reported essentially the same value at the same corner. The only residual doubt is whether the true unconstrained peak lies outside the allowed domain, which the competition does not permit us to find out.

**4. Did your results align with expectations for this function?**
Unimodal, yes. A single interior peak, no - and that mismatch cost me rounds, because I was looking for an interior optimum while the readings were pointing at a boundary.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Process optimisation in manufacturing, where yields vary over orders of magnitude and optimal settings routinely sit against an operating constraint rather than in the middle of the feasible range.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
A quadratic-on-log model cannot extrapolate past its own vertex without predicting a fall. Do not read its prediction at the domain boundary as evidence; read the measured gradient instead.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
