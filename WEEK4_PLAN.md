# Plan — how the Week 4 points get chosen

The diagnostics changed what this plan should be. Previously every function was
treated the same way: fit a GP, maximise an acquisition, submit the answer. The
leave-one-out check says that is only justified on two of the eight. So the method
is now chosen per function, by evidence, rather than applied uniformly.

## Step 0 — the standing checks (before anything else)

- Confirm each `new_trials.csv` has the expected number of rows and that the round-3
  value landed in the **right function**. F4 and F5 are both 4-D and were swapped
  last round; that check happens first, every round, from now on.
- Confirm every coordinate is strictly inside (0, 1), formatted to 6 decimals.
- Confirm the notebook configs on disk match the configs the proposal was computed
  from.

## Step 1 — tier every function by how much the surrogate is worth

Leave-one-out Q² is the deciding number: the fraction of variance the model predicts
for a point it has *not* seen. This is recomputed each round, so a function can move
tier as data accumulates.

| Tier | Test | Functions now | What the model is allowed to decide |
|------|------|---------------|--------------------------------------|
| **A — trust it** | Q² > 0.7 | F4 (0.97), F8 (0.99) | everything: the acquisition picks the point |
| **B — use it, don't obey it** | 0 < Q² ≤ 0.7 | F1, F2, F5, F6, F7 | only ranking of a short, hand-built candidate list |
| **C — ignore it** | Q² ≤ 0 | F3 (−0.24) | nothing; the point is chosen by design, not by model |

## Step 2 — derive the candidate point, by tier

**Tier A — acquisition inside a tight trust region.** Small exploration margin,
trust region around the incumbent sized to the shortest ARD lengthscale. Accept the
proposal only if its predicted mean exceeds the current best; if it does not, shrink
the region and re-derive. This is the classic loop and it has earned the right to run
unsupervised on these two.

**Tier B — local pattern search, surrogate as referee.** Build a small candidate set
by stepping the incumbent one coordinate at a time, up and down, by a step sized from
that dimension's lengthscale (roughly a third of it). Add two or three composite moves
along the direction from the second-best point to the best. Score every candidate with
the surrogate and take the highest, subject to the acceptance checks below. The
guarantee here is structural rather than statistical: every candidate sits near a
value we have actually measured, so a bad round costs a little, not a lot — which is
exactly the property a weak model cannot provide on its own.

**Tier C — spend the round on measurement, not on optimisation.** A near-replicate of
the incumbent, varying only the dimensions the model considers inert. That returns an
effective repeat reading and pins down the noise. Until the noise is known to be
smaller than the differences being chased, no refinement on F3 is detectable and any
"optimisation" there is theatre.

## Step 3 — acceptance checks, applied to every proposal before it is issued

1. **Predicted mean versus incumbent.** If the model predicts below the current best,
   say so explicitly and justify the point on information grounds instead.
2. **Distance to the nearest observation.** A proposal far from all data is
   extrapolation. Allowed in Tier A, flagged in Tier B, disallowed in Tier C.
3. **No boundary pinning of a suspected-inert dimension.** Hold it at the incumbent's
   value instead. This rule exists because a dimension declared inert in round 2 was
   driven to zero over two rounds while the output fell each time, and the refit later
   ranked it among the sharpest.
4. **No exploration increase against a declining run.** Three consecutive declines on
   a function means the last change pushed the wrong way; the response is to tighten,
   never to widen.

## Step 4 — issue, log, submit

Produce one table of eight points with the rule, predicted value and distance to the
incumbent for each. Write the round into `WEEKLY_LOG.md` at the same time, not
afterwards — the log is the defensible record of *why*, and it is worth marks
independently of the values obtained.

## Step 5 — after the outputs come back

Refit, recompute Q² for all eight, and re-tier. A function that climbs into Tier A
gets handed back to the acquisition; one that falls out of it loses that privilege.
Two more rounds of this, then the endgame.

## Budget and the endgame

Seven trials remain on every function except F4, which has eight. The plan is to run
this tiered procedure for rounds 4 and 5, then switch the final two rounds to pure
exploitation everywhere: exploration margin to zero, smallest trust region, best
point the model can name. Functions still in Tier C at that stage get their remaining
trials spent as replicates of their best point rather than on new locations, since a
noisy leaderboard is won by confirming a good reading, not by finding another
uncertain one.

## Open decision

Tier B needs a pattern-search proposer that does not exist in `bbo_toolkit.py` yet.
It is about thirty lines and would slot in beside `propose_next_point`. The
alternative is to keep using the acquisition for Tier B and simply constrain it
harder, which is weaker but requires no new code.
