"""Systèmes A, B, C, D de Kadiga, repris À L'IDENTIQUE depuis kadiga/TP_NER_Djibouti_Binome5.ipynb.

Rien n'est modifié par rapport au notebook : mêmes règles, même lexique (construit sur SON train),
mêmes paramètres (graine 42, 40 époques max, patience 6, lots de 8, dropout 0.3).
Ce module ne lit que kadiga/data/corpus et n'écrit rien dans kadiga/.

  A : spaCy fr_core_news_sm seul
  B : A + EntityRuler (règles génériques, avant le NER)
  C : B + lexique local construit sur le train de Kadiga
  D : NER de spaCy ré-entraîné sur le train de Kadiga (arrêt sur sa validation)
"""
import random
from collections import Counter
from pathlib import Path

import pandas as pd
import spacy
from spacy.training import Example
from spacy.util import fix_random_seed

RACINE = Path(__file__).resolve().parent.parent
CORPUS_KADIGA = RACINE / "kadiga" / "data" / "corpus"
SEED = 42
LABELS = ["ORG", "LOC", "PER", "DATE", "FORM"]
MODELE = "fr_core_news_sm"

# Étiquettes spaCy -> schéma de Kadiga. MISC est écartée.
MAPPING = {"PER": "PER", "LOC": "LOC", "ORG": "ORG", "MISC": None, "DATE": "DATE", "FORM": "FORM"}


# ------------------------------------------------------------------ données de Kadiga
def charger(nom, corpus=CORPUS_KADIGA):
    """Reconstruit la liste de phrases {id, section, text, entities} depuis les deux CSV."""
    phrases = pd.read_csv(corpus / "sentences.csv", encoding="utf-8")
    entites = pd.read_csv(corpus / "entities.csv", encoding="utf-8")
    phrases = phrases[phrases["split"] == nom]
    entites = entites[entites["split"] == nom]
    par_id = {i: g for i, g in entites.groupby("id")}
    docs = []
    for r in phrases.itertuples():
        g = par_id.get(r.id)
        ents = [] if g is None else [
            {"start": int(e.start), "end": int(e.end), "label": e.label, "text": e.text}
            for e in g.itertuples()]
        docs.append({"id": r.id, "section": r.section, "text": r.text, "entities": ents})
    return docs


def refs(docs):
    return {(d["id"], e["start"], e["end"], e["label"]) for d in docs for e in d["entities"]}


# ------------------------------------------------------------------ prédiction et évaluation (celles de Kadiga)
def predire(nlp_modele, docs, mapping=MAPPING):
    """Retourne l'ensemble des (id_phrase, start, end, label) prédits, étiquettes déjà converties."""
    preds = set()
    for d, doc in zip(docs, nlp_modele.pipe([d["text"] for d in docs])):
        for ent in doc.ents:
            lab = mapping.get(ent.label_)
            if lab:
                preds.add((d["id"], ent.start_char, ent.end_char, lab))
    return preds


def evaluer(references, predictions, labels=LABELS):
    """Évaluation de Kadiga (correspondance exacte). NB : arrondie à 3 décimales, comme dans son notebook
    (l'arrêt anticipé de D compare ces valeurs arrondies)."""
    def prf(vp, fp, fn):
        p = vp / (vp + fp) if vp + fp else 0.0
        r = vp / (vp + fn) if vp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        return p, r, f
    lignes, tvp, tfp, tfn = [], 0, 0, 0
    for lab in labels:
        ref = {x for x in references if x[3] == lab}
        pre = {x for x in predictions if x[3] == lab}
        vp, fp, fn = len(ref & pre), len(pre - ref), len(ref - pre)
        tvp, tfp, tfn = tvp + vp, tfp + fp, tfn + fn
        p, r, f = prf(vp, fp, fn)
        lignes.append({"etiquette": lab, "precision": p, "rappel": r, "f1": f, "support": len(ref), "VP": vp, "FP": fp, "FN": fn})
    p, r, f = prf(tvp, tfp, tfn)
    lignes.append({"etiquette": "micro", "precision": p, "rappel": r, "f1": f, "support": tvp + tfn, "VP": tvp, "FP": tfp, "FN": tfn})
    par_lab = pd.DataFrame(lignes)
    lignes.append({"etiquette": "macro", "precision": par_lab["precision"].mean(), "rappel": par_lab["rappel"].mean(),
                   "f1": par_lab["f1"].mean(), "support": par_lab["support"].sum(),
                   "VP": tvp, "FP": tfp, "FN": tfn})
    return pd.DataFrame(lignes).set_index("etiquette").round(3)


# ------------------------------------------------------------------ système B : règles génériques
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
ANNEE = r"^(18|19|20)\d{2}$"
JOUR = r"^(0?[1-9]|[12]\d|3[01]|1er)$"
PREPS = [[], [{"LOWER": p} for p in ("de",)], [{"LOWER": "du"}], [{"LOWER": "des"}],
         [{"LOWER": "d’"}], [{"LOWER": "d'"}], [{"LOWER": "de"}, {"LOWER": "la"}],
         [{"LOWER": "de"}, {"LOWER": "l’"}], [{"LOWER": "de"}, {"LOWER": "l'"}]]
TITRE = {"IS_TITLE": True}


def motifs_tete(tetes, label, sans_prep=True, tete_capitalisee=False, nmax=4):
    """tête + (préposition) + 1 à nmax mots capitalisés  ->  ex. « Université de Xxx », « lac Xxx »."""
    out = []
    for prep in PREPS:
        if not prep and not sans_prep:
            continue
        for n in range(1, nmax + 1):
            tete = {"LOWER": {"IN": tetes}}
            if tete_capitalisee:
                tete["IS_TITLE"] = True
            out.append({"label": label, "pattern": [tete] + prep + [dict(TITRE) for _ in range(n)]})
    return out


def patterns_generiques():
    patterns_B = []
    # DATE
    patterns_B += [
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": JOUR}}, {"LOWER": {"IN": MOIS}}, {"TEXT": {"REGEX": ANNEE}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": JOUR}}, {"LOWER": {"IN": MOIS}}]},
        {"label": "DATE", "pattern": [{"LOWER": {"IN": MOIS}}, {"TEXT": {"REGEX": ANNEE}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": r"^(18|19|20)\d{2}[-–/](18|19|20)?\d{2}$"}}]},
        {"label": "DATE", "pattern": [{"LOWER": {"IN": ["début", "milieu", "fin"]}}, {"LOWER": {"IN": ["des", "du"]}},
                                      {"LOWER": "années"}, {"TEXT": {"REGEX": ANNEE}}]},
        {"label": "DATE", "pattern": [{"TEXT": {"REGEX": ANNEE}}]},
    ]
    # ORG : mots-têtes d'institutions (tête capitalisée pour limiter les faux positifs)
    TETES_ORG = ["université", "ministère", "institut", "faculté", "centre", "conseil", "agence", "banque", "hôpital",
                 "lycée", "maternité", "clinique", "commission", "comité", "organisation", "autorité", "association", "ligue"]
    patterns_B += motifs_tete(TETES_ORG, "ORG", sans_prep=False, tete_capitalisee=True)
    # LOC : reliefs, plans d'eau, infrastructures
    TETES_LOC = ["lac", "mont", "golfe", "désert", "plateau", "mer", "détroit", "océan", "île", "vallée", "baie", "port"]
    patterns_B += motifs_tete(TETES_LOC, "LOC", sans_prep=True, tete_capitalisee=False, nmax=3)
    # FORM : types de diplômes
    patterns_B += [{"label": "FORM", "pattern": [{"TEXT": {"IN": ["DUT", "BTS", "DEUG", "Master", "Licence", "Doctorat"]}}]}]
    for n in range(1, 5):
        patterns_B.append({"label": "FORM", "pattern": [{"LOWER": {"IN": ["master", "licence", "dut", "bts"]}}]
                           + [dict(TITRE) for _ in range(n)]})
        patterns_B.append({"label": "FORM", "pattern": [{"LOWER": {"IN": ["master", "licence"]}},
                           {"LOWER": {"IN": ["appliquée", "professionnelle", "mention"]}}] + [dict(TITRE) for _ in range(n)]})
    return patterns_B


# ------------------------------------------------------------------ système C : lexique construit sur le train
def lexique_train(train):
    """Lexique construit UNIQUEMENT sur le train (DATE exclue). Retourne la liste (texte, label)."""
    lexique = {lab: sorted({e["text"] for d in train for e in d["entities"] if e["label"] == lab})
               for lab in LABELS if lab != "DATE"}
    tous = [(t, lab) for lab, ts in lexique.items() for t in ts]
    doublons = [t for t, n in Counter(t for t, _ in tous).items() if n > 1]
    assert not doublons, f"formes à plusieurs étiquettes : {doublons}"
    return tous


# ------------------------------------------------------------------ système D : NER ré-entraîné
MAX_EPOCHS, PATIENCE, BATCH, DROPOUT = 40, 6, 8, 0.3


def construire_exemples(nlp_modele, docs):
    """Convertit les annotations (offsets de caractères) en Example spaCy. Retourne (exemples, nb_ignorées)."""
    exemples, ignorees = [], 0
    for d in docs:
        doc = nlp_modele.make_doc(d["text"])
        ents = []
        for e in d["entities"]:
            span = doc.char_span(e["start"], e["end"], label=e["label"], alignment_mode="strict")
            if span is None:        # la frontière ne coïncide pas avec un découpage en tokens
                ignorees += 1
            else:
                ents.append(span)
        doc.set_ents(ents)
        exemples.append(Example(nlp_modele.make_doc(d["text"]), doc))
    return exemples, ignorees


def entrainer_D(train, val, graine=SEED, verbeux=True):
    """Ré-entraîne le NER sur le train, garde le meilleur modèle de la validation (arrêt anticipé)."""
    random.seed(graine)
    fix_random_seed(graine)
    refs_val = refs(val)
    nlp_d = spacy.load(MODELE)
    ner_d = nlp_d.get_pipe("ner")
    for lab in ("DATE", "FORM"):
        ner_d.add_label(lab)
    ex_train, ignorees = construire_exemples(nlp_d, train)
    if verbeux:
        print(f"[D] Exemples d'entraînement : {len(ex_train)} phrases ({ignorees} entités ignorées : frontière ≠ tokens)")
    courbe = []
    meilleur_f1, meilleur_etat, sans_progres = -1.0, None, 0
    with nlp_d.select_pipes(enable=["tok2vec", "ner"]):
        optimiseur = nlp_d.resume_training()
        f0 = evaluer(refs_val, predire(nlp_d, val)).loc["micro", "f1"]
        courbe.append((0, None, f0))
        for epoque in range(1, MAX_EPOCHS + 1):
            random.shuffle(ex_train)
            pertes = {}
            for lot in spacy.util.minibatch(ex_train, size=BATCH):
                nlp_d.update(lot, sgd=optimiseur, drop=DROPOUT, losses=pertes)
            f1_val = evaluer(refs_val, predire(nlp_d, val)).loc["micro", "f1"]
            courbe.append((epoque, pertes["ner"], f1_val))
            if f1_val > meilleur_f1:
                meilleur_f1, meilleur_etat, sans_progres = f1_val, nlp_d.to_bytes(), 0
            else:
                sans_progres += 1
            if sans_progres >= PATIENCE:
                if verbeux:
                    print(f"[D] Arrêt anticipé à l'époque {epoque}")
                break
        nlp_d.from_bytes(meilleur_etat)       # on garde le MEILLEUR modèle de la validation
    if verbeux:
        print(f"[D] Meilleur F1 micro sur la validation de Kadiga : {meilleur_f1:.3f}")
    return nlp_d, courbe


# ------------------------------------------------------------------ assemblage
def construire_systemes(train=None, val=None, verbeux=True):
    """Retourne {"A": nlp, "B": nlp, "C": nlp, "D": nlp}. Aucun paramètre n'est modifié."""
    train = train if train is not None else charger("train")
    val = val if val is not None else charger("val")
    nlp_a = spacy.load(MODELE)

    patterns_B = patterns_generiques()
    nlp_b = spacy.load(MODELE)
    nlp_b.add_pipe("entity_ruler", before="ner").add_patterns(patterns_B)

    patterns_C = patterns_B + [{"label": lab, "pattern": t} for t, lab in lexique_train(train)]
    nlp_c = spacy.load(MODELE)
    nlp_c.add_pipe("entity_ruler", before="ner").add_patterns(patterns_C)

    nlp_d, courbe = entrainer_D(train, val, verbeux=verbeux)
    return {"A": nlp_a, "B": nlp_b, "C": nlp_c, "D": nlp_d}


NOMS = {"A": "A – spaCy seul", "B": "B – + règles génériques", "C": "C – + lexique local (train)",
        "D": "D – spaCy ré-entraîné (train)"}


def tableau_comparatif(systemes, test):
    """Reconstruit le tableau de Kadiga (mêmes colonnes) sur son test."""
    refs_test = refs(test)
    lignes = []
    for k, nlp_k in systemes.items():
        r = evaluer(refs_test, predire(nlp_k, test))
        ligne = {"système": NOMS[k], "P micro": r.loc["micro", "precision"], "R micro": r.loc["micro", "rappel"],
                 "F1 micro": r.loc["micro", "f1"], "F1 macro": r.loc["macro", "f1"]}
        ligne.update({f"F1 {lab}": r.loc[lab, "f1"] for lab in LABELS})
        lignes.append(ligne)
    return pd.DataFrame(lignes)


def verifier_contre_kadiga(systemes, test=None):
    """Compare le tableau recalculé au fichier de Kadiga. Retourne (ok, tableau_recalculé, tableau_kadiga, écarts)."""
    test = test if test is not None else charger("test")
    recalcule = tableau_comparatif(systemes, test)
    ref = pd.read_csv(RACINE / "kadiga" / "results" / "tableau_comparatif.csv", encoding="utf-8-sig")
    num = list(ref.columns[1:])
    ecarts = (recalcule[num] - ref[num]).abs().round(3)
    ok = list(recalcule["système"]) == list(ref["système"]) and float(ecarts.max().max()) == 0.0
    return ok, recalcule, ref, ecarts
