"""Scores par type de nos systèmes sur le dev et le test 1 -> results/scores_dev_test1.csv

Ces deux jeux ont servi à régler les règles (dev) ou ont été lus pendant le développement (test 1) :
les scores sont donc OPTIMISTES. Ils servent à comparer, pas à annoncer une performance.

Systèmes (aucun n'est modifié) : A (spaCy seul), 3a (règles locales), 3a+3b (règles + filtres, gelée 087deb3).
Les systèmes de Kadiga sur ces jeux sont déjà dans results/test_externe_lanation.csv.

Lancer : python src/scores_dev_test1.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import essais_3c as E
import regles_locales as R
from mesurer_test2 import liste, predictions_spacy
from mesurer_test3 import calcul

RACINE = Path(__file__).resolve().parent.parent
TYPES3, TYPES4 = ["PER", "ORG", "LOC"], ["PER", "ORG", "LOC", "DATE"]
STATUT = {"dev": "optimiste (a servi à écrire les règles)", "test": "optimiste (lu pendant le développement)"}
SYSTEMES = {
    "A : spaCy seul": lambda: R.construire(groupes=[]),
    "3a : + règles locales": lambda: R.construire(groupes=list(R.GROUPES)),
    "3a+3b : + filtres (3b finale, gelée 087deb3)": lambda: R.construire(groupes=list(R.GROUPES),
                                                                       filtres=list(R.FILTRES_3B_FINAL)),
}


def main():
    segments, gold = E.charger()                       # 168 segments : dev, test, test2
    lignes = []
    for jeu in ["dev", "test"]:
        seg = [s for s in segments if s["split"] == jeu]
        ids = [s["id"] for s in seg]
        for nom, fabrique in SYSTEMES.items():
            preds = predictions_spacy(fabrique(), seg)
            for etiquette, types, cle in [("PER", ["PER"], "PER"), ("ORG", ["ORG"], "ORG"), ("LOC", ["LOC"], "LOC"),
                                          ("DATE", ["DATE"], "DATE"),
                                          ("TOUT (PER+ORG+LOC+DATE)", TYPES4, "TOUT"),
                                          ("TOUT (PER+ORG+LOC)", TYPES3, "TOUT")]:
                g, p = liste(gold, ids, types), liste(preds, ids, types)
                lignes.append((nom, jeu, STATUT[jeu], etiquette) + calcul(g, p, cle))
    cols = ["système", "jeu", "statut", "type", "support", "prédites", "VP exact", "exact P", "exact R", "exact F1",
            "tolérant P", "tolérant R", "tolérant F1"]
    df = pd.DataFrame(lignes, columns=cols)
    (RACINE / "results").mkdir(exist_ok=True)
    df.to_csv(RACINE / "results" / "scores_dev_test1.csv", index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250, "display.max_columns", 20)
    print(df[df["type"].str.startswith("TOUT (PER+ORG+LOC+DATE)")][
        ["système", "jeu", "support", "exact F1", "tolérant F1"]].to_string(index=False))
    print(f"\n{len(df)} lignes écrites dans results/scores_dev_test1.csv")


if __name__ == "__main__":
    main()
