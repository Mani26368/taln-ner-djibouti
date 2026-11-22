"""Prépare le second test : data/corpus_test2.csv (articles A07, A09, A13).

Même méthode que src/preparer_corpus.py, mais sur des articles qui n'ont servi à AUCUNE règle :
1. on garde A07, A09, A13 ;
2. on enlève les segments de moins de MIN_TOKENS tokens (même seuil que pour le sous-corpus : 8 tokens ou plus) ;
3. dans chaque article, on prend N_PAR_ARTICLE segments régulièrement espacés (aucun hasard).

Ne modifie PAS data/corpus_ner.csv. Lancer : python src/preparer_test2.py
"""
import csv
from pathlib import Path

from preparer_corpus import MIN_TOKENS, N_PAR_ARTICLE, COLONNES, choisir_regulierement

RACINE = Path(__file__).resolve().parent.parent
ENTREE = RACINE / "data" / "corpus_bilingue_so.csv"
SORTIE = RACINE / "data" / "corpus_test2.csv"
ARTICLES = ["A07", "A09", "A13"]


def main():
    with open(ENTREE, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f))
    sortie = []
    for article in ARTICLES:
        candidats = [r for r in lignes
                     if r["id"].split("_")[0] == article and int(r["nb_tokens_fr"]) >= MIN_TOKENS]
        for r in choisir_regulierement(candidats, N_PAR_ARTICLE):
            ligne = {c: r[c] for c in COLONNES}
            ligne["split"] = "test2"
            sortie.append(ligne)
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES + ["split"])
        w.writeheader()
        w.writerows(sortie)
    print(f"{len(sortie)} segments écrits dans {SORTIE.name}")
    for article in ARTICLES:
        print(f"  {article}: {sum(1 for r in sortie if r['id'].startswith(article + '_'))}")


if __name__ == "__main__":
    main()
