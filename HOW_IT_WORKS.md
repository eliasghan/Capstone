# How this project works

A plain-language guide to what is in this folder, what the code does, and what you
do each week. No prior knowledge assumed.

---

## 1. The problem

There are eight unknown functions. You cannot see their formulas. The only thing you
can do is submit an input — a list of numbers, each between 0 and 1 — and about a
week later you get back a single number, the output. Every function is to be
**maximised**, and you get **ten submissions per function** in total.

That is the whole game, and the difficulty is not mathematical, it is economic. Ten
measurements is almost nothing. There is no trial and error, no restarting, no
gradient to follow downhill. Each submission has to be chosen carefully, because it
costs a week and you never get it back.

The strategy for spending them is called **Bayesian optimisation**, and it has two
moving parts. First you build a **surrogate**: a statistical model, fitted to
everything measured so far, that guesses what the function does everywhere else.
Second you use that surrogate to **choose where to measure next**. Everything in
this folder is one of those two things, or a record of them.

---

## 2. What is in the folder

| Path | What it is |
|------|-----------|
| `function_1/` … `function_8/` | One folder per function. Each holds that function's data and its own optimiser notebook. This is where you work. |
| `bbo_toolkit.py` | The shared engine. Every notebook imports it. You do not normally edit this. |
| `WEEK4_POINTS.md` | The current round's eight points, with the reasoning for each. Replaced each week. |
| `WEEKLY_LOG.md` | The running record: what was submitted, what came back, what changed and why. This is the defensible history of the project. |
| `WEEK4_PLAN.md` | How the current round's points are being chosen. |
| `GP_surrogate_per_dimension.ipynb` / `.html` | Pictures of what the surrogate believes, one panel per input. Open the `.html` to look without running anything. |
| `surrogate_shootout.py` / `.csv` | The experiment that compared eight candidate models and decided which to use per function. |
| `README.md` | The public-facing project description for GitHub. |
| `initial_data/` | Pristine copies of the original data. Never edited — a safety net if a working copy is damaged. |
| `reference/` | The original assignment descriptions and the early strategy notes. |
| `archive/` | Superseded working files, kept for the record. |
| `_to_delete/` | Junk to remove. Safe to delete this folder entirely. |

Inside each `function_i/` folder there are four files. `initial_inputs.npy` and
`initial_outputs.npy` are the starting data you were given, and are never modified.
`new_trials.csv` is the append-only log of every point you have submitted and what
it returned. `F{i}_optimizer.ipynb` is the notebook that reads those three and
recommends the next point.

---

## 3. What you do each week

1. Open `function_1/F1_optimizer.ipynb`. Run every cell from the top (**Kernel →
   Restart & Run All** is the reliable way).
2. Read the line that says `>>> NEXT POINT TO SUBMIT`. Copy those numbers.
3. Repeat for functions 2 through 8.
4. Submit all eight — **checking carefully that each point goes to the function it
   was computed for.** F4 and F5 both take four numbers, and they were swapped once,
   which cost F5 a round and left F4 a week behind.
5. A week later the outputs arrive. In each notebook, scroll to the **ADD A REALISED
   TRIAL** cell, paste the returned number into `NEW_Y`, and run that cell. It
   appends the result to `new_trials.csv` and prints the next recommendation
   immediately.
6. That is the loop. The data file grows by one row per function per week, and the
   model gets a little better informed each time.

Two habits worth keeping. Save the notebook (Ctrl+S) after you run it, so the
outputs are on disk and can be compared later. And set `NEW_Y = None` again after
the result has been recorded, otherwise re-running the notebook appends the same
trial twice.

---

## 4. What the code actually does

**Fit a surrogate.** The notebook loads every point measured so far and fits a model
to them. The default model is a **Gaussian process**. Two things make it the natural
choice here. It passes exactly through the points it has seen, and — the important
part — at every *unmeasured* location it reports not just a guess but an
**uncertainty**: a range it thinks the true value lies in. That uncertainty is the
whole reason a GP is used instead of ordinary regression. Ordinary regression tells
you what it expects; a GP also tells you how much it does not know, and on a
ten-measurement budget knowing where you are ignorant is worth more than knowing
where you are confident.

**Turn the surrogate into a decision.** An **acquisition function** collapses the
prediction and the uncertainty into a single score for every possible point, and the
next submission is wherever that score is highest. Two are available. **Expected
Improvement** asks "how much do I expect this point to beat my current best?", which
naturally favours places that are either promising or unexplored. **Upper Confidence
Bound** scores a point as its predicted value plus a multiple of its uncertainty,
which is a more direct way of saying "be optimistic in proportion to how little I
know." Each has one knob, `XI` for the first and `BETA` for the second, and turning
that knob up buys exploration at the cost of exploitation.

**Know when not to trust the model.** This is the part added most recently, and it
is the part that changed the strategy. Everything above assumes the surrogate can
predict *places it has never measured*. That assumption can be tested, and it is not
always true. See section 6.

---

## 5. The settings in the CONFIG cell

Every notebook has one cell near the top marked CONFIG. It is the only cell you
normally edit. The knobs, in plain terms:

| Setting | What it means |
|---------|---------------|
| `SURROGATE` | Which model to fit. `"matern"` is the standard Gaussian process. `"additive"` is a GP that forbids interactions between inputs — it assumes each input acts on its own. `"quadratic"` fits a curved trend and puts a GP on what the trend leaves over. |
| `TRANSFORM` | What the model is fitted to. `None` means the raw output. `"log"` and `"log10abs"` are for functions whose outputs span many orders of magnitude, where fitting the raw values does not work. |
| `PROPOSER` | How the point is chosen. `"acquisition"` is the classic optimisation described above. `"local"` scores a handful of small moves away from the current best. `"replicate"` deliberately re-measures near the best point instead of optimising. |
| `ACQUISITION`, `XI`, `BETA` | Which acquisition to use and how exploratory to make it. Larger `XI` or `BETA` means more exploration. |
| `TRUST_REGION`, `TR_RADIUS` | Restrict the search to a box of this half-width around the current best, instead of the whole space. Essential in high dimensions, where a global search over an unmapped space is hopeless. |
| `STEP_FRAC` | For the local proposer: how big each trial step is, as a fraction of what the model thinks that input's natural scale is. |
| `INERT_THRESHOLD` | If the model decides an input barely affects the output, do not waste a step on it. |
| `PLAUSIBLE_MAX` | A hard ceiling on a believable prediction. Candidates predicting above it are discarded as fantasy. |
| `LENGTHSCALE_BOUNDS` | How sharp or smooth the model is allowed to believe the function is. |
| `RANDOM_STATE` | Makes results repeatable. |

---

## 6. Q², and why the strategy changed

Bayesian optimisation only works if the surrogate can predict points it has not
seen. That sounds obvious, and it is testable.

Take one measured point. Remove it. Refit the model on all the others. Ask the
refitted model to predict the point you removed, and compare with what the function
actually returned. Put it back, take out a different one, repeat for every point.
Now score all those predictions:

**Q² = 1** means perfect prediction. **Q² = 0** means the model did no better than
ignoring the inputs entirely and guessing the average every time. **Q² below 0**
means it did worse than that — its predictions actively mislead.

Run the **CHECK** cell in any notebook to see this for that function.

This is not the same as "does the model fit the data." Every model here fits its own
data almost perfectly, with in-sample R² of about 1.00 across the board. Fitting
what you have already seen is easy; predicting what you have not is the hard part,
and only the second one matters when you are about to spend a week measuring
somewhere new.

The measured scores were: F8 0.99 and F4 0.97, which is excellent; F3 at −0.24,
which is worse than useless; and the other five between 0.19 and 0.36, which is
weak. That result is why the eight functions are no longer treated identically.
Where the model predicts well it keeps full control and the acquisition chooses the
point. Where it does not, it is demoted: instead of being asked "where in this whole
space is the optimum" — a question it answers confidently and badly — it is handed
about a dozen small moves away from the current best and asked only to **rank** them.
Every candidate then sits next to something genuinely measured, so a wrong ranking
costs a little rather than a lot. And F3, which cannot predict at all, spends its
round re-measuring near its best point to find out how noisy it is, because until
the noise is smaller than the differences being chased, no improvement there is even
detectable.

---

## 7. Reading the output

Running the RECOMMEND cell prints something like this:

```
=== FUNCTION 6 ===
observed points: 23  (initial 20 + new 3);  new-trial budget: 3/10
surrogate: additive   target: y   proposer: local
best so far: y=-0.6499 at x=[0.422422, 0.143514, 0.801323, 0.999999, 0.000001]
rule: local candidates ranked by EI
>>> NEXT POINT TO SUBMIT:
    [0.422422, 0.453026, 0.801323, 0.999999, 0.000001]
    predicted y: -0.5464 +/- 0.0928
    ABOVE the incumbent   |   distance to it: 0.310
```

The header confirms how much data and budget you have. The middle tells you which
model and which selection rule produced this point. Then the point itself, the
model's prediction with its uncertainty, and two sanity indicators: whether the
prediction beats your current best, and how far the proposal sits from it.

Those last two are the ones to look at. A proposal predicted **above** the incumbent
is a genuine attempt at a new best. One predicted **below** is a deliberate purchase
of information — refining curvature, or measuring noise — and that is legitimate,
but you should know which of the two you are buying. The distance tells you how
adventurous the point is: small means refinement, large means the model is
extrapolating, which is only justified when its Q² has earned it.

When the local proposer runs it also prints its ranked candidate list, so you can
see the alternatives it rejected and why. The choice is auditable rather than
opaque.

---

## 8. If something looks wrong

If a coordinate reads exactly 0 or 1, that is a bug — every point is supposed to be
clamped strictly inside, printed as `0.000001` or `0.999999`.

If a proposal predicts something wildly larger than anything ever observed, the
model is extrapolating past what it can support. That is what `PLAUSIBLE_MAX` exists
to catch, and it has already caught one case where a well-fitting quadratic proposed
a point at which it expected a value roughly a trillion times the largest ever seen.

If re-running the notebook produces a slightly different point than last time, that
is normal and harmless. Fitting the model involves an internal optimisation that can
settle in slightly different places on different machines. The differences are far
smaller than the model's own uncertainty. If it ever matters, submit the point
recorded in `WEEK4_POINTS.md`, since that is the one written into the log.

If the recommendation seems to ignore an input entirely, check the lengthscale
printed for it. A large value means the model believes that input does not affect
the output and has stopped varying it. Treat that verdict with suspicion when it is
based on few points — one input was declared irrelevant early, driven to zero over
two rounds, and the output fell every time before a refit revealed it was one of the
most influential.
