# Mode papier (17/11/2026 09:08 UTC)

Suivi automatique, sans argent réel. Déclencheurs, stops et objectifs suivis heure par heure ; clôtures jugées sur les bougies de 4 heures ; entrée théorique à l'ouverture de la bougie qui suit le déclencheur. Résultats nets de frais et de glissement. Dernière bougie connue : 2026-11-17 08:00 UTC.

Bougies utilisées : les plans créés depuis le 2026-11-15 à 19:00 UTC sont rejoués sur le **contrat perpétuel Kraken PF_XBTUSD** (le prix auquel un ordre serait exécuté) ; les plans antérieurs restent sur le prix au comptant de Coinbase, comme à leur enregistrement. Dernière bougie du contrat Kraken : 2026-11-17 08:00 UTC.

## Plans de Claude
- Enregistrés : 8. Entrés : 2 (clos 1, ouverts 1). En attente : 0. Expirés ou annulés sans entrée : 6. Abandonnés (condition non remplie) : 0.
- **Comptés au critère** (enregistrés avant leur entrée, jamais modifiés) : aucun plan clos. Ouverts et comptés : 1.
- Hors critère : P001 (enregistré après l'entrée).
- Tous les plans entrés, pour mémoire : 1 clos, 0 % gagnants, -1,00 R par trade, -1,00 R au total (-2,50 €).

## Critère de passage en réel
Bilans à dates fixes : à 30, 60, 100 plans comptés clos, puis tous les 50. Un bilan est favorable si l'intervalle à 95 % (tirage par épisodes) est entièrement au-dessus de 0 R, donc meilleur que « ne rien faire », avec au moins 10 épisodes de marché distincts. Entre deux bilans, aucune conclusion.

- Prochain bilan à 30 plans comptés clos (0 pour l'instant).
- **Verdict : CRITÈRE NON ATTEINT, rester en mode papier.**

## Règles mécaniques inscrites d'office (sans jugement)
S4 : short quand le biais mécanique est ≤ −5. L7 : long quand il est ≥ +5. Plan identique au backtest (stop 4 %, objectif 6,5 %, 7 jours au plus), entrée à 0 h UTC, à l'ouverture qui suit la clôture du signal (même si le robot passe en retard, 24 h au plus), une position à la fois par règle. Elles servent d'étalon : le jugement de Claude n'a d'intérêt que s'il fait mieux qu'elles.

- S4 : aucun plan clos ; ouverts 1.
- L7 : aucun plan clos ; ouverts 0.
- Comparaison, plans clos : Claude (comptés) n.d. sur 0 ; règles n.d. sur 0. Pour mémoire, long systématique à chaque plan de Claude -1,00 R, short systématique +0,26 R.

## Par configuration et par jour d'entrée
Plans clos seulement ; pour Claude, plans comptés au critère. À lire au premier bilan (30 plans) : avec quelques plans par ligne, ces moyennes ne veulent rien dire.

| Groupe | Plans clos | R moyen | Total | Ouverts |
|---|---|---|---|---|
| Claude, tous les plans comptés | 0 | n.d. | n.d. | 1 |
| Claude · D-S : short sur rebond raté | 0 | n.d. | n.d. | 1 |
| Claude · entrées en semaine | 0 | n.d. | n.d. | 0 |
| Claude · entrées le week-end | 0 | n.d. | n.d. | 1 |
| Règle S4 | 0 | n.d. | n.d. | 1 |
| Règle S4 · entrées en semaine | 0 | n.d. | n.d. | 1 |
| Règle L7 | 0 | n.d. | n.d. | 0 |

## Scénarios à 7 jours : justesse des probabilités
Chaque analyse donne trois probabilités (baissier, neutre, haussier) séparées par deux seuils de prix. À l'échéance, le robot regarde où le prix a fini. Une prévision ne compte que si elle a été enregistrée dans les 6 heures suivant l'analyse.

- Enregistrées : 2. Résolues : 0 (comptées : 0). En cours : 2.
- Prévisions indépendantes (qui ne se recouvrent pas) parmi les comptées résolues : 0. **Aucune conclusion avant 20 prévisions comptées résolues.**

| Prévision | Créée (UTC) | Échéance (UTC) | Seuils | Baissier / neutre / haussier | État | Prix | Issue | Probabilité donnée | Comptée |
|---|---|---|---|---|---|---|---|---|---|
| SC016 | 2026-11-16 12:39 | 2026-11-23 12:39 | 56 292 € (62 000 $) et 60 378 € (66 500 $) | 42 % / 35 % / 23 % | en cours | 58 721 € (64 675 $) | neutre (provisoire) |  | oui |
| SC015 | 2026-11-15 16:00 | 2026-11-22 16:00 | 56 292 € (62 000 $) et 61 603 € (67 850 $) | 45 % / 35 % / 20 % | en cours | 58 721 € (64 675 $) | neutre (provisoire) |  | oui |

## Intégrité du registre
Aucune modification détectée sur les 11 lignes enregistrées (`papier/registre.csv`).

## Détail des plans de Claude
| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Compté | Configuration | Bougies |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P008 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | expiré sans entrée |  |  |  | n.d. |  | – | C-S | Coinbase |
| P007 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | ouvert | 2026-11-15 04:00 à 58 819 € (64 783 $) |  | en cours | +0,26 R | 0,64 € | oui | D-S | Coinbase |
| P006 | 2026-11-14T19:20 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P005 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P004 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P003 | 2026-11-14T14:25 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P002 | 2026-11-13T18:00 | 2026-11-15 00:44 | long | expiré sans entrée |  |  |  | n.d. |  | – | – | Coinbase |
| P001 | 2026-11-13T11:15 | 2026-11-15 00:44 | long | clos | 2026-11-13 15:00 à 62 194 € (68 500 $) | 2026-11-14 14:00 | stop | -1,00 R | -2,50 € | non (enregistré après l'entrée) | – | Coinbase |

## Détail des plans des règles
| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Configuration | Bougies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S4-2026-11-15 | 2026-11-16T00:00 | 2026-11-16 06:16 | short | ouvert | 2026-11-16 00:00 à 59 301 € (65 314 $) |  | en cours | +0,35 R | 0,88 € | S4 | contrat Kraken |

Un plan « ouvert » affiche son résultat provisoire à la dernière clôture. Résultats hors financement quand celui de Kraken n'est pas encore publié pour la période.
