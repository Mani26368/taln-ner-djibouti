"""Apparence et textes de « Repère Djibouti ». Kadiga : changez les valeurs marquées « À REMPLACER ».

Les COULEURS sont ici ; la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css, qui utilise ces couleurs.
Ce fichier ne contient AUCUN code d'analyse et AUCUN score : seulement des couleurs, des textes et des numéros d'exemples.
Aucune ressource en ligne : tout est local (dégradés et dessin vectoriel CSS).
"""

# ---------------------------------------------------------------------------------------------- textes
TITRE = "Repère Djibouti"                                                                # À REMPLACER
SOUS_TITRE = "Repérez les personnes, lieux, organisations et dates de vos textes."      # À REMPLACER
BANDEAU_TITRE = "Bienvenue sur Repère Djibouti !"                                        # À REMPLACER
PIED_BARRE_LATERALE = "Prototype de projet TALN"                                         # À REMPLACER
FORMATION_PIED = "Master 2 IAMD"                                                         # À REMPLACER
AVERTISSEMENT = "Prototype de projet TALN – peut se tromper."                            # À REMPLACER
NOTE_EXTRAITS = ("Les extraits viennent du corpus de travail du projet : "
                 "le système les connaît mieux que des textes nouveaux.")               # À REMPLACER

# ---------------------------------------------------------------------------------------------- couleurs
COULEURS = {                                                                             # À REMPLACER
    "bleu_nuit": "#0B1F4B",
    "bleu_royal": "#1D4ED8",
    "bleu_royal_survol": "#1E40AF",              # bouton au survol de la souris
    "ciel": "#0EA5E9",
    "turquoise": "#14B8A6",                      # décoration seulement (jamais derrière du texte)
    "fond_page": "#F3F6FB",
    "texte": "#0F172A",
    "texte_secondaire": "#475569",
    "carte_fond": "#FFFFFF",
    "carte_bord": "#DBE4F3",
    "ombre": "rgba(15, 42, 107, 0.08)",
    "resultats_fond": "#ECFDF5",
    "resultats_bord": "#A7F3D0",
    "coche": "#047857",                          # coche verte de « Résultats de l'analyse »
    "encadre": "#EAF1FD",                        # encadré « Prototype… peut se tromper »
    "blanc": "#FFFFFF",
}

# Bandeau d'accueil : dégradé bleu royal -> bleu ciel. Le blanc sur le bleu ciel est trop pâle (contraste 2,8) :
# le bleu royal est donc gardé jusqu'à « arret_pct » % de la largeur, et le texte reste dans les « largeur_texte_pct » % de gauche.
BANDEAU = {"debut": COULEURS["bleu_royal"], "fin": COULEURS["ciel"], "arret_pct": 35, "largeur_texte_pct": 55}   # À REMPLACER

# Pour chaque type : fond pastel du texte surligné (texte sombre dessus) et couleur de la pastille (légende, résumé).
TYPES = {                                                                                # À REMPLACER
    "ORG": {"nom": "Organisation", "pluriel": "organisations", "fond": "#BFDBFE", "point": "#1D4ED8"},   # bleu
    "LOC": {"nom": "Lieu", "pluriel": "lieux", "fond": "#FED7AA", "point": "#EA580C"},                 # orange
    "DATE": {"nom": "Date", "pluriel": "dates", "fond": "#E9D5FF", "point": "#9333EA"},                # violet
    "PER": {"nom": "Personne", "pluriel": "personnes", "fond": "#BBF7D0", "point": "#16A34A"},          # vert
    "FORMATION": {"nom": "Formation", "pluriel": "formations", "fond": "#FBCFE8", "point": "#DB2777"},  # rose
}

# Image facultative du bandeau : si demo/assets/bandeau.jpg existe, elle est utilisée (avec le dégradé par-dessus)
# et le crédit ci-dessous est affiché dans « À propos ». Sinon, le bandeau garde le dégradé et le dessin vectoriel.
CREDIT_BANDEAU = "Photo du bandeau : à créditer (auteur, source, licence)."               # À REMPLACER

# ---------------------------------------------------------------------------------------------- exemples (vrais textes)
# Numéros de segments du corpus La Nation (data/corpus_*.csv). Le texte est lu dans le corpus : rien n'est inventé.
#   1 = un segment avec une DATE, un lieu et une organisation que le système par défaut (3a+3b) trouve entièrement (A14_S001) ;
#   2 = un segment avec des personnes, que D et 3a+3b trouvent entièrement (A12_S005) ;
#   3 = un cas difficile choisi par Mako : A04_S020, où le système par défaut (3a+3b) prend « Washington » pour une personne.
EXEMPLES = [                                                                             # À REMPLACER
    ("A14_S001", "Date, lieu, organisation"),
    ("A12_S005", "Personnes"),
    ("A04_S020", "Cas difficile"),
]

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
