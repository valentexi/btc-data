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
  etat.json               état de chaque source lors du dernier lancement
  dernier.md              relevé lisible, prix en euros
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys
import time
import zipfile

import pandas as pd
import requests

from outils import DATA, chemin, fusionner, lire, nb, pct, pct_brut, prix

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
        ancien = lire(FICHIERS.get(nom, ""))
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


FICHIERS = {
    "prix": "btc_jour.csv",
    "eurusd": "eurusd.csv",
    "financement": "financement_kraken.csv",
    "derives": "derives_instantane.csv",
    "dvol": "dvol.csv",
    "peur_avidite": "peur_avidite.csv",
    "macro": "macro.csv",
    "onchain": "onchain.csv",
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
}


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
        p["eurusd"] = p["eurusd"].ffill()
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

    L.append("## État des sources")
    L.append("| Source | État | Dernière date | Remarque |")
    L.append("|---|---|---|---|")
    for nom, e in ETAT.items():
        L.append(f"| {nom} | {'ok' if e['ok'] else '**échec**'} | {e['derniere_date'] or ''} | {e['note']} |")
    L.append("")
    L.append("Non collecté automatiquement : flux des ETF Bitcoin et carte des liquidations (pas de source gratuite fiable).")
    L.append("")
    with open(chemin("dernier.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


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
