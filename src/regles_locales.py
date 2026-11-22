"""Règles locales pour le NER (Djibouti) : EntityRuler + un petit composant pour « titre + nom ».

Les règles sont rangées par GROUPES, pour pouvoir mesurer l'effet de chaque groupe.
Provenance de chaque groupe : voir SOURCES (dev / connaissance a priori / consigne du guide).
Aucune règle ne doit venir du test.

Utilisation :
    nlp = construire("fr_core_news_sm", groupes=list(GROUPES))
"""
import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.util import filter_spans

# ---------------------------------------------------------------- briques communes
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
JOUR = {"LOWER": {"IN": JOURS}}
MOIS_ = {"LOWER": {"IN": MOIS}}
NUM = {"TEXT": {"REGEX": r"^(0?[1-9]|[12]\d|3[01])(er)?$"}}
ANNEE = {"TEXT": {"REGEX": r"^(19|20)\d{2}$"}}

# petits mots qui peuvent apparaître DANS un nom d'institution (« ministère de la Jeunesse et de la Culture »)
LIAISON = ["de", "du", "des", "la", "le", "les", "l'", "l’", "d'", "d’", "et"]
# adjectifs courants qui suivent un nom dans un intitulé de ministère
ADJ = ["nationale", "supérieure", "professionnelle", "publique", "sociale", "régionale", "technique"]
TITRE = {"IS_TITLE": True, "IS_ALPHA": True}
# « de la Jeunesse », « et de la Culture » : un bloc = mots de liaison (0 ou plus) + un mot à majuscule (+ adjectif)
BLOC = [{"LOWER": {"IN": LIAISON}, "OP": "*"}, TITRE, {"LOWER": {"IN": ADJ}, "OP": "?"}]


def _blocs(k):
    return BLOC * k


# ---------------------------------------------------------------- groupes de règles (patterns EntityRuler)
GROUPES = {}

GROUPES["dates"] = [{"label": "DATE", "pattern": p} for p in [
    [dict(JOUR, OP="?"), NUM, MOIS_, dict(ANNEE, OP="?")],                                   # lundi 5 octobre / 7 octobre / 5 octobre 2026
    [NUM, {"LOWER": "et"}, NUM, MOIS_, dict(ANNEE, OP="?")],                                 # 30 et 31 août 2026
    [NUM, {"TEXT": ","}, NUM, {"LOWER": "et"}, NUM, MOIS_, dict(ANNEE, OP="?")],             # 6, 7 et 8 octobre
    [JOUR, {"LOWER": {"IN": ["matin", "soir"]}}],                                            # jeudi soir
    [JOUR],                                                                                  # lundi
    [ANNEE, {"TEXT": "-"}, ANNEE],                                                           # 2026-2027
]]

GROUPES["org_ministeres"] = (
    [{"label": "ORG", "pattern": [{"LOWER": "ministère"}] + _blocs(k)} for k in range(1, 5)]
    + [{"label": "ORG", "pattern": [{"LOWER": "secrétariat"}, {"LOWER": {"IN": ["d'", "d’"]}}, {"TEXT": "État"}]}]
    + [{"label": "ORG", "pattern": [{"LOWER": "secrétariat"}, {"LOWER": {"IN": ["d'", "d’"]}}, {"TEXT": "État"},
                                    {"LOWER": {"IN": ["chargé", "chargée"]}}] + _blocs(k)} for k in range(1, 4)]
)

QUALIFICATIFS = ["directeur", "exécutif", "national", "régional", "central", "technique",
                 "scientifique", "consultatif", "permanent"]
GROUPES["org_organes"] = [{"label": "ORG", "pattern": p} for p in [
    [{"TEXT": "Comité"}, {"LOWER": {"IN": QUALIFICATIFS}}],                                 # Comité directeur
    [{"TEXT": "Comité"}, {"LOWER": "ad"}, {"LOWER": "hoc"}],                                 # Comité ad hoc
    [{"TEXT": "Conseil"}, {"LOWER": "régional"}],                                            # Conseil régional
    [{"TEXT": "Conseil"}, {"LOWER": "régional"}, {"LOWER": {"IN": ["de", "d'", "d’", "du"]}}, TITRE],
]]

GROUPES["org_entreprises"] = [{"label": "ORG", "pattern": [
    {"IS_TITLE": True, "IS_STOP": False}, dict(TITRE, OP="{0,2}"), {"TEXT": {"IN": ["Industries", "Industry"]}}]}]

LEXIQUE_ORG = [
    # vu dans le dev
    "OIF", "OMS", "Organisation internationale de la Francophonie", "Organisation mondiale de la Santé",
    "Programme élargi de vaccination", "Coopérative artisanale des femmes d'Ardo",
    # connaissance a priori (institutions connues de Djibouti et grandes organisations)
    "Université de Djibouti", "Assemblée nationale", "Cour suprême", "Conseil constitutionnel",
    "Banque centrale de Djibouti", "Djibouti Telecom", "Port autonome international de Djibouti",
    "Électricité de Djibouti", "ONU", "UNICEF", "UNESCO", "FAO", "IGAD", "Union africaine",
    "Banque mondiale", "Ligue arabe", "Croix-Rouge",
]
LEXIQUE_LOC = [
    # vu dans le dev
    "Ardo Bankoualé", "Zone portuaire Sud", "Djibouti-ville", "République de Djibouti",
    # connaissance a priori : le pays, ses 6 régions, quelques localités, voisins, géographie
    "Djibouti", "Ali Sabieh", "Ali-Sabieh", "Arta", "Dikhil", "Obock", "Tadjourah",
    "Balbala", "Holl-Holl", "Loyada", "Yoboki", "Dorra", "Randa", "Khor Angar", "Lac Assal", "Lac Abbé",
    "Goubet", "Corne de l'Afrique", "Éthiopie", "Somalie", "Érythrée", "Yémen", "Addis-Abeba", "Mer Rouge",
]
GROUPES["lexique_org"] = [{"label": "ORG", "pattern": m} for m in LEXIQUE_ORG]
GROUPES["lexique_loc"] = [{"label": "LOC", "pattern": m} for m in LEXIQUE_LOC]

# ---------------------------------------------------------------- titre + nom (composant à part)
FONCTIONS = ["ministre", "président", "présidente", "directeur", "directrice", "ambassadeur", "ambassadrice",
             "inspecteur", "inspectrice", "préfet", "consultant", "consultante", "secrétaire", "sous-directeur",
             "conseiller", "conseillère", "maire", "gouverneur", "recteur"]
CIVILITES = ["Dr", "Pr", "Me", "Mme", "M.", "Monsieur", "Madame", "Maître", "Professeur", "Docteur"]
NOM = {"IS_TITLE": True, "IS_ALPHA": True, "IS_STOP": False}

GROUPES["per_titres"] = "composant"   # géré par le composant « noms_titres »


@Language.factory("noms_titres")
def creer_noms_titres(nlp, name):
    """Marque PER le NOM qui suit un titre ; le titre lui-même reste HORS de l'entité (règle du guide)."""
    matcher = Matcher(nlp.vocab)
    matcher.add("FONCTION", [[{"LOWER": {"IN": FONCTIONS}},
                              {"LOWER": {"IN": ["général", "générale", "adjoint", "adjointe"]}, "OP": "?"},
                              {"TEXT": ",", "OP": "?"},
                              dict(NOM, OP="{2,4}")]])
    matcher.add("CIVILITE", [[{"TEXT": {"IN": CIVILITES}}, dict(NOM, OP="{1,4}")]])

    def composant(doc):
        nouveaux = []
        for match_id, debut, fin in matcher(doc):
            if nlp.vocab.strings[match_id] == "CIVILITE":
                nouveaux.append(doc[debut + 1:fin])                     # on saute la civilité
            else:
                i = fin
                while i > debut and doc[i - 1].is_title and doc[i - 1].is_alpha:
                    i -= 1                                              # on remonte tant que ce sont des noms
                nouveaux.append(doc[i:fin])
        nouveaux = [s for s in nouveaux if len(s) > 0]
        nouveaux = [spacy.tokens.Span(doc, s.start, s.end, label="PER") for s in nouveaux]
        doc.ents = filter_spans(list(doc.ents) + nouveaux)
        return doc

    return composant


# ---------------------------------------------------------------- 3b : filtrage APRÈS le NER, aligné sur le guide
TYPES_FILTRES = ("PER", "ORG", "LOC")          # DATE (et MISC) ne sont jamais touchés par les filtres
GENERIQUES = ["Fédération", "Organisation", "Comité", "Assemblée", "Conseil", "Ministère", "Secrétariat",
              "Association", "Commission", "Direction", "Agence", "Université", "Gouvernement", "Mission"]
DECLENCHEURS_EVENEMENT = ["Mission", "Challenge", "Activités", "Festival", "Forum", "Sommet", "Journée",
                          "Journées", "Semaine", "Championnat", "Tournoi", "Coupe", "Concours",
                          "Conférence", "Séminaire", "Atelier"]
LIAISON_EVT = LIAISON + ["en"]
TITRES_A_RETIRER = [t.lower() for t in CIVILITES + FONCTIONS + ["général", "générale", "adjoint", "adjointe"]]
FILTRES = ["minuscule", "fonction", "mention_courte", "evenement", "titre_per", "debut_phrase", "domaines_ministre"]


def _est_nom_propre_like(tok):
    return tok.is_alpha and (tok.is_title or tok.is_upper)


def _spans_evenements(doc):
    """Repère les noms d'événements (Challenge …, Mission économique …, Assemblée générale …)."""
    spans, i, n = [], 0, len(doc)
    while i < n:
        t = doc[i]
        debut_evt = t.text in DECLENCHEURS_EVENEMENT or (
            t.text == "Assemblée" and i + 1 < n and doc[i + 1].lower_ == "générale")
        if not debut_evt:
            i += 1
            continue
        j = i + 1
        while j < n:
            u = doc[j]
            if _est_nom_propre_like(u) or u.like_num or (u.pos_ == "ADJ" and u.is_lower):
                j += 1
            elif u.lower_ in LIAISON_EVT:
                k = j
                while k < n and doc[k].lower_ in LIAISON_EVT:
                    k += 1
                if k < n and (_est_nom_propre_like(doc[k]) or (doc[k].pos_ == "ADJ" and doc[k].is_lower)):
                    j = k
                else:
                    break
            else:
                break
        if j > i + 1:                                   # un déclencheur seul n'est pas un événement
            spans.append((doc[i].idx, doc[j - 1].idx + len(doc[j - 1])))
        i = max(j, i + 1)
    return spans


def _chaines_fonction(doc):
    """« ministre de l'Agriculture, de l'Eau, de la Pêche … » : suite de mots qui décrit une fonction."""
    chaines, n = [], len(doc)
    for i, t in enumerate(doc):
        if t.lower_ not in FONCTIONS:
            continue
        j = i + 1
        while j < n:
            u = doc[j]
            if u.lower_ in LIAISON or _est_nom_propre_like(u):
                j += 1
            elif u.text == "," and j + 1 < n and doc[j + 1].lower_ in LIAISON:
                j += 1
            else:
                break
        if j > i + 1:
            chaines.append((i, j))
    return chaines


@Language.factory("filtre_guide", default_config={"actifs": FILTRES})
def creer_filtre_guide(nlp, name, actifs):
    """Enlève ou corrige des entités après le NER, selon le guide d'annotation."""
    def composant(doc):
        evts = _spans_evenements(doc) if "evenement" in actifs else []
        chaines = _chaines_fonction(doc) if "domaines_ministre" in actifs else []
        sortie = []
        for ent in doc.ents:
            if ent.label_ not in TYPES_FILTRES:
                sortie.append(ent)
                continue
            premier = doc[ent.start]
            # 1) entité qui commence par une minuscule : un mot commun, pas un nom propre
            #    (exception : « ministère de … » commence par une minuscule et est une ORG du guide)
            if ("minuscule" in actifs and premier.is_alpha and premier.is_lower
                    and premier.lower_ != "ministère"):
                continue
            # 2) entité qui commence par une fonction (« Secrétaire générale de l'… ») : pas une entité
            if "fonction" in actifs and ent.label_ in ("ORG", "LOC") and premier.lower_ in FONCTIONS:
                continue
            # 3) mention courte (« l'Organisation », « la Fédération ») : non annotée
            if "mention_courte" in actifs and ent.label_ in ("ORG", "LOC") and ent.text in GENERIQUES:
                continue
            # 4) événement : hors types
            if "evenement" in actifs:
                d, f = ent.start_char, ent.end_char
                if any(d < fe and f > de for de, fe in evts):
                    continue
            # 5) domaines d'un ministre pris pour des lieux (« de l'Eau, de la Pêche »)
            if ("domaines_ministre" in actifs and ent.label_ == "LOC" and ent.text not in LEXIQUE_LOC
                    and any(a <= ent.start < b for a, b in chaines)):
                continue
            # 6) mot unique en début de phrase qui n'est pas un nom propre (« Détecter », « Diabète »)
            if ("debut_phrase" in actifs and len(ent) == 1 and (premier.is_sent_start or premier.i == 0)
                    and premier.pos_ not in ("PROPN", "X", "")):
                continue
            # 7) titre au début d'un PER (« Me », « inspecteur général ») : on l'enlève
            if "titre_per" in actifs and ent.label_ == "PER":
                debut = ent.start
                while debut < ent.end and doc[debut].lower_ in TITRES_A_RETIRER:
                    debut += 1
                if debut >= ent.end:
                    continue
                if debut != ent.start:
                    ent = spacy.tokens.Span(doc, debut, ent.end, label="PER")
            sortie.append(ent)
        doc.ents = sortie
        return doc
    return composant


# ---------------------------------------------------------------- provenance (pour la transparence)
SOURCES = {
    "dates": "dates : mois et jours = connaissance du français ; formes (5 octobre, 6, 7 et 8 octobre, 2026-2027) vues dans le DEV",
    "org_ministeres": "« ministère de… » / « Secrétariat d'État chargé… » : demandé dans la consigne (3a) ; adjectifs = connaissance générale",
    "org_organes": "« Comité … » / « Conseil régional » : demandé dans la consigne (3a) / règles du guide",
    "org_entreprises": "« X Y Industries » : forme vue dans le DEV (A02), écrite de façon générale",
    "lexique_org": "mélange : entrées vues dans le DEV + institutions connues a priori (voir LEXIQUE_ORG)",
    "lexique_loc": "mélange : entrées vues dans le DEV + pays, régions, villes connues a priori (voir LEXIQUE_LOC)",
    "per_titres": "titre + nom : consigne (3a) ; formes vues dans le DEV (« Secrétaire générale, Louise… »)",
}


def construire(modele="fr_core_news_sm", groupes=None, filtres=None):
    """Retourne un pipeline spaCy.
    groupes : règles placées AVANT le NER (3a).
    filtres : liste de noms de FILTRES appliqués APRÈS le NER (3b) ; None = aucun filtre.
    """
    groupes = list(groupes) if groupes is not None else []
    nlp = spacy.load(modele)
    patterns = []
    for g in groupes:
        if g != "per_titres":
            patterns += GROUPES[g]
    if patterns:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(patterns)
    if "per_titres" in groupes:
        nlp.add_pipe("noms_titres", before="ner")
    if filtres:
        nlp.add_pipe("filtre_guide", last=True, config={"actifs": list(filtres)})
    return nlp
