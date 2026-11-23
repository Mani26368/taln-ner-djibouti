# Données

Deux corpus **séparés** : La Nation (annoté par Mako) et le corpus de Kadiga (`corpus_kadiga/`). Ils ne sont jamais mélangés dans les évaluations.
Données publiques (articles de presse, textes officiels) ; pas de données personnelles.

## La Nation
Segments de 15 articles du journal *La Nation* (Djibouti), choisis de façon reproductible : dans chaque article, 14 segments régulièrement espacés
parmi ceux de 8 tokens ou plus (scripts `src/preparer_corpus.py`, `src/preparer_test2.py`, `src/preparer_test3.py`). Le corpus complet des articles
n'est pas dans le dépôt : seuls les segments utiles y sont.

| Fichier | Contenu |
|---|---|
| `corpus_ner.csv` | segments de `dev` et `test` (colonnes `id, titre, rubrique, url, date, fr, split`) |
| `corpus_test2.csv`, `corpus_test3.csv` | segments de `test2` et `test3` (mêmes colonnes) |
| `annotations.csv`, `annotations_test2.csv`, `annotations_test3.csv` | une ligne par entité : `id_segment, split, texte, entite, type, debut, fin, a_verifier, remarque` |

- **Positions** : `debut` et `fin` sont des positions en caractères dans le texte du segment (`fin` exclue) ; `texte[debut:fin] == entite`.
- **Types** : ORG, LOC, PER, DATE, FORMATION. Un segment sans entité n'a aucune ligne.
- **Annotation** : à la main, par Mako, en lisant le texte brut (aucun modèle n'a servi à annoter), avec `docs/guide_annotation.md`. Les cas incertains sont marqués `a_verifier = oui`.
- **Contrôle** : `python src/verifier_annotations.py [annotations.csv] [corpus.csv]` (position, type, doublons, chevauchements).

| Jeu | Articles | Segments | Entités (ORG / LOC / PER / DATE) | Rôle |
|---|---|---|---|---|
| `dev` | A01, A02, A08, A10, A12, A14 | 84 | 17 / 16 / 14 / 10 | a servi à écrire les règles 3a et 3b : score optimiste |
| `test` | A03, A11, A15 | 42 | 13 / 4 / 7 / 3 | lu en entier pendant l'annotation : score optimiste |
| `test2` | A07, A09, A13 | 42 | 6 / 6 / 1 / 3 | mesuré une fois, puis regardé |
| `test3` | A04, A05, A06 | 42 | 5 / 18 / 0 / 4 | annoté sans regarder aucune prédiction, mesuré une seule fois |

Aucune entité FORMATION dans La Nation.

## Limites
Jeux petits (de 16 à 57 entités), un seul annotateur, annotation faite par la personne qui a aussi écrit les règles, plusieurs cas de convention
(événements, mentions courtes, groupements d'États) qui pèsent sur les scores, et des sujets de `test3` éloignés de Djibouti.
