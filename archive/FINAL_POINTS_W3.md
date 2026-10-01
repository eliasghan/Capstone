# Round 3 — FINAL points to submit (Week 3)

Authoritative list. Generated from `initial_inputs/outputs.npy` + `new_trials.csv`
(2 rows each) with the Week-3 configs now in each notebook. If a local re-run of
the RECOMMEND cell prints something slightly different, **submit this list** — the
difference comes from the GP hyper-parameter fit landing on a different local
optimum on a different scikit-learn / SciPy build, not from different data.

| Fn | Point to submit |
|----|-----------------|
| F1 | `0.812000, 0.784000` |
| F2 | `0.689233, 0.000001` |
| F3 | `0.999999, 0.999999, 0.398940` |
| F4 | `0.354329, 0.422401, 0.453533, 0.446104` |
| F5 | `0.024189, 0.999999, 0.999999, 0.999999` |
| F6 | `0.477446, 0.000001, 0.999999, 0.721227, 0.000001` |
| F7 | `0.000001, 0.068460, 0.298557, 0.000001, 0.383810, 0.745710` |
| F8 | `0.000001, 0.000001, 0.102176, 0.000001, 0.903935, 0.901055, 0.000001, 0.393085` |

## Rule / prediction for each

| Fn | Rule used | Predicted output | Note |
|----|-----------|------------------|------|
| F1 | space-filling, probe queue | ~0 ± 7e-4 | GP disabled: no signal yet |
| F2 | UCB β=1.75 | 0.6135 ± 0.0566 | x1 inert — variation now spent on x0 |
| F3 | EI ξ=0.01 | −0.0448 ± 0.0542 | only x2 matters |
| F4 | UCB β=2.5 | 0.325 ± 0.675 | second point near the 0.524 peak, to learn curvature |
| F5 | EI ξ=0.01 (log) + TR r=0.2 | ≈1044 | inside the trust region |
| F6 | EI ξ=0.10 | −0.609 ± 0.231 | ξ now exceeds the fitted noise (0.077) |
| F7 | EI ξ=0.05 | 2.367 ± 0.126 | x2/x3 inert; x5 held near its best |
| F8 | UCB β=2.0 + TR r=0.30 | 9.814 ± 0.187 | radius grown after the plateau |

## Reproducibility check performed

- Device files vs. the copies used here: `bbo_toolkit.py`, all 16 `.npy` files and
  all 8 `new_trials.csv` files are **byte-identical** (md5 match).
- Notebook configs on the device carry the Week-3 values (F1 `SPACE_FILLING=True`,
  F2 `BETA=1.75`, F6 `XI=0.10`, F7 `XI=0.05`, F8 `TR_RADIUS=0.30`).
- Re-fitting every function under GP seeds {0, 1, 2, 3, 7}: F1, F2, F4, F5, F6, F8
  give **identical** proposals; F7 moves only in the 4th decimal; **F3** is the one
  fragile case — its second lengthscale can settle at the ARD ceiling or at ~1.4,
  which moves x2 between 0.3989 and 0.4067. Both are the same gap-filling choice
  and either is acceptable; use 0.398940 for consistency with the log.
