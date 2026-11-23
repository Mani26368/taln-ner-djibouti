"""Plan B de la démonstration : enregistre dans demo/essais_demo.txt ce que donnent les 3 systèmes sur les 3 exemples.

Si la démonstration en direct échoue le jour de la soutenance, ce fichier montre les résultats réels, obtenus avec
exactement la fonction analyser() que l'application utilise. Il enregistre aussi les temps de chargement et les messages
pour les cas limites (texte vide, texte trop long).

Lancer, depuis la racine du dépôt :   python demo/enregistrer_essais.py
"""
import platform
import sys
import time
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
sys.path.insert(0, str(DOSSIER))
import analyse  # noqa: E402
import theme as T  # noqa: E402


def main():
    lignes = []
    ajouter = lignes.append
    ajouter("ESSAIS DE LA DÉMONSTRATION REPÈRE DJIBOUTI (plan B)")
    ajouter(f"Fichier produit par demo/enregistrer_essais.py le {time.strftime('%Y-%m-%d à %H:%M:%S')}")
    import spacy
    ajouter(f"Python {platform.python_version()} | spaCy {spacy.__version__} | {platform.system()}")
    ajouter("Rien n'est inventé : les textes sont de vrais segments du journal La Nation (corpus du dépôt) ;")
    ajouter("les entités sont celles que renvoie la fonction analyser() de l'application. Prototype : peut se tromper.")
    ajouter("")

    ajouter("=== 1. Chargement des systèmes (une seule fois par lancement) ===")
    for cle, nom in analyse.SYSTEMES.items():
        try:
            analyse.charger_systeme(cle)
            _, secondes, source = analyse._MEMOIRE[cle]
            ajouter(f"- {nom} : chargé en {secondes:.1f} s (source : {source}) ; types possibles : {analyse.types_possibles(cle)}")
        except analyse.ErreurDemo as e:
            ajouter(f"- {nom} : ERREUR -> {e}")
    ajouter("")

    ajouter("=== 2. Les trois exemples, avec les trois systèmes ===")
    for id_segment, libelle in T.EXEMPLES:
        texte = analyse.lire_segment(id_segment)
        ajouter(f"\n[{id_segment}] {libelle}")
        ajouter(f"Texte : {texte}")
        for cle, nom in analyse.SYSTEMES.items():
            try:
                entites = analyse.analyser(texte, cle)
                ajouter(f"  {nom} -> {len(entites)} entité(s)")
                for e in entites:
                    ajouter(f"      {e.texte!r:45} {e.type:10} positions {e.debut}-{e.fin}")
            except analyse.ErreurDemo as e:
                ajouter(f"  {nom} -> ERREUR : {e}")
    ajouter("")

    ajouter("=== 3. Cas limites : messages affichés à l'utilisateur ===")
    for libelle, texte in [("texte vide", ""), ("texte de espaces seulement", "   \n  "),
                           (f"texte de {analyse.MAX_CARACTERES + 1} caractères", "a" * (analyse.MAX_CARACTERES + 1))]:
        try:
            analyse.analyser(texte, "A")
            ajouter(f"- {libelle} : (aucun message)")
        except analyse.TexteInvalide as e:
            ajouter(f"- {libelle} -> {e}")
    sortie = DOSSIER / "essais_demo.txt"
    sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{sortie.name} écrit ({len(lignes)} lignes)")


if __name__ == "__main__":
    main()
