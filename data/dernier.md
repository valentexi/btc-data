# Dernier relevé BTC (15/11/2026 18:13 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-14)
- **Bitcoin : 58 016 € (64 119 $)**, EUR/USD 1,1052 (BCE)
- Variation : -6,0 % sur 1 jour, -15,4 % sur 7 jours, -21,9 % sur 30 jours
- 30 derniers jours : plus haut 76 779 € (84 856 $), plus bas 57 248 € (63 270 $)
- Volatilité réalisée sur 30 jours : 43 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 72 510 € (80 138 $) | -20,0 % |
| 200 jours | 66 027 € (72 973 $) | -12,1 % |
| 200 semaines | 61 394 € (67 852 $) | -5,5 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-15 à 18:13 UTC) : -0,0015 % par 8 h, **négatif : les shorts paient les longs** ; prévision pour l'heure suivante : -0,0011 % (négatif : les shorts paient les longs) ; Deribit : 0,0000 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-14 : 0,0028 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0081 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 295 BTC (relevé du 2026-11-15)
- Volatilité implicite (DVOL) : 47,3 le 2026-11-14
- Options Deribit, rapport puts/calls : 0,76 en positions ouvertes, 1,79 en volume sur 24 h (relevé du 2026-11-15)
- Échéance d'options la plus chargée : 2026-12-25, 146 306 BTC en positions ouvertes, « max pain » à 67 861 € (75 000 $)
- Fear & Greed : 10 le 2026-11-15, 28 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,19 le 2026-11-14

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-14 : -5 sur 10** (structure du prix -2 · positionnement +1 · blockchain -1 · macro -2 · actifs risqués -1). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-08 -3, 11-09 +0, 11-10 -2, 11-11 -2, 11-12 -6, 11-13 -5, 11-14 -5
- Règles mécaniques suivies en papier : **S4 active** (short quand le biais mécanique est ≤ −5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-14 à 58 016 € (64 119 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 61 394 € (67 852 $) | -5,5 % | cassé le 2026-11-14 (1 j), pas repris |
| Moyenne 200 jours | 66 027 € (72 973 $) | -12,1 % | cassé le 2026-11-12 (3 j), pas repris |
| Plus bas des 90 jours précédents | 56 670 € (62 631 $) | +2,4 % | tient |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : oui ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 5,15 % (2026-11-13)
- Taux américain à 2 ans : 4,88 % (2026-11-13)
- Taux réel à 10 ans : 2,91 % (2026-11-13)
- VIX : 19,3 (2026-11-13)
- Nasdaq-100 : 27 944 points (2026-11-13)
- S&P 500 : 7 562 points (2026-11-13)
- Dollar (DXY) : 103,41 (2026-11-13)
- Brent : 95,8 $ (2026-11-13)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-14 16:00 | 65 689 $ | 66 151 $ | 64 978 $ | 59 423 € (65 675 $) |
| 2026-11-14 20:00 | 65 675 $ | 65 832 $ | 63 270 $ | 58 016 € (64 119 $) |
| 2026-11-15 00:00 | 64 119 $ | 65 564 $ | 61 946 $ | 58 617 € (64 783 $) |
| 2026-11-15 04:00 | 64 783 $ | 65 127 $ | 63 726 $ | 57 882 € (63 971 $) |
| 2026-11-15 08:00 | 63 971 $ | 66 100 $ | 63 832 $ | 59 098 € (65 316 $) |
| 2026-11-15 12:00 | 65 316 $ | 65 767 $ | 64 387 $ | 58 547 € (64 706 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-15)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,75 | 0,82 | 67 % | 1,53 | 1,20 |
| IREN | 0,92 | 0,38 | 15 % | 0,98 | 1,03 |
| CleanSpark (CLSK) | 0,85 | 0,37 | 14 % | 1,21 | 1,30 |
| Solana (SOL) | 1,24 | 0,87 | 75 % | 1,22 | 1,17 |
| Microsoft | 0,22 | 0,34 | 11 % | 0,23 | 0,43 |
| Meta | 0,29 | 0,27 | 7 % | 0,17 | 0,14 |
| Amazon | 0,24 | 0,32 | 10 % | 0,18 | 0,34 |
| Monday.com | 0,29 | 0,18 | 3 % | 0,24 | 0,28 |
| Nasdaq-100 | 0,26 | 0,48 | 23 % | 0,22 | 0,23 |
| S&P 500 | 0,16 | 0,48 | 23 % | 0,15 | 0,18 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-14 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-13 | 2 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-14 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-15 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-14 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-15 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-13 | 2 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-14 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-15 12:00 | 0.09 j | à jour | (Coinbase, heures agrégées) |
| financement_deribit | historique | ok | 2026-11-14 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-15 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-15 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-14 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
