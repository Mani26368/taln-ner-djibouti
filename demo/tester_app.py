"""Teste VRAIMENT l'application « NER-djib » (outil de test de Streamlit, sans navigateur) et écrit demo/test_application.txt.

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
import subprocess
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
ATTENDU_EXEMPLES = ["Une date", "Des personnes", "Un cas difficile"]
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
    paires = [(f"texte sombre sur le surlignage pastel {code}", C["texte"], v["fond"]) for code, v in T.TYPES.items()]
    paires += [(f"étiquette de type {code} (petit texte coloré) sur son pastel", v["texte"], v["fond"]) for code, v in T.TYPES.items()]
    paires += [(f"chiffre {code} (coloré) sur sa carte pastel", v["texte"], v["fond"]) for code, v in T.TYPES.items()]
    paires += [("texte sur le fond de page", C["texte"], C["fond_page"]),
               ("texte sur une carte blanche", C["texte"], C["carte_fond"]),
               ("texte secondaire (légendes) sur le fond de page", C["texte_secondaire"], C["fond_page"]),
               ("texte secondaire sur une carte blanche", C["texte_secondaire"], C["carte_fond"]),
               ("bleu foncé (titres de cartes, pilules) sur carte blanche", C["bandeau"], C["carte_fond"]),
               ("lien « Télécharger en CSV » sur carte blanche", C["bouton"], C["carte_fond"]),
               ("blanc sur le bandeau (titre, onglet actif)", C["blanc"], C["bandeau"]),
               ("sous-titre et onglets du bandeau sur le bandeau", C["bandeau_texte_secondaire"], C["bandeau"]),
               ("blanc sur le bouton « Analyser le texte »", C["blanc"], C["bouton"])]
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
    verifier(not re.search(r"box-shadow:\s*(?!none)\S", css), "style.css : aucune ombre portée")
    verifier(not re.search(r"@import", css) and css.count("@font-face") == 1 and "__POLICE_INTER__" in css,
             "style.css : une seule règle @font-face, pour la police locale ; aucun @import")
    verifier(not re.search(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", sans_donnees),
             "style.css : aucune couleur écrite en dur (toutes viennent de demo/theme.py par des variables --nom)")
    verifier('"Inter"' in css and "system-ui" in css, "style.css : police Inter, avec polices du système en secours")
    for reglage in ["--largeur-max", "--rayon-carte", "--rayon-petit", "--police"]:
        verifier(reglage in css.split("/* ---------- Police")[0], f"style.css : le réglage {reglage} est dans le bloc « RÉGLAGES » du début")
    for fichier in ["app.py", "theme.py", "analyse.py", "style.css"]:
        verifier(not EMOJIS.search((DOSSIER / fichier).read_text(encoding="utf-8")), f"{fichier} : aucun emoji")
    verifier("vague" not in css.lower() and "wave" not in css.lower(), "aucune vague")
    verifier(re.search(r"@keyframes fondu \{ from \{ opacity: 0; \} to \{ opacity: 1; \} \}", css) is not None
             and "animation: fondu .3s" in css and "infinite" not in css,
             "apparition douce des cartes : fondu de 0,3 s, aucune animation en boucle")
    attendu = {"bandeau": "#13255C", "bandeau_icone": "#2F5BD8", "bandeau_texte_secondaire": "#B8C6EE", "bouton": "#1E3FAE",
               "fond_page": "#F4F6FA", "texte": "#1B2336", "texte_secondaire": "#5B6783", "carte_fond": "#FFFFFF", "bord": "#E2E6EF"}
    verifier(all(T.COULEURS[k].upper() == v for k, v in attendu.items()),
             "palette de la maquette : bandeau #13255C, bouton #1E3FAE, fond #F4F6FA, cartes blanches bordure #E2E6EF, texte #1B2336, secondaire #5B6783")
    fonds = {"ORG": ("#BFDBFE", "#1E3A8A"), "LOC": ("#FED7AA", "#7C3A0E"), "DATE": ("#E9D5FF", "#4C1D95"),
             "PER": ("#BBF7D0", "#14532D"), "FORMATION": ("#FBCFE8", None)}
    verifier(all(T.TYPES[k]["fond"].upper() == f and (t is None or T.TYPES[k]["texte"].upper() == t) for k, (f, t) in fonds.items()),
             "pastels et couleurs de texte : ORG, LOC, DATE, PER, FORMATION")
    verifier("--rayon-carte: 12px" in css, "cartes : coins arrondis de 12 px")
    verifier(T.TITRE == "NER-djib" and T.PHRASE == "Personnes, lieux, organisations et dates de vos textes",
             "bandeau : « NER-djib » et la phrase de la maquette")
    verifier("page_title=T.TITRE" in (DOSSIER / "app.py").read_text(encoding="utf-8"), "titre de page = « NER-djib »")
    verifier([libelle for _, libelle in T.EXEMPLES] == ATTENDU_EXEMPLES and [i for i, _ in T.EXEMPLES] == ["A14_S001", "A12_S005", "A04_S020"],
             f"3 pilules d'exemples : {ATTENDU_EXEMPLES} = A14_S001 (date), A12_S005 (personnes), A04_S020 (erreur Washington)")
    verifier(".st-key-contenu" in css and "[data-testid=\"stSidebar\"]" in css and "display: none" in css,
             "pas de barre latérale (masquée) ; contenu centré sous le bandeau")
    src = (DOSSIER / "app.py").read_text(encoding="utf-8")
    verifier('setAttribute("lang", "fr")' in src and 'setAttribute("translate", "no")' in src and '"notranslate"' in src
             and 'meta.setAttribute("name", "google")' in src and "unsafe_allow_javascript=True" in src and "empecher_traduction()" in src,
             "traduction automatique du navigateur empêchée : lang=\"fr\", translate=\"no\", meta google notranslate (script de app.py)")
    suivis = subprocess.run(["git", "ls-files", "docs"], cwd=RACINE, capture_output=True, text=True).stdout
    verifier("maquette" not in suivis.lower(), "le fichier maquette n'est pas dans le dépôt (docs/ suivi par Git)")
    theme_sans_infos = re.sub(r"A_PROPOS_INFOS = \[.*?\n\]\n", "", (DOSSIER / "theme.py").read_text(encoding="utf-8"), flags=re.S).replace("data/corpus_kadiga", "")
    verifier("Kadiga" not in theme_sans_infos and "Mako" not in theme_sans_infos,
             "theme.py : les noms d'auteurs sont seulement dans A_PROPOS_INFOS (page À propos)")


# ------------------------------------------------------------------------------------------------ outils AppTest
def nouvelle_app():
    at = AppTest.from_file(str(DOSSIER / "app.py"), default_timeout=300)
    at.run()
    return at


def tout_html(at):
    return "\n".join(m.value for m in at.markdown)


def entites_affichees(at):
    """Les entités soulignées à l'écran, lues dans le code HTML produit par l'application."""
    morceaux = re.findall(r'<span class="ent ent-(\w+)" title="[^"]*">(.*?)<sup class="type-tag">', tout_html(at))
    return [(t, html.unescape(x)) for t, x in morceaux]


def ligne_de_chiffres(at):
    """(total, {type: valeur affichée}) lus dans la ligne de 5 petites cartes sous le texte annoté.
    La valeur est un nombre, ou « – » pour un type que le système ne sait pas produire."""
    m = re.search(r'<div class="chiffres">(.*)</div></div>', tout_html(at), flags=re.S)
    if not m:
        return None
    cartes = re.findall(r'chiffre chiffre-(\w+)"[^>]*><div class="nom">([^<]*)</div><div class="valeur">([^<]*)</div>', m.group(1))
    total = int([v for t, _n, v in cartes if t == "total"][0])
    par_type = {t: v for t, _n, v in cartes if t != "total"}
    return total, par_type


def tableau_affiche(at):
    """(en-têtes, lignes) du tableau « Entités repérées » lu dans le HTML produit."""
    m = re.search(r'<table class="tableau-entites"><thead><tr>(.*?)</tr></thead><tbody>(.*?)</tbody></table>', tout_html(at), flags=re.S)
    if not m:
        return None
    entetes = re.findall(r"<th>(.*?)</th>", m.group(1))
    lignes = [(html.unescape(a), b, int(c), int(d)) for a, b, c, d in
              re.findall(r"<tr><td>(.*?)</td><td>(\w+)</td><td>(\d+)</td><td>(\d+)</td></tr>", m.group(2))]
    return entetes, lignes


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


def _contient(bloc, predicat):
    for el in getattr(bloc, "children", {}).values():
        if predicat(el) or _contient(el, predicat):
            return True
    return False


def colonne_contenant(at, predicat):
    """La colonne qui contient (même dans une carte à l'intérieur) un élément répondant au prédicat."""
    for col in at.columns:
        if _contient(col, predicat):
            return col
    return None


# ------------------------------------------------------------------------------------------------ 4
def test_exemples():
    note("\n4. Page Analyser : mise en page, exemples, systèmes")
    at = nouvelle_app()
    verifier(not at.exception, "la page d'accueil s'affiche sans erreur")
    contenu = tout_html(at)
    verifier("NER-djib" in contenu and html.escape(T.PHRASE) in contenu, "bandeau : « NER-djib » et la phrase")
    verifier(any(b.label == "Analyser le texte" for b in at.button), "bouton « Analyser le texte » présent")
    verifier(at.selectbox(key="systeme").value == "3a+3b", "système par défaut = 3a+3b")
    verifier(list(analyse.SYSTEMES)[:1] == ["3a+3b"] and list(analyse.SYSTEMES)[1:] == ["D", "A"],
             "3a+3b par défaut ; D et A restent dans « Options avancées »")
    verifier(len(at.sidebar.button) == 0 and len(at.sidebar.radio) == 0, "pas de barre latérale : le menu est dans le bandeau")
    verifier([b.label for b in at.button if b.key and b.key.startswith("nav_")] == ["Analyser", "Catégories", "À propos"],
             "bandeau : navigation Analyser, Catégories, À propos")
    verifier('class="legende"' in contenu and all(f'<span class="leg-{t}">{t}</span>' in contenu for t in T.TYPES_LEGENDE),
             "carte « Texte annoté » : légende des 4 types (ORG, LOC, DATE, PER)")
    verifier(at.text_area(key="texte").value == analyse.lire_segment(T.EXEMPLE_ACCUEIL) and at.session_state["exemple_actif"] == T.EXEMPLE_ACCUEIL,
             f"à l'ouverture : l'extrait de La Nation {T.EXEMPLE_ACCUEIL} est dans la zone de texte")
    attendu = [(e.type, e.texte) for e in analyse.analyser(analyse.lire_segment(T.EXEMPLE_ACCUEIL), "3a+3b")]
    verifier(entites_affichees(at) == attendu and len(attendu) > 0 and "Exemple : votre texte apparaîtra ainsi" not in contenu,
             "à l'ouverture : l'extrait est déjà analysé (entités surlignées, comme le fait l'analyse)")
    chiffres_accueil, tableau_accueil = ligne_de_chiffres(at), tableau_affiche(at)
    verifier(chiffres_accueil is not None and chiffres_accueil[0] == len(attendu) and tableau_accueil is not None
             and [(x, t) for x, t, _d, _f in tableau_accueil[1]] == [(x, t) for t, x in attendu],
             "à l'ouverture : petites cartes de chiffres et tableau déjà affichés")
    verifier("Comment ça marche" in contenu and all(html.escape(t) in contenu for _n, t in T.ETAPES),
             "bande « Comment ça marche » : les 3 étapes")
    visible = html.unescape(re.sub(r"<style.*?</style>|<script.*?</script>", "", contenu, flags=re.S))
    visible += " ".join(c.value for c in at.caption) + " " + " ".join(b.help or "" for b in at.button) + " " + " ".join(sb.label for sb in at.selectbox)
    visible += " " + " ".join(str(o) for sb in at.selectbox for o in sb.options)
    interdits = ["A01_S002", "gelée", "figée", "3a+3b", "3a", "3b", "Système utilisé", "Système d'analyse", "Repère", "repere"]
    verifier(not [m for m in interdits if re.search(r"(?<![\w-])" + re.escape(m) + r"(?![\w-])", visible)]
             and "Méthode utilisée : règles + lexique locaux" in visible and "Extrait d'un article de La Nation." in visible,
             "texte affiché à l'ouverture : aucun identifiant ni terme interne ; « Méthode utilisée : règles + lexique locaux »")
    verifier(html.escape(T.PIED) in contenu and f'href="{T.DEPOT}"' in contenu,
             "pied de page : « Prototype de projet TALN · M2 IAMD · Université de Djibouti » et lien GitHub")
    css_apercu = (DOSSIER / "style.css").read_text(encoding="utf-8")
    verifier("opacity" not in re.search(r"\.texte-annote\.exemple[^}]*\}", css_apercu).group(0) and ".texte-annote.exemple .ent" in css_apercu,
             "aperçu avant analyse : texte en gris, surlignages en pleine couleur (pas d'opacité qui les délave)")
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
            types_cartes = list(T.TYPES_LEGENDE) + (["FORMATION"] if any(e.type == "FORMATION" for e in entites) else [])
            verifier(chiffres is not None and chiffres[0] == len(entites) and list(chiffres[1]) == types_cartes
                     and all(chiffres[1][t] == (str(sum(1 for e in entites if e.type == t)) if t in possibles else "–") for t in types_cartes),
                     f"{id_segment} / {cle} : cartes Entités ({len(entites)}), Organisations, Lieux, Dates, Personnes ; « – » pour un type que le système ne produit pas")
            tab = tableau_affiche(at)
            verifier(tab is not None and tab[0] == ["Texte repéré", "Type", "Début", "Fin"]
                     and tab[1] == [(e.texte, e.type, e.debut, e.fin) for e in entites],
                     f"{id_segment} / {cle} : tableau « Texte repéré, Type, Début, Fin » identique aux entités ({len(entites)} ligne(s))")
            verifier("texte-annote exemple" not in tout_html(at), f"{id_segment} / {cle} : la phrase d'exemple en grisé disparaît après l'analyse")
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
            raise analyse.ModeleManquant("Le modèle de langue français n'est pas installé sur cet ordinateur. "
                                         "Suivez les instructions d'installation du dépôt, puis relancez l'application.")
        analyse._construire = sans_modele
        analyse._MEMOIRE.clear()
        at = nouvelle_app()
        verifier(any("n'est pas installé" in e.value and "fr_core_news" not in e.value for e in at.error),
                 "modèle manquant : message d'erreur clair, sans nom technique")
        verifier(not at.exception, "modèle manquant : pas de page d'erreur technique")
    finally:
        analyse._construire = sauvegarde
        analyse._MEMOIRE.clear()
        analyse._MEMOIRE.update(memoire)


# ------------------------------------------------------------------------------------------------ 6
def aller_a(at, indice):
    at.button(key=f"nav_{indice}").click()
    at.run()


def test_pages():
    note("\n6. Les trois pages (navigation dans le bandeau)")
    at = nouvelle_app()
    memoire_D = analyse._MEMOIRE.pop("D", None)          # on simule « D pas encore chargé » pour tester le chargement à la demande
    try:
        for indice, page in [(1, "Catégories"), (2, "À propos"), (0, "Analyser")]:
            aller_a(at, indice)
            contenu = tout_html(at) + " ".join(x.value for x in at.info) + " ".join(str(d.value) for d in at.dataframe)
            verifier(not at.exception, f"page « {page} » : s'affiche sans erreur")
            verifier(at.session_state["page"] == page, f"page « {page} » : le clic sur le menu change bien de page")
            verifier("NER-djib" in contenu, f"page « {page} » : le bandeau « NER-djib » est présent")
            verifier(not re.search(r"\bF1\b|précision|rappel|score", contenu, flags=re.I), f"page « {page} » : aucun chiffre de performance affiché")
            if page != "À propos":
                verifier(not re.search(r"Kadiga|Mako|Houssein", contenu), f"page « {page} » : aucun nom d'auteur (les noms sont seulement dans À propos)")
            if page == "Catégories":
                for code in analyse.ORDRE_TYPES:
                    verifier(f"({code})" in contenu, f"page Catégories : le type {code} est présenté")
                verifier("Master IAMD" in contenu and html.escape(T.ORIGINE_FORMATION) in contenu,
                         "page Catégories : exemple de FORMATION « Master IAMD » avec son origine (corpus de ressources, phrase de cours)")
                verifier("corpus de Kadiga" not in contenu and "de Kadiga" not in contenu, "page Catégories : plus de « Kadiga »")
                # page simple pour un utilisateur normal : seulement les 5 types et leurs exemples
                verifier(len(at.dataframe) == 0, "page Catégories : aucun tableau (la comparaison des systèmes n'est pas dans l'application)")
                verifier(len(at.info) == 0 and len(at.warning) == 0, "page Catégories : aucun encadré (3a+3b, D, formations)")
                verifier(not any(b.key == "ajouter_d" for b in at.button), "page Catégories : pas de bouton pour ajouter le modèle D")
                verifier(contenu.count('class="carte-type"') == len(analyse.ORDRE_TYPES) == 5,
                         "page Catégories : exactement 5 cartes, une par type, chacune avec son exemple surligné")
                verifier(all(f'ent ent-{code}"' in contenu for code in analyse.ORDRE_TYPES), "page Catégories : un exemple surligné pour chacun des 5 types")
                verifier(not re.search(r"results/|3a\+3b|modèle D|ré-entraîné|dates à trouver|Oui|Non", contenu),
                         "page Catégories : aucun terme technique (systèmes, results/, tableau Oui/Non)")
            if page == "À propos":
                texte = html.unescape(contenu)
                verifier(f'class="etiquette">À propos<' in texte and T.A_PROPOS_TITRE in texte and T.A_PROPOS_INTRO in texte
                         and T.A_PROPOS_INTRO == "Trouve les personnes, les lieux, les organisations et les dates dans un texte français, pensé pour les textes de Djibouti.",
                         "carte d'introduction : petit titre « À PROPOS », titre « NER-djib », une seule phrase")
                verifier(texte.count('class="petite-carte"') == 3 and 'class="grille-cartes"' in texte, "3 petites cartes côte à côte (grille qui s'empile sur téléphone)")
                for titre, phrase in [("Prototype", "Il peut se tromper, surtout sur les noms locaux."),
                                      ("Vie privée", "Le texte saisi est analysé sur le moment et n'est pas enregistré."),
                                      ("Limite", f"{analyse.MAX_CARACTERES} caractères par analyse.")]:
                    verifier(f'<div class="etiquette">{titre}</div><div class="texte-propos">{phrase}</div>' in texte, f"petite carte « {titre} » : « {phrase} »")
                verifier(texte.count('class="icone-propos"') == 3 and texte.count("<svg") >= 3, "chaque petite carte a une icône simple")
                verifier('class="etiquette">Le projet<' in texte and texte.count('class="info"') == 4 and 'class="grille-infos"' in texte,
                         "carte « LE PROJET » : 4 informations en deux colonnes")
                for libelle, valeur in [("Projet", "Binôme 5 – Reconnaissance d'entités nommées propres à Djibouti"),
                                        ("Réalisé par", "Mako Mohamed Aden et Kadiga Ali Ahmed"), ("Encadrant", "Dr Houssein Ahmed Assowe"),
                                        ("Formation", "M2 IAMD, Université de Djibouti, cours TALN, 2026")]:
                    verifier(f'<div class="info-libelle">{libelle}</div><div class="info-valeur">{valeur}</div>' in texte,
                             f"information du projet : {libelle} = {valeur}")
                liens = at.get("link_button")
                verifier(len(liens) == 1 and liens[0].proto.url == "https://github.com/Mani26368/taln-ner-djibouti"
                         and liens[0].proto.label == "Voir le dépôt GitHub",
                         "bouton « Voir le dépôt GitHub » vers https://github.com/Mani26368/taln-ner-djibouti")
                verifier("Prototype de projet TALN – peut se tromper." in texte, "pied de page « Prototype de projet TALN – peut se tromper. »")
                verifier(not re.search(r"(a fait|a réalisé|a écrit|s'est occupée|chargée|partie)", texte), "aucune mention de qui a fait quelle partie")
                for interdit in ["spaCy", "3a+3b", "modèle D", "results/", "jeux d'évaluation", "chiffre"]:
                    verifier(interdit not in texte, f"page À propos : ne contient pas « {interdit} »")
                verifier(not re.search(r"mod[eè]le|fr_core_news|version \d|F1", texte, flags=re.I), "page À propos : aucun mot « modèle », aucune version, aucun score")
    finally:
        if memoire_D is not None and "D" not in analyse._MEMOIRE:
            analyse._MEMOIRE["D"] = memoire_D


def test_messages():
    note("\n6 bis. Message d'attente, README, dépendances")
    source = (DOSSIER / "app.py").read_text(encoding="utf-8")
    verifier("environ 30 secondes" in source and "Première utilisation du modèle ré-entraîné" in source,
             "le message d'attente « Première utilisation du modèle ré-entraîné … environ 30 secondes » est dans l'application")
    readme = (RACINE / "README.md").read_text(encoding="utf-8")
    verifier("environ 30 secondes" in readme, "le README annonce l'attente d'environ 30 secondes pour D")
    verifier("NER-djib" in readme, "le README présente l'application sous le nom « NER-djib »")
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
