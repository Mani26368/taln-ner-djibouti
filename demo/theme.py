"""Apparence et textes de la démonstration. Kadiga : changez les valeurs marquées « À REMPLACER ».

Ce fichier ne contient AUCUN code d'analyse et AUCUN score : seulement des couleurs, des textes et des numéros d'exemples.
Les couleurs sont reprises de la maquette (demo/maquette.png). Aucune image n'est utilisée : tout est local (dégradés CSS).
"""

# ---------------------------------------------------------------------------------------------- textes
TITRE = "NER Djibouti"                                                                   # À REMPLACER
SOUS_TITRE = "Extraire facilement les informations clés de vos textes"                   # À REMPLACER
BANDEAU_TITRE = "Bienvenue sur NER Djibouti !"                                           # À REMPLACER
PHRASE_ACCUEIL = ("Collez un texte et découvrez automatiquement les personnes, lieux, "
                  "organisations et plus encore.")                                       # À REMPLACER
PIED_BARRE_LATERALE = "Prototype de projet TALN"                                         # À REMPLACER
FORMATION_PIED = "Master 2 IAMD"                                                         # À REMPLACER
AVERTISSEMENT = "Prototype de projet TALN – peut se tromper."                            # À REMPLACER

# ---------------------------------------------------------------------------------------------- couleurs
COULEURS = {                                                                             # À REMPLACER
    "fond_page": "#F3F7FC",
    "texte": "#14213D",             # texte sombre (sur fond clair ou pastel)
    "titre": "#14306E",
    "barre_haut": "#0D2B6B",        # barre latérale : dégradé du haut vers le bas
    "barre_bas": "#1A4BA3",
    "barre_texte": "#FFFFFF",
    "menu_actif": "#1F5FD6",
    "bouton": "#1D4FC2",
    "bouton_fin": "#2A63D6",
    "bouton_texte": "#FFFFFF",
    "bandeau_debut": "#DCEBFB",
    "bandeau_fin": "#BBD6F5",
    "carte_fond": "#FFFFFF",
    "carte_bord": "#D5E1F1",
    "resultats_fond": "#EEF8F1",
    "resultats_bord": "#C9E5D2",
}

# Pour chaque type : fond pastel du texte surligné (texte sombre dessus) et couleur du point de la légende.
TYPES = {                                                                                # À REMPLACER
    "ORG": {"nom": "Organisation", "pluriel": "organisations", "fond": "#BFD8F7", "point": "#1F5FD6"},   # bleu
    "LOC": {"nom": "Lieu", "pluriel": "lieux", "fond": "#F9CFA3", "point": "#F28C28"},                 # orange
    "DATE": {"nom": "Date", "pluriel": "dates", "fond": "#DCC9F3", "point": "#9B51E0"},                # violet
    "PER": {"nom": "Personne", "pluriel": "personnes", "fond": "#BDE8C4", "point": "#2E9E4F"},         # vert
    "FORMATION": {"nom": "Formation", "pluriel": "formations", "fond": "#F7C4DA", "point": "#E0508F"},  # rose
}

# ---------------------------------------------------------------------------------------------- exemples (vrais textes)
# Numéros de segments du corpus La Nation (data/corpus_*.csv). Le texte est lu dans le corpus : rien n'est inventé.
# Règles de choix (écrites avant de regarder les segments), en ordre du corpus (corpus_ner, test2, test3) :
#   1 = un segment avec une DATE, un lieu et une organisation que le système par défaut (3a+3b) trouve entièrement
#       (A14_S001, suggéré ; il montre les trois couleurs, A12_S001 n'en montre que deux) ;
#   2 = premier segment suivant avec au moins 2 entités réelles dont des personnes, où D est entièrement correct (A12_S005) ;
#   3 = premier segment avec au moins 2 entités réelles où le système par défaut (3a+3b) se trompe (A03_S002).
EXEMPLES = [                                                                             # À REMPLACER
    ("A14_S001", "Un extrait avec une date, un lieu et une organisation"),
    ("A12_S005", "Un extrait avec des personnes"),
    ("A03_S002", "Un extrait où le système par défaut se trompe"),
]

# Un exemple par catégorie (page « Catégories reconnues »).
#   (identifiant du segment, texte de l'entité) pour La Nation : l'entité doit exister dans les annotations du dépôt.
#   FORMATION : La Nation n'en contient aucune ; l'exemple vient du corpus de Kadiga (kadiga/data/corpus).
EXEMPLES_CATEGORIES = {                                                                  # À REMPLACER
    "ORG": ("A03_S001", "Fédération djiboutienne de football"),
    "LOC": ("A14_S011", "Tadjourah"),
    "PER": ("A02_S014", "Radwan Abdillahi Bahdon"),
    "DATE": ("A02_S001", "lundi 5 octobre"),
    "FORMATION": ("ENS-02", "Master IAMD"),      # corpus de Kadiga
}

# Définitions simples (reprises du guide d'annotation, docs/guide_annotation.md).
DEFINITIONS = {                                                                          # À REMPLACER
    "ORG": "une institution, un ministère, une fédération, une entreprise, une organisation",
    "LOC": "un pays, une ville, un quartier, une localité, un site nommé",
    "PER": "une personne, désignée par son nom propre (sans son titre)",
    "DATE": "une date ou un moment repéré dans le calendrier",
    "FORMATION": "un diplôme, un master, une filière",
}

# ---------------------------------------------------------------------------------------------- notes sur les systèmes
NOTE_3A3B = "règles réglées sur les articles du projet, moins fiable sur d'autres textes"          # À REMPLACER

# ---------------------------------------------------------------------------------------------- page « À propos »
A_PROPOS = {                                                                             # À REMPLACER
    "Nom": "NER Djibouti",
    "Domaine": "Traitement automatique des langues (TALN)",
    "Objectif": ("Montrer comment un programme peut repérer, dans un texte français, les personnes, les lieux, "
                 "les organisations, les dates et les formations."),
    "Cadre": "Master 2 IAMD – Université de Djibouti",
    "Technologies": "Python, spaCy, Streamlit",
    "Projet": "Binôme 5 : Mako et Kadiga",
}
