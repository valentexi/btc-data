# -*- coding: utf-8 -*-
"""
Règles mécaniques partagées par le relevé (`collecte.py`) et le mode papier (`papier.py`).

- Biais mécanique du jour : les cinq familles du backtest, avec la dernière valeur connue de chaque donnée.
- Supports majeurs : définition fixe de la méthode (moyennes 200 semaines et 200 jours, plus bas des 90 jours
  précédents), avec leur état en clôture journalière. Elle tranche la règle du long de retournement.
- Règles inscrites d'office en mode papier (S4 et L7 du backtest), mêmes paramètres que dans le backtest.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest import DUREE, FAMILLES, OBJECTIF, STOP, charger, familles_mecaniques

# Règles mécaniques suivies en papier à partir de la clôture du 15 nov. 2026 (première entrée possible le 16).
DEBUT_REGLES = "2026-11-15"
REGLES_PAPIER = [
    {"id": "S4", "nom": "Short quand le biais mécanique est ≤ −5", "sens": -1, "seuil": -5},
    {"id": "L7", "nom": "Long quand le biais mécanique est ≥ +5", "sens": 1, "seuil": 5},
]
STOP_PCT, OBJ_PCT, DUREE_H = STOP, OBJECTIF, DUREE * 24

# Supports majeurs : fenêtres et seuils fixés le 15 nov. 2026, non optimisés.
FENETRE_BAS = 90          # plus bas des 90 jours précédents (bas journaliers, jusqu'à la veille)
PRES_SUPPORT = 0.03       # long de retournement : dernière clôture au plus 3 % au-dessus d'un support qui tient
POSE_SUPPORT = 0.02       # short : prix « posé » sur un support = au plus 2 % au-dessus
CASSE_RECENT = 10         # un support cassé depuis moins de 10 jours sans reprise exclut le long
PEUR_EXTREME = 20


def jour_vivant(J: pd.DataFrame) -> pd.DataFrame:
    """Chaque donnée prend sa dernière valeur connue (3 jours au plus), comme on le ferait en direct.

    Le backtest, lui, n'utilise que la valeur du jour même : les deux ne diffèrent que sur les derniers jours.
    """
    K = J.copy()
    for col in ("peur", "mvrv", "plateformes", "fin_jour"):
        if col in K.columns:
            K[col] = K[col].ffill(limit=3)
    return K


def biais_du_jour(J: pd.DataFrame | None = None, jours: int = 7) -> dict | None:
    """Biais mécanique de la dernière clôture et des précédentes, avec la note de chaque famille."""
    if J is None:
        d = charger()
        if d is None:
            return None
        J = d[0]
    K = jour_vivant(J)
    F = familles_mecaniques(K)
    F["biais"] = F[FAMILLES].sum(axis=1, min_count=len(FAMILLES))
    F.loc[F[FAMILLES].isna().any(axis=1), "biais"] = np.nan
    F["date"] = K["date"].to_numpy()
    F["cloture"] = K["cloture"].to_numpy()
    dernier = F.iloc[-1]
    return {
        "date": str(dernier["date"]),
        "biais": float(dernier["biais"]),
        "familles": {f: float(dernier[f]) for f in FAMILLES},
        "manquantes": [f for f in FAMILLES if dernier[f] != dernier[f]],
        "historique": F.iloc[-jours:][["date", "biais", *FAMILLES]].reset_index(drop=True),
        "table": F,
    }


def signal(regle: dict, biais: float) -> bool:
    if biais != biais:
        return False
    return biais <= regle["seuil"] if regle["sens"] == -1 else biais >= regle["seuil"]


def _etat(c: np.ndarray, niv: np.ndarray, dates: np.ndarray) -> dict:
    """État d'un niveau en clôture journalière : tient, cassé (depuis quand), repris (quand)."""
    k = len(c) - 1
    if niv[k] != niv[k]:
        return {"etat": "indisponible", "depuis": None, "jours": None}
    dessous = c < niv
    if dessous[k]:
        j = k
        while j > 0 and dessous[j - 1] and niv[j - 1] == niv[j - 1]:
            j -= 1
        return {"etat": "cassé", "depuis": str(dates[j]), "jours": k - j + 1}
    j = k
    while j > 0 and not dessous[j - 1] and niv[j - 1] == niv[j - 1]:
        j -= 1
    if j > 0 and k - j + 1 <= CASSE_RECENT:
        return {"etat": "repris", "depuis": str(dates[j]), "jours": k - j + 1}
    return {"etat": "tient", "depuis": None, "jours": None}


def supports_majeurs(J: pd.DataFrame) -> dict:
    """Niveaux, écarts et états des supports majeurs ; décision mécanique sur le long de retournement."""
    c = J["cloture"].to_numpy(float)
    dates = J["date"].to_numpy()
    cs = J["cloture"].astype(float)
    mm200s = sum(cs.shift(7 * i) for i in range(200)) / 200      # une clôture par semaine, comme le relevé
    niveaux = [
        ("Moyenne 200 semaines", mm200s.to_numpy(float)),
        ("Moyenne 200 jours", J["mm200"].to_numpy(float)),
        (f"Plus bas des {FENETRE_BAS} jours précédents", J["bas"].rolling(FENETRE_BAS).min().shift(1).to_numpy(float)),
    ]
    lignes = []
    for nom, niv in niveaux:
        e = _etat(c, niv, dates)
        ecart = c[-1] / niv[-1] - 1 if niv[-1] == niv[-1] else float("nan")
        lignes.append({"nom": nom, "niveau": float(niv[-1]), "ecart": float(ecart), **e})
    connus = [x for x in lignes if x["etat"] != "indisponible"]
    proche = [x for x in connus if x["etat"] in ("tient", "repris") and 0 <= x["ecart"] <= PRES_SUPPORT]
    casse_recent = [x for x in connus if x["etat"] == "cassé" and x["jours"] <= CASSE_RECENT]
    pose = [x for x in connus if x["etat"] in ("tient", "repris") and 0 <= x["ecart"] <= POSE_SUPPORT]
    if casse_recent:
        long_retour = (False, "support majeur cassé depuis moins de "
                       f"{CASSE_RECENT} jours sans reprise en clôture ({casse_recent[0]['nom'].lower()})")
    elif proche:
        long_retour = (True, f"clôture au-dessus d'un support qui tient, à moins de {PRES_SUPPORT * 100:.0f} % "
                       f"({proche[0]['nom'].lower()})")
    else:
        long_retour = (False, f"aucun support majeur qui tient à moins de {PRES_SUPPORT * 100:.0f} % sous le prix")
    return {"lignes": lignes, "long_retournement": long_retour, "pose": pose, "date": str(dates[-1]),
            "cloture": float(c[-1])}


def condition_short(supports: dict, financement_8h_pct: float | None, peur: float | None) -> tuple[bool | None, str]:
    """Condition éliminatoire du short : prix posé sur un support majeur, financement négatif et peur extrême."""
    if financement_8h_pct is None or peur is None:
        return None, "donnée manquante"
    pose = bool(supports["pose"])
    neg = financement_8h_pct < 0
    peur_x = peur <= PEUR_EXTREME
    detail = (f"posé sur un support majeur : {'oui' if pose else 'non'} ; financement en direct négatif : "
              f"{'oui' if neg else 'non'} ; peur extrême (≤ {PEUR_EXTREME}) : {'oui' if peur_x else 'non'}")
    return pose and neg and peur_x, detail
