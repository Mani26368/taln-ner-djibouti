"""Mesure UNE FOIS les systèmes sur un corpus annoté, en score EXACT et en score TOLÉRANT.

Systèmes mesurés (aucun n'est modifié ici) :
  A          spaCy fr_core_news_sm seul
  3a         + règles locales (EntityRuler, src/regles_locales.py, groupes figés)
  3a+3b      + filtres de la 3b finale (R.FILTRES_3B_FINAL, figée au commit 087deb3)
  Kadiga B   règles génériques de Kadiga
  Kadiga C   B + lexique de SON train
  Kadiga D   NER ré-entraîné sur SON train (graine 42)

Garde-fou : avant de mesurer, on vérifie qu'on retrouve le tableau de Kadiga sur SON test. Sinon : arrêt.

Usage :
  python src/mesurer_test2.py                                  # test 2 (data/corpus_test2.csv, annotations_test2.csv)
  python src/mesurer_test2.py CORPUS ANNOTATIONS DOSSIER_SORTIE # autre corpus (essai à blanc)
"""
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regles_locales as R
import systemes_kadiga as K
from evaluate import evaluer, evaluer_tolerant

RACINE = K.RACINE
TYPES3 = ["PER", "ORG", "LOC"]
TYPES4 = ["PER", "ORG", "LOC", "DATE"]
VERS_NOTRE = {"PER": "PER", "ORG": "ORG", "LOC": "LOC", "DATE": "DATE", "FORM": "FORMATION"}
NOMS = {"A": "A : spaCy seul", "3a": "3a : + règles locales", "3a+3b": "3a+3b : + filtres (3b finale)",
        "K-B": "Kadiga B : règles génériques", "K-C": "Kadiga C : + lexique de son train",
        "K-D": "Kadiga D : NER ré-entraîné"}


def lire(corpus, annotations):
    with open(corpus, encoding="utf-8", newline="") as f:
        segments = list(csv.DictReader(f))
    gold = {s["id"]: [] for s in segments}
    with open(annotations, encoding="utf-8", newline="") as f:
        for a in csv.DictReader(f):
            gold[a["id_segment"]].append((int(a["debut"]), int(a["fin"]), a["type"]))
    return segments, gold


def predictions_spacy(nlp, segments):
    """Pipelines de R.construire : on garde PER, ORG, LOC, DATE (MISC ignorée)."""
    par_id = {}
    for s, doc in zip(segments, nlp.pipe([s["fr"] for s in segments])):
        par_id[s["id"]] = sorted((e.start_char, e.end_char, e.label_) for e in doc.ents if e.label_ in TYPES4)
    return par_id


def predictions_kadiga(nlp, segments):
    brut = K.predire(nlp, [{"id": s["id"], "text": s["fr"]} for s in segments])   # sa fonction, son mapping
    par_id = {s["id"]: [] for s in segments}
    for (i, d, f, lab) in sorted(brut):
        par_id[i].append((d, f, VERS_NOTRE[lab]))
    return par_id


def liste(par_id, ids, types):
    return [[e for e in par_id[i] if e[2] in types] for i in ids]


def main():
    args = sys.argv[1:]
    corpus = Path(args[0]) if args else RACINE / "data" / "corpus_test2.csv"
    annotations = Path(args[1]) if len(args) > 1 else RACINE / "data" / "annotations_test2.csv"
    sortie = Path(args[2]) if len(args) > 2 else RACINE / "results"
    prefixe = "test2" if not args else "essai"
    sortie.mkdir(parents=True, exist_ok=True)

    print("== Garde-fou : tableau de Kadiga sur SON test ==")
    systemes_k = K.construire_systemes(verbeux=False)
    ok, _, _, ecarts = K.verifier_contre_kadiga(systemes_k)
    print("écart maximal :", float(ecarts.max().max()))
    if not ok:
        sys.exit("ÉCHEC du garde-fou : le tableau de Kadiga n'est pas retrouvé. ARRÊT, aucune mesure.")
    print("OK : tableau de Kadiga retrouvé à l'identique.\n")

    segments, gold = lire(corpus, annotations)
    ids = [s["id"] for s in segments]
    print(f"== Mesure sur {corpus.name} : {len(ids)} segments, {sum(len(v) for v in gold.values())} entités ==")

    preds = {
        "A": predictions_spacy(R.construire(groupes=[]), segments),
        "3a": predictions_spacy(R.construire(groupes=list(R.GROUPES)), segments),
        "3a+3b": predictions_spacy(R.construire(groupes=list(R.GROUPES), filtres=list(R.FILTRES_3B_FINAL)), segments),
        "K-B": predictions_kadiga(systemes_k["B"], segments),
        "K-C": predictions_kadiga(systemes_k["C"], segments),
        "K-D": predictions_kadiga(systemes_k["D"], segments),
    }

    lignes = []
    for k, nom in NOMS.items():
        for etiquette, types in [("PER", ["PER"]), ("ORG", ["ORG"]), ("LOC", ["LOC"]), ("DATE", ["DATE"]),
                                 ("TOUT PER+ORG+LOC", TYPES3), ("TOUT PER+ORG+LOC+DATE", TYPES4)]:
            g, p = liste(gold, ids, types), liste(preds[k], ids, types)
            ex, to = evaluer(g, p), evaluer_tolerant(g, p)
            cle = "TOUT" if etiquette.startswith("TOUT") else types[0]
            e = ex.get(cle, (0.0, 0.0, 0.0, 0))
            t = to.get(cle, (0.0, 0.0, 0.0, 0))
            n_gold = sum(len(x) for x in g)
            n_pred = sum(len(x) for x in p)
            lignes.append((nom, etiquette, n_gold, n_pred, round(e[0], 3), round(e[1], 3), round(e[2], 3),
                           round(t[0], 3), round(t[1], 3), round(t[2], 3)))
        n_form = sum(1 for i in ids for e in preds[k][i] if e[2] == "FORMATION")
        lignes.append((nom, "FORMATION prédite (support 0, hors tableau)", 0, n_form, 0, 0, 0, 0, 0, 0))
    cols = ["système", "type", "support (gold)", "prédites", "exact P", "exact R", "exact F1",
            "tolérant P", "tolérant R", "tolérant F1"]
    df = pd.DataFrame(lignes, columns=cols)
    df.to_csv(sortie / f"{prefixe}_resultats.csv", index=False, encoding="utf-8-sig")

    pd.set_option("display.width", 250, "display.max_columns", 20)
    for etiquette in ["TOUT PER+ORG+LOC", "TOUT PER+ORG+LOC+DATE", "PER", "ORG", "LOC", "DATE"]:
        print(f"\n--- {etiquette} ---")
        print(df[df["type"] == etiquette].drop(columns="type").to_string(index=False))

    # Ce qui est prédit EN PLUS (fausses) ou EN MOINS (manquées), au sens exact, pour chaque système
    texte = {s["id"]: s["fr"] for s in segments}
    ecarts = []
    for k, nom in NOMS.items():
        for i in ids:
            g, p = set(gold[i]), set(preds[k][i])
            for d, f, t in sorted(p - g):
                chev = any(t == gt and min(f, gf) > max(d, gd) for gd, gf, gt in g)
                ecarts.append((nom, i, "EN PLUS (prédite, absente du gold)", texte[i][d:f], t, d, f,
                               "frontière (chevauche une entité réelle du même type)" if chev else "sans équivalent"))
            for d, f, t in sorted(g - p):
                chev = any(t == pt and min(f, pf) > max(d, pd_) for pd_, pf, pt in p)
                ecarts.append((nom, i, "EN MOINS (dans le gold, non prédite)", texte[i][d:f], t, d, f,
                               "frontière (une prédiction du même type la chevauche)" if chev else "totalement manquée"))
    edf = pd.DataFrame(ecarts, columns=["système", "id_segment", "écart", "entité", "type", "début", "fin", "nature"])
    edf.to_csv(sortie / f"{prefixe}_ecarts.csv", index=False, encoding="utf-8-sig")
    print(f"\n{len(edf)} écarts écrits dans {prefixe}_ecarts.csv")


if __name__ == "__main__":
    main()
