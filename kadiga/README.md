# Reconnaissance d'entités nommées propres à Djibouti (Binôme 5)

Projet de fin de module – TALN, Master 2 IAMD, Université de Djibouti (novembre 2026).

**Question.** Un modèle NER français généraliste (spaCy `fr_core_news_sm`) reconnaît-il les institutions,
lieux, formations, dates et personnes propres à Djibouti, et un enrichissement local (règles + lexique)
l'améliore-t-il ?

## Structure du projet

```
ner_djibouti_binome5/
├── README.md                        ce fichier
├── requirements.txt                 dépendances
├── TP_NER_Djibouti_Binome5.ipynb    notebook principal (Étapes 1 à 10, style des TP)
├── data/
│   ├── raw/SOURCES.md               provenance des textes (URL, licence, date)
│   └── corpus/
│       ├── corpus_annote.csv        SOURCE modifiable : une phrase par ligne, annotation [texte|ETIQUETTE]
│       ├── sentences.csv            généré : phrases + split (train/val/test, 60/20/20 par blocs)
│       ├── entities.csv             généré : une ligne par entité (start, end, label)
│       └── DATA_CARD.md             guide d'annotation, découpage, limites
├── src/build_dataset.py             corpus_annote.csv -> sentences.csv / entities.csv (+ vérifications)
├── tests/test_corpus.py             tests automatiques du corpus
├── results/                         tableau_comparatif.csv, erreurs_par_etiquette.csv, erreurs_analysees.csv, lexique_local.csv, courbe_apprentissage.csv
├── figures/                         graphiques (P/R/F1, matrice de confusion…)
├── rapport/                         rapport de 6 à 8 pages
└── slides/                          8 à 10 diapositives
```

## Installation

```bash
python -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```

## Reproduction

```bash
python src/build_dataset.py        # régénère sentences.csv et entities.csv (60/20/20 par blocs), affiche les statistiques
python -m pytest -q                # tests automatiques du corpus
jupyter notebook TP_NER_Djibouti_Binome5.ipynb    # exécuter de haut en bas ("Run All")
```

La graine aléatoire est fixée à 42 (`SEED`). Le train construit le lexique et entraîne le modèle, la validation règle et arrête l'entraînement,
le test n'est utilisé qu'à la fin.

## Données

137 phrases, 331 entités : Wikipédia FR (CC BY-SA 4.0), rapports Hcéres (Université de Djibouti, licence LALT),
arrêtés du Journal officiel sur les masters, loi d'orientation de l'éducation et exemples du cours.
Découpage 60/20/20 par blocs : train 84 / val 26 / test 27 phrases. Détails : `data/raw/SOURCES.md`, `data/corpus/DATA_CARD.md`.
Aucune donnée personnelle.

## État d'avancement

| Élément | État |
|---|---|
| Corpus annoté, découpage train/val/test (60/20/20), fiche de données | fait (annotations à relire par le binôme) |
| Tests automatiques du corpus (12 tests) | fait |
| Systèmes A (spaCy), B (règles génériques), C (lexique du train), D (spaCy ré-entraîné) | code fait et exécuté, résultats dans `results/` |
| Analyse de ≥ 10 erreurs (système choisi sur la validation ; familles et impact préremplis ; colonnes « cause » et « amélioration ») | **à rédiger par vous** : `results/erreurs_analysees.csv` |
| Réponses aux questions d'analyse, synthèse, conclusion du notebook | **à rédiger par vous** |
| Démonstration, rapport, diapositives | à faire |

## Résultats (test, correspondance exacte, graine 42, une exécution)

| Système | P micro | R micro | F1 micro | F1 macro |
|---|---|---|---|---|
| A – spaCy seul | 0.400 | 0.441 | 0.420 | 0.296 |
| B – + règles génériques (baseline) | 0.438 | 0.676 | 0.532 | 0.470 |
| C – + lexique local (train) | 0.467 | 0.735 | 0.571 | 0.502 |
| D – spaCy ré-entraîné (train, arrêt sur val) | 0.576 | 0.721 | 0.641 | 0.536 |

Test de 68 entités seulement : écarts à interpréter avec prudence (voir limites).

## Limites connues

- Très petit corpus : 27 phrases et 68 entités en test ; PER : 4 exemples en test. Scores à forte variance.
- Le test est dominé par les arrêtés du Journal officiel (14 phrases sur 27), très gabaritiels.
- FORM : 4 exemples seulement dans le train (19 au total) : D n'apprend rien sur cette classe (F1 = 0).
- Annotations pré-remplies, à relire par le binôme ; extraits Hcéres-UD/loi à comparer à l'original.
