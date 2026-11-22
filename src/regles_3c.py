"""Version 3c : améliorations GÉNÉRALES ajoutées à la version gelée 3a+3b (commit 087deb3).

Ce fichier NE MODIFIE PAS src/regles_locales.py (gelé). Il le réutilise et ajoute 3 options :
  djibouti_ne_coupe_pas : la règle de lexique « Djibouti » ne doit pas couper une ORG plus longue qui le contient
  annee_seule           : une année seule en contexte (« en 2022 ») devient DATE
  habitants             : les noms d'habitants (« Djiboutiens », « Indiens ») ne sont pas des entités

Avec les trois options à False et le modèle sm, le pipeline est IDENTIQUE à 3a+3b (vérifié par essais_3c.py).
Pas de réentraînement, pas de réglage fin de seuils.
"""
import re

import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.util import filter_spans

import regles_locales as R

# ------------------------------------------------------------------ année seule en contexte
PREPOSITIONS_ANNEE = ["en", "depuis", "dès", "avant", "après", "vers", "durant", "pendant"]
ANNEE = r"^(19|20)\d{2}$"


@Language.factory("annee_seule_3c")
def creer_annee_seule(nlp, name):
    """« en 2022 » -> DATE = « 2022 » (la préposition reste hors de l'entité). Pas de préposition = pas de DATE
    (donc « Activités Estivales 2026 », nom d'événement, n'est pas touché)."""
    matcher = Matcher(nlp.vocab)
    matcher.add("ANNEE", [[{"LOWER": {"IN": PREPOSITIONS_ANNEE}}, {"TEXT": {"REGEX": ANNEE}}]])

    def composant(doc):
        nouveaux = [spacy.tokens.Span(doc, debut + 1, fin, label="DATE") for _, debut, fin in matcher(doc)]
        doc.ents = filter_spans(list(doc.ents) + nouveaux)      # le plus long gagne (« 2026-2027 » reste entier)
        return doc
    return composant


# ------------------------------------------------------------------ « Djibouti » ne coupe pas une ORG plus longue
@Language.factory("remplir_djibouti_3c")
def creer_remplir_djibouti(nlp, name):
    """Le mot « Djibouti » n'est plus posé AVANT le NER (il coupait « Institut … de Djibouti » en deux).
    Après le NER : s'il reste non couvert par une entité, on le marque LOC."""
    def composant(doc):
        deja = {i for e in doc.ents for i in range(e.start, e.end)}
        ajout = [spacy.tokens.Span(doc, t.i, t.i + 1, label="LOC")
                 for t in doc if t.text == "Djibouti" and t.i not in deja]
        if ajout:
            doc.ents = list(doc.ents) + ajout
        return doc
    return composant


# ------------------------------------------------------------------ noms d'habitants
DETERMINANTS_HABITANTS = ["les", "des", "aux", "ces", "nos", "ses", "leurs", "de", "d'", "d’", "certains", "plusieurs"]
SUFFIXE_HABITANTS = re.compile(r"^[A-ZÉÈ][\w’'-]*(iens|ienne|iennes)$")


@Language.factory("filtre_habitants_3c")
def creer_filtre_habitants(nlp, name):
    """Un seul mot en -iens / -ienne(s), précédé d'un déterminant (« des Djiboutiens ») : nom d'habitants, pas un lieu."""
    def composant(doc):
        gardees = []
        for ent in doc.ents:
            if (ent.label_ in ("LOC", "ORG", "PER") and len(ent) == 1 and SUFFIXE_HABITANTS.match(ent.text)
                    and ent.start > 0 and doc[ent.start - 1].lower_ in DETERMINANTS_HABITANTS):
                continue
            gardees.append(ent)
        doc.ents = gardees
        return doc
    return composant


# ------------------------------------------------------------------ assemblage
def construire_3c(modele="fr_core_news_sm", djibouti_ne_coupe_pas=False, annee_seule=False, habitants=False,
                  remplir_apres_filtre=True):
    """remplir_apres_filtre=False reproduit la 1re version de l'essai b) (ordre fautif, gardée pour la transparence)."""
    nlp = spacy.load(modele)
    patterns = []
    for g in R.GROUPES:
        if g == "per_titres":
            continue
        for p in R.GROUPES[g]:
            if djibouti_ne_coupe_pas and g == "lexique_loc" and p["pattern"] == "Djibouti":
                continue                                    # on retire seulement le « Djibouti » seul
            patterns.append(p)
    nlp.add_pipe("entity_ruler", before="ner").add_patterns(patterns)
    nlp.add_pipe("noms_titres", before="ner")               # composant de regles_locales (gelé)
    if annee_seule:
        nlp.add_pipe("annee_seule_3c", before="ner")
    if djibouti_ne_coupe_pas and not remplir_apres_filtre:
        nlp.add_pipe("remplir_djibouti_3c", after="ner")       # 1re version : AVANT le filtre (fautive)
    if habitants:
        nlp.add_pipe("filtre_habitants_3c", after="ner")
    nlp.add_pipe("filtre_guide", last=True, config={"actifs": list(R.FILTRES_3B_FINAL)})
    if djibouti_ne_coupe_pas and remplir_apres_filtre:
        nlp.add_pipe("remplir_djibouti_3c", last=True)          # APRÈS le filtre : sinon un LOC supprimé par le filtre fait perdre « Djibouti »
    return nlp


# ------------------------------------------------------------------ CONFIGURATION FIGÉE DE 3c
# Résultat des essais (voir results/essais_3c.csv) : AUCUN essai n'a passé les critères de décision
# (gain net d'au moins +0.02 de F1 exact sur les 12 articles déjà vus, et au moins 2 segments changés).
# 3c est donc IDENTIQUE à 3a+3b (commit 087deb3). Ce fichier est gelé : on ne le modifie plus.
CONFIG_3C = {"modele": "fr_core_news_sm", "djibouti_ne_coupe_pas": False, "annee_seule": False,
             "habitants": False, "remplir_apres_filtre": True}


def construire_3c_final():
    """La version 3c gelée (= 3a+3b : tous les essais ont été refusés)."""
    return construire_3c(**CONFIG_3C)
