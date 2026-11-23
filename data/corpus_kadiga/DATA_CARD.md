# Fiche de données – NER Djibouti (Binôme 5, TALN M2 IAMD)

## Fichiers
| Fichier | Rôle |
|---|---|
| `corpus_annote.csv` | **Source modifiable** : une ligne par phrase, annotation en ligne `[texte|ETIQUETTE]`. C'est ici qu'on corrige. |
| `sentences.csv` | Généré : `id, split, source, section, bloc, text` |
| `entities.csv` | Généré : une ligne par entité (`id, split, start, end, label, text`), lisible dans Excel |

Régénération : `python src/build_dataset.py` (ne pas modifier `sentences.csv` ni `entities.csv` à la main).

## Provenance (137 phrases, 331 entités)
| Source | Phrases | Licence / statut |
|---|---|---|
| Wikipédia FR, article « Djibouti » (WP-Djibouti) | 72 | CC BY-SA 4.0 |
| Rapport d'évaluation Hcéres de l'Université de Djibouti, 2019 (HCERES-UD-2019) | 21 | rapport public, courtes citations |
| Rapport Hcéres, licence LALT de l'IUT Tertiaire, 2022 (HCERES-LALT-IUT-2022) | 16 | rapport public, courtes citations |
| Arrêtés du Journal officiel de Djibouti sur les masters, 2026 (JO-Djibouti-Arretes-Masters) | 14 | texte officiel |
| Wikipédia FR, « Université de Djibouti » (WP-Univ-Djibouti) | 5 | CC BY-SA 4.0 |
| Exemples fournis par l'enseignant, TP4 et TP9-10 (Enseignant-TP) | 4 | matériel de cours (phrases synthétiques) |
| Loi d'orientation de l'éducation (Loi-orientation-education) | 3 | texte officiel |
| Wikipédia FR, « Lac Assal » (WP-Lac-Assal) | 2 | CC BY-SA 4.0 |

Aucune donnée personnelle ; les personnes citées sont des personnalités publiques ou des signataires de documents officiels publics.

**À vérifier avant le dépôt** : les phrases Hcéres-UD, loi et « Université de Djibouti » ont été récupérées par un outil d'extraction automatique, pas copiées à la main : comparez-les aux documents originaux (URL dans `data/raw/SOURCES.md`).

## Découpage 60 / 20 / 20 (train / val / test)
Découpage **par blocs** (source + section, ou source entière pour les arrêtés du Journal officiel qui suivent un même gabarit), jamais phrase par phrase : les phrases d'un même document partagent leurs entités, un tirage au hasard ferait fuiter le train vers le test. Les blocs sont affectés par une recherche aléatoire à graine fixe (42) qui vise 60/20/20 et exige au moins 3 à 5 entités de chaque classe (FORM comprise) en validation et en test.

| split | phrases | ORG | LOC | PER | DATE | FORM | total |
|---|---|---|---|---|---|---|---|
| train | 84 (61 %) | 51 | 83 | 14 | 55 | 4 | 207 |
| val | 26 (19 %) | 27 | 8 | 5 | 6 | 10 | 56 |
| test | 27 (20 %) | 28 | 13 | 4 | 18 | 5 | 68 |

- **train** : WP-Djibouti (Histoire, Géographie, Économie, Santé, Bases militaires), Hcéres-UD, exemples du TP.
- **val** : Hcéres-LALT, loi d'orientation, WP-Djibouti (Culture, Éducation), lac Assal.
- **test** : arrêtés du Journal officiel (14 phrases), WP-Djibouti (Politique, Forces armées), article « Université de Djibouti ».

Seules 9 des 47 entités distinctes de la validation et 11 des 57 du test apparaissent aussi dans le train : l'évaluation mesure surtout la généralisation.

Rôles : le **train** construit le lexique (système C) et entraîne le modèle (système D) ; la **validation** règle les règles et arrête l'entraînement ; le **test** n'est utilisé qu'une fois, à la fin.

## Guide d'annotation
- **ORG** : institutions, administrations, organisations internationales, partis, hôpitaux, établissements, facultés, forces armées, médias.
- **LOC** : pays, régions, villes, quartiers, reliefs, plans d'eau, golfes, infrastructures (port, camp), territoires historiques.
- **PER** : personnes nommées, sans titre ni fonction.
- **DATE** : dates complètes, jour + mois, mois + année, années, périodes nommées (« début des années 2000 »). Une plage « du 28 au 30 janvier 2019 » est une seule entité.
- **FORM** : intitulés de diplômes ou parcours, y compris leurs sigles (Licence appliquée Logistique et Transport, LALT, Master IAMD…).
- On annote l'expression la plus longue, sans entités imbriquées. Un nom générique sans nom propre n'est pas annoté.

## Limites connues
1. **Très petit corpus** : 27 phrases et 68 entités en test ; PER : 4 exemples en test, 5 en validation. Un seul exemple change le F1 de plusieurs points : les scores par classe sont indicatifs. Une validation croisée par blocs renforcerait les résultats.
2. **Test dominé par les arrêtés du Journal officiel** (14 phrases sur 27) : textes très gabaritiels (« Article 1er : Le présent Arrêté a pour objet… »), très différents du train, surtout encyclopédique. Les scores dépendent beaucoup de ce bloc.
3. **FORM rare dans le train** (4 entités sur 19) : D et C ne peuvent presque rien apprendre sur cette classe.
4. **Annotations pré-remplies par Claude** (corpus de départ et ajouts) : à relire entièrement par le binôme.
5. **Ambiguïtés voulues** : « port de Djibouti » (LOC ou ORG), « La Nation », « chambre de commerce », « Journal Officiel », « Centre de recherches », « Djibouti » ville ou pays, sigles FORM (LALT, TISL).
6. **Sources de style différent** (encyclopédie, rapport institutionnel, loi, arrêté) : utile pour tester la généralisation, mais les performances dépendent des blocs tombés en test.
