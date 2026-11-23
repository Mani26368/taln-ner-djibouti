"""Apparence et textes de « Repère Djibouti ». Changez ici les valeurs marquées « À REMPLACER ».

Les COULEURS sont ici ; la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css, qui utilise ces couleurs.
Design sobre : bandeau bleu foncé, fond clair, cartes blanches, police Inter (fichier local, voir demo/assets/fonts/).
Ce fichier ne contient AUCUN code d'analyse et AUCUN chiffre de performance : seulement des couleurs, des textes et des numéros d'exemples.
"""

# ---------------------------------------------------------------------------------------------- textes
TITRE = "Repère Djibouti"                                                                # À REMPLACER
PHRASE = "Personnes, lieux, organisations et dates de vos textes"                       # À REMPLACER
AVERTISSEMENT = "Prototype de projet TALN – peut se tromper."                            # À REMPLACER
NOTE_EXTRAITS = ("Extrait du corpus de travail du projet : le système le connaît mieux "
                 "que des textes nouveaux.")                                             # À REMPLACER
LEGENDE_ERREUR = ("Avec le système par défaut (3a+3b), « Washington » est pris à tort pour une personne (PER) : "
                  "c'est un lieu. C'est une erreur du système.")                         # À REMPLACER
DEPOT = "https://github.com/Mani26368/taln-ner-djibouti"                                 # À REMPLACER

# Phrase d'exemple, affichée en grisé avant la première analyse : phrase illustrative, ABRÉGÉE d'après le segment A02_S001
# de La Nation (ce n'est pas un extrait exact ; l'écran dit seulement « Exemple »).
PHRASE_EXEMPLE = ("Le ministre de l'Agriculture s'est rendu lundi 5 octobre à l'usine Douda Tazwid Industries, "
                  "à Djibouti-ville.")                                                    # À REMPLACER
ENTITES_EXEMPLE = [("lundi 5 octobre", "DATE"), ("Douda Tazwid Industries", "ORG"), ("Djibouti-ville", "LOC")]

# ---------------------------------------------------------------------------------------------- couleurs
COULEURS = {                                                                             # À REMPLACER
    "bandeau": "#13255C",
    "bandeau_icone": "#2F5BD8",
    "bandeau_texte_secondaire": "#B8C6EE",
    "bouton": "#1E3FAE",                         # bouton principal, lien « Télécharger en CSV »
    "fond_page": "#F4F6FA",
    "texte": "#1B2336",
    "texte_secondaire": "#5B6783",
    "carte_fond": "#FFFFFF",
    "bord": "#E2E6EF",
    "bord_champ": "#D5DBE8",
    "bord_pilule": "#C9D2E6",
    "ligne_tableau": "#EEF1F6",
    "blanc": "#FFFFFF",
}

# Fond pastel (surlignage) et couleur du texte de chaque type.
TYPES = {                                                                                # À REMPLACER
    "ORG": {"nom": "Organisation", "pluriel": "Organisations", "fond": "#BFDBFE", "texte": "#1E3A8A"},
    "LOC": {"nom": "Lieu", "pluriel": "Lieux", "fond": "#FED7AA", "texte": "#7C3A0E"},
    "DATE": {"nom": "Date", "pluriel": "Dates", "fond": "#E9D5FF", "texte": "#4C1D95"},
    "PER": {"nom": "Personne", "pluriel": "Personnes", "fond": "#BBF7D0", "texte": "#14532D"},
    "FORMATION": {"nom": "Formation", "pluriel": "Formations", "fond": "#FBCFE8", "texte": "#831843"},
}
TYPES_LEGENDE = ["ORG", "LOC", "DATE", "PER"]     # les 4 types de la légende ; FORMATION s'ajoute si le résultat en contient

# ---------------------------------------------------------------------------------------------- exemples (vrais textes)
# Numéros de segments du corpus La Nation (data/corpus_*.csv). Le texte est lu dans le corpus : rien n'est inventé.
EXEMPLES = [                                                                             # À REMPLACER
    ("A14_S001", "Une date"),
    ("A12_S005", "Des personnes"),
    ("A04_S020", "Un cas difficile"),
]
EXEMPLE_ERREUR = "A04_S020"       # celui qui affiche LEGENDE_ERREUR

# Un exemple par catégorie (page « Catégories »).
#   (identifiant du segment, texte de l'entité) pour La Nation : l'entité doit exister dans les annotations du dépôt.
#   FORMATION : La Nation n'en contient aucune ; l'exemple vient du corpus de ressources (data/corpus_kadiga/sentences.csv,
#   id ENS-02 : phrase synthétique de cours, pas un texte officiel).
EXEMPLES_CATEGORIES = {                                                                  # À REMPLACER
    "ORG": ("A03_S001", "Fédération djiboutienne de football"),
    "LOC": ("A14_S011", "Tadjourah"),
    "PER": ("A02_S014", "Radwan Abdillahi Bahdon"),
    "DATE": ("A02_S001", "lundi 5 octobre"),
    "FORMATION": ("ENS-02", "Master IAMD"),      # corpus de ressources
}
ORIGINE_FORMATION = "exemple tiré du corpus de ressources (phrase synthétique de cours, ENS-02)"

# Définitions simples (reprises du guide d'annotation, docs/guide_annotation.md).
DEFINITIONS = {                                                                          # À REMPLACER
    "ORG": "une institution, un ministère, une fédération, une entreprise, une organisation",
    "LOC": "un pays, une ville, un quartier, une localité, un site nommé",
    "PER": "une personne, désignée par son nom propre (sans son titre)",
    "DATE": "une date ou un moment repéré dans le calendrier",
    "FORMATION": "un diplôme, un master, une filière",
}

# ---------------------------------------------------------------------------------------------- page « À propos »
# Page simple pour un utilisateur normal : aucun terme technique (ni modèle, ni système, ni chiffre).
A_PROPOS_UTILITE = ("Repère Djibouti repère, dans un texte français, les personnes, les lieux, les organisations, "
                    "les dates et les formations. Il a été pensé pour des textes de Djibouti, comme les articles de presse.")   # À REMPLACER
A_PROPOS_PROTOTYPE = "Prototype : il peut se tromper, surtout sur les noms locaux."                                              # À REMPLACER
A_PROPOS_HORS_LIGNE = "Tout fonctionne hors ligne : le texte saisi ne quitte pas l'ordinateur."                                  # À REMPLACER
# Informations du projet (les deux auteures ensemble, sans dire qui a fait quelle partie).
A_PROPOS_INFOS = [                                                                                                               # À REMPLACER
    ("Projet", "Binôme 5 – Reconnaissance d'entités nommées propres à Djibouti"),
    ("Réalisé par", "Mako Mohamed Aden et Kadiga"),
    ("Encadrant", "Dr Houssein Ahmed Assowe"),
    ("Formation", "M2 IAMD, Université de Djibouti, cours TALN, 2026"),
]
