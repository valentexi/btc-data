# -*- coding: utf-8 -*-
"""
Statistiques robustes pour le backtest.

Les trades d'un même épisode de marché (ré-entrées successives pendant une même baisse,
par exemple) ne sont pas indépendants. On les regroupe donc en épisodes et on
ré-échantillonne des épisodes entiers (bootstrap par blocs). Pour les séries
quotidiennes, on ré-échantillonne des blocs de jours consécutifs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N_TIRAGES = 2000
MIN_TRADES = 30
MIN_EPISODES = 10


def episodes(t_entree, ecart_jours: int = 10, duree_max: int = 30) -> np.ndarray:
    """Numéro d'épisode de chaque trade.

    Nouvel épisode après plus de `ecart_jours` sans entrée, ou quand l'épisode en cours dure depuis plus
    de `duree_max` jours (sinon une règle qui trade en continu ne formerait qu'un seul épisode).
    """
    t = pd.to_datetime(pd.Series(list(t_entree)), utc=True)
    if len(t) == 0:
        return np.zeros(0, int)
    jours = (t - t.iloc[0]).dt.total_seconds().to_numpy() / 86400.0
    ep, numero, debut = np.zeros(len(t), int), 0, jours[0]
    for k in range(1, len(t)):
        if jours[k] - jours[k - 1] > ecart_jours or jours[k] - debut > duree_max:
            numero, debut = numero + 1, jours[k]
        ep[k] = numero
    return ep


def ic_episodes(r, ep, n: int = N_TIRAGES, graine: int = 0) -> tuple[float, float]:
    """Intervalle à 95 % de la moyenne, en tirant des épisodes entiers avec remise."""
    r, ep = np.asarray(r, float), np.asarray(ep, int)
    if len(r) == 0:
        return float("nan"), float("nan")
    ne = int(ep.max()) + 1
    sommes = np.bincount(ep, weights=r, minlength=ne)
    tailles = np.bincount(ep, minlength=ne).astype(float)
    rng = np.random.default_rng(graine)
    tir = rng.integers(0, ne, size=(n, ne))
    moy = sommes[tir].sum(axis=1) / tailles[tir].sum(axis=1)
    lo, hi = np.percentile(moy, [2.5, 97.5])
    return float(lo), float(hi)


def tirages_blocs(n_obs: int, bloc: int, n: int = 1000, graine: int = 0):
    """Indices ré-échantillonnés par blocs consécutifs (bootstrap par blocs mobiles)."""
    rng = np.random.default_rng(graine)
    nb = int(np.ceil(n_obs / bloc))
    base = np.arange(bloc)
    for _ in range(n):
        debuts = rng.integers(0, max(1, n_obs - bloc + 1), size=nb)
        yield (debuts[:, None] + base[None, :]).ravel()[:n_obs]


def resume(trades: list[dict], t_milieu: str | None = None) -> dict:
    """Statistiques d'une liste de trades (clés R, R_fin, R_stress, t_entree)."""
    n = len(trades)
    if n == 0:
        return {"n": 0}
    r = np.array([t["R"] for t in trades], float)
    rf = np.array([t["R_fin"] for t in trades], float)
    rs = np.array([t["R_stress"] for t in trades], float)
    te = [t["t_entree"] for t in trades]
    ep = episodes(te)
    lo, hi = ic_episodes(r, ep)
    serie, pire = 0, 0
    for x in r:
        serie = serie + 1 if x < 0 else 0
        pire = max(pire, serie)
    avec = ~np.isnan(rf)
    res = {
        "n": n, "episodes": int(ep.max()) + 1, "gagnants": float((r > 0).mean()),
        "r": float(r.mean()), "lo": lo, "hi": hi, "r_stress": float(rs.mean()),
        "n_fin": int(avec.sum()),
        "r_fin": float(rf[avec].mean()) if avec.any() else float("nan"),
        "r_sans_fin_meme_periode": float(r[avec].mean()) if avec.any() else float("nan"),
        "pire_serie": pire, "r_total": float(r.sum()),
    }
    if t_milieu is not None:
        avant = np.array([str(x) < t_milieu for x in te])
        res["r1"] = float(r[avant].mean()) if avant.any() else float("nan")
        res["r2"] = float(r[~avant].mean()) if (~avant).any() else float("nan")
        res["n1"], res["n2"] = int(avant.sum()), int((~avant).sum())
    return res


def verdict(s: dict, reference: float) -> str:
    """Jamais « validé » : un backtest ne peut que désigner un candidat à confirmer en mode papier."""
    if s.get("n", 0) < MIN_TRADES or s.get("episodes", 0) < MIN_EPISODES:
        return "échantillon insuffisant"
    if s["hi"] < 0:
        return "négatif"
    if s["lo"] > 0:
        stable = s.get("r1", 0) > 0 and s.get("r2", 0) > 0
        if stable and s["r"] > reference and s["r_stress"] > 0:
            return "candidat, à confirmer en papier"
        return "positif mais fragile"
    return "pas d'avantage démontré"
