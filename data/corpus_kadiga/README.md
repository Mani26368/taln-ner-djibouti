# Corpus de Kadiga

Phrases de textes publics en français (Wikipédia, Journal officiel, rapports Hcéres, loi d'orientation de l'éducation, exemples de cours), annotées par Kadiga
en ORG, LOC, PER, DATE et FORM (formation). Provenance, licences et guide d'annotation détaillés : `DATA_CARD.md` et `SOURCES.md`.

| Fichier | Rôle |
|---|---|
| `corpus_annote.csv` | source annotée à la main (une phrase par ligne) |
| `sentences.csv` | phrases et jeu (`train`, `val`, `test`), découpage par blocs, graine 42 |
| `entities.csv` | une ligne par entité : `id, split, start, end, label, text` |
| `tableau_comparatif_kadiga.csv` | résultats de Kadiga sur son propre test : référence de contrôle de `src/systemes_kadiga.py` |

- **Taille** : 84 phrases en `train`, 26 en `val`, 27 en `test` ; 207, 56 et 68 entités.
- **Étiquette FORM** : s'appelle `FORMATION` dans les corpus de La Nation.
- Ce corpus a ses propres règles d'annotation : ne pas comparer ses scores à ceux de La Nation.
- Les fichiers viennent du travail de Kadiga (branche `kadiga`) ; ils n'ont pas été modifiés.
