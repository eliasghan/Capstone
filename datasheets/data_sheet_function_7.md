# Datasheet - Function 7: ML model with six hyperparameters

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 7 - ML model with six hyperparameters.

**2. What real-world scenario does this function simulate?**
Tuning a machine-learning model through six hyperparameters - for example learning rate, regularisation strength or number of hidden layers. The output is the model's performance score, such as accuracy or F1.

**3. What is the dimensionality of the input?**
6-D.

**4. How many initial data points were provided?**
30, supplied as `initial_inputs.npy` with shape (30, 6) and `initial_outputs.npy` with shape (30,).

**5. What does the output represent?**
Model performance score. Higher is better.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (30, 6), outputs (30,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_7/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 42 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
No replicate taken. The smoothness of the local readings and the model's high predictive score both suggest low noise.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
Smooth and well-behaved, and the best-modelled function of the eight by the end: a cross-validated score of 0.944 on the final data. It has a clear interior optimum with one input sitting on the lower boundary. The response along several inputs is single-peaked and well resolved.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation with a Matern 5/2 Gaussian process and an Upper Confidence Bound acquisition, inside a trust region around the best point.

**2. Why did you choose this method for this particular function?**
This is the one function where the orthodox method worked more or less as the textbook describes, and it was given the most freedom as a result. The trust region reflects a simple budget calculation: six dimensions cannot be searched globally on twelve trials, so the acquisition is given freedom inside a box rather than across the cube.

**3. How did you balance exploration and exploitation?**
Explicitly tiered. The model was demoted to ranking-only when its score was weak, and promoted back to full acquisition control in round 6 when the score jumped from 0.29 to 0.73. The exploration weight was cut to zero in round 10 for the endgame, and the trust region narrowed from 0.20 to 0.03 for the final rounds.

**4. Did your strategy change over the weeks? Why?**
Yes, and in both directions, which is the point of scoring the model every week rather than deciding once. The most consequential change was lowering the **lengthscale ceiling** from 10.0 to 0.8 in round 9, after the third input was written off as irrelevant for the second time on this function - while readings at 0.25, 0.45 and 0.65 showed a clear peak. With the tighter ceiling nothing saturated, every lengthscale was fitted rather than pinned, and the score rose.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling, no output transform. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Matern 5/2 Gaussian process with a lengthscale per input.**

Final scores: **Q2 = 0.944 (Matern, in use) - additive 0.807, quadratic 0.735**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [0.800, 0.603, 0.722, 0.355, 0.272, 0.415] - the first still at the ceiling, which should be lowered again if more trials were available

**3. What preprocessing did the surrogate require?**
Lengthscale bounds restricted to (0.01, 0.8). This is the single most important preprocessing decision on this function: a ceiling that is too high lets lengthscales saturate, and a saturated lengthscale reads as 'this input does not matter' when it actually means 'I cannot tell weak influence from none at the ceiling you gave me'.

**4. Did you handle outliers or unusual data points?**
None removed.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
Each round sharpened a well-behaved picture, which is what Bayesian optimisation is supposed to feel like. The two false 'irrelevant input' verdicts are the exception and were the most expensive mistakes on this function - one of them drove a coordinate toward zero over two rounds while the output fell each time.

**2. Did you encounter local optima? How did you detect them?**
One region, progressively refined. Releasing the trust region was never necessary here because the local improvements kept coming.

**3. Which queried inputs were most informative, and why?**
The readings that contradicted the irrelevance verdict - three values along the third input showing an unambiguous peak. They cost nothing extra and corrected a structural misunderstanding.

**4. If you restarted, what would you do differently?**
Set lengthscale ceilings by checking for saturation from the first fit onward, rather than discovering the problem twice. Beyond that I would change little; this is the function where the method worked as designed.

---

## Performance and results

**1. What is the best output value you achieved?**
**2.748654**, against **1.364968** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.000001, 0.154956, 0.492485, 0.255685, 0.345436, 0.698119]`

**3. How confident are you that this is near the global maximum?**
Moderate to good for a six-dimensional problem on twelve trials. The model predicts well, has under-predicted its own last two proposals (it is conservative rather than optimistic), and the result is ahead of every peer figure I have seen. But twelve points cannot characterise a six-dimensional space, and the search has been local throughout.

**4. Did your results align with expectations for this function?**
Yes. A smooth, single-peaked performance surface is what hyperparameter tuning usually looks like, and it is what the data showed.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
This *is* a real-world task - hyperparameter tuning is the canonical application of Bayesian optimisation, and it behaved the way the literature says it should.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Watch the lengthscale ceiling. This function produced a false 'irrelevant input' verdict twice, and both times the fix was to lower the bound rather than to believe the verdict.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
