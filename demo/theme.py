"""Apparence et textes de « Repère Djibouti ». Kadiga : changez les valeurs marquées « À REMPLACER ».

Les COULEURS sont ici ; la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css, qui utilise ces couleurs.
Design sobre : fond clair, texte sombre, UNE seule couleur d'accent, police Inter (fichier local, voir demo/assets/fonts/).
Ce fichier ne contient AUCUN code d'analyse et AUCUN chiffre de performance : seulement des couleurs, des textes et des numéros d'exemples.
"""

# ---------------------------------------------------------------------------------------------- textes
TITRE = "Repère Djibouti"                                                                # À REMPLACER
PHRASE = "Repérez les personnes, lieux, organisations et dates de vos textes."          # À REMPLACER
AVERTISSEMENT = "Prototype de projet TALN – peut se tromper."                            # À REMPLACER
PIED_BARRE_LATERALE = "Master 2 IAMD – Université de Djibouti"                           # À REMPLACER
NOTE_EXTRAITS = ("Les extraits viennent du corpus de travail du projet : "
                 "le système les connaît mieux que des textes nouveaux.")               # À REMPLACER
LEGENDE_ERREUR = ("Avec le système par défaut (3a+3b), « Washington » est pris à tort pour une personne (PER) : "
                  "c'est un lieu. C'est une erreur du système.")                         # À REMPLACER
DEPOT = "https://github.com/Mani26368/taln-ner-djibouti"                                 # À REMPLACER

# ---------------------------------------------------------------------------------------------- couleurs
COULEURS = {                                                                             # À REMPLACER
    "fond_page": "#FAFAF9",
    "texte": "#111827",
    "accent": "#1E3A8A",                         # LA couleur d'accent : titre, bouton principal, liens, menu actif
    "texte_secondaire": "#4B5563",
    "carte_fond": "#FFFFFF",
    "bord": "#E5E7EB",
    "encadre": "#F3F4F6",                        # encadré gris « Prototype… peut se tromper »
    "blanc": "#FFFFFF",
}

# Fond pastel du soulignement de chaque type (le texte reste sombre, la lisibilité ne dépend pas du pastel).
TYPES = {                                                                                # À REMPLACER
    "ORG": {"nom": "Organisation", "pluriel": "organisations", "fond": "#BFDBFE"},
    "LOC": {"nom": "Lieu", "pluriel": "lieux", "fond": "#FED7AA"},
    "DATE": {"nom": "Date", "pluriel": "dates", "fond": "#E9D5FF"},
    "PER": {"nom": "Personne", "pluriel": "personnes", "fond": "#BBF7D0"},
    "FORMATION": {"nom": "Formation", "pluriel": "formations", "fond": "#FBCFE8"},
}

# ---------------------------------------------------------------------------------------------- exemples (vrais textes)
# Numéros de segments du corpus La Nation (data/corpus_*.csv). Le texte est lu dans le corpus : rien n'est inventé.
EXEMPLES = [                                                                             # À REMPLACER
    ("A14_S001", "Date"),
    ("A12_S005", "Personnes"),
    ("A04_S020", "Erreur"),
]
EXEMPLE_ERREUR = "A04_S020"       # celui qui affiche LEGENDE_ERREUR

# Un exemple par catégorie (page « Catégories reconnues »).
#   (identifiant du segment, texte de l'entité) pour La Nation : l'entité doit exister dans les annotations du dépôt.
#   FORMATION : La Nation n'en contient aucune ; l'exemple vient du corpus de Kadiga (data/corpus_kadiga).
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
    "Nom": "Repère Djibouti",
    "Nom technique": "reconnaissance d'entités nommées (NER)",
    "Domaine": "Traitement automatique des langues (TALN)",
    "Objectif": ("Montrer comment un programme peut repérer, dans un texte français, les personnes, les lieux, "
                 "les organisations, les dates et les formations."),
    "Cadre": "Master 2 IAMD – Université de Djibouti",
    "Technologies": "Python, spaCy, Streamlit",
    "Projet": "Binôme 5 : Mako et Kadiga",
}
