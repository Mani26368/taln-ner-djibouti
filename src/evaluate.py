"""Évaluation du NER : précision, rappel, F1.

Une entité est (début, fin, type). Elle est JUSTE seulement si
le début, la fin ET le type sont exactement les mêmes que dans la vérité terrain.

- précision = entités justes / entités prédites
- rappel    = entités justes / entités réelles
- F1        = 2 * précision * rappel / (précision + rappel)
"""
from collections import defaultdict


def _prf(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    rappel = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * rappel / (precision + rappel) if (precision + rappel) else 0.0
    return precision, rappel, f1


def evaluer(gold, pred):
    """gold, pred : listes (une par texte) de listes d'entités (debut, fin, type).

    Retourne un dictionnaire {type ou 'TOUT': (précision, rappel, F1, support)}.
    """
    assert len(gold) == len(pred), "Même nombre de textes attendu"
    compte = defaultdict(lambda: [0, 0, 0])  # tp, fp, fn
    for g_doc, p_doc in zip(gold, pred):
        g, p = set(g_doc), set(p_doc)
        for ent in p & g:
            compte[ent[2]][0] += 1
        for ent in p - g:
            compte[ent[2]][1] += 1
        for ent in g - p:
            compte[ent[2]][2] += 1
    resultats = {}
    total = [0, 0, 0]
    for label, (tp, fp, fn) in sorted(compte.items()):
        p, r, f = _prf(tp, fp, fn)
        resultats[label] = (p, r, f, tp + fn)
        total[0] += tp
        total[1] += fp
        total[2] += fn
    p, r, f = _prf(*total)
    resultats["TOUT"] = (p, r, f, total[0] + total[2])
    return resultats


def erreurs(texte, g_doc, p_doc):
    """Liste les erreurs d'un texte : (genre, entité).

    Genres : 'manquée' (non détectée), 'fausse' (détectée à tort).
    Une 'fausse' avec le même texte qu'une 'manquée' = mauvaise frontière ou mauvais type.
    """
    g, p = set(g_doc), set(p_doc)
    out = []
    for e in sorted(g - p):
        out.append(("manquée", e, texte[e[0]:e[1]]))
    for e in sorted(p - g):
        out.append(("fausse", e, texte[e[0]:e[1]]))
    return out


def afficher(resultats):
    print(f"{'Type':<12}{'Précision':>10}{'Rappel':>10}{'F1':>8}{'Support':>9}")
    for label, (p, r, f, s) in resultats.items():
        print(f"{label:<12}{p:>10.2f}{r:>10.2f}{f:>8.2f}{s:>9}")


if __name__ == "__main__":
    # Petit exemple pour comprendre (pas de vraies données).
    texte = "Le CRMN est à l'Université de Djibouti."
    gold = [[(3, 7, "ORG"), (16, 38, "ORG")]]
    pred = [[(3, 7, "ORG"), (16, 26, "ORG")]]  # frontière fausse sur la 2e entité
    afficher(evaluer(gold, pred))
    print()
    for genre, ent, mot in erreurs(texte, gold[0], pred[0]):
        print(genre, ent, repr(mot))
