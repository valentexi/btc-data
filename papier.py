#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mode papier : suivi automatique des plans proposés par les analyses, sans argent réel.

Chaque plan est une ligne de papier/plans.csv, écrite AVANT que le marché ne tranche.
Ce script rejoue ensuite les bougies de 4 heures : déclencheur atteint ou non, prix
d'entrée théorique, sortie, résultat net de frais. Il compare les plans à deux
références mécaniques (un long et un short systématiques au moment de chaque plan).

Colonnes de plans.csv (heures en UTC, prix en dollars) :
  id, cree_utc, source, sens (long|short), declencheur, zone_bas, zone_haut, niveau,
  entree, stop, obj1, obj2, expire_utc, sortie_utc, risque_eur, biais, note

Déclencheurs :
  immediat         entrée à l'ouverture de la première bougie après la création
  limite           ordre limite au prix `entree`
  cloture_4h       une bougie de 4 h clôture au-delà de `niveau` (au-dessus pour un long, en dessous pour un short)
  cloture_jour     même chose pour la clôture journalière (0 h UTC)
  zone_cloture_4h  le prix entre dans la zone [zone_bas, zone_haut], puis une bougie de 4 h clôture au-delà de `niveau`
Après un déclencheur en clôture, l'entrée théorique se fait à l'ouverture de la bougie suivante.
obj1 vide : sortie unique à obj2. Sinon : moitié à obj1, stop ramené à l'entrée, reste à obj2.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

from outils import RACINE, RAPPORT, eur, lire, lire_h4, nb, prix
from simulation import barres, simuler
from stats import episodes, ic_episodes

PLANS = os.environ.get("BTC_PLANS", os.path.join(RACINE, "papier", "plans.csv"))
RESULTATS = os.path.join(os.path.dirname(PLANS), "resultats.csv")
SEUIL_TRADES = 30          # critère de passage en réel : nombre minimal de trades papier clos
REF_STOP, REF_OBJ, REF_BARRES = 0.04, 0.065, 42


def _t(x) -> pd.Timestamp | None:
    if x is None or (isinstance(x, float) and x != x) or str(x).strip() == "":
        return None
    return pd.Timestamp(str(x).strip().replace("Z", ""), tz="UTC")


def _f(x) -> float | None:
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def evaluer(plan: dict, B: dict) -> dict:
    """Rejoue un plan sur les bougies de 4 heures. Aucune information postérieure n'est utilisée pour décider."""
    sens = 1 if str(plan["sens"]).strip().lower() == "long" else -1
    cree, expire, sortie = _t(plan["cree_utc"]), _t(plan.get("expire_utc")), _t(plan.get("sortie_utc"))
    decl = str(plan["declencheur"]).strip()
    stop, obj1, obj2 = _f(plan.get("stop")), _f(plan.get("obj1")), _f(plan.get("obj2"))
    niveau, entree_prevue = _f(plan.get("niveau")), _f(plan.get("entree"))
    zb, zh = _f(plan.get("zone_bas")), _f(plan.get("zone_haut"))
    res = {"id": plan["id"], "sens": "long" if sens == 1 else "short", "etat": "", "t_entree": "", "prix_entree": np.nan,
           "t_sortie": "", "motif": "", "R": np.nan, "R_fin": np.nan, "eur": np.nan, "detail": ""}
    if stop is None or obj2 is None or cree is None:
        res["etat"] = "plan incomplet"
        return res
    debut = B["t"]                                   # début de chaque bougie
    fin = debut + np.timedelta64(4, "h")
    cree64 = np.datetime64(cree.tz_convert(None))
    exp64 = np.datetime64(expire.tz_convert(None)) if expire is not None else np.datetime64("2262-01-01")
    apres = np.flatnonzero(debut >= cree64)          # bougies entièrement postérieures à la création
    closes = np.flatnonzero((fin > cree64) & (fin <= exp64))   # clôtures connues après la création, avant expiration
    derniere = B["n"] - 1
    perime = fin[derniere] >= exp64                  # les données couvrent-elles l'expiration ?

    def au_dela(k):                                  # clôture du bon côté du niveau
        return B["c"][k] > niveau if sens == 1 else B["c"][k] < niveau

    i, prix_limite = None, None
    if decl == "immediat":
        if len(apres):
            i = int(apres[0])
    elif decl == "limite" and entree_prevue is not None:
        for k in apres:
            if debut[k] > exp64:
                break
            touche = B["l"][k] <= entree_prevue if sens == 1 else B["h"][k] >= entree_prevue
            if touche:
                mieux = B["o"][k] < entree_prevue if sens == 1 else B["o"][k] > entree_prevue
                i, prix_limite = int(k), (float(B["o"][k]) if mieux else entree_prevue)
                break
    elif decl in ("cloture_4h", "cloture_jour") and niveau is not None:
        for k in closes:
            if decl == "cloture_jour" and not str(B["date"][k]).endswith("20:00"):
                continue
            if au_dela(k):
                i = int(k) + 1
                break
    elif decl == "zone_cloture_4h" and niveau is not None and zb is not None and zh is not None:
        dans_zone = False
        for k in closes:
            if debut[k] >= cree64 and (B["h"][k] >= zb if sens == -1 else B["l"][k] <= zh):
                dans_zone = True
            if dans_zone and au_dela(k):
                i = int(k) + 1
                break
    else:
        res["etat"] = "déclencheur inconnu ou incomplet"
        return res

    if i is None:
        res["etat"] = "expiré sans entrée" if perime else "en attente du déclencheur"
        return res
    if i > derniere:
        res["etat"] = "déclenché, entrée à la prochaine bougie"
        return res
    i_max = derniere
    if sortie is not None:
        avant = np.flatnonzero(fin <= np.datetime64(sortie.tz_convert(None)))
        i_max = int(avant[-1]) if len(avant) else i
        i_max = max(i_max, i)
    t = simuler(B, i, sens, stop, obj1, obj2, i_max, entree=prix_limite)
    if t is None:
        res["etat"] = "annulé : stop déjà dépassé à l'entrée"
        res["t_entree"] = str(B["date"][i])
        return res
    ouvert = "durée" in t["motif"] and (sortie is None or fin[derniere] < np.datetime64(sortie.tz_convert(None)))
    risque = _f(plan.get("risque_eur")) or 0.0
    res.update({"etat": "ouvert" if ouvert else "clos", "t_entree": t["t_entree"], "prix_entree": t["entree"],
                "t_sortie": "" if ouvert else t["t_sortie"], "motif": "en cours" if ouvert else t["motif"],
                "R": t["R"], "R_fin": t["R_fin"], "eur": t["R"] * risque,
                "detail": "" if entree_prevue is None else f"écart à l'entrée prévue {(t['entree'] / entree_prevue - 1) * 100:+.2f} %"})
    return res


def reference(plan: dict, B: dict, sens: int) -> float:
    """Long ou short systématique au moment où le plan est créé : stop 4 %, objectif 6,5 %, 7 jours."""
    cree = _t(plan["cree_utc"])
    apres = np.flatnonzero(B["t"] >= np.datetime64(cree.tz_convert(None)))
    if not len(apres):
        return float("nan")
    i = int(apres[0])
    E = B["o"][i]
    i_max = i + REF_BARRES - 1
    t = simuler(B, i, sens, E * (1 - sens * REF_STOP), None, E * (1 + sens * REF_OBJ), i_max)
    if t is None or (i_max > B["n"] - 1 and "durée" in t["motif"]):
        return float("nan")                           # pas encore dénoué
    return t["R"]


def r_(x):
    return "n.d." if x != x else f"{x:+.2f}".replace(".", ",") + " R"


def main() -> int:
    os.makedirs(RAPPORT, exist_ok=True)
    sortie = os.path.join(RAPPORT, "papier.md")
    h4, p = lire_h4(), lire("btc_jour.csv")
    if not os.path.exists(PLANS) or h4 is None:
        with open(sortie, "w", encoding="utf-8") as f:
            f.write("# Mode papier\n\nAucun plan enregistré ou bougies de 4 heures indisponibles.\n")
        return 0
    plans = pd.read_csv(PLANS, dtype=str).fillna("")
    fk = lire("financement_kraken.csv")
    fin = {} if fk is None else {d: v / 100.0 for d, v in zip(fk["date"], fk["cumul_jour_pct"])}
    B = barres(h4.sort_values("date").reset_index(drop=True), fin)
    fx = float(p["eurusd"].dropna().iloc[-1]) if p is not None and "eurusd" in p.columns else float("nan")

    lignes = []
    for _, pl in plans.iterrows():
        pl = pl.to_dict()
        try:
            r = evaluer(pl, B)
            r["ref_long"], r["ref_short"] = reference(pl, B, 1), reference(pl, B, -1)
        except Exception as e:  # noqa: BLE001 - une ligne mal saisie ne doit pas bloquer les autres
            r = {"id": pl.get("id", "?"), "sens": pl.get("sens", ""), "etat": f"ligne illisible : {e}", "t_entree": "",
                 "prix_entree": np.nan, "t_sortie": "", "motif": "", "R": np.nan, "R_fin": np.nan, "eur": np.nan,
                 "detail": "", "ref_long": np.nan, "ref_short": np.nan}
        r.update({"cree_utc": pl.get("cree_utc", ""), "source": pl.get("source", ""), "note": pl.get("note", "")})
        lignes.append(r)
    R = pd.DataFrame(lignes)
    R.to_csv(RESULTATS, index=False, float_format="%.5g")

    clos = R[R["etat"] == "clos"]
    n = len(clos)
    L = [f"# Mode papier ({dt.datetime.now(dt.timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC)", ""]
    L.append("Suivi automatique des plans des analyses, sans argent réel. Prix d'entrée théorique : ouverture de la "
             "bougie de 4 heures qui suit le déclencheur. Résultats nets de frais et de glissement. "
             f"Dernière bougie connue : {B['date'][-1]} UTC.")
    L.append("")
    L.append("## Bilan")
    L.append(f"- Plans enregistrés : {len(R)}. Entrés : {int(R['etat'].isin(['clos', 'ouvert']).sum())}. "
             f"Clos : {n}. Ouverts : {int((R['etat'] == 'ouvert').sum())}. "
             f"En attente : {int(R['etat'].str.startswith('en attente').sum())}. "
             f"Expirés sans entrée : {int((R['etat'] == 'expiré sans entrée').sum())}.")
    if n:
        r = clos["R"].to_numpy(float)
        lo, hi = ic_episodes(r, episodes(clos["t_entree"])) if n >= 5 else (float("nan"), float("nan"))
        L.append(f"- Plans clos : {nb((r > 0).mean() * 100)} % gagnants, {r_(r.mean())} par trade, {r_(r.sum())} au total, "
                 f"soit {eur(float(clos['eur'].sum()), 2)}." + (f" Intervalle à 95 % : {r_(lo)} à {r_(hi)}." if n >= 5 else ""))
    rl, rs = R["ref_long"].dropna(), R["ref_short"].dropna()
    L.append(f"- Référence « long systématique à chaque plan » : {r_(rl.mean()) if len(rl) else 'n.d.'} sur {len(rl)} dénoués. "
             f"Référence « short systématique » : {r_(rs.mean()) if len(rs) else 'n.d.'} sur {len(rs)}.")
    L.append("- Référence « ne rien faire » : 0 R.")
    L.append("")
    L.append("## Critère de passage en réel")
    ok_n = n >= SEUIL_TRADES
    ok_ic = bool(n >= SEUIL_TRADES and ic_episodes(clos["R"].to_numpy(float), episodes(clos["t_entree"]))[0] > 0)
    ok_ref = bool(n and len(rl) and len(rs) and clos["R"].mean() > max(rl.mean(), rs.mean(), 0))
    L.append(f"- Au moins {SEUIL_TRADES} plans clos : {'oui' if ok_n else f'non ({n} sur {SEUIL_TRADES})'}.")
    L.append(f"- Résultat moyen positif avec un intervalle à 95 % entièrement positif : {'oui' if ok_ic else 'non'}.")
    L.append(f"- Mieux que les références : {'oui' if ok_ref else 'non'}.")
    L.append(f"- **Verdict : {'CRITÈRE ATTEINT' if (ok_n and ok_ic and ok_ref) else 'CRITÈRE NON ATTEINT, rester en mode papier'}.**")
    L.append("")
    L.append("## Plans")
    L.append("| Plan | Créé (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Réf. long | Réf. short |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for _, x in R.iloc[::-1].iterrows():
        entree = "" if x["prix_entree"] != x["prix_entree"] else f"{x['t_entree']} à {prix(x['prix_entree'], fx)}"
        L.append(f"| {x['id']} | {x['cree_utc']} | {x['sens']} | {x['etat']} | {entree} | {x['t_sortie']} | {x['motif']} | "
                 f"{r_(x['R'])} | {'' if x['eur'] != x['eur'] else eur(x['eur'], 2)} | {r_(x['ref_long'])} | {r_(x['ref_short'])} |")
    L.append("")
    L.append("Les résultats sont hors financement quand celui de Kraken n'est pas encore publié pour la période. "
             "Un plan « ouvert » affiche son résultat provisoire à la dernière clôture.")
    L.append("")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Papier : {len(R)} plans, {n} clos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
