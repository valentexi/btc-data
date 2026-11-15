# btc-data

Collecte de données sur le Bitcoin, backtest de règles long et short, et suivi de plans en mode papier.
Outil d'analyse uniquement : **aucun ordre n'est passé**, aucune clé d'API, aucune donnée personnelle.

## Ce que fait le dépôt
GitHub Actions lance les scripts tout seul :

| Quand (UTC) | Quoi |
|---|---|
| 4 h 47 chaque jour | Relevé complet (`collecte.py`), suivi papier (`papier.py`), backtest (`backtest.py`) |
| Toutes les heures, à la minute 12 | Relevé, suivi papier et alertes. GitHub ne garantit pas ses horaires (retards, passages sautés) : un passage par heure rend l'outil insensible à un passage manqué ; le backtest est rattrapé s'il a plus de 26 heures |
| À la main, case « test_alerte » | Envoie une alerte de test (issue ouverte puis fermée) pour vérifier la notification sur le téléphone |
| À chaque modification du code ou de `papier/plans.csv` | Tests, puis tout le reste |

## Où regarder
| Fichier | Contenu |
|---|---|
| `data/dernier.md` | Relevé du moment : prix en euros (dollars entre parenthèses), moyennes mobiles, bougies de 4 heures, financement, options, macro, contrat Kraken, bêtas, fraîcheur de chaque source |
| `rapport/backtest.md` | Ce que les règles et les configurations ont donné sur le passé, avec intervalles de confiance |
| `rapport/papier.md` | Suivi des plans en mode papier, comparé à des stratégies de référence |
| `data/etat.json` | État et fraîcheur de chaque source au dernier lancement |
| Onglet **Issues** | Alertes : plans déclenchés, sorties, anomalies du registre |

## Données collectées
| Fichier | Source | Nature |
|---|---|---|
| `btc_jour.csv` | Coinbase (secours : Kraken) | Clôtures journalières depuis 2017 |
| `h4/btc_h4_AAAA-MM.csv` | Coinbase, heures agrégées (secours : Kraken) | Bougies de 4 heures depuis 2017 |
| `eurusd.csv` | Banque centrale européenne | Taux de référence, différé |
| `financement_kraken.csv` | Kraken Futures | Financement réel du contrat perpétuel, un an glissant puis cumulé |
| `financement_kraken_h.csv` | Kraken Futures | Financement heure par heure, 120 jours (conditions des plans) |
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
Deux registres de plans, rejoués heure par heure par `papier.py` (résultat net de frais et de glissement) :

| Fichier | Contenu |
|---|---|
| `papier/plans.csv` | Plans des analyses de Claude (format en tête de `papier.py`) |
| `papier/plans_regles.csv` | Plans des règles mécaniques S4 (short si biais ≤ −5) et L7 (long si biais ≥ +5), inscrits d'office par le robot : l'étalon que le jugement de Claude doit battre |
| `papier/annulations.csv` | Annulations (`id,annule_utc,motif`), jamais rétroactives |
| `papier/registre.csv` | Heure de première apparition et empreinte de chaque ligne (tenu par le robot) |
| `papier/alertes.csv` | Alertes déjà envoyées |
| `papier/scenarios.csv` | Prévisions à 7 jours de chaque analyse (trois probabilités, deux seuils de prix), confrontées au prix à l'échéance : justesse des probabilités dans `rapport/papier.md` |
| `papier/configurations.csv` | Facultatif : code de configuration du backtest d'un plan (`id,configuration`), pour le tableau par configuration |

Les plans créés depuis le 15 nov. 2026 à 19 h UTC sont rejoués sur les bougies d'une heure du **contrat perpétuel Kraken** (`data/h1_kraken.csv`) ; les plans antérieurs restent sur le prix au comptant de Coinbase.

Règles d'intégrité :
- une ligne enregistrée ne change plus ; une modification est signalée (rapport et alerte) et le plan sort du critère ;
- un plan de Claude ne compte au critère que s'il a été enregistré avant son entrée ;
- pour remplacer un plan : une annulation, puis un nouveau plan.

Critère de passage en réel (`rapport/papier.md`) : bilans à 30, 60 et 100 plans comptés clos, puis tous les 50 ;
un bilan est favorable si l'intervalle à 95 % (tirage par épisodes) est entièrement au-dessus de 0 R, avec au moins
10 épisodes de marché. Pas de conclusion entre deux bilans.

## Alertes
`alertes.py` ouvre une issue GitHub quand un plan de Claude se déclenche (ordres à vérifier, taille pour 2,50 € de
risque), la commente et la ferme à la sortie, et signale toute modification du registre. Notification sur le
téléphone avec l'appli GitHub (notifications activées pour ce dépôt). N'envoie rien hors de GitHub Actions.

## Lecture mécanique dans le relevé
`regles.py` calcule, pour `data/dernier.md` : le biais mécanique du jour (cinq familles du backtest), l'état des
supports majeurs (moyennes 200 semaines et 200 jours, plus bas des 90 jours précédents), la règle du long de
retournement et la condition éliminatoire du short (support, financement en direct, peur extrême).

## Lancer à la main
Onglet **Actions**, « Collecte BTC », bouton **Run workflow**. Sur un ordinateur :
```
pip install -r requirements.txt
python tests/test_local.py   # tests sans réseau
python collecte.py && python papier.py && python alertes.py && python backtest.py
```
