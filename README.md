# NER propre à Djibouti — Projet TALN (Binôme 5)

Master 2 IAMD — Université de Djibouti — Module TALN (Dr Houssein Ahmed Assowe) — Novembre 2026

## Question
Peut-on extraire automatiquement les institutions, lieux, personnes, dates et formations dans des textes français locaux (Djibouti) ?
On compare une baseline (spaCy seul) à plusieurs façons de l'adapter, avec une évaluation exacte (début, fin ET type) et une évaluation tolérante.

## Approches comparées
| Approche | Description | Auteure |
|---|---|---|
| **A** (baseline) | spaCy `fr_core_news_sm` seul | commune |
| **B** | A + `EntityRuler` à règles génériques | Kadiga |
| **C** | B + lexique local construit sur le train de son corpus | Kadiga |
| **D** | NER de spaCy ré-entraîné sur son corpus | Kadiga |
| **3a** | A + règles locales (`EntityRuler`, titre + nom) écrites sur le dev | Mako |
| **3b** | 3a + filtres appliqués après spaCy, selon le guide d'annotation | Mako |
| **3c** | essais d'amélioration (modèles `md` et `lg`, règle « Djibouti », année seule, noms d'habitants) : **aucun retenu**, donc 3c = 3a+3b (`results/essais_3c.csv`) | Mako |

## Données
- **La Nation** (`data/`) : segments de 15 articles de presse du journal *La Nation* (Djibouti), annotés à la main avec `docs/guide_annotation.md`,
  répartis en 4 jeux : `dev`, `test`, `test2`, `test3`. Rôle de chaque jeu et format des fichiers : `data/README.md`.
- **Corpus de Kadiga** (`data/corpus_kadiga/`) : phrases de textes publics (Wikipédia, Journal officiel, rapports Hcéres). Description : `data/corpus_kadiga/README.md`.
- Données publiques seulement ; pas de données personnelles. Les deux corpus ne sont **jamais mélangés** dans les évaluations.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```
Sous Windows, la variante PowerShell sans activer le venv et la précaution sur les chemins trop longs sont dans « Lancer la démo » ci-dessous.

## Reproduction
1. **Notebook final** : `notebooks/NER_Djibouti_final.ipynb`. Le lire ou l'exécuter de haut en bas (environ une minute). Choisir comme noyau
   l'environnement `.venv`. Il importe le code de `src/` et lit les résultats dans `results/` ; l'interrupteur `RELANCER = False`
   évite de ré-entraîner le modèle D de Kadiga.
2. **Les résultats** de `results/` ont été produits par les scripts de `src/` :

   | Script | Rôle |
   |---|---|
   | `src/evaluate.py` | score exact et score tolérant (précision, rappel, F1) |
   | `src/regles_locales.py` | règles 3a et filtres 3b (version gelée) |
   | `src/regles_3c.py`, `src/essais_3c.py` | essais 3c |
   | `src/systemes_kadiga.py` | systèmes A, B, C, D de Kadiga, repris à l'identique |
   | `src/evaluer_lanation.py` | systèmes de Kadiga sur La Nation |
   | `src/mesurer_test2.py`, `src/mesurer_test3.py`, `src/scores_dev_test1.py` | mesures sur test2, test3, dev et test |
   | `src/preparer_*.py`, `src/verifier_annotations.py` | sélection des segments et contrôle des annotations |

   Les scripts `preparer_*.py` partent du corpus complet des articles, qui n'est **pas** dans le dépôt (seuls les segments utiles y sont).

## Lancer la démo

**Repère Djibouti** est une application Streamlit (dossier `demo/`) : on colle un texte français et elle surligne les personnes, lieux,
organisations et dates. Elle sert aussi de démonstration de 3 minutes. Son nom technique est « reconnaissance d'entités nommées (NER) ».
**C'est un prototype : il peut se tromper.**

**Depuis un dossier neuf, Windows PowerShell, sans activer le venv** (variante la plus fiable) :

```powershell
git clone https://github.com/Mani26368/taln-ner-djibouti.git
cd taln-ner-djibouti
git checkout mako              # tant que la démo n'est pas fusionnée dans main
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m spacy download fr_core_news_sm
.venv\Scripts\python.exe -m streamlit run demo/app.py
```

Si on préfère activer le venv et que PowerShell répond « l'exécution de scripts est désactivée sur ce système » :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass     # valable seulement pour cette fenêtre
.venv\Scripts\Activate.ps1
streamlit run demo/app.py
```

**macOS / Linux** : `source .venv/bin/activate`, puis `pip install -r requirements.txt`, `python -m spacy download fr_core_news_sm`
et `streamlit run demo/app.py`.

> **Windows : « No such file or directory » pendant `pip install`.** Windows limite les chemins à 260 caractères et Jupyter
> (dans `requirements.txt`) a des fichiers aux chemins très longs. Il faut alors cloner le projet dans un dossier au chemin court
> (par exemple `C:\taln`) ou activer les chemins longs de Windows. Constaté lors du test depuis un clone neuf.

Il faut internet **seulement pour l'installation**. Ensuite l'application fonctionne hors ligne (aucune police ni image en ligne ;
les statistiques d'usage de Streamlit sont désactivées dans `.streamlit/config.toml`, qui masque aussi le bouton « Deploy » et le menu).
Le navigateur s'ouvre, et l'adresse locale est affichée dans le terminal.

**Démarrage.** Le système par défaut, **3a+3b** (nos règles locales, version gelée), ne demande aucun entraînement :
la page d'accueil est prête 14,0 s à 24,6 s après la commande (3 essais dédiés : 24,6 s, 15,2 s et 14,0 s ; cinq autres démarrages
mesurés pendant les essais de D : de 15,2 s à 23,6 s).

**Première utilisation du modèle D : attendre environ 30 secondes.** Le modèle D (le modèle ré-entraîné de Kadiga, à choisir dans
« Options avancées ») n'est enregistré nulle part dans Git (un modèle spaCy est trop gros) : la première fois qu'on le choisit, il s'entraîne.
L'application affiche un message d'attente (« Première utilisation du modèle D : il est en cours d'entraînement… »).
Il est ensuite gardé dans `demo/.cache/` (dossier ignoré par Git, environ 26 Mo).
Temps mesurés sur l'ordinateur de Mako (Windows) pour ce choix de D : première utilisation 27,4 s et 23,5 s (2 essais) ;
utilisations suivantes 2,5 s, 1,9 s et 1,9 s (3 essais). Ces durées varient beaucoup d'un ordinateur et d'un moment à l'autre.

- **Pages** (barre de gauche) : « Analyser un texte », « Catégories reconnues », « À propos ».
- **Systèmes** : **3a+3b** par défaut (règles réglées sur les articles du projet, moins fiable sur d'autres textes).
  « Options avancées » permet de choisir « D – modèle ré-entraîné (Kadiga) » ou « A – spaCy seul ». D trouve peu de dates sur nos
  segments de La Nation (les chiffres, lus dans `results/`, sont sur la page « Catégories reconnues »).
  La légende indique ce que le système PEUT produire, pas ce qu'il trouve toujours.
- **Apparence** : les couleurs, le titre et les textes sont dans `demo/theme.py` (valeurs marquées « À REMPLACER ») ;
  la mise en forme (hauteur du bandeau, tailles de police, couleur du bouton) est dans `demo/style.css`, bloc « RÉGLAGES » en haut du fichier.
  Une image facultative `demo/assets/bandeau.jpg` est utilisée si elle existe (avec le dégradé par-dessus) ; son crédit s'écrit dans `demo/theme.py`.
  `demo/maquette.png` ne sert que de référence visuelle : l'application ne l'utilise pas.
- **Plan B** (si la démo en direct échoue) : `python demo/enregistrer_essais.py` écrit les résultats réels des 3 systèmes sur 3 exemples
  dans `demo/essais_demo.txt` (déjà fourni). `python demo/tester_app.py` teste l'application et écrit `demo/test_application.txt`.

## Résultats
Tous les chiffres sont dans `results/` et sont affichés, jeu par jeu, dans la section 6 du notebook final.
Le jeu `test3` (articles jamais regardés avant la mesure) est la seule mesure honnête ; les autres jeux ont servi à régler ou ont été regardés.
Le surapprentissage de 3a+3b est étudié dans la section 8 du notebook.

## Structure
```
README.md, requirements.txt, .gitignore
notebooks/NER_Djibouti_final.ipynb   notebook final (à lire en premier)
data/                                corpus La Nation + annotations ; data/corpus_kadiga/ : corpus de Kadiga
src/                                 code : évaluation exacte et tolérante, règles, systèmes de Kadiga, scripts de mesure
results/                             tous les résultats chiffrés (le notebook final les lit)
demo/                                application Streamlit « Repère Djibouti » (démo de 3 minutes)
docs/                                guide d'annotation, sujet et cours de référence
.streamlit/config.toml               configuration de la démo
```
Le travail individuel (notebooks de Mako et de Kadiga) reste dans l'historique et dans les branches `mako` et `kadiga`.

## Auteures
Mako Mohamed Aden et Kadiga — M2 IAMD, Université de Djibouti.
