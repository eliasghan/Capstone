# Datasheet - Function 3: Drug discovery - adverse reactions from three compounds

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 3 - Drug discovery - adverse reactions from three compounds.

**2. What real-world scenario does this function simulate?**
A drug discovery project testing combinations of three compounds. Each input row is the amount of each compound; the output records adverse reactions. The underlying goal is to minimise side effects, framed here as maximising a negated output.

**3. What is the dimensionality of the input?**
3-D.

**4. How many initial data points were provided?**
15, supplied as `initial_inputs.npy` with shape (15, 3) and `initial_outputs.npy` with shape (15,).

**5. What does the output represent?**
Negated adverse-reaction count. All observed values are negative, so the task is to get as close to zero as possible.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (15, 3), outputs (15,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_3/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 27 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
Small but real. A deliberate replicate in round 7 implied a standard deviation of about 0.0014. That measurement mattered: the model had been fitting a noise term roughly sixty times larger, which meant real structure was being absorbed into noise. The noise bounds were pinned near the measured value for every subsequent round.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
**The hardest function of the eight to model, by a wide margin.** No surrogate family ever exceeded a cross-validated score of about 0.13, meaning the models are barely better than always guessing the mean. The data suggest a broad, shallow surface with a weak optimum near one boundary. Both free inputs are now bracketed on either side by readings and the top is flat - three successive moves all returned within 0.0005 of each other.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation, but with the model held under tight restriction. Because its score never justified letting it choose a location, it was only ever allowed to **rank** about a dozen small candidate steps constructed geometrically around the best point. The final rounds used explicit probes at the vertices of parabolas fitted through the bracketing readings.

**2. Why did you choose this method for this particular function?**
A model that cannot predict held-out points has not earned the right to choose where to spend a trial. Letting it rank small, bounded steps uses the little signal it has while capping the cost of a wrong ranking. Ranking also switched from Expected Improvement to the plain predicted mean, because EI had collapsed to near-zero everywhere and was discarding a candidate predicted *above* the incumbent purely for being too certain.

**3. How did you balance exploration and exploitation?**
Mostly exploitation, by necessity rather than choice - with a model this weak there is no reliable basis on which to explore. One trial was spent on a deliberate replicate, which was the single most valuable query on this function. The final trial went to a maximin space-filling point, on the reasoning that refinement was worth essentially nothing and only a different region could change the outcome.

**4. Did your strategy change over the weeks? Why?**
Yes, three times. Round 5 abandoned EI for the predicted mean. Round 7 pinned the noise bounds to the measured value. Round 8 cut the step size hard, after a refit briefly enlarged one step and sent a proposal outside the bracket the data had already drawn - where the model predicted a positive value, better than anything ever observed, on a score of 0.03.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling, no output transform. The output range is narrow enough that neither helps. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Matern 5/2 Gaussian process with a lengthscale per input.**

Final scores: **Q2 = 0.130 (Matern, in use) - additive 0.072, quadratic 0.059**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: [10.0, 0.265, 0.065] - the first lengthscale is pinned at its ceiling, which means the model cannot distinguish weak influence from none on that input, not that the input does nothing

**3. What preprocessing did the surrogate require?**
Noise bounds restricted to (1e-10, 1e-4) after the replicate. The inert-input threshold was tightened so that only the axis with the strongest evidence is stepped, on the grounds that a model scoring near zero has not earned the right to choose between dimensions.

**4. Did you handle outliers or unusual data points?**
None removed. With 27 observations and a model this weak, there is no defensible basis for deciding a reading is wrong.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
Mostly negative learning, which is still learning: each round narrowed where the optimum is *not*. The replicate was the exception - it changed the model's noise assumption by a factor of sixty and so changed every subsequent fit.

**2. Did you encounter local optima? How did you detect them?**
Possibly. A peer reported a value roughly five times better than mine without disclosing its location, which suggests a region I never sampled. My own data show nothing promising at low values of the first input, and another peer's best sits in my region and is worse than mine. I could not resolve it with the budget remaining.

**3. Which queried inputs were most informative, and why?**
The deliberate replicate, by a distance. One trial spent on measuring rather than optimising corrected a six-round modelling error.

**4. If you restarted, what would you do differently?**
Run a coarse screening design before any modelling. With a function this hard to fit, the surrogate was never going to earn its keep, and the budget would have been better spent on a structured sweep than on sequential refinement guided by a model scoring 0.13.

---

## Performance and results

**1. What is the best output value you achieved?**
**-0.0252350**, against **-0.0348353** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.999999, 0.580426, 0.859784]`

**3. How confident are you that this is near the global maximum?**
Low. This is the function I would least want to defend. The local optimum is well bracketed, but a peer reported a substantially better value elsewhere, the model has no predictive power, and large parts of the cube were never sampled. I would describe this as the best point found, not as an estimate of the maximum.

**4. Did your results align with expectations for this function?**
Partly. The description frames it as a minimisation of side effects, which is what the shallow, bounded surface looks like. It gives no hint that the function would be this resistant to modelling.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Compound screening and dose-combination studies, where each experiment is slow and expensive and the response surface is poorly behaved. The honest lesson is one that real screening programmes know well: sometimes the surrogate does not work, and the correct response is to design experiments rather than to trust it anyway.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Do not let a model with a near-zero cross-validation score select locations. Mine, left unrestricted for one round, proposed a point outside the measured bracket and predicted a value better than anything ever observed there.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
