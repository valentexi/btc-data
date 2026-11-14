# btc-data

Collecte quotidienne de données sur le Bitcoin et backtest de règles simples, long et short.
Outil d'analyse uniquement : aucun ordre n'est passé, aucune clé d'API, aucune donnée personnelle.

## Ce que fait le dépôt
Chaque jour à 4 h 47 UTC, GitHub Actions lance deux scripts puis enregistre le résultat :

1. `collecte.py` télécharge les données et met à jour le dossier `data/`.
2. `backtest.py` rejoue les règles sur tout l'historique et écrit `rapport/backtest.md`.

Au premier lancement, tout l'historique disponible est téléchargé. Ensuite, seuls les derniers jours sont mis à jour.

## Où regarder
| Fichier | Contenu |
|---|---|
| `data/dernier.md` | Relevé du jour : prix en euros (dollars entre parenthèses), moyennes mobiles, financement, sentiment, macro |
| `rapport/backtest.md` | Résultats du backtest |
| `data/etat.json` | État de chaque source au dernier lancement |
| `rapport/trades.csv` | Tous les trades simulés |

## Données collectées
| Fichier | Source | Historique |
|---|---|---|
| `btc_jour.csv` | Coinbase (secours : Kraken) | depuis 2017 |
| `eurusd.csv` | Banque centrale européenne | depuis 2017 |
| `financement_kraken.csv` | Kraken Futures, contrat perpétuel | environ un an, puis s'allonge |
| `derives_instantane.csv` | Kraken Futures, Deribit | un relevé par jour à partir du premier lancement |
| `dvol.csv` | Deribit (volatilité implicite) | depuis 2021 |
| `peur_avidite.csv` | alternative.me (Fear & Greed) | depuis 2018 |
| `macro.csv` | FRED : taux américains, VIX, Nasdaq-100, S&P 500, dollar, Brent | depuis 2017 |
| `onchain.csv` | Coin Metrics, offre gratuite : MVRV et autres | depuis 2017 |

Non collecté : flux des ETF Bitcoin et carte des liquidations (pas de source gratuite fiable).

## Règles du backtest
- Règles fixées à l'avance, aucun réglage optimisé sur le passé.
- Signal à la clôture du jour J, entrée à l'ouverture du jour J+1.
- Stop et objectif touchés le même jour : on compte le stop.
- Frais, glissement et financement déduits.
- Résultat en R : 1 R = la perte prévue quand le stop saute.

## Lancer à la main
Onglet **Actions**, « Collecte BTC », bouton **Run workflow**.

Sur un ordinateur :
```
pip install -r requirements.txt
python tests/test_local.py   # tests sans réseau
python collecte.py
python backtest.py
```
