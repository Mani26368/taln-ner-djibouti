"""Teste VRAIMENT l'application « Repère Djibouti » (outil de test de Streamlit, sans navigateur) et écrit demo/test_application.txt.

Ce qui est vérifié :
  1. contraste des couleurs de demo/theme.py ;
  2. hors ligne et configuration (barre d'outils minimale, pas de bandeau « fichier modifié », police Inter locale) ;
  3. design sobre : aucun dégradé, aucune ombre portée, aucun emoji, aucune couleur écrite en dur dans style.css, une seule couleur d'accent ;
  4. page Analyser : deux colonnes, texte annoté, ligne de chiffres, tableau (texte, type, début, fin), CSV, 3 exemples, légende de l'erreur ;
     les 3 systèmes sur les 3 exemples : ce que l'écran affiche = ce que renvoie analyser() ;
  5. cas limites : texte vide, texte trop long, code HTML saisi, modèle manquant ;
  6. les 3 pages (menu en boutons), sans chiffre de performance ; chiffres sur D recalculés séparément ; page À propos ;
  7. D rechargé depuis le cache = D mesuré dans results/test3.csv.

Ce test ne remplace PAS un coup d'œil sur l'écran réel (alignements, couleurs) : celui-là a été fait avec un navigateur sans fenêtre.
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
ATTENDU_EXEMPLES = ["Date", "Personnes", "Erreur"]
EMOJIS = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌✨]")


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
    paires = [(f"texte sombre sur le soulignement pastel {code}", C["texte"], v["fond"]) for code, v in T.TYPES.items()]
    paires += [("texte sur le fond de page", C["texte"], C["fond_page"]),
               ("texte sur une carte blanche", C["texte"], C["carte_fond"]),
               ("texte sur l'encadré gris", C["texte"], C["encadre"]),
               ("texte secondaire (légendes) sur le fond de page", C["texte_secondaire"], C["fond_page"]),
               ("texte secondaire sur une carte blanche", C["texte_secondaire"], C["carte_fond"]),
               ("texte secondaire sur l'encadré gris", C["texte_secondaire"], C["encadre"]),
               ("accent (titre, liens, menu actif) sur le fond de page", C["accent"], C["fond_page"]),
               ("accent sur une carte blanche", C["accent"], C["carte_fond"]),
               ("accent sur l'encadré gris (menu actif)", C["accent"], C["encadre"]),
               ("blanc sur l'accent (bouton « Analyser le texte »)", C["blanc"], C["accent"])]
    pire = None
    for nom, fg, bg in paires:
        r = contraste(fg, bg)
        note(f"     {r:5.1f}  {nom}  ({fg} sur {bg})")
        pire = r if pire is None else min(pire, r)
        verifier(r >= 4.5, f"contraste suffisant : {nom}")
    note(f"     -> contraste le plus faible : {pire:.1f}")
    note("     Audit du contraste sur la page RENDUE (navigateur sans fenêtre) : voir le rapport de mise en œuvre.")


# ------------------------------------------------------------------------------------------------ 2 et 3. hors ligne, design
def test_hors_ligne():
    note("\n2. Hors ligne et configuration")
    trouve = []
    for f in [DOSSIER / "app.py", DOSSIER / "analyse.py", DOSSIER / "theme.py", DOSSIER / "style.css", RACINE / ".streamlit" / "config.toml"]:
        for m in re.findall(r"https?://[^\s\"')]+", f.read_text(encoding="utf-8")):
            if f.name == "theme.py" and m.startswith("https://github.com/Mani26368/"):
                continue                                  # le lien du dépôt (un simple lien, rien n'est chargé)
            trouve.append((f.name, m))
    verifier(not trouve, f"aucune URL de ressource en ligne ({trouve or 'rien trouvé'})")
    verifier("googleapis" not in (DOSSIER / "app.py").read_text(encoding="utf-8"), "aucune police en ligne")
    verifier(not list(DOSSIER.rglob("*.jpg")) and not list(DOSSIER.rglob("*.jpeg")), "aucune photo dans demo/")
    verifier("maquette" not in (DOSSIER / "app.py").read_text(encoding="utf-8"), "l'application ne charge pas la maquette")
    cfg = (RACINE / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    verifier('address = "localhost"' in cfg, "le serveur reste sur l'adresse locale (pas de recherche d'adresse publique)")
    verifier("gatherUsageStats = false" in cfg, "statistiques d'usage de Streamlit désactivées")
    verifier('toolbarMode = "minimal"' in cfg, 'toolbarMode = "minimal" (pas de bouton « Deploy » ni de menu)')
    verifier("runOnSave = false" in cfg and 'fileWatcherType = "none"' in cfg,
             "pas de surveillance des fichiers : le bandeau « Changement de fichier / Toujours relancer » n'apparaît pas")
    police = DOSSIER / "assets" / "fonts" / "Inter-latin-variable.woff2"
    verifier(police.exists() and police.read_bytes()[:4] == b"wOF2", "la police Inter est un fichier LOCAL (demo/assets/fonts/, format woff2)")
    verifier((DOSSIER / "assets" / "fonts" / "LICENSE-Inter.txt").exists(), "la licence de la police (OFL) est dans le dépôt")


def test_design():
    note("\n3. Design sobre")
    css = (DOSSIER / "style.css").read_text(encoding="utf-8")
    sans_donnees = re.sub(r'url\("[^"]*"\)', "", css)
    verifier("gradient" not in css.lower(), "style.css : aucun dégradé")
    verifier(not re.search(r"box-shadow:\s*(?!none|inset)\S", css), "style.css : aucune ombre portée (seulement le soulignement pastel)")
    verifier(not re.search(r"@import", css) and css.count("@font-face") == 1 and "__POLICE_INTER__" in css,
             "style.css : une seule règle @font-face, pour la police locale ; aucun @import")
    verifier(not re.search(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", sans_donnees),
             "style.css : aucune couleur écrite en dur (toutes viennent de demo/theme.py par des variables --nom)")
    verifier('"Inter"' in css and "system-ui" in css, "style.css : police Inter, avec polices du système en secours")
    for reglage in ["--largeur-max", "--taille-titre", "--taille-texte", "--bouton-couleur"]:
        verifier(reglage in css.split("/* ---------- Police")[0], f"style.css : le réglage {reglage} est dans le bloc « RÉGLAGES » du début")
    for fichier in ["app.py", "theme.py", "analyse.py", "style.css"]:
        verifier(not EMOJIS.search((DOSSIER / fichier).read_text(encoding="utf-8")), f"{fichier} : aucun emoji")
    verifier("banniere" not in css.lower() and "bandeau" not in css.lower() and "vague" not in css.lower(), "aucune bannière ni vague")
    attendu = {"fond_page": "#FAFAF9", "texte": "#111827", "accent": "#1E3A8A"}
    verifier(all(T.COULEURS[k].upper() == v for k, v in attendu.items()), "palette : fond #FAFAF9, texte #111827, accent #1E3A8A")
    verifier(set(T.COULEURS) == {"fond_page", "texte", "accent", "texte_secondaire", "carte_fond", "bord", "encadre", "blanc"},
             "une seule couleur d'accent : le reste de la palette est neutre (fond, texte, gris, blanc)")
    fonds = {"ORG": "#BFDBFE", "LOC": "#FED7AA", "DATE": "#E9D5FF", "PER": "#BBF7D0", "FORMATION": "#FBCFE8"}
    verifier(all(T.TYPES[k]["fond"].upper() == v for k, v in fonds.items()), "soulignements pastel : ORG, LOC, DATE, PER, FORMATION")
    verifier(T.TITRE == "Repère Djibouti" and T.PHRASE == "Repérez les personnes, lieux, organisations et dates de vos textes.",
             "en-tête : « Repère Djibouti » et la phrase demandée")
    verifier("page_title=T.TITRE" in (DOSSIER / "app.py").read_text(encoding="utf-8"), "titre de page = « Repère Djibouti »")
    verifier([libelle for _, libelle in T.EXEMPLES] == ATTENDU_EXEMPLES and [i for i, _ in T.EXEMPLES] == ["A14_S001", "A12_S005", "A04_S020"],
             f"3 exemples discrets : {ATTENDU_EXEMPLES} = A14_S001 (date), A12_S005 (personnes), A04_S020 (erreur Washington)")
    verifier(T.NOTE_EXTRAITS == "Les extraits viennent du corpus de travail du projet : le système les connaît mieux que des textes nouveaux.",
             "phrase sur les extraits : texte demandé")


# ------------------------------------------------------------------------------------------------ outils AppTest
def nouvelle_app():
    at = AppTest.from_file(str(DOSSIER / "app.py"), default_timeout=300)
    at.run()
    return at


def tout_html(at):
    return "\n".join(m.value for m in at.markdown)


def entites_affichees(at):
    """Les entités soulignées à l'écran, lues dans le code HTML produit par l'application."""
    morceaux = re.findall(r'<span class="ent ent-(\w+)" title="[^"]*">(.*?)<span class="type-tag">', tout_html(at))
    return [(t, html.unescape(x)) for t, x in morceaux]


def ligne_de_chiffres(at):
    """(total, {type: nombre}) lus dans la ligne de chiffres sous le texte annoté."""
    m = re.search(r'<div class="chiffres">(.*?)</div>', tout_html(at), flags=re.S)
    if not m:
        return None
    total = int(re.search(r"<span><b>(\d+)</b> entit", m.group(1)).group(1))
    par_type = {t: int(n) for t, n in re.findall(r'puce-(\w+)"></i><b>(\d+)</b>', m.group(1))}
    return total, par_type


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


def colonne_contenant(at, predicat):
    for col in at.columns:
        for el in col.children.values():
            if predicat(el):
                return col
    return None


# ------------------------------------------------------------------------------------------------ 4
def test_exemples():
    note("\n4. Page Analyser : mise en page, exemples, systèmes")
    at = nouvelle_app()
    verifier(not at.exception, "la page d'accueil s'affiche sans erreur")
    contenu = tout_html(at)
    verifier("Repère Djibouti" in contenu and html.escape(T.PHRASE) in contenu, "en-tête : « Repère Djibouti » et la phrase d'accueil")
    verifier(any(b.label == "Analyser le texte" for b in at.button), "bouton « Analyser le texte » présent")
    verifier(at.selectbox(key="systeme").value == "3a+3b", "système par défaut = 3a+3b")
    verifier(list(analyse.SYSTEMES)[:1] == ["3a+3b"] and list(analyse.SYSTEMES)[1:] == ["D", "A"],
             "3a+3b par défaut ; D et A restent dans « Options avancées »")
    verifier(len(at.sidebar.radio) == 0, "barre latérale : aucun bouton radio")
    verifier([b.label for b in at.sidebar.button] == ["Analyser un texte", "Catégories reconnues", "À propos"], "barre latérale : le menu est fait de 3 boutons")
    libelles = [b.label for b in at.button if b.key and b.key.startswith("exemple_")]
    verifier(libelles == ATTENDU_EXEMPLES, f"3 boutons d'exemples : {libelles}")
    verifier(not any(c.value == T.LEGENDE_ERREUR for c in at.caption), "la légende de l'erreur n'est pas affichée avant le choix de l'exemple d'erreur")
    for id_segment, libelle in T.EXEMPLES:
        at.button(key=f"exemple_{id_segment}").click()
        at.run()
        texte = at.text_area(key="texte").value
        verifier(texte == analyse.lire_segment(id_segment), f"le bouton « {libelle} » remplit le texte du segment {id_segment}")
        legende = any(c.value == T.LEGENDE_ERREUR for c in at.caption)
        verifier(legende == (id_segment == T.EXEMPLE_ERREUR),
                 f"{id_segment} : la légende de l'erreur est " + ("affichée sous l'exemple d'erreur" if id_segment == T.EXEMPLE_ERREUR else "absente (ce n'est pas l'exemple d'erreur)"))
        note(f"\n  [{id_segment}] {libelle}\n  Texte : {texte}")
        gold = gold_du_segment(id_segment)
        for cle, nom in analyse.SYSTEMES.items():
            lancer_analyse(at, texte, cle)
            entites = analyse.analyser(texte, cle)
            attendu = [(e.type, e.texte) for e in entites]
            vu = entites_affichees(at)
            note(f"    {nom} -> écran : {[f'{x} [{t}]' for t, x in vu]}")
            verifier(not at.exception, f"{id_segment} / {cle} : aucune erreur")
            verifier(vu == attendu, f"{id_segment} / {cle} : l'écran affiche exactement les entités de analyser()")
            chiffres = ligne_de_chiffres(at)
            possibles = analyse.types_possibles(cle)
            verifier(chiffres is not None and chiffres[0] == len(entites)
                     and list(chiffres[1]) == possibles
                     and all(chiffres[1][t] == sum(1 for e in entites if e.type == t) for t in possibles),
                     f"{id_segment} / {cle} : ligne de chiffres = total ({len(entites)}) + un chiffre par type du système {possibles}")
            tab = at.dataframe[0].value if at.dataframe else None
            verifier(tab is not None and list(tab.columns) == ["Texte", "Type", "Début", "Fin"]
                     and [tuple(r) for r in tab.itertuples(index=False)] == [(e.texte, e.type, e.debut, e.fin) for e in entites],
                     f"{id_segment} / {cle} : tableau « Texte, Type, Début, Fin » identique aux entités ({len(entites)} ligne(s))")
            verifier(len(at.get("download_button")) == (1 if entites else 0), f"{id_segment} / {cle} : bouton « Télécharger en CSV » " + ("présent" if entites else "absent (aucune entité)"))
            if cle == "3a+3b":           # le système par défaut, comparé à la vérité terrain annotée à la main
                exact = {(e.debut, e.fin, e.type) for e in entites} == gold
                voulu = id_segment != T.EXEMPLE_ERREUR      # les 2 premiers exemples sont exacts, le dernier contient une erreur
                verifier(exact == voulu, f"{id_segment} : avec 3a+3b le résultat est " + ("exact" if voulu else "faux (exemple d'erreur voulu)"))
                if id_segment == "A14_S001":
                    verifier("DATE" in [t for t, _ in vu], "A14_S001 : une DATE est soulignée avec le système par défaut")
                if id_segment == T.EXEMPLE_ERREUR:
                    verifier(("PER", "Washington") in vu, "A04_S020 : « Washington » est pris pour une PERSONNE par 3a+3b (l'erreur voulue)")
        at.selectbox(key="systeme").select("3a+3b")
    # deux colonnes : le texte à gauche, le texte annoté à droite
    gauche = colonne_contenant(at, lambda el: getattr(el, "key", None) == "texte")
    droite = colonne_contenant(at, lambda el: isinstance(getattr(el, "value", None), str) and "texte-annote" in el.value)
    verifier(gauche is not None and droite is not None and gauche is not droite,
             "deux colonnes : la zone de texte est dans une colonne, le texte annoté dans l'autre")
    # le CSV téléchargeable
    e = [analyse.Entite(14, 28, "LOC", "Ardo Bankoualé"), analyse.Entite(5, 9, "ORG", 'a, "b"')]
    contenu_csv = analyse.entites_en_csv(e)
    verifier(contenu_csv.startswith(b"\xef\xbb\xbf") and contenu_csv.decode("utf-8-sig") == 'texte,type,debut,fin\nArdo Bankoualé,LOC,14,28\n"a, ""b""",ORG,5,9\n',
             "CSV : colonnes texte, type, debut, fin ; accents et guillemets corrects ; lisible par Excel (BOM)")


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


def aller_a(at, indice):
    at.sidebar.button(key=f"nav_{indice}").click()
    at.run()


def test_pages():
    note("\n6. Les trois pages (menu en boutons)")
    at = nouvelle_app()
    memoire_D = analyse._MEMOIRE.pop("D", None)          # on simule « D pas encore chargé » pour tester le chargement à la demande
    try:
        for indice, page in [(1, "Catégories reconnues"), (2, "À propos"), (0, "Analyser un texte")]:
            aller_a(at, indice)
            contenu = tout_html(at) + " ".join(x.value for x in at.info) + " ".join(str(d.value) for d in at.dataframe)
            verifier(not at.exception, f"page « {page} » : s'affiche sans erreur")
            verifier(at.session_state["page"] == page, f"page « {page} » : le clic sur le menu change bien de page")
            verifier("Repère Djibouti" in contenu, f"page « {page} » : l'en-tête « Repère Djibouti » est présent")
            verifier(not re.search(r"\bF1\b|précision|rappel|score", contenu, flags=re.I), f"page « {page} » : aucun chiffre de performance affiché")
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
                import spacy
                version = spacy.util.get_package_version("fr_core_news_sm")
                for attendu in ["Repère Djibouti", "reconnaissance d'entités nommées (NER)", "Traitement automatique des langues (TALN)",
                                "Master 2 IAMD – Université de Djibouti", "Python, spaCy, Streamlit", "Binôme 5",
                                "Prototype de projet TALN – peut se tromper", "Modèle de langue", "Limites", "Dépôt",
                                f"fr_core_news_sm", f"version {version}", T.DEPOT,
                                "moins fiable sur d'autres textes", "ne quitte pas l'ordinateur"]:
                    verifier(attendu.replace("'", "&#x27;") in contenu or attendu in contenu, f"page À propos : « {attendu} »")
    finally:
        if memoire_D is not None and "D" not in analyse._MEMOIRE:
            analyse._MEMOIRE["D"] = memoire_D


def test_messages():
    note("\n6 bis. Message d'attente, README, dépendances")
    source = (DOSSIER / "app.py").read_text(encoding="utf-8")
    verifier("environ 30 secondes" in source and "Première utilisation du modèle D" in source,
             "le message d'attente « Première utilisation du modèle D … environ 30 secondes » est dans l'application")
    readme = (RACINE / "README.md").read_text(encoding="utf-8")
    verifier("environ 30 secondes" in readme, "le README annonce l'attente d'environ 30 secondes pour D")
    verifier("Repère Djibouti" in readme, "le README présente l'application sous le nom « Repère Djibouti »")
    verifier("Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" in readme and "-m streamlit run demo/app.py" in readme,
             "le README donne la variante PowerShell (sans activer le venv) et la ligne Set-ExecutionPolicy")
    verifier("streamlit>=1.67.0,<2" in (RACINE / "requirements.txt").read_text(encoding="utf-8"), "requirements.txt : streamlit>=1.67.0,<2")


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
    note("TEST DE L'APPLICATION REPÈRE DJIBOUTI (outil de test de Streamlit, sans navigateur)")
    note(f"Fait le {time.strftime('%Y-%m-%d à %H:%M:%S')}\n")
    for t in [test_contraste, test_hors_ligne, test_design, test_exemples, test_cas_limites, test_pages, test_messages, test_cache_D]:
        t()
    ok = sum(1 for l in LIGNES if l.startswith("  [OK ]"))
    note(f"\nDurée totale : {time.time() - debut:.0f} s | contrôles OK : {ok} | échecs : {len(ECHECS)}")
    for e in ECHECS:
        note(f"  ÉCHEC : {e}")
    (DOSSIER / "test_application.txt").write_text("\n".join(LIGNES) + "\n", encoding="utf-8")
    sys.exit(1 if ECHECS else 0)


if __name__ == "__main__":
    main()
