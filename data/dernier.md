# Dernier relevé BTC (22/11/2026 06:45 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-21)
- **Bitcoin : 54 673 € (60 086 $)**, EUR/USD 1,0990 (BCE)
- Variation : +2,2 % sur 1 jour, -6,3 % sur 7 jours, -26,1 % sur 30 jours
- 30 derniers jours : plus haut 74 579 € (81 962 $), plus bas 50 142 € (55 106 $)
- Volatilité réalisée sur 30 jours : 46 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 70 188 € (77 136 $) | -22,1 % |
| 200 jours | 65 902 € (72 426 $) | -17,0 % |
| 200 semaines | 61 910 € (68 039 $) | -11,7 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-22 à 06:45 UTC) : 0,0103 % par 8 h, **positif : les longs paient les shorts** ; prévision pour l'heure suivante : 0,0079 % (positif : les longs paient les shorts) ; Deribit : -0,0002 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-21 : 0,0057 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0052 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 243 BTC (relevé du 2026-11-22)
- Volatilité implicite (DVOL) : 58,0 le 2026-11-21
- Options Deribit, rapport puts/calls : 0,82 en positions ouvertes, 0,81 en volume sur 24 h (relevé du 2026-11-22)
- Échéance d'options la plus chargée : 2026-12-25, 156 949 BTC en positions ouvertes, « max pain » à 65 514 € (72 000 $)
- Fear & Greed : 11 le 2026-11-22, 10 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,13 le 2026-11-21

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-21 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-15 -5, 11-16 -5, 11-17 -6, 11-18 -3, 11-19 -4, 11-20 -4, 11-21 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-21 à 54 673 € (60 086 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 61 910 € (68 039 $) | -11,7 % | cassé le 2026-11-14 (8 j), pas repris |
| Moyenne 200 jours | 65 902 € (72 426 $) | -17,0 % | cassé le 2026-11-12 (10 j), pas repris |
| Plus bas des 90 jours précédents | 52 461 € (57 655 $) | +4,2 % | repris le 2026-11-21 |

- **Long de retournement : exclu** (support majeur cassé depuis moins de 10 jours sans reprise en clôture (moyenne 200 semaines)).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : non ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 4,92 % (2026-11-20)
- Taux américain à 2 ans : 4,63 % (2026-11-20)
- Taux réel à 10 ans : 2,77 % (2026-11-20)
- VIX : 35,9 (2026-11-20)
- Nasdaq-100 : 25 029 points (2026-11-20)
- S&P 500 : 6 910 points (2026-11-20)
- Dollar (DXY) : 103,81 (2026-11-20)
- Brent : 89,9 $ (2026-11-20)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-21 04:00 | 56 642 $ | 58 566 $ | 55 106 $ | 52 663 € (57 876 $) |
| 2026-11-21 08:00 | 57 876 $ | 58 543 $ | 57 264 $ | 52 876 € (58 111 $) |
| 2026-11-21 12:00 | 58 111 $ | 60 883 $ | 58 035 $ | 54 437 € (59 826 $) |
| 2026-11-21 16:00 | 59 826 $ | 60 332 $ | 59 657 $ | 54 806 € (60 231 $) |
| 2026-11-21 20:00 | 60 231 $ | 60 443 $ | 59 859 $ | 54 673 € (60 086 $) |
| 2026-11-22 00:00 | 60 086 $ | 60 218 $ | 58 997 $ | 53 891 € (59 226 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-22)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,94 | 0,83 | 68 % | 1,54 | 1,26 |
| IREN | 1,42 | 0,50 | 25 % | 1,02 | 1,15 |
| CleanSpark (CLSK) | 1,25 | 0,47 | 22 % | 1,21 | 1,33 |
| Solana (SOL) | 1,30 | 0,85 | 72 % | 1,22 | 1,17 |
| Microsoft | 0,35 | 0,47 | 22 % | 0,24 | 0,45 |
| Meta | 0,51 | 0,42 | 18 % | 0,19 | 0,19 |
| Amazon | 0,39 | 0,43 | 18 % | 0,19 | 0,36 |
| Monday.com | 0,25 | 0,14 | 2 % | 0,22 | 0,22 |
| Nasdaq-100 | 0,44 | 0,63 | 40 % | 0,23 | 0,27 |
| S&P 500 | 0,29 | 0,64 | 40 % | 0,16 | 0,21 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-21 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-20 | 2 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-21 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-22 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-21 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-22 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-20 | 2 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-21 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-22 00:00 | 0.12 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-22 05:00 | 0.03 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-21 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-22 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-22 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-20 | 2 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
