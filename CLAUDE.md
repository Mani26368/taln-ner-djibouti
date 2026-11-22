# Projet TALN — Binôme 5 : NER propre à Djibouti

## Contexte
- Master 2 IAMD, Université de Djibouti — module TALN (Dr Houssein Ahmed Assowe).
- Sujet : extraire institutions, lieux, formations, dates et personnes dans des textes français locaux.
- Baseline : spaCy NER (`fr_core_news_sm`) + règles `EntityRuler`.
- Approche 2 : enrichir le lexique local (ou petit jeu annoté).
- Évaluation : précision, rappel, F1 sur les entités (frontières ET type exacts).
- Extension : visualisation des entités (`displacy`).
- Dépôt final : lundi 23/11/2026 à 18h. Soutenance : mardi 24/11/2026.
- Le sujet complet est dans `docs/sujet_projets_binomes.pdf`, le cours dans `docs/cours_S4_spacy_ner.pdf`.

## Répartition
- Le notebook (code principal) est fait par ma binôme : ne pas le réécrire, le lire et l'expliquer.
- Moi (Mako) : dépôt GitHub, README, requirements, rapport (6 à 8 pages), slides (8 à 10), démo, analyse des erreurs.

## Façon de travailler
- Je veux **comprendre** chaque étape pour pouvoir l'expliquer au jury : avance étape par étape, explique en mots simples, courts, sans phrase ambiguë, avec un petit exemple.
- Attends mon accord avant de passer à l'étape suivante.
- Ne jamais inventer de résultats ni de chiffres : tout chiffre vient d'une exécution réelle. Si quelque chose manque, le dire.
- Données : publiques, synthétiques ou anonymisées uniquement (pas de données personnelles).
- Documenter le modèle spaCy utilisé (nom, version, langue, limites).
- Écrire en français ; féminin pour me désigner.

## Git
- **Pas de lignes d'attribution Claude dans les commits** (pas de `Co-Authored-By`, pas de `Claude-Session`). Messages courts, en français ou en anglais simple.
- Une branche `mako` pour mon travail, puis Pull Request vers `main`.

## Livrables (rappel du prof)
1. Rapport 6 à 8 pages (intro, données, baseline, méthode améliorée, protocole, résultats, analyse d'erreurs, limites, références)
2. Notebook/scripts exécutables
3. README.md + requirements.txt
4. Échantillon de données + description
5. Tableau comparatif d'au moins 2 approches (dont la baseline)
6. Analyse qualitative d'au moins 10 erreurs
7. Démo de 2 à 4 minutes
8. 8 à 10 diapositives
