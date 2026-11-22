"""Prépare le sous-corpus à annoter : data/corpus_ner.csv.

Sélection reproductible (aucun hasard) :
1. On garde les articles choisis.
2. On enlève les segments de moins de MIN_TOKENS tokens.
3. Dans chaque article, on prend N_PAR_ARTICLE segments régulièrement espacés
   (du début à la fin de l'article). Si l'article en a moins, on les prend tous.

Lancer : python src/preparer_corpus.py
"""
import csv
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ENTREE = RACINE / "data" / "corpus_bilingue_so.csv"
SORTIE = RACINE / "data" / "corpus_ner.csv"

DEV = ["A01", "A02", "A08", "A10", "A12", "A14"]
TEST = ["A03", "A11", "A15"]
MIN_TOKENS = 8
N_PAR_ARTICLE = 14
COLONNES = ["id", "titre", "rubrique", "url", "date", "fr"]


def choisir_regulierement(liste, k):
    """Choisit k éléments espacés régulièrement, premier et dernier inclus."""
    n = len(liste)
    if n <= k:
        return list(liste)
    # indices 0, ..., n-1 répartis en k points
    indices = [round(i * (n - 1) / (k - 1)) for i in range(k)]
    return [liste[i] for i in indices]


def main():
    with open(ENTREE, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f))

    sortie = []
    for article in DEV + TEST:
        split = "dev" if article in DEV else "test"
        candidats = [
            r for r in lignes
            if r["id"].split("_")[0] == article and int(r["nb_tokens_fr"]) >= MIN_TOKENS
        ]
        for r in choisir_regulierement(candidats, N_PAR_ARTICLE):
            ligne = {c: r[c] for c in COLONNES}
            ligne["split"] = split
            sortie.append(ligne)

    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES + ["split"])
        w.writeheader()
        w.writerows(sortie)

    print(f"{len(sortie)} segments écrits dans {SORTIE.name}")
    for article in DEV + TEST:
        n = sum(1 for r in sortie if r["id"].startswith(article + "_"))
        print(f"  {article}: {n}")


if __name__ == "__main__":
    main()
