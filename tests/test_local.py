#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests locaux, sans réseau.

1. Simulation : cas construits à la main (stop, objectif, les deux le même jour, écart, durée, short).
2. Collecte : réponses simulées dans le format exact renvoyé par chaque API.
3. Bout en bout : collecte simulée puis backtest sur un historique artificiel.

Usage : python tests/test_local.py
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
sys.path.insert(0, os.path.dirname(ICI))

import backtest  # noqa: E402
import collecte  # noqa: E402
import outils  # noqa: E402

ECHECS = []


def verifier(nom: str, condition: bool, detail: str = "") -> None:
    print(f"{'ok   ' if condition else 'ECHEC'} {nom} {detail}")
    if not condition:
        ECHECS.append(nom)


def proche(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


# ------------------------------------------------------------ 1. simulation
def bougies(lignes):
    """lignes : (ouverture, haut, bas, clôture)."""
    df = pd.DataFrame(lignes, columns=["ouverture", "haut", "bas", "cloture"]).astype(float)
    df["date"] = [(dt.date(2024, 1, 1) + dt.timedelta(days=i)).isoformat() for i in range(len(df))]
    df["fin_jour"] = 0.0      # pas de financement, pour vérifier les calculs à la main
    df["eurusd"] = 1.10
    return df


def test_simulation():
    risque = 0.04 + 2 * backtest.FRAIS + backtest.GLISSEMENT
    sig = np.array([True, False, False, False, False])

    # Long, objectif touché le 2e jour de position
    df = bougies([(100, 100, 100, 100), (100, 102, 99, 101), (101, 107, 100, 106), (106, 106, 105, 105),
                  (105, 105, 105, 105)])
    t = backtest.simuler(df, sig, 1)[0]
    verifier("long objectif : motif", t["motif"] == "objectif")
    verifier("long objectif : net", proche(t["net"], 0.065 - 2 * backtest.FRAIS), f"{t['net']:.5f}")
    verifier("long objectif : R", proche(t["R"], (0.065 - 0.001) / risque), f"{t['R']:.3f}")

    # Long, stop touché
    df = bougies([(100, 100, 100, 100), (100, 101, 95, 96), (96, 97, 95, 96), (96, 96, 96, 96), (96, 96, 96, 96)])
    t = backtest.simuler(df, sig, 1)[0]
    verifier("long stop : motif", t["motif"] == "stop")
    verifier("long stop : perte = 1 R exactement", proche(t["R"], -1.0), f"{t['R']:.4f}")

    # Stop et objectif touchés le même jour : on compte le stop
    df = bougies([(100, 100, 100, 100), (100, 108, 95, 104), (104, 104, 104, 104), (104, 104, 104, 104),
                  (104, 104, 104, 104)])
    t = backtest.simuler(df, sig, 1)[0]
    verifier("même jour : stop prioritaire", t["motif"] == "stop")

    # Ouverture en écart sous le stop : sortie à l'ouverture, perte supérieure à 1 R
    df = bougies([(100, 100, 100, 100), (100, 101, 99, 100), (90, 91, 89, 90), (90, 90, 90, 90), (90, 90, 90, 90)])
    t = backtest.simuler(df, sig, 1)[0]
    verifier("écart : sortie à l'ouverture", t["motif"] == "stop" and proche(t["prix_sortie"], 90.0))
    verifier("écart : perte pire que 1 R", t["R"] < -2.0, f"{t['R']:.2f}")

    # Sortie à la durée : clôture du 3e jour avec durée = 3
    df = bougies([(100, 100, 100, 100), (100, 101, 99, 100), (100, 102, 99, 101), (101, 103, 100, 102),
                  (102, 110, 102, 110)])
    t = backtest.simuler(df, sig, 1, duree=3)[0]
    verifier("durée : motif et prix", t["motif"] == "durée" and proche(t["prix_sortie"], 102.0))
    verifier("durée : net", proche(t["net"], 0.02 - 2 * backtest.FRAIS), f"{t['net']:.5f}")

    # Short, objectif touché (miroir du long)
    df = bougies([(100, 100, 100, 100), (100, 101, 98, 99), (99, 100, 93, 94), (94, 94, 94, 94), (94, 94, 94, 94)])
    t = backtest.simuler(df, sig, -1)[0]
    verifier("short objectif : motif", t["motif"] == "objectif" and t["sens"] == "short")
    verifier("short objectif : net", proche(t["net"], 0.065 - 2 * backtest.FRAIS), f"{t['net']:.5f}")

    # Short, stop touché
    df = bougies([(100, 100, 100, 100), (100, 105, 99, 104), (104, 104, 104, 104), (104, 104, 104, 104),
                  (104, 104, 104, 104)])
    t = backtest.simuler(df, sig, -1)[0]
    verifier("short stop : perte = 1 R", t["motif"] == "stop" and proche(t["R"], -1.0), f"{t['R']:.4f}")

    # Financement : un long paie quand il est positif, un short encaisse
    df = bougies([(100, 100, 100, 100), (100, 101, 99, 100), (100, 101, 99, 100), (100, 100, 100, 100),
                  (100, 100, 100, 100)])
    df["fin_jour"] = 0.001
    tl = backtest.simuler(df, sig, 1, duree=2)[0]
    ts = backtest.simuler(df, sig, -1, duree=2)[0]
    verifier("financement : le long paie", proche(tl["net"], -2 * backtest.FRAIS - 0.002), f"{tl['net']:.5f}")
    verifier("financement : le short encaisse", proche(ts["net"], -2 * backtest.FRAIS + 0.002), f"{ts['net']:.5f}")

    # Une position à la fois, et pas d'entrée sur un signal donné le dernier jour
    df = bougies([(100, 100, 100, 100)] * 12)
    tr = backtest.simuler(df, np.array([True] * 12), 1, duree=3)
    verifier("une position à la fois", [t["entree"][-2:] for t in tr] == ["02", "05", "08", "11"],
             str([t["entree"][-2:] for t in tr]))

    # Épisodes : jours séparés de plus de 7 jours = épisodes distincts
    m = np.zeros(40, bool)
    m[[1, 2, 3, 20, 21, 35]] = True
    verifier("épisodes", backtest.episodes(m) == 3)


# -------------------------------------------------------------- 2. collecte
class Reponse:
    def __init__(self, data=None, text="", content=b""):
        self._data, self.text, self.content, self.status_code = data, text, content, 200

    def json(self):
        return self._data


def historique(n=3300, graine=7):
    """Historique artificiel avec phases de hausse et de baisse."""
    rng = np.random.default_rng(graine)
    fin = dt.date.today() - dt.timedelta(days=1)
    dates = [fin - dt.timedelta(days=n - 1 - i) for i in range(n)]
    derive = np.where((np.arange(n) // 400) % 2 == 0, 0.0025, -0.0018)
    r = rng.normal(derive, 0.035)
    c = 5000 * np.exp(np.cumsum(r))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.012, n)))
    b = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.012, n)))
    var7 = pd.Series(c).pct_change(7).fillna(0).to_numpy()
    peur = np.clip(50 + var7 * 250 + rng.normal(0, 8, n), 3, 97).astype(int)
    return dates, o, h, b, c, peur


DATES, O, H, B, C, PEUR = historique()


def ts(d: dt.date) -> int:
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())


def faux_get(url, params=None, **_):
    params = params or {}
    if "coinbase" in url:  # [temps, bas, haut, ouverture, clôture, volume], récent d'abord
        d0 = dt.date.fromisoformat(params["start"][:10])
        d1 = dt.date.fromisoformat(params["end"][:10])
        lignes = [[ts(d), B[i], H[i], O[i], C[i], 1000.0] for i, d in enumerate(DATES) if d0 <= d <= d1]
        if d1 >= dt.date.today():  # bougie du jour, incomplète : doit être écartée
            lignes.append([ts(dt.date.today()), 1.0, 1.0, 1.0, 1.0, 1.0])
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
        for d in DATES[-370:] + [dt.date.today()]:
            heures = 24 if d != dt.date.today() else 5
            for hh in range(heures):
                rates.append({"timestamp": f"{d.isoformat()}T{hh:02d}:00:00Z", "fundingRate": 1.3,
                              "relativeFundingRate": 0.0000125 if d.day % 5 else -0.00002})
        return Reponse({"result": "success", "serverTime": "x", "rates": rates})
    if "tickers/PF_XBTUSD" in url:
        return Reponse({"result": "success", "ticker": {
            "symbol": "PF_XBTUSD", "markPrice": 71410.18, "openInterest": 2568.4497, "vol24h": 6303.05,
            "fundingRate": 1.0975, "relativeFundingRate": 0.000015378041666667,
            "relativeFundingRatePrediction": 0.000012484875}})
    if "public/ticker" in url:
        return Reponse({"result": {"open_interest": 1.2e9, "funding_8h": 0.00004}})
    if "get_volatility_index_data" in url:
        fin = params["end_timestamp"]
        lignes = [[ts(d) * 1000, 40.0, 41.0, 39.0, 40.5] for d in DATES[-900:] if ts(d) * 1000 >= params["start_timestamp"]]
        lignes = [x for x in lignes if x[0] <= fin]
        page, reste = lignes[-500:], lignes[:-500]   # deux pages, pour tester la suite
        return Reponse({"jsonrpc": "2.0", "result": {"data": page, "continuation": reste[-1][0] if reste else None}})
    if "alternative.me" in url:
        data = [{"value": str(PEUR[i]), "value_classification": "x", "timestamp": str(ts(d))}
                for i, d in list(enumerate(DATES))[::-1] if d >= dt.date(2018, 2, 1)]
        return Reponse({"name": "Fear and Greed Index", "data": data, "metadata": {"error": None}})
    if "fredgraph" in url:
        s = params["id"]
        if s == "DFII10":
            raise RuntimeError("HTTP 404 simulé")   # une série en échec ne doit pas bloquer les autres
        lignes = [f"{d.isoformat()},{'' if i % 97 == 0 else 4.5 + 0.001 * (i % 30):}" for i, d in enumerate(DATES)
                  if d.weekday() < 5 and d.isoformat() >= params["cosd"]]
        return Reponse(text=f"observation_date,{s}\n" + "\n".join(lignes))
    if "coinmetrics" in url:
        m = params["metrics"]
        if m in ("FlowInExNtv", "FlowOutExNtv", "SplyExNtv"):
            raise RuntimeError("HTTP 403 simulé")   # métriques absentes de l'offre gratuite
        data = []
        for i, d in enumerate(DATES):
            if d.isoformat() < params["start_time"]:
                continue
            ligne = {"asset": "btc", "time": f"{d.isoformat()}T00:00:00.000000000Z"}
            for k in m.split(","):
                ligne[k] = str(C[i] if k == "PriceUSD" else 1.39)
            data.append(ligne)
        return Reponse({"data": data})
    raise RuntimeError(f"URL non prévue dans le test : {url}")


def test_collecte():
    collecte.get = faux_get
    collecte.time.sleep = lambda *_: None
    code = collecte.main()
    verifier("collecte : code de sortie 0", code == 0)
    etat = json.load(open(outils.chemin("etat.json"), encoding="utf-8"))["sources"]
    verifier("collecte : toutes les sources ok", all(e["ok"] for e in etat.values()),
             str({k: v["note"] for k, v in etat.items() if not v["ok"]}))

    p = outils.lire("btc_jour.csv")
    verifier("prix : nombre de jours", len(p) == len(DATES), f"{len(p)} / {len(DATES)}")
    verifier("prix : bougie du jour écartée", p["date"].max() == DATES[-1].isoformat())
    verifier("prix : colonnes dans le bon ordre", proche(p["haut"].iloc[-1], H[-1], 1e-4)
             and proche(p["bas"].iloc[-1], B[-1], 1e-4) and proche(p["ouverture"].iloc[-1], O[-1], 1e-4))
    verifier("prix : euros présents partout", p["cloture_eur"].notna().all() and p["eurusd"].between(1.0, 1.2).all())
    verifier("prix : conversion", proche(p["cloture_eur"].iloc[-1], p["cloture"].iloc[-1] / p["eurusd"].iloc[-1], 1e-6))

    f = outils.lire("financement_kraken.csv")
    verifier("financement : jour incomplet écarté", f["date"].max() == DATES[-1].isoformat() and (f["releves"] == 24).all())
    attendu = 0.0000125 * 8 * 100
    verifier("financement : 0,01 % par 8 h", proche(f.loc[f["taux_8h_pct"] > 0, "taux_8h_pct"].iloc[0], attendu, 1e-9),
             f"{f['taux_8h_pct'].max():.5f}")
    verifier("financement : cumul du jour", proche(f.loc[f["taux_8h_pct"] > 0, "cumul_jour_pct"].iloc[0], attendu * 3, 1e-9))

    d = outils.lire("dvol.csv")
    verifier("dvol : pagination complète", len(d) == 900, str(len(d)))
    m = outils.lire("macro.csv")
    verifier("macro : série en échec ignorée", "taux_reel_10ans" not in m.columns and "vix" in m.columns)
    verifier("macro : note d'état", "taux_reel_10ans" in etat["macro"]["note"])
    o = outils.lire("onchain.csv")
    verifier("onchain : métriques optionnelles", "mvrv" in o.columns and "hashrate" in o.columns
             and "btc_sur_plateformes" not in o.columns)
    der = outils.lire("derives_instantane.csv")
    verifier("dérivés : financement en cours", proche(der["kraken_financement_8h_pct"].iloc[0], 0.000015378041666667 * 800, 1e-9))

    texte = open(outils.chemin("dernier.md"), encoding="utf-8").read()
    verifier("relevé : euros puis dollars", "€ (" in texte and "$)" in texte)
    verifier("relevé : moyenne 200 semaines calculée", "200 semaines | historique insuffisant" not in texte)

    # Deuxième lancement : rien n'est perdu, rien n'est dupliqué
    avant = {n: len(outils.lire(n)) for n in ("btc_jour.csv", "financement_kraken.csv", "dvol.csv", "macro.csv",
                                             "peur_avidite.csv", "onchain.csv", "eurusd.csv")}
    collecte.main()
    apres = {n: len(outils.lire(n)) for n in avant}
    verifier("2e lancement : mêmes fichiers", avant == apres, str({k: (avant[k], apres[k]) for k in avant if avant[k] != apres[k]}))
    verifier("2e lancement : pas de doublon", not outils.lire("btc_jour.csv")["date"].duplicated().any())

    # Panne d'une source secondaire : le lancement continue et l'ancien fichier reste
    def panne(url, params=None, **k):
        if "alternative.me" in url:
            raise RuntimeError("panne simulée")
        return faux_get(url, params, **k)

    collecte.get = panne
    code = collecte.main()
    etat = json.load(open(outils.chemin("etat.json"), encoding="utf-8"))["sources"]
    verifier("panne secondaire : code 0", code == 0)
    verifier("panne secondaire : signalée", not etat["peur_avidite"]["ok"] and len(outils.lire("peur_avidite.csv")) == apres["peur_avidite.csv"])

    # Coinbase en panne : secours Kraken
    def sans_coinbase(url, params=None, **k):
        if "coinbase" in url:
            raise RuntimeError("panne simulée")
        if "api.kraken.com" in url:
            lignes = [[ts(d), str(O[i]), str(H[i]), str(B[i]), str(C[i]), "0", "12.5", 10] for i, d in enumerate(DATES)][-720:]
            return Reponse({"error": [], "result": {"XXBTZUSD": lignes, "last": 1}})
        return faux_get(url, params, **k)

    collecte.get = sans_coinbase
    code = collecte.main()
    etat = json.load(open(outils.chemin("etat.json"), encoding="utf-8"))["sources"]
    verifier("secours Kraken", code == 0 and "secours Kraken" in etat["prix"]["note"]
             and len(outils.lire("btc_jour.csv")) == len(DATES))
    collecte.get = faux_get


# -------------------------------------------------------- 3. bout en bout
def test_backtest():
    code = backtest.main()
    chemin = os.path.join(outils.RAPPORT, "backtest.md")
    texte = open(chemin, encoding="utf-8").read()
    trades = pd.read_csv(os.path.join(outils.RAPPORT, "trades.csv"))
    verifier("backtest : code 0 et rapport écrit", code == 0 and len(texte) > 2000)
    verifier("backtest : toutes les règles ont des trades", set(trades["regle"]) >= {"L0", "L1", "L2", "L4", "S0", "S1", "S3"},
             str(sorted(set(trades["regle"]))))
    verifier("backtest : pas de valeur aberrante", trades["R"].between(-6, 3).all(), f"{trades['R'].min():.2f} à {trades['R'].max():.2f}")
    verifier("backtest : entrée après le signal", (trades["entree"] > trades["signal"]).all())
    verifier("backtest : pas de 'nan' dans le rapport", re.search(r"\bnan\b", texte.lower()) is None)
    df = backtest.charger()
    # Aucun regard vers l'avenir : tronquer l'historique ne change pas les trades déjà clos
    t_complet = backtest.simuler(df, (df["peur"] <= 20).fillna(False).to_numpy(bool), 1)
    coupe = df.iloc[:-300].reset_index(drop=True)
    t_coupe = backtest.simuler(coupe, (coupe["peur"] <= 20).fillna(False).to_numpy(bool), 1)
    communs = [t for t in t_complet if t["sortie"] < coupe["date"].iloc[-10]]
    identiques = all(proche(a["R"], b["R"]) and a["entree"] == b["entree"] for a, b in zip(communs, t_coupe))
    verifier("backtest : aucun regard vers l'avenir", len(communs) > 5 and identiques, f"{len(communs)} trades comparés")
    return texte


if __name__ == "__main__":
    test_simulation()
    test_collecte()
    rapport = test_backtest()
    print()
    if ECHECS:
        print(f"{len(ECHECS)} ECHEC(S) : {ECHECS}")
        sys.exit(1)
    print("TOUS LES TESTS PASSENT")
    if "--rapport" in sys.argv:
        print("\n" + rapport)
        print(open(outils.chemin("dernier.md"), encoding="utf-8").read())
