# Current state — one card per function

*As of round 12 submission (2026-10-05). Trials used **11 of 13**; F4 has used 10 because its
round-3 trial was misrouted. Regenerate this file after any config change.*

## Read this first: which settings are actually live

Every notebook carries the same CONFIG block, but **`PROPOSER` decides which settings are
used and which are ignored.** Reading a value that isn't live is the easiest way to
misunderstand what a function is doing. A non-empty `PROBE_QUEUE` overrides everything below it.

| `PROPOSER` | What runs | Settings that matter | Settings ignored |
|------------|-----------|----------------------|------------------|
| *(any, with `PROBE_QUEUE` set)* | the queued point is submitted as-is | `PROBE_QUEUE` only | everything else |
| `acquisition` | classic BO: maximise the acquisition over a box | `ACQUISITION`, `BETA` (if UCB) or `XI` (if EI), `TRUST_REGION`, `TR_RADIUS` | `SCORE`, `STEP_FRAC`, `PLAUSIBLE_MAX` |
| `local` | build ~a dozen small moves from the best point, model ranks them | `SCORE`, `XI` (if score=ei) or `BETA` (if score=ucb), `STEP_FRAC`, `MIN_STEP`, `INERT_THRESHOLD`, `PLAUSIBLE_MAX` | `ACQUISITION`, `TRUST_REGION`, `TR_RADIUS` |
| `bracket` | step from the best positive reading toward the nearest negative | `BRACKET_ALPHA` | almost everything else |
| `explore` | pure space-filling: the point furthest from every observation | nothing — geometric | everything else |

`SURROGATE`, `TRANSFORM`, `NOISE_BOUNDS` and `LENGTHSCALE_BOUNDS` are live in all modes.

**Q²** below is the leave-one-out score: 1 is perfect prediction of a point the model never
saw, 0 is no better than always guessing the mean, negative is worse than that. It decides
how much authority the model gets, and it is re-measured every round by the CHECK cell.

**All eight are on probes or minimum-size steps for the last two rounds.** Six of the eight
round-12 proposals are explicit probes, because in every one of those cases the structure the
data has already bracketed is finer than the smallest step the proposer can take, or the model's
local gradient has the wrong sign against a direct measurement. That is not a loss of faith in
the method; it is what the method says to do when cross-validation certifies interpolation and
the search has moved somewhere only direct readings can speak to.

---

## F1 — 2-D · best **1.0395e-4**

| | |
|---|---|
| Surrogate | **quadratic** trend + GP residual, fitted to **log₁₀\|y\|** |
| Q² | **0.910** (Matérn 0.949 · additive 0.074) |
| Proposer | `bracket`, `BRACKET_ALPHA = 0.15` — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Other | `LENGTHSCALE_BOUNDS = (0.01, 0.5)` · `PLAUSIBLE_MAX = 0.0` · `MIN_STEP = 0.02` |
| Best at | 0.583533, 0.681526 |
| Lengthscales | 0.5 · 0.5 — **both saturated at the ceiling** |

The source is a **trough**, not a peak: the largest-magnitude reading is negative, so the
maximum sits on the positive lobe just outside it. A sign-bracket search found that lobe and
gained roughly twelve orders of magnitude over four rounds. It has now **converged**: three
readings sit on the peak — 0.581 → 1.020e-4, 0.583533 → 1.040e-4, 0.584781 → 0.974e-4 — and the
parabola through them puts the vertex at 0.582509, worth about 1.6 per cent. That is this
round's probe, and the bracket cannot reach it because the bracket's own next step is already in
the data. Both lengthscales sit at their ceiling, so the model is as smooth as it is allowed to
be and cannot resolve structure at the 0.001 scale this peak lives on — which is exactly why the
three-point parabola is better evidence here than the surrogate.

Note that the second input has **never been varied on the lobe**: every reading on it inherited
0.681526 from the round-4 point that found it. That is the one unexamined question left on this
function, and with the lobe this thin in the first input, a step off the ridge probably falls by
orders of magnitude — which is why the near-certain 1.6 per cent came first.

A display defect, recorded rather than fixed: on this function only, the proposal block's
"distance to it" and "below the incumbent" lines are computed against the best point in *fit*
space, which for a magnitude transform is the large negative trough reading rather than the best
true value printed two lines above. The proposal itself is unaffected.

## F2 — 2-D · best **0.6291**

| | |
|---|---|
| Surrogate | **additive** GP (no interactions between inputs) |
| Q² | **0.667** (Matérn 0.189 · quadratic −0.656) |
| Proposer | `local`, `SCORE = "ei"`, `XI = 0.02`, `STEP_FRAC = 0.01`, `MIN_STEP = 0.0015` — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Other | `INERT_THRESHOLD = 5.0` |
| Best at | 0.712637, 0.926564 |
| Lengthscales | 0.073 · 10.0 |

Genuinely one-dimensional, and confirmed rather than assumed: a single-variable test moved the
second input by 0.35 while holding everything else fixed and changed the output by 0.003.
**The noise is larger than we thought.** Seven readings now sit inside a window 0.009 wide and
span 0.089, standard deviation 0.036 — half again the 0.024 previously assumed. Against a
best-observed score that is *good*: a fresh draw at the peak clears the incumbent about one time
in five, and about one time in three across two rounds, which beats anything else available here.
This round's probe takes that draw by moving the **inert** second input 0.10 rather than
jittering the first — to the function it is the same location, to the record a distinct point,
and it avoids pretending a 0.0015 move in the first input is safe when the readings cannot tell
signal from noise at that scale. The model's own proposal pushed the inert axis to the boundary
and predicted below the incumbent.

## F3 — 3-D · best **−0.025235**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.113** (additive 0.082 · quadratic 0.076) |
| Proposer | `local`, `SCORE = "mean"`, `STEP_FRAC = 0.03`, `MIN_STEP = 0.005` — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Other | `NOISE_BOUNDS = (1e-10, 1e-4)` · `INERT_THRESHOLD = 1.0` |
| Best at | 0.999999, 0.580426, 0.859784 |
| Lengthscales | 5.073 · 0.277 · 0.059 |

The weakest model in the project — barely better than guessing the average, so it is not
allowed to choose a location, only to rank steps. Two corrections shaped it: a deliberate
replicate showed the noise was about sixty times smaller than the model had been fitting, so
`NOISE_BOUNDS` is pinned near the measured value; and ranking switched from expected improvement
to the plain predicted mean, because EI had collapsed to near-zero everywhere and was discarding
a candidate predicted *above* the incumbent purely for being too certain. Both free inputs are
now **bracketed on both sides**: the second from 0.561/0.580/0.598 and the third from
0.855/0.860/0.865. This round's probe sets both to their parabola vertices at once — two
interpolations inside measured brackets, which is the limit of what a model scoring 0.11 should
be trusted with, and more than the proposer can do, since it moves one axis per round.

## F4 — 4-D · best **0.5958135**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.980** (additive 0.972 · quadratic 0.955) |
| Proposer | `local`, `SCORE = "mean"`, `STEP_FRAC = 0.005`, **`MIN_STEP = 0.0005`** — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Best at | 0.407583, 0.421177, 0.360748, 0.432592 |
| Lengthscales | 1.34 · 0.934 · 0.956 · 1.116 |

**The instructive failure of the project.** It scores 0.98 on cross-validation and is still the
worst-behaved function here, because that score is earned on the thirty spread-out initial points
and says nothing about the peak. Near the optimum the surface moves about eighteen units per unit
of distance while the fitted lengthscales say about 1.3. Tightening the kernel does not fix it
(Q² falls from 0.98 to 0.85), because the smooth background is real too: this is a narrow spike
on a smooth surface and one lengthscale cannot describe both. So the model only ranks steps.

This round it set a new best, and in doing so drew a bracket **0.0015 wide** around its own peak
in the second input: 0.411177 → 0.58953, 0.421177 → 0.59581, 0.422760 → 0.58916. The step floor
of 0.005 could not fit inside that, so the proposer asked for +0.01 and valued it at 0.6986 — in
a direction where a reading 0.0016 away has already fallen. `MIN_STEP` is therefore cut tenfold
to 0.0005, and this round's probe goes to the parabola vertex at 0.416930, worth about +0.0075.
Same lesson as week 8, one order of magnitude further down: **a step floor coarser than the
structure makes every automatic proposal overshoot.** Its third input is bracketed just as
tightly (0.347/0.361/0.373); its first and fourth have never been varied in isolation at the
incumbent, which is where its third remaining trial could go.

## F5 — 4-D · best **4998.33**

| | |
|---|---|
| Surrogate | **quadratic** trend + GP residual, fitted to **log y** |
| Q² | **0.859** (additive 0.607 · Matérn 0.574) |
| Proposer | `local`, `SCORE = "mean"`, `STEP_FRAC = 0.02` — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Other | `PLAUSIBLE_MAX = 10.0` |
| Best at | 0.620000, 0.999999, 0.999999, 0.999999 |
| Lengthscales | 3.562 · 0.827 · 1.07 · 0.881 |

Best-performing function of the project, now up more than fourfold from its starting value, and
**the only one where a large gain is still plausible**. Three of its four inputs sit on the upper
boundary, so the first is the only axis still free. Five readings along it now run 4451.7,
4478.9, 4554.8, 4643.2, 4998.3 — monotone, with a log-slope that **doubles every 0.097 of
travel** (0.070, 0.164, 0.292, 0.526). Integrating that growth puts the far corner near 30000.
This round's probe is therefore the **full corner**, all four inputs at the boundary.

The surrogate predicts 770 there and should be ignored on this one point: it is a quadratic on a
log scale, so past its own vertex it is structurally obliged to predict a fall, and its
prediction at the corner is a property of the model family rather than evidence about the
function. The same model predicted a peak below the incumbent last round and was wrong by 355.
If the corner comes back low, the peak is bracketed in (0.62, 1.0) and the final trial bisects.

`PLAUSIBLE_MAX` guards against the polynomial extrapolating absurdly — **it must be raised
whenever the best value grows**, or it silently filters out every candidate better than the
incumbent. At 4998 the incumbent's log-value is 8.52, so the ceiling of 10.0 still has headroom;
if the corner returns anything above about 22000 it must be raised again.

## F6 — 5-D · best **−0.249746**

| | |
|---|---|
| Surrogate | **additive** GP (no interactions between inputs) |
| Q² | **0.899** (quadratic 0.873 · Matérn 0.727) |
| Proposer | `local`, `SCORE = "mean"`, `STEP_FRAC = 0.01` — **overridden this round by `PROBE_QUEUE`** |
| Acquisition | *not used* |
| Best at | 0.422422, 0.453026, 0.694051, 0.794604, 0.000001 |
| Lengthscales | 2.437 · 0.665 · 0.54 · 1.336 · 0.712 |

The additive kernel more than doubled this function's predictive score by forbidding
interactions — a strong assumption the data could not otherwise afford. **Its model now has the
sign of its local gradient wrong, exactly as F5's did.** Holding everything else fixed, the
second input gives −0.27570 at 0.413026 against −0.24975 at 0.453026: improving as it *rises*,
at 0.65 per unit. The surrogate, scoring 0.899, wants to move it *down*. An older configuration
says the same thing across a much wider span (−0.64991 at 0.143514 against −0.49840 at 0.453026),
so two independent slices agree and the model is alone — and nothing above 0.453026 has ever been
measured. The fourth input has its own weaker measured gradient (−0.25519 at 0.834604 against
−0.24975 at 0.794604, improving as it falls, 0.14 per unit). This round's probe moves both along
their own gradients, each by 0.04, the same size as the step that measured it. Moving two axes at
once costs interpretability — a fall will not say which one caused it — and that is the price of
having two rounds rather than five.

The third input is bracketed (0.567/0.694/0.801) and the fifth has sat on the lower boundary
throughout.

## F7 — 6-D · best **2.591659**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.908** — its best yet (additive 0.668 · quadratic 0.745) |
| Proposer | **acquisition** |
| Acquisition | **UCB**, `BETA = 0.0` (pure predicted mean), trust region **`r = 0.03`** |
| Other | `LENGTHSCALE_BOUNDS = (0.01, 0.8)` |
| Best at | 0.000001, 0.159429, 0.511469, 0.262764, 0.369872, 0.728119 |
| Lengthscales | 0.558 · 0.64 · 0.613 · 0.215 · 0.286 · 0.8 |

Promoted back to full acquisition control in round 6 when its score jumped from 0.29 to 0.73,
and it has improved in two of the last three rounds. This function has produced a **false
"irrelevant" verdict twice** — first its fourth input, declared inert and driven toward zero over
two rounds while the output fell each time; then its third, which readings at 0.25, 0.45 and 0.65
show has a clear peak while its lengthscale sat pinned at the ceiling. Bringing that ceiling down
from 10.0 to 0.8 left every lengthscale fitted rather than pinned. The lesson: **a saturated
lengthscale means the model cannot tell weak influence from none at the ceiling it was given**,
not that the input does nothing.

The trust region is narrowed from 0.20 to 0.03 this round. That is the endgame plan — smallest
trust regions — and here it is also the line between interpolation and extrapolation: at 0.20 the
proposal moved the sixth input 0.094, past a reading that came back lower, while at 0.03 every
coordinate stays inside the span the local readings already cover. The predicted gain falls only
from 2.662 to 2.645. Given this function's record, it buys its freedom one round at a time.

## F8 — 8-D · best **9.9730753**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.995** (additive 1.000 · quadratic 0.999) |
| Proposer | **acquisition** |
| Acquisition | **UCB**, `BETA = 0.0` (pure predicted mean), trust region `r = 0.15` |
| Best at | 0.109875, 0.159028, 0.146049, 0.000001, 0.870966, 0.476197, 0.211811, 0.589001 |
| Lengthscales | 4.036 · 5.811 · 3.189 · 7.57 · 9.297 · 5.825 · 4.047 · 10.0 |

The best-modelled function by cross-validation and, revealingly, **not** the best behaved. For
seven consecutive rounds every prediction came in high, averaging about 0.09 — bias rather than
noise, which a score of 0.99 cannot detect because cross-validation tests interpolation between
points the model has, not extrapolation to points it does not. Setting the exploration weight to
zero fixed the calibration; halving it had not, because the bias was in the model rather than the
acquisition. The trust region was widened for one round as a probe for a better basin; it
proposed a point 0.46 away and returned below the incumbent, so the answer was no.

**This function is converged.** Its last four readings sit inside 0.016 of each other, its
proposal predicts the incumbent's own value, and that proposal is unchanged at every
trust-region radius tested from 0.15 down to 0.03. Nothing is changed and its last two trials
are free lottery tickets near the best point.

---

## Shared settings

`RANDOM_STATE = 0` and `TRIAL_BUDGET = 13` everywhere. `LENGTHSCALE_BOUNDS = (0.01, 10.0)`
everywhere except F1 `(0.01, 0.5)` and F7 `(0.01, 0.8)`. `MIN_STEP` is the floor on the local
step size — 0.02 by default, lowered on F2 (0.0015), F3 (0.005) and F4 (0.0005) where the local
structure is narrower than that. Every proposed coordinate is clamped strictly inside the unit
interval and printed to six decimals, so a value never reads as exactly 0 or 1. `PROBE_QUEUE` is
served before any proposer and is skipped automatically once its point is within 1e-3 of an
existing observation, so a spent probe cannot be resubmitted — but it should still be cleared by
hand each round, because a stale queue silently suppresses the proposer.

## Standing rules

**A saturated lengthscale is not evidence of irrelevance** — it means the model cannot tell weak
influence from none at the ceiling it was given; lowering the ceiling is the test, and acting on
the raw verdict has cost trials twice. **A cross-validation score is scoped to the region the
data covers** — F4 scores 0.98 while over-smoothing its own peak more than tenfold. **A step
floor coarser than the structure makes every proposal overshoot** — F4 twice, two orders of
magnitude apart. **When a model's local gradient contradicts a direct measurement taken with
everything else held fixed, the measurement wins** — F5 twice, F6 now; both F5 overrides set
records. A dimension whose lengthscale sits at its ceiling is never stepped onto a boundary.
A challenger surrogate replaces the incumbent only on a clear margin of about 0.1, since below
that the difference is cross-validation noise. Guardrails set against an old scale must be
re-checked as the best value grows. And after any config change, confirm the *output* moved, not
just the setting — a change that alters nothing is worse than no change, because it looks like a
fix.

## ENDGAME (round 10 onward)

Every function is on **pure exploitation** — ranking on the predicted mean, exploration weights
at zero, smallest trust regions. Expected improvement and optimism bonuses exist to buy
information, and with two submissions left there is no round in which to spend it.

Where value actually remains, in order: **F5's corner**, which is the only place a large gain is
still plausible and whose two possible outcomes both leave a well-defined final move; **F2's
second draw** against a measurement noise of 0.036, worth about one chance in five per draw;
and small, well-bracketed refinements on **F1, F3, F4 and F7**, each a few thousandths wide.
**F8 is finished.**

## Plan for the final round

Decide F5 first, because its outcome is the only one that changes what the others should do —
if the corner pays, nothing else matters much; if it does not, the final trial bisects (0.62, 1.0).
F2 takes its second draw regardless. F4 has three trials rather than two and can afford one on
its first or fourth input, neither of which has ever been varied in isolation at the incumbent.
F1, F3 and F7 refine inside their brackets. F8 submits a micro-step near its best and is done.
