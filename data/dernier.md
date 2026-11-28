# Dernier relevé BTC (28/11/2026 13:42 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-27)
- **Bitcoin : 54 630 € (59 858 $)**, EUR/USD 1,0957 (BCE)
- Variation : -1,1 % sur 1 jour, +1,8 % sur 7 jours, -26,3 % sur 30 jours
- 30 derniers jours : plus haut 74 738 € (81 890 $), plus bas 50 293 € (55 106 $)
- Volatilité réalisée sur 30 jours : 47 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 67 758 € (74 243 $) | -19,4 % |
| 200 jours | 65 537 € (71 809 $) | -16,6 % |
| 200 semaines | 62 293 € (68 254 $) | -12,3 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-28 à 13:41 UTC) : -0,0025 % par 8 h, **négatif : les shorts paient les longs** ; prévision pour l'heure suivante : -0,0057 % (négatif : les shorts paient les longs) ; Deribit : 0,0000 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-27 : 0,0018 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0053 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 115 BTC (relevé du 2026-11-28)
- Volatilité implicite (DVOL) : 51,6 le 2026-11-27
- Options Deribit, rapport puts/calls : 0,81 en positions ouvertes, 1,20 en volume sur 24 h (relevé du 2026-11-28)
- Échéance d'options la plus chargée : 2026-12-25, 167 856 BTC en positions ouvertes, « max pain » à 63 886 € (70 000 $)
- Fear & Greed : 10 le 2026-11-28, 12 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,13 le 2026-11-27

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-27 : -2 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -1). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-21 -3, 11-22 -3, 11-23 -3, 11-24 -3, 11-25 -3, 11-26 -4, 11-27 -2
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-27 à 54 630 € (59 858 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 62 293 € (68 254 $) | -12,3 % | cassé le 2026-11-14 (14 j), pas repris |
| Moyenne 200 jours | 65 537 € (71 809 $) | -16,6 % | cassé le 2026-11-12 (16 j), pas repris |
| Plus bas des 90 jours précédents | 50 293 € (55 106 $) | +8,6 % | repris le 2026-11-21 |

- **Long de retournement : exclu** (aucun support majeur qui tient à moins de 3 % sous le prix).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : oui ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 4,94 % (2026-11-27)
- Taux américain à 2 ans : 4,69 % (2026-11-27)
- Taux réel à 10 ans : 2,79 % (2026-11-27)
- VIX : 23,8 (2026-11-27)
- Nasdaq-100 : 26 726 points (2026-11-27)
- S&P 500 : 7 297 points (2026-11-27)
- Dollar (DXY) : 104,01 (2026-11-27)
- Brent : 95,4 $ (2026-11-27)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-27 12:00 | 61 574 $ | 61 630 $ | 58 700 $ | 54 810 € (60 055 $) |
| 2026-11-27 16:00 | 60 054 $ | 60 471 $ | 59 432 $ | 54 607 € (59 833 $) |
| 2026-11-27 20:00 | 59 834 $ | 59 862 $ | 59 511 $ | 54 630 € (59 858 $) |
| 2026-11-28 00:00 | 59 858 $ | 60 200 $ | 59 768 $ | 54 719 € (59 956 $) |
| 2026-11-28 04:00 | 59 956 $ | 60 012 $ | 59 124 $ | 54 550 € (59 771 $) |
| 2026-11-28 08:00 | 59 771 $ | 59 797 $ | 58 996 $ | 54 008 € (59 176 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-28)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,92 | 0,84 | 71 % | 1,57 | 1,29 |
| IREN | 1,66 | 0,54 | 29 % | 1,05 | 1,19 |
| CleanSpark (CLSK) | 1,33 | 0,51 | 26 % | 1,20 | 1,35 |
| Solana (SOL) | 1,24 | 0,86 | 74 % | 1,23 | 1,21 |
| Microsoft | 0,34 | 0,47 | 22 % | 0,24 | 0,45 |
| Meta | 0,60 | 0,47 | 22 % | 0,21 | 0,20 |
| Amazon | 0,44 | 0,48 | 23 % | 0,19 | 0,35 |
| Monday.com | 0,23 | 0,14 | 2 % | 0,23 | 0,21 |
| Nasdaq-100 | 0,51 | 0,64 | 41 % | 0,24 | 0,27 |
| S&P 500 | 0,33 | 0,64 | 41 % | 0,17 | 0,20 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-27 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-27 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-27 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-28 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-27 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-28 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-27 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-27 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-28 08:00 | 0.07 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-28 12:00 | 0.03 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-27 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-28 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-28 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-27 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
