# Dernier relevé BTC (20/11/2026 01:14 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-19)
- **Bitcoin : 56 326 € (61 913 $)**, EUR/USD 1,0992 (BCE)
- Variation : -1,7 % sur 1 jour, -13,3 % sur 7 jours, -25,4 % sur 30 jours
- 30 derniers jours : plus haut 77 198 € (84 856 $), plus bas 55 813 € (61 350 $)
- Volatilité réalisée sur 30 jours : 43 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 71 093 € (78 145 $) | -20,8 % |
| 200 jours | 66 080 € (72 635 $) | -14,8 % |
| 200 semaines | 61 930 € (68 073 $) | -9,0 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-20 à 01:14 UTC) : 0,0129 % par 8 h, **positif : les longs paient les shorts** ; prévision pour l'heure suivante : 0,0154 % (positif : les longs paient les shorts) ; Deribit : 0,0000 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-19 : 0,0040 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0046 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 247 BTC (relevé du 2026-11-20)
- Volatilité implicite (DVOL) : 45,9 le 2026-11-19
- Options Deribit, rapport puts/calls : 0,79 en positions ouvertes, 1,97 en volume sur 24 h (relevé du 2026-11-20)
- Échéance d'options la plus chargée : 2026-12-25, 151 043 BTC en positions ouvertes, « max pain » à 67 322 € (74 000 $)
- Fear & Greed : 12 le 2026-11-20, 20 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,18 le 2026-11-18

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-19 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain -1 · macro +0 · actifs risqués -1). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-13 -5, 11-14 -5, 11-15 -5, 11-16 -5, 11-17 -6, 11-18 -3, 11-19 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-19 à 56 326 € (61 913 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 61 930 € (68 073 $) | -9,0 % | cassé le 2026-11-14 (6 j), pas repris |
| Moyenne 200 jours | 66 080 € (72 635 $) | -14,8 % | cassé le 2026-11-12 (8 j), pas repris |
| Plus bas des 90 jours précédents | 56 356 € (61 946 $) | -0,1 % | cassé le 2026-11-19 (1 j), pas repris |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : non ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 5,04 % (2026-11-19)
- Taux américain à 2 ans : 4,76 % (2026-11-19)
- Taux réel à 10 ans : 2,88 % (2026-11-19)
- VIX : 24,6 (2026-11-18)
- Nasdaq-100 : 26 517 points (2026-11-19)
- S&P 500 : 7 176 points (2026-11-19)
- Dollar (DXY) : 103,86 (2026-11-18)
- Brent : 91,9 $ (2026-11-18)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-19 00:00 | 62 982 $ | 63 227 $ | 62 322 $ | 57 437 € (63 135 $) |
| 2026-11-19 04:00 | 63 135 $ | 63 808 $ | 63 131 $ | 57 923 € (63 669 $) |
| 2026-11-19 08:00 | 63 669 $ | 64 014 $ | 63 494 $ | 58 116 € (63 881 $) |
| 2026-11-19 12:00 | 63 879 $ | 64 024 $ | 62 700 $ | 57 344 € (63 033 $) |
| 2026-11-19 16:00 | 63 033 $ | 63 340 $ | 62 150 $ | 56 670 € (62 292 $) |
| 2026-11-19 20:00 | 62 292 $ | 62 388 $ | 61 350 $ | 56 326 € (61 913 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-20)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,75 | 0,81 | 65 % | 1,54 | 1,23 |
| IREN | 1,01 | 0,41 | 17 % | 0,99 | 1,07 |
| CleanSpark (CLSK) | 0,92 | 0,39 | 15 % | 1,18 | 1,27 |
| Solana (SOL) | 1,21 | 0,84 | 71 % | 1,23 | 1,18 |
| Microsoft | 0,25 | 0,38 | 14 % | 0,24 | 0,45 |
| Meta | 0,36 | 0,34 | 11 % | 0,18 | 0,16 |
| Amazon | 0,23 | 0,29 | 8 % | 0,17 | 0,34 |
| Monday.com | 0,24 | 0,15 | 2 % | 0,23 | 0,25 |
| Nasdaq-100 | 0,35 | 0,57 | 33 % | 0,22 | 0,24 |
| S&P 500 | 0,23 | 0,58 | 34 % | 0,15 | 0,19 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-19 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-19 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-19 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-20 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-19 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-20 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-19 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-19 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-19 20:00 | 0.05 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-20 00:00 | 0.01 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-19 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-20 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-20 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-18 | 2 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
