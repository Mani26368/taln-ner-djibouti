"""Essais de la version 3c, mesurés sur les 12 articles DÉJÀ VUS (dev + test + test2 = 168 segments).

Les essais sont faits dans l'ordre, CUMULATIFS : chaque essai est comparé à la meilleure version gardée jusque-là.
Critères de décision, fixés AVANT de voir les chiffres :
  - F1 exact (TOUT PER+ORG+LOC+DATE) en hausse d'au moins +0.02   ("de façon nette")
  - F1 tolérant (TOUT) ne baisse pas de plus de 0.005
  - l'essai change les prédictions d'au moins 2 segments différents (sinon : règle pour un seul exemple, refusée)

Aucun seuil n'est réglé, aucun modèle n'est ré-entraîné.
Lancer : python src/essais_3c.py   ->  results/essais_3c.csv
"""
import csv
import sys
from pathlib import Path

import pandas as pd
import spacy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regles_3c as C
import regles_locales as R
from evaluate import evaluer, evaluer_tolerant

RACINE = Path(__file__).resolve().parent.parent
TYPES4 = ["PER", "ORG", "LOC", "DATE"]
SEUIL_F1 = 0.02
TOLERANCE_TOL = 0.005
MIN_SEGMENTS = 2


def charger():
    segments, gold = [], {}
    for corpus, ann in [("corpus_ner.csv", "annotations.csv"), ("corpus_test2.csv", "annotations_test2.csv")]:
        with open(RACINE / "data" / corpus, encoding="utf-8", newline="") as f:
            for s in csv.DictReader(f):
                segments.append(s)
                gold[s["id"]] = []
        with open(RACINE / "data" / ann, encoding="utf-8", newline="") as f:
            for a in csv.DictReader(f):
                gold[a["id_segment"]].append((int(a["debut"]), int(a["fin"]), a["type"]))
    return segments, gold


def predire(nlp, segments):
    return {s["id"]: sorted((e.start_char, e.end_char, e.label_) for e in doc.ents if e.label_ in TYPES4)
            for s, doc in zip(segments, nlp.pipe([s["fr"] for s in segments]))}


def f1(gold, pred, ids, types, fn):
    g = [[e for e in gold[i] if e[2] in types] for i in ids]
    p = [[e for e in pred[i] if e[2] in types] for i in ids]
    return fn(g, p)["TOUT"][2]


def scores(gold, pred, ids):
    return {"exact4": f1(gold, pred, ids, TYPES4, evaluer), "tol4": f1(gold, pred, ids, TYPES4, evaluer_tolerant),
            "exact3": f1(gold, pred, ids, TYPES4[:3], evaluer), "tol3": f1(gold, pred, ids, TYPES4[:3], evaluer_tolerant)}


def main():
    segments, gold = charger()
    ids = [s["id"] for s in segments]
    n_ent = sum(len(v) for v in gold.values())
    print(f"{len(ids)} segments, {n_ent} entités (12 articles déjà vus)\n")

    # Contrôle : 3c sans option = 3a+3b gelée (commit 087deb3)
    gelee = predire(R.construire(groupes=list(R.GROUPES), filtres=list(R.FILTRES_3B_FINAL)), segments)
    ref = predire(C.construire_3c(), segments)
    if gelee != ref:
        diff = [i for i in ids if gelee[i] != ref[i]]
        sys.exit(f"ÉCHEC : 3c sans option diffère de 3a+3b sur {len(diff)} segments : {diff[:5]}. ARRÊT.")
    print("Contrôle OK : 3c sans option = 3a+3b gelée (prédictions identiques sur les 168 segments).\n")

    config = {"modele": "fr_core_news_sm", "djibouti_ne_coupe_pas": False, "annee_seule": False, "habitants": False,
              "remplir_apres_filtre": True}
    courant, s_courant = ref, scores(gold, ref, ids)
    essais = [
        ("a) modèle md", {"modele": "fr_core_news_md"}),
        ("a) modèle lg", {"modele": "fr_core_news_lg"}),
        ("b1) « Djibouti » (1re version : rattrapage AVANT le filtre, fautive)", {"djibouti_ne_coupe_pas": True, "remplir_apres_filtre": False}),
        ("b2) « Djibouti » ne coupe pas une ORG (rattrapage APRÈS le filtre)", {"djibouti_ne_coupe_pas": True}),
        ("c) année seule en contexte", {"annee_seule": True}),
        ("d) noms d'habitants", {"habitants": True}),
    ]
    lignes = []
    for nom, modif in essais:
        essai_cfg = {**config, **modif}
        try:
            pred = predire(C.construire_3c(**essai_cfg), segments)
        except OSError as e:
            print(f"- {nom} : modèle non installé -> essai SAUTÉ ({str(e)[:60]})")
            lignes.append((nom, s_courant["exact4"], None, s_courant["tol4"], None, 0, "SAUTÉ", "modèle non installé"))
            continue
        s = scores(gold, pred, ids)
        n_seg = sum(1 for i in ids if pred[i] != courant[i])
        d_ex, d_tol = s["exact4"] - s_courant["exact4"], s["tol4"] - s_courant["tol4"]
        raisons = []
        if d_ex < SEUIL_F1:
            raisons.append(f"gain exact {d_ex:+.3f} < +{SEUIL_F1}")
        if d_tol < -TOLERANCE_TOL:
            raisons.append(f"tolérant baisse de {d_tol:+.3f}")
        if n_seg < MIN_SEGMENTS:
            raisons.append(f"change seulement {n_seg} segment (règle pour un seul exemple)")
        garde = not raisons
        pourquoi = ("gain net : exact " + f"{d_ex:+.3f}, tolérant {d_tol:+.3f}, {n_seg} segments") if garde else "; ".join(raisons)
        lignes.append((nom, s_courant["exact4"], s["exact4"], s_courant["tol4"], s["tol4"], n_seg,
                       "GARDÉ" if garde else "non", pourquoi))
        print(f"- {nom:70} exact {s_courant['exact4']:.3f} -> {s['exact4']:.3f} | tolérant {s_courant['tol4']:.3f} -> {s['tol4']:.3f} "
              f"| {n_seg} segments changés | {'GARDÉ' if garde else 'non'} : {pourquoi}")
        if garde:
            config, courant, s_courant = essai_cfg, pred, s

    df = pd.DataFrame(lignes, columns=["essai", "F1 exact avant", "F1 exact après", "F1 tolérant avant",
                                       "F1 tolérant après", "segments changés", "gardé", "pourquoi"])
    for c in ["F1 exact avant", "F1 exact après", "F1 tolérant avant", "F1 tolérant après"]:
        df[c] = df[c].astype(float).round(3)
    (RACINE / "results").mkdir(exist_ok=True)
    df.to_csv(RACINE / "results" / "essais_3c.csv", index=False, encoding="utf-8-sig")
    print("\nConfiguration finale 3c :", config)
    print("F1 (12 articles, 4 types) : exact %.3f | tolérant %.3f   [PER+ORG+LOC seuls : exact %.3f | tolérant %.3f]"
          % (s_courant["exact4"], s_courant["tol4"], s_courant["exact3"], s_courant["tol3"]))


if __name__ == "__main__":
    main()
