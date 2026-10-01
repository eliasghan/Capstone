# Current state — one card per function

*As of round 11 submission (2026-10-01). Trials used **10 of 13**; F4 has used 9 because its
round-3 trial was misrouted. Regenerate this file after any config change.*

## Read this first: which settings are actually live

Every notebook carries the same CONFIG block, but **`PROPOSER` decides which settings are
used and which are ignored.** Reading a value that isn't live is the easiest way to
misunderstand what a function is doing.

| `PROPOSER` | What runs | Settings that matter | Settings ignored |
|------------|-----------|----------------------|------------------|
| `acquisition` | classic BO: maximise the acquisition over a box | `ACQUISITION`, `BETA` (if UCB) or `XI` (if EI), `TRUST_REGION`, `TR_RADIUS` | `SCORE`, `STEP_FRAC`, `PLAUSIBLE_MAX` |
| `local` | build ~a dozen small moves from the best point, model ranks them | `SCORE`, `XI` (if score=ei) or `BETA` (if score=ucb), `STEP_FRAC`, `INERT_THRESHOLD`, `PLAUSIBLE_MAX` | `ACQUISITION`, `TRUST_REGION`, `TR_RADIUS` |
| `bracket` | step from the best positive reading toward the nearest negative | `BRACKET_ALPHA` | almost everything else |
| `explore` | pure space-filling: the point furthest from every observation | nothing — geometric | everything else |

`SURROGATE`, `TRANSFORM`, `NOISE_BOUNDS` and `LENGTHSCALE_BOUNDS` are live in all three modes.

**Q²** below is the leave-one-out score: 1 is perfect prediction of a point the model never
saw, 0 is no better than always guessing the mean, negative is worse than that. It decides
how much authority the model gets, and it is re-measured every round by the CHECK cell.

---

## F1 — 2-D · best **1.039e-4**

| | |
|---|---|
| Surrogate | **quadratic** trend + GP residual, fitted to **log₁₀\|y\|** |
| Q² | **0.856** (Matérn 0.898 · additive 0.473) |
| Proposer | **bracket**, `BRACKET_ALPHA = 0.15` — fine refinement |
| Acquisition | *not used* |
| Other | `LENGTHSCALE_BOUNDS = (0.01, 0.5)` · `PLAUSIBLE_MAX = 0.0` |
| Best at | 0.583533, 0.681526 |

The source of this function is a **trough**, not a peak: the largest-magnitude reading is
negative, so the maximum sits on the positive lobe just outside it. That lobe was found by a
sign-bracket search which gained roughly twelve orders of magnitude over four rounds — and has
now **converged**. The readings either side of the crossing are nearly equal in size (1.04e-4
positive against 1.40e-4 negative), which places the lobe's peak within about 0.0005 of the
incumbent; bisecting again converges on the crossing itself, where the value passes through
zero. Remaining trials therefore go to space-filling over the parts of the square never
sampled — low odds of a second source, but a better expected value than the one per cent left
in further refinement. Note that the model's prediction at a space-filling point is
meaningless extrapolation; the point is chosen geometrically, not by the model.

## F2 — 2-D · best **0.6291**

| | |
|---|---|
| Surrogate | **additive** GP (no interactions between inputs) |
| Q² | **0.608** (Matérn 0.138 · quadratic −0.634) |
| Proposer | **local**, `SCORE = "ei"`, `XI = 0.02`, `STEP_FRAC = 0.01`, `MIN_STEP = 0.0015` — near-replicates |
| Acquisition | *not used* |
| Other | `INERT_THRESHOLD = 5.0` |
| Best at | 0.712637, 0.926564 |
| Lengthscales | 0.059 · 10.0 |

Genuinely one-dimensional, and now confirmed rather than assumed: a single-variable test
moved the second input by 0.35 while holding everything else fixed and changed the output by
0.003. That question is closed and the proposer no longer spends candidates on it. The same
test showed the fitted noise is essentially zero, so the small differences between readings
near the peak are **real** — and they put the peak in a window about 0.01 wide, which is why
the step size was cut to about a fifth and the step floor lowered below its old hard-coded
0.02. Q² rose from 0.42 to 0.59 as a result.

## F3 — 3-D · best **−0.02524**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.059** (additive 0.132 · quadratic −0.045) |
| Proposer | **local**, `SCORE = "mean"`, `STEP_FRAC = 0.03`, `MIN_STEP = 0.005` |
| Acquisition | *not used* |
| Other | `NOISE_BOUNDS = (1e-10, 1e-4)` · `INERT_THRESHOLD = 1.0` |
| Best at | 0.999999, 0.580426, 0.859784 |
| Lengthscales | 10.0 · 1.505 · 0.084 |

The weakest model in the project — barely better than guessing the average, so it is not
allowed to choose a location, only to rank steps. Two corrections shaped it. A deliberate
replicate showed the noise is about sixty times smaller than the model had been fitting, so
`NOISE_BOUNDS` is now pinned near the measured value; before that, real structure was being
absorbed into a noise term. And ranking switched from expected improvement to the plain
predicted mean, because EI had collapsed to near-zero everywhere and was discarding a
candidate predicted *above* the incumbent purely for being too certain. Two optima are now
bracketed by readings on either side: the third input near 0.86, the second near 0.598. Steps
are deliberately small — when the refit briefly gave the second input a large step, the
proposal landed outside that bracket and predicted a positive value better than anything ever
observed, on a Q² of 0.03. Small steps keep an unreliable model inside the region its own data
supports.

## F4 — 4-D · best **0.5895**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.984** (additive 0.985 · quadratic 0.958) |
| Proposer | **local**, `SCORE = "mean"`, `STEP_FRAC = 0.005`, `MIN_STEP = 0.005` |
| Acquisition | *not used* |
| Best at | 0.407583, 0.411177, 0.360748, 0.432592 |
| Lengthscales | 1.459 · 1.326 · 1.240 · 1.325 |

**The instructive failure of the project.** It scores 0.98 on cross-validation and is still
the worst-behaved function here, because that score is earned on the thirty spread-out initial
points and says nothing about the peak. Near the optimum the surface moves about eighteen
units per unit of distance while the fitted lengthscales say 1.3 — a move of 0.024 cost 0.43,
while 0.012 the round before had gained 0.05. Tightening the kernel does not fix it (Q² falls
from 0.98 to 0.85), because the smooth background is real too: this is a narrow spike sitting
on a smooth surface, and one lengthscale cannot describe both. So the model was taken off
location-choosing entirely and now only ranks steps small enough that a wrong ranking is
cheap. An exploration probe was run in round 7 by releasing the trust region — with the whole
space available the acquisition returned to the same neighbourhood, so the basin is the best
it knows of. Six attempts failed to beat the very first trial; the seventh, with the step size
finally set from the evidence rather than the lengthscales, **beat it by 0.066**.

## F5 — 4-D · best **4643.17**

| | |
|---|---|
| Surrogate | **quadratic** trend + GP residual, fitted to **log y** |
| Q² | **0.834** (Matérn 0.547 · additive 0.565) |
| Proposer | **local**, `SCORE = "mean"`, `STEP_FRAC = 0.02`, one explicit probe queued |
| Acquisition | *not used* |
| Other | `PLAUSIBLE_MAX = 10.0` |
| Best at | 0.480000, 0.999999, 0.999999, 0.999999 |
| Lengthscales | 1.901 · 0.592 · 0.861 · 0.760 |

Best-performing function of the project, up more than fourfold from its starting value. Its
output spans four orders of magnitude, which is why it is modelled on a log scale — and on
that scale a peak of this shape is close to an exact quadratic, which is why the polynomial
beats the GP here. Three of its four inputs now sit on the upper boundary, so **the first
input is the only axis still free to move**, and the step size was cut so candidates land
where the model actually rates them well rather than overshooting. `PLAUSIBLE_MAX` guards
against the polynomial extrapolating absurdly — **it must be raised whenever the best value
grows**, or it silently filters out every candidate better than the incumbent.

## F6 — 5-D · best **−0.2497**

| | |
|---|---|
| Surrogate | **additive** GP (no interactions between inputs) |
| Q² | **0.884** (quadratic 0.810 · Matérn 0.796) |
| Proposer | **local**, `SCORE = "mean"`, `STEP_FRAC = 0.01` |
| Acquisition | *not used* |
| Best at | 0.422422, 0.453026, 0.694051, 0.794604, 0.000001 |
| Lengthscales | 1.045 · 1.459 · 2.924 · 2.059 · 2.997 |

The additive kernel more than doubled this function's predictive score by forbidding
interactions — a strong assumption the data could not otherwise afford. Its lengthscales are
long, which makes steps coarse: `STEP_FRAC` had to be cut to about an eighth of its original
value before the largest available move actually shrank, because the step was saturating
against its internal cap and the model kept selecting the same large jump. That jump size
was also its one badly mispredicted trial.

## F7 — 6-D · best **2.5758**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.851** (additive 0.755 · quadratic 0.609) |
| Proposer | **acquisition** |
| Acquisition | **UCB**, `BETA = 0.0` (pure predicted mean), trust region `r = 0.20` |
| Best at | 0.000001, 0.162206, 0.510665, 0.268312, 0.371891, 0.731059 |
| Lengthscales | 0.668 · 0.488 · 10.0 · 0.298 · 0.257 · 0.601 |

Promoted back to full acquisition control in round 6 when its score jumped from 0.29 to 0.73.
This function has now produced a **false "irrelevant" verdict twice**. First its fourth input,
declared inert and driven toward zero over two rounds while the output fell each time. Then
its third input, which readings at 0.25, 0.45 and 0.65 show has a clear peak — 2.05, 2.48,
2.37 — while its lengthscale sat pinned at the ceiling. Bringing that ceiling down from 10.0
to 0.8 leaves every lengthscale fitted rather than pinned and raised Q² from 0.82 to 0.87.
The lesson: a saturated lengthscale means the model cannot tell weak influence from none at
the ceiling it was given, not that the input does nothing. Promotion and demotion both follow
the score — the tier is a measurement, not a standing judgement.

## F8 — 8-D · best **9.9731**

| | |
|---|---|
| Surrogate | **Matérn 5/2** ARD |
| Q² | **0.994** (additive 1.000 · quadratic 0.999) |
| Proposer | **acquisition** |
| Acquisition | **UCB**, `BETA = 0.0` (pure predicted mean), trust region `r = 0.15` |
| Best at | 0.116261, 0.144649, 0.165854, 0.000001, 0.857440, 0.440650, 0.215491, 0.517384 |
| Lengthscales | 3.344 · 4.924 · 2.547 · 6.855 · 10.0 · 4.697 · 3.395 · 10.0 |

The best-modelled function by cross-validation and, revealingly, **not** the best behaved.
Every prediction it has ever made came in high — six from six, averaging about 0.09 — which
is bias rather than noise, and its score of 0.99 cannot detect it because cross-validation
tests interpolation between points the model has, not extrapolation to points it does not.
Seven trials, seven over-predictions. Halving the exploration weight did not fix it, because
the bias is in the model rather than the acquisition, so the weight is now zero — the proposal
is simply the model's predicted best. The trust region was widened for one round as a probe
for a better basin; it proposed a point 0.46 away and returned below the incumbent, so the
answer is no and the region has been narrowed back. This function looks close to its
practical ceiling.

---

## Shared settings

`RANDOM_STATE = 0` and `TRIAL_BUDGET = 13` everywhere. `LENGTHSCALE_BOUNDS = (0.01, 10.0)`
everywhere except F1 `(0.01, 0.5)` and F7 `(0.01, 0.8)`. `MIN_STEP` is the floor on the local
step size — 0.02 by default, lowered on F2, F3 and F4 where the local structure is narrower
than that. Every proposed coordinate is
clamped strictly inside the unit interval and printed to six decimals, so a value never reads
as exactly 0 or 1.

## Standing rules

**A saturated lengthscale is not evidence of irrelevance** — it means the model cannot tell
weak influence from none at the ceiling it was given; lowering the ceiling is the test, and
acting on the raw verdict has cost trials twice. **A cross-validation score is scoped to the
region the data covers** — F4 scores 0.98 while over-smoothing its own peak more than
tenfold. A dimension whose lengthscale sits at its ceiling is never stepped onto a boundary — moving
it measures nothing and the saturated step size pushes the coordinate to the wall. A
challenger surrogate replaces the incumbent only on a clear margin of about 0.1, since below
that the difference is cross-validation noise. Guardrails set against an old scale must be
re-checked as the best value grows. And after any config change, confirm the *output* moved,
not just the setting — a change that alters nothing is worse than no change, because it looks
like a fix.

## ENDGAME (round 10 onward)

Every function is now on **pure exploitation** — ranking on the predicted mean, exploration
weights at zero. Expected improvement and optimism bonuses exist to buy information, and with
only a few submissions left there is no time to spend it. Six of eight now propose points their own
models rate below the incumbent, which is what running out of local improvement looks like.
The three places real value remains: **F5's probe above its highest reading**, **F2's repeated
draws against its measurement noise** (the score is the best value observed, so each draw is an
independent chance at a high reading), and **F8**, still climbing with the best calibration here.

## Plan for the remaining rounds

Rounds 7–10 keep room for informative moves: F1's bracket, F2's single-variable test, F8's
wider basin probe. Rounds 11–13 go to pure exploitation — exploration weights to zero,
smallest trust regions, and any function whose model still cannot predict spends its last
trials confirming its best reading rather than hunting new ones.
