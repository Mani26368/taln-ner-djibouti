"""Construit sentences.csv et entities.csv (train / val / test, 60/20/20) depuis corpus_annote.csv.

Usage (depuis la racine du projet) :  python src/build_dataset.py

Entree  : data/corpus/corpus_annote.csv  (id, source, section, texte_annote)
          texte_annote utilise le balisage  [texte|ETIQUETTE]
Sorties : data/corpus/sentences.csv  (id, split, source, section, bloc, text)
          data/corpus/entities.csv   (id, split, start, end, label, text)   <- une ligne par entite

Le decoupage se fait par BLOCS (source + premiere partie de la section), jamais phrase par phrase :
les phrases d'un meme article partagent leurs entites, un tirage au hasard fuirait du train vers le test.
Les blocs sont affectes par une recherche aleatoire a graine fixe (SEED) qui vise 60/20/20 en phrases
et exige assez d'entites de chaque classe principale en validation et en test.
"""
import csv
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus"
SEED = 42
RATIOS = {"train": 0.6, "val": 0.2, "test": 0.2}
LABELS = ["ORG", "LOC", "PER", "DATE", "FORM"]
MIN_VAL_TEST = {"ORG": 5, "LOC": 5, "DATE": 5, "PER": 3, "FORM": 3}   # minimum d'entites en val ET en test

SPAN = re.compile(r"\[([^\[\]|]+)\|([A-Z]+)\]")


def parse(row):
    marked = row["texte_annote"]
    parts, ents, pos, last = [], [], 0, 0
    for m in SPAN.finditer(marked):
        parts.append(marked[last:m.start()])
        pos += m.start() - last
        surface, label = m.group(1), m.group(2)
        assert label in LABELS, f"{row['id']}: etiquette inconnue {label}"
        ents.append((pos, pos + len(surface), label, surface))
        parts.append(surface)
        pos += len(surface)
        last = m.end()
    parts.append(marked[last:])
    text = "".join(parts)
    for s, e, _, surf in ents:
        assert text[s:e] == surf, f"{row['id']}: offset faux"
    for a, b in zip(ents, ents[1:]):
        assert a[1] <= b[0], f"{row['id']}: chevauchement"
    assert "[" not in text and "|" not in text, f"{row['id']}: balisage mal ferme"
    return text, ents


def affecter_blocs(blocs, seed=SEED, essais=30000):
    """blocs : {nom: (n_phrases, Counter(etiquettes))}. Retourne {nom: split}."""
    rng = random.Random(seed)
    noms = sorted(blocs)
    n_tot = sum(blocs[b][0] for b in noms)
    meilleur, meilleur_cout = None, float("inf")
    for _ in range(essais):
        aff = {b: rng.choice(("train", "val", "test")) for b in noms}
        n = Counter()
        lab = {s: Counter() for s in RATIOS}
        for b, s in aff.items():
            n[s] += blocs[b][0]
            lab[s].update(blocs[b][1])
        cout = sum(abs(n[s] / n_tot - r) for s, r in RATIOS.items()) * 10
        for s in ("val", "test"):
            for l, mini in MIN_VAL_TEST.items():
                if lab[s][l] < mini:
                    cout += 5 + (mini - lab[s][l])
        if lab["train"]["FORM"] < 3:
            cout += 3 + (3 - lab["train"]["FORM"])   # le train doit contenir des exemples de formation
        if cout < meilleur_cout:
            meilleur, meilleur_cout = aff, cout
    return meilleur


def main():
    with open(CORPUS / "corpus_annote.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "identifiants en double"
    assert len({r["texte_annote"] for r in rows}) == len(rows), "phrases en double"

    parsed = {r["id"]: parse(r) for r in rows}
    bloc_de = {r["id"]: f"{r['source']}|{r['section'].split('/')[0].strip()}" for r in rows}

    blocs = defaultdict(lambda: [0, Counter()])
    for i, (_, ents) in parsed.items():
        blocs[bloc_de[i]][0] += 1
        blocs[bloc_de[i]][1].update(e[2] for e in ents)
    aff = affecter_blocs({b: (v[0], v[1]) for b, v in blocs.items()})

    with open(CORPUS / "sentences.csv", "w", encoding="utf-8", newline="") as fs, \
         open(CORPUS / "entities.csv", "w", encoding="utf-8", newline="") as fe:
        ws, we = csv.writer(fs), csv.writer(fe)
        ws.writerow(["id", "split", "source", "section", "bloc", "text"])
        we.writerow(["id", "split", "start", "end", "label", "text"])
        for r in rows:
            split = aff[bloc_de[r["id"]]]
            text, ents = parsed[r["id"]]
            ws.writerow([r["id"], split, r["source"], r["section"], bloc_de[r["id"]], text])
            for s, e, lab, surf in ents:
                we.writerow([r["id"], split, s, e, lab, surf])

    # Rapport
    print(f"Graine {SEED} | {len(rows)} phrases, {len(blocs)} blocs\n")
    stats = {s: Counter() for s in RATIOS}
    n_phr = Counter()
    vus = {s: set() for s in RATIOS}
    for r in rows:
        s = aff[bloc_de[r["id"]]]
        n_phr[s] += 1
        for _, _, lab, surf in parsed[r["id"]][1]:
            stats[s][lab] += 1
            vus[s].add((surf, lab))
    print(f"{'split':6} {'phrases':>8} {'%':>5}  " + "  ".join(f"{l:>4}" for l in LABELS) + "  total")
    for s in RATIOS:
        tot = sum(stats[s].values())
        print(f"{s:6} {n_phr[s]:8d} {100*n_phr[s]/len(rows):5.0f}  "
              + "  ".join(f"{stats[s][l]:4d}" for l in LABELS) + f"  {tot:5d}")
    print("\nBlocs par split :")
    for s in RATIOS:
        print(f"  {s}: " + " ; ".join(f"{b} ({blocs[b][0]})" for b in sorted(blocs) if aff[b] == s))
    print("\nEntites (forme, etiquette) distinctes deja vues dans le train :")
    for s in ("val", "test"):
        print(f"  {s}: {len(vus[s] & vus['train'])} / {len(vus[s])}")
    vides = [l for l in LABELS if any(stats[s][l] == 0 for s in RATIOS)]
    if vides:
        print(f"\n/!\\ Etiquettes absentes d'au moins un split : {vides}")


if __name__ == "__main__":
    main()
