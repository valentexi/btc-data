#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest de règles simples sur le Bitcoin, long et short.

Principes :
- Règles fixées à l'avance, aucun paramètre optimisé sur l'historique.
- Signal calculé à la clôture du jour J, entrée à l'ouverture du jour J+1.
- Si le stop et l'objectif sont touchés le même jour, on compte le stop (cas défavorable).
- Frais, glissement et financement déduits.
- Résultats exprimés en R : 1 R = la perte prévue quand le stop saute.

Lit data/*.csv, écrit rapport/backtest.md et rapport/trades.csv.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

from outils import RAPPORT, lire, nb, pct, prix

FRAIS = 0.0005        # 0,05 % par ordre au marché (Kraken)
GLISSEMENT = 0.0010   # 0,10 % quand le stop saute
FIN_HYP = 0.0003      # financement supposé quand la donnée manque : 0,01 % par 8 h
RISQUE_EUR = 5.0      # perte maximale par trade retenue dans le projet
STOP, OBJECTIF, DUREE = 0.04, 0.065, 7   # plan type : stop 4 %, objectif 6,5 %, 7 jours
MIN_TRADES = 30       # en dessous, on ne conclut pas


# ------------------------------------------------------------------- données
def charger() -> pd.DataFrame | None:
    p = lire("btc_jour.csv")
    if p is None or len(p) < 400:
        return None
    p = p.sort_values("date").reset_index(drop=True)
    if "eurusd" not in p.columns:
        p["eurusd"] = np.nan
    pa = lire("peur_avidite.csv")
    if pa is not None:
        p = p.merge(pa[["date", "valeur"]].rename(columns={"valeur": "peur"}), on="date", how="left")
    else:
        p["peur"] = np.nan
    fin = lire("financement_kraken.csv")
    if fin is not None:
        f = fin[["date", "cumul_jour_pct"]].copy()
        f["fin_jour"] = f["cumul_jour_pct"] / 100
        p = p.merge(f[["date", "fin_jour"]], on="date", how="left")
    else:
        p["fin_jour"] = np.nan
    c = p["cloture"]
    p["mm200"] = c.rolling(200).mean()
    p["var7"] = c / c.shift(7) - 1
    p["sous200"] = c < p["mm200"]
    p["sur200"] = c > p["mm200"]
    return p


# ---------------------------------------------------------------- simulation
def simuler(df: pd.DataFrame, signal: np.ndarray, sens: int, stop: float = STOP,
            objectif: float = OBJECTIF, duree: int = DUREE) -> list[dict]:
    """Une position à la fois. sens = +1 (long) ou -1 (short)."""
    o, h, b, c = (df[k].to_numpy(float) for k in ("ouverture", "haut", "bas", "cloture"))
    fin = df["fin_jour"].to_numpy(float)
    dates = df["date"].to_numpy()
    n, i, trades = len(df), 0, []
    risque = stop + 2 * FRAIS + GLISSEMENT
    while i < n - 1:
        if not signal[i]:
            i += 1
            continue
        e = i + 1
        entree = o[e]
        p_stop = entree * (1 - sens * stop)
        p_obj = entree * (1 + sens * objectif)
        sortie, motif, j = None, "", e
        dernier = min(e + duree, n) - 1
        for j in range(e, dernier + 1):
            if j > e:  # ouverture en écart au-delà d'un niveau
                if (sens == 1 and o[j] <= p_stop) or (sens == -1 and o[j] >= p_stop):
                    sortie, motif = o[j], "stop"
                    break
                if (sens == 1 and o[j] >= p_obj) or (sens == -1 and o[j] <= p_obj):
                    sortie, motif = o[j], "objectif"
                    break
            stop_touche = b[j] <= p_stop if sens == 1 else h[j] >= p_stop
            obj_touche = h[j] >= p_obj if sens == 1 else b[j] <= p_obj
            if stop_touche:  # prioritaire si les deux sont touchés le même jour
                sortie, motif = p_stop, "stop"
                break
            if obj_touche:
                sortie, motif = p_obj, "objectif"
                break
        if sortie is None:
            sortie, motif = c[j], "durée"
        brut = sens * (sortie / entree - 1)
        f = fin[e:j + 1]
        financement = sens * float(np.where(np.isnan(f), FIN_HYP, f).sum())
        net = brut - 2 * FRAIS - (GLISSEMENT if motif == "stop" else 0.0) - financement
        trades.append({
            "signal": dates[i], "entree": dates[e], "sortie": dates[j], "sens": "long" if sens == 1 else "short",
            "prix_entree": entree, "prix_sortie": sortie, "motif": motif,
            "brut": brut, "net": net, "R": net / risque, "eurusd": df["eurusd"].iloc[e],
        })
        i = j  # un nouveau signal à la clôture du jour de sortie est admis (entrée le lendemain)
    return trades


def bilan(trades: list[dict]) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0}
    r = np.array([t["R"] for t in trades])
    t_stat = float(r.mean() / (r.std(ddof=1) / np.sqrt(n))) if n > 1 and r.std(ddof=1) > 0 else 0.0
    serie, pire = 0, 0
    for x in r:
        serie = serie + 1 if x < 0 else 0
        pire = max(pire, serie)
    cumul = np.cumsum(r)
    creux = float((np.maximum.accumulate(np.maximum(cumul, 0)) - cumul).max())
    moitie = n // 2
    if n < MIN_TRADES:
        verdict = "échantillon insuffisant"
    elif t_stat >= 2:
        verdict = "positif"
    elif t_stat <= -2:
        verdict = "négatif"
    else:
        verdict = "non concluant"
    return {
        "n": n, "gagnants": float((r > 0).mean()), "r_moyen": float(r.mean()), "r_median": float(np.median(r)),
        "r_total": float(r.sum()), "t": t_stat, "pire_serie": pire, "creux": creux,
        "r_1": float(r[:moitie].mean()) if moitie else float("nan"),
        "r_2": float(r[moitie:].mean()) if moitie else float("nan"),
        "verdict": verdict,
    }


def regles(df: pd.DataFrame) -> list[dict]:
    """Les règles testées. Signal connu à la clôture du jour."""
    peur, var7 = df["peur"], df["var7"]
    sous, sur = df["sous200"], df["sur200"]
    lundi = pd.to_datetime(df["date"]).dt.dayofweek == 0
    a_fin = df["fin_jour"].notna()
    fin3 = df["fin_jour"].rolling(3).mean()
    return [
        {"id": "L0", "nom": "Référence : long chaque lundi", "sens": 1, "signal": lundi},
        {"id": "L1", "nom": "Long en peur extrême (Fear & Greed ≤ 20)", "sens": 1, "signal": peur <= 20},
        {"id": "L2", "nom": "Long en peur extrême, prix sous la moyenne 200 jours", "sens": 1,
         "signal": (peur <= 20) & sous},
        {"id": "L3", "nom": "Long en peur extrême, prix au-dessus de la moyenne 200 jours", "sens": 1,
         "signal": (peur <= 20) & sur},
        {"id": "L4", "nom": "Long après une purge (−10 % ou pire en 7 jours)", "sens": 1, "signal": var7 <= -0.10},
        {"id": "L5", "nom": "Long après une purge, prix sous la moyenne 200 jours", "sens": 1,
         "signal": (var7 <= -0.10) & sous},
        {"id": "L6", "nom": "Long quand le financement est négatif (moyenne 3 jours)", "sens": 1,
         "signal": a_fin & (fin3 < 0)},
        {"id": "S0", "nom": "Référence : short chaque lundi", "sens": -1, "signal": lundi},
        {"id": "S1", "nom": "Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours", "sens": -1,
         "signal": (var7 >= 0.08) & sous},
        {"id": "S2", "nom": "Short en avidité extrême (Fear & Greed ≥ 80)", "sens": -1, "signal": peur >= 80},
        {"id": "S3", "nom": "Short sous la moyenne 200 jours, chaque lundi", "sens": -1, "signal": lundi & sous},
    ]


# ------------------------------------------------------- étude d'événements
def episodes(masque: np.ndarray, ecart: int = 7) -> int:
    idx = np.flatnonzero(masque)
    if len(idx) == 0:
        return 0
    return int(1 + (np.diff(idx) > ecart).sum())


def etude(df: pd.DataFrame) -> list[dict]:
    c = df["cloture"]
    futurs = {h: (c.shift(-h) / c - 1) for h in (3, 7, 14, 30)}
    valide = df["mm200"].notna()
    peur, var7 = df["peur"], df["var7"]
    cas = [
        ("Tous les jours (référence)", valide),
        ("Prix au-dessus de la moyenne 200 jours", valide & df["sur200"]),
        ("Prix sous la moyenne 200 jours", valide & df["sous200"]),
        ("Peur extrême (≤ 20)", valide & (peur <= 20)),
        ("Peur extrême, sous la moyenne 200 jours", valide & (peur <= 20) & df["sous200"]),
        ("Peur extrême, au-dessus de la moyenne 200 jours", valide & (peur <= 20) & df["sur200"]),
        ("Avidité extrême (≥ 80)", valide & (peur >= 80)),
        ("Purge : −10 % ou pire en 7 jours", valide & (var7 <= -0.10)),
        ("Purge, sous la moyenne 200 jours", valide & (var7 <= -0.10) & df["sous200"]),
        ("Rebond : +8 % ou plus en 7 jours, sous la moyenne 200 jours", valide & (var7 >= 0.08) & df["sous200"]),
        ("Financement négatif (moyenne 3 jours)", valide & df["fin_jour"].notna()
         & (df["fin_jour"].rolling(3).mean() < 0)),
    ]
    lignes = []
    for nom, m in cas:
        m = m.fillna(False).to_numpy(bool)
        ligne = {"cas": nom, "jours": int(m.sum()), "episodes": episodes(m)}
        for h, f in futurs.items():
            x = f[m].dropna()
            ligne[f"moy{h}"] = float(x.mean()) if len(x) else float("nan")
            if h == 7:
                ligne["med7"] = float(x.median()) if len(x) else float("nan")
                ligne["pos7"] = float((x > 0).mean()) if len(x) else float("nan")
        lignes.append(ligne)
    return lignes


# ---------------------------------------------------------- suivi de tendance
def tendance(df: pd.DataFrame, sens: int) -> dict:
    d = df[df["mm200"].notna()].reset_index(drop=True)
    c = d["cloture"]
    signal = d["sur200"] if sens == 1 else d["sous200"]
    pos = signal.shift(1, fill_value=False).astype(float)   # position tenue le jour suivant le signal
    r = c.pct_change().fillna(0.0)
    fin = d["fin_jour"].fillna(FIN_HYP)
    changements = pos.diff().abs().fillna(pos.iloc[0])
    net = sens * pos * r - changements * (FRAIS + GLISSEMENT / 2) - sens * pos * fin
    courbe = (1 + net).cumprod()
    annees = len(d) / 365.25
    return {
        "rendement": float(courbe.iloc[-1] ** (1 / annees) - 1),
        "creux": float((courbe / courbe.cummax() - 1).min()),
        "temps": float(pos.mean()),
        "allers_retours": int(changements.sum() / 2),
        "detenir": float((c.iloc[-1] / c.iloc[0]) ** (1 / annees) - 1),
        "detenir_creux": float((c / c.cummax() - 1).min()),
        "debut": d["date"].iloc[0], "fin": d["date"].iloc[-1],
    }


# -------------------------------------------------------------------- rapport
def r_txt(x: float) -> str:
    return "n.d." if x != x else f"{x:+.2f}".replace(".", ",") + " R"


def p_txt(x: float, d: int = 1) -> str:
    return "n.d." if x != x else pct(x, d)


def rapport(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    L: list[str] = []
    L.append(f"# Backtest BTC ({dt.datetime.now(dt.timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC)")
    L.append("")
    debut, fin_d = df["date"].iloc[0], df["date"].iloc[-1]
    n_peur = int(df["peur"].notna().sum())
    n_fin = int(df["fin_jour"].notna().sum())

    resultats, tous = [], []
    for reg in regles(df):
        s = reg["signal"].fillna(False).to_numpy(bool)
        tr = simuler(df, s, reg["sens"])
        for t in tr:
            t["regle"] = reg["id"]
        tous += tr
        resultats.append((reg, bilan(tr), tr))

    par_id = {reg["id"]: (reg, b, tr) for reg, b, tr in resultats}

    # --- En bref
    L.append("## En bref")
    for cle, libelle in (("L2", "Long de retournement en peur extrême sous la moyenne 200 jours"),
                         ("S1", "Short sur rebond sous la moyenne 200 jours")):
        _, b, _ = par_id[cle]
        if b["n"] == 0:
            L.append(f"- **{libelle}** : aucun trade dans l'historique.")
        else:
            L.append(
                f"- **{libelle}** : {b['n']} trades, {nb(b['gagnants'] * 100)} % gagnants, {r_txt(b['r_moyen'])} "
                f"par trade en moyenne, soit {nb(b['r_moyen'] * RISQUE_EUR, 2)} € pour {nb(RISQUE_EUR)} € risqués. "
                f"Verdict : **{b['verdict']}**."
            )
    _, b0, _ = par_id["L0"]
    if b0["n"]:
        L.append(f"- Référence, long chaque lundi avec le même plan : {r_txt(b0['r_moyen'])} par trade "
                 f"sur {b0['n']} trades. Une règle n'a d'intérêt que si elle fait nettement mieux.")
    L.append("")

    # --- Données
    L.append("## Données")
    L.append(f"- Prix quotidien du {debut} au {fin_d}, soit {nb(len(df))} jours.")
    L.append(f"- Fear & Greed disponible sur {nb(n_peur)} jours, financement Kraken sur {nb(n_fin)} jours.")
    L.append(f"- Plan type : stop {nb(STOP * 100, 1)} %, objectif {nb(OBJECTIF * 100, 1)} %, {DUREE} jours au plus.")
    L.append(f"- Coûts : {nb(FRAIS * 100, 2)} % par ordre, {nb(GLISSEMENT * 100, 2)} % de glissement au stop, "
             f"financement réel quand il est connu, sinon {nb(FIN_HYP / 3 * 100, 2)} % par 8 h.")
    L.append(f"- 1 R = la perte prévue au stop. Avec {nb(RISQUE_EUR)} € risqués par trade, +0,20 R vaut 1 €.")
    L.append("")

    # --- Étude d'événements
    L.append("## Ce que fait le prix après chaque situation")
    L.append("Variation moyenne du prix dans les jours qui suivent, sans stop ni objectif. "
             "Les jours d'un même épisode se chevauchent : le nombre d'épisodes compte plus que le nombre de jours.")
    L.append("")
    L.append("| Situation | Jours | Épisodes | 3 j | 7 j | Médiane 7 j | Hausse à 7 j | 14 j | 30 j |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for e in etude(df):
        pos = "n.d." if e["pos7"] != e["pos7"] else f"{nb(e['pos7'] * 100)} %"
        L.append(f"| {e['cas']} | {e['jours']} | {e['episodes']} | {p_txt(e['moy3'])} | {p_txt(e['moy7'])} | "
                 f"{p_txt(e['med7'])} | {pos} | {p_txt(e['moy14'])} | {p_txt(e['moy30'])} |")
    L.append("")

    # --- Règles
    L.append("## Règles avec stop et objectif")
    L.append("| Règle | Trades | Gagnants | R moyen | R médian | R total | 1re moitié | 2e moitié | "
             "Pire série | Verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for reg, b, _ in resultats:
        if b["n"] == 0:
            L.append(f"| {reg['id']} {reg['nom']} | 0 | | | | | | | | pas de donnée |")
            continue
        L.append(
            f"| {reg['id']} {reg['nom']} | {b['n']} | {nb(b['gagnants'] * 100)} % | {r_txt(b['r_moyen'])} | "
            f"{r_txt(b['r_median'])} | {r_txt(b['r_total'])} | {r_txt(b['r_1'])} | {r_txt(b['r_2'])} | "
            f"{b['pire_serie']} pertes | {b['verdict']} |"
        )
    L.append("")
    L.append(f"Lecture : « positif » ou « négatif » seulement si l'écart à zéro est net (au moins {MIN_TRADES} "
             "trades et un résultat stable). Les colonnes « moitié » comparent le début et la fin de l'historique : "
             "un signe qui change indique une règle fragile.")
    L.append("")

    # --- Robustesse
    L.append("## Robustesse")
    L.append("R moyen par trade quand on change le stop et la durée (objectif = 1,6 fois le stop). "
             "Ce n'est pas une recherche du meilleur réglage : si le signe change d'une case à l'autre, "
             "le résultat ne tient pas. Nombre de trades entre parenthèses.")
    L.append("")
    for cle in ("L2", "S1"):
        reg, _, _ = par_id[cle]
        s = reg["signal"].fillna(False).to_numpy(bool)
        L.append(f"**{reg['id']} {reg['nom']}**")
        L.append("")
        L.append("| Stop | 3 jours | 7 jours | 14 jours |")
        L.append("|---|---|---|---|")
        for st in (0.03, 0.04, 0.06):
            cases = []
            for du in (3, 7, 14):
                b = bilan(simuler(df, s, reg["sens"], st, st * 1.625, du))
                cases.append("aucun trade" if b["n"] == 0 else f"{r_txt(b['r_moyen'])} ({b['n']})")
            L.append(f"| {nb(st * 100)} % | " + " | ".join(cases) + " |")
        L.append("")

    # --- Tendance
    L.append("## Suivi de tendance (sans stop)")
    L.append("| Stratégie | Rendement annuel | Pire baisse | Temps en position | Allers-retours |")
    L.append("|---|---|---|---|---|")
    tl, ts = tendance(df, 1), tendance(df, -1)
    L.append(f"| Détenir du Bitcoin | {p_txt(tl['detenir'])} | {p_txt(tl['detenir_creux'])} | 100 % | 0 |")
    L.append(f"| Long seulement au-dessus de la moyenne 200 jours | {p_txt(tl['rendement'])} | {p_txt(tl['creux'])} | "
             f"{nb(tl['temps'] * 100)} % | {tl['allers_retours']} |")
    L.append(f"| Short seulement sous la moyenne 200 jours | {p_txt(ts['rendement'])} | {p_txt(ts['creux'])} | "
             f"{nb(ts['temps'] * 100)} % | {ts['allers_retours']} |")
    L.append("")
    L.append(f"Période : du {tl['debut']} au {tl['fin']}. Sans levier.")
    L.append("")

    # --- Derniers trades
    for cle in ("L2", "S1"):
        reg, _, tr = par_id[cle]
        if not tr:
            continue
        L.append(f"## Derniers trades simulés : {reg['id']} {reg['nom']}")
        L.append("| Entrée | Prix d'entrée | Sortie | Motif | Résultat |")
        L.append("|---|---|---|---|---|")
        for t in tr[-8:]:
            fx = t["eurusd"]
            p_e = prix(t["prix_entree"], fx) if fx == fx else nb(t["prix_entree"]) + " $ (taux EUR/USD manquant)"
            L.append(f"| {t['entree']} | {p_e} | {t['sortie']} | {t['motif']} | {r_txt(t['R'])} |")
        L.append("")

    # --- Limites
    L.append("## Limites")
    L.append("- Données quotidiennes : l'ordre exact entre stop et objectif dans une même journée est inconnu "
             "(on compte le stop).")
    L.append("- Le Fear & Greed n'existe que depuis 2018 et le financement Kraken sur environ un an : "
             "peu d'épisodes indépendants.")
    L.append("- Les trades d'un même épisode ne sont pas indépendants : la netteté des verdicts est surestimée.")
    L.append("- Le passé couvre surtout des cycles haussiers. Une règle « long » y est flattée.")
    L.append("- Les flux des ETF et les liquidations ne sont pas testés (pas de source gratuite).")
    L.append("- Un backtest positif ne garantit rien : il sert à écarter les idées qui n'ont jamais marché.")
    L.append("")

    trades = pd.DataFrame(tous)
    if len(trades):
        trades = trades[["regle", "sens", "signal", "entree", "sortie", "prix_entree", "prix_sortie", "eurusd",
                         "motif", "brut", "net", "R"]]
    return "\n".join(L), trades


def main() -> int:
    os.makedirs(RAPPORT, exist_ok=True)
    df = charger()
    sortie = os.path.join(RAPPORT, "backtest.md")
    if df is None:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write("# Backtest BTC\n\nDonnées de prix insuffisantes (moins de 400 jours). "
                    "Relancer après une collecte réussie.\n")
        print("Backtest : données insuffisantes.")
        return 0
    texte, trades = rapport(df)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(texte)
    trades.to_csv(os.path.join(RAPPORT, "trades.csv"), index=False, float_format="%.8g")
    print(f"Backtest : {len(trades)} trades simulés, rapport écrit dans {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
