# Dernier relevé BTC (19/11/2026 01:07 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-18)
- **Bitcoin : 57 423 € (62 982 $)**, EUR/USD 1,0968 (BCE)
- Variation : -2,9 % sur 1 jour, -14,8 % sur 7 jours, -23,0 % sur 30 jours
- 30 derniers jours : plus haut 77 367 € (84 856 $), plus bas 56 479 € (61 946 $)
- Volatilité réalisée sur 30 jours : 44 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 71 643 € (78 578 $) | -19,8 % |
| 200 jours | 66 300 € (72 718 $) | -13,4 % |
| 200 semaines | 62 325 € (68 358 $) | -7,9 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-19 à 01:07 UTC) : 0,0063 % par 8 h, **positif : les longs paient les shorts** ; prévision pour l'heure suivante : 0,0073 % (positif : les longs paient les shorts) ; Deribit : 0,0002 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-18 : 0,0044 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0055 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 378 BTC (relevé du 2026-11-19)
- Volatilité implicite (DVOL) : 45,7 le 2026-11-18
- Options Deribit, rapport puts/calls : 0,78 en positions ouvertes, 1,53 en volume sur 24 h (relevé du 2026-11-19)
- Échéance d'options la plus chargée : 2026-12-25, 149 757 BTC en positions ouvertes, « max pain » à 68 381 € (75 000 $)
- Fear & Greed : 10 le 2026-11-19, 28 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,21 le 2026-11-17

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-18 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-12 -6, 11-13 -5, 11-14 -5, 11-15 -5, 11-16 -5, 11-17 -6, 11-18 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-18 à 57 423 € (62 982 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 62 325 € (68 358 $) | -7,9 % | cassé le 2026-11-14 (5 j), pas repris |
| Moyenne 200 jours | 66 300 € (72 718 $) | -13,4 % | cassé le 2026-11-12 (7 j), pas repris |
| Plus bas des 90 jours précédents | 56 479 € (61 946 $) | +1,7 % | tient |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : oui ; financement en direct négatif : non ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 5,07 % (2026-11-18)
- Taux américain à 2 ans : 4,80 % (2026-11-18)
- Taux réel à 10 ans : 2,88 % (2026-11-18)
- VIX : 25,5 (2026-11-17)
- Nasdaq-100 : 27 116 points (2026-11-18)
- S&P 500 : 7 324 points (2026-11-18)
- Dollar (DXY) : 103,49 (2026-11-17)
- Brent : 93,1 $ (2026-11-17)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-18 00:00 | 64 873 $ | 64 933 $ | 64 034 $ | 58 693 € (64 375 $) |
| 2026-11-18 04:00 | 64 375 $ | 64 890 $ | 64 234 $ | 59 090 € (64 810 $) |
| 2026-11-18 08:00 | 64 810 $ | 64 810 $ | 64 025 $ | 58 492 € (64 154 $) |
| 2026-11-18 12:00 | 64 154 $ | 64 317 $ | 62 918 $ | 57 484 € (63 048 $) |
| 2026-11-18 16:00 | 63 048 $ | 63 458 $ | 62 203 $ | 57 134 € (62 664 $) |
| 2026-11-18 20:00 | 62 664 $ | 63 232 $ | 62 000 $ | 57 423 € (62 982 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-19)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,74 | 0,82 | 67 % | 1,54 | 1,23 |
| IREN | 0,96 | 0,40 | 16 % | 0,99 | 1,06 |
| CleanSpark (CLSK) | 0,85 | 0,38 | 14 % | 1,19 | 1,28 |
| Solana (SOL) | 1,25 | 0,86 | 74 % | 1,23 | 1,18 |
| Microsoft | 0,24 | 0,38 | 14 % | 0,24 | 0,45 |
| Meta | 0,33 | 0,32 | 10 % | 0,18 | 0,16 |
| Amazon | 0,27 | 0,36 | 13 % | 0,18 | 0,35 |
| Monday.com | 0,27 | 0,17 | 3 % | 0,23 | 0,26 |
| Nasdaq-100 | 0,31 | 0,53 | 28 % | 0,22 | 0,25 |
| S&P 500 | 0,20 | 0,53 | 28 % | 0,15 | 0,19 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-18 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-18 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-18 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-19 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-18 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-19 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-18 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-18 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-18 20:00 | 0.05 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-19 00:00 | 0.01 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-18 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-19 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-19 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-17 | 2 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
