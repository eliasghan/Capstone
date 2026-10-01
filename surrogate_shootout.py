"""Does a different surrogate predict these functions better than the GP we use?

Scored by leave-one-out Q2 -- same test for every model, so the comparison is fair.
"""
import warnings, numpy as np, pandas as pd, sys
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (Matern, RBF, ConstantKernel as Ck,
                                              WhiteKernel, DotProduct)
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

RS = 0
LS0 = 1.0
LSB = (1e-2, 10.0)
NB = (1e-6, 1e1)


def gp_matern(nu, d):
    k = Ck(1.0, (1e-3, 1e3)) * Matern(length_scale=[LS0] * d, length_scale_bounds=LSB,
                                      nu=nu) + WhiteKernel(1e-3, NB)
    return GaussianProcessRegressor(kernel=k, alpha=0.0, normalize_y=True,
                                    n_restarts_optimizer=2, random_state=RS)


def gp_rbf(d):
    k = Ck(1.0, (1e-3, 1e3)) * RBF(length_scale=[LS0] * d, length_scale_bounds=LSB) \
        + WhiteKernel(1e-3, NB)
    return GaussianProcessRegressor(kernel=k, alpha=0.0, normalize_y=True,
                                    n_restarts_optimizer=2, random_state=RS)


def gp_linear_trend(d):
    """Matern plus a linear (dot-product) term: lets the GP carry a global slope."""
    k = (Ck(1.0, (1e-3, 1e3)) * Matern(length_scale=[LS0] * d, length_scale_bounds=LSB,
                                       nu=2.5)
         + Ck(1.0, (1e-3, 1e3)) * DotProduct(sigma_0=1.0)
         + WhiteKernel(1e-3, NB))
    return GaussianProcessRegressor(kernel=k, alpha=0.0, normalize_y=True,
                                    n_restarts_optimizer=2, random_state=RS)


def gp_additive(d):
    """Sum of one-dimensional kernels: no interactions, far fewer effective dof."""
    k = None
    for j in range(d):
        ls = np.full(d, 1e5); ls[j] = LS0
        bnd = [(1e5, 1e5 + 1.0)] * d; bnd[j] = LSB
        kj = Ck(1.0, (1e-3, 1e3)) * Matern(length_scale=ls, length_scale_bounds=bnd,
                                           nu=2.5)
        k = kj if k is None else k + kj
    k = k + WhiteKernel(1e-3, NB)
    return GaussianProcessRegressor(kernel=k, alpha=0.0, normalize_y=True,
                                    n_restarts_optimizer=2, random_state=RS)


MODELS = {
    "GP Matern 5/2 (current)": lambda d: gp_matern(2.5, d),
    "GP Matern 3/2 (rougher)": lambda d: gp_matern(1.5, d),
    "GP RBF (smoother)":       lambda d: gp_rbf(d),
    "GP + linear trend":       lambda d: gp_linear_trend(d),
    "GP additive (no interactions)": lambda d: gp_additive(d),
    "Random forest":           lambda d: RandomForestRegressor(n_estimators=300,
                                                               random_state=RS),
    "Quadratic ridge":         lambda d: make_pipeline(
                                   PolynomialFeatures(2), StandardScaler(),
                                   RidgeCV(alphas=np.logspace(-3, 3, 25))),
    "Linear ridge":            lambda d: make_pipeline(
                                   StandardScaler(),
                                   RidgeCV(alphas=np.logspace(-3, 3, 25))),
}

TRANSFORM = {1: "log10abs", 5: "log"}


def load(i):
    X = np.load(f"function_{i}/initial_inputs.npy")
    y = np.load(f"function_{i}/initial_outputs.npy").ravel()
    df = pd.read_csv(f"function_{i}/new_trials.csv")
    X = np.vstack([X, df.iloc[:, :-1].to_numpy(float)])
    y = np.concatenate([y, df.iloc[:, -1].to_numpy(float)])
    t = TRANSFORM.get(i)
    if t == "log":      y = np.log(y)
    if t == "log10abs": y = np.log10(np.abs(y))
    return X, y


def loo_q2(make, X, y):
    n = len(y); pred = np.empty(n)
    for k in range(n):
        m = np.ones(n, bool); m[k] = False
        mdl = make(X.shape[1])
        mdl.fit(X[m], y[m])
        pred[k] = np.ravel(mdl.predict(X[k].reshape(1, -1)))[0]
    return 1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)


rows = []
for i in range(1, 9):
    X, y = load(i)
    r = {"fn": f"F{i}", "dim": X.shape[1], "n": len(y)}
    for name, make in MODELS.items():
        try:
            r[name] = round(float(loo_q2(make, X, y)), 3)
        except Exception as e:
            r[name] = np.nan
    rows.append(r)
    print(f"F{i} done")

df = pd.DataFrame(rows)
pd.set_option("display.width", 250, "display.max_columns", 50)
print()
print(df.to_string(index=False))
df.to_csv("surrogate_shootout.csv", index=False)

mcols = list(MODELS)
best = df[mcols].idxmax(axis=1)
print()
for fn, b, cur in zip(df.fn, best, df["GP Matern 5/2 (current)"]):
    gain = df.loc[df.fn == fn, b].values[0] - cur
    print(f"{fn}: best = {b}  ({df.loc[df.fn==fn, b].values[0]:+.3f}) "
          f"vs current {cur:+.3f}   gain {gain:+.3f}")
