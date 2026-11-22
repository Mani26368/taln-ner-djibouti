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
1. **Notebook final (à lire en premier)** : `notebooks/NER_Djibouti_final.ipynb`. Le lire ou l'exécuter de haut en bas
   (environ une minute). Choisir comme noyau l'environnement `.venv` (celui où `requirements.txt` et `fr_core_news_sm` sont installés).
   Il lit les résultats dans `results/` ; l'interrupteur `RELANCER = False` évite de ré-entraîner le modèle D de Kadiga.
2. Notebooks de travail (historique, non modifiés) :
   - `travaux_individuels/mako_ner_baseline.ipynb` : le notebook de Mako (baseline, règles 3a, filtres 3b, essais 3c) ;
   - `kadiga/TP_NER_Djibouti_Binome5.ipynb` : le notebook de Kadiga (corpus Wikipédia / Journal officiel, systèmes A à D).
3. Évaluer : `python src/evaluate.py` (démonstration du calcul précision / rappel / F1, exact et tolérant).

## Lancer la démo

Une application Streamlit (dossier `demo/`) permet d'essayer le système sur un texte, sans rien savoir de la programmation.
Elle sert aussi de démonstration de 3 minutes. **C'est un prototype : il peut se tromper.**

Depuis un dossier neuf (Windows : remplacer `source .venv/bin/activate` par `.venv\Scripts\activate`) :

```bash
git clone https://github.com/Mani26368/taln-ner-djibouti.git
cd taln-ner-djibouti
git checkout mako              # tant que la démo n'est pas fusionnée dans main
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
streamlit run demo/app.py
```

Il faut internet **seulement pour l'installation**. Ensuite l'application fonctionne hors ligne (aucune police ni image en ligne ;
les statistiques d'usage de Streamlit sont désactivées dans `.streamlit/config.toml`). Le navigateur s'ouvre, et l'adresse locale est affichée dans le terminal.

**Démarrage.** Le système par défaut, **3a+3b** (nos règles locales, version gelée), ne demande aucun entraînement :
la page d'accueil est prête 13,7 s à 18,4 s après la commande (3 essais ; sur d'autres démarrages mesurés pendant les essais,
de 15,3 s à 37,1 s quand l'ordinateur était chargé).

**Première utilisation du modèle D : attendre environ 30 secondes.** Le modèle D (le modèle ré-entraîné de Kadiga, à choisir dans
« Options avancées ») n'est enregistré nulle part dans Git (un modèle spaCy est trop gros) : la première fois qu'on le choisit, il s'entraîne.
L'application affiche un message d'attente (« Première utilisation du modèle D : il est en cours d'entraînement… »).
Il est ensuite gardé dans `demo/.cache/` (dossier ignoré par Git, environ 26 Mo).
Temps mesurés sur l'ordinateur de Mako (Windows) pour ce choix de D : première utilisation 25,2 s et 36,0 s (2 essais) ;
utilisations suivantes 8,4 s, 1,8 s et 1,8 s (3 essais ; le premier incluait une lecture du disque à froid).
Ces durées varient d'un ordinateur à l'autre.

- **Pages** (barre de gauche) : « Analyser un texte », « Catégories reconnues », « À propos ».
- **Systèmes** : **3a+3b** par défaut (règles réglées sur les articles du projet, moins fiable sur d'autres textes).
  « Options avancées » permet de choisir « D – modèle ré-entraîné (Kadiga) » ou « A – spaCy seul ». D trouve peu de dates sur nos
  segments de La Nation (les chiffres, lus dans `results/`, sont sur la page « Catégories reconnues »).
  La légende indique ce que le système PEUT produire, pas ce qu'il trouve toujours.
- **Apparence** : couleurs, titre, phrase d'accueil et exemples sont dans `demo/theme.py` (valeurs marquées « À REMPLACER »).
  `demo/maquette.png` ne sert que de référence visuelle : l'application ne l'utilise pas.
- **Plan B** (si la démo en direct échoue) : `python demo/enregistrer_essais.py` écrit les résultats réels des 3 systèmes sur 3 exemples
  dans `demo/essais_demo.txt` (déjà fourni). `python demo/tester_app.py` teste l'application et écrit `demo/test_application.txt`.

## Résultats
À compléter avec les vrais chiffres (tableau précision / rappel / F1 par approche et par type d'entité).

## Structure
```
notebooks/NER_Djibouti_final.ipynb   notebook final (à lire en premier)
travaux_individuels/                 notebook de travail de Mako
kadiga/                              travail de Kadiga (son notebook, son corpus, ses résultats)
data/                                corpus La Nation annotés (dev, test, test2, test3) + description
src/                                 code : évaluation exacte et tolérante, règles, systèmes de Kadiga, scripts de mesure
results/                             tous les résultats chiffrés (le notebook final les lit)
demo/                                application Streamlit (démo de 3 minutes) : voir « Lancer la démo »
docs/                                guide d'annotation, sujet et cours de référence
rapport/                             rapport (6 à 8 pages)
slides/                              diapositives (8 à 10)
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
