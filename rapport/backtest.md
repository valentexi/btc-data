# Backtest BTC (14/11/2026 19:17 UTC)

## En bref
- **Long de retournement en peur extrême sous la moyenne 200 jours** : 205 trades, 37 % gagnants, -0,12 R par trade en moyenne, soit -0,58 € pour 5 € risqués. Verdict : **non concluant**.
- **Short sur rebond sous la moyenne 200 jours** : 75 trades, 36 % gagnants, -0,11 R par trade en moyenne, soit -0,56 € pour 5 € risqués. Verdict : **non concluant**.
- Référence, long chaque lundi avec le même plan : -0,06 R par trade sur 515 trades. Une règle n'a d'intérêt que si elle fait nettement mieux.

## Données
- Prix quotidien du 2017-01-01 au 2026-11-13, soit 3 604 jours.
- Fear & Greed disponible sur 3 204 jours, financement Kraken sur 367 jours.
- Plan type : stop 4,0 %, objectif 6,5 %, 7 jours au plus.
- Coûts : 0,05 % par ordre, 0,10 % de glissement au stop, financement réel quand il est connu, sinon 0,01 % par 8 h.
- 1 R = la perte prévue au stop. Avec 5 € risqués par trade, +0,20 R vaut 1 €.

## Ce que fait le prix après chaque situation
Variation moyenne du prix dans les jours qui suivent, sans stop ni objectif. Les jours d'un même épisode se chevauchent : le nombre d'épisodes compte plus que le nombre de jours.

| Situation | Jours | Épisodes | 3 j | 7 j | Médiane 7 j | Hausse à 7 j | 14 j | 30 j |
|---|---|---|---|---|---|---|---|---|
| Tous les jours (référence) | 3405 | 1 | +0,5 % | +1,1 % | +0,4 % | 53 % | +2,3 % | +5,2 % |
| Prix au-dessus de la moyenne 200 jours | 1903 | 16 | +0,7 % | +1,7 % | +0,5 % | 53 % | +3,4 % | +7,5 % |
| Prix sous la moyenne 200 jours | 1502 | 16 | +0,2 % | +0,4 % | +0,3 % | 52 % | +1,0 % | +2,4 % |
| Peur extrême (≤ 20) | 422 | 40 | +0,4 % | +1,3 % | +1,3 % | 57 % | +2,6 % | +4,8 % |
| Peur extrême, sous la moyenne 200 jours | 397 | 37 | +0,5 % | +1,4 % | +1,6 % | 57 % | +2,7 % | +5,2 % |
| Peur extrême, au-dessus de la moyenne 200 jours | 25 | 7 | -0,6 % | -0,0 % | -0,7 % | 44 % | +1,0 % | -2,4 % |
| Avidité extrême (≥ 80) | 165 | 15 | +2,7 % | +5,1 % | +3,9 % | 61 % | +9,3 % | +19,8 % |
| Purge : −10 % ou pire en 7 jours | 297 | 67 | +0,1 % | +0,3 % | +0,6 % | 53 % | +1,0 % | +3,1 % |
| Purge, sous la moyenne 200 jours | 187 | 42 | +0,1 % | +0,5 % | +0,8 % | 53 % | +0,3 % | +2,0 % |
| Rebond : +8 % ou plus en 7 jours, sous la moyenne 200 jours | 142 | 36 | -0,2 % | +0,1 % | +0,0 % | 50 % | +0,3 % | +1,7 % |
| Financement négatif (moyenne 3 jours) | 95 | 7 | +0,7 % | +1,8 % | +1,9 % | 60 % | +2,4 % | +1,8 % |

## Règles avec stop et objectif
| Règle | Trades | Gagnants | R moyen | R médian | R total | 1re moitié | 2e moitié | Pire série | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| L0 Référence : long chaque lundi | 515 | 41 % | -0,06 R | -1,00 R | -29,19 R | -0,05 R | -0,07 R | 12 pertes | non concluant |
| L1 Long en peur extrême (Fear & Greed ≤ 20) | 224 | 35 % | -0,15 R | -1,01 R | -32,94 R | -0,11 R | -0,18 R | 11 pertes | non concluant |
| L2 Long en peur extrême, prix sous la moyenne 200 jours | 205 | 37 % | -0,12 R | -1,01 R | -23,73 R | -0,05 R | -0,18 R | 11 pertes | non concluant |
| L3 Long en peur extrême, prix au-dessus de la moyenne 200 jours | 19 | 21 % | -0,48 R | -1,01 R | -9,20 R | -0,46 R | -0,51 R | 7 pertes | échantillon insuffisant |
| L4 Long après une purge (−10 % ou pire en 7 jours) | 228 | 33 % | -0,19 R | -1,01 R | -42,65 R | -0,21 R | -0,17 R | 11 pertes | négatif |
| L5 Long après une purge, prix sous la moyenne 200 jours | 128 | 32 % | -0,22 R | -1,01 R | -27,55 R | -0,23 R | -0,20 R | 10 pertes | négatif |
| L6 Long quand le financement est négatif (moyenne 3 jours) | 32 | 44 % | +0,11 R | -0,36 R | +3,63 R | +0,13 R | +0,10 R | 5 pertes | non concluant |
| S0 Référence : short chaque lundi | 515 | 41 % | -0,04 R | -0,96 R | -21,62 R | -0,02 R | -0,07 R | 12 pertes | non concluant |
| S1 Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours | 75 | 36 % | -0,11 R | -0,96 R | -8,36 R | +0,01 R | -0,23 R | 8 pertes | non concluant |
| S2 Short en avidité extrême (Fear & Greed ≥ 80) | 87 | 33 % | -0,18 R | -0,98 R | -15,53 R | -0,38 R | +0,01 R | 7 pertes | non concluant |
| S3 Short sous la moyenne 200 jours, chaque lundi | 217 | 40 % | -0,08 R | -0,96 R | -17,78 R | -0,09 R | -0,07 R | 9 pertes | non concluant |

Lecture : « positif » ou « négatif » seulement si l'écart à zéro est net (au moins 30 trades et un résultat stable). Les colonnes « moitié » comparent le début et la fin de l'historique : un signe qui change indique une règle fragile.

## Robustesse
R moyen par trade quand on change le stop et la durée (objectif = 1,6 fois le stop). Ce n'est pas une recherche du meilleur réglage : si le signe change d'une case à l'autre, le résultat ne tient pas. Nombre de trades entre parenthèses.

**L2 Long en peur extrême, prix sous la moyenne 200 jours**

| Stop | 3 jours | 7 jours | 14 jours |
|---|---|---|---|
| 3 % | -0,12 R (279) | -0,13 R (252) | -0,14 R (250) |
| 4 % | -0,10 R (249) | -0,12 R (205) | -0,11 R (198) |
| 6 % | -0,05 R (214) | -0,05 R (154) | -0,04 R (138) |

**S1 Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours**

| Stop | 3 jours | 7 jours | 14 jours |
|---|---|---|---|
| 3 % | -0,09 R (99) | -0,09 R (92) | -0,11 R (92) |
| 4 % | -0,02 R (85) | -0,11 R (75) | -0,10 R (75) |
| 6 % | -0,00 R (78) | +0,04 R (61) | +0,05 R (61) |

## Suivi de tendance (sans stop)
| Stratégie | Rendement annuel | Pire baisse | Temps en position | Allers-retours |
|---|---|---|---|---|
| Détenir du Bitcoin | +44,1 % | -83,8 % | 100 % | 0 |
| Long seulement au-dessus de la moyenne 200 jours | +33,1 % | -71,5 % | 56 % | 36 |
| Short seulement sous la moyenne 200 jours | -16,1 % | -89,5 % | 44 % | 35 |

Période : du 2017-07-19 au 2026-11-13. Sans levier.

## Derniers trades simulés : L2 Long en peur extrême, prix sous la moyenne 200 jours
| Entrée | Prix d'entrée | Sortie | Motif | Résultat |
|---|---|---|---|---|
| 2026-06-04 | 55 017 € (64 040 $) | 2026-06-04 | stop | -1,00 R |
| 2026-06-05 | 54 816 € (63 806 $) | 2026-06-05 | stop | -1,00 R |
| 2026-06-06 | 52 433 € (61 032 $) | 2026-06-12 | durée | +0,95 R |
| 2026-06-13 | 54 931 € (63 538 $) | 2026-06-19 | durée | -0,05 R |
| 2026-06-20 | 55 355 € (63 475 $) | 2026-06-24 | stop | -1,00 R |
| 2026-06-25 | 53 768 € (60 983 $) | 2026-06-25 | stop | -1,00 R |
| 2026-06-26 | 52 367 € (59 704 $) | 2026-07-02 | durée | +0,68 R |
| 2026-07-03 | 53 707 € (61 484 $) | 2026-07-09 | durée | +0,59 R |

## Derniers trades simulés : S1 Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours
| Entrée | Prix d'entrée | Sortie | Motif | Résultat |
|---|---|---|---|---|
| 2023-01-13 | 17 429 € (18 848 $) | 2023-01-13 | stop | -0,99 R |
| 2024-08-13 | 54 303 € (59 359 $) | 2024-08-14 | stop | -0,99 R |
| 2024-09-14 | 54 637 € (60 543 $) | 2024-09-19 | stop | -0,96 R |
| 2024-09-20 | 56 382 € (62 956 $) | 2024-09-26 | stop | -0,95 R |
| 2025-04-16 | 73 644 € (83 623 $) | 2025-04-21 | stop | -0,96 R |
| 2026-03-16 | 63 452 € (72 830 $) | 2026-03-17 | stop | -1,00 R |
| 2026-04-11 | 62 333 € (72 998 $) | 2026-04-14 | stop | -1,01 R |
| 2026-07-08 | 55 526 € (63 322 $) | 2026-07-14 | durée | -0,62 R |

## Limites
- Données quotidiennes : l'ordre exact entre stop et objectif dans une même journée est inconnu (on compte le stop).
- Le Fear & Greed n'existe que depuis 2018 et le financement Kraken sur environ un an : peu d'épisodes indépendants.
- Les trades d'un même épisode ne sont pas indépendants : la netteté des verdicts est surestimée.
- Le passé couvre surtout des cycles haussiers. Une règle « long » y est flattée.
- Les flux des ETF et les liquidations ne sont pas testés (pas de source gratuite).
- Un backtest positif ne garantit rien : il sert à écarter les idées qui n'ont jamais marché.
