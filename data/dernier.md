# Dernier relevé BTC (18/11/2026 13:30 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-17)
- **Bitcoin : 59 035 € (64 873 $)**, EUR/USD 1,0989 (BCE)
- Variation : +0,1 % sur 1 jour, -12,0 % sur 7 jours, -20,9 % sur 30 jours
- 30 derniers jours : plus haut 77 219 € (84 856 $), plus bas 56 371 € (61 946 $)
- Volatilité réalisée sur 30 jours : 43 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 71 882 € (78 991 $) | -17,9 % |
| 200 jours | 66 245 € (72 797 $) | -10,9 % |
| 200 semaines | 61 952 € (68 079 $) | -4,7 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-18 à 13:29 UTC) : -0,0020 % par 8 h, **négatif : les shorts paient les longs** ; prévision pour l'heure suivante : 0,0119 % (positif : les longs paient les shorts) ; Deribit : 0,0000 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-17 : 0,0062 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0066 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 383 BTC (relevé du 2026-11-18)
- Volatilité implicite (DVOL) : 43,3 le 2026-11-17
- Options Deribit, rapport puts/calls : 0,77 en positions ouvertes, 1,34 en volume sur 24 h (relevé du 2026-11-18)
- Échéance d'options la plus chargée : 2026-12-25, 149 089 BTC en positions ouvertes, « max pain » à 68 250 € (75 000 $)
- Fear & Greed : 11 le 2026-11-18, 29 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,21 le 2026-11-17

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-17 : -6 sur 10** (structure du prix -2 · positionnement +1 · blockchain -1 · macro -2 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-11 -2, 11-12 -6, 11-13 -5, 11-14 -5, 11-15 -5, 11-16 -5, 11-17 -6
- Règles mécaniques suivies en papier : **S4 active** (short quand le biais mécanique est ≤ −5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-17 à 59 035 € (64 873 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 61 952 € (68 079 $) | -4,7 % | cassé le 2026-11-14 (4 j), pas repris |
| Moyenne 200 jours | 66 245 € (72 797 $) | -10,9 % | cassé le 2026-11-12 (6 j), pas repris |
| Plus bas des 90 jours précédents | 56 371 € (61 946 $) | +4,7 % | tient |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : oui ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 5,10 % (2026-11-17)
- Taux américain à 2 ans : 4,80 % (2026-11-17)
- Taux réel à 10 ans : 2,89 % (2026-11-17)
- VIX : 25,5 (2026-11-17)
- Nasdaq-100 : 27 002 points (2026-11-17)
- S&P 500 : 7 341 points (2026-11-17)
- Dollar (DXY) : 103,49 (2026-11-17)
- Brent : 93,1 $ (2026-11-17)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-17 12:00 | 64 928 $ | 65 383 $ | 63 257 $ | 58 283 € (64 047 $) |
| 2026-11-17 16:00 | 64 047 $ | 64 417 $ | 63 377 $ | 57 945 € (63 675 $) |
| 2026-11-17 20:00 | 63 675 $ | 65 199 $ | 63 584 $ | 59 035 € (64 873 $) |
| 2026-11-18 00:00 | 64 873 $ | 64 933 $ | 64 034 $ | 58 581 € (64 375 $) |
| 2026-11-18 04:00 | 64 375 $ | 64 890 $ | 64 234 $ | 58 977 € (64 810 $) |
| 2026-11-18 08:00 | 64 810 $ | 64 810 $ | 64 025 $ | 58 380 € (64 154 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-18)
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
| Nasdaq-100 | 0,28 | 0,51 | 26 % | 0,22 | 0,25 |
| S&P 500 | 0,18 | 0,52 | 27 % | 0,15 | 0,19 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-17 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-17 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-17 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-18 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-17 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-18 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-17 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-17 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-18 08:00 | 0.06 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-18 12:00 | 0.02 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-17 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-18 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-18 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-17 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
