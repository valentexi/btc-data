#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest du Bitcoin, long et short (version 2).

Ce que ce fichier cherche à établir : une règle a-t-elle, oui ou non, un avantage
statistique après frais ? Il ne cherche pas à produire de beaux résultats.

Principes :
- règles et paramètres fixés à l'avance, aucun réglage optimisé sur l'historique ;
- signal connu à la clôture d'une bougie, entrée à l'ouverture de la suivante ;
- sorties suivies sur des bougies de 4 heures ; stop prioritaire en cas de doute ;
- frais et glissement déduits ; financement réel quand il existe, jamais inventé ;
- trades regroupés par épisodes de marché, intervalle de confiance par bootstrap de blocs ;
- comparaison à une référence (mêmes plans, entrées à dates régulières) ;
- test hors échantillon : deux moitiés d'historique, puis sélection année par année ;
- un backtest ne « valide » jamais : au mieux il désigne un candidat à suivre en mode papier.

Lit data/, écrit rapport/backtest.md et rapport/trades.csv.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

from outils import RAPPORT, lire, lire_h4, nb, pct
from simulation import FRAIS, FRAIS_STRESS, GLISSEMENT, GLISSEMENT_STRESS, barres, plan_structure, simuler
from stats import MIN_EPISODES, MIN_TRADES, episodes, ic_episodes, resume, tirages_blocs, verdict

STOP, OBJECTIF, DUREE = 0.04, 0.065, 7      # plan type des règles journalières
M1, M2, BARRES_MAX = 1.2, 2.4, 30           # configurations 4 h : objectifs à 1,2 R et 2,4 R, 5 jours au plus
TOUCHE, MARGE_STOP, MARGE_CASSURE = 0.003, 0.005, 0.015


# ------------------------------------------------------------------- données
def charger():
    p, h4 = lire("btc_jour.csv"), lire_h4()
    if p is None or len(p) < 400 or h4 is None or len(h4) < 2000:
        return None
    J = p.sort_values("date").reset_index(drop=True)

    def joindre(nom, colonnes):
        nonlocal J
        df = lire(nom)
        for c in colonnes.values():
            J[c] = np.nan
        if df is not None:
            ok = {k: v for k, v in colonnes.items() if k in df.columns}
            if ok:
                J = J.drop(columns=list(ok.values())).merge(df[["date", *ok]].rename(columns=ok), on="date", how="left")

    joindre("peur_avidite.csv", {"valeur": "peur"})
    joindre("financement_kraken.csv", {"cumul_jour_pct": "fin_kraken"})
    joindre("financement_deribit.csv", {"cumul_jour_pct": "fin_deribit"})
    joindre("macro.csv", {"dxy": "dxy", "taux_10ans": "taux10", "nasdaq100": "ndx", "vix": "vix"})
    joindre("onchain.csv", {"mvrv": "mvrv", "btc_sur_plateformes": "plateformes"})
    J["fin_jour"] = (J["fin_kraken"].combine_first(J["fin_deribit"])) / 100.0   # part payée par les longs chaque jour
    for c in ("dxy", "taux10", "ndx", "vix"):
        J[c] = J[c].ffill(limit=5)                                           # week-ends et jours fériés

    c = J["cloture"]
    J["mm50"], J["mm200"] = c.rolling(50).mean(), c.rolling(200).mean()
    J["mm200s"] = c.rolling(1400).mean()                                     # 200 semaines
    J["var7"] = c / c.shift(7) - 1
    J["sur200"], J["sous200"] = c > J["mm200"], c < J["mm200"]
    J["sup20"], J["res20"] = J["bas"].rolling(20).min(), J["haut"].rolling(20).max()   # jusqu'au jour J inclus
    J["sup20_prec"], J["res20_prec"] = J["sup20"].shift(1), J["res20"].shift(1)        # jusqu'à la veille
    J["biais"] = biais_mecanique(J)

    H = h4.sort_values("date").reset_index(drop=True)
    fin = {d: v for d, v in zip(J["date"], J["fin_jour"]) if v == v}
    B = barres(H, fin)
    jours = pd.to_datetime(H["date"].str[:10])
    veille = (jours - pd.Timedelta(days=1)).dt.strftime("%Y-%m-%d")           # dernier jour terminé avant la bougie
    Jx = J.set_index("date")
    for col in ("sup20", "res20", "mm50", "mm200", "mm200s", "cloture"):
        B["j_" + col] = Jx[col].reindex(veille).to_numpy(float)
    B["sur200"] = B["j_cloture"] > B["j_mm200"]
    B["sous200"] = B["j_cloture"] < B["j_mm200"]
    B["week_end"] = pd.to_datetime(H["date"]).dt.dayofweek.to_numpy() >= 5
    ouv = {d[:10]: k for k, d in enumerate(H["date"]) if d.endswith("00:00")}
    lendemain = (pd.to_datetime(J["date"]) + pd.Timedelta(days=1)).dt.strftime("%Y-%m-%d")
    J["i_entree"] = [ouv.get(d, -1) for d in lendemain]                       # bougie de 0 h du lendemain
    return J, B


FAMILLES = ["structure", "positionnement", "blockchain", "macro", "actifs"]


def biais_mecanique(J: pd.DataFrame) -> pd.Series:
    """Approximation mécanique du biais de la méthode, sur cinq des sept familles.

    Seuils conventionnels fixés à l'avance, non optimisés. Les familles « flux » (ETF) et
    « événements » n'ont pas d'historique exploitable : elles sont absentes de ce test.
    """
    f = familles_mecaniques(J)
    return f["structure"] + f["positionnement"] + f["blockchain"] + f["macro"] + f["actifs"]


def familles_mecaniques(J: pd.DataFrame) -> pd.DataFrame:
    """Note de chaque famille (de −2 à +2), jour par jour. NaN quand la donnée de la famille manque."""
    c = J["cloture"]
    f1 = np.sign(c - J["mm200"]) + np.sign(c - J["mm50"])                     # structure du prix
    fin3 = J["fin_jour"].rolling(3).mean()
    f2 = ((J["peur"] <= 20).astype(float) - (J["peur"] >= 80).astype(float)   # positionnement, à contre-pied
          + (fin3 < 0).astype(float) - (fin3 > 0.0009).astype(float)).clip(-2, 2)
    f2[J["peur"].isna()] = np.nan
    mv = J["mvrv"]
    f4 = pd.Series(0.0, index=J.index)
    f4[mv < 1] = 2
    f4[mv > 2.4] = -1
    f4[mv > 3] = -2
    ch = J["plateformes"].pct_change(30)
    f4 = (f4 + (ch < -0.01).astype(float) - (ch > 0.01).astype(float)).clip(-2, 2)   # sorties des plateformes = +
    f4[mv.isna()] = np.nan
    f5 = -np.sign(J["dxy"] - J["dxy"].rolling(50).mean()) - np.sign(J["taux10"] - J["taux10"].rolling(50).mean())
    f6 = (np.sign(J["ndx"] - J["ndx"].rolling(50).mean())
          + (J["vix"] < 15).astype(float) - (J["vix"] > 25).astype(float)).clip(-2, 2)
    f6[J["vix"].isna()] = np.nan
    # somme de −10 à +10, NaN si une famille manque
    return pd.DataFrame({"structure": f1, "positionnement": f2, "blockchain": f4, "macro": f5, "actifs": f6})


# ---------------------------------------------------------------- simulations
def _inacheve(t: dict, B: dict, i_max: int) -> bool:
    """Trade encore ouvert à la fin des données : on ne le compte pas."""
    return i_max > B["n"] - 1 and t["j"] == B["n"] - 1 and "durée" in t["motif"]


def trades_jour(J, B, masque, sens, stop=STOP, obj=OBJECTIF, jours=DUREE) -> list[dict]:
    """Règle journalière : signal à la clôture du jour, entrée à 0 h UTC, une position à la fois."""
    out, libre = [], -1
    for k in np.flatnonzero(np.asarray(masque, bool)):
        i = int(J["i_entree"].iat[k])
        if i < 0 or i <= libre:
            continue
        E = B["o"][i]
        i_max = i + jours * 6 - 1
        t = simuler(B, i, sens, E * (1 - sens * stop), None, E * (1 + sens * obj), i_max)
        if t is None or _inacheve(t, B, i_max):
            continue
        out.append(t)
        libre = t["j"]
    return out


def trades_h4(B, signaux, sens) -> list[dict]:
    """Configuration 4 h : (bougie du signal, stop de structure) -> entrée à l'ouverture suivante."""
    out, libre = [], -1
    for j, stop in sorted(signaux):
        i = j + 1
        if i >= B["n"] or i <= libre or stop != stop:
            continue
        E = B["o"][i]
        ps = plan_structure(E, sens, stop)
        if ps is None:
            continue
        stop, d = ps
        i_max = i + BARRES_MAX - 1
        t = simuler(B, i, sens, stop, E * (1 + sens * M1 * d), E * (1 + sens * M2 * d), i_max)
        if t is None or _inacheve(t, B, i_max):
            continue
        t["aligne"] = bool(B["sur200"][i] if sens == 1 else B["sous200"][i])
        t["week_end"] = bool(B["week_end"][i])
        out.append(t)
        libre = t["j"]
    return out


_REF: dict = {}


def reference(B, sens, d, unique) -> float:
    """R moyen du même plan avec des entrées régulières (toutes les 20 heures), sans aucun signal."""
    cle = (sens, round(d, 3), unique)
    if cle not in _REF:
        r = []
        duree = DUREE * 6 if unique else BARRES_MAX
        for i in range(1200, B["n"] - duree, 5):
            E = B["o"][i]
            if unique:
                t = simuler(B, i, sens, E * (1 - sens * d), None, E * (1 + sens * d * OBJECTIF / STOP), i + duree - 1)
            else:
                t = simuler(B, i, sens, E * (1 - sens * d), E * (1 + sens * M1 * d), E * (1 + sens * M2 * d), i + duree - 1)
            if t:
                r.append(t["R"])
        _REF[cle] = float(np.mean(r)) if r else float("nan")
    return _REF[cle]


# ------------------------------------------------------------------ règles
def regles_jour(J) -> list[dict]:
    peur, var7, sous, sur = J["peur"], J["var7"], J["sous200"], J["sur200"]
    lundi = pd.to_datetime(J["date"]).dt.dayofweek == 6        # clôture du dimanche -> entrée le lundi à 0 h
    fin3 = J["fin_jour"].rolling(3).mean()
    b = J["biais"]
    return [
        {"id": "L0", "nom": "Référence : long chaque lundi", "sens": 1, "m": lundi},
        {"id": "L1", "nom": "Long en peur extrême (Fear & Greed ≤ 20)", "sens": 1, "m": peur <= 20},
        {"id": "L2", "nom": "Long en peur extrême, sous la moyenne 200 jours", "sens": 1, "m": (peur <= 20) & sous},
        {"id": "L3", "nom": "Long en peur extrême, au-dessus de la moyenne 200 jours", "sens": 1, "m": (peur <= 20) & sur},
        {"id": "L4", "nom": "Long après une purge (−10 % en 7 jours)", "sens": 1, "m": var7 <= -0.10},
        {"id": "L5", "nom": "Long après une purge, sous la moyenne 200 jours", "sens": 1, "m": (var7 <= -0.10) & sous},
        {"id": "L6", "nom": "Long quand le financement est négatif (3 jours)", "sens": 1, "m": fin3 < 0},
        {"id": "L7", "nom": "Long quand le biais mécanique est ≥ +5", "sens": 1, "m": b >= 5},
        {"id": "S0", "nom": "Référence : short chaque lundi", "sens": -1, "m": lundi},
        {"id": "S1", "nom": "Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours", "sens": -1,
         "m": (var7 >= 0.08) & sous},
        {"id": "S2", "nom": "Short en avidité extrême (Fear & Greed ≥ 80)", "sens": -1, "m": peur >= 80},
        {"id": "S3", "nom": "Short chaque lundi sous la moyenne 200 jours", "sens": -1, "m": lundi & sous},
        {"id": "S4", "nom": "Short quand le biais mécanique est ≤ −5", "sens": -1, "m": b <= -5},
    ]


def configurations_h4(J, B) -> list[dict]:
    """Les configurations que la méthode recommande réellement, définies mécaniquement."""
    o, h, l, c = B["o"], B["h"], B["l"], B["c"]
    c_prec = np.r_[np.nan, c[:-1]]
    bas3 = pd.Series(l).rolling(3).min().to_numpy() * (1 - MARGE_STOP)
    haut3 = pd.Series(h).rolling(3).max().to_numpy() * (1 + MARGE_STOP)
    sup, res = B["j_sup20"], B["j_res20"]
    haussiere, baissiere = c > o, c < o
    out = []

    def ajouter(ident, nom, sens, masque, stops):
        sig = [(int(j), float(stops[j])) for j in np.flatnonzero(masque)]
        out.append({"id": ident, "nom": nom, "sens": sens, "trades": trades_h4(B, sig, sens)})

    ajouter("A-L", "Long sur rejet d'un support (plus bas de 20 jours)", 1,
            (l <= sup * (1 + TOUCHE)) & (c > sup) & haussiere & (c_prec > sup), bas3)
    ajouter("A-S", "Short sur rejet d'une résistance (plus haut de 20 jours)", -1,
            (h >= res * (1 - TOUCHE)) & (c < res) & baissiere & (c_prec < res), haut3)
    for cle, lib in (("mm50", "50 jours"), ("mm200", "200 jours"), ("mm200s", "200 semaines")):
        mm = B["j_" + cle]
        dessus, dessous = B["j_cloture"] > mm, B["j_cloture"] < mm
        ajouter(f"B-L-{cle}", f"Long sur rebond sur la moyenne {lib}", 1,
                dessus & (l <= mm * (1 + TOUCHE)) & (c > mm) & haussiere, bas3)
        ajouter(f"B-S-{cle}", f"Short sur rejet sous la moyenne {lib}", -1,
                dessous & (h >= mm * (1 - TOUCHE)) & (c < mm) & baissiere, haut3)

    # Cassures en clôture journalière, puis retour sur le niveau cassé (« rebond raté »)
    cj, ie = J["cloture"], J["i_entree"].to_numpy()
    for sens, niv, ident in ((-1, J["sup20_prec"], "S"), (1, J["res20_prec"], "L")):
        if sens == -1:
            casse = (cj < niv) & (cj.shift(1) >= niv.shift(1))
        else:
            casse = (cj > niv) & (cj.shift(1) <= niv.shift(1))
        evts = [(int(ie[k]), float(niv.iat[k])) for k in np.flatnonzero(casse.fillna(False).to_numpy()) if ie[k] > 0]
        sig = [(i - 1, L_ * (1 - sens * MARGE_CASSURE)) for i, L_ in evts]
        nom = ("Short sur cassure d'un support en clôture journalière" if sens == -1
               else "Long sur cassure d'une résistance en clôture journalière")
        out.append({"id": f"C-{ident}", "nom": nom, "sens": sens, "trades": trades_h4(B, sig, sens)})
        retests = []
        for i, L_ in evts:
            for k in range(i, min(i + 42, B["n"])):
                if sens == -1 and h[k] >= L_ * (1 - TOUCHE) and c[k] < L_ and baissiere[k]:
                    retests.append((k, float(haut3[k])))
                    break
                if sens == 1 and l[k] <= L_ * (1 + TOUCHE) and c[k] > L_ and haussiere[k]:
                    retests.append((k, float(bas3[k])))
                    break
        nom = ("Short sur rebond raté (retour sous un support cassé)" if sens == -1
               else "Long sur retour au-dessus d'une résistance cassée")
        out.append({"id": f"D-{ident}", "nom": nom, "sens": sens, "trades": trades_h4(B, retests, sens)})
    return out


# -------------------------------------------------------- biais mécanique
def etude_biais(J) -> dict | None:
    c = J["cloture"]
    f7, f14 = (c.shift(-7) / c - 1), (c.shift(-14) / c - 1)
    ok = J["biais"].notna() & f7.notna()
    if ok.sum() < 500:
        return None
    b, x7, x14 = J["biais"][ok].to_numpy(), f7[ok].to_numpy(), f14[ok].to_numpy()
    classes = [("≤ −5 (baissier)", b <= -5), ("−4 à −2", (b >= -4) & (b <= -2)), ("−1 à +1 (neutre)", np.abs(b) <= 1),
               ("+2 à +4", (b >= 2) & (b <= 4)), ("≥ +5 (haussier)", b >= 5)]

    def rang(v):
        return np.argsort(np.argsort(v)).astype(float)

    def spearman(u, v):
        return float(np.corrcoef(rang(u), rang(v))[0, 1])

    ecarts = {nom: [] for nom, _ in classes}
    rhos = []
    for idx in tirages_blocs(len(b), 30, 1000):
        bb, xx = b[idx], x7[idx]
        tout = xx.mean()
        for (nom, _), m in zip(classes, [bb <= -5, (bb >= -4) & (bb <= -2), np.abs(bb) <= 1,
                                         (bb >= 2) & (bb <= 4), bb >= 5]):
            if m.sum() >= 5:
                ecarts[nom].append(xx[m].mean() - tout)
        rhos.append(spearman(bb, xx))
    lignes = []
    for nom, m in classes:
        if m.sum() == 0:
            lignes.append({"classe": nom, "jours": 0})
            continue
        e = ecarts[nom]
        idx = np.flatnonzero(m)
        lo, hi = (np.percentile(e, [2.5, 97.5]) if len(e) > 100 else (np.nan, np.nan))
        lignes.append({"classe": nom, "jours": int(m.sum()), "episodes": int(1 + (np.diff(idx) > 7).sum()),
                       "moy7": float(x7[m].mean()), "med7": float(np.median(x7[m])), "pos7": float((x7[m] > 0).mean()),
                       "moy14": float(np.nanmean(x14[m])), "ecart": float(x7[m].mean() - x7.mean()),
                       "lo": float(lo), "hi": float(hi)})
    lo, hi = np.percentile(rhos, [2.5, 97.5])
    return {"lignes": lignes, "rho": spearman(b, x7), "rho_lo": float(lo), "rho_hi": float(hi),
            "jours": int(len(b)), "debut": J["date"][ok].iloc[0], "fin": J["date"][ok].iloc[-1],
            "moy7": float(x7.mean())}


# ------------------------------------------------------------ walk-forward
def walk_forward(candidats: dict[str, list[dict]]) -> dict:
    """Chaque 1er janvier : on retient la règle la plus rentable sur le passé (au moins 30 trades,
    R moyen positif) et on la suit pendant l'année. Seuls les trades de l'année suivie comptent."""
    annees = sorted({t["t_entree"][:4] for tr in candidats.values() for t in tr})
    lignes, hors = [], []
    for an in annees[3:]:
        meilleur, score = None, 0.0
        for nom, tr in candidats.items():
            passe = [t["R"] for t in tr if t["t_sortie"][:4] < an]
            if len(passe) >= MIN_TRADES and np.mean(passe) > score:
                meilleur, score = nom, float(np.mean(passe))
        if meilleur is None:
            lignes.append({"an": an, "regle": "aucune règle rentable sur le passé", "passe": float("nan"), "n": 0,
                           "r": float("nan")})
            continue
        suivis = [t for t in candidats[meilleur] if t["t_entree"][:4] == an]
        hors += suivis
        lignes.append({"an": an, "regle": meilleur, "passe": score, "n": len(suivis),
                       "r": float(np.mean([t["R"] for t in suivis])) if suivis else float("nan")})
    hors = sorted(hors, key=lambda t: t["t_entree"])
    return {"lignes": lignes, "bilan": resume(hors) if hors else {"n": 0}}


# ---------------------------------------------------------- suivi de tendance
def tendance(J, sens, avec_fin) -> dict | None:
    d = J[J["mm200"].notna()]
    if avec_fin:
        d = d[d["fin_jour"].notna()]
    if len(d) < 365:
        return None
    d = d.reset_index(drop=True)
    c = d["cloture"]
    pos = (d["sur200"] if sens == 1 else d["sous200"]).shift(1, fill_value=False).astype(float)
    r = c.pct_change().fillna(0.0)
    chg = pos.diff().abs().fillna(pos.iloc[0])
    net = sens * pos * r - chg * (FRAIS + GLISSEMENT / 2)
    if avec_fin:
        net = net - sens * pos * d["fin_jour"]
    courbe = (1 + net).cumprod()
    ans = len(d) / 365.25
    return {"rendement": float(courbe.iloc[-1] ** (1 / ans) - 1), "creux": float((courbe / courbe.cummax() - 1).min()),
            "temps": float(pos.mean()), "detenir": float((c.iloc[-1] / c.iloc[0]) ** (1 / ans) - 1),
            "debut": d["date"].iloc[0], "fin": d["date"].iloc[-1]}


# -------------------------------------------------------------------- rapport
def r_(x, d=2):
    return "n.d." if x != x else f"{x:+.{d}f}".replace(".", ",") + " R"


def p_(x, d=1):
    return "n.d." if x != x else pct(x, d)


ENTETE = ("| Règle | Trades | Épisodes | Gagnants | R moyen | Intervalle à 95 % | Référence | "
          "Avec financement réel | 1re moitié | 2e moitié | Coûts dégradés | Verdict |")
SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|"


def ligne(nom, s, ref) -> str:
    if s.get("n", 0) == 0:
        return f"| {nom} | 0 | | | | | | | | | | aucun trade |"
    fin = "n.d." if s["n_fin"] == 0 else f"{r_(s['r_fin'])} sur {s['n_fin']} (contre {r_(s['r_sans_fin_meme_periode'])} sans)"
    return (f"| {nom} | {s['n']} | {s['episodes']} | {nb(s['gagnants'] * 100)} % | {r_(s['r'])} | "
            f"{r_(s['lo'])} à {r_(s['hi'])} | {r_(ref)} | {fin} | {r_(s.get('r1', float('nan')))} | "
            f"{r_(s.get('r2', float('nan')))} | {r_(s['r_stress'])} | {verdict(s, ref)} |")


def rapport(J, B) -> tuple[str, pd.DataFrame]:
    t_milieu = B["date"][B["n"] // 2]
    tous, lignes_j, lignes_h, verdicts, candidats = [], [], [], [], {}

    def traiter(ident, nom, trades, sens, d_ref, unique, dest):
        s = resume(trades, t_milieu)
        ref = reference(B, sens, d_ref, unique)
        dest.append(ligne(f"{ident} {nom}", s, ref))
        if s.get("n", 0):
            verdicts.append((f"{ident} {nom}", verdict(s, ref), s))
            for t in trades:
                tous.append({**t, "regle": ident})
        return s

    for reg in regles_jour(J):
        tr = trades_jour(J, B, reg["m"].fillna(False), reg["sens"])
        traiter(reg["id"], reg["nom"], tr, reg["sens"], STOP, True, lignes_j)
        if reg["id"] not in ("L0", "S0"):
            candidats[f"{reg['id']} {reg['nom']}"] = tr

    confs = configurations_h4(J, B)
    for cf in confs:
        tr = cf["trades"]
        d_med = float(np.median([t["d"] for t in tr])) if tr else 0.03
        traiter(cf["id"], cf["nom"], tr, cf["sens"], d_med, False, lignes_h)
        al = [t for t in tr if t["aligne"]]
        if cf["id"][0] in "ACD":
            traiter(cf["id"] + "+", cf["nom"] + ", dans le sens de la moyenne 200 jours", al, cf["sens"], d_med, False,
                    lignes_h)
            candidats[f"{cf['id']}+ {cf['nom']}, dans le sens de la tendance"] = al
        candidats[f"{cf['id']} {cf['nom']}"] = tr

    wf = walk_forward(candidats)
    eb = etude_biais(J)
    testees = [v for v in verdicts if v[1] != "échantillon insuffisant"]
    cand = [v for v in verdicts if v[1].startswith("candidat")]
    fragiles = [v for v in verdicts if v[1] == "positif mais fragile"]
    negatifs = [v for v in verdicts if v[1] == "négatif"]

    L: list[str] = []
    L.append(f"# Backtest BTC, version 2 ({dt.datetime.now(dt.timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC)")
    L.append("")
    L.append("## En bref")
    L.append(f"- {len(verdicts)} règles ou configurations testées, dont {len(testees)} avec assez de trades pour conclure "
             f"(au moins {MIN_TRADES} trades et {MIN_EPISODES} épisodes).")
    if cand:
        L.append(f"- **{len(cand)} candidat(s)** : " + " ; ".join(f"{n} ({r_(s['r'])} par trade)" for n, _, s in cand)
                 + ". Un candidat n'est pas validé : il doit se confirmer en mode papier.")
    else:
        L.append("- **Aucune configuration n'a d'avantage statistique démontré après frais.**")
    if fragiles:
        L.append(f"- {len(fragiles)} positive(s) mais fragile(s) (instable d'une moitié à l'autre, pas mieux que la "
                 "référence, ou effacée par des coûts dégradés) : " + " ; ".join(n for n, _, _ in fragiles) + ".")
    if negatifs:
        L.append(f"- {len(negatifs)} nettement perdante(s) : " + " ; ".join(n for n, _, _ in negatifs) + ".")
    attendus = len(testees) * 0.025
    L.append(f"- Avec {len(testees)} tests, le hasard seul ferait ressortir environ {nb(attendus, 1)} faux « positif ». "
             "Un résultat isolé ne prouve rien.")
    b = wf["bilan"]
    if b.get("n", 0):
        L.append(f"- Hors échantillon (règle choisie chaque année sur le passé, puis suivie) : {b['n']} trades, "
                 f"{r_(b['r'])} par trade, intervalle {r_(b['lo'])} à {r_(b['hi'])}.")
    if eb:
        sens = "aucun lien mesurable" if eb["rho_lo"] <= 0 <= eb["rho_hi"] else (
            "lien positif" if eb["rho"] > 0 else "lien inverse")
        L.append(f"- Biais mécanique (cinq familles sur sept) et variation du prix à 7 jours : {sens} "
                 f"(corrélation de rang {nb(eb['rho'], 2)}, intervalle {nb(eb['rho_lo'], 2)} à {nb(eb['rho_hi'], 2)}).")
    L.append("- Le biais complet de la méthode (avec les flux des ETF et les événements) ne peut pas être rejoué sur le "
             "passé : seul le mode papier (`rapport/papier.md`) peut le juger.")
    L.append("")

    L.append("## Comment lire")
    L.append(f"- Données : bougies de 4 heures du {B['date'][0][:10]} au {B['date'][-1][:10]} ({nb(B['n'])} bougies).")
    L.append(f"- 1 R = la perte prévue quand le stop saute, frais ({nb(FRAIS * 100, 2)} % par ordre) et glissement "
             f"({nb(GLISSEMENT * 100, 2)} % au stop) compris. −0,10 R par trade : on perd 10 % de la mise risquée à chaque trade.")
    L.append("- Épisodes : les trades séparés de moins de 10 jours comptent comme un seul épisode de marché "
             "(30 jours au plus par épisode). "
             "L'intervalle à 95 % est calculé en tirant au sort des épisodes entiers (bootstrap par blocs).")
    L.append("- Référence : le même plan, avec des entrées toutes les 20 heures sans aucun signal. "
             "Une règle doit faire mieux pour avoir un intérêt.")
    L.append("- Avec financement réel : résultat sur les seuls trades dont le financement est connu "
             "(Kraken depuis un an, Deribit depuis 2019), comparé au même échantillon sans financement. "
             "Aucun financement n'est supposé quand il manque.")
    L.append(f"- Moitiés : avant et après le {t_milieu[:10]}. Coûts dégradés : frais doublés, glissement triplé.")
    L.append("- Verdicts : « candidat » exige un intervalle entièrement positif, deux moitiés positives, "
             "mieux que la référence et un résultat encore positif avec des coûts dégradés.")
    L.append("")

    L.append("## Règles journalières")
    L.append(f"Stop {nb(STOP * 100)} %, objectif {nb(OBJECTIF * 100, 1)} %, {DUREE} jours au plus, sortie unique.")
    L.append("")
    L += [ENTETE, SEP, *lignes_j, ""]

    L.append("## Configurations de la méthode, en bougies de 4 heures")
    L.append(f"Entrée à l'ouverture de la bougie qui suit le signal. Stop derrière l'extrême des 3 dernières bougies "
             f"(entre 1,5 % et 6 % ; au-delà, pas de trade). Moitié de la position sortie à {nb(M1, 1)} R, stop ramené "
             f"à l'entrée, reste à {nb(M2, 1)} R, {BARRES_MAX // 6} jours au plus.")
    L.append("")
    L += [ENTETE, SEP, *lignes_h, ""]
    L.append("Définitions : support et résistance = plus bas et plus haut des 20 derniers jours ; « rejet » = la bougie "
             "touche le niveau (à 0,3 % près) puis clôture du bon côté ; « cassure » = clôture journalière au-delà du "
             "niveau ; « rebond raté » = dans les 7 jours après une cassure, retour au contact du niveau puis clôture "
             "du mauvais côté.")
    L.append("")

    # Liquidité
    L.append("## Sensibilité à la liquidité (configurations 4 heures)")
    L.append("| Sens | Entrées en semaine | Entrées le week-end |")
    L.append("|---|---|---|")
    for sens, lib in ((1, "Long"), (-1, "Short")):
        tr = [t for cf in confs if cf["sens"] == sens for t in cf["trades"]]
        sem, we = [t["R"] for t in tr if not t["week_end"]], [t["R"] for t in tr if t["week_end"]]
        L.append(f"| {lib} | {r_(np.mean(sem)) if sem else 'n.d.'} sur {len(sem)} | "
                 f"{r_(np.mean(we)) if we else 'n.d.'} sur {len(we)} |")
    L.append("")

    if eb:
        L.append("## Le biais mécanique prédit-il la suite ?")
        L.append(f"Approximation du biais de la méthode sur cinq familles (structure, positionnement, blockchain, macro, "
                 f"actifs risqués), de −10 à +10, du {eb['debut']} au {eb['fin']}. Variation moyenne d'un jour "
                 f"quelconque à 7 jours : {p_(eb['moy7'])}.")
        L.append("")
        L.append("| Biais | Jours | Épisodes | Variation à 7 jours | Médiane | Hausse | À 14 jours | Écart à la moyenne | "
                 "Intervalle à 95 % de l'écart |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for x in eb["lignes"]:
            if x["jours"] == 0:
                L.append(f"| {x['classe']} | 0 | | | | | | | |")
                continue
            L.append(f"| {x['classe']} | {x['jours']} | {x['episodes']} | {p_(x['moy7'])} | {p_(x['med7'])} | "
                     f"{nb(x['pos7'] * 100)} % | {p_(x['moy14'])} | {p_(x['ecart'])} | {p_(x['lo'])} à {p_(x['hi'])} |")
        L.append("")
        L.append("Si l'intervalle de l'écart contient zéro, la classe ne se distingue pas d'un jour quelconque. "
                 "Blocs de 30 jours pour le bootstrap.")
        L.append("")

    L.append("## Hors échantillon : choisir sur le passé, appliquer ensuite")
    L.append("| Année suivie | Règle retenue au 1er janvier | R moyen sur le passé | Trades de l'année | R moyen de l'année |")
    L.append("|---|---|---|---|---|")
    for x in wf["lignes"]:
        L.append(f"| {x['an']} | {x['regle']} | {r_(x['passe'])} | {x['n']} | {r_(x['r'])} |")
    L.append("")

    L.append("## Robustesse des règles journalières")
    L.append("R moyen quand on change le stop et la durée (objectif = 1,6 fois le stop). Nombre de trades entre parenthèses.")
    L.append("")
    par_id = {r["id"]: r for r in regles_jour(J)}
    for cle in ("L2", "S1"):
        reg = par_id[cle]
        L.append(f"**{reg['id']} {reg['nom']}**")
        L.append("")
        L.append("| Stop | 3 jours | 7 jours | 14 jours |")
        L.append("|---|---|---|---|")
        for st in (0.03, 0.04, 0.06):
            cases = []
            for du in (3, 7, 14):
                tr = trades_jour(J, B, reg["m"].fillna(False), reg["sens"], st, st * 1.625, du)
                cases.append("aucun trade" if not tr else f"{r_(np.mean([t['R'] for t in tr]))} ({len(tr)})")
            L.append(f"| {nb(st * 100)} % | " + " | ".join(cases) + " |")
        L.append("")

    L.append("## Suivi de tendance sans stop, sans levier")
    L.append("| Stratégie | Période | Rendement annuel | Pire baisse | Temps en position | Détenir sur la même période |")
    L.append("|---|---|---|---|---|---|")
    for sens, nom in ((1, "Long au-dessus de la moyenne 200 jours"), (-1, "Short sous la moyenne 200 jours")):
        for avec, lib in ((False, "sans financement"), (True, "avec financement réel")):
            t = tendance(J, sens, avec)
            if t:
                L.append(f"| {nom}, {lib} | {t['debut']} au {t['fin']} | {p_(t['rendement'])} | {p_(t['creux'])} | "
                         f"{nb(t['temps'] * 100)} % | {p_(t['detenir'])} |")
    L.append("")

    L.append("## Limites")
    L.append("- Les définitions mécaniques approchent les configurations de la méthode ; elles ne reproduisent pas le "
             "jugement d'une analyse (choix des niveaux, lecture des flux, actualité).")
    L.append("- Les flux des ETF, les liquidations et les événements ne sont pas testés, faute d'historique gratuit.")
    L.append("- Le financement réel avant 2025 est celui de Deribit, pas de Kraken.")
    L.append("- Dans une bougie de 4 heures, l'ordre entre stop et objectif reste inconnu : le stop est compté.")
    L.append("- L'historique couvre surtout des marchés haussiers : les règles « long » y sont flattées, les « short » pénalisées.")
    L.append("- Aucun réglage n'a été ajusté pour améliorer ces résultats.")
    L.append("")

    trades = pd.DataFrame(tous)
    if len(trades):
        trades["sens"] = np.where(trades["sens"] == 1, "long", "short")
        trades = trades[["regle", "sens", "t_entree", "t_sortie", "entree", "stop", "d", "motif", "R", "R_fin", "R_stress"]]
    return "\n".join(L), trades


def main() -> int:
    os.makedirs(RAPPORT, exist_ok=True)
    sortie = os.path.join(RAPPORT, "backtest.md")
    donnees = charger()
    if donnees is None:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write("# Backtest BTC\n\nDonnées insuffisantes (prix journalier ou bougies de 4 heures manquants). "
                    "Relancer après une collecte réussie.\n")
        print("Backtest : données insuffisantes.")
        return 0
    texte, trades = rapport(*donnees)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(texte)
    trades.to_csv(os.path.join(RAPPORT, "trades.csv"), index=False, float_format="%.5g")
    print(f"Backtest : {len(trades)} trades simulés, rapport écrit dans {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
