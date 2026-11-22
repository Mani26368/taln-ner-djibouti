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
Mako Mohamed Aden et Kadiga — M2 IAMD, Université de Djibouti.

---

# Guide pour Kadiga : ajouter ton notebook sur GitHub

Chacune travaille sur **sa propre branche** : Mako sur `mako`, Kadiga sur `kadiga`. Personne ne travaille directement sur `main`. À la fin, on rassemble tout dans `main`.

> Une branche, c'est ta copie de travail du projet. Tu peux y modifier des fichiers sans casser ceux de l'autre.

## Avant de commencer (une seule fois)
1. Avoir un compte GitHub et **accepter l'invitation** reçue par e-mail (« Mani26368 vous invite à collaborer »).
2. Avoir **Git** installé. Vérifier dans PowerShell : `git --version`.
3. Dire à Git qui tu es :
   ```powershell
   git config --global user.name "Kadiga"
   git config --global user.email "ton-email@exemple.com"
   ```

## Étape 1 — Récupérer le projet (une seule fois)
```powershell
git clone https://github.com/Mani26368/taln-ner-djibouti.git
cd taln-ner-djibouti
```

## Étape 2 — Passer sur ta branche
La branche `kadiga` est déjà créée par Mako.
```powershell
git checkout kadiga
```
Vérifier : `git branch` doit afficher `* kadiga`.

## Étape 3 — Ajouter tes fichiers
- Copier ton **notebook** (`.ipynb`) dans le dossier `notebooks/`.
- Copier tes **textes et annotations** dans `data/` (et compléter `data/README.md`).
- Avant d'enregistrer le notebook : dans Jupyter/Colab, faire **Exécuter toutes les cellules** pour que les résultats soient visibles.
- Ne pas mettre de mots de passe, de clés, ni de données personnelles.

## Étape 4 — Envoyer sur GitHub
Taper les commandes **une par une** (pas de `&&` dans PowerShell) :
```powershell
git status
git add notebooks data
git commit -m "Ajout du notebook NER et des données"
git push -u origin kadiga
```
La première fois, GitHub peut ouvrir une fenêtre de connexion : accepter.

## Étape 5 — Prévenir Mako
Envoyer un message « C'est poussé sur la branche kadiga ». Mako ouvre une **Pull Request** (`kadiga` vers `main`) sur GitHub pour rassembler les deux parties.

## Pour continuer à travailler plus tard
Toujours dans cet ordre :
```powershell
git checkout kadiga
git pull
```
puis modifier, puis refaire `git add`, `git commit`, `git push`.

## Si ça bloque
- « Permission denied » ou « 403 » : l'invitation n'est pas acceptée, ou Mako ne t'a pas encore ajoutée comme collaboratrice.
- « branch kadiga not found » : lancer d'abord `git fetch`, puis `git checkout kadiga`.
- Autre message d'erreur : copier-coller le message à Mako.
