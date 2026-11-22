"""Vérifie data/annotations.csv.

Contrôles par ligne :
- texte[debut:fin] == entite
- le type est dans la liste
- pas de doublon exact (même segment, même début, même fin, même type)
Contrôles en plus :
- le texte est identique à celui de data/corpus_ner.csv, et le split aussi
- pas de chevauchement entre deux entités d'un même segment (règle du guide)

Affiche ensuite les comptes.
Lancer : python src/verifier_annotations.py [fichier.csv]
(sans argument, vérifie data/annotations.csv)
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
TYPES = ["ORG", "LOC", "PER", "DATE", "FORMATION"]


def lire(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    corpus = {r["id"]: r for r in lire(RACINE / "data" / "corpus_ner.csv")}
    # Fichier à vérifier : argument facultatif (utile pour tester sur un fichier cassé)
    fichier = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "data" / "annotations.csv"
    lignes = lire(fichier)
    erreurs = []
    vus = set()
    par_segment = defaultdict(list)

    for i, l in enumerate(lignes, start=2):  # ligne 1 = en-tête
        seg, ent, typ = l["id_segment"], l["entite"], l["type"]
        debut, fin = int(l["debut"]), int(l["fin"])
        if seg not in corpus:
            erreurs.append(f"ligne {i}: segment inconnu {seg}")
            continue
        if l["texte"] != corpus[seg]["fr"]:
            erreurs.append(f"ligne {i}: texte différent du corpus ({seg})")
        if l["split"] != corpus[seg]["split"]:
            erreurs.append(f"ligne {i}: split différent du corpus ({seg})")
        if l["texte"][debut:fin] != ent:
            erreurs.append(f"ligne {i}: texte[{debut}:{fin}]={l['texte'][debut:fin]!r} != {ent!r}")
        if typ not in TYPES:
            erreurs.append(f"ligne {i}: type inconnu {typ!r}")
        if l["a_verifier"] not in ("oui", "non"):
            erreurs.append(f"ligne {i}: a_verifier doit être oui ou non")
        cle = (seg, debut, fin, typ)
        if cle in vus:
            erreurs.append(f"ligne {i}: doublon exact {cle}")
        vus.add(cle)
        par_segment[seg].append((debut, fin, ent, i))

    for seg, ents in par_segment.items():
        ents.sort()
        for (d1, f1, e1, l1), (d2, f2, e2, l2) in zip(ents, ents[1:]):
            if d2 < f1:
                erreurs.append(f"chevauchement dans {seg}: {e1!r} (ligne {l1}) et {e2!r} (ligne {l2})")

    if erreurs:
        print(f"{len(erreurs)} ERREUR(S) :")
        for e in erreurs:
            print("  -", e)
        sys.exit(1)
    print("0 erreur.\n")

    splits = ["dev", "test"]
    print("Segments par split (dans le sous-corpus) :")
    for s in splits:
        total = sum(1 for r in corpus.values() if r["split"] == s)
        avec = len({l["id_segment"] for l in lignes if l["split"] == s})
        print(f"  {s:<5} {total} segments dont {avec} avec au moins une entité")

    print("\nEntités par type et par split :")
    compte = Counter((l["type"], l["split"]) for l in lignes)
    print(f"  {'Type':<10}{'dev':>6}{'test':>6}{'total':>7}")
    for t in TYPES:
        d, te = compte[(t, "dev")], compte[(t, "test")]
        print(f"  {t:<10}{d:>6}{te:>6}{d + te:>7}")
    d = sum(compte[(t, "dev")] for t in TYPES)
    te = sum(compte[(t, "test")] for t in TYPES)
    print(f"  {'TOTAL':<10}{d:>6}{te:>6}{d + te:>7}")

    print(f"\nCas a_verifier = oui : {sum(1 for l in lignes if l['a_verifier'] == 'oui')}")


if __name__ == "__main__":
    main()
