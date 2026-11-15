#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alertes du mode papier, par des « issues » GitHub (notification gratuite sur le téléphone via l'appli GitHub).

- Plan de Claude déclenché ou entré : une issue est ouverte, avec les ordres à vérifier.
- Plan clos : commentaire sur la même issue, qui est fermée.
- Plan déclenché puis abandonné (condition de financement, entrée trop éloignée) : issue d'information.
- Registre modifié après coup : issue d'alerte.
Les plans des règles mécaniques ne déclenchent pas d'alerte (étalon de mesure, rien à exécuter).

Lit papier/resultats.csv et papier/anomalies.csv (écrits par papier.py), tient papier/alertes.csv.
Hors de GitHub Actions (ordinateur, session de travail, tests) : simulation, rien n'est envoyé ni enregistré.
"""
from __future__ import annotations

import os
import sys
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from outils import eur, lire, nb, prix
from papier import DOSSIER, RESULTATS, _f, _t, maintenant

ALERTES = os.path.join(DOSSIER, "alertes.csv")
ANOMALIES = os.path.join(DOSSIER, "anomalies.csv")
DEPOT = os.environ.get("GITHUB_REPOSITORY", "valentexi/btc-data")
DESTINATAIRE = "@valentexi"
FRAIS_GLISSEMENT = 0.002
ANCIENNETE_MAX_H = 48          # un événement plus ancien à sa première détection est enregistré sans alerte
PARIS = ZoneInfo("Europe/Paris")
RAPPORT_URL = f"https://github.com/{DEPOT}/blob/main/rapport/papier.md"


def paris(t: pd.Timestamp | None) -> str:
    if t is None:
        return ""
    t = t.tz_convert(PARIS)
    return f"{t.day:02d}/{t.month:02d} à {t.hour} h" + (f" {t.minute:02d}" if t.minute else "")


class GitHub:
    """Appels minimaux à l'API REST de GitHub."""

    def __init__(self, jeton: str):
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {jeton}", "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28"})
        self.base = f"https://api.github.com/repos/{DEPOT}"

    def ouvrir(self, titre: str, corps: str) -> int:
        r = self.s.post(f"{self.base}/issues", json={"title": titre, "body": corps}, timeout=30)
        r.raise_for_status()
        return int(r.json()["number"])

    def commenter_et_fermer(self, numero: int, corps: str) -> int:
        self.s.post(f"{self.base}/issues/{numero}/comments", json={"body": corps}, timeout=30).raise_for_status()
        self.s.patch(f"{self.base}/issues/{numero}", json={"state": "closed"}, timeout=30).raise_for_status()
        return numero


class Simulation:
    def __init__(self):
        self.envois = []

    def ouvrir(self, titre, corps):
        self.envois.append(("ouvrir", titre, corps))
        return 0

    def commenter_et_fermer(self, numero, corps):
        self.envois.append(("commenter", numero, corps))
        return numero


def _taille(entree: float, stop: float, risque: float, fx: float) -> tuple[float, float]:
    """Taille en euros pour perdre `risque` au stop (frais et glissement compris) et quantité en BTC."""
    d = abs(entree - stop) / entree + FRAIS_GLISSEMENT
    taille = risque / d
    return taille, taille * fx / entree


def corps_entree(x: dict, fx: float, dernier_prix: float | None, quand: pd.Timestamp) -> tuple[str, str]:
    ident, sens = x["id"], x["sens"]
    t_decl = _t(x.get("t_declenche"))
    t_ent = _t(x.get("t_entree"))
    stop, obj1, obj2 = _f(x.get("stop")), _f(x.get("obj1")), _f(x.get("obj2"))
    prevue = _f(x.get("entree_prevue"))
    E = _f(x.get("prix_entree")) or prevue or dernier_prix
    if x["etat"] == "déclenché, entrée à la prochaine bougie":
        titre = f"BTC · {ident} déclenché : {sens}"
        tete = (f"{DESTINATAIRE} Plan **{ident}** ({sens}) **déclenché** par la clôture du {paris(t_decl)} (Paris). "
                "Entrée théorique à l'ouverture de la bougie qui commence.")
    else:
        retard = (quand - t_ent).total_seconds() / 3600 if t_ent is not None else 0
        titre = f"BTC · {ident} : entrée papier ({sens})"
        tete = (f"{DESTINATAIRE} Plan **{ident}** ({sens}) **entré en papier** le {paris(t_ent)} (Paris) à "
                f"{prix(E, fx)}." + (f" Il y a {nb(retard, 0)} h : trop tard pour suivre en réel." if retard > 2 else ""))
    L = [tete, ""]
    if dernier_prix:
        L.append(f"- Dernier prix connu (clôture horaire) : {prix(dernier_prix, fx)}")
    if prevue:
        L.append(f"- Entrée prévue au plan : {prix(prevue, fx)}")
    if stop and E:
        objectifs = " puis ".join(prix(o, fx) for o in (obj1, obj2) if o)
        taille, qte = _taille(prevue or E, stop, _f(x.get("risque_eur")) or 2.5, fx)
        L.append(f"- Stop : {prix(stop, fx)} ; objectifs : {objectifs}")
        L.append(f"- Risque {eur(_f(x.get('risque_eur')) or 2.5, 2)} : taille ≈ {eur(taille)}, soit "
                 f"{nb(qte, 4)} BTC ; levier x2, marge ≈ {eur(taille / 2)}, **marge isolée**")
    if x.get("detail"):
        L.append(f"- {x['detail']}")
    L += ["", "**Mode papier** : le critère de passage en réel n'est pas atteint. Si tu décides quand même de suivre "
          "en réel :",
          "1. Lis le prix sur Kraken (PF_XBTUSD). S'il est plus de 0,5 % moins bon que l'entrée prévue, on n'entre pas.",
          "2. Marge isolée, levier x2, stop en « réduction seulement » posé tout de suite.",
          "3. Dis-le-moi, pour séparer le réel du papier.", "", f"Suivi : {RAPPORT_URL}"]
    return titre, "\n".join(L)


def corps_sortie(x: dict, fx: float) -> tuple[str, str]:
    R, e = _f(x.get("R")), _f(x.get("eur"))
    res = f"{R:+.2f} R".replace(".", ",") + (f" ({eur(e, 2)})" if e is not None else "")
    titre = f"BTC · {x['id']} clos : {x['motif']}, {res}"
    corps = (f"{DESTINATAIRE} Plan **{x['id']}** ({x['sens']}) **clos** le {paris(_t(x.get('t_sortie')))} (Paris) : "
             f"{x['motif']}, {res}. Entrée papier à {prix(_f(x.get('prix_entree')), fx)}."
             f"\n\nCompté au critère : {x.get('compte') or 'non'}"
             + (f" ({x['raison']})" if x.get("raison") else "") + f".\n\nSuivi : {RAPPORT_URL}")
    return titre, corps


def main(client=None) -> int:
    if not os.path.exists(RESULTATS):
        print("Alertes : pas de résultats.")
        return 0
    quand = maintenant()
    R = pd.read_csv(RESULTATS, dtype=str).fillna("")
    R = R[R["registre"] == "claude"]
    deja = pd.read_csv(ALERTES, dtype=str).fillna("") if os.path.exists(ALERTES) else \
        pd.DataFrame(columns=["cle", "envoye_utc", "issue", "mode"])
    faits = {r["cle"]: r for _, r in deja.iterrows()}
    jeton = os.environ.get("GITHUB_TOKEN", "")
    # Envoi réel seulement depuis GitHub Actions : une session de travail qui a un jeton n'envoie rien.
    simule = client is None and not (jeton and os.environ.get("GITHUB_ACTIONS") == "true")
    if client is None:
        client = Simulation() if simule else GitHub(jeton)
    p, h1 = lire("btc_jour.csv"), lire("h1_recent.csv")
    fx = float(p["eurusd"].dropna().iloc[-1]) if p is not None and "eurusd" in p.columns else 1.0
    dernier = float(h1.sort_values("date")["cloture"].iloc[-1]) if h1 is not None and len(h1) else None
    nouveaux = []

    def noter(cle, issue, mode):
        nouveaux.append({"cle": cle, "envoye_utc": quand.strftime("%Y-%m-%dT%H:%M:%SZ"), "issue": issue, "mode": mode})
        faits[cle] = nouveaux[-1]

    def ancien(t):
        return t is not None and (quand - t).total_seconds() / 3600 > ANCIENNETE_MAX_H

    for x in R.to_dict("records"):
        etat, ident = x["etat"], x["id"]
        entre = etat in ("ouvert", "clos") or etat == "déclenché, entrée à la prochaine bougie"
        if entre and f"{ident}:entree" not in faits:
            t = _t(x.get("t_entree")) or _t(x.get("t_declenche"))
            if ancien(t):
                noter(f"{ident}:entree", "", "ancien, sans alerte")
            else:
                try:
                    noter(f"{ident}:entree", str(client.ouvrir(*corps_entree(x, fx, dernier, quand))), "envoyé")
                except Exception as e:  # noqa: BLE001 - nouvel essai au prochain lancement
                    print(f"Alerte {ident} (entrée) : échec {e}")
        if etat == "clos" and f"{ident}:sortie" not in faits and f"{ident}:entree" in faits:
            t = _t(x.get("t_sortie"))
            if ancien(t):
                noter(f"{ident}:sortie", "", "ancien, sans alerte")
                continue
            try:
                titre, corps = corps_sortie(x, fx)
                num = str(faits[f"{ident}:entree"].get("issue", ""))
                if num and num != "0":
                    client.commenter_et_fermer(int(num), corps)
                else:
                    num = str(client.ouvrir(titre, corps))
                noter(f"{ident}:sortie", num, "envoyé")
            except Exception as e:  # noqa: BLE001
                print(f"Alerte {ident} (sortie) : échec {e}")
        if (etat.startswith("abandonné") or etat.startswith("annulé : entrée trop")) and f"{ident}:abandon" not in faits:
            t = _t(x.get("t_declenche")) or _t(x.get("t_entree"))
            if ancien(t):
                noter(f"{ident}:abandon", "", "ancien, sans alerte")
                continue
            try:
                titre = f"BTC · {ident} déclenché mais abandonné"
                corps = (f"{DESTINATAIRE} Plan **{ident}** ({x['sens']}) : le déclencheur a été atteint le "
                         f"{paris(_t(x.get('t_declenche')))} (Paris), mais le plan est **{etat}**"
                         + (f" ({x['detail']})" if x.get("detail") else "") + ". Pas d'entrée.\n\nSuivi : " + RAPPORT_URL)
                noter(f"{ident}:abandon", str(client.ouvrir(titre, corps)), "envoyé")
            except Exception as e:  # noqa: BLE001
                print(f"Alerte {ident} (abandon) : échec {e}")

    if os.path.exists(ANOMALIES):
        for a in pd.read_csv(ANOMALIES, dtype=str).fillna("").to_dict("records"):
            cle = f"anomalie:{a['cle']}:{a['empreinte']}"
            if cle in faits:
                continue
            try:
                titre = f"BTC · registre papier : ligne {a['cle']} {a['nature']}"
                corps = (f"{DESTINATAIRE} La ligne **{a['cle']}**, enregistrée le {a['enregistree']}, a été "
                         f"**{a['nature'].split(' après')[0]}** après coup. Le plan sort du critère de passage en réel. "
                         f"Pour corriger un plan : une annulation, puis un nouveau plan.\n\nSuivi : {RAPPORT_URL}")
                noter(cle, str(client.ouvrir(titre, corps)), "envoyé")
            except Exception as e:  # noqa: BLE001
                print(f"Alerte anomalie {a['cle']} : échec {e}")

    envoyes = [n for n in nouveaux if n["mode"] == "envoyé"]
    if simule:
        for e in client.envois:
            print(f"[simulation] {e[0]} : {e[1]}")
        print(f"Alertes : {len(envoyes)} en simulation (hors de GitHub Actions), rien d'enregistré.")
        return 0
    if nouveaux:
        pd.concat([deja, pd.DataFrame(nouveaux)], ignore_index=True).to_csv(ALERTES, index=False)
    print(f"Alertes : {len(envoyes)} envoyée(s), {len(nouveaux) - len(envoyes)} enregistrée(s) sans envoi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
