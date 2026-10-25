# Datasheet - Function 4: Warehouse placement surrogate - four hyperparameters

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (11 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 4 - Warehouse placement surrogate - four hyperparameters.

**2. What real-world scenario does this function simulate?**
An ML model that approximates an expensive warehouse product-placement calculation. It has four hyperparameters, and the output reflects the difference from the expensive baseline. The description warns the system is dynamic and full of local optima.

**3. What is the dimensionality of the input?**
4-D.

**4. How many initial data points were provided?**
30, supplied as `initial_inputs.npy` with shape (30, 4) and `initial_outputs.npy` with shape (30,).

**5. What does the output represent?**
Difference from the expensive baseline calculation. Higher is better; large negative values indicate a badly mis-specified configuration.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (30, 4), outputs (30,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_4/new_trials.csv` and never edited in place, for a final total of 11 bought trials and 41 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
No replicate was taken, so noise is not directly measured. Indirect evidence suggests it is small: a three-point slice through the peak in one input is almost perfectly symmetric, which noise of any size would disturb.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
**A narrow spike sitting on a smooth background, and the most instructive function in the project.** Near the optimum the surface moves roughly eighteen units per unit of distance, while the fitted lengthscales report values near 1.3 - an underestimate of local curvature by more than tenfold. Tightening the kernel makes the cross-validated score *worse*, falling from 0.98 to about 0.85, because the smooth background is real too. One lengthscale cannot describe both, and that is the whole difficulty. Outside the spike the surface falls away catastrophically: a move of 0.024 in one coordinate once cost 0.43.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation initially, with a trust region; from round 8 onward the model was **taken off location-choosing entirely** and allowed only to rank small bounded steps. The final rounds used parabola-vertex probes.

**2. Why did you choose this method for this particular function?**
This function scores 0.980 on cross-validation and is still the worst-behaved of the eight. That score is earned on the thirty spread-out initial points and says nothing about the peak, which is exactly where every decision is made. Demoting a model that scores 0.98 feels wrong and was correct. An exploration probe in round 7 released the trust region entirely; with the whole box available the acquisition returned to the same neighbourhood, which answered the question of whether a better basin was known.

**3. How did you balance exploration and exploitation?**
Six consecutive attempts failed to beat the very first trial, which is as clear a signal as exists that the exploitation step size was wrong rather than the location. One trial was spent on an explicit exploration probe. Everything else was bounded local refinement.

**4. Did your strategy change over the weeks? Why?**
Yes, and the key change was about **scale rather than strategy**. In round 8 the step size was set from measured local differences (0.012 gained, 0.024 lost) instead of from the fitted lengthscales, and the seventh attempt finally beat the round-1 record. In round 12 the same error recurred one order of magnitude further down: the peak bracket in the second input is 0.0015 wide against a step floor of 0.005, so every automatic proposal had to overshoot. The floor was cut tenfold.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling, no output transform. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Matern 5/2 Gaussian process with a lengthscale per input.**

Final scores: **Q2 = 0.980 (Matern, in use) - additive 0.969, quadratic 0.955**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [1.353, 0.923, 0.945, 1.116] - all roughly an order of magnitude larger than the local structure warrants

**3. What preprocessing did the surrogate require?**
Standard. The instructive negative result is that **tightening the kernel does not help** - it was tested and the score fell - so the mismatch cannot be fixed by hyperparameter choice. It has to be handled by restricting what the model is allowed to decide.

**4. Did you handle outliers or unusual data points?**
A reading of -2.29 and one of -32.6 are both retained. They are not errors; they are what this function does a short distance outside its spike, and they are the clearest evidence of how narrow it is.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
Each round narrowed the spike. By the end, two of the four inputs were bracketed on both sides by readings within a few thousandths - and the other two had never been varied in isolation at all, which is the gap described below.

**2. Did you encounter local optima? How did you detect them?**
Yes, and detected the hard way: six attempts in a row that failed to beat an early reading. The round-7 trust-region release established that the model knows of no better basin, which is weaker than establishing that none exists.

**3. Which queried inputs were most informative, and why?**
The three-point slices through each coordinate. Once three readings straddle a peak, a parabola locates it far more accurately than the Gaussian process does, which on this function is a general truth rather than a quirk.

**4. If you restarted, what would you do differently?**
Vary every input once at the incumbent, early. A peer reported a substantially better value by probing the **fourth** input, which in my entire record had taken only four values inside the basin, all within a span of 0.010. I spent rounds refining two coordinates while a third of the remaining value sat on one I had never moved. This is my clearest single regret in the whole project.

---

## Performance and results

**1. What is the best output value you achieved?**
**0.6027542**, against **-4.0255** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.407583, 0.416930, 0.360748, 0.432592]`

**3. How confident are you that this is near the global maximum?**
Confident it is near a local maximum; not confident it is the best one. A peer reached roughly 0.709 on the same function, and the difference is plausibly explained by the untested fourth input. This function also has one fewer trial than the others, because its round-3 submission was misrouted to Function 5 - an error of mine, recorded rather than hidden.

**4. Did your results align with expectations for this function?**
Yes. The description warns of many local optima and a dynamic surface, and a narrow spike on a smooth background is a fair description of what that produces.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Tuning a cheap surrogate against an expensive ground-truth calculation - common in operations research, simulation and engineering design. The failure mode here is extremely common in practice: a model that validates well globally and is unusable locally.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Never size a step from a fitted lengthscale on this function. And treat its cross-validation score as a statement about the thirty initial points, not about the region you are standing in.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
