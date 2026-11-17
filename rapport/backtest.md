# Backtest BTC, version 2 (17/11/2026 13:54 UTC)

## En bref
- 31 règles ou configurations testées, dont 26 avec assez de trades pour conclure (au moins 30 trades et 10 épisodes).
- **Aucune configuration n'a d'avantage statistique démontré après frais.**
- 2 nettement perdante(s) : B-S-mm200 Short sur rejet sous la moyenne 200 jours ; D-L Long sur retour au-dessus d'une résistance cassée.
- Avec 26 tests, le hasard seul ferait ressortir environ 0,7 faux « positif ». Un résultat isolé ne prouve rien.
- Hors échantillon (règle choisie chaque année sur le passé, puis suivie) : 55 trades, -0,12 R par trade, intervalle -0,38 R à +0,13 R.
- Biais mécanique (cinq familles sur sept) et variation du prix à 7 jours : aucun lien mesurable (corrélation de rang 0,04, intervalle -0,03 à 0,12).
- Le biais complet de la méthode (avec les flux des ETF et les événements) ne peut pas être rejoué sur le passé : seul le mode papier (`rapport/papier.md`) peut le juger.

## Comment lire
- Données : bougies de 4 heures du 2017-01-01 au 2026-11-17 (21 640 bougies).
- 1 R = la perte prévue quand le stop saute, frais (0,05 % par ordre) et glissement (0,10 % au stop) compris. −0,10 R par trade : on perd 10 % de la mise risquée à chaque trade.
- Épisodes : les trades séparés de moins de 10 jours comptent comme un seul épisode de marché (30 jours au plus par épisode). L'intervalle à 95 % est calculé en tirant au sort des épisodes entiers (bootstrap par blocs).
- Référence : le même plan, avec des entrées toutes les 20 heures sans aucun signal. Une règle doit faire mieux pour avoir un intérêt.
- Avec financement réel : résultat sur les seuls trades dont le financement est connu (Kraken depuis un an, Deribit depuis 2019), comparé au même échantillon sans financement. Aucun financement n'est supposé quand il manque.
- Moitiés : avant et après le 2021-12-10. Coûts dégradés : frais doublés, glissement triplé.
- Verdicts : « candidat » exige un intervalle entièrement positif, deux moitiés positives, mieux que la référence et un résultat encore positif avec des coûts dégradés.

## Règles journalières
Stop 4 %, objectif 6,5 %, 7 jours au plus, sortie unique.

| Règle | Trades | Épisodes | Gagnants | R moyen | Intervalle à 95 % | Référence | Avec financement réel | 1re moitié | 2e moitié | Coûts dégradés | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L0 Référence : long chaque lundi | 514 | 103 | 41 % | +0,01 R | -0,08 R à +0,11 R | +0,02 R | -0,04 R sur 392 (contre -0,02 R sans) | +0,03 R | -0,01 R | -0,04 R | pas d'avantage démontré |
| L1 Long en peur extrême (Fear & Greed ≤ 20) | 225 | 42 | 36 % | -0,12 R | -0,28 R à +0,04 R | +0,02 R | -0,14 R sur 174 (contre -0,14 R sans) | -0,06 R | -0,20 R | -0,18 R | pas d'avantage démontré |
| L2 Long en peur extrême, sous la moyenne 200 jours | 206 | 39 | 37 % | -0,09 R | -0,26 R à +0,09 R | +0,02 R | -0,11 R sur 156 (contre -0,11 R sans) | +0,01 R | -0,19 R | -0,14 R | pas d'avantage démontré |
| L3 Long en peur extrême, au-dessus de la moyenne 200 jours | 19 | 7 | 21 % | -0,47 R | -0,86 R à -0,19 R | +0,02 R | -0,44 R sur 18 (contre -0,44 R sans) | -0,50 R | -0,37 R | -0,53 R | échantillon insuffisant |
| L4 Long après une purge (−10 % en 7 jours) | 228 | 64 | 34 % | -0,16 R | -0,31 R à +0,02 R | +0,02 R | -0,14 R sur 132 (contre -0,14 R sans) | -0,17 R | -0,15 R | -0,22 R | pas d'avantage démontré |
| L5 Long après une purge, sous la moyenne 200 jours | 128 | 38 | 32 % | -0,20 R | -0,37 R à +0,00 R | +0,02 R | -0,19 R sur 83 (contre -0,19 R sans) | -0,16 R | -0,27 R | -0,26 R | pas d'avantage démontré |
| L6 Long quand le financement est négatif (3 jours) | 273 | 64 | 43 % | +0,03 R | -0,11 R à +0,18 R | +0,02 R | +0,03 R sur 273 (contre +0,03 R sans) | +0,05 R | +0,01 R | -0,02 R | pas d'avantage démontré |
| L7 Long quand le biais mécanique est ≥ +5 | 89 | 37 | 52 % | +0,11 R | -0,11 R à +0,29 R | +0,02 R | +0,08 R sur 86 (contre +0,10 R sans) | +0,21 R | +0,08 R | +0,06 R | pas d'avantage démontré |
| S0 Référence : short chaque lundi | 515 | 103 | 42 % | -0,05 R | -0,15 R à +0,05 R | -0,07 R | -0,04 R sur 393 (contre -0,05 R sans) | -0,09 R | -0,01 R | -0,10 R | pas d'avantage démontré |
| S1 Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours | 75 | 34 | 36 % | -0,13 R | -0,32 R à +0,07 R | -0,07 R | -0,29 R sur 49 (contre -0,29 R sans) | -0,07 R | -0,26 R | -0,19 R | pas d'avantage démontré |
| S2 Short en avidité extrême (Fear & Greed ≥ 80) | 87 | 16 | 33 % | -0,14 R | -0,37 R à +0,20 R | -0,07 R | -0,10 R sur 87 (contre -0,14 R sans) | -0,17 R | -0,02 R | -0,19 R | pas d'avantage démontré |
| S3 Short chaque lundi sous la moyenne 200 jours | 215 | 51 | 42 % | -0,05 R | -0,19 R à +0,08 R | -0,07 R | -0,07 R sur 159 (contre -0,07 R sans) | +0,02 R | -0,10 R | -0,10 R | pas d'avantage démontré |
| S4 Short quand le biais mécanique est ≤ −5 | 48 | 21 | 54 % | +0,21 R | -0,19 R à +0,52 R | -0,07 R | +0,23 R sur 42 (contre +0,23 R sans) | +0,06 R | +0,26 R | +0,17 R | pas d'avantage démontré |

## Configurations de la méthode, en bougies de 4 heures
Entrée à l'ouverture de la bougie qui suit le signal. Stop derrière l'extrême des 3 dernières bougies (entre 1,5 % et 6 % ; au-delà, pas de trade). Moitié de la position sortie à 1,2 R, stop ramené à l'entrée, reste à 2,4 R, 5 jours au plus.

| Règle | Trades | Épisodes | Gagnants | R moyen | Intervalle à 95 % | Référence | Avec financement réel | 1re moitié | 2e moitié | Coûts dégradés | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-L Long sur rejet d'un support (plus bas de 20 jours) | 113 | 53 | 42 % | -0,14 R | -0,33 R à +0,05 R | -0,03 R | -0,16 R sur 91 (contre -0,15 R sans) | -0,18 R | -0,12 R | -0,23 R | pas d'avantage démontré |
| A-L+ Long sur rejet d'un support (plus bas de 20 jours), dans le sens de la moyenne 200 jours | 49 | 27 | 45 % | -0,11 R | -0,40 R à +0,26 R | -0,03 R | -0,10 R sur 48 (contre -0,09 R sans) | -0,13 R | -0,10 R | -0,20 R | pas d'avantage démontré |
| A-S Short sur rejet d'une résistance (plus haut de 20 jours) | 208 | 81 | 45 % | -0,08 R | -0,22 R à +0,07 R | -0,10 R | -0,04 R sur 173 (contre -0,06 R sans) | -0,14 R | -0,02 R | -0,18 R | pas d'avantage démontré |
| A-S+ Short sur rejet d'une résistance (plus haut de 20 jours), dans le sens de la moyenne 200 jours | 59 | 30 | 37 % | -0,17 R | -0,39 R à +0,10 R | -0,10 R | -0,17 R sur 46 (contre -0,18 R sans) | -0,20 R | -0,16 R | -0,28 R | pas d'avantage démontré |
| B-L-mm50 Long sur rebond sur la moyenne 50 jours | 109 | 61 | 47 % | +0,01 R | -0,18 R à +0,21 R | -0,02 R | +0,09 R sur 83 (contre +0,10 R sans) | -0,15 R | +0,12 R | -0,08 R | pas d'avantage démontré |
| B-S-mm50 Short sur rejet sous la moyenne 50 jours | 107 | 61 | 47 % | -0,04 R | -0,25 R à +0,15 R | -0,10 R | -0,05 R sur 83 (contre -0,06 R sans) | -0,11 R | +0,01 R | -0,14 R | pas d'avantage démontré |
| B-L-mm200 Long sur rebond sur la moyenne 200 jours | 28 | 19 | 36 % | -0,24 R | -0,56 R à +0,16 R | -0,03 R | -0,29 R sur 26 (contre -0,28 R sans) | -0,43 R | -0,05 R | -0,33 R | échantillon insuffisant |
| B-S-mm200 Short sur rejet sous la moyenne 200 jours | 35 | 15 | 43 % | -0,27 R | -0,49 R à -0,05 R | -0,10 R | -0,26 R sur 35 (contre -0,27 R sans) | -0,30 R | -0,25 R | -0,38 R | négatif |
| B-L-mm200s Long sur rebond sur la moyenne 200 semaines | 29 | 11 | 52 % | +0,17 R | -0,02 R à +0,36 R | -0,04 R | +0,16 R sur 29 (contre +0,17 R sans) | n.d. | +0,17 R | +0,08 R | échantillon insuffisant |
| B-S-mm200s Short sur rejet sous la moyenne 200 semaines | 24 | 8 | 21 % | -0,48 R | -0,83 R à +0,02 R | -0,10 R | -0,47 R sur 24 (contre -0,48 R sans) | n.d. | -0,48 R | -0,60 R | échantillon insuffisant |
| C-S Short sur cassure d'un support en clôture journalière | 66 | 51 | 39 % | -0,13 R | -0,40 R à +0,12 R | -0,06 R | -0,15 R sur 51 (contre -0,16 R sans) | -0,28 R | -0,04 R | -0,21 R | pas d'avantage démontré |
| C-S+ Short sur cassure d'un support en clôture journalière, dans le sens de la moyenne 200 jours | 43 | 33 | 47 % | -0,03 R | -0,34 R à +0,26 R | -0,06 R | +0,09 R sur 30 (contre +0,09 R sans) | -0,32 R | +0,21 R | -0,10 R | pas d'avantage démontré |
| D-S Short sur rebond raté (retour sous un support cassé) | 44 | 39 | 41 % | -0,15 R | -0,48 R à +0,16 R | -0,09 R | -0,15 R sur 33 (contre -0,16 R sans) | -0,20 R | -0,12 R | -0,25 R | pas d'avantage démontré |
| D-S+ Short sur rebond raté (retour sous un support cassé), dans le sens de la moyenne 200 jours | 28 | 25 | 43 % | -0,10 R | -0,55 R à +0,31 R | -0,09 R | -0,04 R sur 19 (contre -0,04 R sans) | -0,27 R | +0,05 R | -0,19 R | échantillon insuffisant |
| C-L Long sur cassure d'une résistance en clôture journalière | 131 | 74 | 48 % | +0,10 R | -0,11 R à +0,31 R | -0,02 R | +0,00 R sur 101 (contre +0,03 R sans) | +0,15 R | +0,03 R | +0,02 R | pas d'avantage démontré |
| C-L+ Long sur cassure d'une résistance en clôture journalière, dans le sens de la moyenne 200 jours | 83 | 47 | 45 % | +0,04 R | -0,24 R à +0,31 R | -0,02 R | +0,00 R sur 75 (contre +0,04 R sans) | -0,01 R | +0,09 R | -0,04 R | pas d'avantage démontré |
| D-L Long sur retour au-dessus d'une résistance cassée | 97 | 66 | 40 % | -0,21 R | -0,40 R à -0,00 R | -0,03 R | -0,32 R sur 79 (contre -0,30 R sans) | -0,05 R | -0,38 R | -0,30 R | négatif |
| D-L+ Long sur retour au-dessus d'une résistance cassée, dans le sens de la moyenne 200 jours | 63 | 40 | 41 % | -0,24 R | -0,48 R à +0,00 R | -0,03 R | -0,29 R sur 56 (contre -0,27 R sans) | -0,22 R | -0,27 R | -0,33 R | pas d'avantage démontré |

Définitions : support et résistance = plus bas et plus haut des 20 derniers jours ; « rejet » = la bougie touche le niveau (à 0,3 % près) puis clôture du bon côté ; « cassure » = clôture journalière au-delà du niveau ; « rebond raté » = dans les 7 jours après une cassure, retour au contact du niveau puis clôture du mauvais côté.

## Sensibilité à la liquidité (configurations 4 heures)
| Sens | Entrées en semaine | Entrées le week-end |
|---|---|---|
| Long | +0,00 R sur 406 | -0,26 R sur 101 |
| Short | -0,07 R sur 383 | -0,31 R sur 101 |

## Le biais mécanique prédit-il la suite ?
Approximation du biais de la méthode sur cinq familles (structure, positionnement, blockchain, macro, actifs risqués), de −10 à +10, du 2018-02-01 au 2026-11-09. Variation moyenne d'un jour quelconque à 7 jours : +0,8 %.

| Biais | Jours | Épisodes | Variation à 7 jours | Médiane | Hausse | À 14 jours | Écart à la moyenne | Intervalle à 95 % de l'écart |
|---|---|---|---|---|---|---|---|---|
| ≤ −5 (baissier) | 103 | 21 | -2,1 % | -1,0 % | 37 % | -5,9 % | -2,9 % | -6,5 % à +0,9 % |
| −4 à −2 | 669 | 54 | +0,4 % | +0,4 % | 53 % | +1,1 % | -0,4 % | -1,9 % à +0,7 % |
| −1 à +1 (neutre) | 1208 | 74 | +0,9 % | +0,1 % | 51 % | +2,1 % | +0,0 % | -0,7 % à +0,9 % |
| +2 à +4 | 965 | 57 | +1,3 % | +0,4 % | 53 % | +2,4 % | +0,5 % | -0,4 % à +1,4 % |
| ≥ +5 (haussier) | 255 | 32 | +1,2 % | +0,9 % | 56 % | +2,0 % | +0,4 % | -1,0 % à +1,8 % |

Si l'intervalle de l'écart contient zéro, la classe ne se distingue pas d'un jour quelconque. Blocs de 30 jours pour le bootstrap.

## Hors échantillon : choisir sur le passé, appliquer ensuite
| Année suivie | Règle retenue au 1er janvier | R moyen sur le passé | Trades de l'année | R moyen de l'année |
|---|---|---|---|---|
| 2020 | C-L Long sur cassure d'une résistance en clôture journalière | +0,40 R | 24 | +0,07 R |
| 2021 | C-L Long sur cassure d'une résistance en clôture journalière | +0,25 R | 14 | -0,37 R |
| 2022 | C-L Long sur cassure d'une résistance en clôture journalière | +0,15 R | 7 | -0,41 R |
| 2023 | S4 Short quand le biais mécanique est ≤ −5 | +0,28 R | 4 | -0,24 R |
| 2024 | S4 Short quand le biais mécanique est ≤ −5 | +0,23 R | 0 | n.d. |
| 2025 | S4 Short quand le biais mécanique est ≤ −5 | +0,23 R | 1 | +1,52 R |
| 2026 | S4 Short quand le biais mécanique est ≤ −5 | +0,26 R | 5 | -0,22 R |

## Robustesse des règles journalières
R moyen quand on change le stop et la durée (objectif = 1,6 fois le stop). Nombre de trades entre parenthèses.

**L2 Long en peur extrême, sous la moyenne 200 jours**

| Stop | 3 jours | 7 jours | 14 jours |
|---|---|---|---|
| 3 % | -0,09 R (281) | -0,10 R (254) | -0,11 R (252) |
| 4 % | -0,08 R (250) | -0,09 R (206) | -0,09 R (199) |
| 6 % | -0,04 R (215) | -0,03 R (155) | -0,01 R (139) |

**S1 Short sur rebond (+8 % en 7 jours) sous la moyenne 200 jours**

| Stop | 3 jours | 7 jours | 14 jours |
|---|---|---|---|
| 3 % | -0,09 R (99) | -0,08 R (92) | -0,11 R (92) |
| 4 % | -0,03 R (85) | -0,13 R (75) | -0,13 R (75) |
| 6 % | -0,02 R (78) | +0,02 R (61) | +0,03 R (61) |

## Suivi de tendance sans stop, sans levier
| Stratégie | Période | Rendement annuel | Pire baisse | Temps en position | Détenir sur la même période |
|---|---|---|---|---|---|
| Long au-dessus de la moyenne 200 jours, sans financement | 2017-07-19 au 2026-11-16 | +41,4 % | -70,7 % | 56 % | +43,3 % |
| Long au-dessus de la moyenne 200 jours, avec financement réel | 2019-05-01 au 2026-11-16 | +23,8 % | -65,5 % | 60 % | +39,3 % |
| Short sous la moyenne 200 jours, sans financement | 2017-07-19 au 2026-11-16 | -19,0 % | -92,1 % | 44 % | +43,3 % |
| Short sous la moyenne 200 jours, avec financement réel | 2019-05-01 au 2026-11-16 | -19,4 % | -87,3 % | 40 % | +39,3 % |

## Limites
- Les définitions mécaniques approchent les configurations de la méthode ; elles ne reproduisent pas le jugement d'une analyse (choix des niveaux, lecture des flux, actualité).
- Les flux des ETF, les liquidations et les événements ne sont pas testés, faute d'historique gratuit.
- Le financement réel avant 2025 est celui de Deribit, pas de Kraken.
- Dans une bougie de 4 heures, l'ordre entre stop et objectif reste inconnu : le stop est compté.
- L'historique couvre surtout des marchés haussiers : les règles « long » y sont flattées, les « short » pénalisées.
- Aucun réglage n'a été ajusté pour améliorer ces résultats.
