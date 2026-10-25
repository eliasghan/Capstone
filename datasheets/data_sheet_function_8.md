# Datasheet - Function 8: High-dimensional model tuning - eight parameters

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 8 - High-dimensional model tuning - eight parameters.

**2. What real-world scenario does this function simulate?**
An eight-dimensional black box in which every input affects the output and the internals are unknown - framed as tuning a model with eight hyperparameters and reading back a validation score. The description suggests that finding strong local maxima is the practical goal rather than the global optimum.

**3. What is the dimensionality of the input?**
8-D.

**4. How many initial data points were provided?**
40, supplied as `initial_inputs.npy` with shape (40, 8) and `initial_outputs.npy` with shape (40,).

**5. What does the output represent?**
A performance score. Note that the description suggests a validation accuracy between 0 and 1, whereas observed values sit around 9.6 to 10.0 - so the output is on a different scale from the illustrative framing.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (40, 8), outputs (40,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_8/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 52 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
Not directly measured. The last four readings sit within 0.016 of each other, which is consistent with either very low noise or a genuinely flat optimum.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
Smooth, extremely well-fitted, and **flat near the optimum**. All three surrogate families score above 0.99 on cross-validation. That is also the warning: this is the best-modelled function of the eight and it was *not* the best behaved.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation with a Matern 5/2 Gaussian process and Upper Confidence Bound inside a narrow trust region.

**2. Why did you choose this method for this particular function?**
Forty initial points in eight dimensions is the most data of any function here and the model earned its authority. The trust region is essential at this dimensionality: a global search on twelve trials in eight dimensions is not a search at all.

**3. How did you balance exploration and exploitation?**
A deliberate exploration probe was run by widening the trust region for one round; it proposed a point 0.46 away and returned below the incumbent, which answered the question and the region was narrowed again. Everything else was exploitation, and from round 8 the exploration weight was zero.

**4. Did your strategy change over the weeks? Why?**
Yes, because of a calibration failure that is the most important single finding of the project. This model **over-predicted its own proposal on seven consecutive rounds**, by about 0.09 on average - a systematic bias, not noise - while scoring 0.99 on cross-validation. Halving the exploration weight did not fix it, because the bias was in the model rather than in the acquisition. Setting the weight to zero did, and the model has under-predicted since.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling, no output transform. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Matern 5/2 Gaussian process with a lengthscale per input.**

Final scores: **Q2 = 0.996 (Matern, in use) - additive 1.000, quadratic 0.999**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [3.946, 5.644, 3.101, 7.301, 8.865, 5.640, 3.975, 10.0] - long throughout, and the last pinned at the ceiling

**3. What preprocessing did the surrogate require?**
Standard. The substantive intervention was to the acquisition, not the kernel.

**4. Did you handle outliers or unusual data points?**
None removed.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
The landscape is a broad plateau rather than a peak. By the end the proposals predicted the incumbent's own value and were unchanged at every trust-region radius tested from 0.15 down to 0.03 - which is what a converged search looks like.

**2. Did you encounter local optima? How did you detect them?**
The description recommends settling for a strong local maximum, and that is what happened. The widened-trust-region probe is the only direct evidence about alternatives, and it came back negative.

**3. Which queried inputs were most informative, and why?**
The basin probe, and the run of over-predictions - the latter not because any single reading mattered, but because the *pattern* across seven of them exposed a bias no score could see.

**4. If you restarted, what would you do differently?**
Keep a calibration log from round one: predicted against realised for every submitted point. It is nearly free, and it is the only diagnostic that would have caught this bias at round two instead of round eight. It is the single change I would make earliest across the whole project.

---

## Performance and results

**1. What is the best output value you achieved?**
**9.974458**, against **9.598482** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.108546, 0.163472, 0.141025, 0.000001, 0.863819, 0.487005, 0.208507, 0.599440]`

**3. How confident are you that this is near the global maximum?**
Confident it is a strong local maximum and not confident it is global - which is exactly what the problem description recommends settling for. Twelve trials in eight dimensions cannot cover the space; what gives some comfort is that the deliberate probe for a better basin came back negative.

**4. Did your results align with expectations for this function?**
Yes on structure and difficulty. Not on scale - the description's illustrative range of 0 to 1 does not match the observed values, which is worth flagging to anyone comparing results.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
High-dimensional hyperparameter tuning, where exhaustive search is impossible and a good local optimum found cheaply is the realistic goal.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
**A near-perfect cross-validation score is not evidence that a model is right where you are about to use it.** This function is the proof: it scored 0.99 while being wrong in the same direction seven times running, because cross-validation tests interpolation among points the model already has, not extrapolation to the point about to be bought.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
