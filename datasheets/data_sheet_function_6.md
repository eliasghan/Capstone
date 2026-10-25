# Datasheet - Function 6: Cake recipe - five ingredients

*BBO capstone project. Completed from the Module 25 datasheet template.
Record is final at 12 bought trials (12 on this function); the thirteenth round was never scored.*

---

## Function overview

**1. Which function does this datasheet describe?**
Function 6 - Cake recipe - five ingredients.

**2. What real-world scenario does this function simulate?**
Optimising a cake recipe with five ingredient quantities - for example flour, sugar, eggs, butter and milk. Each recipe is scored on flavour, consistency, calories, waste and cost, with every factor contributing negative points. The total is negative by design and the goal is to bring it as close to zero as possible.

**3. What is the dimensionality of the input?**
5-D.

**4. How many initial data points were provided?**
20, supplied as `initial_inputs.npy` with shape (20, 5) and `initial_outputs.npy` with shape (20,).

**5. What does the output represent?**
Combined penalty score, negative by construction. Closer to zero is better.

---

## Nature of the data

**1. Describe the structure of the initial dataset.**
Inputs (20, 5), outputs (20,), both `float64`, every coordinate inside the unit interval. These files are immutable and are duplicated unmodified under `initial_data/` so the record can always be rebuilt.

**2. How does the dataset evolve as you add new queries weekly?**
One point per week, appended to `function_6/new_trials.csv` and never edited in place, for a final total of 12 bought trials and 32 observations. The sampling pattern changes character over the sequence: the supplied design is space-filling, the early trials spread out to answer structural questions, and the later trials cluster tightly around the best point found. By the end the design is dense in one small neighbourhood and sparse everywhere else - the correct allocation for finding a maximum, and a biased sample for anything else.

**3. Does the function include noise or randomness?**
Not directly measured on this function; a peer reported a standard deviation of roughly 0.02-0.03, which is comparable to the size of my final improvements and is a caveat on them.

**4. Does the function appear unimodal, multimodal, noisy, or smooth?**
Smooth, with a single well-defined basin and strong additive structure. The additive kernel - which forbids interactions between ingredients - more than doubled the predictive score over the Matern kernel, which is a meaningful finding about the function and not just a modelling convenience: it says the ingredients largely act independently over the range sampled.

---

## Optimisation strategy

**1. Which optimisation method(s) did you use?**
Bayesian optimisation with an additive Gaussian process, with the model restricted to ranking small local steps rather than choosing locations.

**2. Why did you choose this method for this particular function?**
The additive assumption is the most informative thing the data supports: five dimensions and thirty-two observations cannot afford a full interaction model, and the score says interactions are not needed. Restricting the model to ranking reflects a score good enough to order candidates but a search operating in a region the score is not really about.

**3. How did you balance exploration and exploitation?**
Exploratory for the first several rounds across all five inputs; exploitative thereafter. In the final rounds the model's preferred direction was overruled by direct measurement - holding everything else fixed, one input improved as it *rose* while the surrogate wanted it lowered, and two independent slices of the data agreed with the readings rather than the model.

**4. Did your strategy change over the weeks? Why?**
Yes. The step size had to be cut to about an eighth of its original value before the largest available move actually shrank - the step was saturating against an internal cap and the model kept selecting the same large jump, which was also its one badly mispredicted trial. That is a lesson in verifying that a configuration change moves the *output*, not just the setting.

---

## Data handling and preprocessing

**1. Did you rescale or normalise inputs?**
No input rescaling, no output transform. Outputs are standardised internally before the Gaussian process is fitted, which is standard practice and keeps the kernel's scale parameters from having to absorb the output's units.

**2. Did you train any surrogate models?**
Yes. Three families competed every round and were scored by leave-one-out cross-validation: a Matern 5/2 Gaussian process with a lengthscale per input, an additive Gaussian process that forbids interactions, and a quadratic trend with a Gaussian process on the residual. The family in use at the end of this function was: **Additive Gaussian process (a sum of one-dimensional kernels).**

Final scores: **Q2 = 0.901 (additive, in use) - quadratic 0.894, Matern 0.722**. A challenger replaced the incumbent only on a clear margin of about 0.1, since below that the difference is cross-validation noise at these sample sizes.

Fitted lengthscales: not reported for the additive kernel; the Matern fit gives roughly [2.4, 0.67, 0.54, 1.34, 0.71]

**3. What preprocessing did the surrogate require?**
Standard; the model family choice is the substantive decision here.

**4. Did you handle outliers or unusual data points?**
None removed.

---

## Weekly iteration and learning

**1. How did new data points change your understanding of the function landscape?**
The landscape turned out to be a tight basin: points a few hundredths away from the best return noticeably worse scores. That made step size the critical parameter and the surrogate's lengthscales an unreliable guide to it.

**2. Did you encounter local optima? How did you detect them?**
One basin found and refined. A peer reported a value roughly three times better, which suggests either a different basin or a better position within this one; without their coordinates I could not distinguish the two.

**3. Which queried inputs were most informative, and why?**
The one-at-a-time slices holding the other four inputs fixed. They are the only readings that produced an unambiguous direction, and they are what justified overruling the model.

**4. If you restarted, what would you do differently?**
Vary the fifth input. It sat on the lower boundary in **all twelve** trials and was never tested at the incumbent - the same blind spot as Function 4, on a function where I finished well behind the best reported result. I would also combine axis moves only when there is a round left to diagnose a failure; the one combined move I made came back slightly worse and could not say which axis caused it.

---

## Performance and results

**1. What is the best output value you achieved?**
**-0.2497464**, against **-0.714265** in the supplied starting design.

**2. Which input vector produced this value?**
`[0.422422, 0.453026, 0.694051, 0.794604, 0.000001]`

**3. How confident are you that this is near the global maximum?**
Low to moderate. The improvement over the starting design is large, but a peer reached roughly -0.088 against my -0.250, and a second reached -0.111. I am fairly confident I am inside the right basin and fairly confident I am not at the bottom of it.

**4. Did your results align with expectations for this function?**
Yes. A sum of independently-contributing penalty terms is exactly the structure that makes an additive model win, and that is what the cross-validation found without being told.

---

## Ethical, practical and general considerations

**1. How does this task relate to real-world applications?**
Formulation and recipe optimisation, where several ingredients trade off against a composite quality score. The additive finding is practically useful: if ingredients act independently, each can be tuned with far fewer experiments than a full factorial design would require.

**2. What limitations arise from the synthetic nature of the function?**
The oracle is noiseless in its bookkeeping, always available, and costs nothing but time. A real instrument has drift, failed runs, and a cost that varies with where you sample. The domain is also a clean unit box; real feasible regions have constraints that rule out whole areas, and a method that drives coordinates onto a boundary - as happened on several functions here - would need those constraints modelled explicitly. Finally, the problem hands you a well-posed scalar objective. In practice choosing that objective is often the harder half of the work.

**3. Would your strategy scale to more serious or more expensive problems?**
The decision procedure scales well, because its cost is negligible against the cost of an evaluation and it is explicitly designed for a budget measured in tens. What does not scale is dimensionality: at eight inputs the models are already straining, and beyond a few dozen the uncertainty estimates would have no basis. For a higher-stakes problem I would keep the tiering of model authority and the calibration log, and add a formal screening design before any refinement.

**4. What risks or pitfalls should a future user be aware of?**
Check that a change to the step size actually changes the proposal. On this function the step saturated against an internal cap, so several rounds of nominal tightening changed nothing at all.

A general caution that applies to every function in this project: a high cross-validation score certifies **interpolation** among points the model already holds, not **extrapolation** to the point you are about to buy - and every query is an extrapolation. Track predicted against realised values separately; it is the only diagnostic that tests the thing you are relying on.

---

*See [`../model_card.md`](../model_card.md) for the optimisation approach, [`../WEEKLY_LOG.md`](../WEEKLY_LOG.md) for the dated record of every decision including the mistakes, and [`../STATUS.md`](../STATUS.md) for the final per-function configuration.*
