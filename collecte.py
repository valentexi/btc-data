#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collecte quotidienne des données Bitcoin.

Sources publiques et gratuites, sans clé d'API. Aucun ordre n'est passé, aucune
donnée personnelle n'est utilisée.

Premier lancement : tout l'historique disponible est téléchargé.
Lancements suivants : seuls les derniers jours sont mis à jour.

Fichiers produits dans data/ :
  btc_jour.csv            prix quotidien (Coinbase, secours Kraken), en dollars et en euros
  eurusd.csv              taux de référence de la BCE (dollars pour un euro)
  financement_kraken.csv  taux de financement du contrat perpétuel Kraken, par jour
  derives_instantane.csv  relevé du jour : intérêt ouvert, financement en cours
  dvol.csv                volatilité implicite du Bitcoin (indice DVOL de Deribit)
  peur_avidite.csv        indice Fear & Greed
  macro.csv               taux américains (Trésor), VIX (CBOE), Nasdaq-100, S&P 500, DXY, Brent (Yahoo)
  onchain.csv             données de la blockchain (Coin Metrics, offre gratuite)
  h4/btc_h4_AAAA-MM.csv   bougies de 4 heures (Coinbase, heures agrégées), un fichier par mois
  h1_recent.csv           bougies d'une heure des 75 derniers jours (suivi papier)
  financement_deribit.csv financement historique réel du contrat perpétuel Deribit, depuis 2019
  kraken_contrat.csv      paramètres réels du contrat Kraken (marges, levier maximum, frais)
  actifs.csv, betas.csv   cours d'un panier d'actifs liés au Bitcoin et leurs bêtas
  etat.json               état et fraîcheur de chaque source lors du dernier lancement
  dernier.md              relevé lisible, prix en euros, avec la fraîcheur de chaque source
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys
import time
import zipfile

import numpy as np
import pandas as pd
import requests

from outils import DATA, chemin, ecrire_h4, fusionner, lire, lire_h4, nb, pct, pct_brut, prix, usd

DEBUT = "2017-01-01"
UA = {"User-Agent": "Mozilla/5.0 (compatible; btc-data/1.0; collecte quotidienne)"}
ETAT: dict[str, dict] = {}


# ---------------------------------------------------------------- utilitaires
def maintenant() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def aujourd_hui() -> str:
    return maintenant().strftime("%Y-%m-%d")


def get(url: str, params: dict | None = None, essais: int = 2, timeout: int = 30,
        entetes: dict | None = None) -> requests.Response:
    """Requête GET avec quelques essais. Lève une erreur claire en cas d'échec."""
    erreur: Exception | None = None
    for k in range(essais):
        try:
            r = requests.get(url, params=params, headers=entetes or UA, timeout=(10, timeout))
            if r.status_code == 200:
                return r
            erreur = RuntimeError(f"HTTP {r.status_code} sur {url.split('?')[0]}")
            if r.status_code in (400, 401, 403, 404):
                break
        except requests.RequestException as e:  # réseau, délai dépassé
            erreur = RuntimeError(f"{type(e).__name__} sur {url.split('?')[0]}")
        time.sleep(2.0 * (k + 1))
    raise erreur  # type: ignore[misc]


def depuis(nom: str, marge: int = 10) -> str:
    """Date à partir de laquelle recharger : dernière date connue moins une marge."""
    df = lire(nom)
    if df is None:
        return DEBUT
    d = dt.date.fromisoformat(str(df["date"].max())) - dt.timedelta(days=marge)
    return max(d.isoformat(), DEBUT)


def executer(nom: str, fonction) -> pd.DataFrame | None:
    """Lance une source sans jamais interrompre les autres."""
    try:
        df, note = fonction()
        ETAT[nom] = {"ok": True, "lignes": int(len(df)), "derniere_date": str(df["date"].max()), "note": note}
        print(f"[ok]     {nom:22s} {len(df):6d} lignes, jusqu'au {df['date'].max()} {note}")
        return df
    except Exception as e:  # noqa: BLE001 - on veut tout attraper, source par source
        ancien = lire_h4() if nom == "h4" else lire(FICHIERS.get(nom, ""))
        ETAT[nom] = {
            "ok": False,
            "lignes": int(len(ancien)) if ancien is not None else 0,
            "derniere_date": str(ancien["date"].max()) if ancien is not None else None,
            "note": f"échec : {e}",
        }
        print(f"[ECHEC]  {nom:22s} {e}")
        return ancien


# -------------------------------------------------------------------- sources
def _prix_coinbase() -> pd.DataFrame:
    d0 = dt.date.fromisoformat(depuis("btc_jour.csv"))
    fin = maintenant().date()
    lignes = []
    while d0 <= fin:
        d1 = min(d0 + dt.timedelta(days=290), fin)
        r = get(
            "https://api.exchange.coinbase.com/products/BTC-USD/candles",
            {"granularity": 86400, "start": f"{d0}T00:00:00Z", "end": f"{d1}T00:00:00Z"},
        )
        # format : [temps, bas, haut, ouverture, clôture, volume], du plus récent au plus ancien
        for t, bas, haut, ouv, clo, vol in r.json():
            lignes.append(
                {
                    "date": dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d"),
                    "ouverture": float(ouv),
                    "haut": float(haut),
                    "bas": float(bas),
                    "cloture": float(clo),
                    "volume_btc": float(vol),
                }
            )
        d0 = d1 + dt.timedelta(days=1)
        time.sleep(0.35)
    if not lignes:
        raise RuntimeError("Coinbase n'a renvoyé aucune bougie")
    return pd.DataFrame(lignes)


def _prix_kraken() -> pd.DataFrame:
    j = get("https://api.kraken.com/0/public/OHLC", {"pair": "XBTUSD", "interval": 1440}).json()
    if j.get("error"):
        raise RuntimeError(f"Kraken : {j['error']}")
    cle = [k for k in j["result"] if k != "last"][0]
    # format : [temps, ouverture, haut, bas, clôture, prix moyen, volume, nombre]
    lignes = [
        {
            "date": dt.datetime.fromtimestamp(int(x[0]), dt.timezone.utc).strftime("%Y-%m-%d"),
            "ouverture": float(x[1]),
            "haut": float(x[2]),
            "bas": float(x[3]),
            "cloture": float(x[4]),
            "volume_btc": float(x[6]),
        }
        for x in j["result"][cle]
    ]
    return pd.DataFrame(lignes)


def src_prix():
    note = "(Coinbase)"
    try:
        df = _prix_coinbase()
    except Exception as e:  # noqa: BLE001
        df = _prix_kraken()
        note = f"(secours Kraken, Coinbase en échec : {e})"
    df = df[df["date"] < aujourd_hui()]  # la bougie du jour n'est pas terminée
    return fusionner("btc_jour.csv", df), note


def fred(serie: str, debut: str = DEBUT) -> pd.DataFrame:
    """Une série FRED au format CSV (une seule série par appel)."""
    r = get("https://fred.stlouisfed.org/graph/fredgraph.csv", {"id": serie, "cosd": debut})
    df = pd.read_csv(io.StringIO(r.text), na_values=[".", ""])
    if df.shape[1] != 2:
        raise RuntimeError(f"FRED {serie} : format inattendu")
    df.columns = ["date", serie]
    df[serie] = pd.to_numeric(df[serie], errors="coerce")
    return df.dropna()


def src_eurusd():
    note = "(BCE)"
    try:
        r = get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        df = pd.read_csv(z.open(z.namelist()[0]), na_values=["N/A"], skipinitialspace=True)
        df = df[["Date", "USD"]].rename(columns={"Date": "date", "USD": "eurusd"})
        df["eurusd"] = pd.to_numeric(df["eurusd"], errors="coerce")
        df = df.dropna()
    except Exception as e:  # noqa: BLE001
        df = fred("DEXUSEU").rename(columns={"DEXUSEU": "eurusd"})
        note = f"(secours FRED, BCE en échec : {e})"
    df = df[df["date"].astype(str) >= DEBUT]
    return fusionner("eurusd.csv", df), note


def src_financement():
    r = get(
        "https://futures.kraken.com/derivatives/api/v4/historicalfundingrates",
        {"symbol": "PF_XBTUSD"},
        timeout=120,
        essais=3,
    )
    df = pd.DataFrame(r.json()["rates"])
    if df.empty:
        raise RuntimeError("aucun taux renvoyé")
    df["date"] = df["timestamp"].str[:10]
    # relativeFundingRate : part de la position payée par heure (les longs paient si positif)
    g = df.groupby("date")["relativeFundingRate"]
    out = pd.DataFrame(
        {
            "taux_8h_pct": g.mean() * 8 * 100,
            "cumul_jour_pct": g.sum() * 100,
            "min_8h_pct": g.min() * 8 * 100,
            "max_8h_pct": g.max() * 8 * 100,
            "releves": g.count(),
        }
    ).reset_index()
    out = out[(out["date"] < aujourd_hui()) & (out["releves"] >= 20)]  # jours complets seulement
    return fusionner("financement_kraken.csv", out), "(Kraken Futures)"


def src_derives():
    t = get("https://futures.kraken.com/derivatives/api/v3/tickers/PF_XBTUSD").json()["ticker"]
    ligne = {
        "date": aujourd_hui(),
        "heure_utc": maintenant().strftime("%H:%M"),
        "kraken_prix_marque": float(t["markPrice"]),
        "kraken_interet_ouvert_btc": float(t["openInterest"]),
        "kraken_financement_8h_pct": float(t["relativeFundingRate"]) * 8 * 100,
        "kraken_prevision_8h_pct": float(t.get("relativeFundingRatePrediction", float("nan"))) * 8 * 100,
        "kraken_volume_24h_btc": float(t["vol24h"]),
    }
    note = "(Kraken Futures)"
    try:
        d = get(
            "https://www.deribit.com/api/v2/public/ticker", {"instrument_name": "BTC-PERPETUAL"}
        ).json()["result"]
        ligne["deribit_interet_ouvert_usd"] = float(d["open_interest"])
        ligne["deribit_financement_8h_pct"] = float(d["funding_8h"]) * 100
        note = "(Kraken Futures, Deribit)"
    except Exception:  # noqa: BLE001
        pass
    return fusionner("derives_instantane.csv", pd.DataFrame([ligne])), note


def src_dvol():
    t0 = int(dt.datetime.fromisoformat(depuis("dvol.csv") + "T00:00:00+00:00").timestamp() * 1000)
    fin: int | None = int(maintenant().timestamp() * 1000)
    lignes, tours = [], 0
    while fin and tours < 30:
        res = get(
            "https://www.deribit.com/api/v2/public/get_volatility_index_data",
            {"currency": "BTC", "start_timestamp": t0, "end_timestamp": fin, "resolution": "1D"},
        ).json()["result"]
        lignes += res.get("data", [])
        fin = res.get("continuation")
        tours += 1
        time.sleep(0.3)
    if not lignes:
        raise RuntimeError("aucune donnée DVOL")
    # format : [temps en ms, ouverture, haut, bas, clôture]
    df = pd.DataFrame(lignes, columns=["t", "ouverture", "haut", "bas", "cloture"])
    df["date"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.strftime("%Y-%m-%d")
    df = df.drop(columns="t")[["date", "ouverture", "haut", "bas", "cloture"]]
    df = df[df["date"] < aujourd_hui()]
    return fusionner("dvol.csv", df), "(Deribit)"


def src_peur():
    j = get("https://api.alternative.me/fng/", {"limit": 0, "format": "json"}).json()
    lignes = [
        {
            "date": dt.datetime.fromtimestamp(int(x["timestamp"]), dt.timezone.utc).strftime("%Y-%m-%d"),
            "valeur": int(x["value"]),
            "classe": x.get("value_classification", ""),
        }
        for x in j["data"]
    ]
    if not lignes:
        raise RuntimeError("aucune donnée")
    return fusionner("peur_avidite.csv", pd.DataFrame(lignes)), "(alternative.me)"


NAVIGATEUR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0 Safari/537.36",
    "Accept": "application/json,text/csv,*/*",
}


def tresor(genre: str, annee: int) -> pd.DataFrame:
    """Taux du Trésor américain pour une année. genre : 'nominal' ou 'reel'."""
    type_ = "daily_treasury_yield_curve" if genre == "nominal" else "daily_treasury_real_yield_curve"
    url = (
        "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
        f"daily-treasury-rates.csv/{annee}/all?type={type_}&field_tdr_date_value={annee}&page&_format=csv"
    )
    df = pd.read_csv(io.StringIO(get(url, entetes=NAVIGATEUR).text))
    df.columns = [c.strip().lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
    if genre == "nominal":
        out = df[["date", "2 yr", "10 yr"]].rename(columns={"2 yr": "taux_2ans", "10 yr": "taux_10ans"})
    else:
        out = df[["date", "10 yr"]].rename(columns={"10 yr": "taux_reel_10ans"})
    for c in out.columns[1:]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna()


def vix_cboe() -> pd.DataFrame:
    r = get("https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv", entetes=NAVIGATEUR)
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip().lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
    df["vix"] = pd.to_numeric(df["close"], errors="coerce")
    return df[["date", "vix"]].dropna()


def yahoo(symbole: str, nom: str, debut: str) -> pd.DataFrame:
    """Clôtures quotidiennes d'un indice ou d'un contrat (Yahoo Finance, sans clé)."""
    t0 = int(dt.datetime.fromisoformat(debut + "T00:00:00+00:00").timestamp())
    r = get(
        "https://query1.finance.yahoo.com/v8/finance/chart/" + requests.utils.quote(symbole, safe=""),
        {"period1": t0, "period2": int(maintenant().timestamp()), "interval": "1d"},
        entetes=NAVIGATEUR,
    )
    res = r.json()["chart"]["result"][0]
    df = pd.DataFrame({"t": res["timestamp"], nom: res["indicators"]["quote"][0]["close"]})
    df["date"] = pd.to_datetime(df["t"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    df[nom] = pd.to_numeric(df[nom], errors="coerce")
    return df[["date", nom]].dropna().drop_duplicates(subset="date", keep="last")


YAHOO = {"^NDX": "nasdaq100", "^GSPC": "sp500", "DX-Y.NYB": "dxy", "BZ=F": "brent"}


def src_macro():
    debut = depuis("macro.csv", 30)
    annees = range(int(debut[:4]), maintenant().year + 1)
    morceaux: list[pd.DataFrame] = []
    echecs: list[str] = []

    def essayer(nom: str, fonction) -> bool:
        try:
            morceaux.append(fonction())
            return True
        except Exception:  # noqa: BLE001
            return False

    def annees_tresor(genre: str) -> pd.DataFrame:
        return pd.concat([tresor(genre, a) for a in annees], ignore_index=True)

    if not essayer("taux", lambda: annees_tresor("nominal")):
        if not essayer("taux", lambda: yahoo("^TNX", "taux_10ans", debut)):   # secours : 10 ans seulement
            echecs.append("taux_10ans")
        echecs.append("taux_2ans")
    if not essayer("taux réel", lambda: annees_tresor("reel")):
        echecs.append("taux_reel_10ans")
    if not essayer("vix", vix_cboe) and not essayer("vix", lambda: yahoo("^VIX", "vix", debut)):
        echecs.append("vix")
    for symbole, nom in YAHOO.items():
        if not essayer(nom, lambda s=symbole, n=nom: yahoo(s, n, debut)):
            echecs.append(nom)
        time.sleep(0.4)

    if not morceaux:
        raise RuntimeError("aucune série macro disponible")
    tout = morceaux[0]
    for m in morceaux[1:]:
        tout = tout.merge(m, on="date", how="outer")
    tout = tout[(tout["date"] >= debut) & (tout["date"] < aujourd_hui())]
    source = "(Trésor américain, CBOE, Yahoo Finance)"
    note = source if not echecs else source[:-1] + f" ; séries manquantes : {', '.join(echecs)})"
    return fusionner("macro.csv", tout), note


def coinmetrics(metriques: str, debut: str) -> pd.DataFrame:
    url: str | None = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    params: dict | None = {
        "assets": "btc",
        "metrics": metriques,
        "frequency": "1d",
        "start_time": debut,
        "page_size": 10000,
    }
    lignes = []
    while url:
        j = get(url, params).json()
        lignes += j.get("data", [])
        url, params = j.get("next_page_url"), None
        time.sleep(0.7)
    if not lignes:
        raise RuntimeError(f"Coin Metrics : rien pour {metriques}")
    df = pd.DataFrame(lignes)
    df["date"] = df["time"].str[:10]
    df = df.drop(columns=[c for c in df.columns if c in ("asset", "time") or "-status" in c])
    for c in df.columns:
        if c != "date":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


ONCHAIN_BASE = {"PriceUSD": "prix_usd", "CapMVRVCur": "mvrv"}
ONCHAIN_OPTION = {
    "CapRealUSD": "cap_realisee_usd",
    "AdrActCnt": "adresses_actives",
    "HashRate": "hashrate",
    "FlowInExNtv": "entrees_plateformes_btc",
    "FlowOutExNtv": "sorties_plateformes_btc",
    "SplyExNtv": "btc_sur_plateformes",
}


def src_onchain():
    debut = depuis("onchain.csv", 10)
    tout = coinmetrics(",".join(ONCHAIN_BASE), debut).rename(columns=ONCHAIN_BASE)
    absentes = []
    for m, nom in ONCHAIN_OPTION.items():  # une par une : l'offre gratuite ne les sert pas toutes
        try:
            tout = tout.merge(coinmetrics(m, debut).rename(columns={m: nom}), on="date", how="outer")
        except Exception:  # noqa: BLE001
            absentes.append(nom)
    tout = tout[tout["date"] < aujourd_hui()]
    note = "(Coin Metrics)" if not absentes else f"(Coin Metrics, non disponibles : {', '.join(absentes)})"
    return fusionner("onchain.csv", tout), note


# ------------------------------------------------------- sources ajoutées (V2)
DEBUT_H4 = "2017-01-01"


def _heures_coinbase(d0: dt.datetime, fin: dt.datetime) -> tuple[list, str]:
    """Bougies d'une heure entre d0 et fin. Renvoie ce qui a pu être lu, même en cas de panne."""
    lignes, note = [], ""
    while d0 < fin:
        d1 = min(d0 + dt.timedelta(hours=290), fin)
        try:
            r = get(
                "https://api.exchange.coinbase.com/products/BTC-USD/candles",
                {"granularity": 3600, "start": d0.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "end": d1.strftime("%Y-%m-%dT%H:%M:%SZ")},
            )
        except Exception as e:  # noqa: BLE001
            note = f" ; interrompu au {d0:%Y-%m-%d} : {e}"
            break
        lignes += r.json()   # [temps, bas, haut, ouverture, clôture, volume]
        d0 = d1
        time.sleep(0.12)
    return lignes, note


def agreger_h4(lignes: list, maintenant_: dt.datetime) -> pd.DataFrame:
    """Heures -> bougies de 4 heures calées sur 0 h, 4 h, 8 h... UTC. Seules les bougies terminées sont gardées."""
    h = pd.DataFrame(lignes, columns=["t", "bas", "haut", "ouverture", "cloture", "volume_btc"]).astype(float)
    h = h.drop_duplicates(subset="t").sort_values("t")
    h["bloc"] = (h["t"] // 14400).astype(int) * 14400
    g = h.groupby("bloc")
    out = pd.DataFrame({
        "ouverture": g["ouverture"].first(), "haut": g["haut"].max(), "bas": g["bas"].min(),
        "cloture": g["cloture"].last(), "volume_btc": g["volume_btc"].sum(), "heures": g["t"].count(),
    }).reset_index()
    out = out[out["bloc"] + 14400 <= maintenant_.timestamp()]
    out["date"] = pd.to_datetime(out["bloc"], unit="s", utc=True).dt.strftime("%Y-%m-%d %H:%M")
    return out[["date", "ouverture", "haut", "bas", "cloture", "volume_btc", "heures"]]


def enregistrer_heures(lignes: list, maintenant_: dt.datetime, jours: int = 75) -> None:
    """Garde les bougies d'une heure terminées des 75 derniers jours : le suivi papier s'en sert
    pour juger les déclencheurs à l'heure près."""
    h = pd.DataFrame(lignes, columns=["t", "bas", "haut", "ouverture", "cloture", "volume_btc"]).astype(float)
    h = h.drop_duplicates(subset="t")
    h = h[h["t"] + 3600 <= maintenant_.timestamp()]
    if h.empty:
        return
    h["date"] = pd.to_datetime(h["t"], unit="s", utc=True).dt.strftime("%Y-%m-%d %H:%M")
    tout = fusionner("h1_recent.csv", h[["date", "ouverture", "haut", "bas", "cloture"]])
    limite = (maintenant_ - dt.timedelta(days=jours)).strftime("%Y-%m-%d %H:%M")
    tout[tout["date"] >= limite].to_csv(chemin("h1_recent.csv"), index=False, float_format="%.10g")


def src_h4():
    ancien = lire_h4()
    if ancien is None:
        d0 = dt.datetime.fromisoformat(DEBUT_H4 + "T00:00:00+00:00")
    else:
        d0 = dt.datetime.fromisoformat(str(ancien["date"].max()).replace(" ", "T") + ":00+00:00") - dt.timedelta(days=2)
    if lire("h1_recent.csv") is None:   # première fois : il faut 60 jours d'heures pour le suivi papier
        d0 = min(d0, maintenant() - dt.timedelta(days=60))
    lignes, note = _heures_coinbase(d0, maintenant())
    source = "(Coinbase, heures agrégées"
    if lignes:
        df = agreger_h4(lignes, maintenant())
        enregistrer_heures(lignes, maintenant())
    else:  # secours : Kraken ne donne que les 720 dernières bougies de 4 heures
        j = get("https://api.kraken.com/0/public/OHLC", {"pair": "XBTUSD", "interval": 240}).json()
        cle = [k for k in j["result"] if k != "last"][0]
        df = pd.DataFrame([{
            "date": dt.datetime.fromtimestamp(int(x[0]), dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "ouverture": float(x[1]), "haut": float(x[2]), "bas": float(x[3]), "cloture": float(x[4]),
            "volume_btc": float(x[6]), "heures": 4,
        } for x in j["result"][cle] if int(x[0]) + 14400 <= maintenant().timestamp()])
        source = "(secours Kraken"
    if df.empty:
        raise RuntimeError("aucune bougie de 4 heures" + note)
    ecrire_h4(df)
    tout = lire_h4()
    return tout, f"{source}{note})"


def src_financement_deribit():
    """Financement réellement payé sur le contrat perpétuel Deribit, heure par heure, depuis 2019."""
    ancien = lire("financement_deribit.csv")
    debut = "2019-05-01" if ancien is None else depuis("financement_deribit.csv", 3)
    d0 = dt.datetime.fromisoformat(debut + "T00:00:00+00:00")
    fin = maintenant()
    lignes, note = [], ""
    while d0 < fin:
        d1 = min(d0 + dt.timedelta(days=30), fin)   # 744 relevés au plus par appel
        try:
            res = get(
                "https://www.deribit.com/api/v2/public/get_funding_rate_history",
                {"instrument_name": "BTC-PERPETUAL", "start_timestamp": int(d0.timestamp() * 1000),
                 "end_timestamp": int(d1.timestamp() * 1000)},
            ).json()["result"]
        except Exception as e:  # noqa: BLE001
            note = f" ; interrompu au {d0:%Y-%m-%d} : {e}"
            break
        lignes += [(x["timestamp"], x["interest_1h"]) for x in res]
        d0 = d1
        time.sleep(0.15)
    if not lignes:
        raise RuntimeError("aucun relevé" + note)
    df = pd.DataFrame(lignes, columns=["t", "taux_1h"]).drop_duplicates(subset="t")
    df["date"] = pd.to_datetime(df["t"], unit="ms", utc=True).dt.strftime("%Y-%m-%d")
    g = df.groupby("date")["taux_1h"]
    out = pd.DataFrame({
        "taux_8h_pct": g.mean() * 8 * 100, "cumul_jour_pct": g.sum() * 100, "releves": g.count(),
    }).reset_index()
    out = out[(out["date"] < aujourd_hui()) & (out["releves"] >= 20)]
    if out.empty:
        raise RuntimeError("aucun jour complet" + note)
    return fusionner("financement_deribit.csv", out), f"(Deribit{note})"


def src_options():
    """Options Bitcoin sur Deribit : rapport puts/calls et prochaine grosse échéance (relevé instantané)."""
    res = get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency",
              {"currency": "BTC", "kind": "option"}, timeout=60).json()["result"]
    lignes = []
    for x in res:
        morceaux = str(x.get("instrument_name", "")).split("-")
        if len(morceaux) != 4:
            continue
        try:
            ech = dt.datetime.strptime(morceaux[1], "%d%b%y").date()
            lignes.append({"ech": ech, "prix_ex": float(morceaux[2]), "type": morceaux[3],
                           "oi": float(x.get("open_interest") or 0), "vol": float(x.get("volume") or 0)})
        except ValueError:
            continue
    o = pd.DataFrame(lignes)
    if o.empty or o["oi"].sum() <= 0:
        raise RuntimeError("aucune option exploitable")
    calls, puts = o[o["type"] == "C"], o[o["type"] == "P"]
    ligne = {
        "date": aujourd_hui(),
        "options_oi_calls_btc": calls["oi"].sum(), "options_oi_puts_btc": puts["oi"].sum(),
        "options_puts_calls_oi": puts["oi"].sum() / calls["oi"].sum() if calls["oi"].sum() else float("nan"),
        "options_puts_calls_volume": puts["vol"].sum() / calls["vol"].sum() if calls["vol"].sum() else float("nan"),
    }
    # échéance la plus chargée dans les 45 jours, et son « max pain »
    # (prix d'exercice où les acheteurs d'options perdent le plus à l'échéance)
    limite = maintenant().date() + dt.timedelta(days=45)
    proches = o[(o["ech"] >= maintenant().date()) & (o["ech"] <= limite)]
    if len(proches):
        par_ech = proches.groupby("ech")["oi"].sum()
        ech = par_ech.idxmax()
        e = proches[proches["ech"] == ech]
        k, typ, oi = e["prix_ex"].to_numpy(), e["type"].to_numpy(), e["oi"].to_numpy()
        niveaux = np.unique(k)
        valeur = [float((oi * np.where(typ == "C", np.maximum(s_ - k, 0), np.maximum(k - s_, 0))).sum())
                  for s_ in niveaux]
        ligne.update({"options_echeance": ech.isoformat(), "options_echeance_oi_btc": float(par_ech.max()),
                      "options_echeance_max_pain_usd": float(niveaux[int(np.argmin(valeur))])})
    return fusionner("derives_instantane.csv", pd.DataFrame([ligne])), "(Deribit)"


def _premier_palier(paliers) -> tuple[float, float]:
    """Marge initiale et de maintenance du premier palier d'un barème Kraken."""
    if isinstance(paliers, dict):
        paliers = list(paliers.values())
    p = paliers[0]
    return float(p["initialMargin"]), float(p["maintenanceMargin"])


def src_contrat_kraken():
    """Paramètres réels du contrat perpétuel PF_XBTUSD, pour ne plus les supposer."""
    inst = get("https://futures.kraken.com/derivatives/api/v3/instruments", timeout=60).json()["instruments"]
    c = next(x for x in inst if x.get("symbol") == "PF_XBTUSD")
    note = "(Kraken Futures, barème Europe, particuliers)"
    try:
        europe = c["marginSchedules"]["europa"]
        paliers = europe.get("retail") if isinstance(europe, dict) else europe
        mi, mm = _premier_palier(paliers)
    except Exception:  # noqa: BLE001
        mi, mm = _premier_palier(c.get("retailMarginLevels") or c["marginLevels"])
        note = "(Kraken Futures, barème général : barème Europe illisible)"
    ligne = {
        "date": aujourd_hui(), "marge_initiale": mi, "marge_maintenance": mm, "levier_max": round(1 / mi, 2),
        "taille_max_btc": float(c.get("maxPositionSize", float("nan"))),
        "financement_max_par_heure": float(c.get("maxRelativeFundingRate", float("nan"))),
    }
    try:
        baremes = get("https://futures.kraken.com/derivatives/api/v3/feeschedules").json()["feeSchedules"]
        b = next(x for x in baremes if x.get("uid") == c.get("feeScheduleUid"))
        t = sorted(b["tiers"], key=lambda z: float(z.get("usdVolume", 0)))[0]
        en_pct = lambda v: float(v) if float(v) >= 0.005 else float(v) * 100   # noqa: E731
        ligne["frais_preneur_pct"], ligne["frais_teneur_pct"] = en_pct(t["takerFee"]), en_pct(t["makerFee"])
    except Exception:  # noqa: BLE001
        note = note[:-1] + " ; frais non lus)"
    return fusionner("kraken_contrat.csv", pd.DataFrame([ligne])), note


# Panier d'actifs dont le cours est lié au Bitcoin ou à la tech américaine (statistiques de marché publiques).
PANIER = {
    "MSTR": "Strategy (MSTR)", "IREN": "IREN", "CLSK": "CleanSpark (CLSK)", "SOL-USD": "Solana (SOL)",
    "MSFT": "Microsoft", "META": "Meta", "AMZN": "Amazon", "MNDY": "Monday.com",
}


def calculer_betas() -> pd.DataFrame | None:
    """Bêta de chaque actif par rapport au Bitcoin : de combien il bouge quand le BTC bouge de 1 %."""
    p, a, mac = lire("btc_jour.csv"), lire("actifs.csv"), lire("macro.csv")
    if p is None:
        return None
    base = p[["date", "cloture"]].rename(columns={"cloture": "btc"})
    series: dict[str, pd.DataFrame] = {}
    if a is not None:
        for sym, nom in PANIER.items():
            if sym in a.columns:
                series[nom] = a[["date", sym]].rename(columns={sym: "x"})
    if mac is not None:
        for col, nom in (("nasdaq100", "Nasdaq-100"), ("sp500", "S&P 500")):
            if col in mac.columns:
                series[nom] = mac[["date", col]].rename(columns={col: "x"})
    lignes = []
    for nom, s_ in series.items():
        m = base.merge(s_.dropna(), on="date").sort_values("date")
        r = m[["btc", "x"]].pct_change().dropna()
        r["date"] = m["date"].iloc[1:].to_numpy()
        if len(r) < 40:
            continue
        fin_ = dt.date.fromisoformat(r["date"].iloc[-1])

        def fenetre(jours):
            return r[r["date"] >= (fin_ - dt.timedelta(days=jours)).isoformat()]

        def beta(z):
            return float(np.cov(z["x"], z["btc"])[0, 1] / z["btc"].var()) if len(z) >= 25 and z["btc"].var() > 0 else float("nan")

        r90, r365 = fenetre(90), fenetre(365)
        baisse = r365[r365["btc"] < 0]
        corr90 = float(r90["x"].corr(r90["btc"])) if len(r90) >= 25 else float("nan")
        lignes.append({
            "actif": nom, "beta_90j": beta(r90), "correlation_90j": corr90,
            "part_expliquee_90j": corr90 ** 2 if corr90 == corr90 else float("nan"),
            "beta_1an": beta(r365), "beta_1an_jours_de_baisse": beta(baisse),
            "observations_90j": len(r90), "derniere_date": r["date"].iloc[-1],
        })
    if not lignes:
        return None
    out = pd.DataFrame(lignes)
    os.makedirs(DATA, exist_ok=True)
    out.to_csv(chemin("betas.csv"), index=False, float_format="%.4g")
    return out


def src_actifs():
    debut = "2024-06-01" if lire("actifs.csv") is None else depuis("actifs.csv", 10)
    tout, echecs = None, []
    for sym in PANIER:
        try:
            df = yahoo(sym, sym, debut)
            tout = df if tout is None else tout.merge(df, on="date", how="outer")
        except Exception:  # noqa: BLE001
            echecs.append(sym)
        time.sleep(0.4)
    if tout is None:
        raise RuntimeError("aucun cours disponible")
    tout = tout[tout["date"] < aujourd_hui()]
    note = "(Yahoo Finance)" if not echecs else f"(Yahoo Finance ; manquants : {', '.join(echecs)})"
    return fusionner("actifs.csv", tout), note


FICHIERS = {
    "prix": "btc_jour.csv",
    "eurusd": "eurusd.csv",
    "financement": "financement_kraken.csv",
    "derives": "derives_instantane.csv",
    "dvol": "dvol.csv",
    "peur_avidite": "peur_avidite.csv",
    "macro": "macro.csv",
    "onchain": "onchain.csv",
    "h4": "h4",
    "financement_deribit": "financement_deribit.csv",
    "options": "derives_instantane.csv",
    "contrat_kraken": "kraken_contrat.csv",
    "actifs": "actifs.csv",
}
SOURCES = {
    "prix": src_prix,
    "eurusd": src_eurusd,
    "financement": src_financement,
    "derives": src_derives,
    "dvol": src_dvol,
    "peur_avidite": src_peur,
    "macro": src_macro,
    "onchain": src_onchain,
    "h4": src_h4,
    "financement_deribit": src_financement_deribit,
    "options": src_options,
    "contrat_kraken": src_contrat_kraken,
    "actifs": src_actifs,
}

# Nature de chaque donnée et retard toléré, en jours, avant de la déclarer en retard.
#   historique : clôture de la veille ; différée : publiée avec retard (jours ouvrés) ; instantanée : relevée au lancement
NATURE = {
    "prix": ("historique", 1), "eurusd": ("différée", 4), "financement": ("historique", 1),
    "derives": ("instantanée", 0), "dvol": ("historique", 1), "peur_avidite": ("historique", 1),
    "macro": ("différée", 4), "onchain": ("différée", 2), "h4": ("historique", 0),
    "financement_deribit": ("historique", 1), "options": ("instantanée", 0),
    "contrat_kraken": ("instantanée", 0), "actifs": ("différée", 4),
}


def fraicheur() -> int:
    """Complète l'état de chaque source : nature, âge de la dernière donnée, verdict. Renvoie le nombre d'anomalies."""
    auj = maintenant().date()
    anomalies = 0
    for nom, e in ETAT.items():
        nature, tolerance = NATURE.get(nom, ("historique", 1))
        e["nature"] = nature
        d = e.get("derniere_date")
        if not d:
            e["age_jours"], e["fraicheur"] = None, "absente"
        elif nom == "h4":   # jugé en heures : la dernière bougie terminée doit dater de moins de 5 heures
            fin_bougie = dt.datetime.fromisoformat(str(d).replace(" ", "T") + ":00+00:00") + dt.timedelta(hours=4)
            heures = (maintenant() - fin_bougie).total_seconds() / 3600
            e["age_jours"] = round(heures / 24, 2)
            e["fraicheur"] = "à jour" if heures <= 5 else ("en retard" if heures <= 24 else "périmée")
        else:
            age = (auj - dt.date.fromisoformat(str(d)[:10])).days
            e["age_jours"] = age
            e["fraicheur"] = "à jour" if age <= tolerance else ("en retard" if age <= tolerance + 3 else "périmée")
        if not e["ok"] and e["fraicheur"] == "à jour":
            e["fraicheur"] = "à jour (lancement en échec, donnée précédente)"
        if not e["ok"] or not e["fraicheur"].startswith("à jour"):
            anomalies += 1
    return anomalies


# ----------------------------------------------------------------- assemblage
def ajouter_euros() -> pd.DataFrame | None:
    """Ajoute au fichier de prix le taux EUR/USD du jour et la clôture en euros."""
    p, fx = lire("btc_jour.csv"), lire("eurusd.csv")
    if p is None:
        return None
    p = p[["date", "ouverture", "haut", "bas", "cloture", "volume_btc"]]
    if fx is not None:
        # la BCE ne publie pas le week-end : on reporte le dernier taux connu
        p = p.merge(fx, on="date", how="left").sort_values("date")
        avant = fx[fx["date"] < p["date"].min()]
        if pd.isna(p["eurusd"].iloc[0]) and len(avant):
            p.iloc[0, p.columns.get_loc("eurusd")] = avant["eurusd"].iloc[-1]
        p["eurusd"] = p["eurusd"].ffill().bfill()   # week-ends, jours fériés et tout premier jour
        p["cloture_eur"] = p["cloture"] / p["eurusd"]
    os.makedirs(DATA, exist_ok=True)
    p.to_csv(chemin("btc_jour.csv"), index=False, float_format="%.10g")
    return p


def _dernier(df: pd.DataFrame | None, col: str):
    """Dernière valeur connue d'une colonne et sa date, ou (None, None)."""
    if df is None or col not in df.columns:
        return None, None
    s = df[["date", col]].dropna()
    if s.empty:
        return None, None
    return float(s[col].iloc[-1]), str(s["date"].iloc[-1])


def ecrire_dernier(p: pd.DataFrame | None) -> None:
    """Relevé lisible : ce que l'analyse quotidienne lit en premier."""
    L: list[str] = []
    L.append(f"# Dernier relevé BTC ({maintenant().strftime('%d/%m/%Y %H:%M')} UTC)")
    L.append("")
    L.append("Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).")
    L.append("")

    if p is None or len(p) < 2 or "eurusd" not in p.columns:
        L.append("**Prix indisponible lors de ce lancement.** Voir `etat.json`.")
    else:
        c = p["cloture"].to_numpy()
        fx = float(p["eurusd"].iloc[-1])
        d = p["date"].iloc[-1]

        def var(n):
            return pct(c[-1] / c[-1 - n] - 1) if len(c) > n else "n.d."

        L.append(f"## Prix (clôture du {d})")
        L.append(f"- **Bitcoin : {prix(c[-1], fx)}**, EUR/USD {nb(fx, 4)} (BCE)")
        L.append(f"- Variation : {var(1)} sur 1 jour, {var(7)} sur 7 jours, {var(30)} sur 30 jours")
        if len(p) >= 30:
            L.append(
                f"- 30 derniers jours : plus haut {prix(p['haut'].iloc[-30:].max(), fx)}, "
                f"plus bas {prix(p['bas'].iloc[-30:].min(), fx)}"
            )
        if len(c) >= 31:
            r = pd.Series(c).pct_change().iloc[-30:]
            L.append(f"- Volatilité réalisée sur 30 jours : {nb(float(r.std()) * (365 ** 0.5) * 100, 0)} % par an")
        L.append("")
        L.append("## Moyennes mobiles")
        L.append("| Moyenne | Niveau | Écart du prix |")
        L.append("|---|---|---|")
        moyennes = [("50 jours", c[-50:].mean() if len(c) >= 50 else None),
                    ("200 jours", c[-200:].mean() if len(c) >= 200 else None)]
        hebdo = c[::-1][::7][:200]  # une clôture par semaine, 200 semaines
        moyennes.append(("200 semaines", hebdo.mean() if len(hebdo) == 200 else None))
        for nom, m in moyennes:
            if m is None:
                L.append(f"| {nom} | historique insuffisant | |")
            else:
                L.append(f"| {nom} | {prix(m, fx)} | {pct(c[-1] / m - 1)} |")
        L.append("")

    L.append("## Dérivés et sentiment")
    fin = lire("financement_kraken.csv")
    v, d = _dernier(fin, "taux_8h_pct")
    if v is not None:
        m7 = float(fin["taux_8h_pct"].iloc[-7:].mean())
        L.append(
            f"- Financement Kraken : {pct_brut(v, 4)} par 8 h le {d}, {pct_brut(m7, 4)} en moyenne sur 7 jours "
            "(positif : les longs paient)"
        )
    der = lire("derives_instantane.csv")
    v, d = _dernier(der, "kraken_interet_ouvert_btc")
    if v is not None:
        L.append(f"- Intérêt ouvert sur le contrat Kraken : {nb(v, 0)} BTC (relevé du {d})")
    v, d = _dernier(lire("dvol.csv"), "cloture")
    if v is not None:
        L.append(f"- Volatilité implicite (DVOL) : {nb(v, 1)} le {d}")
    v, d = _dernier(der, "options_puts_calls_oi")
    if v is not None:
        vol, _ = _dernier(der, "options_puts_calls_volume")
        L.append(f"- Options Deribit, rapport puts/calls : {nb(v, 2)} en positions ouvertes"
                 + (f", {nb(vol, 2)} en volume sur 24 h" if vol is not None else "") + f" (relevé du {d})")
        mp, _ = _dernier(der, "options_echeance_max_pain_usd")
        if mp is not None and "options_echeance" in der.columns and "eurusd" in (p.columns if p is not None else []):
            ech = der["options_echeance"].dropna().iloc[-1]
            oi, _ = _dernier(der, "options_echeance_oi_btc")
            L.append(f"- Échéance d'options la plus chargée : {ech}, {nb(oi, 0)} BTC en positions ouvertes, "
                     f"« max pain » à {prix(mp, float(p['eurusd'].iloc[-1]))}")
    pa = lire("peur_avidite.csv")
    v, d = _dernier(pa, "valeur")
    if v is not None:
        avant = f", {int(pa['valeur'].iloc[-8])} sept jours plus tôt" if len(pa) >= 8 else ""
        L.append(f"- Fear & Greed : {int(v)} le {d}{avant}")
    v, d = _dernier(lire("onchain.csv"), "mvrv")
    if v is not None:
        L.append(f"- MVRV (prix divisé par le prix de revient moyen du réseau) : {nb(v, 2)} le {d}")
    L.append("")

    L.append("## Macro (dernières clôtures connues)")
    mac = lire("macro.csv")
    libelles = [
        ("taux_10ans", "Taux américain à 10 ans", 2, " %"),
        ("taux_2ans", "Taux américain à 2 ans", 2, " %"),
        ("taux_reel_10ans", "Taux réel à 10 ans", 2, " %"),
        ("vix", "VIX", 1, ""),
        ("nasdaq100", "Nasdaq-100", 0, " points"),
        ("sp500", "S&P 500", 0, " points"),
        ("dxy", "Dollar (DXY)", 2, ""),
        ("brent", "Brent", 1, " $"),
    ]
    for col, nom, dec, unite in libelles:
        v, d = _dernier(mac, col)
        if v is not None:
            L.append(f"- {nom} : {nb(v, dec)}{unite} ({d})")
    if mac is None:
        L.append("- Indisponible lors de ce lancement.")
    L.append("")

    h4 = lire_h4()
    if h4 is not None and len(h4) >= 6 and p is not None and "eurusd" in p.columns:
        fx = float(p["eurusd"].iloc[-1])
        L.append("## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)")
        L.append("| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |")
        L.append("|---|---|---|---|---|")
        for _, x in h4.iloc[-6:].iterrows():
            L.append(f"| {x['date']} | {usd(x['ouverture'])} | {usd(x['haut'])} | {usd(x['bas'])} | "
                     f"{prix(x['cloture'], fx)} |")
        L.append("")

    kc = lire("kraken_contrat.csv")
    if kc is not None:
        k = kc.iloc[-1]
        L.append(f"## Contrat perpétuel Kraken PF_XBTUSD (barème lu le {k['date']})")
        L.append(f"- Marge initiale {nb(k['marge_initiale'] * 100, 1)} %, marge de maintenance "
                 f"{nb(k['marge_maintenance'] * 100, 1)} %, levier maximum x{nb(k['levier_max'], 0)}.")
        if "frais_preneur_pct" in kc.columns and k["frais_preneur_pct"] == k["frais_preneur_pct"]:
            L.append(f"- Frais : {pct_brut(k['frais_preneur_pct'], 3)} par ordre au marché, "
                     f"{pct_brut(k['frais_teneur_pct'], 3)} par ordre limite (premier palier).")
        mm = float(k["marge_maintenance"])
        L.append(f"- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ {nb(1 - mm, 3)} ; "
                 f"short = entrée × (1 + 1/levier) ÷ {nb(1 + mm, 3)}. "
                 "Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.")
        L.append("- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.")
        L.append("")

    be = calculer_betas()
    if be is not None:
        L.append("## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)")
        L.append("| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | "
                 "Bêta 1 an, jours de baisse du BTC |")
        L.append("|---|---|---|---|---|---|")

        def f(x, d=2):
            return "n.d." if x != x else nb(x, d)

        for _, x in be.iterrows():
            part = "n.d." if x["part_expliquee_90j"] != x["part_expliquee_90j"] else f"{nb(x['part_expliquee_90j'] * 100)} %"
            L.append(f"| {x['actif']} | {f(x['beta_90j'])} | {f(x['correlation_90j'])} | {part} | "
                     f"{f(x['beta_1an'])} | {f(x['beta_1an_jours_de_baisse'])} |")
        L.append("")
        L.append("Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 "
                 "pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des "
                 "mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.")
        L.append("")

    anomalies = fraicheur()
    L.append("## État et fraîcheur des sources")
    if anomalies == 0:
        L.append("**Relevé complet : toutes les sources sont à jour.**")
    else:
        L.append(f"**Attention : {anomalies} source(s) en échec ou en retard.** Une donnée absente ou périmée "
                 "est « indisponible » : elle ne compte jamais en faveur d'un trade.")
    L.append("")
    L.append("| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |")
    L.append("|---|---|---|---|---|---|---|")
    for nom, e in ETAT.items():
        age = "" if e.get("age_jours") is None else f"{e['age_jours']} j"
        L.append(f"| {nom} | {e['nature']} | {'ok' if e['ok'] else '**échec**'} | {e['derniere_date'] or ''} | "
                 f"{age} | {e['fraicheur']} | {e['note']} |")
    L.append("")
    L.append("Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). "
             "À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, "
             "sans jamais dépasser 0 dans le sens du trade envisagé.")
    L.append("")
    L.append("Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et "
             "`rapport/papier.md` (suivi des plans en mode papier).")
    L.append("")
    with open(chemin("dernier.md"), "w", encoding="utf-8") as f_:
        f_.write("\n".join(L))


def main() -> int:
    os.makedirs(DATA, exist_ok=True)
    for nom, fonction in SOURCES.items():
        executer(nom, fonction)
    p = ajouter_euros()
    ecrire_dernier(p)
    with open(chemin("etat.json"), "w", encoding="utf-8") as f:
        json.dump({"execution_utc": maintenant().isoformat(timespec="seconds"), "sources": ETAT}, f,
                  ensure_ascii=False, indent=2)
    # Le lancement n'est en échec que si le prix manque : c'est la seule donnée indispensable.
    return 0 if ETAT.get("prix", {}).get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
