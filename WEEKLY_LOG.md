# BBO Capstone — Weekly Optimisation Log

A running record of each week's recommended points, realised outputs, findings, and any changes made to the per-function strategy. Newest week is added at the top of the log. Setup: 8 black-box functions, all **maximise** over [0, 1]^d, with a budget of 13 sequential trials per function (~1 week per evaluation). Optimiser configs live in each `function_i/F{i}_optimizer.ipynb`; shared code in `bbo_toolkit.py`.

**Current best-so-far (final, before round 13 returns):** **F1 1.05167e-4** · **F2 0.6894681** · F3 −0.0252350 · **F4 0.6027542** · **F5 8662.405** · F6 −0.2497464 · **F7 2.7486539** · **F8 9.9744580**
**Trials used: 12 of 13 · remaining: 1 — the final submission** *(F4: 11 used; its 13th is unrecoverable, the round-3 trial was misrouted, see Week 3)*
**Round 13 — the final round — submitted 2026-10-14. Nothing follows it.**

---

## Week 13 — Round-12 results and the FINAL submission (logged 2026-10-14)

**Summary. Six new bests in one round: F1, F2, F4, F5, F7, F8.** The headline is **F5 at
8662.41**, a 1.73× gain that lands within 0.08 of the figure a peer reported for the same
corner — so that function is now solved to the boundary. **F7 jumped to 2.748654**, past every
peer value we have seen. F3 and F6 came back marginally below their incumbents.

| Fn | Realised | Prev best | New best? | Predicted | Error |
|----|----------|-----------|-----------|-----------|-------|
| 1 | **1.05167e-4** | 1.03949e-4 | **yes** | 1.056e-4 (parabola) | −0.4% |
| 2 | **0.6894681** | 0.6291 | **yes** | 0.598 (model mean) | a high draw, by design |
| 3 | −0.0254738 | −0.025235 | no | −0.02499 | −0.0005, inside the noise |
| 4 | **0.6027542** | 0.5958135 | **yes** | 0.60334 (parabola) | −0.0006 |
| 5 | **8662.405** | 4998.33 | **yes** | ~30000 (our extrapolation) | **−3.5×** |
| 6 | −0.2512392 | −0.249746 | no | −0.2848 | +0.034 |
| 7 | **2.7486539** | 2.5916590 | **yes** | 2.645 | **+0.104** |
| 8 | **9.9744580** | 9.9730753 | **yes** | 9.9727 | +0.0018 |

**What the calibration column says.** The two predictions that were nearly exact came from
three-point parabolas through direct readings, not from any surrogate. The Gaussian processes
were *conservative* where their cross-validation score was high — F7 under-predicted by 0.104
and has now under-predicted twice running — and wrong about magnitude where it was not. And our
own log-slope extrapolation on F5, the most confident call of the project, was out by a factor
of three and a half. It got the direction right from five monotone readings and the destination
wrong by extending an accelerating trend that in fact saturates. **An accelerating gradient tells
you which way to go and almost nothing about how far.**

**The two functions that did not improve, and why that is informative.** F3's last three moves
have all come back inside 0.0005 of each other: that is a plateau top, and the parabola vertices
for both free inputs now sit inside the points already measured. F6's combined move came back
0.0015 below the incumbent, which — as flagged when it was made — does not say which of the two
axes caused it. Both functions are out of productive local moves.

---

### The final round: what changes when there is no round after this one

The score is the **best value observed**, so a probe that fails costs nothing — the incumbent is
kept either way. For twelve rounds that was not the governing consideration, because a wasted
trial meant one fewer chance to exploit later. On the last trial it is the only consideration,
and it inverts the usual logic: **a refinement worth zero is strictly worse than a long shot
worth nothing on average**, because the long shot has an upper tail and the refinement does not.

Three functions turned out to have genuinely nothing left on the axes we have been working:

- **F1's first input is exhausted to the limit of its resolution.** Four readings now sit on the
  lobe and the parabola vertex through the best three is 0.582562, predicting a gain over the
  incumbent of **0.00%**. There is no refinement left to buy.
- **F4's second input is on its vertex**, with readings either side 0.0015 apart.
- **F3 is on a plateau**, with both free inputs bracketed and flat.

So those three spend the last trial on something untested, as do F6 and, in a different sense,
F2.

**F1 — the second input, never varied on the lobe.** Every reading on the positive lobe
inherited 0.681526 from the round-4 point that found it; that axis has never moved. Fitting a
full two-dimensional quadratic to the magnitude across all readings puts the feature's centre
near (0.52, 0.52), which says the magnitude grows steeply as the second input *falls*. That fit
is crude — it mispredicts our own best point by 2.4 decades — so it is a direction, not a
destination. The first input is lowered by 0.004 alongside it, to stay on the positive side of
the zero crossing, whose location along the one slice we have is known. Potentially orders of
magnitude; realistically a coin flip; costs nothing if wrong.

**F4 — the fourth input, never varied inside the basin.** It has taken four values in the basin,
all between 0.430 and 0.441, and never moved at the incumbent. Two independent estimates now say
that is the wrong place: a peer brackets the peak below 0.428 with a vertex at 0.4166, having
measured 0.7089 there — above our best — and *our own* model's profile along that axis peaks
near 0.420 and rates our 0.4326 below both. The submitted value, 0.4183, is the midpoint of two
estimates that were arrived at independently.

**F6 — the fifth input, pinned on the boundary for all twelve trials.** Everything else is
bracketed: lowering the second input is worse, raising the fourth is worse, and the combined move
was worse. The fifth has never left the lower boundary. It is set to 0.056401, which is the value
it took in our best initial-design reading rather than a number chosen for the occasion.

**F3 — the largest hole in the cube.** The plateau is worth nothing more, and a peer reports a
value five times better than ours without saying where. The submitted point is the maximin
choice: 0.635 from every observation we hold, against a typical nearest-neighbour spacing of
0.152. Low odds, but it is the only move that could change this function's standing, and a
refinement worth 0.0002 cannot.

**F2 — one more draw.** Eight readings in the peak window average 0.610 with a standard
deviation of 0.046, so a fresh draw clears the incumbent about one time in twenty-four. That is
poor, and it is still the best available: every other location on the ridge has a lower mean.
The draw is taken on the inert second input again.

**F5 — the corner, resubmitted.** All four inputs are on the boundary and there is nowhere
further to go. The first input is moved by nine parts in a million purely so the submission is a
distinct point; the cost is about one unit in 8662.

**F7 and F8 — the model, with the leash let out slightly on F7.** F7's cross-validated score is
now **0.944**, its highest, and it has under-predicted its own proposal twice running. Its trust
region goes back from 0.03 to 0.05: the proposal predicts 2.819 with a larger uncertainty band
than the tighter box gives, and on a final draw scored by the best value observed, more mean and
more variance both help. F8 is unchanged and proposes the same point at every radius tested,
predicting fractionally below its own incumbent — it has been converged for three rounds.

**Final submission.**

| Fn | Point | Rationale |
|----|-------|-----------|
| 1 | 0.578600-0.671526 | untested second axis, toward the fitted feature centre |
| 2 | 0.712637-0.726564 | one more draw against a measurement noise of 0.046 |
| 3 | 0.442112-0.998457-0.899989 | maximin: the largest unsampled hole |
| 4 | 0.407583-0.416930-0.360748-0.418300 | untested fourth axis; two independent estimates agree |
| 5 | 0.999990-0.999999-0.999999-0.999999 | the corner; solved |
| 6 | 0.422422-0.453026-0.694051-0.794604-0.056401 | untested fifth axis, off the boundary |
| 7 | 0.000001-0.156255-0.476911-0.266948-0.324858-0.654164 | acquisition, trust region 0.05 |
| 8 | 0.104766-0.163677-0.137498-0.000184-0.828521-0.492790-0.197999-0.605977 | acquisition, converged |

**Closing position before the final results.** F1 1.05167e-4 · F2 0.6894681 · F3 −0.0252350 ·
F4 0.6027542 · F5 8662.405 · F6 −0.2497464 · F7 2.7486539 · F8 9.9744580. Against the three peer
posts we have seen, that is ahead on F1, F5, F7 and F8, level on F2 and F4 pending this round,
and behind on F3 and F6.

**The lesson of the last three rounds, stated plainly.** Three of the eight functions were
leaving most of their remaining value on an axis we had never varied at the incumbent, while we
spent round after round refining axes that were already bracketed. Local refinement concentrates
effort where feedback already exists, and that is precisely where the remaining gain is smallest.
A one-variable sweep across every axis, run early and cheaply, would have cost a few trials and
found those three gaps nine rounds sooner. That is the single change I would make to the method.

---

## Peer intelligence — three public posts (logged 2026-10-08)

Three classmates posted their round-11 positions. Same problem set (scales match ours on every
function). Treat the sources unequally: the second post is precise, numeric and
self-consistent; the first is moderate; the third is clearly LLM-written and inflated in its
prose, though its terminal table of portal values looks like genuine output.

**Where we stand.**

| Fn | Ours | Peer A | Peer B | Peer C | Read |
|----|------|--------|--------|--------|------|
| 1 | **1.04e-4** | ~0 | — | 0.000000 | **we lead** — nobody else is off the zero plateau |
| 2 | 0.6291 | 0.697 | ~0.726 | 0.6768 | behind on paper; see below — it is noise, not position |
| 3 | −0.02524 | −0.034 | −0.0464 | **−0.004807** | Peer C far ahead, no coordinates given |
| 4 | 0.5958 | 0.422 | **0.7089** | 0.3675 | Peer B ahead, **and they gave the coordinate** |
| 5 | 4998 (corner pending) | 6136.65 | corner (1,1,1,1) | **8662.48** | our round-12 point is exactly their corner |
| 6 | −0.2497 | −0.111 | **−0.088** | −0.2084 | behind, no coordinates |
| 7 | 2.5917 | **2.607** | ~2.58 | 2.3378 | level; our round-12 proposal predicts 2.645 |
| 8 | **9.9731** | ~9.9 | — | 9.9567 | **we lead** |

**F5 — the override was right, the extrapolation was not.** Two peers independently place the
optimum at the upper corner, one quoting above 8600 and the other stating the corner outright.
Our round-12 probe is that exact point, so it should land there. Our own log-slope extrapolation
predicted near 30000 — too high by roughly three and a half times. The *direction* was read
correctly off five monotone readings; the *magnitude* was a straight-line extension of an
accelerating trend that in fact saturates. Worth remembering: an accelerating gradient tells you
which way to go and almost nothing about how far.

**F4 — the one actionable coordinate.** Peer B reports a new best of 0.7089 from probing the
**fourth** input at 0.425, brackets the peak below 0.428, and puts the vertex at 0.4166. Our
fourth input has taken only four values inside the basin, all between 0.430 and 0.441 — we have
never looked below 0.430. On a function whose peak is a spike this narrow, being 0.016 off on
one axis is the right order of magnitude to explain the whole 0.113 gap.

**F2 — we are not actually behind.** Binning our own readings by the first input: 0.68–0.705
averages 0.591, 0.705–0.720 averages 0.599, and 0.72–0.76 collapses to 0.331. That
independently reproduces Peer B's ridge geometry (flat from 0.66 to 0.70, collapsing by 0.74)
and shows our location sits on the flat part, not the shoulder. Peer B also reports three
readings at a *single* point spanning 0.598–0.726. So the peers' 0.697 and 0.726 are luckier
draws from the same distribution, not a better position. The correct response is unchanged:
keep drawing.

**F6 — close but off, and we know by how much.** Peer B reports that points 0.03–0.05 from
their peak return −0.26 to −0.29, which is exactly the band our last several readings occupy.
That calibrates our distance to the optimum without giving its direction. The fifth input has
sat on the lower boundary in **all eleven** of our trials and has never been varied at the
incumbent — the same blind spot that is costing us on F4.

**F3 — unverifiable.** Peer C claims −0.004807 against our −0.02524 but gives no location, and
theirs is the least trustworthy of the three posts. Our own data shows nothing promising at low
values of the first input, and Peer A's best sits in our region and is *worse* than ours.

**The pattern across F4 and F6.** In both cases the gap to a peer is best explained by an axis
we have never varied at the incumbent, while we spent rounds refining the axes we had already
bracketed. Local refinement concentrates effort where feedback already exists, which is also
where the remaining gain is smallest. A single-variable sweep on every axis, early, would have
been cheap relative to what not having it has cost.

---

## Week 12 — Round-11 results (logged 2026-10-05)

**Summary.** Three new bests — **F5 4998.33**, **F4 0.5958135**, **F7 2.5916590** — and the
round's real news is that F5's ridge is still accelerating and F2 turned out to be far noisier
than we had priced in. Routing checked first: all eight submitted inputs match the recommended
points exactly.

**Results this round.**

| Fn | Realised | Prev best | New best? |
|----|----------|-----------|-----------|
| 1 | 1.0200e-4 | 1.0395e-4 | no — but it pinned the lobe maximum between two readings |
| 2 | 0.540073 | 0.6291 | no — and it settled the noise question the other way |
| 3 | −0.026440 | −0.025235 | no — brackets x2 tightly from above |
| 4 | **0.5958135** | 0.5895267 | **yes** |
| 5 | **4998.33** | 4643.17 | **yes — second vindicated override in a row** |
| 6 | −0.275699 | −0.249746 | no — and it refuted the model's preferred direction |
| 7 | **2.5916590** | 2.575776 | **yes** |
| 8 | 9.9718498 | 9.9730753 | no — fourth reading in a row inside 0.016 |

**Four findings.**

- **F5's ridge has not turned, and the rise is super-exponential.** Five readings now sit on
  the corner with the other three inputs pinned at the boundary: 4451.7, 4478.9, 4554.8,
  4643.2, 4998.3. The log-slope across those steps runs 0.070, 0.164, 0.292, 0.526 — it
  **doubles every 0.097 of travel in that input**. Fitting that growth and integrating it puts
  the far corner near 30000, roughly six times the incumbent. The surrogate disagrees violently
  (it predicts 770 there) but it cannot do otherwise: it is a quadratic on a log scale, so past
  its own vertex it is structurally obliged to predict a fall. Its prediction at the corner is a
  property of the model family, not evidence about the function.

- **F2 is noisier than we had priced in — and that is good news.** Seven readings now sit inside
  a window 0.009 wide and span 0.089, with a standard deviation of 0.036. That is half again the
  0.024 we had been assuming. Against a best-observed score, a bigger noise band makes repeated
  drawing *better*, not worse: a fresh draw at the peak has about a one-in-five chance of
  clearing the incumbent, and one-in-three across the two remaining rounds. Nothing else
  available on this function comes close to those odds.

- **F6's model has the sign of its gradient wrong, exactly as F5's did.** Holding everything else
  fixed, the second input gives −0.27570 at 0.413026 against −0.24975 at 0.453026 — improving as
  it rises, at 0.65 per unit. The additive surrogate, scoring 0.899, wants to move it *down*.
  An older configuration says the same thing over a much wider span (−0.64991 at 0.143514
  against −0.49840 at 0.453026), so two independent slices agree and the model is alone. Nothing
  above 0.453026 has ever been measured on that axis.

- **F4's step floor was still coarser than its own structure.** Three readings differing only in
  the second input give 0.58953, 0.59581, 0.58916 at 0.411177, 0.421177 and 0.422760 — a bracket
  **0.0015 wide**, against a step floor of 0.005. The proposer therefore had to overshoot, and it
  did: it asked for +0.01 and valued it at 0.6986, in a direction where a reading 0.0016 away has
  already fallen. This is the week-8 lesson recurring one order of magnitude further down.

**Changes applied for round 12.**

- **F5** — probe to the **full corner**, all four inputs at the boundary. Five monotone readings
  with an accelerating log-slope, and the other three inputs already pinned there, both say the
  optimum is a corner. If it comes back low, the peak is bracketed in (0.62, 1.0) and the final
  trial bisects; if it comes back high, this is the project's largest single gain.
- **F4** — `MIN_STEP` cut tenfold to 0.0005 so the proposer can step inside its own bracket, plus
  a probe at the parabola vertex of the three-point slice (0.416930), worth about +0.0075.
- **F6** — probe moving the second input **up** 0.04 and the fourth **down** 0.04, each along its
  own measured gradient and each the same size as the step that measured it. Moving two axes at
  once costs interpretability — a fall will not say which one caused it — and that is the price
  of having two rounds rather than five.
- **F2** — probe taking a clean replicate draw, generated by moving the **inert** second input by
  0.10 rather than by jittering the first. A 0.35 move on that axis changed the output by 0.003,
  so to the function this is the same location, while to the record it is a distinct point. The
  model's own proposal pushed that inert axis to the boundary and predicted below the incumbent.
- **F3** — probe setting both free inputs to the vertices of the parabolas through their own
  bracketing readings (0.586388 and 0.860752). Both are interpolations inside measured brackets,
  which is the limit of what a model scoring 0.11 should be trusted with; the proposer moves one
  axis per round and cannot take both.
- **F1** — probe at the lobe vertex, 0.582509, read off the three readings now sitting on the
  peak. Worth about 1.6 per cent. Its own bracket cannot reach it, because the bracket's next
  step is already in the data.
- **F7** — trust region narrowed from 0.20 to **0.03**. This is the endgame plan (smallest trust
  regions) and here it is also the line between interpolation and extrapolation: at 0.20 the
  proposal moved the sixth input 0.094, past a reading that came back lower, and at 0.03 every
  coordinate stays inside the span the local readings cover. The predicted gain falls only from
  2.662 to 2.645.
- **F8** — unchanged. Its proposal is insensitive to the trust-region radius at every value
  tested, and it predicts the incumbent's own value. This function is converged.

**Cross-validation this round.** F1 0.910 (Matérn 0.949 — ahead, but inside the 0.1 margin, so
no change) · F2 0.667 · F3 0.113 · F4 0.980 · F5 0.859 · F6 0.899 · F7 **0.908**, its best yet ·
F8 0.995.

**One defect noticed, not fixed.** On F1 only, the "distance to it" and "below the incumbent"
lines in the proposal block are computed against the best point in *fit* space. Because F1 is
fitted to the magnitude of its output, that is the large negative trough reading, not the best
true value printed two lines above. The proposal itself is unaffected. With two rounds left the
risk of touching display code outweighs the benefit; it is recorded here instead.

**What the last round should hold.** F5 is the only function where a large gain is still
plausible, and both its outcomes leave a well-defined final move. F2 should take its second
draw. F1, F3, F4 and F7 are refining inside brackets a few thousandths wide. F8 is finished and
its last trial is a free lottery ticket near the incumbent.

---

## Week 11 — Round-10 results (logged 2026-10-01)

**Summary.** Three new bests, and the headline one vindicates a deliberate override of the
model. **F5 reached 4643.17.** Last round its surrogate predicted a peak *below* the
incumbent and mis-predicted its own measured point by 126, while three direct readings ran
monotonically upward. I overrode the model with an explicit probe past the highest reading,
and the probe set a new best. **F8 reached 9.9731**, its third consecutive record, and it
under-predicted again — its calibration is now the most reliable thing in the project.
**F6 edged up to −0.2497.** F4 came within a whisker of its own record, confirming it sits
on its peak.

**Results this round.**

| Fn | Realised | Prev best | New best? |
|----|----------|-----------|-----------|
| 1 | 9.744e-5 | 1.0395e-4 | no — but it located the lobe maximum |
| 2 | 0.55950 | 0.6291 | no — and it settled the noise question |
| 3 | −0.027964 | −0.025235 | no |
| 4 | 0.5891556 | 0.5895267 | no — within 0.0004 of its own record |
| 5 | **4643.17** | 4554.83 | **yes — the override was right** |
| 6 | **−0.249746** | −0.255190 | **yes** |
| 7 | 2.565676 | 2.575776 | no |
| 8 | **9.9730753** | 9.9667517 | **yes (third in a row)** |

**Three findings.**

- **F5's ridge is rising and accelerating.** The corner readings along its one free input now
  run 4451.7, 4478.9, 4554.8, 4643.2 — and the gain per unit of distance across those steps
  runs roughly 310, then 740, then 1340. Nothing in that suggests a turn. The next probe takes
  a deliberately larger step: with three rounds left, creeping would leave ground uncovered,
  and a fall still brackets the peak for the final two.
- **F2 is definitively noisy.** A reading taken *between* two points that gave 0.626 and 0.629,
  barely a thousandth away from each, came back at 0.560. No deterministic surface does that.
  Across the seven readings in that window the spread implies a standard deviation around
  0.024, which makes the current best roughly four-fifths of a deviation above the underlying
  mean — a lucky draw rather than a found optimum. **Three more draws at the peak therefore
  have about an even chance of beating it**, which is a better return than any alternative use
  of those trials, and the configuration is already set up to deliver them.
- **F1's lobe maximum is at or just below the incumbent.** One step up came back lower. The
  bracket, by construction, can only step upward, so a downward probe was added by hand. Worth
  a few per cent at most — but this function has nothing better to do with its remaining
  trials.

**Changes made.** F5's probe moved further up the ridge; F1 gained a downward probe. Nothing
else changed: F3, F4, F6 and F8 all now propose points their own models rate above their
incumbents, which is the first time in several rounds that a majority have.

**Notable signal.** The F5 episode is the clearest instance of a theme running through this
whole log: **when a model's local behaviour contradicts direct repeated measurements, the
measurements win.** It had a respectable cross-validation score and still had the sign of the
local slope wrong, because that score is dominated by observations far from the region now
being searched. Overriding it was not a departure from the method — recognising where a model
stops being reliable is the method.

---

---

## Week 10 — Round-9 results (logged 2026-09-23)

**Summary.** Three new bests — **F6 to −0.2552**, a large gain; **F8 to 9.9668**; and **F3 to
−0.02524**, marginal but real. F8's model under-predicted slightly for the first time, which
means its calibration is now genuinely good rather than merely corrected. F1's space-filling
probe returned **exactly 0.0** — not a small number, zero — which settles that question: the
function underflows to nothing away from its source, so covering empty space is worth
precisely nothing.

**Results this round.**

| Fn | Realised | Prev best | New best? |
|----|----------|-----------|-----------|
| 1 | 0 (exact) | 1.04e-4 | no — but it closed the exploration question |
| 2 | 0.60406 | 0.6291 | no — and it revealed noise, see below |
| 3 | **−0.025235** | −0.025534 | **yes (marginal)** |
| 4 | 0.52109 | 0.58953 | no — optimum confirmed to within 0.013 |
| 5 | 4478.88 | 4554.83 | no |
| 6 | **−0.25519** | −0.3558 | **yes (large)** |
| 7 | 2.53489 | 2.57578 | no |
| 8 | **9.96675** | 9.95740 | **yes** |

**Two findings that changed the endgame plan.**

- **F2 is genuinely noisy, and that changes the optimal play.** Its readings around the peak
  are not monotone: 0.7126 gives 0.629, 0.7149 gives 0.604, 0.7176 gives 0.608. Over a span
  that small that is measurement noise, not structure, and it matches this function's original
  description as a noisy likelihood. **Because the score is the best value observed rather than
  the mean, the correct response to real noise is to keep drawing at the best location** —
  every draw is an independent chance at a high reading, and the expected maximum of several
  draws exceeds any single one. Its step size has been cut to the point where candidates are
  near-replicates with just enough jitter to remain distinct points.
- **F5's model contradicts its own measurements.** At the corner it now occupies, the three
  readings along its one free input run 4451.7, 4478.9, 4554.8 — monotonically increasing —
  while the global model predicts a peak *below* them, and mis-predicts its own measured point
  there by 126. A model whose local slope has the wrong sign does not get to choose the next
  point. An explicit probe steps past the highest reading to find out whether the rise
  continues; if it does not, the peak is bracketed and the model resumes.

**Changes made — the endgame sweep.** With four submissions left, every function is now on
pure exploitation. Expected improvement and optimism bonuses exist to buy information, and
there is no longer time to spend it.

- **F5, F6 — ranking switched from expected improvement to predicted mean.** EI had been
  choosing the most *uncertain* candidate over the highest-predicted one. On F5 that single
  change raised the value of the chosen candidate from 3809 to 4635.
- **F7 — exploration weight to zero**, raising its proposal's predicted value from 2.515 to
  2.561. F8 was already there; F3 and F4 already rank on the mean.
- **F1 — back to the bracket at a much smaller step.** Halving had converged *on* the
  crossing, where the value is zero. From the rate the magnitude grows, the lobe's maximum sits
  roughly a sixth of the way from the best positive reading toward the crossing, and the step
  now aims there. A zero-safe transform was also needed: the exact-zero reading produced an
  infinity that broke the fit.
- **F6 — step size cut again**, because a parabola through its three readings on the input
  being moved puts the peak at 0.667 and the step was too coarse to land near it.

**Where the remaining value is.** Most of these have converged: six of eight now propose
points their own models rate below the incumbent, which is what running out of local
improvement looks like. The three places real value remains are F5's probe above its highest
reading, F2's repeated draws against its noise, and F8, which is still climbing steadily with
the best calibration in the project.

---

## Week 9 — Round-8 results (logged 2026-09-15)

**Summary.** Three new bests, and every one of them came from a change made the previous round
in response to a diagnosed failure. **F4 finally broke the record it set on its very first
trial**, 0.5235 → **0.5895**, after six failed attempts: the move that did it was a single
coordinate shifted by 0.013, exactly the scale the evidence had pointed to. **F7** rose to
**2.5758** once the lengthscale ceiling was lowered and the model could finally see the input
it had been calling irrelevant. **F8** reached **9.9574** with its exploration weight at zero,
and — more tellingly — its prediction error was **−0.010**, against a previous best of −0.028
and a running average near −0.09. The optimism correction worked cleanly. F2, F3, F5 and F6
all came in slightly under their incumbents, which is itself useful: each confirmed the
coordinate we moved was already at its best value.

**Results this round.**

| Fn | Realised | Prev best | New best? |
|----|----------|-----------|-----------|
| 1 | −0.00014 | 1.04e-4 | no — bracket closed (see below) |
| 2 | 0.62644 | 0.6291 | no — peak confirmed |
| 3 | −0.02700 | −0.02553 | no — optimum confirmed |
| 4 | **0.58953** | 0.5235 | **yes — first time beaten** |
| 5 | 4148.33 | 4554.83 | no — boundary confirmed |
| 6 | −0.42760 | −0.3558 | no — optimum confirmed |
| 7 | **2.57578** | 2.4814 | **yes** |
| 8 | **9.95740** | 9.9502 | **yes** |

**The round's real finding: most of these have converged.** Only two of eight now propose a
point their own model rates above the incumbent, down from six the week before. That is not a
failure — it is what running out of local improvement looks like, and recognising it is the
difference between spending the last trials well and spending them out of habit.

**F1 is finished, and the arithmetic says so.** The readings either side of its sign flip are
now nearly equal in size — 1.04e-4 positive against 1.40e-4 negative. From the rate at which
the magnitude grows along that line, the positive lobe's peak sits within about 0.0005 of the
incumbent. Bisecting again converges on the crossing itself, **where the value passes through
zero** — so the procedure that gained twelve orders of magnitude now has nothing left to give.
Its remaining trials are worth more spent elsewhere in the square: low odds of a second
source, but a better expected value than the one per cent left on the table here. **A search
procedure can be correct, productive, and finished, and the third is a separate judgement from
the first two.**

**Changes made for next round.**

- **F1 — switched to space-filling exploration.** Per the above. The first probe sits 0.4 from
  any existing observation.
- **F5 — step size cut again.** This round proved that moving one of its boundary-pinned
  inputs off the boundary costs about 400, yet the proposal wanted to do exactly that,
  predicting 3273 against an incumbent of 4555 — a knowingly wasted trial. Finer steps keep
  candidates close enough to the boundary that the known-bad direction stops being
  competitive; the proposal is now a move along the one free input, predicted **above** the
  incumbent.
- **F2, F3, F4, F6, F7, F8 — no change.** F4, F7 and F8 are all still climbing; F2, F3 and F6
  are creeping at their peaks, which is the right thing to be doing with six trials left.

**Notable model signals.** F8's calibration is worth recording as a result in its own right:
seven consecutive over-predictions averaging −0.09, then −0.010 once the acquisition stopped
adding optimism to a model that already had a measured positive bias. The lesson is that
**acquisition optimism and model bias compound**, and cross-validation cannot see the second
one, because it tests interpolation among points the model has rather than extrapolation to
the one you are about to buy.

---

---

## Week 8 — Round-7 results (logged 2026-09-09)

**Summary.** Two new bests — **F5 to 4554.83** and **F6 to −0.3558**, the latter a large jump —
but the round's value is almost entirely diagnostic. Four separate readings each overturned
something the models had been assuming, and three of those assumptions had been quietly
costing trials for weeks. This was the most informative round of the project, and none of it
came from a good score.

**Results this round.**

| Fn | Realised | Prev best | New best? | What it told us |
|----|----------|-----------|-----------|-----------------|
| 1 | −0.00136 | 1.04e-4 | no | sign bracket narrowed to a window of 0.017 |
| 2 | 0.62654 | 0.6291 | no | **the "irrelevant" input really is irrelevant** — question closed |
| 3 | −0.04121 | −0.0255 | no | the second input's optimum is bracketed near 0.598 |
| 4 | **−0.00143** | 0.5235 | no | **the peak is a spike** — see below |
| 5 | **4554.83** | 4451.67 | **yes** | the first input has a mild optimum above its old value |
| 6 | **−0.3558** | −0.4487 | **yes** | large gain; predicted −0.387, beat the prediction |
| 7 | 2.0494 | 2.4814 | no | **the "inert" third input is not inert** — again |
| 8 | 9.9062 | 9.9502 | no | seventh consecutive over-prediction |

**Four findings.**

- **F4's peak is a narrow spike sitting on a smooth background.** A move of **0.024** cost
  **0.43**, while a move of 0.012 the round before had *gained* 0.05. That is a local gradient
  of roughly eighteen units per unit of distance, against fitted lengthscales that say about
  1.3. The model is over-smoothing by more than an order of magnitude exactly where the search
  now lives. Its cross-validated score of 0.98 is real but earned on the thirty spread-out
  initial points; it says nothing about behaviour inside the spike. **Tightening the kernel
  does not fix it** — forcing shorter lengthscales drops Q² from 0.98 to 0.85, because the
  smooth background is also real. The honest response is to stop asking the model to choose a
  location and confine the search to steps small enough that a wrong ranking is cheap.
- **F7's third input is not inert, and this is the second time this function has produced a
  false "irrelevant" verdict.** Readings at 0.25, 0.45 and 0.65 give 2.05, 2.48 and 2.37 — a
  clear peak. The input's lengthscale had saturated at its ceiling, which the model reports as
  "no influence" when it can equally mean "the ceiling is too high to distinguish weak
  influence from none". Bringing the ceiling down from 10.0 to 0.8 leaves every lengthscale
  fitted rather than pinned and **raises Q² from 0.82 to 0.87**. The same mistake cost this
  function two rounds earlier in the project on a different input.
- **F2's single-variable test settled its open question.** Moving the suspected-inert input by
  0.35 while holding everything else fixed changed the output by 0.003. It is genuinely inert,
  and stepping it can stop. The same test also showed the fitted noise is essentially zero,
  which means the small differences between readings near the peak are **real** — and those
  readings put the peak inside a window about 0.01 wide, far narrower than the step size was
  able to resolve.
- **F8's bias did not go away when the exploration weight was halved.** Seven trials, seven
  over-predictions, latest −0.104. Halving the weight last round treated it as an acquisition
  problem; it is a model problem, and adding any optimism on top of a model with a measured
  positive bias is simply adding a known error.

**Changes made for next round.**

- **Toolkit — the local step size now has an adjustable floor.** It had been hard-coded at
  0.02, which was fine until three functions turned out to have structure narrower than that.
  A floor that cannot go below the width of the peak makes every candidate overshoot the thing
  being refined, and nothing in the output reveals it.
- **F1 — bracket now steps toward the *nearest* negative reading, not the strongest.** Once
  the bracket tightens, the strongest negative sits outside it, and stepping toward that point
  steps straight past the crossing being pinned down. A correctness fix, not a tuning change.
- **F2 — inert threshold restored, step size cut to about a fifth.** The test is done and the
  answer is in, so candidates stop being spent on that input; the finer step can now resolve a
  peak 0.01 wide. Q² rose from 0.42 to **0.59**.
- **F3 — step size cut again.** The refit made its second input look influential and gave it a
  step of 0.074, which put the proposal at 0.449 — outside the bracket its own data has drawn
  (0.548 → −0.028, 0.598 → −0.026, 0.648 → −0.041) — where the model predicted a *positive*
  value, better than anything ever observed, on a Q² of 0.03. Small steps keep an unreliable
  model inside the region its own data supports.
- **F4 — taken off the acquisition entirely, onto bounded local steps ranked by predicted
  mean.** Step size set from the evidence (0.012 gained, 0.024 lost) rather than from the
  lengthscales. The mean rather than expected improvement, because a model that over-predicts
  should not also receive an uncertainty bonus.
- **F7 — lengthscale ceiling brought down** so nothing saturates, per the finding above.
- **F8 — exploration weight to zero and the trust region narrowed back.** The wider box was a
  deliberate probe for a better basin; it proposed a point 0.46 away and returned below the
  incumbent, so the answer is no. Question asked, answered, region restored.
- **F5, F6 — no change.** Both working; F6's model reached **Q² 0.956**, the highest of any
  non-trivial function in the project.

**Points submitted (round 8).**

| Fn | Point | Predicted vs incumbent |
|----|-------|------------------------|
| 1 | 0.591855, 0.681526 | bracket step |
| 2 | 0.708402, 0.926564 | **above** |
| 3 | 0.999999, 0.560976, 0.859784 | **above** |
| 4 | 0.407583, 0.411177, 0.360748, 0.432592 | below (bounded probe) |
| 5 | 0.414278, 0.968997, 0.999999, 0.999999 | **above** |
| 6 | 0.422422, 0.453026, 0.567434, 0.680403, 0.000001 | **above** |
| 7 | 0.000001, 0.162206, 0.510665, 0.268312, 0.371891, 0.731059 | **above** |
| 8 | 0.115486, 0.158198, 0.176940, 0.000001, 0.903935, 0.440256, 0.205245, 0.402084 | **above** |

Six of eight are predicted above their incumbents, the best position of the project so far.

**Notable model signals.** Two lessons generalise beyond this project. **A saturated
lengthscale is not evidence of irrelevance** — it means the model cannot distinguish weak
influence from none at the ceiling it was given, and lowering the ceiling is the test.
Acting on the "irrelevant" reading has now cost trials twice on the same function. And **a
high cross-validation score is scoped to the region the data covers**: F4 scores 0.98 while
over-smoothing its own peak by more than tenfold, because the score is dominated by
observations spread far from the optimum. Where a model is *used* and where it was *validated*
are not the same place.

---

---

## Week 7 — Round-6 results (logged 2026-09-03)

**Summary.** Two new bests, one of them decisive. **F5 reached 4451.67**, up from 2917 — the
high-corner hypothesis is confirmed, and that figure also clears the best publicly posted by
a peer working the same eight functions, on the one where we were furthest behind.
**F6 improved to −0.4487**, which the halved step size made possible. F4 climbed to 0.4713,
its closest approach yet to a record it has not beaten since round one. **F1 came back
negative**, which is the sign-bracket working rather than failing: the sign now flips inside
a window a third of its previous width, and the strongest negative reading moved with it.
F2, F3, F7 and F8 all came in under their incumbents.

**Budget correction.** The trial budget is **14 per function, not 10**. Every plan in this log
before this entry was written against the wrong number, and the correction matters: it turns
"four trials left, stop exploring" into "eight left, two or three exploratory shots are
affordable before the endgame". The endgame now begins around round eleven. `TRIAL_BUDGET`
has been corrected in all eight notebooks so the printed remaining count is honest.

**Results this round.**

| Fn | Rule used | Predicted | Realised | Prev best | New best? |
|----|-----------|-----------|----------|-----------|-----------|
| 1 | sign bracket | \|y\| ≈ 10⁻²·⁸ | −0.00837 | 1.04e-4 | no — but the bracket narrowed to a third |
| 2 | local steps, EI | 0.616 | 0.608 | 0.629 | no |
| 3 | local steps, EI | −0.045 | −0.067 | −0.0255 | no — peak now bracketed |
| 4 | UCB β=1.5, TR r=0.20 | 0.467 | 0.471 | 0.524 | no (closest yet) |
| 5 | local steps, EI | ≈2809 | **4451.67** | 2917 | **yes (+53%)** |
| 6 | local steps, EI | −0.389 | **−0.4487** | −0.498 | **yes** |
| 7 | EI ξ=0.01, TR r=0.20 | 2.494 | 2.373 | 2.481 | no |
| 8 | UCB β=1.5, TR r=0.15 | 9.977 | 9.906 | 9.950 | no |

**Two bugs found, both silent.**

- **F5's plausibility ceiling had turned into a blindfold.** That guardrail exists to stop a
  polynomial surrogate proposing a physically absurd value, and it was set when the best
  observed value was far lower. The incumbent's own log-value has since climbed past the
  ceiling, so the filter was discarding **every candidate the model rated above the
  incumbent** and leaving only worse ones to rank. That is why F5's proposal this week was
  a step in the wrong direction, predicted at barely a third of the current best. Raising
  the ceiling restored six candidates, and the proposal changed from a retreat to a step
  along the only coordinate still free to move. **The lesson generalises: a guardrail
  calibrated against an old scale stops protecting and starts blinding, and it fails
  silently because a filtered candidate leaves no trace in the output.**
- **F8's surrogate is systematically optimistic.** Checking every prediction it has ever made
  against what came back: −0.142, −0.100, −0.132, −0.028, −0.051, −0.092. Six out of six
  overestimates, averaging about −0.09. That is bias, not noise, and its cross-validated
  score of 0.99 cannot see it, because cross-validation tests interpolation among points the
  model has, not extrapolation to points it does not. Meanwhile the acquisition was adding
  its own optimism on top, so proposals were effectively selected on a value roughly 0.18
  too high. **A high cross-validation score certifies interpolation, not extrapolation, and
  the two come apart exactly where a proposal lives.**

**Changes made for next round.**

- **F3 — rank on the predicted mean rather than expected improvement.** Every candidate now
  scores essentially zero on EI because the model expects no improvement anywhere, which
  makes the ranking noise. Worse, it was discarding a candidate the model predicts *above*
  the incumbent with high confidence, purely because that candidate carried little
  uncertainty — EI penalises certainty. With this function's noise now known to be tiny, the
  mean is the right thing to rank on. Its step size was also cut, since the peak on the
  active axis is bracketed by three readings and the previous step jumped outside that
  bracket. The proposal is now predicted above the incumbent for the first time in weeks.
- **F8 — exploration weight cut and trust region widened.** The weight comes down to correct
  the double optimism above; the region widens because six readings now sit in one narrow
  band inside a single basin the search has never left. With the optimism corrected, a wider
  box is the affordable way to find out whether a better basin exists.
- **F2 — the "irrelevant" second input is being tested.** It has been written off all project
  on the strength of a saturated lengthscale. That exact verdict was wrong on F7 and cost
  several rounds there before a refit corrected it. The proposal now moves that input alone,
  holding everything else at the incumbent, which makes the result a clean single-variable
  answer either way.
- **F4 — probe run and reverted, no trial spent.** The trust region was released and the
  exploration weight raised to see whether the acquisition would leave a basin it has failed
  to improve on in five attempts. With the entire box available it returned to the same
  neighbourhood — which, from a model scoring 0.98, is a substantive answer rather than a
  failure to explore. Settings restored. **Worth noting as a technique: an exploration
  question can sometimes be answered by re-running the acquisition under different settings,
  without spending an evaluation on it.**
- **F1, F6, F7 — no change.** All three are working; F6 and F7 both propose above their
  incumbents, and F1's bracket is the highest-leverage search in the project.

**Points submitted (round 7).**

| Fn | Point |
|----|-------|
| 1 | 0.600178, 0.681526 |
| 2 | 0.712637, 0.576564 |
| 3 | 0.999999, 0.648179, 0.859784 |
| 4 | 0.403066, 0.391304, 0.394235, 0.440750 |
| 5 | 0.414278, 0.999999, 0.999999, 0.999999 |
| 6 | 0.422422, 0.453026, 0.567434, 0.834604, 0.000001 |
| 7 | 0.000001, 0.141344, 0.248347, 0.274723, 0.404053, 0.755914 |
| 8 | 0.163812, 0.025334, 0.194424, 0.000001, 0.999999, 0.441446, 0.160229, 0.893085 |

Four of the eight are now predicted above their incumbents, up from three.

**Plan for the remaining eight rounds.** Rounds 7–10 keep room for informative moves: F1's
bracket, F2's single-variable test, F8's wider basin probe. Rounds 11–14 go to pure
exploitation — exploration weights to zero, smallest trust regions, and any function whose
model still cannot predict spends its last trials confirming its best reading rather than
hunting new ones.

---
**Round 6 submitted 2026-08-27; outputs pending.**

---

## Week 6 — Round-5 results (logged 2026-08-27)

**Summary.** Three new bests, and one of them is the single largest gain of the project.
**F1 returned 1.04e-4** — positive — against a previous best of 6.4e-12. That is **eight
orders of magnitude in one trial**, and it landed almost exactly where the magnitude model
said it would (predicted \|y\| near 10⁻⁴·³, realised 10⁻³·⁹⁸). The sign-bracket reasoning
introduced last week was correct: the source is a trough, not a peak, and the large
positive values sit just outside it. **F5** went 1895 → **2917**, and **F2** set a modest
new best at **0.629**. F4 recovered to its second-best value, and F7 and F8 came in just
under their records, which is what refinement looks like when a model is well calibrated.
F3 and F6 both went backwards.

The quieter and arguably more important story is that **the surrogates improved sharply**.
Cross-validated Q² moved up almost everywhere: F7 **0.29 → 0.73**, F5 0.65 → 0.74, F6
0.77 → 0.81, F1 0.77 → 0.81, F4 0.97 → 0.98, and **F3 crossed above zero for the first
time in the project** (−0.07 → +0.04), vindicating last week's noise correction. Models
that predict better make the remaining budget worth more, so this matters as much as the
scoreboard.

**Results this round.**

| Fn | Rule used | Predicted | Realised | Prev best | New best? |
|----|-----------|-----------|----------|-----------|-----------|
| 1 | sign bracket, halfway | \|y\| ≈ 10⁻⁴·³ | **1.04e-4** | 6.4e-12 | **yes — eight orders of magnitude** |
| 2 | local steps, EI | 0.570 | **0.629** | 0.611 | **yes** |
| 3 | local steps, EI (x2 line search) | −0.045 | −0.038 | −0.026 | no |
| 4 | UCB β=1.5, TR r=0.20 | 0.479 | 0.425 | 0.524 | no (2nd of 34) |
| 5 | local steps, EI | ≈2705 | **2917** | 1895 | **yes (+54%)** |
| 6 | local steps, EI | −0.500 | −0.659 | −0.498 | no — the model's one bad miss |
| 7 | local steps, EI | 2.328 | 2.396 | 2.481 | no (2nd of 35) |
| 8 | UCB β=1.5, TR r=0.15 | 9.976 | 9.925 | 9.950 | no (2nd of 45) |

**Changes made for next round.** Five functions are left exactly as they are — they are
working, and this is not the point in the budget to disturb a method that is producing
records. Three are changed, each triggered by something measured this round.

- **F7 — promoted back to full acquisition control.** Its cross-validated score more than
  doubled, from 0.29 to 0.73, which puts it in the range where the model can be trusted to
  choose a *location* rather than merely rank a handful of local steps. `PROPOSER` goes
  from local back to acquisition, with a trust region enabled at the same radius used on
  the other well-modelled function — six dimensions is far too large to search globally on
  five remaining trials. The immediate effect is a proposal predicted **above** the
  incumbent, which the local candidate set could not reach.
- **F2 — surrogate switched to the additive kernel.** It now scores 0.41 against the
  Matérn's 0.12, comfortably clearing the 0.1 margin we require before changing model. The
  proposed point is unchanged, but the prediction attached to it is tighter and better
  calibrated, which is what will matter when the final exploitation rounds arrive.
- **F6 — step size cut so the largest available move is roughly halved.** Its one bad miss
  this round was a large single-coordinate jump: the model predicted −0.500 and the
  function returned −0.659. Halving the step parameter turned out to be *nominal* — the
  candidate set still contained a jump of the same size, because this kernel fits long
  lengthscales and the step was saturating against its cap, and the model kept choosing it.
  Cutting further caps the reach directly rather than hoping the ranking avoids it. The new
  proposal moves half as far and is still predicted well above the incumbent.
- **F1, F3, F4, F5, F8 — no change.**

**Points submitted (round 6).**

| Fn | Point | Rule |
|----|-------|------|
| 1 | 0.616824, 0.681526 | sign bracket, halved again |
| 2 | 0.717637, 0.926564 | local step (additive model) |
| 3 | 0.999999, 0.598179, 0.892673 | x2 line search |
| 4 | 0.393611, 0.416793, 0.401217, 0.430336 | UCB argmax |
| 5 | 0.224189, 0.999999, 0.999999, 0.999999 | x1 step |
| 6 | 0.422422, 0.453026, 0.801323, 0.834604, 0.000001 | x3 step, halved reach |
| 7 | 0.000001, 0.147363, 0.648347, 0.269252, 0.346010, 0.759983 | EI argmax in trust region |
| 8 | 0.086449, 0.000001, 0.125674, 0.000001, 0.903935, 0.498012, 0.340137, 0.393085 | UCB argmax |

**Notable model signals.** Two things worth carrying forward. First, **promotion and
demotion should both be automatic consequences of the cross-validation score**, not
one-way decisions. F7 was demoted when its score was weak and is promoted now that it is
strong; treating the tier as a standing judgement rather than a measurement would have
left it searching timidly with a model that had earned better. Second, **a parameter
change that does not change behaviour is worse than no change at all**, because it
creates the appearance of a fix. Halving F6's step left the offending move in the
candidate set and the model kept selecting it; only capping the reach actually altered the
decision. Worth checking that a change moves the output, not just the config.

**Budget.** Halfway. Five trials remain on every function except F4, which has six. The
plan holds: one or two more informative gambles, then the final two rounds go to pure
exploitation — margins to zero, smallest trust regions, and any function still scoring
near zero spends its remaining trials confirming its best reading rather than hunting new
ones.

---

## Week 5 — Round-4 results (logged 2026-08-20)

**Summary.** The best round of the project: **four new bests**, after a round with none.
F5 jumped 1089 → **1895** (+74%), F7 2.406 → **2.481**, F8 9.874 → **9.950**, F6 −0.650 →
**−0.498**. F4 returned 0.341, its second-best ever and a recovery from −2.29. The
evidence-based turn taken in week 4 is doing what it was supposed to: the three functions
flagged in advance as most likely to set a record — F5, F6 and F8 — all did. F8's model
predicted 9.978 and the function returned 9.950, an error of under three parts in a
thousand, which is what a cross-validated score of 0.99 is supposed to buy. F6 came back
*better* than predicted. Both of the two functions still handled by the classic continuous
acquisition (F4, F8) behaved exactly as modelled, and the five handled by ranked local
moves all either improved or stayed within a whisker of their incumbent — no repeat of the
week-3 pattern where every exploratory push made things worse.

**Results this round.**

| Fn | Rule used | Predicted | Realised | Prev best | New best? |
|----|-----------|-----------|----------|-----------|-----------|
| 1 | local steps on log₁₀\|y\| | −2.27 (log scale) | 6.40e-12 | ~0 | technically yes — but see below |
| 2 | local steps, EI | 0.583 | 0.591 | 0.611 | no (2nd of 14) |
| 3 | near-replicate | −0.0268 | −0.0276 | −0.0255 | no — **and that was the point** |
| 4 | UCB β=1.5, TR r=0.20 | 0.515 | 0.341 | 0.524 | no (2nd of 33) — big recovery |
| 5 | local steps, EI | ≈2939 | **1895** | 1089 | **yes (+74%)** |
| 6 | local steps, EI | −0.546 | **−0.498** | −0.650 | **yes** |
| 7 | local steps, EI | 2.299 | **2.481** | 2.406 | **yes** |
| 8 | UCB β=1.5, TR r=0.15 | 9.978 | **9.950** | 9.874 | **yes** |

**Changes made for next round.** The working configuration is deliberately left alone on
six functions — mid-run changes to something that is working are how a good streak gets
lost. Two functions are changed, and in both cases the round itself forced the change.

- **F3 — the replicate paid for itself, and overturns the noise assumption.** The two
  near-identical points returned **−0.025534** and **−0.027582**: a difference of **0.002**,
  implying a noise standard deviation near **0.0014**. The model had been fitting a noise
  level of about **0.126** — sixty times too large — which means it was absorbing real
  structure into a noise term. That is the direct cause of its negative cross-validated
  score. `NOISE_BOUNDS` now caps the noise near its measured value. Two consequences: this
  function's leaderboard *is* trustworthy after all, so small differences between readings
  are real; and with the noise term no longer swamping everything, a second input stopped
  looking inert. Q² improves (−0.24 → −0.07) but is still negative, so the round is a plain
  one-dimensional line search along the single input with the clearest evidence.
  Separately, the replicate proposer would have **resubmitted a point already in the data** —
  it does not check the existing design. A duplicate guard now raises rather than wasting
  a trial, and the proposer is switched to local steps.
- **F1 — the model was optimising the wrong quantity.** Round 4 measured **+6.4e-12** at
  x0 = 0.517 and **−3.6e-03** at x0 = 0.650, on the same x1. The sign flips between them
  and the magnitude grows by nine orders of magnitude toward 0.650. That location is the
  source — and it is a **trough**, not a peak. Fitting log₁₀\|y\| models the magnitude
  beautifully (Q² ≈ 0.77) but maximises \|y\| when the objective is y. A signed-log target
  is monotone in y, so its argmax is correct; it was tested and rejected because the sign
  flip is a cliff in that space that no smooth model fits (Q² falls to about −0.29). The
  resolution keeps the magnitude model for *reading* the surface and chooses the point
  geometrically: step from the best positive reading toward the strongest negative one.
  Each trial then either lands positive with a far larger magnitude — a new best,
  potentially by several orders — or halves the bracket on where the sign flips. The
  magnitude model puts \|y\| near 10⁻⁴·³ at the proposed point, which if positive would beat
  the current best by roughly seven orders of magnitude.
- **F2, F4, F5, F6, F7, F8 — no change.** All working; four of the six set records.

**Points submitted (round 5).**

| Fn | Point | Rule |
|----|-------|------|
| 1 | 0.583533, 0.681526 | sign bracket, halfway |
| 2 | 0.712637, 0.926564 | improving direction ×0.5 |
| 3 | 0.999999, 0.598179, 0.832940 | x2 −1 step |
| 4 | 0.395440, 0.407724, 0.408719, 0.433646 | UCB argmax |
| 5 | 0.224189, 0.846480, 0.999999, 0.999999 | x2 +1 step |
| 6 | 0.422422, 0.453026, 0.451323, 0.999999, 0.000001 | x2 −1 step |
| 7 | 0.000001, 0.044238, 0.448347, 0.289155, 0.373715, 0.749975 | x1 −1 step |
| 8 | 0.000001, 0.158500, 0.135447, 0.000001, 0.903935, 0.339455, 0.203198, 0.693085 | UCB argmax |

**Notable model signals.** Two lessons, both about *what you are modelling* rather than
*how well*. First, a surrogate can be excellent and still be pointed at the wrong target:
F1's magnitude model is the best-cross-validated model in the project outside F4 and F8,
and it was steering the search toward a minimum. Fit quality and objective correctness are
independent, and only the second is checked by asking what the number you are maximising
actually means. Second, a noise estimate is a *fitted parameter*, not a fact — F3's was
wrong by a factor of sixty and had been silently corrupting both its predictions and the
strategy built on them. One deliberately spent trial exposed it. A replicate looks like a
wasted round on the scoreboard and is sometimes the highest-value point available.

**Operational note.** `NEW_Y` was left filled in across all eight notebooks after the
results were recorded. Re-running any of them in that state appends the same trial a
second time and silently corrupts `new_trials.csv`. All eight have been reset to `None`.

---

## Week 4 — Round-4 submissions (logged 2026-08-11, outputs pending)

**Summary.** This round changes the *method*, not just the settings, and the reason is a
measurement. Leave-one-out cross-validation (remove one observation, refit on the rest,
predict the removed point, repeat for all of them; Q² = 1 is perfect, 0 is no better than
always guessing the mean, below 0 is worse than that) was run for eight candidate
surrogates on all eight functions. The result: only **F4 (0.97)** and **F8 (0.99)** have
models that genuinely predict unmeasured points. **F3 is negative (−0.24)**. The other
five sit between 0.19 and 0.36. Since Bayesian optimisation is precisely the act of
trusting a model about somewhere nobody has measured, that score decides how much
authority each model gets. Two consequences follow. First, on three functions a
**different surrogate** predicts substantially better and has been adopted: a quadratic
trend on the log scale for F1 and F5 (a Gaussian-shaped peak is exactly a quadratic once
you take logs) and an **additive** kernel for F6 (it forbids interactions between inputs;
with this little data that constraint buys more than the flexibility it gives up).
Second, where Q² is weak the acquisition no longer chooses a location freely: it
maximises EI over a **generated set of local moves** from the incumbent instead of over
the whole box, so every candidate sits beside a real measurement. F4 and F8 keep the
continuous acquisition unchanged. F3 spends its round on a replicate rather than an
optimisation.

**Configuration and rationale, per function.**

| Fn | Surrogate (fitted to) | LOO Q² *(alternatives)* | Acquisition + parameters | Search domain | Predicted | vs best |
|----|----------------------|--------------------------|--------------------------|---------------|-----------|---------|
| 1 | **quadratic trend + GP residual**, on log₁₀\|y\| | **0.734** *(Matérn 0.197, additive −0.338)* | EI, ξ = 0.00, plausibility cap 0.0 | 5 local moves (base step 0.067) | log₁₀\|y\| −2.27 ± 6.29 | above |
| 2 | Matérn 5/2 ARD, raw y | 0.316 *(additive 0.289, quadratic −0.530)* | EI, ξ = 0.02 | 6 local moves (base step 0.019; x1 inert, not stepped) | 0.583 ± 0.046 | below |
| 3 | Matérn 5/2 ARD, raw y | **−0.242** *(additive −0.027, quadratic −0.234)* | none — deliberate replicate | incumbent, inert axes shifted 0.05 | −0.026 ± 0.014 | below |
| 4 | Matérn 5/2 ARD, raw y | **0.967** *(additive 0.978, quadratic 0.962)* | UCB, β = 1.5 *(was 2.5)* | continuous, trust region r = 0.20 | 0.515 ± 0.582 | below |
| 5 | **quadratic trend + GP residual**, on log y | **0.653** *(Matérn 0.190, additive −0.161)* | EI, ξ = 0.01, plausibility cap 8.0 | 14 local moves | log y 7.99 ± 0.01 → ≈2939 | **above** |
| 6 | **additive GP**, raw y | **0.772** *(Matérn 0.358, quadratic 0.583)* | EI, ξ = 0.01 *(was 0.10)* | 12 local moves (x0 inert, not stepped) | −0.546 ± 0.093 | **above** |
| 7 | Matérn 5/2 ARD, raw y | 0.290 *(additive −0.312, quadratic 0.250)* | EI, ξ = 0.01 *(was 0.05)* | 20 local moves (x2 inert, not stepped) | 2.299 ± 0.160 | below |
| 8 | Matérn 5/2 ARD, raw y | **0.991** *(additive 1.000, quadratic 0.995)* | UCB, β = 1.5 *(was 2.0)* | continuous, trust region r = 0.15 *(was 0.30)* | 9.978 ± 0.054 | **above** |

On F4 and F8 the additive kernel scored marginally higher, but the adopted rule is that a
challenger replaces the incumbent model only on a margin of about 0.1 — below that the
difference is cross-validation noise on a few dozen points — so both keep the Matérn.

**Points submitted.**

| Fn | Point | Winning move |
|----|-------|--------------|
| 1 | 0.516951, 0.681526 | x0 −2 steps |
| 2 | 0.682637, 0.926564 | x0 −1 step |
| 3 | 0.949999, 0.548179, 0.859784 | replicate |
| 4 | 0.373537, 0.419038, 0.433148, 0.440012 | UCB argmax |
| 5 | 0.224189, 0.846480, 0.879484, 0.999999 | x3 +1 step |
| 6 | 0.422422, 0.453026, 0.801323, 0.999999, 0.000001 | x1 +2 steps |
| 7 | 0.000001, 0.184614, 0.448347, 0.289155, 0.373715, 0.749975 | x3 +1 step |
| 8 | 0.150001, 0.150001, 0.193946, 0.000001, 0.753935, 0.451055, 0.256022, 0.543085 | UCB argmax |

**The logic, function by function.**

- **F1 — follow the only gradient that exists.** Ranked by magnitude its readings run
  −2.4, −15.1, −39.6, −40.2 … −123.5 in log₁₀\|y\|, climbing steadily as x0 decreases. Raw
  y is numerically zero everywhere, which is why the GP had nothing to fit; on the log
  scale there is a clean steep surface and the quadratic captures it. The chosen move
  continues down x0 from 0.650 to 0.517, holding x1.
- **F2 — a one-dimensional problem, treated as one.** x1's lengthscale is at its ceiling,
  so it is held exactly at the incumbent rather than stepped. Fitted noise (sd ≈ 0.12) is
  larger than the gap between the top readings, so a small step in x0 doubles as a
  near-repeat that tests whether the incumbent was partly luck.
- **F3 — buy information, not a value.** Q² negative and noise larger than the whole
  spread of observations means no refinement is measurable. The influential axis is held
  exactly; the two inert axes move 0.05. Effectively a repeat measurement.
- **F4 — learn the curvature.** Q² = 0.97 earns the model full control. Round 2 moved x2
  by 0.12 and lost 2.8 units, which says the peak is far sharper than the fitted
  lengthscales imply. β lowered and a trust region added so the acquisition refines
  instead of roaming.
- **F5 — one variable, cleanly attributable.** The log-scale quadratic says x3 is still
  rising; it goes to its edge while every other coordinate stays at the known-good
  setting, so whatever returns is attributable to that single change.
- **F6 — test the additivity while exploiting it.** The additive model's own component for
  x1 peaks well above its current value, so x1 moves and the rest hold. Because the model
  assumes no interactions, a single-input move is simultaneously the best exploit and a
  direct test of the assumption. ξ returns to 0.01: the 0.10 setting rested on a fitted
  noise of 0.077 that has since collapsed to the floor.
- **F7 — reverse a wrong call.** x3 was declared inert in week 2 and driven toward zero
  over two rounds while the output fell each time (2.406 → 1.190 → 1.076); the refit now
  ranks its lengthscale among the shortest. This point moves x3 back up from the
  round-1 best.
- **F8 — tighten after the failed widening.** Growing the radius in week 3 produced three
  declining readings. Radius halved, β lowered, and for the first time the proposal's
  predicted mean sits above the incumbent.

**Guardrails added this round (both triggered on the first attempt).** Inert dimensions
are no longer stepped at all: a lengthscale at the ceiling saturates the step size, which
pushed a coordinate onto the boundary — the same failure mode as week 3. And a
plausibility ceiling now filters candidates: F1's quadratic, despite Q² = 0.73, first
proposed a point at which it predicted \|y\| ≈ 10¹², because an indefinite quadratic has no
maximum. Interpolating well does not license extrapolating; the filter enforces that.

**Notable model signals.** The headline is that **constrained models beat flexible ones
under a tight evaluation budget** — additive and quadratic surrogates outscored the full
ARD GP on four functions, sometimes by a factor of several. The second is that **in-sample
fit is worthless as a diagnostic here**: every model interpolates its own data at R² ≈
1.00 while cross-validated Q² ranges from −0.24 to 0.99. Only the second number says
whether a proposal means anything.

---

## Week 3 — Round-3 results (logged 2026-08-11)

**Summary.** No function set a new best this week, and the round has to be read as a correction rather than a loss. Two things dominate it. First, a **submission error**: the point computed for F4 was entered into F5. Both are 4-D so nothing rejected it. The consequence is that F5 spent its trial on a point chosen against a different surface (returning 79.9, rank 9 of 23 — it did at least confirm the central region is poor) and **F4 received no trial at all**, leaving it one round behind the rest. Second, and more important methodologically, **every function where exploration was increased got worse, monotonically**: F6 went −0.650 → −0.725 → −0.851 as ξ was raised, F7 went 2.406 → 1.190 → 1.076, and F8 went 9.874 → 9.867 → 9.682 as the trust region was grown. Three declining points each is no longer noise; it is the dial being pushed past its useful range. The one clear success was **F2**, which returned 0.570 (2nd of 13) after exploration was redirected off the inert axis onto x0 — that change worked exactly as intended. F1's probe returned ~0 again but produced the week's most useful discovery (below). The stance for round 4 therefore **reverses**: with 7 trials left, exploration has already bought the structural information it was going to buy, and the remaining budget is worth more spent refining known basins.

**Results this round.**

| Fn | Acquisition (config) | Realised output | Prev best | New best? |
|----|----------------------|-----------------|-----------|-----------|
| 1 | space-filling probe | 6.5e-41 (~0) | ~0 | no — but see log-magnitude finding |
| 2 | UCB β=1.75 | 0.570 | 0.611 | no (2nd of 13) — strong recovery |
| 3 | EI ξ=0.01 | −0.0546 | −0.0255 | no (6th of 18) |
| 4 | — | **not submitted** | 0.524 | trial misrouted to F5 |
| 5 | *(received F4's point)* | 79.9 | 1089 | no (9th of 23) |
| 6 | EI ξ=0.10 | −0.851 | −0.650 | no (5th of 23) — 3rd decline |
| 7 | EI ξ=0.05 | 1.076 | 2.406 | no (4th of 33) — 3rd decline |
| 8 | UCB β=2.0 + TR r=0.30 | 9.682 | 9.874 | no (3rd of 43) — 3rd decline |

**Changes made for next round.**

- **All functions — reverse the exploration dial and switch to local refinement.** ξ back to 0.01–0.02, β down to 1.5, and a trust region on every function that has a credible incumbent. This is the decision rule from round 1 firing as written: no improvement for two-plus rounds with the declines pointing away from the incumbent means the exploration setting, not the basin, is the problem.
- **F1 — model log|y|, not y.** The single most valuable finding of the week. Ranked by magnitude, F1's readings are not flat at all: log10|y| runs −2.4, −15.1, −39.6, −40.2, … −123.5, and the largest-magnitude readings are spatial neighbours around (0.650, 0.682). On the raw scale everything is indistinguishable from zero, which is why the GP had nothing to fit; on the log-magnitude scale there is a clean, steep, smooth gradient. Search now runs on that surrogate, restricted to a tight box around the peak. Caveat to watch: the peak-magnitude reading is *negative*, so the source region may be a trough rather than a peak — but it is the only region with any dynamic range, so it is where the answer must be.
- **F7 — x3 is NOT inert; stop pinning it to zero.** Week 2's ARD read called x3 inert and the last two rounds drove it toward the boundary (0.214 → 0.039 → ~0) while the output fell (2.406 → 1.190 → 1.076). The refit now puts x3's lengthscale at 0.227, among the shortest. ξ back to 0.01 and the search restricted to a box around the round-1 best.
- **F8 — shrink the trust region to r=0.15.** Growing it was the right *rule* for a plateau but the wrong *diagnosis*: the three readings were declining, not flat. Local refinement now predicts above the incumbent for the first time.
- **F6 — ξ back to 0.01, trust region r=0.15.** The ξ=0.10 rationale rested on a fitted noise of 0.077; with the third point the refit puts F6's noise at the floor (1e-6), so that justification has evaporated.
- **F5 — unchanged config, but re-issue the point it never received.** The trust region remains r=0.2.
- **F4 — resume with UCB β lowered to 1.5 inside a trust region.** It has one extra trial in hand relative to the others; the proposal sits close to the 0.524 peak to learn the curvature the GP is still under-fitting.
- **F3 — spend the round on a near-replicate of the incumbent.** Fitted noise sd (0.126) now exceeds the entire spread of the observed values, so the ranking carries almost no information and any refinement is unmeasurable. Varying only the inert axes gives an effective repeat measurement and pins the noise down before more budget goes in.

**Notable model signals.** The week's cautionary finding is that **the ARD and noise estimates from week 2 were not stable**. F7's x3 flipped from inert to one of its sharpest dimensions, F6's x0 flipped the other way (from most influential to the ARD ceiling), and F6's noise estimate collapsed from 0.077 to the floor — all on the strength of one additional observation each. Structural readings from a dozen-odd points are hypotheses, not facts, and the operational lesson is to stop acting on them by pinning a dimension to a boundary; keep a suspected-inert dimension near the incumbent's value instead, where a wrong call costs nothing.

---

## Week 2 — Round-2 results (logged 2026-08-05)

**Summary.** On the scoreboard this was a quiet week — only **F3** set a new best (−0.0255, now rank 1 of 17) and it did so by a hair. But measured by *information gained* it was the most productive round so far, because refitting the GPs on 12–42 points each made the ARD lengthscales finally readable, and four functions turned out to be **effectively lower-dimensional than their nominal dimension**: F2 is driven almost entirely by x0 (x1's lengthscale saturates), F3 almost entirely by x2 (x0 and x1 both saturate), F7 by x0/x1/x4/x5 (x2 and x3 saturate), and F8 by five of its eight inputs (x3, x4, x7 inert). That collapses the volume we actually need to search and is worth more than a single incremental best. The clearest config win was **F5**: enabling the trust region turned last week's wild corner gamble (371) into 1007.8, the second-best value ever seen and within 7% of the incumbent — the model stopped chasing extrapolated corners. The two apparent "failures", F4 (−2.29) and F7 (1.19), are both explained rather than mysterious: F4's peak is much sharper than the fitted lengthscales imply (a 0.12 move in x2 cost 2.8 units), and F7's trial spent its variation on an inert dimension while making a small move in its sharpest one. Both refits have already absorbed the lesson. The stance for next round stays **exploratory but better-targeted**: with 8 trials left, the gain now comes from exploring the dimensions that actually matter instead of spreading uniformly.

**Results this round.**

| Fn | Acquisition (config) | Realised output | Prev best | New best? |
|----|----------------------|-----------------|-----------|-----------|
| 1 | UCB β=3.0 | −4.5e-117 (~0) | ~0 | no — still no signal |
| 2 | UCB β=2.5 | 0.331 | 0.611 | no (4th of 12) — recovery from R1 |
| 3 | EI ξ=0.01 | **−0.0255** | −0.0348 | **yes (marginal)** |
| 4 | UCB β=2.5 | −2.287 | 0.524 | no (2nd of 32) |
| 5 | EI ξ=0.01 (log) + **TR r=0.2** | 1007.8 | 1089 | no (2nd of 22) — big recovery |
| 6 | EI ξ=0.02 | −0.7245 | −0.650 | no (3rd of 22) |
| 7 | EI ξ=0.02 | 1.190 | 2.406 | no (3rd of 32) |
| 8 | UCB β=2.0 + TR r=0.2 | 9.867 | 9.874 | no (2nd of 42) — plateau |

**Changes made for next round.**

- **F1 — abandon GP-UCB, switch to deliberate space-filling.** After 12 points the surface is still numerically zero everywhere and the GP has nothing to fit, so UCB is just bouncing between unexplored box corners. One genuine clue exists: the two largest-magnitude readings, −0.0036 at (0.650, 0.682) and 7.7e-16 at (0.731, 0.733), are neighbours — everything else is 10^40 times smaller. Plan: probe that neighbourhood once, then maximin-fill the untouched gaps (notably low-x0/low-x1) with the remaining trials.
- **F2 — stop spending trials on x1.** ARD puts x1's lengthscale at the ceiling and x0's at 0.052; the top four points all sit at x0 ∈ [0.67, 0.88] with x1 ranging over the entire interval. The current proposal ([~0, ~1]) is UCB exploring a dimension that does not affect the output. Lower β to ~1.5–2.0 and/or restrict the sweep to the x0 band. This is *not* early exploitation — it is redirecting exploration onto the axis that carries the signal.
- **F6 — raise ξ from 0.02 to ~0.10.** Fitted noise is 0.077 while the gap between the best (−0.650) and the third best (−0.7245) is 0.075. We are chasing differences of about one noise standard deviation, so the leaderboard is not trustworthy and refinements are undetectable. A larger EI margin forces the acquisition to demand an improvement bigger than the measurement error before it treats a point as promising.
- **F7 — raise ξ from 0.02 to ~0.05.** Best achievable EI has fallen to 0.027, i.e. the model no longer expects much. With x2/x3 confirmed inert, the useful exploration is spread in x0/x1 while holding x4 ≈ 0.38 and x5 ≈ 0.75 (its sharpest dimension, lengthscale 0.125).
- **F8 — grow the trust region from r=0.2 to r=0.3.** Two consecutive rounds landing at 9.874 and 9.867 means the interior is a plateau, not a slope; the stall signal calls for growing, not shrinking. Three of eight inputs are inert, so widening is cheap — the extra volume falls almost entirely in the five dimensions that matter.
- **F5 — no change; keep the trust region at r=0.2.** It did exactly its job this week.
- **F4 — no change; keep β=2.5.** Still multimodal, still early, and the acquisition is already doing local work by itself (its proposal sits 0.12 from the best) because uncertainty is naturally highest beside a lone high point. The GP is currently under-fitting the peak's sharpness and needs a second point near it to learn the curvature.
- **F3 — no change, but flag the noise.** Fitted noise (0.0155) is roughly half the entire spread of the top six values, so F3's ranking is partly luck. Worth one replicate at the incumbent later to pin the noise down rather than over-investing.

**Notable model signals.** Effective dimensionality is now the dominant finding: **F2 → ~1-D (x0)**, **F3 → ~1-D (x2)**, **F7 → ~4-D (x0, x1, x4, x5)**, **F8 → ~5-D (x3, x4, x7 inert)**. Noise estimates split the set cleanly: F2 (0.016), F3 (0.016) and F6 (0.077) carry real measurement noise, while F1, F5, F7 and F8 fit at the noise floor (1e-6), i.e. effectively deterministic — worth trusting their raw readings much more than F6's.

---

## Week 1 — Round-1 results (logged 2026-07-30)

**Summary.** This first round's points were proposed from the initial data alone (10–40 points per function). Five of the eight functions set a new best: F4 leapt from −4.03 to **+0.524** (its exploratory UCB found a strong central basin around ~0.41 in every input), F7 rose from 1.365 to **+2.406**, F8 improved to **9.874** inside its trust region, and F6 improved to **−0.650**. The three that did not improve were informative rather than failures: F1 returned ~0 again (its sparse surface still shows no signal, so exploration must continue), F2's high-β corner pick returned the worst value seen (−0.139, confirming that corner is dead), and F5's corner gamble returned 371 versus its incumbent 1089 — the model chasing far corners with huge uncertainty, as expected for its extreme output scale. The guiding decision this week was to stay in the **explore-early phase**: with ~9 trials still remaining, we deliberately avoid closing in on the good basins we've found (especially the multimodal F4), since every evaluated point stays in the GP's memory and those basins can be exploited in the final rounds without being lost now.

**Results this round.**

| Fn | Acquisition (config) | Realised output | Prev best | New best? |
|----|----------------------|-----------------|-----------|-----------|
| 1 | UCB β=3.0 | ~0 (8e-62) | ~0 | no — still no signal |
| 2 | UCB β=2.5 | −0.139 | 0.611 | no — worst so far |
| 3 | EI ξ=0.01 | −0.172 | −0.035 | no — near worst |
| 4 | UCB β=2.5 | **0.524** | −4.03 | **yes (large)** |
| 5 | EI ξ=0.01 (log) | 371.3 | 1089 | no (3rd best) |
| 6 | EI ξ=0.02 | **−0.650** | −0.714 | **yes** |
| 7 | EI ξ=0.02 | **2.406** | 1.365 | **yes (large)** |
| 8 | UCB β=2.0 + TR r=0.2 | **9.874** | 9.598 | **yes** |

**Changes made for next round.**

- **F5 — enable trust region** (`TRUST_REGION=True`, radius 0.2, centred on the best point). It is unimodal, so localising around the current peak stops EI from wasting trials on high-uncertainty corners. *(The only config change this week.)*
- **F2, F4 — no change; keep exploring.** Both multimodal and it is too early to exploit; leave β at 2.5.
- **F8 — no change; stay in the trust region at radius 0.2.** Global search is infeasible in 8-D, so local search is the productive mode. Shrink the radius only once improvement stalls.
- **F1 — no change; keep discovering.** Switch to EI only when a non-zero reading appears.
- **F3, F6, F7 — no change.** EI settings are working; will lower ξ toward 0 in the final rounds.

**Notable model signals.** ARD lengthscales suggest several inputs barely matter: F2 x1, F7 x2, and F8 x3/x4/x7 (making F8 effectively ~5-D). Worth watching as we accumulate data.

---

<!-- ============================================================
TEMPLATE — copy this block above the previous week each time.

## Week N — Round-N results (logged YYYY-MM-DD)

**Summary.** One paragraph: which points were run, which functions improved
and by how much, what the misses tell us, and the overall explore/exploit
stance for this round.

**Results this round.**

| Fn | Acquisition (config) | Realised output | Prev best | New best? |
|----|----------------------|-----------------|-----------|-----------|
| 1 |  |  |  |  |
| ... |  |  |  |  |

**Changes made for next round.**
- Fn X — what changed and why.
- Fn Y — no change; reason.

**Notable model signals.** Anything from ARD lengthscales / uncertainty.
============================================================ -->
