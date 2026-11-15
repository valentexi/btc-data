#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mode papier : suivi automatique des plans, sans argent réel.

Deux registres de plans, rejoués heure par heure (clôtures jugées sur les bougies de 4 heures) :
- papier/plans.csv : plans des analyses de Claude ;
- papier/plans_regles.csv : plans des règles mécaniques S4 et L7, inscrits d'office par ce script.

Intégrité (version 3, 15 nov. 2026) :
- papier/registre.csv garde, pour chaque plan et chaque annulation, l'heure où le robot l'a vu pour la première
  fois et son empreinte. Une ligne déjà enregistrée ne doit plus changer : une modification est signalée et le
  plan sort du critère.
- Un plan de Claude ne compte au critère que s'il a été enregistré AVANT son entrée.
- Annuler un plan : ajouter une ligne à papier/annulations.csv (id, annule_utc, motif). L'annulation prend effet
  à l'heure la plus tardive entre `annule_utc` et son enregistrement : jamais rétroactive. Avant l'entrée, le plan
  ne se déclenche plus ; après l'entrée, la position est soldée à la clôture de la bougie en cours à cette heure.

Colonnes de plans.csv (heures en UTC, prix en dollars) :
  id, cree_utc, source, sens (long|short), declencheur, zone_bas, zone_haut, niveau,
  entree, stop, obj1, obj2, expire_utc, sortie_utc, risque_eur, biais, note, condition_financement

Déclencheurs :
  immediat         entrée à l'ouverture de la première bougie après la création
  limite           ordre limite au prix `entree`
  cloture_4h       une bougie de 4 h clôture au-delà de `niveau` (au-dessus pour un long, en dessous pour un short)
  cloture_jour     même chose pour la clôture journalière (0 h UTC)
  zone_cloture_4h  le prix entre dans la zone [zone_bas, zone_haut], puis une bougie de 4 h clôture au-delà de `niveau`
Après un déclencheur en clôture, l'entrée théorique se fait à l'ouverture de la bougie suivante. Si elle est plus
de 0,5 % moins bonne que `entree`, le plan est annulé (on ne court pas après le prix).
obj1 vide : sortie unique à obj2. Sinon : moitié à obj1, stop ramené à l'entrée, reste à obj2.
condition_financement (facultatif) : positif_ou_nul ou negatif_ou_nul, vérifiée sur le financement Kraken de
l'heure du déclenchement ; non remplie ou inconnue : le plan est abandonné.
Plans des règles : stop_pct, obj_pct et duree_h remplacent stop, obj2 et sortie_utc (calculés sur l'entrée réelle).

Bougies : les plans créés depuis DEBUT_KRAKEN sont rejoués sur les bougies d'une heure du contrat perpétuel Kraken
PF_XBTUSD (data/h1_kraken.csv) ; les plans antérieurs restent sur Coinbase.

Scénarios (papier/scenarios.csv) : id, cree_utc, source, horizon_j, seuil_bas, seuil_haut, p_baissier, p_neutre,
p_haussier, note. Seuils en dollars, probabilités en % (total 100). Baissier : prix sous seuil_bas à l'échéance ;
haussier : au-dessus de seuil_haut ; neutre : entre les deux. Une ligne ne compte que si elle est enregistrée dans les
6 heures suivant cree_utc, et ne se modifie plus.

Configurations (papier/configurations.csv, facultatif) : id, configuration. Code du backtest (A-L, C-S, D-S...) d'un
plan dont la note ne le contient pas. Sert au tableau « par configuration ».
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import sys

import numpy as np
import pandas as pd

from outils import RACINE, RAPPORT, eur, lire, lire_h4, nb, prix
from simulation import barres, simuler
from stats import MIN_EPISODES, episodes, ic_episodes

PLANS = os.environ.get("BTC_PLANS", os.path.join(RACINE, "papier", "plans.csv"))
DOSSIER = os.path.dirname(PLANS)
PLANS_REGLES = os.path.join(DOSSIER, "plans_regles.csv")
ANNULATIONS = os.path.join(DOSSIER, "annulations.csv")
REGISTRE = os.path.join(DOSSIER, "registre.csv")
RESULTATS = os.path.join(DOSSIER, "resultats.csv")

PALIERS = (30, 60, 100)    # bilans à dates fixes (nombre de plans comptés clos), puis tous les 50
ECART_MAX = 0.005          # entrée théorique plus de 0,5 % moins bonne que prévu : plan annulé
REF_STOP, REF_OBJ, REF_BARRES = 0.04, 0.065, 42
COLONNES = ["id", "cree_utc", "source", "sens", "declencheur", "zone_bas", "zone_haut", "niveau", "entree", "stop",
            "obj1", "obj2", "expire_utc", "sortie_utc", "risque_eur", "biais", "note", "condition_financement"]
COLONNES_REGLES = ["id", "regle", "cree_utc", "source", "sens", "declencheur", "stop_pct", "obj_pct", "duree_h",
                   "expire_utc", "risque_eur", "biais", "note"]
ENTRES = ("clos", "ouvert")

# Depuis cette heure (UTC), les nouveaux plans sont rejoués sur les bougies du contrat perpétuel Kraken.
DEBUT_KRAKEN = "2026-11-15T19:00"
CONFIGURATIONS = os.path.join(DOSSIER, "configurations.csv")     # id, configuration (code du backtest)
NOMS_CONFIG = {"A-L": "long sur rejet d'un support", "A-S": "short sur rejet d'une résistance",
               "B-L": "long sur rebond sur une moyenne", "B-S": "short sur rejet sous une moyenne",
               "C-L": "long sur cassure d'une résistance", "C-S": "short sur cassure d'un support",
               "D-L": "long sur retour au-dessus d'une résistance cassée", "D-S": "short sur rebond raté"}

# Scénarios : prévisions à quelques jours, confrontées au prix à l'échéance.
SCENARIOS = os.path.join(DOSSIER, "scenarios.csv")
COLONNES_SCENARIOS = ["id", "cree_utc", "source", "horizon_j", "seuil_bas", "seuil_haut",
                      "p_baissier", "p_neutre", "p_haussier", "note"]
ISSUES = ("baissier", "neutre", "haussier")
DELAI_SCENARIO_H = 6       # une prévision ne compte que si elle est enregistrée dans les 6 heures
MIN_SCENARIOS = 20         # aucune conclusion avant 20 prévisions comptées résolues


def maintenant() -> pd.Timestamp:
    t = os.environ.get("BTC_MAINTENANT")              # pour les tests
    return pd.Timestamp(t, tz="UTC") if t else pd.Timestamp.now(tz="UTC")


def _t(x) -> pd.Timestamp | None:
    if x is None or (isinstance(x, float) and x != x) or str(x).strip() == "":
        return None
    t = pd.Timestamp(str(x).strip().replace("Z", ""))
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def _f(x) -> float | None:
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _np(t: pd.Timestamp) -> np.datetime64:
    return np.datetime64(t.tz_convert(None))


# ------------------------------------------------------------------ registre
def empreinte(ligne: dict) -> str:
    """Empreinte des champs renseignés : une colonne vide ajoutée au fichier ne change pas l'empreinte."""
    champs = sorted((str(k), str(v).strip()) for k, v in ligne.items() if str(v).strip() not in ("", "nan"))
    return hashlib.sha256("|".join(f"{k}={v}" for k, v in champs).encode()).hexdigest()[:16]


def tenir_registre(entrees: list[tuple[str, dict]], quand: pd.Timestamp) -> tuple[dict, list[dict]]:
    """Enregistre les nouvelles lignes, ne modifie jamais les anciennes. Renvoie le registre et les anomalies."""
    reg = pd.read_csv(REGISTRE, dtype=str).fillna("") if os.path.exists(REGISTRE) else \
        pd.DataFrame(columns=["cle", "premiere_vue_utc", "empreinte"])
    connus = {r["cle"]: r for _, r in reg.iterrows()}
    anomalies, nouveaux = [], []
    presents = set()
    for cle, ligne in entrees:
        presents.add(cle)
        e = empreinte(ligne)
        if cle not in connus:
            r = {"cle": cle, "premiere_vue_utc": quand.strftime("%Y-%m-%dT%H:%M:%SZ"), "empreinte": e}
            nouveaux.append(r)
            connus[cle] = r
        elif connus[cle]["empreinte"] != e:
            anomalies.append({"cle": cle, "nature": "modifiée après enregistrement",
                              "enregistree": connus[cle]["premiere_vue_utc"], "empreinte": e})
    for cle, r in connus.items():
        if cle not in presents:
            anomalies.append({"cle": cle, "nature": "supprimée après enregistrement",
                              "enregistree": r["premiere_vue_utc"], "empreinte": ""})
    if nouveaux:
        os.makedirs(DOSSIER, exist_ok=True)
        pd.concat([reg, pd.DataFrame(nouveaux)], ignore_index=True).to_csv(REGISTRE, index=False)
    return connus, anomalies


# ---------------------------------------------------------------- évaluation
def _financement(fin_h: pd.Series | None, t: np.datetime64) -> float | None:
    """Financement Kraken (% par 8 h) en vigueur à l'instant t : dernier taux horaire publié, 2 heures au plus."""
    if fin_h is None or not len(fin_h):
        return None
    avant = fin_h[(fin_h.index <= t) & (fin_h.index >= t - np.timedelta64(2, "h"))]
    return float(avant.iloc[-1]) if len(avant) else None


def evaluer(plan: dict, B: dict, annule: pd.Timestamp | None = None, fin_h: pd.Series | None = None) -> dict:
    """Rejoue un plan. Aucune information postérieure n'est utilisée pour décider."""
    sens = 1 if str(plan["sens"]).strip().lower() == "long" else -1
    cree, expire, sortie = _t(plan["cree_utc"]), _t(plan.get("expire_utc")), _t(plan.get("sortie_utc"))
    decl = str(plan["declencheur"]).strip()
    stop, obj1, obj2 = _f(plan.get("stop")), _f(plan.get("obj1")), _f(plan.get("obj2"))
    stop_pct, obj_pct, duree_h = _f(plan.get("stop_pct")), _f(plan.get("obj_pct")), _f(plan.get("duree_h"))
    relatif = stop_pct is not None and obj_pct is not None
    niveau, entree_prevue = _f(plan.get("niveau")), _f(plan.get("entree"))
    zb, zh = _f(plan.get("zone_bas")), _f(plan.get("zone_haut"))
    cond = str(plan.get("condition_financement", "") or "").strip()
    res = {"id": plan["id"], "sens": "long" if sens == 1 else "short", "etat": "", "t_entree": "", "prix_entree": np.nan,
           "t_sortie": "", "motif": "", "R": np.nan, "R_fin": np.nan, "eur": np.nan, "detail": "", "t_declenche": "",
           "stop_calcule": np.nan, "obj2_calcule": np.nan}
    if cree is None or (not relatif and (stop is None or obj2 is None)):
        res["etat"] = "plan incomplet"
        return res
    if annule is not None:
        expire = annule if expire is None else min(expire, annule)
    pas = int(B.get("pas_h", 4))
    debut = B["t"]                                   # début de chaque bougie
    fin = debut + np.timedelta64(pas, "h")
    heure_fin = (pd.DatetimeIndex(debut).hour.to_numpy() + pas) % 24
    cloture_4h, cloture_jour = heure_fin % 4 == 0, heure_fin == 0    # la bougie termine-t-elle une bougie de 4 h, un jour ?
    cree64 = _np(cree)
    exp64 = _np(expire) if expire is not None else np.datetime64("2262-01-01")
    apres = np.flatnonzero(debut >= cree64)          # bougies entièrement postérieures à la création
    closes = np.flatnonzero((fin > cree64) & (fin <= exp64))   # clôtures connues après la création, avant expiration
    derniere = B["n"] - 1
    perime = fin[derniere] >= exp64                  # les données couvrent-elles l'expiration ?
    fin_ou_attente = "expiré sans entrée"
    if annule is not None and (expire is None or annule <= expire) and perime:
        fin_ou_attente = "annulé avant entrée"

    def au_dela(k):                                  # clôture du bon côté du niveau
        return B["c"][k] > niveau if sens == 1 else B["c"][k] < niveau

    i, prix_limite = None, None
    if decl == "immediat":
        if len(apres) and debut[apres[0]] < exp64:
            i = int(apres[0])
        elif len(apres):
            res["etat"] = fin_ou_attente
            return res
    elif decl == "limite" and entree_prevue is not None:
        for k in apres:
            if debut[k] >= exp64:
                break
            touche = B["l"][k] <= entree_prevue if sens == 1 else B["h"][k] >= entree_prevue
            if touche:
                mieux = B["o"][k] < entree_prevue if sens == 1 else B["o"][k] > entree_prevue
                i, prix_limite = int(k), (float(B["o"][k]) if mieux else entree_prevue)
                break
    elif decl in ("cloture_4h", "cloture_jour") and niveau is not None:
        for k in closes:
            if not (cloture_jour[k] if decl == "cloture_jour" else cloture_4h[k]):
                continue
            if au_dela(k):
                i = int(k) + 1
                break
    elif decl == "zone_cloture_4h" and niveau is not None and zb is not None and zh is not None:
        dans_zone = False
        for k in closes:
            if debut[k] >= cree64 and (B["h"][k] >= zb if sens == -1 else B["l"][k] <= zh):
                dans_zone = True
            if dans_zone and cloture_4h[k] and au_dela(k):
                i = int(k) + 1
                break
    else:
        res["etat"] = "déclencheur inconnu ou incomplet"
        return res

    if i is None:
        res["etat"] = fin_ou_attente if perime else "en attente du déclencheur"
        return res
    t_decl = debut[i] if i <= derniere else fin[derniere]   # heure de la clôture qui déclenche (ou de l'entrée)
    res["t_declenche"] = str(pd.Timestamp(t_decl))[:16]
    if cond:
        v = _financement(fin_h, t_decl)
        if v is None:
            dernier_taux = fin_h.index[-1] if fin_h is not None and len(fin_h) else None
            if dernier_taux is None or dernier_taux < t_decl:
                res["etat"] = "déclenché, condition de financement en attente de donnée"
            else:
                res["etat"] = "abandonné : financement inconnu au déclenchement"
            return res
        ok = v >= 0 if cond == "positif_ou_nul" else (v <= 0 if cond == "negatif_ou_nul" else False)
        res["detail"] = f"financement au déclenchement {v:+.4f} % par 8 h".replace(".", ",")
        if not ok:
            res["etat"] = "abandonné : condition de financement non remplie"
            return res
    if i > derniere:
        res["etat"] = "déclenché, entrée à la prochaine bougie"
        return res
    E = float(B["o"][i]) if prix_limite is None else prix_limite
    if entree_prevue is not None and prix_limite is None and sens * (E - entree_prevue) / entree_prevue > ECART_MAX:
        res.update({"etat": "annulé : entrée trop éloignée du prix prévu", "t_entree": str(B["date"][i]),
                    "detail": f"ouverture à {E:,.0f} $ pour {entree_prevue:,.0f} $ prévus".replace(",", " ")})
        return res
    if relatif:
        stop, obj1, obj2 = E * (1 - sens * stop_pct), None, E * (1 + sens * obj_pct)
        fin_duree = pd.Timestamp(debut[i], tz="UTC") + pd.Timedelta(hours=duree_h or 168)
        sortie = fin_duree if sortie is None else min(sortie, fin_duree)
        res["stop_calcule"], res["obj2_calcule"] = stop, obj2
    i_max, termine, coupe = derniere, False, False
    if sortie is not None:                           # sortie prévue : dernière clôture avant l'heure limite
        avant = np.flatnonzero(fin <= _np(sortie))
        i_max = max(int(avant[-1]) if len(avant) else i, i)
        termine = bool(fin[derniere] >= _np(sortie))
    if annule is not None:                           # annulation : première clôture après, jamais avant
        apres_a = np.flatnonzero(fin >= _np(annule))
        if len(apres_a) and max(int(apres_a[0]), i) < i_max:
            i_max, coupe = max(int(apres_a[0]), i), True
        termine = termine or bool(len(apres_a))
    t = simuler(B, i, sens, stop, obj1, obj2, i_max, entree=prix_limite)
    if t is None:
        res["etat"] = "annulé : stop déjà dépassé à l'entrée"
        res["t_entree"] = str(B["date"][i])
        return res
    ouvert = "durée" in t["motif"] and not termine
    motif = t["motif"]
    if not ouvert and "durée" in motif and coupe:
        motif = "sortie sur annulation"
    risque = _f(plan.get("risque_eur")) or 0.0
    detail = res["detail"]
    if entree_prevue is not None:
        detail = (detail + " ; " if detail else "") + f"écart à l'entrée prévue {(t['entree'] / entree_prevue - 1) * 100:+.2f} %".replace(".", ",")
    res.update({"etat": "ouvert" if ouvert else "clos", "t_entree": t["t_entree"], "prix_entree": t["entree"],
                "t_sortie": "" if ouvert else t["t_sortie"], "motif": "en cours" if ouvert else motif,
                "R": t["R"], "R_fin": t["R_fin"], "eur": t["R"] * risque, "detail": detail})
    return res


def reference(plan: dict, B: dict, sens: int) -> float:
    """Long ou short systématique au moment où le plan est créé : stop 4 %, objectif 6,5 %, 7 jours."""
    cree = _t(plan["cree_utc"])
    apres = np.flatnonzero(B["t"] >= _np(cree))
    if not len(apres):
        return float("nan")
    i = int(apres[0])
    E = B["o"][i]
    i_max = i + REF_BARRES * 4 // int(B.get("pas_h", 4)) - 1
    t = simuler(B, i, sens, E * (1 - sens * REF_STOP), None, E * (1 + sens * REF_OBJ), i_max)
    if t is None or (i_max > B["n"] - 1 and "durée" in t["motif"]):
        return float("nan")                           # pas encore dénoué
    return t["R"]


# ------------------------------------------------------------- critère
def paliers_atteints(n: int) -> list[int]:
    out, k, liste = [], 0, list(PALIERS)
    while True:
        k = liste[len(out)] if len(out) < len(liste) else liste[-1] + 50 * (len(out) - len(liste) + 1)
        if k > n:
            return out
        out.append(k)


def prochain_palier(n: int) -> int:
    faits = paliers_atteints(n)
    k = len(faits)
    return PALIERS[k] if k < len(PALIERS) else PALIERS[-1] + 50 * (k - len(PALIERS) + 1)


def bilans(clos: pd.DataFrame) -> list[dict]:
    """Bilan à chaque palier atteint, sur les k premiers plans comptés clos (ordre d'entrée)."""
    c = clos.sort_values("t_entree")
    out = []
    for k in paliers_atteints(len(c)):
        sub = c.iloc[:k]
        r = sub["R"].to_numpy(float)
        ep = episodes(sub["t_entree"])
        ne = int(ep.max()) + 1 if len(ep) else 0
        lo, hi = ic_episodes(r, ep)
        if ne < MIN_EPISODES:
            v = f"épisodes insuffisants ({ne} sur {MIN_EPISODES})"
        elif lo > 0:
            v = "favorable"
        elif hi < 0:
            v = "défavorable"
        else:
            v = "non concluant"
        out.append({"palier": k, "r": float(r.mean()), "lo": lo, "hi": hi, "episodes": ne, "verdict": v})
    return out


# ---------------------------------------------------- règles mécaniques
def generer_regles(regles_df: pd.DataFrame, evals: dict, quand: pd.Timestamp) -> pd.DataFrame:
    """Inscrit d'office le plan d'une règle mécanique active à la dernière clôture (une position à la fois)."""
    import backtest
    import regles

    donnees = backtest.charger()
    if donnees is None:
        return regles_df
    b = regles.biais_du_jour(donnees[0])
    jour = b["date"]
    if jour < regles.DEBUT_REGLES:
        return regles_df
    # Le plan est daté de la clôture qui donne le signal (0 h UTC), pas du passage du robot : l'entrée se fait
    # à l'ouverture de 0 h UTC, comme au backtest, même si le lancement programmé a du retard. L'heure réelle
    # d'inscription reste dans papier/registre.csv (première apparition).
    cloture = pd.Timestamp(jour, tz="UTC") + pd.Timedelta(days=1)
    limite = cloture + pd.Timedelta(days=1)                         # au plus 24 h après la clôture
    if quand < cloture or quand >= limite:
        return regles_df
    nouveaux = []
    for r in regles.REGLES_PAPIER:
        ident = f"{r['id']}-{jour}"
        if not regles.signal(r, b["biais"]) or ident in set(regles_df["id"]):
            continue
        en_cours = [p for p in regles_df[regles_df["regle"] == r["id"]]["id"]
                    if evals.get(p, {}).get("etat", "") not in ("clos", "expiré sans entrée", "annulé avant entrée")
                    and not str(evals.get(p, {}).get("etat", "")).startswith("annulé")]
        if en_cours:
            continue                                   # une position à la fois par règle, comme au backtest
        nouveaux.append({
            "id": ident, "regle": r["id"], "cree_utc": cloture.strftime("%Y-%m-%dT%H:%M"),
            "source": f"règle {r['id']} : {r['nom']}", "sens": "long" if r["sens"] == 1 else "short",
            "declencheur": "immediat", "stop_pct": regles.STOP_PCT, "obj_pct": regles.OBJ_PCT,
            "duree_h": regles.DUREE_H, "expire_utc": (cloture + pd.Timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M"),
            "risque_eur": 2.5, "biais": int(b["biais"]), "note": f"signal de la clôture du {jour}",
        })
    if not nouveaux:
        return regles_df
    out = pd.concat([regles_df, pd.DataFrame(nouveaux).astype(str)], ignore_index=True)
    out[COLONNES_REGLES].to_csv(PLANS_REGLES, index=False)
    return out


# ------------------------------------------------- bougies, configurations
def choisir_bougies(pl: dict, B1: dict | None, B4: dict, BK: dict | None) -> tuple[dict, str]:
    """Bougies sur lesquelles un plan est rejoué, fixées une fois pour toutes par sa date de création.

    Plans créés depuis DEBUT_KRAKEN : bougies d'une heure du contrat perpétuel Kraken (ce qui serait exécuté).
    Plans antérieurs : bougies Coinbase, comme à leur enregistrement (rien de ce qui est déjà joué ne change).
    Sans bougies d'une heure couvrant le plan : bougies de 4 heures Coinbase."""
    cree = _t(pl.get("cree_utc"))
    if cree is not None:
        if BK is not None and cree >= _t(DEBUT_KRAKEN) and _np(cree) >= BK["t"][0]:
            return BK, "contrat Kraken"
        if B1 is not None and _np(cree) >= B1["t"][0]:
            return B1, "Coinbase"
    return B4, "Coinbase"


def configuration(ident: str, note: str, table: dict[str, str]) -> str:
    """Code de la configuration du backtest (A-L, C-S, D-S...) : fichier configurations.csv, sinon lu dans la note."""
    if table.get(ident):
        return table[ident]
    m = re.search(r"(?<![\w-])([A-D]-[LS]\+?(?:-mm\d+s?)?)(?![\w-])", str(note))
    return m.group(1) if m else ""


# ---------------------------------------------------------------- scénarios
def evaluer_scenario(sc: dict, B4: dict, vue: pd.Timestamp | None) -> dict:
    """Prévision à `horizon_j` jours : trois issues séparées par deux seuils (dollars).

    Baissier : prix sous `seuil_bas` à l'échéance ; haussier : au-dessus de `seuil_haut` ; neutre : entre les deux.
    Jugée sur la clôture de la dernière bougie de 4 heures terminée à l'échéance. Ne compte que si la ligne a été
    enregistrée dans les DELAI_SCENARIO_H heures suivant sa création : une prévision écrite après coup ne vaut rien."""
    res = {"id": sc.get("id", "?"), "etat": "", "issue": "", "prix": np.nan, "echeance": "", "p_issue": np.nan,
           "brier": np.nan, "compte": "", "p": [np.nan] * 3, "cree": None}
    try:
        cree = _t(sc.get("cree_utc"))
    except Exception:  # noqa: BLE001
        cree = None
    h, bas, haut = _f(sc.get("horizon_j")), _f(sc.get("seuil_bas")), _f(sc.get("seuil_haut"))
    p = [_f(sc.get(k)) for k in ("p_baissier", "p_neutre", "p_haussier")]
    if cree is None or h is None or h <= 0 or bas is None or haut is None or None in p or not bas < haut or min(p) < 0:
        res["etat"] = "ligne illisible"
        return res
    total = sum(p)
    if not (abs(total - 100) <= 1.5 or abs(total - 1) <= 0.015):
        res["etat"] = "ligne illisible : le total des probabilités n'est pas 100 %"
        return res
    p = [x / total for x in p]
    ech = cree + pd.Timedelta(days=h)
    res.update({"p": p, "cree": cree, "echeance": ech.strftime("%Y-%m-%d %H:%M")})
    tardif = vue is None or (vue - cree).total_seconds() / 3600 > DELAI_SCENARIO_H
    res["compte"] = "non (enregistré trop tard)" if tardif else "oui"
    fin = B4["t"] + np.timedelta64(int(B4.get("pas_h", 4)), "h")
    ech64 = _np(ech)

    def issue(x):
        return 0 if x < bas else (2 if x > haut else 1)

    if fin[-1] < ech64:                              # l'échéance n'est pas encore couverte par les données
        res.update({"etat": "en cours", "prix": float(B4["c"][-1]), "issue": ISSUES[issue(float(B4["c"][-1]))]})
        return res
    avant = np.flatnonzero(fin <= ech64)
    if not len(avant) or ech64 - fin[avant[-1]] > np.timedelta64(8, "h"):
        res["etat"] = "donnée manquante à l'échéance"
        return res
    x = float(B4["c"][avant[-1]])
    k = issue(x)
    res.update({"etat": "résolu", "prix": x, "issue": ISSUES[k], "p_issue": p[k],
                "brier": float(sum((p[j] - (1.0 if j == k else 0.0)) ** 2 for j in range(3)))})
    return res


def independantes(S: list[dict]) -> int:
    """Nombre de prévisions qui ne se recouvrent pas (chacune commence après l'échéance de la précédente retenue)."""
    n, libre = 0, None
    for s in sorted((s for s in S if s["cree"] is not None), key=lambda s: s["cree"]):
        if libre is None or s["cree"] >= libre:
            n, libre = n + 1, _t(s["echeance"])
    return n


def section_scenarios(S: list[dict], fx: float) -> list[str]:
    L = ["## Scénarios à 7 jours : justesse des probabilités"]
    if not S:
        return L + ["Aucune prévision enregistrée (`papier/scenarios.csv`).", ""]
    L.append("Chaque analyse donne trois probabilités (baissier, neutre, haussier) séparées par deux seuils de prix. "
             "À l'échéance, le robot regarde où le prix a fini. Une prévision ne compte que si elle a été enregistrée "
             f"dans les {DELAI_SCENARIO_H} heures suivant l'analyse.")
    L.append("")
    comptes = [s for s in S if s["etat"] == "résolu" and s["compte"] == "oui"]
    n = len(comptes)
    L.append(f"- Enregistrées : {len(S)}. Résolues : {sum(s['etat'] == 'résolu' for s in S)} (comptées : {n}). "
             f"En cours : {sum(s['etat'] == 'en cours' for s in S)}.")
    if n:
        pm = float(np.mean([s["p_issue"] for s in comptes]))
        br = float(np.mean([s["brier"] for s in comptes]))
        juste = float(np.mean([s["p_issue"] >= max(s["p"]) - 1e-12 for s in comptes]))
        L.append(f"- Probabilité moyenne donnée à l'issue qui s'est réalisée : {nb(pm * 100)} % (au hasard : 33 %).")
        L.append(f"- Score de Brier moyen : {nb(br, 2)} (0 = parfait ; 0,67 = trois issues à 33 % ; au-dessus de 0,67 : "
                 "pire que de ne rien savoir).")
        L.append(f"- L'issue jugée la plus probable s'est réalisée dans {nb(juste * 100)} % des cas.")
        L.append("")
        L.append("| Issue | Probabilité moyenne annoncée | Fréquence observée |")
        L.append("|---|---|---|")
        for j, nom in enumerate(ISSUES):
            L.append(f"| {nom} | {nb(float(np.mean([s['p'][j] for s in comptes])) * 100)} % | "
                     f"{nb(float(np.mean([s['issue'] == nom for s in comptes])) * 100)} % |")
        L.append("")
    L.append(f"- Prévisions indépendantes (qui ne se recouvrent pas) parmi les comptées résolues : {independantes(comptes)}. "
             f"**Aucune conclusion avant {MIN_SCENARIOS} prévisions comptées résolues.**")
    L.append("")
    L.append("| Prévision | Créée (UTC) | Échéance (UTC) | Seuils | Baissier / neutre / haussier | État | Prix | Issue | "
             "Probabilité donnée | Comptée |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in S[::-1]:
        if s["cree"] is None:
            L.append(f"| {s['id']} |  |  |  |  | {s['etat']} |  |  |  |  |")
            continue
        probas = " / ".join(f"{nb(x * 100)} %" for x in s["p"])
        px = "" if s["prix"] != s["prix"] else prix(s["prix"], fx)
        issue_ = s["issue"] + (" (provisoire)" if s["etat"] == "en cours" and s["issue"] else "")
        donnee = "" if s["p_issue"] != s["p_issue"] else f"{nb(s['p_issue'] * 100)} %"
        L.append(f"| {s['id']} | {s['cree'].strftime('%Y-%m-%d %H:%M')} | {s['echeance']} | {s['seuils']} | {probas} | "
                 f"{s['etat']} | {px} | {issue_} | {donnee} | {s['compte']} |")
    L.append("")
    return L


# ------------------------------------------------------------- rapport
def r_(x):
    return "n.d." if x != x else f"{x:+.2f}".replace(".", ",") + " R"


def _lire(chemin_: str, colonnes: list[str]) -> pd.DataFrame:
    if not os.path.exists(chemin_):
        return pd.DataFrame(columns=colonnes)
    df = pd.read_csv(chemin_, dtype=str).fillna("")
    for c in colonnes:
        if c not in df.columns:
            df[c] = ""
    return df


def _resume(df: pd.DataFrame) -> str:
    clos = df[df["etat"] == "clos"]
    n = len(clos)
    if not n:
        return "aucun plan clos"
    r = clos["R"].to_numpy(float)
    txt = (f"{n} clos, {nb((r > 0).mean() * 100)} % gagnants, {r_(r.mean())} par trade, "
           f"{r_(r.sum())} au total ({eur(float(clos['eur'].sum()), 2)})")
    if n >= 5:
        lo, hi = ic_episodes(r, episodes(clos["t_entree"]))
        txt += f", intervalle à 95 % {r_(lo)} à {r_(hi)}"
    return txt


def main() -> int:
    os.makedirs(RAPPORT, exist_ok=True)
    sortie = os.path.join(RAPPORT, "papier.md")
    quand = maintenant()
    h4, p = lire_h4(), lire("btc_jour.csv")
    if not os.path.exists(PLANS) or h4 is None:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write("# Mode papier\n\nAucun plan enregistré ou bougies de 4 heures indisponibles.\n")
        return 0
    plans = _lire(PLANS, COLONNES)
    regles_df = _lire(PLANS_REGLES, COLONNES_REGLES)
    annul = _lire(ANNULATIONS, ["id", "annule_utc", "motif"])
    fk = lire("financement_kraken.csv")
    fin = {} if fk is None else {d: v / 100.0 for d, v in zip(fk["date"], fk["cumul_jour_pct"])}
    fh = lire("financement_kraken_h.csv")
    fin_h = None
    if fh is not None:
        fin_h = pd.Series(fh["taux_8h_pct"].to_numpy(float),
                          index=pd.to_datetime(fh["date"]).to_numpy().astype("datetime64[s]")).sort_index()
    B4 = barres(h4.sort_values("date").reset_index(drop=True), fin)
    h1 = lire("h1_recent.csv")
    B1 = barres(h1.sort_values("date").reset_index(drop=True), fin, pas_h=1) if h1 is not None and len(h1) > 48 else None

    hk = lire("h1_kraken.csv")
    BK = barres(hk.sort_values("date").reset_index(drop=True), fin, pas_h=1) if hk is not None and len(hk) > 48 else None
    scenarios = _lire(SCENARIOS, COLONNES_SCENARIOS)
    configs = {x["id"]: x["configuration"].strip() for x in _lire(CONFIGURATIONS, ["id", "configuration"]).to_dict("records")}

    def bougies_pour(pl):
        return choisir_bougies(pl, B1, B4, BK)[0]

    B = B1 if B1 is not None else B4
    fx = float(p["eurusd"].dropna().iloc[-1]) if p is not None and "eurusd" in p.columns else float("nan")

    # 1. Règles mécaniques : état des plans existants, puis inscription d'un nouveau plan si une règle est active
    def evaluer_sur(pl, annule=None):
        try:
            return evaluer(pl, bougies_pour(pl), annule, fin_h)
        except Exception as e:  # noqa: BLE001 - une ligne mal saisie ne doit pas bloquer les autres
            return {"id": pl.get("id", "?"), "sens": pl.get("sens", ""), "etat": f"ligne illisible : {e}",
                    "t_entree": "", "prix_entree": np.nan, "t_sortie": "", "motif": "", "R": np.nan, "R_fin": np.nan,
                    "eur": np.nan, "detail": "", "t_declenche": "", "stop_calcule": np.nan, "obj2_calcule": np.nan}

    try:
        evals_regles = {pl["id"]: evaluer_sur(pl) for pl in regles_df.to_dict("records")}
        regles_df = generer_regles(regles_df, evals_regles, quand)
    except Exception as e:  # noqa: BLE001
        print(f"Règles mécaniques : échec ({e})")

    # 2. Registre : première apparition et empreinte de chaque ligne
    entrees = [(pl["id"], {k: pl.get(k, "") for k in COLONNES}) for pl in plans.to_dict("records")]
    entrees += [(pl["id"], {k: pl.get(k, "") for k in COLONNES_REGLES}) for pl in regles_df.to_dict("records")]
    entrees += [(f"annulation:{a['id']}", a) for a in annul.to_dict("records")]
    entrees += [(f"scenario:{s['id']}", {k: s.get(k, "") for k in COLONNES_SCENARIOS}) for s in scenarios.to_dict("records")]
    registre, anomalies = tenir_registre(entrees, quand)
    modifiees = {a["cle"] for a in anomalies}

    def vue(cle):
        r = registre.get(cle)
        return _t(r["premiere_vue_utc"]) if r is not None else None

    effets = {}
    for a in annul.to_dict("records"):
        t_a, t_v = _t(a.get("annule_utc")), vue(f"annulation:{a['id']}")
        if t_a is not None and t_v is not None and a["id"] not in effets:
            effets[a["id"]] = max(t_a, t_v)

    # 3. Évaluation
    lignes = []
    for registre_nom, df in (("claude", plans), ("regle", regles_df)):
        for pl in df.to_dict("records"):
            r = evaluer_sur(pl, effets.get(pl["id"]) if registre_nom == "claude" else None)
            if registre_nom == "claude" and not str(r["etat"]).startswith("ligne illisible"):
                Bp = bougies_pour(pl)
                r["ref_long"], r["ref_short"] = reference(pl, Bp, 1), reference(pl, Bp, -1)
            else:
                r["ref_long"], r["ref_short"] = np.nan, np.nan
            v = vue(pl["id"])
            r["enregistre_utc"] = "" if v is None else v.strftime("%Y-%m-%d %H:%M")
            compte, raison = "", ""
            if registre_nom == "claude" and r["etat"] in ENTRES:
                if pl["id"] in modifiees:
                    compte, raison = "non", "ligne modifiée après enregistrement"
                elif v is None or v > _t(r["t_entree"]):
                    compte, raison = "non", "enregistré après l'entrée"
                else:
                    compte = "oui"
            try:
                r["bougies"] = choisir_bougies(pl, B1, B4, BK)[1]
            except Exception:  # noqa: BLE001 - date de création illisible
                r["bougies"] = ""
            r["configuration"] = configuration(pl["id"], pl.get("note", ""), configs) if registre_nom == "claude" \
                else str(pl.get("regle", ""))
            t_e = _t(r["t_entree"]) if r.get("t_entree") else None
            r["week_end"] = "" if t_e is None else ("oui" if t_e.dayofweek >= 5 else "non")   # jour UTC, comme au backtest
            r.update({"registre": registre_nom, "compte": compte, "raison": raison, "cree_utc": pl.get("cree_utc", ""),
                      "source": pl.get("source", ""), "note": pl.get("note", ""), "risque_eur": pl.get("risque_eur", ""),
                      "entree_prevue": pl.get("entree", ""), "stop": pl.get("stop", ""), "obj1": pl.get("obj1", ""),
                      "obj2": pl.get("obj2", ""), "declencheur": pl.get("declencheur", ""),
                      "sortie_prevue": pl.get("sortie_utc", "")})
            lignes.append(r)
    R = pd.DataFrame(lignes)
    R.to_csv(RESULTATS, index=False, float_format="%.6g")
    if anomalies:
        pd.DataFrame(anomalies).to_csv(os.path.join(DOSSIER, "anomalies.csv"), index=False)
    elif os.path.exists(os.path.join(DOSSIER, "anomalies.csv")):
        os.remove(os.path.join(DOSSIER, "anomalies.csv"))

    C = R[R["registre"] == "claude"]
    G = R[R["registre"] == "regle"]
    comptes_clos = C[(C["etat"] == "clos") & (C["compte"] == "oui")]
    n = len(comptes_clos)

    L = [f"# Mode papier ({quand.strftime('%d/%m/%Y %H:%M')} UTC)", ""]
    L.append("Suivi automatique, sans argent réel. Déclencheurs, stops et objectifs suivis heure par heure ; clôtures "
             "jugées sur les bougies de 4 heures ; entrée théorique à l'ouverture de la bougie qui suit le déclencheur. "
             f"Résultats nets de frais et de glissement. Dernière bougie connue : {B['date'][-1]} UTC.")
    L.append("")
    L.append(f"Bougies utilisées : les plans créés depuis le {DEBUT_KRAKEN.replace('T', ' à ')} UTC sont rejoués sur le "
             "**contrat perpétuel Kraken PF_XBTUSD** (le prix auquel un ordre serait exécuté) ; les plans antérieurs "
             "restent sur le prix au comptant de Coinbase, comme à leur enregistrement. "
             + (f"Dernière bougie du contrat Kraken : {BK['date'][-1]} UTC." if BK is not None else
                "**Bougies du contrat Kraken indisponibles : les nouveaux plans sont rejoués sur Coinbase en attendant.**"))
    L.append("")
    L.append("## Plans de Claude")
    etats = C["etat"].astype(str)
    L.append(f"- Enregistrés : {len(C)}. Entrés : {int(etats.isin(ENTRES).sum())} (clos {int((etats == 'clos').sum())}, "
             f"ouverts {int((etats == 'ouvert').sum())}). En attente : {int(etats.str.startswith('en attente').sum() + etats.str.startswith('déclenché').sum())}. "
             f"Expirés ou annulés sans entrée : {int((etats.str.startswith('expiré') | etats.str.startswith('annulé')).sum())}. "
             f"Abandonnés (condition non remplie) : {int(etats.str.startswith('abandonné').sum())}.")
    L.append(f"- **Comptés au critère** (enregistrés avant leur entrée, jamais modifiés) : {_resume(C[C['compte'] == 'oui'])}. "
             f"Ouverts et comptés : {int(((C['etat'] == 'ouvert') & (C['compte'] == 'oui')).sum())}.")
    hors = C[C["compte"] == "non"]
    if len(hors):
        L.append("- Hors critère : " + " ; ".join(f"{x['id']} ({x['raison']})" for _, x in hors.iterrows()) + ".")
    L.append(f"- Tous les plans entrés, pour mémoire : {_resume(C)}.")
    L.append("")
    L.append("## Critère de passage en réel")
    L.append(f"Bilans à dates fixes : à {', '.join(str(k) for k in PALIERS)} plans comptés clos, puis tous les 50. "
             f"Un bilan est favorable si l'intervalle à 95 % (tirage par épisodes) est entièrement au-dessus de 0 R, "
             f"donc meilleur que « ne rien faire », avec au moins {MIN_EPISODES} épisodes de marché distincts. "
             "Entre deux bilans, aucune conclusion.")
    L.append("")
    B_ = bilans(comptes_clos)
    if B_:
        L.append("| Bilan | R moyen | Intervalle à 95 % | Épisodes | Verdict |")
        L.append("|---|---|---|---|---|")
        for b in B_:
            L.append(f"| {b['palier']} plans | {r_(b['r'])} | {r_(b['lo'])} à {r_(b['hi'])} | {b['episodes']} | {b['verdict']} |")
        L.append("")
    atteint = any(b["verdict"] == "favorable" for b in B_)
    L.append(f"- Prochain bilan à {prochain_palier(n)} plans comptés clos ({n} pour l'instant).")
    if atteint:
        verdict = "CRITÈRE ATTEINT"
    elif B_ and B_[-1]["verdict"] == "défavorable":
        verdict = "CRITÈRE NON ATTEINT, bilan défavorable : revoir la méthode avant de continuer"
    else:
        verdict = "CRITÈRE NON ATTEINT, rester en mode papier"
    L.append(f"- **Verdict : {verdict}.**")
    L.append("")
    L.append("## Règles mécaniques inscrites d'office (sans jugement)")
    L.append("S4 : short quand le biais mécanique est ≤ −5. L7 : long quand il est ≥ +5. Plan identique au backtest "
             "(stop 4 %, objectif 6,5 %, 7 jours au plus), entrée à 0 h UTC, à l'ouverture qui suit la clôture du signal (même si le "
             "robot passe en retard, 24 h au plus), "
             "une position à la fois par règle. Elles servent d'étalon : le jugement de Claude n'a d'intérêt que s'il "
             "fait mieux qu'elles.")
    L.append("")
    for ident in ("S4", "L7"):
        L.append(f"- {ident} : {_resume(G[G['id'].str.startswith(ident + '-')])}"
                 f" ; ouverts {int(((G['etat'] == 'ouvert') & G['id'].str.startswith(ident + '-')).sum())}.")
    L.append(f"- Comparaison, plans clos : Claude (comptés) {r_(comptes_clos['R'].mean()) if n else 'n.d.'} sur {n} ; "
             f"règles {r_(G[G['etat'] == 'clos']['R'].mean()) if (G['etat'] == 'clos').any() else 'n.d.'} "
             f"sur {int((G['etat'] == 'clos').sum())}. Pour mémoire, long systématique à chaque plan de Claude "
             f"{r_(C['ref_long'].mean()) if C['ref_long'].notna().any() else 'n.d.'}, short systématique "
             f"{r_(C['ref_short'].mean()) if C['ref_short'].notna().any() else 'n.d.'}.")
    L.append("")
    L.append("## Par configuration et par jour d'entrée")
    L.append("Plans clos seulement ; pour Claude, plans comptés au critère. À lire au premier bilan (30 plans) : "
             "avec quelques plans par ligne, ces moyennes ne veulent rien dire.")
    L.append("")
    L.append("| Groupe | Plans clos | R moyen | Total | Ouverts |")
    L.append("|---|---|---|---|---|")

    def ligne_groupe(nom, df):
        clos = df[df["etat"] == "clos"]
        r = clos["R"].to_numpy(float)
        L.append(f"| {nom} | {len(clos)} | {r_(r.mean()) if len(r) else 'n.d.'} | {r_(r.sum()) if len(r) else 'n.d.'} | "
                 f"{int((df['etat'] == 'ouvert').sum())} |")

    Cc = C[C["compte"] == "oui"]
    ligne_groupe("Claude, tous les plans comptés", Cc)
    for code in sorted(set(Cc["configuration"])):
        nom = NOMS_CONFIG.get(code[:3], "configuration non testée au backtest") if code else "configuration non précisée"
        ligne_groupe(f"Claude · {code + ' : ' if code else ''}{nom}", Cc[Cc["configuration"] == code])
    for we, nom in (("non", "entrées en semaine"), ("oui", "entrées le week-end")):
        ligne_groupe(f"Claude · {nom}", Cc[Cc["week_end"] == we])
    for ident in ("S4", "L7"):
        Gi = G[G["id"].str.startswith(ident + "-")]
        ligne_groupe(f"Règle {ident}", Gi)
        for we, nom in (("non", "entrées en semaine"), ("oui", "entrées le week-end")):
            if len(Gi[Gi["week_end"] == we]):
                ligne_groupe(f"Règle {ident} · {nom}", Gi[Gi["week_end"] == we])
    L.append("")
    S = []
    for s in scenarios.to_dict("records"):
        e = evaluer_scenario(s, B4, vue(f"scenario:{s['id']}"))
        if f"scenario:{s['id']}" in modifiees and e["compte"] == "oui":
            e["compte"] = "non (ligne modifiée)"
        b_, h_ = _f(s.get("seuil_bas")), _f(s.get("seuil_haut"))
        e["seuils"] = "" if b_ is None or h_ is None else f"{prix(b_, fx)} et {prix(h_, fx)}"
        S.append(e)
    L.extend(section_scenarios(S, fx))
    L.append("## Intégrité du registre")
    if anomalies:
        L.append(f"**{len(anomalies)} anomalie(s) : une ligne déjà enregistrée a changé ou disparu.** Les plans "
                 "concernés sortent du critère. Pour corriger un plan, ajouter une annulation et un nouveau plan.")
        for a in anomalies:
            L.append(f"- {a['cle']} : {a['nature']} (enregistrée le {a['enregistree']}).")
    else:
        L.append(f"Aucune modification détectée sur les {len(registre)} lignes enregistrées (`papier/registre.csv`).")
    L.append("")
    if len(annul):
        L.append("## Annulations")
        for a in annul.to_dict("records"):
            e = effets.get(a["id"])
            L.append(f"- {a['id']} : demandée pour {a['annule_utc']}, effective le "
                     f"{e.strftime('%Y-%m-%d %H:%M') if e is not None else 'n.d.'} UTC ({a.get('motif', '')}).")
        L.append("")

    def table(df, regle):
        T = ["| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros |"
             + (" Compté |" if not regle else "") + " Configuration | Bougies |"]
        T.append("|---|---|---|---|---|---|---|---|---|---|" + ("---|" if not regle else "") + "---|---|")
        for _, x in df.iloc[::-1].iterrows():
            entree = "" if x["prix_entree"] != x["prix_entree"] else f"{x['t_entree']} à {prix(x['prix_entree'], fx)}"
            T.append(f"| {x['id']} | {x['cree_utc']} | {x['enregistre_utc']} | {x['sens']} | {x['etat']} | {entree} | "
                     f"{x['t_sortie']} | {x['motif']} | {r_(x['R'])} | {'' if x['eur'] != x['eur'] else eur(x['eur'], 2)} |"
                     + (f" {x['compte'] or '–'}{' (' + x['raison'] + ')' if x['raison'] else ''} |" if not regle else "")
                     + f" {x['configuration'] or '–'} | {x['bougies']} |")
        return T

    L.append("## Détail des plans de Claude")
    L.extend(table(C, False))
    L.append("")
    if len(G):
        L.append("## Détail des plans des règles")
        L.extend(table(G, True))
        L.append("")
    L.append("Un plan « ouvert » affiche son résultat provisoire à la dernière clôture. Résultats hors financement "
             "quand celui de Kraken n'est pas encore publié pour la période.")
    L.append("")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Papier : {len(C)} plans de Claude ({n} comptés clos), {len(G)} plans de règles, {len(anomalies)} anomalie(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
