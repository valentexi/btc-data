# btc-data

Collecte de données sur le Bitcoin, backtest de règles long et short, et suivi de plans en mode papier.
Outil d'analyse uniquement : **aucun ordre n'est passé**, aucune clé d'API, aucune donnée personnelle.

## Ce que fait le dépôt
GitHub Actions lance les scripts tout seul :

| Quand (UTC) | Quoi |
|---|---|
| 4 h 47 chaque jour | Relevé complet (`collecte.py`), suivi papier (`papier.py`), backtest (`backtest.py`) |
| 0 h 12, 8 h 12, 12 h 12, 16 h 12, 20 h 12 | Mise à jour légère après chaque clôture de bougie de 4 heures : relevé et suivi papier |
| À chaque modification du code ou de `papier/plans.csv` | Tests, puis tout le reste |

## Où regarder
| Fichier | Contenu |
|---|---|
| `data/dernier.md` | Relevé du moment : prix en euros (dollars entre parenthèses), moyennes mobiles, bougies de 4 heures, financement, options, macro, contrat Kraken, bêtas, fraîcheur de chaque source |
| `rapport/backtest.md` | Ce que les règles et les configurations ont donné sur le passé, avec intervalles de confiance |
| `rapport/papier.md` | Suivi des plans en mode papier, comparé à des stratégies de référence |
| `data/etat.json` | État et fraîcheur de chaque source au dernier lancement |

## Données collectées
| Fichier | Source | Nature |
|---|---|---|
| `btc_jour.csv` | Coinbase (secours : Kraken) | Clôtures journalières depuis 2017 |
| `h4/btc_h4_AAAA-MM.csv` | Coinbase, heures agrégées (secours : Kraken) | Bougies de 4 heures depuis 2017 |
| `eurusd.csv` | Banque centrale européenne | Taux de référence, différé |
| `financement_kraken.csv` | Kraken Futures | Financement réel du contrat perpétuel, un an glissant puis cumulé |
| `financement_deribit.csv` | Deribit | Financement réel du contrat perpétuel depuis 2019 |
| `derives_instantane.csv` | Kraken Futures, Deribit | Relevé instantané : intérêt ouvert, financement, options (puts/calls, échéance principale) |
| `kraken_contrat.csv` | Kraken Futures | Marges, levier maximum et frais réels du contrat PF_XBTUSD |
| `dvol.csv` | Deribit | Volatilité implicite depuis 2021 |
| `peur_avidite.csv` | alternative.me | Fear & Greed depuis 2018 |
| `macro.csv` | Trésor américain, CBOE, Yahoo Finance | Taux, VIX, Nasdaq-100, S&P 500, DXY, Brent |
| `onchain.csv` | Coin Metrics, offre gratuite | MVRV, plateformes, activité |
| `actifs.csv`, `betas.csv` | Yahoo Finance | Panier d'actifs liés au Bitcoin et leurs bêtas |

Non collecté : flux des ETF Bitcoin et liquidations (aucune source gratuite fiable).

## Règles du backtest
- Règles et paramètres fixés à l'avance, rien n'est optimisé sur le passé.
- Signal à la clôture d'une bougie, entrée à l'ouverture de la suivante, sorties suivies en 4 heures.
- Stop et objectif dans la même bougie : on compte le stop.
- Frais et glissement déduits. Financement réel quand il existe, jamais supposé.
- Trades regroupés par épisodes ; intervalles de confiance par bootstrap de blocs.
- Tests hors échantillon : deux moitiés, puis sélection année par année.
- Un backtest ne valide rien : au mieux, il désigne un candidat à confirmer en mode papier.

## Mode papier
`papier/plans.csv` contient les plans, écrits avant que le marché ne tranche (format décrit en tête de `papier.py`).
`papier.py` rejoue les bougies de 4 heures et calcule le résultat net de chaque plan.
Critère de passage en réel affiché dans `rapport/papier.md` : 30 plans clos, résultat positif avec un intervalle
à 95 % entièrement positif, et mieux que les références.

## Lancer à la main
Onglet **Actions**, « Collecte BTC », bouton **Run workflow**. Sur un ordinateur :
```
pip install -r requirements.txt
python tests/test_local.py   # tests sans réseau
python collecte.py && python papier.py && python backtest.py
```
