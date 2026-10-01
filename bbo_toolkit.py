"""
bbo_toolkit.py
==============
Reusable Bayesian-Optimisation building blocks for the 8-function capstone.

Three core pieces, each written to work UNCHANGED on every one of the 8 functions
(they only differ in dimensionality and output scale, which are all handled by
arguments rather than hard-coded):

    fit_gp(X, y, ...)                    -> fit a Gaussian-Process surrogate
    expected_improvement(X, gp, ...)     -> EI acquisition  (exploration via `xi`)
    upper_confidence_bound(X, gp, ...)   -> UCB acquisition (exploration via `beta`)

plus one convenience helper that the two acquisitions need in order to be useful:

    propose_next_point(gp, dim, acquisition, ...) -> the next x to submit

Everything is maximisation (all 8 functions are framed as "maximise"), and every
input lives in the unit hypercube [0, 1]^d, so the acquisition optimiser searches
that box directly.

Dependencies: numpy, scipy, scikit-learn.
    pip install numpy scipy scikit-learn
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (
    Matern, ConstantKernel, WhiteKernel,
)


# =====================================================================
# 1) GP FITTING
# =====================================================================
def fit_gp(
    X,
    y,
    noise=True,
    nu=2.5,
    length_scale_bounds=(1e-2, 1e1),
    noise_bounds=(1e-6, 1e-1),
    n_restarts_optimizer=10,
    normalize_y=True,
    random_state=0,
):
    """
    Fit a Gaussian-Process regressor that acts as the cheap surrogate for one
    black-box function. Returns a fitted sklearn GaussianProcessRegressor whose
    `.predict(X, return_std=True)` gives the posterior mean and std used by the
    acquisition functions.

    Parameters
    ----------
    X : (n, d) array   -- the inputs observed so far (initial data + any new trials).
    y : (n,)  array    -- the corresponding outputs (already on the scale you want
                          to MAXIMISE; e.g. F3/F6 are the negatives of a cost).
    noise : bool       -- add a WhiteKernel to model observation noise.
    nu : float         -- Matern smoothness (2.5 = Matern-5/2, the BO default).
    length_scale_bounds : (low, high)  -- bounds for the per-dimension lengthscales.
    noise_bounds : (low, high)         -- bounds for the learned noise variance.
    n_restarts_optimizer : int         -- restarts for the kernel-hyperparameter fit.
    normalize_y : bool                 -- standardise y internally (see reasoning).
    random_state : int                 -- reproducibility.

    Returns
    -------
    gp : fitted GaussianProcessRegressor
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    d = X.shape[1]

    # --- Kernel construction ------------------------------------------------
    # ConstantKernel: a learnable "signal variance" (output amplitude). Without
    #   it the GP would assume unit output amplitude, which is wrong for functions
    #   whose outputs span very different ranges (compare F1 ~0 vs F5 up to ~1089).
    #
    # Matern(nu=2.5): the standard BO kernel. RBF assumes the function is
    #   infinitely smooth (unrealistically wiggle-free); Matern-5/2 assumes a
    #   more realistic, moderate smoothness, which is why it is the default in
    #   virtually every BO library.
    #
    # ARD (Automatic Relevance Determination): we pass a *vector* of lengthscales,
    #   one per input dimension, by giving `length_scale=np.ones(d)`. The optimiser
    #   then learns a separate lengthscale per dimension. This is crucial for the
    #   higher-dim functions (F7 6-D, F8 8-D): a large fitted lengthscale means a
    #   dimension barely affects the output, so ARD effectively tells us which
    #   inputs matter and lets the GP ignore the rest -- vital when you only have
    #   a handful of points relative to the dimension.
    kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
        length_scale=np.ones(d),
        length_scale_bounds=length_scale_bounds,
        nu=nu,
    )

    # WhiteKernel adds an independent-noise term. Several functions are noisy
    #   (F2 is explicitly a "noisy log-likelihood"). Modelling noise stops the GP
    #   from interpolating every wobble and chasing phantom peaks. For functions
    #   you believe are noise-free you can set noise=False, but a small noise term
    #   also improves numerical stability ("jitter"), so leaving it on is safe.
    if noise:
        kernel = kernel + WhiteKernel(
            noise_level=1e-3, noise_level_bounds=noise_bounds
        )
        alpha = 0.0            # noise handled by the kernel itself
    else:
        alpha = 1e-8          # tiny jitter for a stable Cholesky factorisation

    # normalize_y standardises y to zero mean / unit variance before fitting and
    #   un-standardises predictions afterwards. This matters because a zero-mean
    #   GP prior would otherwise pull predictions toward 0 in unobserved regions,
    #   which is badly wrong for something like F5 (all large positive) or F4
    #   (all large negative). Predictions and stds still come back in ORIGINAL
    #   units, so the acquisition functions and `y_best` below stay in real units.
    gp = GaussianProcessRegressor(
        kernel=kernel,
        alpha=alpha,
        normalize_y=normalize_y,
        # The marginal-likelihood surface we optimise to pick lengthscales/noise
        #   is non-convex; multiple restarts from random starts make it far less
        #   likely we settle on a bad local optimum (a wrong lengthscale gives a
        #   badly mis-calibrated surrogate).
        n_restarts_optimizer=n_restarts_optimizer,
        random_state=random_state,
    )
    gp.fit(X, y)
    return gp


# =====================================================================
# 2) EXPECTED IMPROVEMENT  (exploration knob: xi)
# =====================================================================
def expected_improvement(X, gp, y_best, xi=0.01):
    """
    Expected Improvement for MAXIMISATION.

    EI(x) = E[ max(f(x) - y_best - xi, 0) ]  under the GP posterior.
    It answers: "how much do we expect this point to beat our current best?"
    and has a closed form for a Gaussian posterior, so it is cheap to evaluate
    over thousands of candidate points.

    Parameters
    ----------
    X : (m, d) array  -- candidate points to score.
    gp : fitted GP from fit_gp().
    y_best : float    -- the incumbent to beat. For noise-free functions use
                         max(observed y). For NOISY functions (e.g. F2) prefer the
                         max of the GP posterior MEAN at the observed points, so a
                         single lucky noisy read doesn't set an unbeatable bar.
    xi : float >= 0   -- exploration margin. xi=0 is greedy; larger xi demands a
                         bigger predicted gain before a point looks attractive,
                         which spreads sampling out. Practical schedule for this
                         project: xi a bit larger (e.g. 0.05-0.1 * output-scale)
                         in the early weeks, then xi -> 0 for the final exploit
                         trials.

    Returns
    -------
    ei : (m,) array of non-negative EI values (higher = more promising).
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))

    # Posterior mean (mu) and standard deviation (sigma) at each candidate.
    # sigma encodes model UNCERTAINTY -- it is large far from observed data and
    # small near it, which is exactly what lets EI trade off exploiting a high mu
    # against exploring a high sigma.
    mu, sigma = gp.predict(X, return_std=True)
    sigma = np.maximum(sigma, 1e-12)   # guard against divide-by-zero

    # improvement over the incumbent (minus the exploration margin xi)
    imp = mu - y_best - xi
    Z = imp / sigma

    # Closed-form EI = imp * Phi(Z) + sigma * phi(Z):
    #   - imp * Phi(Z): the "exploit" term -- reward for a high predicted mean.
    #   - sigma * phi(Z): the "explore" term -- reward for high uncertainty, so a
    #     point can be attractive purely because we're unsure about it.
    ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)

    # Where the model is certain (sigma ~ 0) there is no expected improvement.
    ei[sigma < 1e-12] = 0.0
    # EI is defined as an expectation of a non-negative quantity.
    return np.maximum(ei, 0.0)


# =====================================================================
# 3) UPPER CONFIDENCE BOUND  (exploration knob: beta)
# =====================================================================
def upper_confidence_bound(X, gp, beta=2.0):
    """
    Upper Confidence Bound for MAXIMISATION.

    UCB(x) = mu(x) + beta * sigma(x)

    An "optimistic" score: it ranks a point by its predicted mean PLUS a multiple
    of its uncertainty, so it will happily sample somewhere it is unsure about if
    that uncertainty is large enough. UCB is preferred over EI when you want a
    single, transparent exploration dial:

        small beta (~0.5-1)  -> exploit  (trust the mean, refine the best basin)
        large beta (~2-4)    -> explore  (chase uncertain regions; good for the
                                          multimodal/sparse functions F1, F4, F8)

    Note: the theory schedules beta to grow slowly with the number of trials
    (beta_t ~ sqrt(2 log(t^... ))). With only 10 trials a fixed beta per phase is
    simpler and works fine; just lower it as you move from exploring to exploiting.

    Parameters
    ----------
    X : (m, d) array  -- candidate points to score.
    gp : fitted GP from fit_gp().
    beta : float >= 0 -- exploration weight on the posterior std.

    Returns
    -------
    ucb : (m,) array (higher = more promising).
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    mu, sigma = gp.predict(X, return_std=True)
    return mu + beta * sigma


# =====================================================================
# 4) HELPER: turn an acquisition function into the next point to submit
# =====================================================================
def _as_bounds_array(bounds, dim):
    """Normalise `bounds` into two (dim,) arrays (lo, hi).

    Accepts either a single (low, high) tuple applied to every dimension, or an
    array-like of shape (dim, 2) giving a separate box per dimension (used for the
    trust-region search in F8).
    """
    b = np.asarray(bounds, dtype=float)
    if b.shape == (2,):                       # single (lo, hi) for all dims
        lo = np.full(dim, b[0])
        hi = np.full(dim, b[1])
    elif b.shape == (dim, 2):                 # per-dimension boxes
        lo, hi = b[:, 0].copy(), b[:, 1].copy()
    else:
        raise ValueError(
            f"bounds must be a (low,high) tuple or shape ({dim},2); got {b.shape}"
        )
    return lo, hi


def trust_region_bounds(center, radius, lo=0.0, hi=1.0):
    """Build a per-dimension box of half-width `radius` around `center`, clipped
    to [lo, hi]. Feed the result to `propose_next_point(bounds=...)` to restrict
    the search to a local neighbourhood -- the core idea behind trust-region BO
    (TuRBO), which is how we keep F8 tractable in 8 dimensions: instead of trying
    to model the whole space with ~50 points, we only search a small, well-sampled
    box around the current best and move/resize it as we learn.
    """
    center = np.asarray(center, dtype=float).ravel()
    low = np.clip(center - radius, lo, hi)
    high = np.clip(center + radius, lo, hi)
    return np.stack([low, high], axis=1)      # shape (dim, 2)


def propose_next_point(
    gp,
    dim,
    acquisition="ei",
    xi=0.01,
    beta=2.0,
    y_best=None,
    n_random=5000,
    n_local_restarts=5,
    bounds=(0.0, 1.0),
    random_state=0,
):
    """
    Find the point that MAXIMISES the chosen acquisition function within `bounds`.
    This is what actually gives you "the x to run next week".

    We optimise the acquisition (itself cheap, unlike the real black box) in two
    stages, because the acquisition surface is multimodal and gradient methods
    alone get stuck:
      1. Coarse random search over `n_random` points -- covers the whole box and
         gives good starting points. (Uniform random is fine; a Sobol/LHS sequence
         would be marginally better coverage if you have SciPy's qmc handy.)
      2. Local polish with L-BFGS-B from the best few random points -- sharpens the
         coarse winner to a precise location.

    Parameters
    ----------
    gp : fitted GP from fit_gp().
    dim : int                 -- input dimensionality of this function.
    acquisition : "ei"|"ucb"  -- which acquisition to maximise.
    xi, beta : the exploration knobs for EI / UCB respectively.
    y_best : float or None    -- incumbent for EI; if None, uses max of the GP's
                                 posterior mean at the training points (noise-safe).
    n_random : int            -- coarse-search sample count.
    n_local_restarts : int    -- how many top random points to polish with L-BFGS-B.
    bounds : (low, high) tuple, OR (dim, 2) array of per-dimension boxes.
                                 All functions live in [0,1], so the default is the
                                 unit box; pass a trust_region_bounds(...) array to
                                 search only a local neighbourhood (F8).
    random_state : int        -- reproducibility.

    Returns
    -------
    x_next : (dim,) array     -- the recommended next input to evaluate.
    acq_value : float         -- the acquisition value there (for logging/ranking).
    """
    rng = np.random.default_rng(random_state)
    lo, hi = _as_bounds_array(bounds, dim)

    # For EI we need an incumbent. Using the posterior mean at the observed X
    # (rather than the raw max y) is the noise-robust choice recommended above.
    if y_best is None:
        mu_train, _ = gp.predict(gp.X_train_, return_std=True)
        y_best = float(np.max(mu_train))

    def acq(Xcand):
        if acquisition == "ei":
            return expected_improvement(Xcand, gp, y_best=y_best, xi=xi)
        elif acquisition == "ucb":
            return upper_confidence_bound(Xcand, gp, beta=beta)
        raise ValueError("acquisition must be 'ei' or 'ucb'")

    # ---- stage 1: coarse random search (uniform inside the per-dim box) ----
    Xr = rng.uniform(lo, hi, size=(n_random, dim))
    vals = acq(Xr)
    order = np.argsort(vals)[::-1]           # best first
    best_x = Xr[order[0]].copy()
    best_v = float(vals[order[0]])

    # ---- stage 2: local polish (we MINIMISE the negative acquisition) ----
    def neg_acq(x):
        return -float(acq(x.reshape(1, -1))[0])

    for idx in order[:n_local_restarts]:
        res = minimize(
            neg_acq, x0=Xr[idx], method="L-BFGS-B",
            bounds=list(zip(lo, hi)),
        )
        if res.success and -res.fun > best_v:
            best_v = float(-res.fun)
            best_x = np.clip(res.x, lo, hi)

    return best_x, best_v



# =====================================================================
# 5) ALTERNATIVE SURROGATES  (added week 4)
# =====================================================================
# The Matern GP above allows arbitrary interactions between inputs. With only
# 13-43 observations that flexibility is often not affordable: the model
# interpolates its own data perfectly but predicts held-out points poorly.
# Cross-validation (see loo_q2 below) showed that on several functions a MORE
# CONSTRAINED surrogate predicts substantially better. Two are provided here.

def fit_additive_gp(
    X, y,
    length_scale_bounds=(1e-2, 10.0),
    noise=True,
    noise_bounds=(1e-6, 1e1),
    normalize_y=True,
    n_restarts_optimizer=10,
    random_state=0,
):
    """A GP that FORBIDS interactions: f(x) = f0(x0) + f1(x1) + ...

    Built as a sum of kernels, each of which varies in one dimension only (the
    other lengthscales are frozen at a huge value, which makes that kernel flat
    along those axes). Because each term has a single free lengthscale, the model
    has far fewer effective degrees of freedom than a full ARD kernel -- which is
    exactly what helps when data is scarce.

    Use when the partial-dependence curves for different settings of the other
    inputs look roughly parallel (little interaction), and when loo_q2 confirms it.
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    d = X.shape[1]
    FROZEN = 1e5

    kernel = None
    for j in range(d):
        ls = np.full(d, FROZEN)
        ls[j] = 1.0
        bounds = [(FROZEN, FROZEN + 1.0)] * d
        bounds[j] = length_scale_bounds
        term = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
            length_scale=ls, length_scale_bounds=bounds, nu=2.5
        )
        kernel = term if kernel is None else kernel + term

    if noise:
        kernel = kernel + WhiteKernel(noise_level=1e-3, noise_level_bounds=noise_bounds)
        alpha = 0.0
    else:
        alpha = 1e-8

    gp = GaussianProcessRegressor(
        kernel=kernel, alpha=alpha, normalize_y=normalize_y,
        n_restarts_optimizer=n_restarts_optimizer, random_state=random_state,
    )
    gp.fit(X, y)
    return gp


class TrendGP:
    """A polynomial trend with a GP fitted to whatever the trend leaves over.

    Motivation: on a log scale a Gaussian-shaped peak is exactly a quadratic, so
    for those functions a quadratic is not an approximation -- it is the right
    functional form, and it extrapolates sensibly where a stationary GP flattens
    out to the prior mean. The GP on the residual restores the local detail AND,
    crucially, supplies the uncertainty that EI and UCB need (a bare polynomial
    regression gives a mean but no sigma, so it cannot drive an acquisition).

    Exposes .predict(X, return_std=...) so it is a drop-in replacement for a GP
    everywhere in this toolkit.
    """

    def __init__(self, poly, ridge, gp):
        self.poly, self.ridge, self.gp = poly, ridge, gp
        self.X_train_ = gp.X_train_
        self.kernel_ = gp.kernel_

    def _trend(self, X):
        return self.ridge.predict(self.poly.transform(np.atleast_2d(X)))

    def predict(self, X, return_std=False):
        X = np.atleast_2d(np.asarray(X, dtype=float))
        base = self._trend(X)
        if return_std:
            mu, sd = self.gp.predict(X, return_std=True)
            return base + mu, sd
        return base + self.gp.predict(X)


def fit_trend_gp(
    X, y,
    degree=2,
    length_scale_bounds=(1e-2, 10.0),
    noise=True,
    noise_bounds=(1e-6, 1e1),
    n_restarts_optimizer=10,
    random_state=0,
):
    """Fit a degree-`degree` ridge trend, then a GP on the residual."""
    from sklearn.linear_model import RidgeCV
    from sklearn.preprocessing import PolynomialFeatures

    X = np.atleast_2d(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=float).ravel()

    poly = PolynomialFeatures(degree)
    Z = poly.fit_transform(X)
    ridge = RidgeCV(alphas=np.logspace(-3, 3, 25)).fit(Z, y)
    resid = y - ridge.predict(Z)

    gp = fit_gp(
        X, resid, length_scale_bounds=length_scale_bounds, noise=noise,
        noise_bounds=noise_bounds, normalize_y=False,
        n_restarts_optimizer=n_restarts_optimizer, random_state=random_state,
    )
    return TrendGP(poly, ridge, gp)


SURROGATES = {
    "matern":    lambda X, y, **kw: fit_gp(X, y, **kw),
    "additive":  lambda X, y, **kw: fit_additive_gp(X, y, **kw),
    "quadratic": lambda X, y, **kw: fit_trend_gp(X, y, degree=2, **kw),
}


def fit_surrogate(X, y, kind="matern", **kw):
    """Fit one of the surrogates by name. `kind` in SURROGATES."""
    if kind not in SURROGATES:
        raise ValueError(f"unknown surrogate {kind!r}; choose from {list(SURROGATES)}")
    return SURROGATES[kind](X, y, **kw)


# =====================================================================
# 6) MODEL SELECTION BY LEAVE-ONE-OUT  (added week 4)
# =====================================================================
def loo_q2(X, y, kind="matern", n_restarts_optimizer=2, random_state=0, **kw):
    """How well does this surrogate predict a point it was NOT shown?

    Removes each observation in turn, refits on the rest, predicts the held-out
    point, and scores all those predictions:

        Q2 = 1 - SSE(model) / SSE(predicting the mean every time)

      Q2 = 1    perfect prediction
      Q2 = 0    no better than ignoring the inputs and guessing the average
      Q2 < 0    worse than that -- the model's predictions actively mislead

    This is the test of whether a surrogate has earned the right to choose a point
    in a region nobody has measured. In-sample fit does NOT answer that question:
    every model here interpolates its own training data almost perfectly.

    Note: with a few dozen points Q2 is itself a noisy estimate. Treat differences
    below about 0.05 as meaningless, and only switch surrogate on a clear margin.
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    n = len(y)
    pred = np.empty(n)
    for k in range(n):
        m = np.ones(n, dtype=bool)
        m[k] = False
        mdl = fit_surrogate(X[m], y[m], kind=kind,
                            n_restarts_optimizer=n_restarts_optimizer,
                            random_state=random_state, **kw)
        pred[k] = float(np.ravel(mdl.predict(X[k].reshape(1, -1)))[0])
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss_res / max(ss_tot, 1e-300)


def compare_surrogates(X, y, kinds=("matern", "additive", "quadratic"), **kw):
    """Q2 for each candidate surrogate. Returns {name: q2}, best first."""
    out = {}
    for k in kinds:
        try:
            out[k] = float(loo_q2(X, y, kind=k, **kw))
        except Exception as exc:                       # a model may fail on some d
            out[k] = float("nan")
    return dict(sorted(out.items(), key=lambda kv: (-kv[1] if kv[1] == kv[1] else 1)))


# =====================================================================
# 7) LOCAL CANDIDATE PROPOSER  (added week 4)
# =====================================================================
# When loo_q2 says the surrogate cannot predict unmeasured regions, asking it
# "where in the whole space is the optimum?" produces a confident guess with
# nothing behind it. Asking it a smaller question -- "which of these few small
# moves from a point we have actually measured looks best?" -- is a question it
# can still answer, and every answer lands next to known-good data, so a wrong
# ranking costs little.

def local_candidates(
    X, y, lengthscales=None, step_frac=0.33, steps=(1.0, 2.0),
    include_direction=True, eps=1e-6, dedupe_tol=1e-3,
    skip_inert=True, inert_threshold=5.0, max_step=0.35, min_step=0.02,
):
    """Small moves away from the current best point.

    - one coordinate at a time, up and down, by `steps` multiples of a base step
    - `min_step` is the floor on that base step. It defaults to 0.02, but several
      of these functions turned out to have peaks narrower than that -- a move of
      0.024 once cost almost half a unit on one of them -- so the floor has to be
      lowered wherever the local structure is sharper than the fitted lengthscales
      suggest, or every candidate overshoots the thing being refined.
    - the base step for dimension j is step_frac * lengthscale_j (clipped to a
      sensible range), so sharp dimensions get small moves and flat ones get
      bigger moves
    - plus, optionally, a couple of points along the direction that led from the
      second-best observation to the best one (the empirical improving direction)

    Returns (candidates, labels).
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=float).ravel()
    d = X.shape[1]
    best_i = int(np.argmax(y))
    best = X[best_i].copy()

    if lengthscales is None:
        base = np.full(d, max(0.25, min_step))
        inert = np.zeros(d, dtype=bool)
    else:
        ls = np.atleast_1d(lengthscales).astype(float)
        base = np.clip(step_frac * ls, min_step, max_step)
        # A lengthscale at (or near) its upper bound means the model believes the
        # output barely responds to that input. Two reasons not to step it:
        # spending a trial there measures nothing, and step_frac * a huge
        # lengthscale saturates to max_step, which shoves the coordinate onto the
        # boundary -- exactly the boundary-pinning that has already cost trials.
        inert = ls > inert_threshold

    cands, labels = [], []

    def _add(c, tag):
        c = np.clip(np.asarray(c, dtype=float).ravel(), eps, 1.0 - eps)
        for prev in cands:
            if np.linalg.norm(prev - c) < dedupe_tol:
                return
        if np.min(np.linalg.norm(X - c, axis=1)) < dedupe_tol:
            return                                   # already measured
        cands.append(c); labels.append(tag)

    active = [j for j in range(d) if not (skip_inert and inert[j])]
    if not active:                       # every dimension looks inert: step all
        active = list(range(d))
    for j in active:
        for mult in steps:
            for sign in (+1.0, -1.0):
                c = best.copy()
                c[j] = best[j] + sign * mult * base[j]
                _add(c, f"x{j} {'+' if sign > 0 else '-'}{mult:g} step")

    if include_direction and len(y) > 1:
        second = X[int(np.argsort(y)[::-1][1])]
        vec = best - second
        nrm = float(np.linalg.norm(vec))
        if nrm > 1e-9:
            for a in (0.5, 1.0):
                _add(best + a * vec, f"improving direction x{a:g}")

    return np.array(cands), labels


def propose_local(
    model, X, y, lengthscales=None, step_frac=0.33, steps=(1.0, 2.0),
    score="ei", xi=0.01, beta=1.5, y_best=None, eps=1e-6, verbose=False,
    plausible_max=None, skip_inert=True, inert_threshold=5.0, min_step=0.02,
):
    """Rank local candidates with the surrogate and return the winner.

    `score`: "ei"   -- expected improvement (uses the model's uncertainty)
             "ucb"  -- mean + beta * sd
             "mean" -- posterior mean only (pure exploitation)

    Returns (x_next, table) where `table` lists every candidate with its label,
    predicted mean, sd and score -- so the choice is auditable rather than opaque.
    """
    cands, labels = local_candidates(
        X, y, lengthscales=lengthscales, step_frac=step_frac, steps=steps, eps=eps,
        skip_inert=skip_inert, inert_threshold=inert_threshold, min_step=min_step,
    )
    if len(cands) == 0:
        raise RuntimeError("no admissible local candidates (all already measured)")

    mu, sd = model.predict(cands, return_std=True)

    # Plausibility filter. A polynomial-trend surrogate can interpolate its data
    # beautifully and still extrapolate to an absurd value a short step away (an
    # indefinite quadratic has no maximum). `plausible_max` is a hard ceiling on
    # what the output could physically be; candidates predicting above it are
    # dropped rather than trusted.
    if plausible_max is not None:
        keep = mu <= plausible_max
        if keep.any():
            cands, mu, sd = cands[keep], mu[keep], sd[keep]
            labels = [l for l, k in zip(labels, keep) if k]
        elif verbose:
            print("  ! every candidate exceeded plausible_max; filter ignored")
    if y_best is None:
        y_best = float(np.max(np.ravel(model.predict(X))))

    if score == "ei":
        vals = expected_improvement(cands, model, y_best=y_best, xi=xi)
    elif score == "ucb":
        vals = mu + beta * sd
    elif score == "mean":
        vals = mu
    else:
        raise ValueError("score must be 'ei', 'ucb' or 'mean'")

    order = np.argsort(vals)[::-1]
    table = [
        {"label": labels[i], "x": cands[i], "mean": float(mu[i]),
         "sd": float(sd[i]), "score": float(vals[i])}
        for i in order
    ]
    if verbose:
        print(f"  ranked {len(cands)} local candidates (score={score}):")
        for r in table[:6]:
            print(f"    {r['label']:<26} mean {r['mean']:+.4g} +/- {r['sd']:.3g}"
                  f"   score {r['score']:.4g}")
    return cands[order[0]], table

# =====================================================================
# Minimal usage example (runs only if you execute this file directly)
# =====================================================================
if __name__ == "__main__":
    # Toy 2-D demo so you can see the pieces fit together. In practice you load
    # X, y from initial_data/function_i and (each week) append the new trial.
    rng = np.random.default_rng(0)
    X = rng.uniform(0, 1, size=(10, 2))
    y = -np.sum((X - 0.7) ** 2, axis=1)      # a simple peak at (0.7, 0.7)

    gp = fit_gp(X, y, noise=True)

    # Explore-leaning UCB pick vs. exploit-leaning EI pick:
    x_ucb, v_ucb = propose_next_point(gp, dim=2, acquisition="ucb", beta=2.5)
    x_ei,  v_ei  = propose_next_point(gp, dim=2, acquisition="ei",  xi=0.01)
    print("UCB(beta=2.5) proposes:", np.round(x_ucb, 3), " value:", round(v_ucb, 4))
    print("EI (xi=0.01)  proposes:", np.round(x_ei, 3),  " value:", round(v_ei, 4))
