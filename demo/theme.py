"""Apparence et textes de « NER-djib ». Changez ici les valeurs marquées « À REMPLACER ».

Les COULEURS sont ici ; la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css, qui utilise ces couleurs.
Design sobre : bandeau bleu foncé, fond clair, cartes blanches, police Inter (fichier local, voir demo/assets/fonts/).
Ce fichier ne contient AUCUN code d'analyse et AUCUN chiffre de performance : seulement des couleurs, des textes et des numéros d'exemples.
"""

# ---------------------------------------------------------------------------------------------- textes
TITRE = "NER-djib"                                                                       # À REMPLACER
PHRASE = "Personnes, lieux, organisations et dates de vos textes"                       # À REMPLACER
AVERTISSEMENT = "Prototype de projet TALN – peut se tromper."                            # À REMPLACER
NOTE_EXTRAITS = "Extrait d'un article de La Nation."                                   # À REMPLACER
LEGENDE_ERREUR = ("Ici, « Washington » est pris à tort pour une personne (PER) : "
                  "c'est un lieu. C'est une erreur de l'application.")                 # À REMPLACER
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
# Nom de la méthode affiché sous le texte annoté (clé interne -> texte). Les clés internes ne changent pas.
METHODES_COURT = {"3a+3b": "règles + lexique locaux", "D": "modèle ré-entraîné", "A": "spaCy seul"}
EXEMPLE_ACCUEIL = "A01_S002"      # extrait de La Nation analysé dès l'ouverture de la page (il contient les 4 types)
ETAPES = [("1", "Collez un texte"), ("2", "Cliquez sur Analyser"), ("3", "Lisez les entités et téléchargez le CSV")]
PIED = "NER-djib · Prototype de projet TALN · M2 IAMD · Université de Djibouti"
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
ORIGINE_FORMATION = "exemple tiré d'une phrase de cours écrite pour le projet"

# Définitions simples (reprises du guide d'annotation, docs/guide_annotation.md).
DEFINITIONS = {                                                                          # À REMPLACER
    "ORG": "une institution, un ministère, une fédération, une entreprise, une organisation",
    "LOC": "un pays, une ville, un quartier, une localité, un site nommé",
    "PER": "une personne, désignée par son nom propre (sans son titre)",
    "DATE": "une date ou un moment repéré dans le calendrier",
    "FORMATION": "un diplôme, un master, une filière",
}

# ---------------------------------------------------------------------------------------------- page « À propos »
# Page simple pour un utilisateur normal : aucun terme technique (ni modèle, ni système, ni chiffre de performance).
A_PROPOS_TITRE = "NER-djib"                                                                                               # À REMPLACER
A_PROPOS_INTRO = ("Trouve les personnes, les lieux, les organisations et les dates dans un texte français, "
                  "pensé pour les textes de Djibouti.")                                                                          # À REMPLACER
# Trois petites cartes : (titre, phrase, icône). {limite} est remplacé par la limite de caractères de l'application.
A_PROPOS_CARTES = [                                                                                                              # À REMPLACER
    ("Prototype", "Il peut se tromper, surtout sur les noms locaux.", "info"),
    ("Vie privée", "Le texte saisi est analysé sur le moment et n'est pas enregistré.", "cadenas"),
    ("Limite", "{limite} caractères par analyse.", "regle"),
]
# Informations du projet (les deux auteures ensemble, sans dire qui a fait quelle partie).
A_PROPOS_INFOS = [                                                                                                               # À REMPLACER
    ("Projet", "Binôme 5 – Reconnaissance d'entités nommées propres à Djibouti"),
    ("Réalisé par", "Mako Mohamed Aden et Kadiga Ali"),
    ("Encadrant", "Dr Houssein Ahmed Assowe"),
    ("Formation", "M2 IAMD, Université de Djibouti, cours TALN, 2026"),
]
A_PROPOS_BOUTON = "Voir le dépôt GitHub"                                                                                         # À REMPLACER
