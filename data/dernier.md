# Dernier relevé BTC (17/11/2026 09:08 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-16)
- **Bitcoin : 58 849 € (64 817 $)**, EUR/USD 1,1014 (BCE)
- Variation : -0,8 % sur 1 jour, -13,9 % sur 7 jours, -20,4 % sur 30 jours
- 30 derniers jours : plus haut 77 044 € (84 856 $), plus bas 56 243 € (61 946 $)
- Volatilité réalisée sur 30 jours : 44 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 72 056 € (79 363 $) | -18,3 % |
| 200 jours | 66 155 € (72 864 $) | -11,0 % |
| 200 semaines | 61 917 € (68 195 $) | -5,0 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-17 à 09:08 UTC) : -0,0030 % par 8 h, **négatif : les shorts paient les longs** ; prévision pour l'heure suivante : 0,0100 % (positif : les longs paient les shorts) ; Deribit : 0,0021 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-16 : 0,0096 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0072 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 244 BTC (relevé du 2026-11-17)
- Volatilité implicite (DVOL) : 43,1 le 2026-11-16
- Options Deribit, rapport puts/calls : 0,77 en positions ouvertes, 1,25 en volume sur 24 h (relevé du 2026-11-17)
- Échéance d'options la plus chargée : 2026-12-25, 148 190 BTC en positions ouvertes, « max pain » à 68 095 € (75 000 $)
- Fear & Greed : 12 le 2026-11-17, 32 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,21 le 2026-11-16

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-16 : -5 sur 10** (structure du prix -2 · positionnement +1 · blockchain -1 · macro -2 · actifs risqués -1). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-10 -2, 11-11 -2, 11-12 -6, 11-13 -5, 11-14 -5, 11-15 -5, 11-16 -5
- Règles mécaniques suivies en papier : **S4 active** (short quand le biais mécanique est ≤ −5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-16 à 58 849 € (64 817 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 61 917 € (68 195 $) | -5,0 % | cassé le 2026-11-14 (3 j), pas repris |
| Moyenne 200 jours | 66 155 € (72 864 $) | -11,0 % | cassé le 2026-11-12 (5 j), pas repris |
| Plus bas des 90 jours précédents | 56 243 € (61 946 $) | +4,6 % | tient |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : oui ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 5,12 % (2026-11-16)
- Taux américain à 2 ans : 4,83 % (2026-11-16)
- Taux réel à 10 ans : 2,92 % (2026-11-16)
- VIX : 22,9 (2026-11-16)
- Nasdaq-100 : 27 197 points (2026-11-16)
- S&P 500 : 7 417 points (2026-11-16)
- Dollar (DXY) : 103,55 (2026-11-16)
- Brent : 92,4 $ (2026-11-16)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-16 08:00 | 64 920 $ | 64 931 $ | 64 055 $ | 58 450 € (64 377 $) |
| 2026-11-16 12:00 | 64 377 $ | 65 627 $ | 63 833 $ | 58 470 € (64 399 $) |
| 2026-11-16 16:00 | 64 399 $ | 65 138 $ | 64 161 $ | 59 017 € (65 001 $) |
| 2026-11-16 20:00 | 65 001 $ | 65 476 $ | 64 724 $ | 58 849 € (64 817 $) |
| 2026-11-17 00:00 | 64 817 $ | 65 150 $ | 64 315 $ | 59 012 € (64 996 $) |
| 2026-11-17 04:00 | 64 996 $ | 65 037 $ | 64 228 $ | 58 721 € (64 675 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-17)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,74 | 0,82 | 67 % | 1,54 | 1,23 |
| IREN | 0,95 | 0,40 | 16 % | 0,99 | 1,06 |
| CleanSpark (CLSK) | 0,84 | 0,38 | 14 % | 1,19 | 1,28 |
| Solana (SOL) | 1,25 | 0,87 | 76 % | 1,23 | 1,18 |
| Microsoft | 0,24 | 0,38 | 15 % | 0,24 | 0,45 |
| Meta | 0,32 | 0,31 | 10 % | 0,18 | 0,16 |
| Amazon | 0,27 | 0,36 | 13 % | 0,18 | 0,35 |
| Monday.com | 0,27 | 0,18 | 3 % | 0,23 | 0,26 |
| Nasdaq-100 | 0,28 | 0,51 | 26 % | 0,22 | 0,25 |
| S&P 500 | 0,18 | 0,52 | 27 % | 0,15 | 0,19 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-16 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-16 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-16 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-17 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-16 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-17 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-16 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-16 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-17 04:00 | 0.05 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-17 08:00 | 0.01 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-16 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-17 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-17 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-16 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
