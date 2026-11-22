"""Teste VRAIMENT l'application (avec l'outil de test de Streamlit, sans navigateur) et écrit demo/test_application.txt.

Ce qui est vérifié :
  1. contraste du texte sur les fonds (lisibilité) ;      2. aucune ressource en ligne ;
  3. les 3 systèmes sur les 3 exemples : ce que l'écran affiche = ce que renvoie analyser() ;
     le système par défaut (3a+3b) est exact sur les 2 premiers exemples et se trompe sur le 3e (voulu) ; le violet apparaît ;
  4. légende = types réellement produits par le système ;  5. texte vide, texte trop long, code HTML saisi, modèle manquant ;
  6. les 3 pages s'affichent, sans score ; chiffres sur D recalculés séparément ;  7. D rechargé depuis le cache = D de results/test3.csv.

Ce test ne remplace PAS un coup d'œil humain sur l'écran (couleurs, mise en page).
Lancer, depuis la racine du dépôt :   python demo/tester_app.py
"""
import html
import re
import sys
import time
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
RACINE = DOSSIER.parent
sys.path.insert(0, str(DOSSIER))
sys.path.insert(0, str(RACINE / "src"))
import analyse  # noqa: E402
import theme as T  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

LIGNES, ECHECS = [], []


def note(texte=""):
    LIGNES.append(texte)
    print(texte)


def verifier(condition, libelle):
    note(f"  [{'OK ' if condition else 'ÉCHEC'}] {libelle}")
    if not condition:
        ECHECS.append(libelle)


# ------------------------------------------------------------------------------------------------ 1. contraste
def luminance(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_contraste():
    note("1. Lisibilité : rapport de contraste (norme WCAG : 4,5 minimum pour du texte courant, 7 = très confortable)")
    C = T.COULEURS
    paires = [(f"texte sombre sur surlignage {code}", C["texte"], v["fond"]) for code, v in T.TYPES.items()]
    paires += [("texte sombre sur carte blanche", C["texte"], C["carte_fond"]),
               ("texte sombre sur carte des résultats", C["texte"], C["resultats_fond"]),
               ("texte sombre sur fond de page", C["texte"], C["fond_page"]),
               ("texte sombre sur encadré d'avertissement", C["texte"], "#E7F1FC"),
               ("titre sur début du bandeau", C["titre"], C["bandeau_debut"]),
               ("titre sur fin du bandeau", C["titre"], C["bandeau_fin"]),
               ("texte sombre sur début du bandeau", C["texte"], C["bandeau_debut"]),
               ("texte sombre sur fin du bandeau", C["texte"], C["bandeau_fin"]),
               ("texte blanc sur haut de la barre latérale", C["barre_texte"], C["barre_haut"]),
               ("texte blanc sur bas de la barre latérale", C["barre_texte"], C["barre_bas"]),
               ("texte blanc sur menu actif", C["barre_texte"], C["menu_actif"]),
               ("texte du bouton sur le début du dégradé", C["bouton_texte"], C["bouton"]),
               ("texte du bouton sur la fin du dégradé", C["bouton_texte"], C["bouton_fin"])]
    pire = None
    for nom, fg, bg in paires:
        r = contraste(fg, bg)
        note(f"     {r:5.1f}  {nom}  ({fg} sur {bg})")
        pire = r if pire is None else min(pire, r)
        verifier(r >= 4.5, f"contraste suffisant : {nom}")
    note(f"     -> contraste le plus faible : {pire:.1f}")


# ------------------------------------------------------------------------------------------------ 2. hors ligne
def test_hors_ligne():
    note("\n2. Hors ligne : recherche de ressources en ligne dans les fichiers de la démo")
    trouve = []
    for f in [DOSSIER / "app.py", DOSSIER / "analyse.py", DOSSIER / "theme.py", RACINE / ".streamlit" / "config.toml"]:
        for m in re.findall(r"https?://[^\s\"')]+", f.read_text(encoding="utf-8")):
            if m != "http://www.w3.org/2000/svg":      # identifiant de format du dessin du drapeau, pas une ressource
                trouve.append((f.name, m))
    verifier(not trouve, f"aucune URL de ressource en ligne ({trouve or 'rien trouvé'})")
    verifier("googleapis" not in (DOSSIER / "app.py").read_text(encoding="utf-8"), "aucune police en ligne")
    verifier(not any(DOSSIER.glob("*.jpg")) and not any(DOSSIER.glob("*.jpeg")), "aucune photo dans l'application")
    verifier("maquette" not in (DOSSIER / "app.py").read_text(encoding="utf-8"), "l'application ne charge pas la maquette")
    verifier('address = "localhost"' in (RACINE / ".streamlit" / "config.toml").read_text(encoding="utf-8"),
             "le serveur reste sur l'adresse locale (pas de recherche d'adresse publique sur internet)")
    verifier("gatherUsageStats = false" in (RACINE / ".streamlit" / "config.toml").read_text(encoding="utf-8"),
             "statistiques d'usage de Streamlit désactivées")


# ------------------------------------------------------------------------------------------------ outils AppTest
def nouvelle_app():
    at = AppTest.from_file(str(DOSSIER / "app.py"), default_timeout=300)
    at.run()
    return at


def tout_html(at):
    return "\n".join(m.value for m in at.markdown)


def entites_affichees(at):
    """Les entités surlignées à l'écran, lues dans le code HTML produit par l'application."""
    morceaux = re.findall(r'<mark class="ent ent-(\w+)" title="[^"]*">(.*?)<small>', tout_html(at))
    return [(t, html.unescape(x)) for t, x in morceaux]


def legende_affichee(at):
    m = re.search(r'<div class="legende">(.*?)</div>', tout_html(at), flags=re.S)
    if not m:
        return []
    noms = re.findall(r"</i>([^<]+)</span>", m.group(1))
    return [re.search(r"\((\w+)\)", n).group(1) for n in noms]


def lancer_analyse(at, texte, systeme):
    at.text_area(key="texte").set_value(texte)
    at.selectbox(key="systeme").select(systeme)
    at.button(key="analyser").click()
    at.run()
    return at


def gold_du_segment(id_segment):
    """Les entités annotées à la main pour ce segment (data/annotations*.csv)."""
    import csv
    sortie = set()
    for fichier in ["annotations.csv", "annotations_test2.csv", "annotations_test3.csv"]:
        with open(RACINE / "data" / fichier, encoding="utf-8", newline="") as f:
            for a in csv.DictReader(f):
                if a["id_segment"] == id_segment:
                    sortie.add((int(a["debut"]), int(a["fin"]), a["type"]))
    return sortie


# ------------------------------------------------------------------------------------------------ 3 et 4
def test_exemples():
    note("\n3. Les 3 systèmes sur les 3 exemples (ce que l'écran affiche, comparé à analyser())")
    at = nouvelle_app()
    verifier(not at.exception, "la page d'accueil s'affiche sans erreur")
    verifier("Bienvenue sur NER Djibouti !" in tout_html(at), "bandeau « Bienvenue sur NER Djibouti ! » présent")
    verifier("Votre texte" in tout_html(at) and ("Résultats de l'analyse" in tout_html(at) or "Résultats de l&#x27;analyse" in tout_html(at)),
             "cartes « Votre texte » et « Résultats de l'analyse » présentes")
    verifier(any(b.label == "Analyser le texte" for b in at.button), "bouton « Analyser le texte » présent")
    verifier(at.selectbox(key="systeme").value == "3a+3b", "système par défaut = 3a+3b")
    verifier(analyse.SYSTEME_PAR_DEFAUT == "3a+3b" and list(analyse.SYSTEMES)[0] == "3a+3b",
             "3a+3b est le premier du menu et le système par défaut")
    verifier(list(analyse.SYSTEMES)[1:] == ["D", "A"], "D et A restent disponibles dans « Options avancées »")
    for id_segment, libelle in T.EXEMPLES:
        at.button(key=f"exemple_{id_segment}").click()
        at.run()
        texte = at.text_area(key="texte").value
        verifier(texte == analyse.lire_segment(id_segment), f"le bouton « {libelle} » remplit le texte du segment {id_segment}")
        note(f"\n  [{id_segment}] {libelle}\n  Texte : {texte}")
        gold = gold_du_segment(id_segment)
        for cle, nom in analyse.SYSTEMES.items():
            lancer_analyse(at, texte, cle)
            attendu = [(e.type, e.texte) for e in analyse.analyser(texte, cle)]
            vu = entites_affichees(at)
            note(f"    {nom} -> écran : {[f'{x} [{t}]' for t, x in vu]}")
            verifier(not at.exception, f"{id_segment} / {cle} : aucune erreur")
            verifier(vu == attendu, f"{id_segment} / {cle} : l'écran affiche exactement les entités de analyser()")
            verifier(legende_affichee(at) == analyse.types_possibles(cle),
                     f"{id_segment} / {cle} : la légende = les types possibles du système {analyse.types_possibles(cle)}")
            verifier("Résumé" in tout_html(at) and (f"{len(attendu)} entité" in tout_html(at) or not attendu),
                     f"{id_segment} / {cle} : le résumé annonce {len(attendu)} entité(s)")
            lignes_tableau = len(at.dataframe[0].value) if at.dataframe else 0
            verifier(lignes_tableau == len(attendu), f"{id_segment} / {cle} : le tableau « entité / type » a {len(attendu)} ligne(s)")
            if cle == "3a+3b":           # le système par défaut, comparé à la vérité terrain annotée à la main
                exact = {(e.debut, e.fin, e.type) for e in analyse.analyser(texte, cle)} == gold
                voulu = id_segment != T.EXEMPLES[-1][0]      # les 2 premiers exemples sont exacts, le dernier contient une erreur
                verifier(exact == voulu, f"{id_segment} : avec 3a+3b le résultat est " + ("exact" if voulu else "faux (exemple d'erreur voulu)"))
                if id_segment == T.EXEMPLES[0][0]:
                    verifier("DATE" in [t for t, _ in vu], f"{id_segment} : une DATE est surlignée (le violet apparaît) avec le système par défaut")
        at.selectbox(key="systeme").select("3a+3b")


# ------------------------------------------------------------------------------------------------ 5
def test_cas_limites():
    note("\n5. Cas limites")
    at = nouvelle_app()
    at.text_area(key="texte").set_value("")
    at.button(key="analyser").click()
    at.run()
    verifier(any("Le texte est vide" in w.value for w in at.warning), "texte vide : message clair affiché")
    verifier(not at.exception, "texte vide : pas d'erreur technique")
    at.text_area(key="texte").set_value("a" * (analyse.MAX_CARACTERES + 1))
    at.button(key="analyser").click()
    at.run()
    verifier(any("trop long" in w.value for w in at.warning), f"texte de {analyse.MAX_CARACTERES + 1} caractères : message « trop long » affiché")
    at.text_area(key="texte").set_value("<b>gras</b> <script>alert(1)</script> Djibouti")
    at.button(key="analyser").click()
    at.run()
    html_ecran = tout_html(at)
    verifier("<script>alert(1)</script>" not in html_ecran and "&lt;script&gt;" in html_ecran,
             "du code HTML saisi par l'utilisateur est affiché comme du texte, jamais exécuté")
    # modèle manquant : on simule l'absence du modèle spaCy
    sauvegarde, memoire = analyse._construire, dict(analyse._MEMOIRE)
    try:
        def sans_modele(cle):
            raise analyse.ModeleManquant("Le modèle de langue « fr_core_news_sm » n'est pas installé sur cet ordinateur. "
                                         "Installez-le avec la commande : python -m spacy download fr_core_news_sm")
        analyse._construire = sans_modele
        analyse._MEMOIRE.clear()
        at = nouvelle_app()
        verifier(any("python -m spacy download fr_core_news_sm" in e.value for e in at.error),
                 "modèle manquant : message d'erreur clair avec la commande d'installation")
        verifier(not at.exception, "modèle manquant : pas de page d'erreur technique")
    finally:
        analyse._construire = sauvegarde
        analyse._MEMOIRE.clear()
        analyse._MEMOIRE.update(memoire)


# ------------------------------------------------------------------------------------------------ 6
def chiffres_d_recalcules():
    """Dates retrouvées exactement par D (et dates à trouver), recalculées ICI, séparément de l'application."""
    import pandas as pd
    e = pd.read_csv(RACINE / "results" / "test_externe_lanation.csv", encoding="utf-8-sig")
    vp, sup = 0, 0
    for per in ["dev (84)", "test (42)"]:
        r = e[(e["système"].str.startswith("D –")) & (e["périmètre"] == per) & (e["type"] == "DATE")].iloc[0]
        vp, sup = vp + int(r["VP"]), sup + int(r["support"])
    t2 = pd.read_csv(RACINE / "results" / "test2_resultats.csv", encoding="utf-8-sig")
    r2 = t2[t2["système"].str.startswith("Kadiga D") & (t2["type"] == "DATE")].iloc[0]
    t3 = pd.read_csv(RACINE / "results" / "test3.csv", encoding="utf-8-sig")
    r3 = t3[t3["système"].str.startswith("Kadiga D") & (t3["type"] == "DATE")].iloc[0]
    vp += round(r2["exact R"] * r2["support (gold)"]) + int(r3["VP exact"])
    sup += int(r2["support (gold)"]) + int(r3["support"])
    return vp, sup


def test_pages():
    note("\n6. Les trois pages")
    at = nouvelle_app()
    memoire_D = analyse._MEMOIRE.pop("D", None)          # on simule « D pas encore chargé » pour tester le chargement à la demande
    try:
        for page in ["Catégories reconnues", "À propos", "Analyser un texte"]:
            at.sidebar.radio(key="page").set_value(page)
            at.run()
            contenu = tout_html(at) + " ".join(x.value for x in at.info) + " ".join(str(d.value) for d in at.dataframe)
            verifier(not at.exception, f"page « {page} » : s'affiche sans erreur")
            verifier(not re.search(r"\bF1\b|précision|rappel|score", contenu, flags=re.I), f"page « {page} » : aucun score affiché")
            if page == "Catégories reconnues":
                for code in analyse.ORDRE_TYPES:
                    verifier(f"({code})" in contenu, f"page Catégories : le type {code} est présenté")
                verifier("Master IAMD" in contenu, "page Catégories : exemple de FORMATION = « Master IAMD » (corpus de Kadiga)")
                verifier(len(at.dataframe[0].value.columns) == 2, "page Catégories : sans D chargé, le tableau a 2 systèmes (3a+3b et A)")
                verifier(any(b.key == "ajouter_d" for b in at.button), "page Catégories : un bouton propose d'ajouter D (chargement à la demande)")
                phrase = "règles réglées sur les articles du projet, moins fiable sur d'autres textes"
                verifier(any(phrase in i.value for i in at.info), f"page Catégories : phrase exacte sur 3a+3b : « {phrase} »")
                vp, sup = chiffres_d_recalcules()
                note(f"     Recalcul séparé depuis results/ : D retrouve exactement {vp} dates sur {sup}")
                verifier(any("peu de dates" in i.value and f"sur {sup} dates" in i.value and f"exactement {vp} " in i.value for i in at.info),
                         f"page Catégories : D « trouve peu de dates », chiffre affiché = chiffre recalculé ({vp} sur {sup})")
                at.button(key="ajouter_d").click()
                at.run()
                verifier(not at.exception, "page Catégories : le chargement de D à la demande s'exécute sans erreur")
                tab = at.dataframe[0].value
                verifier(len(tab.columns) == 3, "page Catégories : après le clic, le tableau a 3 systèmes (D ajouté)")
                note("     Tableau « ce que chaque système sait reconnaître » (avec D) :\n" + tab.to_string())
            if page == "À propos":
                for attendu in ["NER Djibouti", "Traitement automatique des langues (TALN)", "Master 2 IAMD – Université de Djibouti",
                                "Python, spaCy, Streamlit", "Binôme 5", "Prototype de projet TALN – peut se tromper"]:
                    verifier(attendu.replace("'", "&#x27;") in contenu or attendu in contenu, f"page À propos : « {attendu} »")
    finally:
        if memoire_D is not None and "D" not in analyse._MEMOIRE:
            analyse._MEMOIRE["D"] = memoire_D


def test_messages():
    note("\n6 bis. Message d'attente pour la première utilisation de D")
    source = (DOSSIER / "app.py").read_text(encoding="utf-8")
    verifier("environ 30 secondes" in source and "Première utilisation du modèle D" in source,
             "le message d'attente « Première utilisation du modèle D … environ 30 secondes » est dans l'application")
    verifier("environ 30 secondes" in (RACINE / "README.md").read_text(encoding="utf-8"),
             "le README annonce l'attente d'environ 30 secondes pour D")


# ------------------------------------------------------------------------------------------------ 7
def test_cache_D():
    note("\n7. D rechargé depuis le cache = D de results/test3.csv (63 valeurs comparées)")
    import pandas as pd
    import mesurer_test3 as M
    from mesurer_test2 import lire, predictions_kadiga
    nlp, secondes, source = analyse.charger_systeme("D")
    note(f"     D chargé en {secondes:.1f} s (source : {source})")
    segs, gold = lire(RACINE / "data" / "corpus_test3.csv", RACINE / "data" / "annotations_test3.csv")
    ids = [s["id"] for s in segs]
    M.NOMS = {"K-D": "Kadiga D : NER ré-entraîné"}
    nouveau = M.tableau(gold, {"K-D": predictions_kadiga(nlp, segs)}, ids)
    ancien = pd.read_csv(RACINE / "results" / "test3.csv", encoding="utf-8-sig")
    ancien = ancien[ancien["système"] == "Kadiga D : NER ré-entraîné"].reset_index(drop=True)
    diff, n = 0, 0
    for i in range(len(ancien)):
        for c in [c for c in ancien.columns if c not in ("système", "type")]:
            a, b = nouveau.loc[i, c], ancien.loc[i, c]
            n += 1
            if not (pd.isna(a) and pd.isna(b)) and (pd.isna(a) != pd.isna(b) or abs(float(a) - float(b)) > 1e-9):
                diff += 1
    verifier(diff == 0, f"{n} valeurs comparées, {diff} différence(s)")


def main():
    debut = time.time()
    note("TEST DE L'APPLICATION NER DJIBOUTI (outil de test de Streamlit, sans navigateur)")
    note(f"Fait le {time.strftime('%Y-%m-%d à %H:%M:%S')}\n")
    for t in [test_contraste, test_hors_ligne, test_exemples, test_cas_limites, test_pages, test_messages, test_cache_D]:
        t()
    note(f"\nDurée totale : {time.time() - debut:.0f} s | échecs : {len(ECHECS)}")
    for e in ECHECS:
        note(f"  ÉCHEC : {e}")
    (DOSSIER / "test_application.txt").write_text("\n".join(LIGNES) + "\n", encoding="utf-8")
    sys.exit(1 if ECHECS else 0)


if __name__ == "__main__":
    main()
