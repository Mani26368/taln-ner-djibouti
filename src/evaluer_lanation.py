"""Test externe : les systèmes A, B, C, D de Kadiga (sans aucune modification) sur nos 126 segments de La Nation.

Étapes :
1. On reconstruit A, B, C, D (src/systemes_kadiga.py) et on vérifie qu'on retrouve SON tableau sur SON test.
   Si ce n'est pas le cas, on s'arrête (code de sortie 2).
2. On applique A, B, C, D à data/corpus_ner.csv et on évalue avec src/evaluate.py (correspondance exacte).
3. Contrôle croisé : A doit redonner la Section 2 du notebook (PER/ORG/LOC).
4. On écrit results/test_externe_lanation.csv et results/erreurs_lanation.csv (erreurs du meilleur système).

Aucune règle n'est modifiée ici. Lancer : python src/evaluer_lanation.py
"""
import csv
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import systemes_kadiga as K
from evaluate import evaluer

RACINE = K.RACINE
SORTIE = RACINE / "results"
TYPES = ["PER", "ORG", "LOC", "DATE"]          # tableau principal
TYPES3 = ["PER", "ORG", "LOC"]                 # types que spaCy sait produire
# nos types -> types de Kadiga (seule FORMATION s'appelle FORM chez elle)
VERS_NOTRE = {"PER": "PER", "ORG": "ORG", "LOC": "LOC", "DATE": "DATE", "FORM": "FORMATION"}


def lire_corpus():
    with open(RACINE / "data" / "corpus_ner.csv", encoding="utf-8", newline="") as f:
        segments = list(csv.DictReader(f))
    gold = {s["id"]: [] for s in segments}
    with open(RACINE / "data" / "annotations.csv", encoding="utf-8", newline="") as f:
        for a in csv.DictReader(f):
            gold[a["id_segment"]].append((int(a["debut"]), int(a["fin"]), a["type"]))
    return segments, gold


def predictions_par_segment(nlp_k, segments):
    """Applique un système de Kadiga (sa fonction predire) puis range les entités par segment."""
    docs = [{"id": s["id"], "text": s["fr"]} for s in segments]
    brut = K.predire(nlp_k, docs)
    par_id = {s["id"]: [] for s in segments}
    for (i, d, f, lab) in sorted(brut):
        par_id[i].append((d, f, VERS_NOTRE[lab]))
    return par_id


def filtrer(par_id, ids, types):
    return [[e for e in par_id[i] if e[2] in types] for i in ids]


def mesurer(gold, pred, ids, types):
    """Évaluation avec src/evaluate.py. Retourne {type ou 'TOUT': (P, R, F1, support, VP, FP, FN)}."""
    g, p = filtrer(gold, ids, types), filtrer(pred, ids, types)
    res = evaluer(g, p)
    out = {}
    for label, (pr, ra, f1, sup) in res.items():
        vp = round(ra * sup) if sup else 0
        n_pred = sum(1 for liste in p for e in liste if (label == "TOUT" or e[2] == label))
        out[label] = (pr, ra, f1, sup, vp, n_pred - vp, sup - vp)
    for t in types:                       # type absent partout (support 0 et rien prédit)
        out.setdefault(t, (0.0, 0.0, 0.0, 0, 0, 0, 0))
    return out


def classer_erreurs(texte, g, p):
    """Range les erreurs d'un segment : manquée, fausse détection, mauvais type, mauvaise frontière.
    g, p : listes de (début, fin, type). Une paire gold/prédit qui se chevauchent = UNE erreur."""
    g, p = set(g), set(p)
    manq, faux = sorted(g - p), sorted(p - g)
    chev = lambda a, b: min(a[1], b[1]) - max(a[0], b[0])
    paires = sorted(((chev(a, b), a, b) for a in manq for b in faux if chev(a, b) > 0),
                    key=lambda x: (-x[0], x[1], x[2]))
    pris_g, pris_p, lignes = set(), set(), []
    for _, a, b in paires:
        if a in pris_g or b in pris_p:
            continue
        pris_g.add(a); pris_p.add(b)
        if (a[0], a[1]) == (b[0], b[1]):
            genre = "mauvais type"
        elif a[2] == b[2]:
            genre = "mauvaise frontière"
        else:
            genre = "mauvaise frontière et mauvais type"
        lignes.append((genre, texte[b[0]:b[1]], b[2], b[0], b[1], texte[a[0]:a[1]], a[2], a[0], a[1]))
    for a in manq:
        if a not in pris_g:
            lignes.append(("manquée", "", "", "", "", texte[a[0]:a[1]], a[2], a[0], a[1]))
    for b in faux:
        if b not in pris_p:
            lignes.append(("fausse détection", texte[b[0]:b[1]], b[2], b[0], b[1], "", "", "", ""))
    return lignes


def main():
    t0 = time.time()
    print("== 1. Reconstruction de A, B, C, D (corpus de Kadiga, graine 42) ==")
    systemes = K.construire_systemes()
    ok, recalcule, ref, ecarts = K.verifier_contre_kadiga(systemes)
    pd.set_option("display.width", 220)
    print("\nTableau recalculé sur le TEST de Kadiga :\n", recalcule.to_string(index=False))
    print("\nTableau de Kadiga (kadiga/results/tableau_comparatif.csv) :\n", ref.to_string(index=False))
    print("\nÉcart absolu maximal :", float(ecarts.max().max()))
    if not ok:
        print("\n>>> ÉCHEC : le script ne redonne pas le tableau de Kadiga. ARRÊT (aucune mesure sur La Nation).")
        print(ecarts.to_string())
        sys.exit(2)
    print(">>> OK : le tableau de Kadiga est retrouvé à l'identique.\n")

    print("== 2. Application à nos 126 segments ==")
    segments, gold = lire_corpus()
    ids_all = [s["id"] for s in segments]
    split = {s["id"]: s["split"] for s in segments}
    portees = {"126 segments": ids_all,
               "dev (84)": [i for i in ids_all if split[i] == "dev"],
               "test (42)": [i for i in ids_all if split[i] == "test"]}
    preds = {k: predictions_par_segment(nlp_k, segments) for k, nlp_k in systemes.items()}

    lignes_csv, resume = [], {}
    for k in "ABCD":
        for nom_portee, ids in portees.items():
            quatre = mesurer(gold, preds[k], ids, TYPES)
            trois = mesurer(gold, preds[k], ids, TYPES3)
            resume[(k, nom_portee)] = (quatre, trois)
            for t in TYPES:
                lignes_csv.append((K.NOMS[k], nom_portee, t) + quatre[t])
            lignes_csv.append((K.NOMS[k], nom_portee, "TOUT (PER+ORG+LOC+DATE)") + quatre["TOUT"])
            lignes_csv.append((K.NOMS[k], nom_portee, "TOUT (PER+ORG+LOC)") + trois["TOUT"])
        n_form = sum(1 for i in ids_all for e in preds[k][i] if e[2] == "FORMATION")
        lignes_csv.append((K.NOMS[k], "126 segments", "FORMATION (prédites, support 0 : hors tableau principal)",
                           0.0, 0.0, 0.0, 0, 0, n_form, 0))

    colonnes = ["système", "périmètre", "type", "précision", "rappel", "F1", "support", "VP", "FP", "FN"]
    SORTIE.mkdir(exist_ok=True)
    df = pd.DataFrame(lignes_csv, columns=colonnes)
    df[["précision", "rappel", "F1"]] = df[["précision", "rappel", "F1"]].round(3)
    df.to_csv(SORTIE / "test_externe_lanation.csv", index=False, encoding="utf-8-sig")

    print("\nRésultats sur les 126 segments (correspondance exacte, src/evaluate.py) :")
    for k in "ABCD":
        print(f"\n--- {K.NOMS[k]} ---")
        sous = df[(df["système"] == K.NOMS[k]) & (df["périmètre"] == "126 segments")]
        print(sous.drop(columns=["système", "périmètre"]).to_string(index=False))

    print("\n== 3. Contrôle croisé : système A vs Section 2 du notebook (PER/ORG/LOC) ==")
    attendu = {"test (42)": (0.47, 0.58, 0.52), "dev (84)": (0.49, 0.72, 0.59)}
    for portee, att in attendu.items():
        p, r, f = resume[("A", portee)][1]["TOUT"][:3]
        mesure = (round(p, 2), round(r, 2), round(f, 2))
        print(f"  {portee:10} A mesuré (P,R,F1) = {mesure} | attendu (Section 2) = {att} -> {'IDENTIQUE' if mesure == att else 'DIFFÉRENT'}")

    print("\n== 4. Erreurs du meilleur système ==")
    meilleur = max("ABCD", key=lambda k: resume[(k, "126 segments")][0]["TOUT"][2])
    scores_f1 = {k: round(resume[(k, "126 segments")][0]["TOUT"][2], 3) for k in "ABCD"}
    print("F1 TOUT (PER+ORG+LOC+DATE) sur 126 segments :", scores_f1, "-> meilleur :", K.NOMS[meilleur])
    texte = {s["id"]: s["fr"] for s in segments}
    erreurs = []
    for i in ids_all:
        g = gold[i]
        p = preds[meilleur][i]                       # toutes les prédictions, FORMATION incluse
        for ligne in classer_erreurs(texte[i], g, p):
            erreurs.append((K.NOMS[meilleur], split[i], i) + ligne + (texte[i],))
    cols_err = ["système", "split", "id_segment", "type_erreur", "entité_prédite", "type_prédit", "début_prédit",
                "fin_prédit", "entité_réelle", "type_réel", "début_réel", "fin_réel", "phrase"]
    edf = pd.DataFrame(erreurs, columns=cols_err)
    edf.insert(len(cols_err) - 1, "hypothèse_cause", "")
    edf.to_csv(SORTIE / "erreurs_lanation.csv", index=False, encoding="utf-8-sig")
    print(edf["type_erreur"].value_counts().to_string())
    print(f"\n{len(edf)} erreurs écrites dans results/erreurs_lanation.csv")
    print(f"\nTemps total : {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
