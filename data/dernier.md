# Dernier relevé BTC (25/11/2026 17:25 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-24)
- **Bitcoin : 54 493 € (59 741 $)**, EUR/USD 1,0963 (BCE)
- Variation : -2,4 % sur 1 jour, -7,9 % sur 7 jours, -25,4 % sur 30 jours
- 30 derniers jours : plus haut 74 697 € (81 890 $), plus bas 50 265 € (55 106 $)
- Volatilité réalisée sur 30 jours : 47 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 68 994 € (75 638 $) | -21,0 % |
| 200 jours | 65 792 € (72 128 $) | -17,2 % |
| 200 semaines | 62 268 € (68 264 $) | -12,5 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-25 à 17:25 UTC) : 0,0028 % par 8 h, **positif : les longs paient les shorts** ; prévision pour l'heure suivante : 0,0096 % (positif : les longs paient les shorts) ; Deribit : 0,0000 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-24 : 0,0014 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0052 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 1 980 BTC (relevé du 2026-11-25)
- Volatilité implicite (DVOL) : 53,1 le 2026-11-24
- Options Deribit, rapport puts/calls : 0,81 en positions ouvertes, 1,31 en volume sur 24 h (relevé du 2026-11-25)
- Échéance d'options la plus chargée : 2026-12-25, 163 470 BTC en positions ouvertes, « max pain » à 63 851 € (70 000 $)
- Fear & Greed : 13 le 2026-11-25, 11 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,13 le 2026-11-24

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-24 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-18 -3, 11-19 -4, 11-20 -4, 11-21 -3, 11-22 -3, 11-23 -3, 11-24 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-24 à 54 493 € (59 741 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 62 268 € (68 264 $) | -12,5 % | cassé le 2026-11-14 (11 j), pas repris |
| Moyenne 200 jours | 65 792 € (72 128 $) | -17,2 % | cassé le 2026-11-12 (13 j), pas repris |
| Plus bas des 90 jours précédents | 50 265 € (55 106 $) | +8,4 % | repris le 2026-11-21 |

- **Long de retournement : exclu** (aucun support majeur qui tient à moins de 3 % sous le prix).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : non ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 4,91 % (2026-11-24)
- Taux américain à 2 ans : 4,63 % (2026-11-24)
- Taux réel à 10 ans : 2,79 % (2026-11-24)
- VIX : 26,4 (2026-11-24)
- Nasdaq-100 : 26 214 points (2026-11-24)
- S&P 500 : 7 201 points (2026-11-24)
- Dollar (DXY) : 103,81 (2026-11-24)
- Brent : 91,4 $ (2026-11-24)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-24 16:00 | 59 643 $ | 60 210 $ | 59 190 $ | 54 365 € (59 601 $) |
| 2026-11-24 20:00 | 59 601 $ | 60 013 $ | 59 378 $ | 54 493 € (59 741 $) |
| 2026-11-25 00:00 | 59 741 $ | 59 749 $ | 58 853 $ | 54 119 € (59 331 $) |
| 2026-11-25 04:00 | 59 331 $ | 59 332 $ | 58 528 $ | 53 502 € (58 654 $) |
| 2026-11-25 08:00 | 58 655 $ | 59 397 $ | 58 365 $ | 53 410 € (58 553 $) |
| 2026-11-25 12:00 | 58 553 $ | 58 848 $ | 57 208 $ | 53 139 € (58 256 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-25)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,97 | 0,84 | 70 % | 1,56 | 1,28 |
| IREN | 1,71 | 0,56 | 31 % | 1,08 | 1,17 |
| CleanSpark (CLSK) | 1,38 | 0,52 | 27 % | 1,24 | 1,36 |
| Solana (SOL) | 1,28 | 0,85 | 72 % | 1,23 | 1,20 |
| Microsoft | 0,34 | 0,47 | 22 % | 0,24 | 0,45 |
| Meta | 0,56 | 0,46 | 21 % | 0,21 | 0,20 |
| Amazon | 0,41 | 0,46 | 21 % | 0,19 | 0,35 |
| Monday.com | 0,25 | 0,14 | 2 % | 0,22 | 0,21 |
| Nasdaq-100 | 0,51 | 0,66 | 44 % | 0,25 | 0,27 |
| S&P 500 | 0,33 | 0,66 | 43 % | 0,17 | 0,20 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-24 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-25 | 0 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-24 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-25 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-24 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-25 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-24 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-24 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-25 12:00 | 0.06 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-25 16:00 | 0.02 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-24 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-25 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-25 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-24 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
