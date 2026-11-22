# NER propre à Djibouti — Projet TALN (Binôme 5)

Master 2 IAMD — Université de Djibouti — Module TALN (Dr Houssein Ahmed Assowe) — Novembre 2026

## Question
Peut-on extraire automatiquement les institutions, lieux, formations, dates et personnes dans des textes français locaux (Djibouti) ?

## Approches comparées
| Approche | Description |
|---|---|
| Baseline | spaCy `fr_core_news_sm` + règles `EntityRuler` |
| Approche 2 | Lexique local enrichi (à compléter) |

## Données
À compléter : provenance, nombre de textes annotés, types d'entités, séparation, limites. Voir `data/README.md`.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```

## Reproduction
1. Ouvrir le notebook dans `notebooks/` et l'exécuter dans l'ordre.
2. Évaluer : `python src/evaluate.py` (démonstration du calcul précision / rappel / F1).

## Résultats
À compléter avec les vrais chiffres (tableau précision / rappel / F1 par approche et par type d'entité).

## Structure
```
data/        échantillon des données + description
notebooks/   notebook principal
src/         évaluation (precision, rappel, F1)
rapport/     rapport (6 à 8 pages)
slides/      diapositives (8 à 10)
docs/        sujet et cours de référence
```

## Auteures
Mako Mohamed Aden et sa binôme — M2 IAMD, Université de Djibouti.
