# Datasheet - Function 2: Noisy log-likelihood of a mystery model

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 2 - Noisy log-likelihood of a mystery model.

**2. What real-world scenario does this function simulate?**
A black-box machine-learning model that takes two numbers and returns a log-likelihood score. The description warns that each output is noisy and that the surface has local optima.

**3. What is the dimensionality of the input?**
2-D.

**4. How many initial data points were provided?**
10, supplied as `initial_inputs.npy` with shape (10, 2) and `initial_outputs.npy` with shape (10,).

**5. What does the output represent?**
A log-likelihood score. Higher is better.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (10, 2), outputs (10,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_2/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 22 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
**Yes, substantially, and this is the defining feature of the function.** Eight readings inside a window 0.009 wide span 0.089, with a standard deviation of about 0.046. A peer independently reported three readings at a *single* point spanning 0.598 to 0.726. Since the competition score is the best value ever observed, this changes the optimal play completely: once the peak region is located, repeated drawing beats refinement, because each draw is an independent chance at a high reading.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
Effectively **one-dimensional and noisy**. A ridge runs across the first input; the second input is inert over almost its whole range. The ridge is flat between roughly 0.68 and 0.72 and collapses sharply above 0.74 - our own reading at 0.748 fell to a third of the ridge value, which independently reproduced a peer's description of the same geometry.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation with an additive Gaussian process and Expected Improvement, then - once the noise was measured - **deliberate near-replication**: the final trials drew repeatedly at the best location rather than trying to improve it.

**2. Why did you choose this method for this particular function?**
The additive kernel forbids interactions between the two inputs. That is a strong assumption, but with one input confirmed inert it is close to true, and it more than doubled the cross-validated score over the Matern kernel. The switch to repeated drawing follows directly from the scoring rule: against a standard deviation of 0.046 and a flat ridge, no amount of refinement beats another draw.

**3. How did you balance exploration and exploitation?**
Exploration was spent early on one decisive question - a single-variable test that moved the second input by 0.35 while holding the first fixed, and changed the output by 0.003. That closed the question permanently and freed every later candidate for the axis that matters. Later rounds were pure exploitation, implemented as repeated draws.

**4. Did your strategy change over the weeks? Why?**
Yes, twice. The step size was cut to about a fifth of its original value once the peak window was identified as about 0.01 wide, and the step floor was lowered below its hard-coded minimum to match. Then the strategy changed in kind rather than degree: from refining a location to drawing repeatedly at one. The draws were taken by moving the **inert** second input rather than jittering the first - to the function it is the same location, to the record a distinct point, and it avoids pretending a thousandth-scale move in the live axis is safe.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling. No output transform - the raw log-likelihood is already on a sensible scale. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Additive Gaussian process (a sum of one-dimensional kernels, no interaction terms).**

Final scores: **Q2 = 0.689 (additive, in use) - Matern 0.390, quadratic -0.569**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: not reported for the additive kernel (its structure differs from the ARD form); the Matern fit gives roughly [0.07, 10.0], the second lengthscale pinned at its ceiling

**3. What preprocessing did the surrogate require?**
Matern 5/2 with per-input lengthscales was the incumbent until round 6, when the additive kernel cleared the 0.1 margin we require before changing model family. A white-noise term is fitted; on this function it carries real weight rather than absorbing structure.

**4. Did you handle outliers or unusual data points?**
None removed, and deliberately so. On a function this noisy, a low reading is data about the noise distribution, not an error. Removing the low readings would have made the noise look smaller than it is and led straight back to refinement.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
The single-variable test converted an assumption into a fact and halved the effective dimensionality. The noise measurement did something subtler: it told me that the differences I had been chasing between nearby readings were not structure at all.

**2. Did you encounter local optima? How did you detect them?**
The description warns of local optima and I never found convincing evidence of more than one. What looked like local structure on the ridge turned out, when measured, to be noise.

**3. Which queried inputs were most informative, and why?**
The single-variable test on the second input, and the repeated draws near the peak. Neither improved the score at the time; both changed what every later trial did.

**4. If you restarted, what would you do differently?**
Measure the noise in round two, not round ten. Everything about the correct strategy here follows from the size of the noise, and two early trials would have established it. I spent several middle rounds making small, careful moves that the noise made meaningless.

---

## Performance and results

**1. What is the best output value you achieved?**
**0.689468**, against **0.611205** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.712637, 0.826564]`

**3. How confident are you that this is near the global maximum?**
Confident about the **location** - the ridge is well mapped and the collapse above 0.74 is measured. Not at all confident the recorded value is near the maximum of the underlying function, because the recorded value is a single draw from a distribution with a standard deviation of about 0.046. A different week's draw at the same point could easily be worse by a tenth.

**4. Did your results align with expectations for this function?**
Yes on noise, which the description warned about and the data confirmed emphatically. Not on local optima - the description implies several, and I found one ridge.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Tuning any model whose evaluation is itself stochastic: cross-validation with random splits, anything involving sampling, A/B tests with limited traffic. The lesson - that with a noisy objective and a best-of-N score, replication can beat refinement - is directly transferable and slightly counter-intuitive.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Do not interpret differences between nearby readings as structure before measuring the noise. On this function the noise is larger than almost every real local gradient, and a model fitted without that knowledge will chase it.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
