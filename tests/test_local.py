#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests locaux, sans réseau.

1. Simulation d'un trade sur bougies de 4 heures : cas construits à la main.
2. Statistiques : épisodes, bootstrap par blocs.
3. Mode papier : chaque type de déclencheur.
4. Collecte : réponses simulées au format exact de chaque API, relance, pannes.
5. Backtest de bout en bout sur un historique artificiel, sans regard vers l'avenir.

Usage : python tests/test_local.py [--rapport]
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import tempfile
import zipfile

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="btc-test-")
os.environ["BTC_DATA_DIR"] = os.path.join(TMP, "data")
os.environ["BTC_RAPPORT_DIR"] = os.path.join(TMP, "rapport")
os.environ["BTC_PLANS"] = os.path.join(TMP, "papier", "plans.csv")
sys.path.insert(0, os.path.dirname(ICI))

import backtest  # noqa: E402
import collecte  # noqa: E402
import outils  # noqa: E402
import papier  # noqa: E402
import simulation as sim  # noqa: E402
import stats  # noqa: E402

ECHECS = []


def verifier(nom: str, condition: bool, detail: str = "") -> None:
    print(f"{'ok   ' if condition else 'ECHEC'} {nom} {detail}")
    if not condition:
        ECHECS.append(nom)


def proche(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


# ------------------------------------------------------------ 1. simulation
def bougies(lignes, debut="2024-01-01 00:00", fin=0.0):
    """lignes : (ouverture, haut, bas, clôture), bougies de 4 heures consécutives."""
    df = pd.DataFrame(lignes, columns=["ouverture", "haut", "bas", "cloture"]).astype(float)
    t0 = pd.Timestamp(debut)
    df["date"] = [(t0 + pd.Timedelta(hours=4 * i)).strftime("%Y-%m-%d %H:%M") for i in range(len(df))]
    jours = {d[:10] for d in df["date"]}
    return sim.barres(df, None if fin is None else {j: fin for j in jours})


def test_simulation():
    F, G = sim.FRAIS, sim.GLISSEMENT
    risque = 0.04 + 2 * F + G
    plat = (100, 100, 100, 100)

    B = bougies([(100, 102, 99, 101), (101, 107, 100, 106), plat])            # long, objectif unique
    t = sim.simuler(B, 0, 1, 96, None, 106.5, 2)
    verifier("long objectif unique", t["motif"] == "objectif" and proche(t["net"], 0.065 - 2 * F)
             and proche(t["R"], (0.065 - 2 * F) / risque), f"{t['R']:.3f}")

    B = bougies([(100, 101, 95, 96), plat])                                    # long, stop
    t = sim.simuler(B, 0, 1, 96, None, 106.5, 1)
    verifier("long stop = −1 R exactement", t["motif"] == "stop" and proche(t["R"], -1.0), f"{t['R']:.4f}")

    B = bougies([(100, 108, 95, 104), plat])                                   # les deux dans la même bougie
    t = sim.simuler(B, 0, 1, 96, None, 106.5, 1)
    verifier("même bougie : stop prioritaire", t["motif"] == "stop")

    B = bougies([(100, 101, 99, 100), (90, 91, 89, 90), plat])                 # ouverture en écart sous le stop
    t = sim.simuler(B, 0, 1, 96, None, 106.5, 2)
    verifier("écart : sortie à l'ouverture, pire que 1 R", t["motif"] == "stop" and t["R"] < -2.0, f"{t['R']:.2f}")

    B = bougies([(100, 101, 99, 100), (100, 102, 99, 101), (101, 103, 100, 102), (102, 110, 102, 110)])
    t = sim.simuler(B, 0, 1, 96, None, 106.5, 2)                                # sortie à la durée
    verifier("durée : clôture de la dernière bougie", t["motif"] == "durée" and proche(t["net"], 0.02 - 2 * F))

    B = bougies([(100, 101, 98, 99), (99, 100, 93, 94), plat])                 # short, objectif
    t = sim.simuler(B, 0, -1, 104, None, 93.5, 2)
    verifier("short objectif", t["motif"] == "objectif" and proche(t["net"], 0.065 - 2 * F))
    B = bougies([(100, 105, 99, 104), plat])
    t = sim.simuler(B, 0, -1, 104, None, 93.5, 1)
    verifier("short stop = −1 R", t["motif"] == "stop" and proche(t["R"], -1.0))

    # Gestion en deux temps : moitié à l'objectif 1, stop ramené à l'entrée, reste à l'objectif 2
    B = bougies([(100, 105, 99, 104), (104, 110, 103, 109), plat])
    t = sim.simuler(B, 0, 1, 96, 104.8, 109.6, 2)
    verifier("deux objectifs atteints", t["motif"] == "objectif"
             and proche(t["net"], 0.5 * 0.048 + 0.5 * 0.096 - 2 * F), f"{t['net']:.5f}")
    B = bougies([(100, 105, 99, 104), (104, 104, 99.5, 100), plat])
    t = sim.simuler(B, 0, 1, 96, 104.8, 109.6, 2)
    verifier("objectif 1 puis stop à l'entrée", t["motif"] == "stop à l'entrée"
             and proche(t["net"], 0.5 * 0.048 - 2 * F - 0.5 * G), f"{t['net']:.5f}")
    B = bougies([(100, 105, 99.5, 104), plat, plat])
    t = sim.simuler(B, 0, 1, 96, 104.8, 109.6, 0)
    verifier("stop à l'entrée inactif dans la bougie de l'objectif 1", t["motif"] == "objectif 1 puis durée"
             and proche(t["net"], 0.5 * 0.048 + 0.5 * 0.04 - 2 * F), f"{t['net']:.5f}")

    # Financement : jamais inventé
    B = bougies([(100, 101, 99, 100)] * 6, fin=0.0012)                           # 0,12 % par jour, 6 bougies
    tl, ts = sim.simuler(B, 0, 1, 90, None, 120, 5), sim.simuler(B, 0, -1, 110, None, 80, 5)
    rl = 0.10 + 2 * F + G
    verifier("financement : le long paie, le short encaisse",
             proche(tl["R_fin"], (-2 * F - 0.0012) / rl) and proche(ts["R_fin"], (-2 * F + 0.0012) / rl),
             f"{tl['R_fin']:.4f} {ts['R_fin']:.4f}")
    verifier("financement absent du résultat de base", proche(tl["R"], -2 * F / rl))
    B = bougies([(100, 101, 99, 100)] * 6, fin=None)
    t = sim.simuler(B, 0, 1, 90, None, 120, 5)
    verifier("financement inconnu : NaN, pas d'hypothèse", t["R_fin"] != t["R_fin"] and proche(t["R"], -2 * F / rl))

    verifier("stop déjà dépassé : pas de trade", sim.simuler(B, 0, 1, 101, None, 120, 5) is None)
    t = sim.simuler(bougies([(100, 101, 97, 98), plat]), 0, 1, 94, None, 110, 1, entree=98.0)
    verifier("ordre limite : entrée au prix demandé", proche(t["entree"], 98.0))
    verifier("stop de structure borné", sim.plan_structure(100, 1, 99.5)[1] == 0.015
             and sim.plan_structure(100, 1, 90) is None and proche(sim.plan_structure(100, -1, 103)[1], 0.03))
    verifier("coûts dégradés plus lourds", tl["R_stress"] < tl["R"])


# ------------------------------------------------------------ 2. statistiques
def test_stats():
    t = ["2024-01-01 00:00", "2024-01-03 00:00", "2024-01-05 00:00", "2024-02-01 00:00", "2024-02-02 00:00",
         "2024-03-20 00:00"]
    ep = stats.episodes(t)
    verifier("épisodes : écart de plus de 10 jours", list(ep) == [0, 0, 0, 1, 1, 2], str(list(ep)))
    continu = [f"2024-01-{j:02d} 00:00" for j in range(1, 29)] + [f"2024-02-{j:02d} 00:00" for j in range(1, 29)]
    verifier("épisodes : 30 jours au plus", stats.episodes(continu).max() == 1, str(stats.episodes(continu).max()))
    rng = np.random.default_rng(1)
    # 40 épisodes de 10 trades identiques : l'intervalle par épisodes doit être bien plus large que l'intervalle naïf
    moy = rng.normal(0.0, 1.0, 40)
    r = np.repeat(moy, 10)
    ep = np.repeat(np.arange(40), 10)
    lo, hi = stats.ic_episodes(r, ep)
    naif = 1.96 * r.std(ddof=1) / np.sqrt(len(r))
    verifier("bootstrap par épisodes plus large que l'intervalle naïf", (hi - lo) / 2 > 2.5 * naif,
             f"{(hi - lo) / 2:.3f} contre {naif:.3f}")
    verifier("intervalle autour de la moyenne", lo < r.mean() < hi)
    idx = next(stats.tirages_blocs(100, 30, 1))
    verifier("blocs consécutifs", len(idx) == 100 and (np.diff(idx)[:29] == 1).all())
    tr = [{"R": 1.0, "R_fin": float("nan"), "R_stress": 0.9, "t_entree": f"2024-{m:02d}-01 00:00"} for m in range(1, 13)]
    s = stats.resume(tr * 3, "2024-07-01")
    verifier("verdict : jamais « validé »", "candidat" in stats.verdict({**s, "lo": 0.5, "hi": 1.5, "episodes": 12}, 0.0)
             and stats.verdict({**s, "n": 10}, 0.0) == "échantillon insuffisant"
             and stats.verdict({**s, "lo": -0.1, "hi": 0.4, "episodes": 12}, 0.0) == "pas d'avantage démontré")


# ------------------------------------------------------------ 3. mode papier
def test_papier():
    base = {"id": "T", "source": "test", "risque_eur": "2.5", "zone_bas": "", "zone_haut": "", "niveau": "",
            "entree": "", "obj1": "", "expire_utc": "2024-01-03T00:00", "sortie_utc": "2024-01-04T00:00"}
    #            0 h              4 h              8 h               12 h             16 h            20 h
    B = bougies([(100, 101, 99, 100), (100, 103, 100, 102), (102, 102.5, 98, 98.5), (98.5, 99, 93, 94),
                 (94, 95, 93.5, 94), (94, 94, 94, 94), (94, 94, 94, 94)])
    # Short sur rebond raté : zone 101,5–103 touchée à 4 h, clôture sous 99 à 8 h, entrée à l'ouverture de 12 h
    pl = {**base, "cree_utc": "2024-01-01T03:00", "sens": "short", "declencheur": "zone_cloture_4h",
          "zone_bas": "101.5", "zone_haut": "103", "niveau": "99", "stop": "103.5", "obj2": "93.5"}
    r = papier.evaluer(pl, B)
    verifier("papier : rebond raté déclenché", r["etat"] == "clos" and r["t_entree"] == "2024-01-01 12:00"
             and proche(r["prix_entree"], 98.5) and r["motif"] == "objectif", str(r["etat"]) + " " + str(r["t_entree"]))
    verifier("papier : résultat en euros", proche(r["eur"], r["R"] * 2.5) and r["R"] > 0)
    # Même plan créé après le passage dans la zone : pas de déclenchement
    r = papier.evaluer({**pl, "cree_utc": "2024-01-01T08:30"}, B)
    verifier("papier : zone touchée avant la création, ignorée", r["etat"] == "en attente du déclencheur", r["etat"])
    # Expiration avant la clôture qui déclenche
    r = papier.evaluer({**pl, "expire_utc": "2024-01-01T10:00"}, B)
    verifier("papier : expiré sans entrée", r["etat"] == "expiré sans entrée", r["etat"])
    # Clôture journalière : seule la bougie de 20 h compte
    pj = {**base, "cree_utc": "2024-01-01T01:00", "sens": "short", "declencheur": "cloture_jour", "niveau": "95",
          "stop": "97", "obj2": "90"}
    r = papier.evaluer(pj, B)
    verifier("papier : clôture journalière", r["t_entree"] == "2024-01-02 00:00" and r["etat"] == "ouvert", r["etat"])
    r = papier.evaluer({**pj, "declencheur": "cloture_4h"}, B)
    verifier("papier : clôture 4 heures", r["t_entree"] == "2024-01-01 16:00", r["t_entree"])
    # Ordre limite long à 99 : touché dans la bougie de 8 h
    r = papier.evaluer({**base, "cree_utc": "2024-01-01T04:00", "sens": "long", "declencheur": "limite", "entree": "99",
                        "stop": "97", "obj2": "101"}, B)
    verifier("papier : ordre limite", r["t_entree"] == "2024-01-01 08:00" and proche(r["prix_entree"], 99.0)
             and r["motif"] == "stop", f"{r['t_entree']} {r['motif']}")
    r = papier.evaluer({**base, "cree_utc": "2024-01-01T00:00", "sens": "long", "declencheur": "immediat",
                        "stop": "", "obj2": "110"}, B)
    verifier("papier : plan incomplet signalé", r["etat"] == "plan incomplet")
    # Suivi heure par heure : plan créé à 0 h 08, zone touchée à 1 h, clôture 4 h (bougie de 3 h) sous le niveau
    hh = pd.DataFrame([(100, 100.5, 99.5, 100), (100, 102, 100, 101.5), (101.5, 101.6, 99, 99.5), (99.5, 99.8, 98, 98.6),
                       (98.6, 98.7, 96, 96.5), (96.5, 96.6, 93, 93.4), (93.4, 93.5, 93.2, 93.3)],
                      columns=["ouverture", "haut", "bas", "cloture"]).astype(float)
    hh["date"] = [f"2024-01-01 {k:02d}:00" for k in range(len(hh))]
    B1 = sim.barres(hh, {"2024-01-01": 0.0}, pas_h=1)
    ph = {**pl, "cree_utc": "2024-01-01T00:08", "zone_bas": "101.5", "zone_haut": "103", "niveau": "99"}
    r = papier.evaluer(ph, B1)
    verifier("papier : déclencheur à l'heure près", r["t_entree"] == "2024-01-01 04:00" and proche(r["prix_entree"], 98.6)
             and r["motif"] == "objectif", f"{r['etat']} {r['t_entree']}")
    r = papier.evaluer({**ph, "niveau": "99.6"}, B1)   # la clôture de 2 h est sous 99,6 mais ne termine pas une bougie de 4 h
    verifier("papier : seules les clôtures de 4 heures comptent", r["t_entree"] == "2024-01-01 04:00", r["t_entree"])
    r = papier.evaluer({**ph, "cree_utc": "2024-01-01T02:30"}, B1)   # créé après le passage dans la zone
    verifier("papier : heure de création respectée", r["etat"] != "clos", r["etat"])
    verifier("papier : référence long dénouée au stop", proche(papier.reference(pl, B, 1), -1.0))
    tard = {**pl, "cree_utc": "2024-01-02T00:00"}
    verifier("papier : référence non dénouée = NaN", papier.reference(tard, B, 1) != papier.reference(tard, B, 1))


def test_scenarios_et_bougies():
    # Choix des bougies : fixé par la date de création du plan
    def faux(nom):
        return {"t": np.array(["2026-11-01T00:00"], dtype="datetime64[s]"), "nom": nom}
    b1, b4, bk = faux("h1"), faux("h4"), faux("kraken")
    choix = lambda cree, k=bk: papier.choisir_bougies({"cree_utc": cree}, b1, b4, k)  # noqa: E731
    verifier("bougies : contrat Kraken à partir de la date de bascule seulement",
             choix("2026-11-15T18:59")[0]["nom"] == "h1" and choix("2026-11-15T18:59")[1] == "Coinbase"
             and choix("2026-11-15T19:00")[0]["nom"] == "kraken" and choix("2026-11-15T19:00")[1] == "contrat Kraken"
             and choix("2026-11-16T00:00", None)[0]["nom"] == "h1" and choix("2026-10-01T00:00")[0]["nom"] == "h4")
    verifier("configuration : lue dans la note, sinon dans la table",
             papier.configuration("P7", "Rebond raté ; configuration D-S au backtest : pas d avantage", {}) == "D-S"
             and papier.configuration("P8", "Cassure ; soumis à un financement", {}) == ""
             and papier.configuration("P8", "Cassure", {"P8": "C-S"}) == "C-S"
             and papier.configuration("P9", "config B-S-mm200", {}) == "B-S-mm200"
             and papier.configuration("P9", "B-L-mm200s : rebond sur la moyenne 200 semaines", {}) == "B-L-mm200s")
    # Scénario : jugé sur la clôture de la dernière bougie de 4 heures terminée à l'échéance
    B = bougies([(100, 101, 99, 100)] * 5 + [(100, 101, 94, 95), (95, 120, 95, 118), (118, 119, 117, 118)])
    sc = {"id": "S", "cree_utc": "2024-01-01T02:00", "horizon_j": "1", "seuil_bas": "100", "seuil_haut": "110",
          "p_baissier": "50", "p_neutre": "30", "p_haussier": "20"}
    tot = pd.Timestamp("2024-01-01T03:00", tz="UTC")
    r = papier.evaluer_scenario(sc, B, tot)
    verifier("scénario : issue, probabilité donnée et score de Brier", r["etat"] == "résolu" and r["issue"] == "baissier"
             and proche(r["prix"], 95) and proche(r["p_issue"], 0.5) and proche(r["brier"], 0.38) and r["compte"] == "oui",
             str(r))
    r = papier.evaluer_scenario(sc, B, pd.Timestamp("2024-01-01T09:00", tz="UTC"))
    verifier("scénario : enregistré trop tard, non compté", r["etat"] == "résolu" and r["compte"].startswith("non"))
    r = papier.evaluer_scenario({**sc, "horizon_j": "2"}, B, tot)
    verifier("scénario : en cours tant que l'échéance n'est pas couverte", r["etat"] == "en cours" and np.isnan(r["brier"]))
    r = papier.evaluer_scenario({**sc, "p_haussier": "10"}, B, tot)
    verifier("scénario : total différent de 100 % refusé", r["etat"].startswith("ligne illisible"))
    r = papier.evaluer_scenario({**sc, "cree_utc": "2024-01-01T08:00", "p_baissier": "0.2", "p_neutre": "0.3",
                                 "p_haussier": "0.5"}, B, pd.Timestamp("2024-01-01T08:30", tz="UTC"))
    verifier("scénario : haussier, probabilités en fractions acceptées", r["etat"] == "résolu" and r["issue"] == "haussier"
             and proche(r["p_issue"], 0.5), str(r))
    S = [{"cree": pd.Timestamp(f"2024-01-{j:02d}", tz="UTC"), "echeance": f"2024-01-{j + 7:02d} 00:00"} for j in (1, 3, 8, 20)]
    verifier("scénarios : prévisions indépendantes comptées sans recouvrement", papier.independantes(S) == 3)


def test_papier_v3():
    import alertes
    import regles
    base = {"id": "T", "source": "test", "risque_eur": "2.5", "zone_bas": "", "zone_haut": "", "niveau": "",
            "entree": "", "obj1": "", "expire_utc": "2024-01-03T00:00", "sortie_utc": "2024-01-04T00:00"}
    B = bougies([(100, 101, 99, 100), (100, 103, 100, 102), (102, 102.5, 98, 98.5), (98.5, 99, 93, 94),
                 (94, 95, 93.5, 94), (94, 94, 94, 94), (94, 94, 94, 94)])
    pl = {**base, "cree_utc": "2024-01-01T03:00", "sens": "short", "declencheur": "zone_cloture_4h",
          "zone_bas": "101.5", "zone_haut": "103", "niveau": "99", "stop": "103.5", "obj2": "93.5"}
    # Annulations : jamais rétroactives
    r = papier.evaluer(pl, B, annule=pd.Timestamp("2024-01-01T06:00", tz="UTC"))
    verifier("annulation avant l'entrée", r["etat"] == "annulé avant entrée", r["etat"])
    r = papier.evaluer({**pl, "obj2": "90"}, B, annule=pd.Timestamp("2024-01-01T13:00", tz="UTC"))
    verifier("annulation après l'entrée : sortie à la clôture suivante", r["etat"] == "clos"
             and r["motif"] == "sortie sur annulation" and r["t_sortie"] == "2024-01-01 12:00", f"{r['etat']} {r['motif']} {r['t_sortie']}")
    r = papier.evaluer({**pl, "obj2": "90"}, B, annule=pd.Timestamp("2024-01-01T17:00", tz="UTC"))
    verifier("annulation : jamais avant son heure", r["t_sortie"] == "2024-01-01 16:00", f"{r['etat']} {r['t_sortie']}")
    # Entrée théorique trop éloignée du prix prévu (short prévu à 99,5, ouverture à 98,5 : −1 %)
    r = papier.evaluer({**pl, "entree": "99.5"}, B)
    verifier("entrée à plus de 0,5 % du prix prévu : annulé", r["etat"].startswith("annulé : entrée trop"), r["etat"])
    r = papier.evaluer({**pl, "entree": "98.9"}, B)
    verifier("entrée à moins de 0,5 % : pris", r["etat"] == "clos", r["etat"])
    # Condition de financement, vérifiée à l'heure du déclenchement (12 h)
    t12 = np.datetime64("2024-01-01T12:00")
    fin_pos = pd.Series([0.01], index=[t12])
    fin_neg = pd.Series([-0.01], index=[t12])
    fin_vieux = pd.Series([0.01], index=[np.datetime64("2024-01-01T08:00")])
    c = {**pl, "condition_financement": "positif_ou_nul"}
    verifier("condition de financement remplie", papier.evaluer(c, B, fin_h=fin_pos)["etat"] == "clos")
    r = papier.evaluer(c, B, fin_h=fin_neg)
    verifier("condition de financement non remplie : abandonné", r["etat"].startswith("abandonné"), r["etat"])
    r = papier.evaluer(c, B, fin_h=fin_vieux)
    verifier("financement pas encore publié : en attente", "en attente de donnée" in r["etat"], r["etat"])
    r = papier.evaluer(c, B, fin_h=pd.Series([0.01, 0.01], index=[np.datetime64("2024-01-01T08:00"), np.datetime64("2024-01-01T20:00")]))
    verifier("financement inconnu au déclenchement : abandonné", r["etat"].startswith("abandonné : financement inconnu"), r["etat"])
    # Plan de règle : stop et objectif en pourcentage de l'entrée réelle
    pr = {"id": "S4-x", "cree_utc": "2024-01-01T07:30", "sens": "short", "declencheur": "immediat", "stop_pct": "0.04",
          "obj_pct": "0.05", "duree_h": "168", "expire_utc": "2024-01-01T13:30", "risque_eur": "2.5"}
    r = papier.evaluer(pr, B)
    verifier("plan de règle : entrée, stop et objectif relatifs", r["t_entree"] == "2024-01-01 08:00"
             and proche(r["stop_calcule"], 102 * 1.04) and proche(r["obj2_calcule"], 102 * 0.95) and r["motif"] == "objectif",
             f"{r['etat']} {r['motif']}")
    r = papier.evaluer({**pr, "cree_utc": "2024-01-01T21:00", "expire_utc": "2024-01-01T23:00"}, B)
    verifier("plan de règle : expiré si aucune bougie avant l'expiration", r["etat"] == "expiré sans entrée", r["etat"])
    # Empreintes
    e1 = papier.empreinte({"id": "P1", "stop": "100", "note": "x"})
    verifier("empreinte : colonne vide ajoutée sans effet", e1 == papier.empreinte({"id": "P1", "stop": "100", "note": "x", "cond": ""}))
    verifier("empreinte : valeur changée détectée", e1 != papier.empreinte({"id": "P1", "stop": "101", "note": "x"}))
    # Paliers des bilans
    verifier("paliers des bilans", papier.paliers_atteints(29) == [] and papier.paliers_atteints(30) == [30]
             and papier.paliers_atteints(149) == [30, 60, 100] and papier.paliers_atteints(150) == [30, 60, 100, 150]
             and papier.prochain_palier(0) == 30 and papier.prochain_palier(100) == 150)
    jours_ = pd.date_range("2024-01-01", periods=30, freq="12D").strftime("%Y-%m-%d %H:%M")
    bon = papier.bilans(pd.DataFrame({"t_entree": jours_, "R": [1.0, 0.5, 0.8] * 10}))
    peu = papier.bilans(pd.DataFrame({"t_entree": pd.date_range("2024-01-01", periods=30, freq="D").strftime("%Y-%m-%d %H:%M"),
                                      "R": [1.0] * 30}))
    verifier("bilan favorable à 30 plans", len(bon) == 1 and bon[0]["verdict"] == "favorable", str(bon))
    verifier("bilan : moins de 10 épisodes, pas de conclusion", peu[0]["verdict"].startswith("épisodes insuffisants"), str(peu))
    # Supports majeurs et condition du short
    n_ = 1500
    cl = np.r_[np.linspace(100, 200, n_ - 3), [150, 140, 145]]
    Js = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=n_, freq="D").strftime("%Y-%m-%d"),
                       "cloture": cl, "bas": cl * 0.99})
    Js["mm200s"] = Js["cloture"].rolling(1400).mean()
    Js["mm200"] = Js["cloture"].rolling(200).mean()
    s_ = regles.supports_majeurs(Js)
    etats = {x["nom"]: x["etat"] for x in s_["lignes"]}
    verifier("supports : moyenne 200 jours cassée, retournement exclu", etats["Moyenne 200 jours"] == "cassé"
             and s_["long_retournement"][0] is False, str(etats))
    Js2 = Js.copy()
    Js2.loc[Js2.index[-1], "cloture"] = 196.0      # reprise au-dessus de la moyenne 200 jours
    s2 = regles.supports_majeurs(Js2)
    verifier("supports : reprise en clôture reconnue", {x["nom"]: x["etat"] for x in s2["lignes"]}["Moyenne 200 jours"] == "repris")
    verifier("condition du short : active seulement si les trois", regles.condition_short({"pose": [1]}, -0.01, 10)[0] is True
             and regles.condition_short({"pose": [1]}, 0.01, 10)[0] is False and regles.condition_short({"pose": []}, -0.01, 10)[0] is False
             and regles.condition_short({"pose": [1]}, None, 10)[0] is None)
    # Alertes : simulation, une seule fois par événement
    sim_ = alertes.Simulation()
    x = {"id": "P9", "sens": "short", "etat": "déclenché, entrée à la prochaine bougie", "t_declenche": "2030-01-01 00:00",
         "entree_prevue": "63100", "stop": "64900", "obj1": "62000", "obj2": "59500", "risque_eur": "2.5", "detail": ""}
    titre, corps = alertes.corps_entree(x, 1.1, 63000.0, pd.Timestamp("2030-01-01T00:20", tz="UTC"))
    verifier("alerte : titre et ordres", "P9 déclenché" in titre and "marge isolée" in corps and "0,5 %" in corps
             and outils.prix(63100, 1.1) in corps and "@valentexi" in corps, titre)


# -------------------------------------------------------------- 4. collecte
class Reponse:
    def __init__(self, data=None, text="", content=b""):
        self._data, self.text, self.content, self.status_code = data, text, content, 200

    def json(self):
        return self._data


def historique(jours=1750, graine=7):
    """Historique artificiel heure par heure, avec phases de hausse et de baisse."""
    rng = np.random.default_rng(graine)
    fin = pd.Timestamp(dt.datetime.now(dt.timezone.utc)).tz_convert(None).floor("h")
    n = jours * 24
    t = pd.date_range(end=fin - pd.Timedelta(hours=1), periods=n, freq="h")
    derive = np.where((np.arange(n) // (300 * 24)) % 2 == 0, 0.00011, -0.00008)
    c = 5000 * np.exp(np.cumsum(rng.normal(derive, 0.0075)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.002, n)))
    b = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.002, n)))
    H = pd.DataFrame({"t": t, "o": o, "h": h, "l": b, "c": c})
    H["ts"] = (H["t"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    H["jour"] = H["t"].dt.strftime("%Y-%m-%d")
    g = H.groupby("jour")
    J = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last(),
                      "n": g["o"].count()}).reset_index()
    J = J[J["n"] == 24].reset_index(drop=True)
    var7 = J["c"].pct_change(7).fillna(0).to_numpy()
    J["peur"] = np.clip(50 + var7 * 250 + rng.normal(0, 8, len(J)), 3, 97).astype(int)
    return H, J


H1, JOURS = historique()
DATES = [dt.date.fromisoformat(d) for d in JOURS["jour"]]
AUJ = dt.datetime.now(dt.timezone.utc).date()
KRAKEN_ECART = 1.0005      # le contrat Kraken cote un peu différemment du comptant : l'écart rend les deux sources distinguables


def ts(d: dt.date) -> int:
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())


def faux_get(url, params=None, **_):
    params = params or {}
    if "coinbase" in url:   # [temps, bas, haut, ouverture, clôture, volume], récent d'abord
        if params["granularity"] == 3600:
            t0 = pd.Timestamp(params["start"]).tz_convert(None)
            t1 = pd.Timestamp(params["end"]).tz_convert(None)
            x = H1[(H1["t"] >= t0) & (H1["t"] <= t1)]
            return Reponse([[int(a), l, h, o, c, 10.0] for a, l, h, o, c in
                            zip(x["ts"], x["l"], x["h"], x["o"], x["c"])][::-1])
        d0, d1 = params["start"][:10], params["end"][:10]
        x = JOURS[(JOURS["jour"] >= d0) & (JOURS["jour"] <= d1)]
        lignes = [[ts(dt.date.fromisoformat(j)), l, h, o, c, 1000.0] for j, l, h, o, c in
                  zip(x["jour"], x["l"], x["h"], x["o"], x["c"])]
        if d1 >= AUJ.isoformat():   # bougie du jour, incomplète : doit être écartée
            lignes.append([ts(AUJ), 1.0, 1.0, 1.0, 1.0, 1.0])
        return Reponse(lignes[::-1])
    if "eurofxref" in url:
        csv = "Date,USD,JPY,\n" + "\n".join(
            f"{d.isoformat()},{1.10 + 0.0001 * (i % 50):.4f},160.0," for i, d in list(enumerate(DATES))[::-1]
            if d.weekday() < 5)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("eurofxref-hist.csv", csv)
        return Reponse(content=buf.getvalue())
    if "historicalfundingrates" in url:
        rates = []
        for d in DATES[-370:] + [AUJ]:
            for hh in range(24 if d != AUJ else 3):
                rates.append({"timestamp": f"{d.isoformat()}T{hh:02d}:00:00Z", "fundingRate": 1.3,
                              "relativeFundingRate": 0.0000125 if d.day % 5 else -0.00002})
        return Reponse({"result": "success", "serverTime": "x", "rates": rates})
    if "get_funding_rate_history" in url:
        t0, t1 = params["start_timestamp"] // 1000, params["end_timestamp"] // 1000
        x = H1[(H1["ts"] >= t0) & (H1["ts"] <= t1) & (H1["jour"] >= DATES[500].isoformat())]   # pas d'historique avant
        return Reponse({"jsonrpc": "2.0", "result": [
            {"timestamp": int(a) * 1000, "index_price": 1.0, "prev_index_price": 1.0, "interest_8h": 0.0001,
             "interest_1h": 0.00001 if int(a) // 86400 % 7 else -0.00003} for a in x["ts"]][-744:]})
    if "get_book_summary_by_currency" in url:
        e1 = (AUJ + dt.timedelta(days=12)).strftime("%d%b%y").upper().lstrip("0")
        e2 = (AUJ + dt.timedelta(days=200)).strftime("%d%b%y").upper()
        return Reponse({"jsonrpc": "2.0", "result": [
            {"instrument_name": f"BTC-{e1}-75000-P", "open_interest": 300.0, "volume": 30.0},
            {"instrument_name": f"BTC-{e1}-70000-C", "open_interest": 500.0, "volume": 20.0},
            {"instrument_name": f"BTC-{e1}-80000-C", "open_interest": 100.0, "volume": 10.0},
            {"instrument_name": f"BTC-{e2}-90000-C", "open_interest": 50.0, "volume": 0.0},
            {"instrument_name": "BTC-PERPETUAL", "open_interest": 1.0, "volume": 1.0}]})
    if url.endswith("/instruments"):
        paliers = [{"contracts": 0, "initialMargin": 0.1, "maintenanceMargin": 0.05},
                   {"contracts": 30000000, "initialMargin": 0.2, "maintenanceMargin": 0.1}]
        return Reponse({"result": "success", "instruments": [
            {"symbol": "PF_ETHUSD"},
            {"symbol": "PF_XBTUSD", "maxPositionSize": 1200, "maxRelativeFundingRate": 0.005, "feeScheduleUid": "u1",
             "marginLevels": [{"contracts": 0, "initialMargin": 0.01, "maintenanceMargin": 0.005}],
             "marginSchedules": {"europa": {"retail": paliers, "professional": paliers}}}]})
    if url.endswith("/feeschedules"):
        return Reponse({"feeSchedules": [{"uid": "u1", "tiers": [{"makerFee": 0.02, "takerFee": 0.05, "usdVolume": 0},
                                                                  {"makerFee": 0.015, "takerFee": 0.04, "usdVolume": 1e5}]}]})
    if "charts/v1" in url:   # contrat Kraken : temps en millisecondes, prix en texte, 1000 bougies au plus par appel
        x = H1[(H1["ts"] >= params["from"]) & (H1["ts"] <= params["to"])]
        lot = x.iloc[:1000]
        return Reponse({"candles": [{"time": int(a) * 1000, "open": f"{o * KRAKEN_ECART:.4f}", "high": f"{h * KRAKEN_ECART:.4f}",
                                     "low": f"{l * KRAKEN_ECART:.4f}", "close": f"{c * KRAKEN_ECART:.4f}", "volume": "12.5"}
                                    for a, o, h, l, c in zip(lot["ts"], lot["o"], lot["h"], lot["l"], lot["c"])],
                        "more_candles": len(x) > 1000})
    if "tickers/PF_XBTUSD" in url:
        return Reponse({"result": "success", "ticker": {
            "symbol": "PF_XBTUSD", "markPrice": 71410.18, "openInterest": 2568.4497, "vol24h": 6303.05,
            "relativeFundingRate": 0.000015378041666667, "relativeFundingRatePrediction": 0.000012484875}})
    if "public/ticker" in url:
        return Reponse({"result": {"open_interest": 1.2e9, "funding_8h": 0.00004}})
    if "get_volatility_index_data" in url:
        lignes = [[ts(d) * 1000, 40.0, 41.0, 39.0, 40.5] for d in DATES[-900:]
                  if params["start_timestamp"] <= ts(d) * 1000 <= params["end_timestamp"]]
        page, reste = lignes[-500:], lignes[:-500]   # deux pages, pour tester la suite
        return Reponse({"jsonrpc": "2.0", "result": {"data": page, "continuation": reste[-1][0] if reste else None}})
    if "alternative.me" in url:
        return Reponse({"name": "Fear and Greed Index", "metadata": {"error": None}, "data": [
            {"value": str(v), "value_classification": "x", "timestamp": str(ts(d))}
            for d, v in list(zip(DATES, JOURS["peur"]))[::-1]]})
    if "treasury.gov" in url:
        annee = int(url.split("daily-treasury-rates.csv/")[1][:4])
        if "real_yield" in url:
            raise RuntimeError("HTTP 404 simulé")   # une série en échec ne doit pas bloquer les autres
        lignes = [f"{d.strftime('%m/%d/%Y')},4.10,4.88,4.98,{5.0 + 0.3 * np.sin(i / 40):.2f},5.47"
                  for i, d in list(enumerate(DATES))[::-1] if d.year == annee and d.weekday() < 5]
        return Reponse(text='Date,"1 Mo","2 Yr","5 Yr","10 Yr","30 Yr"\n' + "\n".join(lignes))
    if "cboe.com" in url:
        lignes = [f"{d.strftime('%m/%d/%Y')},18.0,19.0,17.5,{18 + 9 * np.sin(i / 25):.2f}"
                  for i, d in enumerate(DATES) if d.weekday() < 5]
        lignes.append(f"{AUJ.strftime('%m/%d/%Y')},1,1,1,99.0")   # séance du jour : doit être écartée
        return Reponse(text="DATE,OPEN,HIGH,LOW,CLOSE\n" + "\n".join(lignes))
    if "finance.yahoo.com" in url:
        if "MNDY" in url:
            raise RuntimeError("HTTP 429 simulé")   # un titre en échec ne bloque pas les autres
        suit_btc = any(s in url for s in ("MSTR", "IREN", "CLSK", "SOL"))
        cours = dict(zip(JOURS["jour"], JOURS["c"]))
        jours = [d for d in DATES if (d.weekday() < 5 or "SOL" in url) and ts(d) >= params["period1"]]
        if suit_btc:   # actif qui amplifie le BTC d'un facteur 1,5
            vals = [float(cours[d.isoformat()]) ** 1.5 for d in jours]
        else:
            vals = [None if k % 61 == 0 else 25000.0 + 40 * np.sin(k / 9) + k for k in range(len(jours))]
        return Reponse({"chart": {"error": None, "result": [{
            "timestamp": [ts(d) + 52200 for d in jours], "indicators": {"quote": [{"close": vals}]}}]}})
    if "fredgraph" in url:
        raise RuntimeError("FRED ne répond pas (simulé)")
    if "coinmetrics" in url:
        m = params["metrics"]
        if m in ("FlowInExNtv", "FlowOutExNtv"):
            raise RuntimeError("HTTP 403 simulé")   # métriques absentes de l'offre gratuite
        data = []
        for i, d in enumerate(DATES):
            if d.isoformat() < params["start_time"]:
                continue
            x = {"asset": "btc", "time": f"{d.isoformat()}T00:00:00.000000000Z", f"{m.split(',')[0]}-status": "reviewed"}
            for k in m.split(","):
                x[k] = str({"PriceUSD": JOURS["c"][i], "CapMVRVCur": 0.8 + 2.6 * (0.5 + 0.5 * np.sin(i / 120)),
                            "SplyExNtv": 2.5e6 * (1 + 0.05 * np.sin(i / 60))}.get(k, 1.0))
            data.append(x)
        return Reponse({"data": data})
    raise RuntimeError(f"URL non prévue dans le test : {url}")


def etat():
    return json.load(open(outils.chemin("etat.json"), encoding="utf-8"))["sources"]


def test_collecte():
    collecte.get = faux_get
    collecte.time.sleep = lambda *_: None
    code = collecte.main()
    e = etat()
    verifier("collecte : code 0 et 14 sources ok", code == 0 and len(e) == 14 and all(x["ok"] for x in e.values()),
             str({k: v["note"] for k, v in e.items() if not v["ok"]}))
    hk = outils.lire("h1_kraken.csv")
    der = H1.iloc[-1]
    verifier("contrat Kraken : 60 jours d'heures, pagination, dernière heure terminée",
             hk is not None and 59 * 24 <= len(hk) <= 60 * 24 + 1 and hk["date"].is_unique
             and hk["date"].iloc[-1] == der["t"].strftime("%Y-%m-%d %H:%M")
             and proche(hk["cloture"].iloc[-1], der["c"] * KRAKEN_ECART, 1e-3)
             and proche(hk["bas"].iloc[-1], der["l"] * KRAKEN_ECART, 1e-3), str(None if hk is None else len(hk)))
    n_hk = len(hk)
    collecte.main()
    verifier("contrat Kraken : relance sans doublon", len(outils.lire("h1_kraken.csv")) == n_hk)

    p = outils.lire("btc_jour.csv")
    verifier("prix : jours complets, bougie du jour écartée", len(p) == len(DATES) and p["date"].max() == DATES[-1].isoformat())
    verifier("prix : colonnes dans le bon ordre", proche(p["haut"].iloc[-1], JOURS["h"].iloc[-1], 1e-3)
             and proche(p["bas"].iloc[-1], JOURS["l"].iloc[-1], 1e-3))
    verifier("prix : euros partout", p["cloture_eur"].notna().all()
             and proche(p["cloture_eur"].iloc[-1], p["cloture"].iloc[-1] / p["eurusd"].iloc[-1], 1e-6))

    h4 = outils.lire_h4()
    attendu = H1.assign(b=H1["ts"] // 14400).groupby("b").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"),
                                                                 c=("c", "last"), n=("o", "count"))
    complet = attendu[(attendu.index + 1) * 14400 <= dt.datetime.now(dt.timezone.utc).timestamp()]
    verifier("4 heures : nombre de bougies", len(h4) == len(complet), f"{len(h4)} / {len(complet)}")
    k = complet.iloc[-5]
    x = h4[h4["date"] == pd.to_datetime(complet.index[-5] * 14400, unit="s").strftime("%Y-%m-%d %H:%M")].iloc[0]
    verifier("4 heures : agrégation exacte", proche(x["ouverture"], k["o"], 1e-3) and proche(x["haut"], k["h"], 1e-3)
             and proche(x["bas"], k["l"], 1e-3) and proche(x["cloture"], k["c"], 1e-3))
    verifier("4 heures : calées sur 0, 4, 8... h UTC, un fichier par mois",
             set(h4["date"].str[11:]) == {"00:00", "04:00", "08:00", "12:00", "16:00", "20:00"}
             and len(os.listdir(outils.chemin("h4"))) > 50)

    h1 = outils.lire("h1_recent.csv")
    verifier("heures récentes : 75 jours au plus, heures terminées", 59 * 24 <= len(h1) <= 75 * 24 + 1
             and h1["date"].is_unique and h1["date"].max() == H1["t"].iloc[-1].strftime("%Y-%m-%d %H:%M"), str(len(h1)))

    f = outils.lire("financement_kraken.csv")
    verifier("financement Kraken : jour incomplet écarté, 0,01 % par 8 h",
             f["date"].max() == DATES[-1].isoformat() and (f["releves"] == 24).all()
             and proche(f["taux_8h_pct"].max(), 0.01, 1e-9))
    fd = outils.lire("financement_deribit.csv")
    verifier("financement Deribit : historique paginé", len(fd) > 1000 and fd["date"].is_unique and fd["date"].min() == DATES[500].isoformat()
             and proche(fd["cumul_jour_pct"].max(), 0.024, 1e-9), f"{len(fd)} jours")

    der = outils.lire("derives_instantane.csv").iloc[-1]
    verifier("options : rapport puts/calls", proche(der["options_puts_calls_oi"], 300 / 650, 1e-9)
             and proche(der["options_puts_calls_volume"], 1.0, 1e-9))
    verifier("options : échéance principale et max pain", proche(der["options_echeance_max_pain_usd"], 70000.0)
             and der["options_echeance"] == (AUJ + dt.timedelta(days=12)).isoformat(), str(der["options_echeance_max_pain_usd"]))
    verifier("dérivés et options sur la même ligne", proche(der["kraken_financement_8h_pct"], 0.000015378041666667 * 800, 1e-9))

    kc = outils.lire("kraken_contrat.csv").iloc[-1]
    verifier("contrat Kraken : barème Europe", proche(kc["marge_initiale"], 0.1) and proche(kc["marge_maintenance"], 0.05)
             and proche(kc["levier_max"], 10) and proche(kc["frais_preneur_pct"], 0.05))

    m = outils.lire("macro.csv")
    verifier("macro : séries présentes, échec partiel signalé", {"taux_10ans", "vix", "nasdaq100", "dxy"} <= set(m.columns)
             and "taux_reel_10ans" not in m.columns and "taux_reel_10ans" in e["macro"]["note"]
             and m["date"].max() < AUJ.isoformat())
    o = outils.lire("onchain.csv")
    verifier("onchain : sans colonne d'état", not any("-status" in c for c in o.columns) and "btc_sur_plateformes" in o.columns)

    be = pd.read_csv(outils.chemin("betas.csv"))
    b = be.set_index("actif")
    verifier("bêtas : actif qui amplifie le BTC de 1,5", abs(b.loc["Strategy (MSTR)", "beta_90j"] - 1.5) < 0.1
             and b.loc["Strategy (MSTR)", "correlation_90j"] > 0.95, f"{b.loc['Strategy (MSTR)', 'beta_90j']:.2f}")
    verifier("bêtas : actif sans lien", abs(b.loc["Microsoft", "beta_90j"]) < 0.3 and "Monday.com" not in b.index
             and "MNDY" in e["actifs"]["note"])

    verifier("fraîcheur : nature et âge de chaque source", all(x["fraicheur"].startswith("à jour") for x in e.values())
             and e["macro"]["nature"] == "différée" and e["options"]["nature"] == "instantanée"
             and e["prix"]["age_jours"] == 1, str({k: v["fraicheur"] for k, v in e.items() if not v["fraicheur"].startswith("à jour")}))
    texte = open(outils.chemin("dernier.md"), encoding="utf-8").read()
    verifier("relevé : sections nouvelles", all(s in texte for s in (
        "bougies de 4 heures", "Contrat perpétuel Kraken", "croisée par défaut", "Liens avec le Bitcoin",
        "toutes les sources sont à jour", "max pain", "€ (")))
    verifier("relevé : pas de valeur manquante affichée", re.search(r"\bnan\b", texte.lower()) is None)
    verifier("relevé : financement en direct et lecture mécanique", all(s_ in texte for s_ in (
        "Financement Kraken en direct", "les longs paient les shorts", "Biais mécanique à la clôture",
        "Supports majeurs", "Long de retournement :", "Condition éliminatoire du short")), texte[texte.find("## Dérivés"):][:300])
    fh = outils.lire("financement_kraken_h.csv")
    verifier("financement horaire enregistré", fh is not None and len(fh) > 24 * 100 and fh["date"].is_unique
             and proche(fh["taux_8h_pct"].iloc[0], 0.0000125 * 800) or proche(fh["taux_8h_pct"].iloc[0], -0.00002 * 800))

    # Deuxième lancement : rien n'est perdu, rien n'est dupliqué
    noms = ("btc_jour.csv", "financement_kraken.csv", "financement_deribit.csv", "dvol.csv", "macro.csv",
            "peur_avidite.csv", "onchain.csv", "eurusd.csv", "actifs.csv", "kraken_contrat.csv", "derives_instantane.csv")
    avant = {n: len(outils.lire(n)) for n in noms} | {"h4": len(outils.lire_h4())}
    collecte.main()
    apres = {n: len(outils.lire(n)) for n in noms} | {"h4": len(outils.lire_h4())}
    verifier("2e lancement : mêmes fichiers, pas de doublon", avant == apres and outils.lire_h4()["date"].is_unique,
             str({k: (avant[k], apres[k]) for k in avant if avant[k] != apres[k]}))

    # Pannes : une source secondaire, puis Coinbase
    def panne(url, params=None, **k):
        if "alternative.me" in url or "get_book_summary" in url:
            raise RuntimeError("panne simulée")
        return faux_get(url, params, **k)

    collecte.get = panne
    code = collecte.main()
    e = etat()
    texte = open(outils.chemin("dernier.md"), encoding="utf-8").read()
    verifier("panne secondaire : lancement réussi, anomalie affichée", code == 0 and not e["peur_avidite"]["ok"]
             and not e["options"]["ok"] and "2 source(s) en échec ou en retard" in texte
             and len(outils.lire("peur_avidite.csv")) == apres["peur_avidite.csv"])

    def sans_coinbase(url, params=None, **k):
        if "coinbase" in url:
            raise RuntimeError("panne simulée")
        if "api.kraken.com" in url:
            if params["interval"] == 240:
                x = H1.assign(b=H1["ts"] // 14400).groupby("b").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"),
                                                                      c=("c", "last")).iloc[-720:]
                return Reponse({"error": [], "result": {"XXBTZUSD": [
                    [int(b_) * 14400, str(r.o), str(r.h), str(r.l), str(r.c), "0", "1.0", 5] for b_, r in x.iterrows()],
                    "last": 1}})
            return Reponse({"error": [], "result": {"XXBTZUSD": [
                [ts(dt.date.fromisoformat(j)), str(o_), str(h_), str(l_), str(c_), "0", "12.5", 10]
                for j, o_, h_, l_, c_ in zip(JOURS["jour"], JOURS["o"], JOURS["h"], JOURS["l"], JOURS["c"])][-720:],
                "last": 1}})
        return faux_get(url, params, **k)

    collecte.get = sans_coinbase
    code = collecte.main()
    e = etat()
    verifier("secours Kraken : prix et 4 heures", code == 0 and "secours Kraken" in e["prix"]["note"]
             and "secours Kraken" in e["h4"]["note"] and len(outils.lire_h4()) == apres["h4"])
    collecte.get = faux_get
    collecte.main()


# -------------------------------------------------------- 5. bout en bout
def test_backtest():
    code = backtest.main()
    texte = open(os.path.join(outils.RAPPORT, "backtest.md"), encoding="utf-8").read()
    trades = pd.read_csv(os.path.join(outils.RAPPORT, "trades.csv"))
    verifier("backtest : rapport écrit", code == 0 and len(texte) > 4000)
    presentes = set(trades["regle"])
    verifier("backtest : règles journalières et configurations 4 h", {"L0", "L1", "L4", "S0", "A-L", "A-S", "C-L", "C-S",
                                                                       "D-S", "B-L-mm200", "B-S-mm50"} <= presentes,
             str(sorted(presentes)))
    verifier("backtest : pertes au stop bornées", trades["R"].min() > -4 and trades["R"].max() < 3,
             f"{trades['R'].min():.2f} à {trades['R'].max():.2f}")
    verifier("backtest : entrée avant la sortie", (trades["t_entree"] <= trades["t_sortie"]).all())
    verifier("backtest : financement réel sur une partie seulement", 0 < trades["R_fin"].notna().mean() < 1,
             f"{trades['R_fin'].notna().mean():.2f}")
    verifier("backtest : sections attendues", all(s in texte for s in (
        "## En bref", "Intervalle à 95 %", "Hors échantillon", "biais mécanique", "Sensibilité à la liquidité",
        "Avec financement réel", "Suivi de tendance")))
    verifier("backtest : pas de 'nan' dans le rapport", re.search(r"\bnan\b", texte.lower()) is None)
    verifier("backtest : aucun verdict « validé »", "validé" not in texte.replace("n'est pas validé", ""))

    # Aucun regard vers l'avenir : tronquer l'historique ne change aucun trade déjà dénoué
    J, B = backtest.charger()
    complet = {c["id"]: c["trades"] for c in backtest.configurations_h4(J, B)}
    lire0, h40 = backtest.lire, backtest.lire_h4
    coupe_j = J["date"].iloc[-200]
    backtest.lire = lambda nom: (lambda d: None if d is None else d[d["date"] <= coupe_j])(lire0(nom))
    backtest.lire_h4 = lambda: (lambda d: d[d["date"] < coupe_j + " 24"])(h40())
    try:
        J2, B2 = backtest.charger()
        tronque = {c["id"]: c["trades"] for c in backtest.configurations_h4(J2, B2)}
        jour_tr = backtest.trades_jour(J2, B2, (J2["peur"] <= 20).fillna(False), 1)
    finally:
        backtest.lire, backtest.lire_h4 = lire0, h40
    limite = J["date"].iloc[-215]
    n_cmp, identiques = 0, True
    for ident, tr in complet.items():
        a = [(t["t_entree"], round(t["R"], 9)) for t in tr if t["t_sortie"] < limite]
        b = [(t["t_entree"], round(t["R"], 9)) for t in tronque[ident] if t["t_sortie"] < limite]
        n_cmp += len(a)
        identiques &= a == b
    jour_c = backtest.trades_jour(J, B, (J["peur"] <= 20).fillna(False), 1)
    a = [(t["t_entree"], round(t["R"], 9)) for t in jour_c if t["t_sortie"] < limite]
    b = [(t["t_entree"], round(t["R"], 9)) for t in jour_tr if t["t_sortie"] < limite]
    verifier("backtest : aucun regard vers l'avenir", identiques and a == b and n_cmp > 200, f"{n_cmp + len(a)} trades comparés")
    verifier("backtest : biais mécanique borné", J["biais"].dropna().between(-10, 10).all() and J["biais"].notna().sum() > 200)

    # Mode papier de bout en bout
    os.makedirs(os.path.dirname(papier.PLANS), exist_ok=True)
    h4 = outils.lire_h4()
    ref = h4.iloc[-120]
    with open(papier.PLANS, "w", encoding="utf-8") as f_:
        f_.write("id,cree_utc,source,sens,declencheur,zone_bas,zone_haut,niveau,entree,stop,obj1,obj2,expire_utc,"
                 "sortie_utc,risque_eur,biais,note\n")
        f_.write(f"P1,{ref['date'].replace(' ', 'T')},test,long,immediat,,,,,{ref['cloture'] * 0.9},,"
                 f"{ref['cloture'] * 1.2},,{h4.iloc[-100]['date'].replace(' ', 'T')},2.5,0,test\n")
        f_.write(f"P2,{h4.iloc[-3]['date'].replace(' ', 'T')},test,short,cloture_jour,,,1,,2,,0.5,2099-01-01T00:00,,2.5,0,test\n")
        f_.write("P3,pas une date,test,long,immediat,,,,,1,,2,,,2.5,0,ligne abîmée\n")
    code = papier.main()
    res = pd.read_csv(papier.RESULTATS).set_index("id")
    txt = open(os.path.join(outils.RAPPORT, "papier.md"), encoding="utf-8").read()
    verifier("papier : bout en bout", code == 0 and res.loc["P1", "etat"] == "clos" and res.loc["P1", "motif"] == "durée"
             and res.loc["P2", "etat"] == "en attente du déclencheur" and "illisible" in res.loc["P3", "etat"]
             and "CRITÈRE NON ATTEINT" in txt, str(res["etat"].to_dict()))
    reg = pd.read_csv(papier.REGISTRE, dtype=str)
    verifier("registre : chaque plan enregistré une fois", sorted(reg["cle"]) == ["P1", "P2", "P3"])
    verifier("plan enregistré après son entrée : hors critère", res.loc["P1", "compte"] == "non"
             and "après l'entrée" in res.loc["P1", "raison"], str(res.loc["P1", "raison"]))
    # Modifier une ligne enregistrée : anomalie signalée, registre inchangé
    lignes_ = open(papier.PLANS, encoding="utf-8").read().replace("P2,", "P2,", 1).replace(",2099-01-01T00:00,", ",2098-01-01T00:00,")
    open(papier.PLANS, "w", encoding="utf-8").write(lignes_)
    papier.main()
    txt2 = open(os.path.join(outils.RAPPORT, "papier.md"), encoding="utf-8").read()
    reg2 = pd.read_csv(papier.REGISTRE, dtype=str)
    verifier("registre : modification après coup détectée", "P2 : modifiée après enregistrement" in txt2
             and reg2.equals(reg) and os.path.exists(os.path.join(papier.DOSSIER, "anomalies.csv")))
    # Alertes en simulation : rien d'enregistré hors de GitHub Actions
    import alertes
    alertes.main()
    verifier("alertes : simulation sans enregistrement", not os.path.exists(alertes.ALERTES))
    sim_ = alertes.Simulation()
    os.environ["BTC_MAINTENANT"] = str(pd.Timestamp(h4.iloc[-100]["date"]) + pd.Timedelta(hours=10))
    alertes.main(client=sim_)
    verifier("alertes : anomalie du registre signalée", any("registre papier" in e_[1] for e_ in sim_.envois), str(sim_.envois))
    n_envois = len(sim_.envois)
    alertes.main(client=sim_)
    verifier("alertes : pas de doublon", len(sim_.envois) == n_envois, str(len(sim_.envois)))
    del os.environ["BTC_MAINTENANT"]
    # Règle mécanique : inscrite d'office seulement si le signal est actif et frais
    import regles
    J_, _ = backtest.charger()
    b_ = regles.biais_du_jour(J_)
    seuil0 = [dict(r) for r in regles.REGLES_PAPIER]
    debut0 = regles.DEBUT_REGLES
    regles.DEBUT_REGLES = "2000-01-01"
    for r in regles.REGLES_PAPIER:
        r["seuil"] = b_["biais"]                       # force le signal sur la dernière clôture
    os.environ["BTC_MAINTENANT"] = str(pd.Timestamp(b_["date"]) + pd.Timedelta(hours=24, minutes=12))
    papier.main()
    pr_ = pd.read_csv(papier.PLANS_REGLES, dtype=str)
    papier.main()
    pr2 = pd.read_csv(papier.PLANS_REGLES, dtype=str)
    verifier("règles : plans inscrits d'office, une fois", len(pr_) == 2 and len(pr2) == 2
             and set(pr_["regle"]) == {"S4", "L7"}, str(pr_[["id", "cree_utc"]].values.tolist()))
    # Un passage en retard du robot ne décale pas l'étalon : le plan reste daté de la clôture (0 h UTC)
    cloture_ = (pd.Timestamp(b_["date"]) + pd.Timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    os.environ["BTC_MAINTENANT"] = str(pd.Timestamp(b_["date"]) + pd.Timedelta(hours=30))
    os.remove(papier.PLANS_REGLES)
    papier.main()
    pr3 = pd.read_csv(papier.PLANS_REGLES, dtype=str)
    verifier("règles : plan daté de la clôture, même inscrit en retard", len(pr3) == 2
             and set(pr_["cree_utc"]) == {cloture_} and set(pr3["cree_utc"]) == {cloture_}
             and pr3[papier.COLONNES_REGLES].equals(pr_[papier.COLONNES_REGLES]), str(pr3["cree_utc"].tolist()))
    os.environ["BTC_MAINTENANT"] = str(pd.Timestamp(b_["date"]) + pd.Timedelta(hours=49))
    os.remove(papier.PLANS_REGLES)
    papier.main()
    verifier("règles : signal trop ancien ignoré", not os.path.exists(papier.PLANS_REGLES))
    del os.environ["BTC_MAINTENANT"]
    regles.DEBUT_REGLES = debut0
    for r, r0 in zip(regles.REGLES_PAPIER, seuil0):
        r["seuil"] = r0["seuil"]
    # Scénarios et bougies du contrat Kraken, de bout en bout
    vieux, recent = h4.iloc[-60], h4.iloc[-3]
    with open(papier.SCENARIOS, "w", encoding="utf-8") as f_:
        f_.write(",".join(papier.COLONNES_SCENARIOS) + "\n")
        f_.write(f"SC1,{vieux['date'].replace(' ', 'T')},test,7,{vieux['cloture'] * 0.5},{vieux['cloture'] * 2},10,80,10,ancien\n")
        f_.write(f"SC2,{recent['date'].replace(' ', 'T')},test,7,{recent['cloture'] * 0.9},{recent['cloture'] * 1.1},40,40,20,récent\n")
    with open(papier.CONFIGURATIONS, "w", encoding="utf-8") as f_:
        f_.write("id,configuration\nP2,C-S\n")
    debut_k = papier.DEBUT_KRAKEN
    papier.DEBUT_KRAKEN = (pd.Timestamp(h4.iloc[-10]["date"])).strftime("%Y-%m-%dT%H:%M")   # P2 après, P1 avant
    try:
        papier.main()
    finally:
        papier.DEBUT_KRAKEN = debut_k
    txt3 = open(os.path.join(outils.RAPPORT, "papier.md"), encoding="utf-8").read()
    res3 = pd.read_csv(papier.RESULTATS, dtype=str).fillna("").set_index("id")
    reg3 = pd.read_csv(papier.REGISTRE, dtype=str)
    l1 = [x for x in txt3.split("\n") if x.startswith("| SC1 ")]
    l2 = [x for x in txt3.split("\n") if x.startswith("| SC2 ")]
    verifier("scénarios : section, résolu et en cours, registre", "## Scénarios à 7 jours" in txt3 and len(l1) == 1
             and "résolu" in l1[0] and "neutre" in l1[0] and "enregistré trop tard" in l1[0] and len(l2) == 1
             and "en cours" in l2[0] and {"scenario:SC1", "scenario:SC2"} <= set(reg3["cle"]), str(l1 + l2))
    verifier("papier : bougies du contrat Kraken pour les plans récents, Coinbase pour les anciens",
             res3.loc["P2", "bougies"] == "contrat Kraken" and res3.loc["P1", "bougies"] == "Coinbase"
             and res3.loc["P2", "configuration"] == "C-S" and "contrat perpétuel Kraken" in txt3
             and "## Par configuration et par jour d'entrée" in txt3, str(res3[["bougies", "configuration"]].to_dict()))
    return texte, txt


def test_controle_short():
    """Condition éliminatoire du short vérifiée par le robot au déclenchement (20 nov. 2026)."""
    # Journalier : clôture à 100, plus bas des 90 jours précédents à 98,5 (le prix est 1,5 % au-dessus : « posé »)
    n = 120
    dates = [(pd.Timestamp("2023-09-03") + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]
    J = pd.DataFrame({"date": dates, "cloture": 100.0, "bas": 99.5, "haut": 100.5, "mm200": np.nan})
    J.loc[n - 30, "bas"] = 98.5
    peur = pd.DataFrame({"date": dates + ["2023-12-31", "2024-01-01"], "valeur": [15.0] * (n + 2)})
    t_decl = np.datetime64("2024-01-01T12:00")          # veille : 2023-12-31, dernière ligne de J
    neg = pd.Series([-0.01], index=[t_decl])
    pos = pd.Series([0.01], index=[t_decl])
    actif, det, att = papier.controle_short(J, peur, neg)(t_decl)
    verifier("contrôle du short : posé + financement négatif + peur extrême = active", actif is True and not att, det)
    actif, det, att = papier.controle_short(J, peur, pos)(t_decl)
    verifier("contrôle du short : financement positif = inactive", actif is False and not att, det)
    actif, det, att = papier.controle_short(J, peur.assign(valeur=40.0), neg)(t_decl)
    verifier("contrôle du short : pas de peur extrême = inactive", actif is False, det)
    actif, det, att = papier.controle_short(J.assign(bas=90.0), peur, neg)(t_decl)
    verifier("contrôle du short : loin du support = inactive", actif is False, det)
    actif, det, att = papier.controle_short(J, peur, neg)(np.datetime64("2024-01-03T12:00"))
    verifier("contrôle du short : clôture pas encore collectée = en attente", actif is None and att, det)
    actif, det, att = papier.controle_short(J, peur, None)(t_decl)
    verifier("contrôle du short : financement absent = indéterminée", actif is None and not att, det)
    # Dans evaluer : même plan short qu'au test v3 (déclenché, entrée à 12 h le 1er janvier 2024)
    B = bougies([(100, 101, 99, 100), (100, 103, 100, 102), (102, 102.5, 98, 98.5), (98.5, 99, 93, 94),
                 (94, 95, 93.5, 94), (94, 94, 94, 94), (94, 94, 94, 94)])
    pl = {"id": "T", "source": "test", "risque_eur": "2.5", "cree_utc": "2024-01-01T03:00", "sens": "short",
          "declencheur": "zone_cloture_4h", "zone_bas": "101.5", "zone_haut": "103", "niveau": "99", "entree": "",
          "stop": "103.5", "obj1": "", "obj2": "93.5", "expire_utc": "2024-01-03T00:00", "sortie_utc": "2024-01-04T00:00"}
    def actif_(t):
        return True, "test", False
    def inactif(t):
        return False, "test", False
    def attente(t):
        return None, "test", True
    def inconnu(t):
        return None, "test", False
    r = papier.evaluer(pl, B, controle=actif_, debut_controle="2000-01-01T00:00")
    verifier("short déclenché avec la condition active : abandonné", r["etat"] == "abandonné : condition éliminatoire du short active", r["etat"])
    r = papier.evaluer(pl, B, controle=inactif, debut_controle="2000-01-01T00:00")
    verifier("short déclenché avec la condition inactive : pris", r["etat"] == "clos" and "inactive" in r["detail"], f"{r['etat']} {r['detail']}")
    r = papier.evaluer(pl, B, controle=attente, debut_controle="2000-01-01T00:00")
    verifier("contrôle en attente de donnée : plan en suspens", r["etat"].startswith("déclenché, contrôle"), r["etat"])
    r = papier.evaluer(pl, B, controle=inconnu, debut_controle="2000-01-01T00:00")
    verifier("contrôle indéterminé : abandonné", r["etat"].startswith("abandonné : condition éliminatoire du short indéterminée"), r["etat"])
    r = papier.evaluer(pl, B, controle=actif_)
    verifier("déclenchement antérieur au contrôle : jamais rejugé", r["etat"] == "clos", r["etat"])
    r = papier.evaluer({**pl, "sens": "long", "zone_bas": "93", "zone_haut": "95", "niveau": "94.5", "stop": "90",
                        "obj2": "120"}, B, controle=actif_, debut_controle="2000-01-01T00:00")
    verifier("contrôle du short : sans effet sur un long", not r["etat"].startswith("abandonné"), r["etat"])
    r = papier.evaluer({**pl, "condition_financement": "positif_ou_nul"}, B, fin_h=pd.Series([0.01], index=[np.datetime64("2024-01-01T12:00")]),
                       controle=inactif, debut_controle="2000-01-01T00:00")
    verifier("contrôle du short puis condition de financement : les deux détails gardés",
             r["etat"] == "clos" and "inactive" in r["detail"] and "financement au déclenchement" in r["detail"], r["detail"])
    # Registre : en cas de doublon après fusion de deux passages, la première vue la plus ancienne fait foi
    with tempfile.TemporaryDirectory() as d:
        ancien = papier.REGISTRE
        papier.REGISTRE = os.path.join(d, "registre.csv")
        e = papier.empreinte({"id": "P9"})
        pd.DataFrame([{"cle": "P9", "premiere_vue_utc": "2026-11-18T18:49:13Z", "empreinte": e},
                      {"cle": "P9", "premiere_vue_utc": "2026-11-18T14:52:02Z", "empreinte": e}]).to_csv(papier.REGISTRE, index=False)
        try:
            reg, anom = papier.tenir_registre([("P9", {"id": "P9"})], pd.Timestamp("2026-11-20", tz="UTC"))
        finally:
            papier.REGISTRE = ancien
        verifier("registre : doublon fusionné, la plus ancienne vue fait foi",
                 reg["P9"]["premiere_vue_utc"] == "2026-11-18T14:52:02Z" and not anom, str(reg["P9"]))


if __name__ == "__main__":
    test_simulation()
    test_stats()
    test_papier()
    test_papier_v3()
    test_controle_short()
    test_scenarios_et_bougies()
    test_collecte()
    rapport, pap = test_backtest()
    print()
    if ECHECS:
        print(f"{len(ECHECS)} ECHEC(S) : {ECHECS}")
        sys.exit(1)
    print("TOUS LES TESTS PASSENT")
    if "--rapport" in sys.argv:
        print("\n" + rapport + "\n" + pap)
        print(open(outils.chemin("dernier.md"), encoding="utf-8").read())
