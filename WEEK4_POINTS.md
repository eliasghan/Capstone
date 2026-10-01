# Round 4 — points to submit

**Check the routing first.** Last round the point computed for F4 was submitted to
F5 (both are 4-D, so nothing flagged it): F5 lost its round and F4 never got one.
Paste each row into the matching function and nothing else.

| Fn | Point to submit |
|----|-----------------|
| F1 | `0.516951, 0.681526` |
| F2 | `0.682637, 0.926564` |
| F3 | `0.949999, 0.548179, 0.859784` |
| F4 | `0.373537, 0.419038, 0.433148, 0.440012` |
| F5 | `0.224189, 0.846480, 0.879484, 0.999999` |
| F6 | `0.422422, 0.453026, 0.801323, 0.999999, 0.000001` |
| F7 | `0.000001, 0.184614, 0.448347, 0.289155, 0.373715, 0.749975` |
| F8 | `0.150001, 0.150001, 0.193946, 0.000001, 0.753935, 0.451055, 0.256022, 0.543085` |

These are exactly what the notebooks now print. Re-running the RECOMMEND cell
reproduces them.

## What produced each one

| Fn | Surrogate | Q² | How the point was chosen | Predicted | vs incumbent |
|----|-----------|-----|--------------------------|-----------|--------------|
| F1 | quadratic on log10\|y\| | **0.73** (was 0.14) | local steps, ranked by EI | log10\|y\| −2.27 | above |
| F2 | Matérn | 0.32 | local steps, ranked by EI | 0.583 | below |
| F3 | Matérn | **−0.24** | near-replicate of the incumbent | −0.026 | below |
| F4 | Matérn | **0.97** | UCB β=1.5, trust region r=0.20 | 0.515 | below |
| F5 | quadratic on log y | **0.65** (was 0.06) | local steps, ranked by EI | ≈2939 | **above** |
| F6 | additive | **0.77** (was 0.31) | local steps, ranked by EI | −0.546 | **above** |
| F7 | Matérn | 0.29 | local steps, ranked by EI | 2.299 | below |
| F8 | Matérn | **0.99** | UCB β=1.5, trust region r=0.15 | 9.978 | **above** |

Three proposals predict above their current best: **F5, F6 and F8**. Those are where
a new best is most likely this round. The rest are deliberately modest — refinements
and measurements, not gambles.

## What changed in the method

**Surrogate choice is now evidence-based, on three functions.** Leave-one-out Q²
was measured for eight candidate models on all eight functions. Where the gain was
large the model changed: a quadratic trend on the log scale for F1 and F5 (a
Gaussian-shaped peak is exactly a quadratic once you take logs), and an additive
kernel for F6 (it forbids interactions between inputs, which costs flexibility the
data cannot afford anyway). Everywhere else the Matérn GP stayed, because nothing
beat it by a margin worth acting on.

**How the point is chosen now depends on whether the model has earned it.** F4 and
F8 predict held-out points at Q² ≈ 0.97 and 0.99, so the acquisition keeps full
control there. The rest score between −0.24 and 0.77, which is not enough to trust a
location nobody has measured — so instead of asking the model "where in this space
is the optimum", it is handed about a dozen small moves from the current best and
asked only to rank them. Every candidate then sits next to something real, and a
wrong ranking costs a little rather than a lot.

**F3 spends this round on measurement, not optimisation.** Its Q² is negative — it
predicts worse than guessing the average — and its fitted noise exceeds the entire
spread of its observations. Until the noise is known to be smaller than the
differences being chased, no refinement there is detectable. The point is a
near-replicate of the incumbent, varying only the axes the model calls inert.

**Two guardrails were added after the proposals were first generated, because the
first run broke our own rules.** Inert dimensions are no longer stepped at all —
a huge lengthscale saturated the step size and shoved the coordinate onto the
boundary, which is exactly the mistake that cost trials in week 3. And a
plausibility ceiling now filters candidates: F1's quadratic, which interpolates its
data at Q² = 0.73, initially proposed a point where it predicted \|y\| ≈ 10¹², because
an indefinite quadratic has no maximum. Good interpolation does not license
extrapolation, and the filter enforces that.

## New in the notebooks

Each CONFIG cell has three new knobs — `SURROGATE`, `TRANSFORM` and `PROPOSER` —
plus the settings the local proposer needs. There is also a new **CHECK** cell that
re-runs the leave-one-out comparison for this function and prints Q² for each
candidate surrogate. Run it every few rounds: the winner changes as data
accumulates, and a challenger should only replace the incumbent on a clear margin
of about 0.1, since smaller differences are cross-validation noise.

## Budget

Seven trials remain on every function except **F4, which has eight**. Rounds 4 and 5
run this scheme; rounds 6 and 7 switch to pure exploitation — exploration margins to
zero, smallest trust regions. Any function still scoring near zero at that stage
spends its remaining trials confirming its best reading rather than hunting new
locations, because a noisy leaderboard is won by confirming a good value, not by
adding another uncertain one.
