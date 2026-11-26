# Mode papier (26/11/2026 02:47 UTC)

Suivi automatique, sans argent réel. Déclencheurs, stops et objectifs suivis heure par heure ; clôtures jugées sur les bougies de 4 heures ; entrée théorique à l'ouverture de la bougie qui suit le déclencheur. Résultats nets de frais et de glissement. Dernière bougie connue : 2026-11-26 01:00 UTC.

Bougies utilisées : les plans créés depuis le 2026-11-15 à 19:00 UTC sont rejoués sur le **contrat perpétuel Kraken PF_XBTUSD** (le prix auquel un ordre serait exécuté) ; les plans antérieurs restent sur le prix au comptant de Coinbase, comme à leur enregistrement. Dernière bougie du contrat Kraken : 2026-11-26 01:00 UTC.

## Plans de Claude
- Enregistrés : 17. Entrés : 4 (clos 4, ouverts 0). En attente : 0. Expirés ou annulés sans entrée : 13. Abandonnés (condition non remplie) : 0.
- **Comptés au critère** (enregistrés avant leur entrée, jamais modifiés) : 3 clos, 0 % gagnants, -0,72 R par trade, -2,16 R au total (-5,40 €). Ouverts et comptés : 0.
- Hors critère : P001 (enregistré après l'entrée).
- Tous les plans entrés, pour mémoire : 4 clos, 0 % gagnants, -0,79 R par trade, -3,16 R au total (-7,90 €).

## Critère de passage en réel
Bilans à dates fixes : à 30, 60, 100 plans comptés clos, puis tous les 50. Un bilan est favorable si l'intervalle à 95 % (tirage par épisodes) est entièrement au-dessus de 0 R, donc meilleur que « ne rien faire », avec au moins 10 épisodes de marché distincts. Entre deux bilans, aucune conclusion.

- Prochain bilan à 30 plans comptés clos (3 pour l'instant).
- **Verdict : CRITÈRE NON ATTEINT, rester en mode papier.**

## Règles mécaniques inscrites d'office (sans jugement)
S4 : short quand le biais mécanique est ≤ −5. L7 : long quand il est ≥ +5. Plan identique au backtest (stop 4 %, objectif 6,5 %, 7 jours au plus), entrée à 0 h UTC, à l'ouverture qui suit la clôture du signal (même si le robot passe en retard, 24 h au plus), une position à la fois par règle. Elles servent d'étalon : le jugement de Claude n'a d'intérêt que s'il fait mieux qu'elles.

- S4 : 1 clos, 100 % gagnants, +1,52 R par trade, +1,52 R au total (3,81 €) ; ouverts 0.
- L7 : aucun plan clos ; ouverts 0.
- Comparaison, plans clos : Claude (comptés) -0,72 R sur 3 ; règles +1,52 R sur 1. Pour mémoire, long systématique à chaque plan de Claude -0,53 R, short systématique +0,68 R.

## Par configuration et par jour d'entrée
Plans clos seulement ; pour Claude, plans comptés au critère. À lire au premier bilan (30 plans) : avec quelques plans par ligne, ces moyennes ne veulent rien dire.

| Groupe | Plans clos | R moyen | Total | Ouverts |
|---|---|---|---|---|
| Claude, tous les plans comptés | 3 | -0,72 R | -2,16 R | 0 |
| Claude · D-S : short sur rebond raté | 3 | -0,72 R | -2,16 R | 0 |
| Claude · entrées en semaine | 1 | -1,00 R | -1,00 R | 0 |
| Claude · entrées le week-end | 2 | -0,58 R | -1,16 R | 0 |
| Règle S4 | 1 | +1,52 R | +1,52 R | 0 |
| Règle S4 · entrées en semaine | 1 | +1,52 R | +1,52 R | 0 |
| Règle L7 | 0 | n.d. | n.d. | 0 |

## Scénarios à 7 jours : justesse des probabilités
Chaque analyse donne trois probabilités (baissier, neutre, haussier) séparées par deux seuils de prix. À l'échéance, le robot regarde où le prix a fini. Une prévision ne compte que si elle a été enregistrée dans les 6 heures suivant l'analyse.

- Enregistrées : 9. Résolues : 4 (comptées : 4). En cours : 5.
- Probabilité moyenne donnée à l'issue qui s'est réalisée : 38 % (au hasard : 33 %).
- Score de Brier moyen : 0,59 (0 = parfait ; 0,67 = trois issues à 33 % ; au-dessus de 0,67 : pire que de ne rien savoir).
- L'issue jugée la plus probable s'est réalisée dans 50 % des cas.

| Issue | Probabilité moyenne annoncée | Fréquence observée |
|---|---|---|
| baissier | 38 % | 100 % |
| neutre | 39 % | 0 % |
| haussier | 22 % | 0 % |

- Prévisions indépendantes (qui ne se recouvrent pas) parmi les comptées résolues : 1. **Aucune conclusion avant 20 prévisions comptées résolues.**

| Prévision | Créée (UTC) | Échéance (UTC) | Seuils | Baissier / neutre / haussier | État | Prix | Issue | Probabilité donnée | Comptée |
|---|---|---|---|---|---|---|---|---|---|
| SC028 | 2026-11-25 17:23 | 2026-12-02 17:23 | 50 297 € (55 000 $) et 56 699 € (62 000 $) | 33 % / 47 % / 20 % | en cours | 55 220 € (60 384 $) | neutre (provisoire) |  | oui |
| SC026 | 2026-11-24 10:16 | 2026-12-01 10:16 | 51 212 € (56 000 $) et 58 528 € (64 000 $) | 30 % / 50 % / 20 % | en cours | 55 220 € (60 384 $) | neutre (provisoire) |  | oui |
| SC025 | 2026-11-23 15:20 | 2026-11-30 15:20 | 53 955 € (59 000 $) et 61 271 € (67 000 $) | 28 % / 50 % / 22 % | en cours | 55 220 € (60 384 $) | neutre (provisoire) |  | oui |
| SC023 | 2026-11-21 16:49 | 2026-11-28 16:49 | 51 669 € (56 500 $) et 58 070 € (63 500 $) | 30 % / 47 % / 23 % | en cours | 55 220 € (60 384 $) | neutre (provisoire) |  | oui |
| SC019 | 2026-11-19 15:08 | 2026-11-26 15:08 | 55 784 € (61 000 $) et 60 357 € (66 000 $) | 30 % / 45 % / 25 % | en cours | 55 220 € (60 384 $) | baissier (provisoire) |  | oui |
| SC018 | 2026-11-18 14:51 | 2026-11-25 14:51 | 55 784 € (61 000 $) et 60 357 € (66 000 $) | 33 % / 45 % / 22 % | résolu | 53 546 € (58 553 $) | baissier | 33 % | oui |
| SC017 | 2026-11-17 14:28 | 2026-11-24 14:28 | 56 699 € (62 000 $) et 61 271 € (67 000 $) | 33 % / 42 % / 25 % | résolu | 55 187 € (60 347 $) | baissier | 33 % | oui |
| SC016 | 2026-11-16 12:39 | 2026-11-23 12:39 | 56 699 € (62 000 $) et 60 814 € (66 500 $) | 42 % / 35 % / 23 % | résolu | 56 102 € (61 347 $) | baissier | 42 % | oui |
| SC015 | 2026-11-15 16:00 | 2026-11-22 16:00 | 56 699 € (62 000 $) et 62 048 € (67 850 $) | 45 % / 35 % / 20 % | résolu | 55 601 € (60 799 $) | baissier | 45 % | oui |

## Intégrité du registre
Aucune modification détectée sur les 29 lignes enregistrées (`papier/registre.csv`).

## Annulations
- P009 : demandée pour 2026-11-18T14:51, effective le 2026-11-18 18:49 UTC (Gain/risque au dernier objectif 1,49 frais compris (sous 1,5) : remplacé par P010 (objectif 2 à 61 800 $)).
- P010 : demandée pour 2026-11-19T15:08, effective le 2026-11-19 15:09 UTC (Condition éliminatoire du short ACTIVE au relevé du 19 nov. 13:57 UTC (financement Kraken négatif, prix à 1,7 % du plus bas des 90 jours, peur extrême) : remplacé par P011, mêmes niveaux, sous condition de financement positif ou nul).

## Détail des plans de Claude
| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Compté | Configuration | Bougies |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P018 | 2026-11-25T17:23 | 2026-11-25 17:24 | short | clos | 2026-11-25 18:00 à 54 504 € (59 600 $) | 2026-11-26 00:00 | stop | -1,00 R | -2,50 € | oui | D-S | contrat Kraken |
| P017 | 2026-11-24T10:16 | 2026-11-24 10:16 | short | expiré sans entrée |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P016 | 2026-11-23T15:20 | 2026-11-23 15:21 | short | expiré sans entrée |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P015 | 2026-11-21T16:49 | 2026-11-21 17:27 | short | clos | 2026-11-22 12:00 à 55 762 € (60 976 $) | 2026-11-23 13:00 | stop | -1,00 R | -2,50 € | oui | D-S | contrat Kraken |
| P014 | 2026-11-21T06:50 | 2026-11-21 06:51 | short | expiré sans entrée |  |  |  | n.d. |  | – | C-S | contrat Kraken |
| P013 | 2026-11-21T06:50 | 2026-11-21 06:51 | short | annulé : entrée trop éloignée du prix prévu |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P011 | 2026-11-19T15:08 | 2026-11-19 15:09 | short | expiré sans entrée |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P010 | 2026-11-18T14:51 | 2026-11-18 18:49 | short | annulé avant entrée |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P009 | 2026-11-18T14:51 | 2026-11-18 14:52 | short | annulé avant entrée |  |  |  | n.d. |  | – | D-S | contrat Kraken |
| P008 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | expiré sans entrée |  |  |  | n.d. |  | – | C-S | Coinbase |
| P007 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | clos | 2026-11-15 04:00 à 59 244 € (64 783 $) | 2026-11-17 12:00 | durée | -0,16 R | -0,40 € | oui | D-S | Coinbase |
| P006 | 2026-11-14T19:20 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P005 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P004 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P003 | 2026-11-14T14:25 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P002 | 2026-11-13T18:00 | 2026-11-15 00:44 | long | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P001 | 2026-11-13T11:15 | 2026-11-15 00:44 | long | clos | 2026-11-13 15:00 à 62 643 € (68 500 $) | 2026-11-14 14:00 | stop | -1,00 R | -2,50 € | non (enregistré après l'entrée) | – | Coinbase |

## Détail des plans des règles
| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Configuration | Bougies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S4-2026-11-15 | 2026-11-16T00:00 | 2026-11-16 06:16 | short | clos | 2026-11-16 00:00 à 59 729 € (65 314 $) | 2026-11-20 15:00 | objectif | +1,52 R | 3,81 € | S4 | contrat Kraken |

Un plan « ouvert » affiche son résultat provisoire à la dernière clôture. Résultats hors financement quand celui de Kraken n'est pas encore publié pour la période.
