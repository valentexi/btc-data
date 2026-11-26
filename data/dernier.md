# Dernier relevé BTC (26/11/2026 12:17 UTC)

Produit automatiquement par `collecte.py`. Clôtures quotidiennes à minuit UTC (1 h à Paris en hiver).

## Prix (clôture du 2026-11-25)
- **Bitcoin : 55 220 € (60 384 $)**, EUR/USD 1,0935 (BCE)
- Variation : +1,1 % sur 1 jour, -4,1 % sur 7 jours, -24,5 % sur 30 jours
- 30 derniers jours : plus haut 74 888 € (81 890 $), plus bas 50 394 € (55 106 $)
- Volatilité réalisée sur 30 jours : 47 % par an

## Moyennes mobiles
| Moyenne | Niveau | Écart du prix |
|---|---|---|
| 50 jours | 68 710 € (75 135 $) | -19,6 % |
| 200 jours | 65 868 € (72 027 $) | -16,2 % |
| 200 semaines | 62 684 € (68 545 $) | -11,9 % |

## Dérivés et sentiment
- **Financement Kraken en direct** (relevé le 2026-11-26 à 12:17 UTC) : -0,0009 % par 8 h, **négatif : les shorts paient les longs** ; prévision pour l'heure suivante : 0,0064 % (positif : les longs paient les shorts) ; Deribit : 0,0001 %. C'est ce chiffre qui compte pour les conditions éliminatoires.
- Financement Kraken, moyenne de la journée du 2026-11-25 : 0,0069 % par 8 h (positif : les longs paient les shorts) ; moyenne sur 7 jours : 0,0056 % (positif : les longs paient les shorts)
- Intérêt ouvert sur le contrat Kraken : 2 164 BTC (relevé du 2026-11-26)
- Volatilité implicite (DVOL) : 52,3 le 2026-11-25
- Options Deribit, rapport puts/calls : 0,80 en positions ouvertes, 1,46 en volume sur 24 h (relevé du 2026-11-26)
- Échéance d'options la plus chargée : 2026-12-25, 164 807 BTC en positions ouvertes, « max pain » à 64 015 € (70 000 $)
- Fear & Greed : 11 le 2026-11-26, 10 sept jours plus tôt
- MVRV (prix divisé par le prix de revient moyen du réseau) : 1,14 le 2026-11-25

## Lecture mécanique (règles fixes de la méthode, sans jugement)
- **Biais mécanique à la clôture du 2026-11-25 : -3 sur 10** (structure du prix -2 · positionnement +1 · blockchain +0 · macro +0 · actifs risqués -2). Cinq familles sur sept, seuils fixes ; sans avantage démontré au backtest.
- Sept derniers jours : 11-19 -4, 11-20 -4, 11-21 -3, 11-22 -3, 11-23 -3, 11-24 -3, 11-25 -3
- Règles mécaniques suivies en papier : aucune active (S4 : biais ≤ −5 ; L7 : biais ≥ +5). Quand une règle est active, son plan est inscrit d'office dans `papier/plans_regles.csv` (signaux suivis depuis la clôture du 2026-11-15, une position à la fois par règle).

Supports majeurs (définition de la méthode), clôture du 2026-11-25 à 55 220 € (60 384 $) :

| Support | Niveau | Écart de la clôture | État en clôture journalière |
|---|---|---|---|
| Moyenne 200 semaines | 62 684 € (68 545 $) | -11,9 % | cassé le 2026-11-14 (12 j), pas repris |
| Moyenne 200 jours | 65 868 € (72 027 $) | -16,2 % | cassé le 2026-11-12 (14 j), pas repris |
| Plus bas des 90 jours précédents | 50 394 € (55 106 $) | +9,6 % | repris le 2026-11-21 |

- **Long de retournement : exclu** (aucun support majeur qui tient à moins de 3 % sous le prix).
- **Condition éliminatoire du short (support, financement, peur) : inactive** (posé sur un support majeur : non ; financement en direct négatif : oui ; peur extrême (≤ 20) : oui).

## Macro (dernières clôtures connues)
- Taux américain à 10 ans : 4,85 % (2026-11-25)
- Taux américain à 2 ans : 4,61 % (2026-11-25)
- Taux réel à 10 ans : 2,73 % (2026-11-25)
- VIX : 28,3 (2026-11-25)
- Nasdaq-100 : 26 047 points (2026-11-25)
- S&P 500 : 7 183 points (2026-11-25)
- Dollar (DXY) : 103,67 (2026-11-25)
- Brent : 94,6 $ (2026-11-25)

## Six dernières bougies de 4 heures terminées (heure de début, UTC ; Paris = UTC + 1 h en hiver)
| Début (UTC) | Ouverture | Plus haut | Plus bas | Clôture |
|---|---|---|---|---|
| 2026-11-25 12:00 | 58 553 $ | 58 848 $ | 57 208 $ | 53 275 € (58 256 $) |
| 2026-11-25 16:00 | 58 256 $ | 60 337 $ | 58 023 $ | 54 693 € (59 807 $) |
| 2026-11-25 20:00 | 59 807 $ | 60 487 $ | 59 720 $ | 55 220 € (60 384 $) |
| 2026-11-26 00:00 | 60 384 $ | 61 527 $ | 60 295 $ | 55 502 € (60 692 $) |
| 2026-11-26 04:00 | 60 692 $ | 61 042 $ | 60 295 $ | 55 278 € (60 446 $) |
| 2026-11-26 08:00 | 60 446 $ | 60 988 $ | 60 386 $ | 55 451 € (60 636 $) |

## Contrat perpétuel Kraken PF_XBTUSD (barème lu le 2026-11-26)
- Marge initiale 10,0 %, marge de maintenance 5,0 %, levier maximum x10.
- Frais : 0,050 % par ordre au marché, 0,020 % par ordre limite (premier palier).
- Liquidation estimée en marge isolée : long = entrée × (1 − 1/levier) ÷ 0,950 ; short = entrée × (1 + 1/levier) ÷ 1,050. Toujours comparer au prix de liquidation affiché par Kraken avant de valider un ordre.
- Kraken applique la marge **croisée par défaut** : choisir « isolée » avant d'ouvrir une position.

## Liens avec le Bitcoin (bêta : variation de l'actif quand le BTC bouge de 1 %)
| Actif | Bêta 90 jours | Corrélation 90 jours | Part expliquée par le BTC | Bêta 1 an | Bêta 1 an, jours de baisse du BTC |
|---|---|---|---|---|---|
| Strategy (MSTR) | 1,98 | 0,84 | 71 % | 1,56 | 1,28 |
| IREN | 1,72 | 0,56 | 32 % | 1,05 | 1,17 |
| CleanSpark (CLSK) | 1,39 | 0,53 | 28 % | 1,21 | 1,36 |
| Solana (SOL) | 1,27 | 0,86 | 74 % | 1,23 | 1,20 |
| Microsoft | 0,33 | 0,46 | 21 % | 0,24 | 0,45 |
| Meta | 0,57 | 0,46 | 21 % | 0,21 | 0,20 |
| Amazon | 0,40 | 0,44 | 19 % | 0,18 | 0,35 |
| Monday.com | 0,26 | 0,15 | 2 % | 0,22 | 0,21 |
| Nasdaq-100 | 0,51 | 0,66 | 43 % | 0,24 | 0,27 |
| S&P 500 | 0,33 | 0,65 | 43 % | 0,17 | 0,20 |

Lecture : 100 € d'un actif de bêta 1,5 pèsent comme 150 € de Bitcoin. Un ETF Nasdaq à levier x2 pèse environ deux fois le bêta du Nasdaq-100. La « part expliquée » dit quelle fraction des mouvements de l'actif vient du BTC : le reste n'est pas couvert par un short BTC.

## État et fraîcheur des sources
**Relevé complet : toutes les sources sont à jour.**

| Source | Nature | Lancement | Dernière donnée | Âge | Fraîcheur | Remarque |
|---|---|---|---|---|---|---|
| prix | historique | ok | 2026-11-25 | 1 j | à jour | (Coinbase) |
| eurusd | différée | ok | 2026-11-25 | 1 j | à jour | (BCE) |
| financement | historique | ok | 2026-11-25 | 1 j | à jour | (Kraken Futures) |
| derives | instantanée | ok | 2026-11-26 | 0 j | à jour | (Kraken Futures, Deribit) |
| dvol | historique | ok | 2026-11-25 | 1 j | à jour | (Deribit) |
| peur_avidite | historique | ok | 2026-11-26 | 0 j | à jour | (alternative.me) |
| macro | différée | ok | 2026-11-25 | 1 j | à jour | (Trésor américain, CBOE, Yahoo Finance) |
| onchain | différée | ok | 2026-11-25 | 1 j | à jour | (Coin Metrics, non disponibles : cap_realisee_usd) |
| h4 | historique | ok | 2026-11-26 08:00 | 0.01 j | à jour | (Coinbase, heures agrégées) |
| h1_kraken | historique | ok | 2026-11-26 11:00 | 0.01 j | à jour | (Kraken Futures, contrat PF_XBTUSD) |
| financement_deribit | historique | ok | 2026-11-25 | 1 j | à jour | (Deribit) |
| options | instantanée | ok | 2026-11-26 | 0 j | à jour | (Deribit) |
| contrat_kraken | instantanée | ok | 2026-11-26 | 0 j | à jour | (Kraken Futures, barème Europe, particuliers) |
| actifs | différée | ok | 2026-11-25 | 1 j | à jour | (Yahoo Finance) |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable). À relever par recherche web ; à défaut, la famille concernée est notée sur ce qui reste, sans jamais dépasser 0 dans le sens du trade envisagé.

Voir aussi : `rapport/backtest.md` (ce que les règles ont donné sur le passé) et `rapport/papier.md` (suivi des plans en mode papier).
