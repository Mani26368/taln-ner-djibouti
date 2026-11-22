"""Mesure UNIQUE sur test3 (articles A04, A05, A06, jamais utilisés pour régler quoi que ce soit).

Systèmes (aucun n'est modifié) :
  A       spaCy fr_core_news_sm seul
  3a+3b   règles locales + filtres, version gelée au commit 087deb3 (3c est IDENTIQUE : essais tous refusés, commit 1fa9f60)
  Kadiga D  NER ré-entraîné sur le train de Kadiga (graine 42)

Garde-fou : le tableau de Kadiga sur SON test doit être retrouvé, sinon arrêt.
Valeurs non calculables : précision sans aucune prédiction, rappel et F1 sans entité réelle -> « n/d » (laissées vides dans le CSV).

Usage :
  python src/mesurer_test3.py                              # test3 -> results/test3*.csv
  python src/mesurer_test3.py CORPUS ANNOTATIONS DOSSIER   # essai à blanc sur autre chose
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import essais_3c as E
import regles_locales as R
import systemes_kadiga as K
from evaluate import evaluer, evaluer_tolerant
from mesurer_test2 import lire, liste, predictions_kadiga, predictions_spacy

RACINE = K.RACINE
TYPES3, TYPES4 = ["PER", "ORG", "LOC"], ["PER", "ORG", "LOC", "DATE"]
NOMS = {"A": "A : spaCy seul",
        "3a+3b": "3a+3b (= 3c) : règles + filtres, gelée 087deb3",
        "K-D": "Kadiga D : NER ré-entraîné"}


def nd(x):
    return None if x is None else round(float(x), 3)


def calcul(g, p, cle):
    """g, p : listes par segment. Retourne support, prédites, VP, et (P, R, F1) exact et tolérant (None = n/d)."""
    n_gold, n_pred = sum(len(x) for x in g), sum(len(x) for x in p)
    vp = sum(len(set(a) & set(b)) for a, b in zip(g, p))
    sortie = []
    for res in (evaluer(g, p), evaluer_tolerant(g, p)):
        P, Rr, F, _ = res.get(cle, (0.0, 0.0, 0.0, 0))
        sortie += [nd(P) if n_pred else None, nd(Rr) if n_gold else None, nd(F) if n_gold else None]
    return (n_gold, n_pred, vp, *sortie)


def tableau(gold, preds, ids):
    lignes = []
    for k, nom in NOMS.items():
        for etiquette, types, cle in [("PER", ["PER"], "PER"), ("ORG", ["ORG"], "ORG"), ("LOC", ["LOC"], "LOC"),
                                      ("DATE", ["DATE"], "DATE"),
                                      ("TOUT (PER+ORG+LOC+DATE)", TYPES4, "TOUT"), ("TOUT (PER+ORG+LOC)", TYPES3, "TOUT")]:
            g, p = liste(gold, ids, types), liste(preds[k], ids, types)
            lignes.append((nom, etiquette) + calcul(g, p, cle))
        n_form = sum(1 for i in ids for e in preds[k][i] if e[2] == "FORMATION")
        lignes.append((nom, "FORMATION prédite (support 0, hors tableau)", 0, n_form, 0) + (None,) * 6)
    cols = ["système", "type", "support", "prédites", "VP exact", "exact P", "exact R", "exact F1",
            "tolérant P", "tolérant R", "tolérant F1"]
    return pd.DataFrame(lignes, columns=cols)


def main():
    args = sys.argv[1:]
    corpus = Path(args[0]) if args else RACINE / "data" / "corpus_test3.csv"
    annotations = Path(args[1]) if len(args) > 1 else RACINE / "data" / "annotations_test3.csv"
    sortie = Path(args[2]) if len(args) > 2 else RACINE / "results"
    sortie.mkdir(parents=True, exist_ok=True)

    print("== Garde-fou : tableau de Kadiga sur SON test ==")
    systemes_k = K.construire_systemes(verbeux=False)
    ok, _, _, ecarts = K.verifier_contre_kadiga(systemes_k)
    print("écart maximal :", float(ecarts.max().max()))
    if not ok:
        sys.exit("ÉCHEC du garde-fou : tableau de Kadiga non retrouvé. ARRÊT, aucune mesure.")
    print("OK.\n")

    nlp_3a3b = R.construire(groupes=list(R.GROUPES), filtres=list(R.FILTRES_3B_FINAL))
    nlp_a = R.construire(groupes=[])

    def predire_tous(segments):
        return {"A": predictions_spacy(nlp_a, segments), "3a+3b": predictions_spacy(nlp_3a3b, segments),
                "K-D": predictions_kadiga(systemes_k["D"], segments)}

    # ---- mesure sur le corpus cible
    segments, gold = lire(corpus, annotations)
    ids = [s["id"] for s in segments]
    preds = predire_tous(segments)
    print(f"== {corpus.name} : {len(ids)} segments, {sum(len(v) for v in gold.values())} entités ==")
    df = tableau(gold, preds, ids)
    df.to_csv(sortie / "test3.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250, "display.max_columns", 20)
    print(df.astype(object).fillna("n/d").to_string(index=False))

    # ---- ce qui est prédit en plus / en moins
    texte = {s["id"]: s["fr"] for s in segments}
    ec = []
    for k, nom in NOMS.items():
        for i in ids:
            g, p = set(gold[i]), set(preds[k][i])
            for d, f, t in sorted(p - g):
                chev = any(t == gt and min(f, gf) > max(d, gd) for gd, gf, gt in g)
                ec.append((nom, i, "EN PLUS (prédite, absente du gold)", texte[i][d:f], t,
                           "frontière" if chev else "sans équivalent dans le gold"))
            for d, f, t in sorted(g - p):
                chev = any(t == pt and min(f, pf) > max(d, pd_) for pd_, pf, pt in p)
                ec.append((nom, i, "EN MOINS (dans le gold, non prédite)", texte[i][d:f], t,
                           "frontière" if chev else "totalement manquée"))
    pd.DataFrame(ec, columns=["système", "id_segment", "écart", "entité", "type", "nature"]).to_csv(
        sortie / "test3_ecarts.csv", index=False, encoding="utf-8-sig")

    # ---- comparaison avec les articles de réglage (surapprentissage ?)
    seg12, gold12 = E.charger()
    ids12 = [s["id"] for s in seg12]
    preds12 = predire_tous(seg12)
    jeux = {"dev (84 seg., réglage)": [s["id"] for s in seg12 if s["split"] == "dev"],
            "test 1 (42 seg., vu)": [s["id"] for s in seg12 if s["split"] == "test"],
            "test 2 (42 seg., vu)": [s["id"] for s in seg12 if s["split"] == "test2"],
            "12 articles vus (168 seg.)": ids12}
    lignes = []
    for k, nom in NOMS.items():
        for jeu, idj in list(jeux.items()) + [(f"{corpus.stem} (JAMAIS VU)", None)]:
            g_all, p_all, idl = (gold12, preds12[k], idj) if idj is not None else (gold, preds[k], ids)
            vals = {}
            for lib, types in [("4", TYPES4), ("3", TYPES3)]:
                g, p = liste(g_all, idl, types), liste(p_all, idl, types)
                vals[lib] = (calcul(g, p, "TOUT"))
            lignes.append((nom, jeu, len(idl), vals["4"][0], nd(vals["4"][5]), nd(vals["4"][8]),
                           vals["3"][0], nd(vals["3"][5]), nd(vals["3"][8])))
    cmp_df = pd.DataFrame(lignes, columns=["système", "jeu", "segments", "support (4 types)", "F1 exact (4 types)",
                                           "F1 tolérant (4 types)", "support (PER+ORG+LOC)", "F1 exact (PER+ORG+LOC)",
                                           "F1 tolérant (PER+ORG+LOC)"])
    cmp_df.to_csv(sortie / "test3_comparaison_reglage.csv", index=False, encoding="utf-8-sig")
    print("\n== Comparaison avec les articles de réglage ==")
    print(cmp_df.astype(object).fillna("n/d").to_string(index=False))


if __name__ == "__main__":
    main()
