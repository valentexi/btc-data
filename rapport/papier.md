# Mode papier (15/11/2026 13:02 UTC)

Suivi automatique, sans argent réel. Déclencheurs, stops et objectifs suivis heure par heure ; clôtures jugées sur les bougies de 4 heures ; entrée théorique à l'ouverture de la bougie qui suit le déclencheur. Résultats nets de frais et de glissement. Dernière bougie connue : 2026-11-15 12:00 UTC.

## Plans de Claude
- Enregistrés : 8. Entrés : 2 (clos 1, ouverts 1). En attente : 1. Expirés ou annulés sans entrée : 5. Abandonnés (condition non remplie) : 0.
- **Comptés au critère** (enregistrés avant leur entrée, jamais modifiés) : aucun plan clos. Ouverts et comptés : 1.
- Hors critère : P001 (enregistré après l'entrée).
- Tous les plans entrés, pour mémoire : 1 clos, 0 % gagnants, -1,00 R par trade, -1,00 R au total (-2,50 €).

## Critère de passage en réel
Bilans à dates fixes : à 30, 60, 100 plans comptés clos, puis tous les 50. Un bilan est favorable si l'intervalle à 95 % (tirage par épisodes) est entièrement au-dessus de 0 R, donc meilleur que « ne rien faire », avec au moins 10 épisodes de marché distincts. Entre deux bilans, aucune conclusion.

- Prochain bilan à 30 plans comptés clos (0 pour l'instant).
- **Verdict : CRITÈRE NON ATTEINT, rester en mode papier.**

## Règles mécaniques inscrites d'office (sans jugement)
S4 : short quand le biais mécanique est ≤ −5. L7 : long quand il est ≥ +5. Plan identique au backtest (stop 4 %, objectif 6,5 %, 7 jours au plus), entrée à l'ouverture de l'heure qui suit l'inscription, une position à la fois par règle. Elles servent d'étalon : le jugement de Claude n'a d'intérêt que s'il fait mieux qu'elles.

- S4 : aucun plan clos ; ouverts 0.
- L7 : aucun plan clos ; ouverts 0.
- Comparaison, plans clos : Claude (comptés) n.d. sur 0 ; règles n.d. sur 0. Pour mémoire, long systématique à chaque plan de Claude -1,00 R, short systématique +0,26 R.

## Intégrité du registre
Aucune modification détectée sur les 8 lignes enregistrées (`papier/registre.csv`).

## Détail des plans de Claude
| Plan | Créé (UTC) | Enregistré (UTC) | Sens | État | Entrée | Sortie | Motif | Résultat | En euros | Compté |
|---|---|---|---|---|---|---|---|---|---|---|
| P008 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | en attente du déclencheur |  |  |  | n.d. |  | – |
| P007 | 2026-11-15T00:08 | 2026-11-15 00:50 | short | ouvert | 2026-11-15 04:00 à 58 617 € (64 783 $) |  | en cours | -0,43 R | -1,07 € | oui |
| P006 | 2026-11-14T19:20 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – |
| P005 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – |
| P004 | 2026-11-14T16:53 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – |
| P003 | 2026-11-14T14:25 | 2026-11-15 00:44 | short | expiré sans entrée |  |  |  | n.d. |  | – |
| P002 | 2026-11-13T18:00 | 2026-11-15 00:44 | long | expiré sans entrée |  |  |  | n.d. |  | – |
| P001 | 2026-11-13T11:15 | 2026-11-15 00:44 | long | clos | 2026-11-13 15:00 à 61 980 € (68 500 $) | 2026-11-14 14:00 | stop | -1,00 R | -2,50 € | non (enregistré après l'entrée) |

Un plan « ouvert » affiche son résultat provisoire à la dernière clôture. Résultats hors financement quand celui de Kraken n'est pas encore publié pour la période.
