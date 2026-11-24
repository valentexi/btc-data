# Dernier relevé BTC (24/11/2026 10:16 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-23)
- **Bitcoin : 55 937 € (61 190 $)**, EUR/USD 1,0939 (BCE)
- Variation : +0,0 % sur 1 jour, -5,6 % sur 7 jours, -24,2 % sur 30 jours
- 30 derniers jours : plus haut 74 861 € (81 890 $), plus bas 50 376 € (55 106 $)
- Volatilité réalisée sur 30 jours : 47 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 69 621 € (76 158 $) | -19,7 % |
| 200 jours | 66 030 € (72 230 $) | -15,3 % |
| 200 semaines | 62 516 € (68 386 $) | -10,5 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-24 à 10:16 UTC) : 0,0003 % par 8 h, **positif : les longs paient les shorts** ; prévision pour l'heure suivante : 0,0019 % (positif : les longs paient les shorts) ; Deribit : -0,0001 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-23 : 0,0069 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0059 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 123 BTC (relevé du 2026-11-24)
- Volatilité implicite (DVOL) : 52,3 le 2026-11-23
- Options Deribit, rapport puts/calls : 0,80 en positions ouvertes, 0,73 en volume sur 24 h (relevé du 2026-11-24)
- Échéance d'options la plus chargée : 2026-12-25, 162 579 BTC en positions ouvertes, « max pain » à 65 820 € (72 000 $)
- Fear & Greed : 11 le 2026-11-24, 12 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,15 le 2026-11-23

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-23 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-17 -6, 11-18 -3, 11-19 -4, 11-20 -4, 11-21 -3, 11-22 -3, 11-23 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-23 à 55 937 € (61 190 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 62 516 € (68 386 $) | -10,5 % | cassé le 2026-11-14 (10 j), pas repris |
| Moyenne 200 jours | 66 030 € (72 230 $) | -15,3 % | cassé le 2026-11-12 (12 j), pas repris |
| Plus bas des 90 jours précédents | 50 376 € (55 106 $) | +11,0 % | repris le 2026-11-21 |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : non ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 4,92 % (2026-11-23)
- Taux américain à 2 ans : 4,63 % (2026-11-23)
- Taux réel à 10 ans : 2,79 % (2026-11-23)
- VIX : 26,6 (2026-11-23)
- Nasdaq-100 : 26 746 points (2026-11-23)
- S&P 500 : 7 237 points (2026-11-23)
- Dollar (DXY) : 104,32 (2026-11-23)
- Brent : 89,4 $ (2026-11-23)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-23 08:00 | 61 370 $ | 61 845 $ | 61 052 $ | 56 081 € (61 347 $) |
| 2026-11-23 12:00 | 61 347 $ | 64 534 $ | 60 991 $ | 57 430 € (62 823 $) |
| 2026-11-23 16:00 | 62 823 $ | 62 868 $ | 60 687 $ | 55 938 € (61 191 $) |
| 2026-11-23 20:00 | 61 191 $ | 61 515 $ | 60 979 $ | 55 937 € (61 190 $) |
| 2026-11-24 00:00 | 61 191 $ | 61 603 $ | 59 366 $ | 55 085 € (60 257 $) |
| 2026-11-24 04:00 | 60 257 $ | 60 706 $ | 60 201 $ | 55 179 € (60 360 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-24)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,94 | 0,83 | 69 % | 1,55 | 1,28 |
| IREN | 1,67 | 0,54 | 29 % | 1,07 | 1,16 |
| CleanSpark (CLSK) | 1,35 | 0,51 | 26 % | 1,23 | 1,35 |
| Solana (SOL) | 1,28 | 0,85 | 72 % | 1,23 | 1,20 |
| Microsoft | 0,35 | 0,48 | 23 % | 0,24 | 0,45 |
| Meta | 0,56 | 0,45 | 21 % | 0,21 | 0,19 |
| Amazon | 0,41 | 0,45 | 20 % | 0,19 | 0,35 |
| Monday.com | 0,26 | 0,15 | 2 % | 0,22 | 0,21 |
| Nasdaq-100 | 0,51 | 0,66 | 43 % | 0,25 | 0,26 |
| S&P 500 | 0,33 | 0,65 | 43 % | 0,17 | 0,20 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-23 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-23 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-23 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-24 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-23 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-24 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-23 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-23 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-24 04:00 | 0.09 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-24 09:00 | 0.01 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-23 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-24 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-24 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-23 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
