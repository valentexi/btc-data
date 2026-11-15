# -*- coding: utf-8 -*-
"""Fonctions communes : chemins, lecture/écriture des CSV, mise en forme des nombres."""
from __future__ import annotations

import os

import pandas as pd

RACINE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("BTC_DATA_DIR", os.path.join(RACINE, "data"))
RAPPORT = os.environ.get("BTC_RAPPORT_DIR", os.path.join(RACINE, "rapport"))

ESP = " "  # espace insécable, pour que les nombres ne soient pas coupés


def chemin(nom: str) -> str:
    return os.path.join(DATA, nom)


def lire(nom: str) -> pd.DataFrame | None:
    """Lit un CSV du dossier data. Renvoie None s'il est absent ou vide."""
    p = chemin(nom)
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p, dtype={"date": str})
    return df if len(df) else None


def fusionner(nom: str, nouveau: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les nouvelles lignes au fichier existant.

    Une date déjà présente est mise à jour, jamais supprimée : le fichier ne fait
    que grandir, même si une source ne renvoie qu'un historique court.
    """
    nouveau = nouveau.copy()
    nouveau["date"] = nouveau["date"].astype(str)
    nouveau = nouveau.drop_duplicates(subset="date", keep="last").set_index("date")
    ancien = lire(nom)
    if ancien is not None:
        ancien = ancien.drop_duplicates(subset="date", keep="last").set_index("date")
        colonnes = list(nouveau.columns) + [c for c in ancien.columns if c not in nouveau.columns]
        tout = nouveau.combine_first(ancien)[colonnes]
    else:
        tout = nouveau
    tout = tout.sort_index().reset_index()
    os.makedirs(os.path.dirname(chemin(nom)), exist_ok=True)
    tout.to_csv(chemin(nom), index=False, float_format="%.10g")
    return tout


def lire_h4() -> pd.DataFrame | None:
    """Toutes les bougies de 4 heures (un fichier par mois dans data/h4). Colonne date = début UTC."""
    dossier = chemin("h4")
    if not os.path.isdir(dossier):
        return None
    morceaux = [pd.read_csv(os.path.join(dossier, f), dtype={"date": str})
                for f in sorted(os.listdir(dossier)) if f.endswith(".csv")]
    morceaux = [m for m in morceaux if len(m)]
    if not morceaux:
        return None
    df = pd.concat(morceaux, ignore_index=True).drop_duplicates(subset="date", keep="last")
    return df.sort_values("date").reset_index(drop=True)


def ecrire_h4(df: pd.DataFrame) -> int:
    """Enregistre les bougies de 4 heures, un fichier par mois (seuls les mois modifiés changent)."""
    df = df.copy()
    df["date"] = df["date"].astype(str)
    n = 0
    for mois, bloc in df.groupby(df["date"].str[:7]):
        n += len(fusionner(f"h4/btc_h4_{mois}.csv", bloc))
    return n


def nb(x: float, d: int = 0) -> str:
    """68500.4 -> '68 500' ; 1.1081 avec d=4 -> '1,1081'."""
    return f"{x:,.{d}f}".replace(",", ESP).replace(".", ",")


def eur(x: float, d: int = 0) -> str:
    return nb(x, d) + ESP + "€"


def usd(x: float, d: int = 0) -> str:
    return nb(x, d) + ESP + "$"


def prix(x_usd: float, fx: float) -> str:
    """Prix du Bitcoin : euros d'abord, dollars entre parenthèses."""
    return f"{eur(x_usd / fx)} ({usd(x_usd)})"


def pct(x: float, d: int = 1) -> str:
    """0.0312 -> '+3,1 %'."""
    return f"{x * 100:+.{d}f}".replace(".", ",") + ESP + "%"


def pct_brut(x: float, d: int = 2) -> str:
    """Valeur déjà exprimée en pourcentage : 0.0102 -> '0,01 %' (signe seulement si négatif)."""
    return f"{x:.{d}f}".replace(".", ",") + ESP + "%"
