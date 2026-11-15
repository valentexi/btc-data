# -*- coding: utf-8 -*-
"""
Simulation d'un trade sur des bougies de 4 heures.

Conventions (toutes défavorables au trader quand il y a un doute) :
- si le stop et un objectif sont touchés dans la même bougie, on compte le stop ;
- une ouverture au-delà du stop sort au prix d'ouverture (perte supérieure à 1 R) ;
- après le premier objectif, le stop passe au prix d'entrée à partir de la bougie suivante ;
- le financement n'est jamais inventé : s'il manque sur la période, le résultat
  « avec financement » vaut NaN et seul le résultat « hors financement » est donné.

Résultat en R : 1 R = perte quand le stop saute, frais et glissement compris.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FRAIS = 0.0005        # 0,05 % par ordre au marché (barème Kraken, premier palier)
GLISSEMENT = 0.0010   # 0,10 % sur toute sortie par stop
FRAIS_STRESS = 0.0010       # conditions dégradées : frais doublés
GLISSEMENT_STRESS = 0.0030  # et glissement triplé


def barres(h4: pd.DataFrame, fin_jour: dict[str, float] | None = None, pas_h: int = 4) -> dict:
    """Prépare les tableaux pour des bougies de `pas_h` heures (4 par défaut, 1 pour le suivi papier).

    fin_jour : part payée par les longs chaque jour (fraction), par date."""
    t = pd.to_datetime(h4["date"], utc=True)
    B = {
        "t": t.dt.tz_convert(None).to_numpy().astype("datetime64[s]"),   # début de chaque bougie, UTC
        "date": h4["date"].to_numpy(),
        "jour": h4["date"].str[:10].to_numpy(),
        "o": h4["ouverture"].to_numpy(float),
        "h": h4["haut"].to_numpy(float),
        "l": h4["bas"].to_numpy(float),
        "c": h4["cloture"].to_numpy(float),
        "n": len(h4),
        "pas_h": pas_h,
    }
    fin = np.full(len(h4), np.nan)
    if fin_jour:
        fin = np.array([fin_jour.get(j, np.nan) for j in B["jour"]], float) / (24.0 / pas_h)
    B["fin"] = fin
    return B


def simuler(B: dict, i: int, sens: int, stop: float, obj1: float | None, obj2: float, i_max: int,
            entree: float | None = None) -> dict | None:
    """Un trade. Entrée à l'ouverture de la bougie i, ou au prix `entree` (ordre limite exécuté dans la bougie i).

    obj1 = None : sortie unique à obj2. Sinon : moitié à obj1, stop ramené à l'entrée, reste à obj2.
    Renvoie None si le stop est déjà dépassé au moment d'entrer.
    """
    o, h, l, c, fin = B["o"], B["h"], B["l"], B["c"], B["fin"]
    E = float(o[i]) if entree is None else float(entree)
    d = sens * (E - stop) / E
    if not d > 0:
        return None
    i_max = min(i_max, B["n"] - 1)
    if i > i_max:
        return None
    reste, brut, part_stop = 1.0, 0.0, 0.0
    fin_cum, fin_ok = 0.0, True
    stop_c, moitie_faite = stop, obj1 is None
    motif, j = "durée", i
    for j in range(i, i_max + 1):
        if np.isnan(fin[j]):
            fin_ok = False
        else:
            fin_cum += sens * fin[j] * reste
        if j > i and sens * (o[j] - stop_c) <= 0:           # ouverture au-delà du stop
            brut += reste * sens * (o[j] / E - 1)
            part_stop += reste
            motif = "stop" if stop_c == stop else "stop à l'entrée"
            reste = 0.0
            break
        touche_stop = l[j] <= stop_c if sens == 1 else h[j] >= stop_c
        if touche_stop:                                       # prioritaire dans la bougie
            brut += reste * sens * (stop_c / E - 1)
            part_stop += reste
            motif = "stop" if stop_c == stop else "stop à l'entrée"
            reste = 0.0
            break
        if j == i and entree is not None:
            continue          # ordre limite exécuté en cours de bougie : ses plus hauts et plus bas ont pu précéder l'entrée
        remonter = False
        if not moitie_faite and (h[j] >= obj1 if sens == 1 else l[j] <= obj1):
            brut += 0.5 * sens * (obj1 / E - 1)
            reste, moitie_faite, remonter = 0.5, True, True
        if moitie_faite and (h[j] >= obj2 if sens == 1 else l[j] <= obj2):
            brut += reste * sens * (obj2 / E - 1)
            reste, motif = 0.0, "objectif"
            break
        if remonter:
            stop_c = E
    ouvert = reste > 0
    if ouvert:                                                # sortie à la clôture de la dernière bougie
        brut += reste * sens * (c[j] / E - 1)
        motif = "durée" if (obj1 is None or reste == 1.0) else "objectif 1 puis durée"
    risque = d + 2 * FRAIS + GLISSEMENT
    net = brut - 2 * FRAIS - GLISSEMENT * part_stop
    net_stress = brut - 2 * FRAIS_STRESS - GLISSEMENT_STRESS * part_stop
    return {
        "i": i, "j": j, "sens": sens, "entree": E, "stop": stop, "d": d,
        "t_entree": B["date"][i], "t_sortie": B["date"][j],
        "brut": brut, "net": net, "R": net / risque, "R_stress": net_stress / risque,
        "R_fin": (net - fin_cum) / risque if fin_ok else np.nan,
        "fin": fin_cum if fin_ok else np.nan,
        "motif": motif, "obj1_touche": bool(moitie_faite and obj1 is not None),
    }


def plan_structure(E: float, sens: int, stop: float, d_min: float = 0.015, d_max: float = 0.06):
    """Borne la distance du stop : trop proche -> ramené à d_min ; trop loin -> pas de trade (None)."""
    d = sens * (E - stop) / E
    if d > d_max:
        return None
    if d < d_min:
        d = d_min
        stop = E * (1 - sens * d)
    return stop, d
