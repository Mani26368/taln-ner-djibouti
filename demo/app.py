"""Application « Repère Djibouti » (Streamlit) : démonstration pour des utilisateurs non techniques.

Lancer, depuis la racine du dépôt :   streamlit run demo/app.py
Fonctionne SANS internet : aucune police, image ou script en ligne (la police Inter est un fichier local).
  - les COULEURS et les TEXTES sont dans demo/theme.py ;
  - la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css.
Aucun chiffre de performance n'est affiché : c'est un prototype qui peut se tromper.
"""
import base64
import csv
import html
import sys
from pathlib import Path

import pandas as pd
import spacy
import streamlit as st

DOSSIER = Path(__file__).resolve().parent
RACINE = DOSSIER.parent
sys.path.insert(0, str(DOSSIER))
import analyse  # noqa: E402
import theme as T  # noqa: E402

st.set_page_config(page_title=T.TITRE, layout="wide", initial_sidebar_state="expanded")

PAGES = ["Analyser un texte", "Catégories reconnues", "À propos"]
NOM_COMPLET = {code: f"{v['nom']} ({code})" for code, v in T.TYPES.items()}
POLICE_INTER = DOSSIER / "assets" / "fonts" / "Inter-latin-variable.woff2"


# ------------------------------------------------------------------------------------------------ apparence
def variables_css():
    """Les couleurs de theme.py, sous forme de variables CSS (--nom) utilisables dans style.css."""
    morceaux = [f"--{cle.replace('_', '-')}: {valeur};" for cle, valeur in T.COULEURS.items()]
    morceaux += [f"--{code.lower()}-fond: {v['fond']};" for code, v in T.TYPES.items()]
    return ":root { " + " ".join(morceaux) + " }"


def uri_police():
    """La police Inter, intégrée à la page sous forme de données (aucun téléchargement)."""
    if not POLICE_INTER.exists():
        return ""
    return "data:font/woff2;base64," + base64.b64encode(POLICE_INTER.read_bytes()).decode("ascii")


def injecter_css():
    style = (DOSSIER / "style.css").read_text(encoding="utf-8").replace("__POLICE_INTER__", uri_police())
    st.html(f"<style>{variables_css()}\n{style}</style>")


def en_tete():
    st.markdown(f'<div class="en-tete"><div class="titre">{html.escape(T.TITRE)}</div>'
                f'<div class="phrase">{html.escape(T.PHRASE)}</div></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------ composants
def surligner(texte, entites):
    """Le texte avec les entités soulignées en pastel et une petite étiquette de type.
    Tout le texte est « échappé » : aucun code HTML saisi n'est exécuté."""
    morceaux, position = [], 0
    for e in sorted(entites, key=lambda x: x.debut):
        if e.debut < position:
            continue
        morceaux.append(html.escape(texte[position:e.debut]))
        morceaux.append(f'<span class="ent ent-{e.type}" title="{html.escape(NOM_COMPLET[e.type])}">'
                        f'{html.escape(texte[e.debut:e.fin])}<span class="type-tag">{e.type}</span></span>')
        position = e.fin
    morceaux.append(html.escape(texte[position:]))
    return "".join(morceaux)


def pluriel(n, singulier, plur):
    return f"{n} {singulier if n == 1 else plur}"


def chiffres(entites, systeme):
    """Une ligne de chiffres : le total, puis un chiffre par type que CE système peut produire (lus dans son pipeline)."""
    total = len(entites)
    morceaux = [f'<span><b>{total}</b> {"entité" if total == 1 else "entités"}</span>']
    for t in analyse.types_possibles(systeme):
        n = sum(1 for e in entites if e.type == t)
        morceaux.append(f'<span><i class="puce puce-{t}"></i><b>{n}</b> {t}</span>')
    return f'<div class="chiffres">{"".join(morceaux)}</div>'


def avertissement():
    return f'<div class="avertissement">{html.escape(T.AVERTISSEMENT)}</div>'


def preparer_systeme(cle):
    """Charge le système choisi (une seule fois par lancement). Message d'attente clair pour D à sa première utilisation."""
    if analyse.est_charge(cle):
        return True
    zone = st.empty()
    if cle == "D" and not analyse.d_en_cache_disque():
        zone.info("**Première utilisation du modèle D : il est en cours d'entraînement (environ 30 secondes).** "
                  "Merci de patienter. Cela n'arrive qu'une fois : ensuite il est gardé sur cet ordinateur "
                  "et son chargement est plus rapide.")
        attente = "Entraînement du modèle D en cours (environ 30 secondes)…"
    elif cle == "D":
        zone.info("Chargement du modèle D en cours (quelques secondes)…")
        attente = "Chargement du modèle D…"
    else:
        attente = f"Chargement du système « {analyse.SYSTEMES[cle]} »…"
    try:
        with st.spinner(attente):
            analyse.charger_systeme(cle)
    except analyse.ErreurDemo as e:
        zone.empty()
        st.error(str(e))
        return False
    except Exception as e:                                   # imprévu : message clair, pas de page blanche
        zone.empty()
        st.error(f"Impossible de charger le système « {analyse.SYSTEMES[cle]} ». Détail technique : {e}")
        return False
    zone.empty()
    return True


def choisir_exemple(id_segment):
    st.session_state["texte"] = analyse.lire_segment(id_segment)
    st.session_state["exemple_actif"] = id_segment
    st.session_state["resultat"] = None
    st.session_state.pop("avertissement", None)


def aller(page):
    st.session_state["page"] = page


# ------------------------------------------------------------------------------------------------ pages
def page_analyser():
    en_tete()
    systeme = st.session_state.get("systeme", analyse.SYSTEME_PAR_DEFAUT)
    if not preparer_systeme(systeme):
        st.stop()

    gauche, droite = st.columns(2, gap="large")
    with gauche:
        st.markdown('<div class="etiquette">Votre texte</div>', unsafe_allow_html=True)
        st.text_area("Texte à analyser", key="texte", height=300, label_visibility="collapsed",
                     placeholder="Collez ou écrivez un texte en français…")
        st.caption("Exemples tirés du journal La Nation :")
        colonnes = st.columns([1, 1.3, 1])
        for colonne, (id_segment, libelle) in zip(colonnes, T.EXEMPLES):
            colonne.button(libelle, key=f"exemple_{id_segment}", type="tertiary", on_click=choisir_exemple, args=(id_segment,),
                           help=f"Segment {id_segment} du corpus La Nation")
        if st.session_state.get("exemple_actif"):
            st.caption(f"Extrait affiché : {st.session_state['exemple_actif']} (journal La Nation)")
        if st.session_state.get("exemple_actif") == T.EXEMPLE_ERREUR:
            st.caption(T.LEGENDE_ERREUR)
        st.caption(T.NOTE_EXTRAITS)
        clic = st.button("Analyser le texte", type="primary", key="analyser", width="stretch")
        with st.expander("Options avancées", expanded=False):
            st.selectbox("Système d'analyse", options=list(analyse.SYSTEMES), key="systeme",
                         format_func=lambda k: analyse.SYSTEMES[k])
        if st.session_state.get("avertissement"):
            st.warning(st.session_state["avertissement"])

    if clic:
        st.session_state.pop("avertissement", None)
        texte = st.session_state.get("texte", "")
        try:
            with st.spinner("Analyse en cours…"):
                entites = analyse.analyser(texte, systeme)
            st.session_state["resultat"] = {"texte": texte, "systeme": systeme, "entites": entites}
        except analyse.TexteInvalide as e:
            st.session_state["resultat"] = None
            st.warning(str(e))
        except analyse.ErreurDemo as e:
            st.session_state["resultat"] = None
            st.error(str(e))

    res = st.session_state.get("resultat")
    with droite:
        st.markdown('<div class="etiquette">Texte annoté</div>', unsafe_allow_html=True)
        if not res:
            st.caption("Le texte annoté s'affichera ici après l'analyse.")
        else:
            st.markdown(f'<div class="texte-annote">{surligner(res["texte"], res["entites"])}</div>', unsafe_allow_html=True)
            st.markdown(chiffres(res["entites"], res["systeme"]), unsafe_allow_html=True)
            st.caption(f"Système utilisé : {analyse.SYSTEMES[res['systeme']]}")

    if res:
        st.markdown('<div class="etiquette" style="margin-top:1.6rem">Entités repérées</div>', unsafe_allow_html=True)
        if res["entites"]:
            tableau = pd.DataFrame({"Texte": [e.texte for e in res["entites"]],
                                    "Type": [e.type for e in res["entites"]],
                                    "Début": [e.debut for e in res["entites"]],
                                    "Fin": [e.fin for e in res["entites"]]})
            st.dataframe(tableau, hide_index=True)
            st.download_button("Télécharger en CSV", data=analyse.entites_en_csv(res["entites"]), file_name="entites_reperees.csv",
                               mime="text/csv", key="telecharger")
        else:
            st.info("Aucune entité n'a été trouvée dans ce texte par ce système.")
        st.markdown(avertissement(), unsafe_allow_html=True)


def lire_phrase_kadiga(id_phrase):
    with open(RACINE / "data" / "corpus_kadiga" / "sentences.csv", encoding="utf-8", newline="") as f:
        for ligne in csv.DictReader(f):
            if ligne["id"] == id_phrase:
                return ligne["text"]
    raise analyse.ErreurDemo(f"Phrase introuvable dans le corpus de Kadiga : {id_phrase}")


def formations_predites_par_d():
    """Combien de formations D a prédites dans nos mesures (results/). None si les fichiers sont absents."""
    total, trouve = 0, False
    for fichier, systeme, colonne in [("test2_resultats.csv", "Kadiga D", "prédites"), ("test3.csv", "Kadiga D", "prédites"),
                                      ("test_externe_lanation.csv", "D –", "FP")]:
        chemin = RACINE / "results" / fichier
        if not chemin.exists():
            continue
        df = pd.read_csv(chemin, encoding="utf-8-sig")
        sel = df[df["système"].str.startswith(systeme) & df["type"].str.startswith("FORMATION")]
        if not sel.empty:
            trouve = True
            total += int(sel[colonne].sum())
    return total if trouve else None


def dates_retrouvees_par_d():
    """Ce que D a réellement retrouvé comme dates dans nos mesures (results/) :
    [(jeu, trouvées exactement, à trouver)]. None si les fichiers sont absents."""
    resultat = []
    try:
        e = pd.read_csv(RACINE / "results" / "test_externe_lanation.csv", encoding="utf-8-sig")
        for perimetre, jeu in [("dev (84)", "dev"), ("test (42)", "test")]:
            r = e[(e["système"].str.startswith("D –")) & (e["périmètre"] == perimetre) & (e["type"] == "DATE")].iloc[0]
            resultat.append((jeu, int(r["VP"]), int(r["support"])))
        t2 = pd.read_csv(RACINE / "results" / "test2_resultats.csv", encoding="utf-8-sig")
        r = t2[t2["système"].str.startswith("Kadiga D") & (t2["type"] == "DATE")].iloc[0]
        resultat.append(("test2", round(r["exact R"] * r["support (gold)"]), int(r["support (gold)"])))
        t3 = pd.read_csv(RACINE / "results" / "test3.csv", encoding="utf-8-sig")
        r = t3[t3["système"].str.startswith("Kadiga D") & (t3["type"] == "DATE")].iloc[0]
        resultat.append(("test3", int(r["VP exact"]), int(r["support"])))
    except (OSError, IndexError, KeyError):
        return None
    return resultat


def ajouter_d_au_tableau():
    st.session_state["inclure_D"] = True


def page_categories():
    en_tete()
    st.markdown('<div class="etiquette">Catégories reconnues</div>', unsafe_allow_html=True)
    st.caption("Les cinq types d'informations que l'application peut chercher dans un texte, avec un exemple réel de chacun.")
    # La légende et le tableau ci-dessous sont lus dans les systèmes chargés. 3a+3b et A sont rapides à charger ;
    # D demande un entraînement la première fois : on ne le charge que si l'utilisateur le demande (ou s'il est déjà prêt).
    if not all(preparer_systeme(cle) for cle in ["3a+3b", "A"]):
        st.stop()
    if analyse.est_charge("D") or st.session_state.get("inclure_D"):
        if not preparer_systeme("D"):
            st.stop()
    for code in analyse.ORDRE_TYPES:
        id_segment, entite = T.EXEMPLES_CATEGORIES[code]
        if code == "FORMATION":
            phrase, origine = lire_phrase_kadiga(id_segment), "exemple tiré du corpus de Kadiga (textes officiels)"
        else:
            phrase, origine = analyse.lire_segment(id_segment), f"extrait réel de La Nation ({id_segment})"
        debut = phrase.find(entite)
        extrait = surligner(phrase, [analyse.Entite(debut, debut + len(entite), code, entite)]) if debut >= 0 else html.escape(phrase)
        st.markdown(f'<div class="carte-type"><h4><i class="puce puce-{code}"></i>{html.escape(NOM_COMPLET[code])}</h4>'
                    f'<div>C\'est {html.escape(T.DEFINITIONS[code])}.</div>'
                    f'<div class="texte-annote" style="margin-top:.6rem">{extrait}</div>'
                    f'<div class="source">{html.escape(origine)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="etiquette" style="margin-top:1.4rem">Ce que chaque système sait reconnaître</div>', unsafe_allow_html=True)
    st.caption("Lu dans le code des systèmes : un type est « Oui » seulement si le modèle ou ses règles peuvent l'étiqueter.")
    lignes = {}
    for cle, nom in analyse.SYSTEMES.items():
        if not analyse.est_charge(cle):
            continue
        possibles = analyse.types_possibles(cle)
        lignes[nom] = {NOM_COMPLET[t]: ("Oui" if t in possibles else "Non") for t in analyse.ORDRE_TYPES}
    st.dataframe(pd.DataFrame(lignes))
    if not analyse.est_charge("D"):
        st.button("Ajouter le modèle D au tableau (il se charge ; la première fois, environ 30 secondes)",
                  key="ajouter_d", on_click=ajouter_d_au_tableau, width="stretch")
    st.info(f"**3a+3b** (nos règles, système par défaut) : {T.NOTE_3A3B}.")
    dates = dates_retrouvees_par_d()
    if dates is not None:
        trouvees, total = sum(d[1] for d in dates), sum(d[2] for d in dates)
        detail = ", ".join(f"{v} sur {n}" for _jeu, v, n in dates)
        st.info(f"**D** (modèle ré-entraîné de Kadiga) : il trouve peu de dates sur nos segments de La Nation. "
                f"Dans nos mesures (dossier results/), sur {total} dates à trouver il en retrouve exactement {trouvees} "
                f"(par groupe d'articles : {detail}).")
    n_form = formations_predites_par_d()
    if n_form is not None:
        st.info(f"Remarque : le système D peut étiqueter des formations, mais dans nos mesures sur des textes de La Nation "
                f"(dossier results/) il en a prédit {n_form}. Ces textes ne contiennent aucune formation : "
                f"cette catégorie n'a donc pas été vérifiée sur des cas réels de La Nation.")
    st.markdown(avertissement(), unsafe_allow_html=True)


def page_a_propos():
    en_tete()
    with st.container(key="carte_simple"):
        for cle, valeur in T.A_PROPOS.items():
            st.markdown(f"**{cle}** : {valeur}")
        version_modele = spacy.util.get_package_version(analyse.MODELE_SPACY)
        st.markdown("### Modèle de langue")
        st.markdown(f"Le modèle spaCy utilisé est **`{analyse.MODELE_SPACY}`** (version {version_modele}, spaCy {spacy.__version__}) : "
                    "un petit modèle français généraliste. Le système par défaut (3a+3b) s'appuie sur lui et lui ajoute des règles locales ; "
                    "le modèle D est le même modèle ré-entraîné sur le corpus de Kadiga.")
        st.markdown("### Limites")
        st.markdown(
            "- C'est un prototype : il se trompe parfois, par exemple en prenant un lieu pour une personne.\n"
            f"- Système par défaut (3a+3b) : {T.NOTE_3A3B}.\n"
            "- Le modèle spaCy n'a pas été entraîné sur la presse de Djibouti et ne sait pas repérer les dates : "
            "les dates viennent de nos règles.\n"
            "- Le modèle D trouve peu de dates sur nos segments de La Nation (les chiffres sont sur la page « Catégories reconnues »).\n"
            "- Les jeux d'évaluation sont petits (moins de 60 entités par jeu) : un seul changement déplace les résultats de plusieurs points. "
            "Aucun chiffre de performance n'est affiché ici pour cette raison.\n"
            "- Aucun texte de La Nation ne contient de formation (diplôme, master) : cette catégorie n'a pas été vérifiée sur de vrais cas de La Nation.\n"
            f"- Le texte est limité à {analyse.MAX_CARACTERES} caractères. Tout fonctionne hors ligne : le texte saisi ne quitte pas l'ordinateur.")
        st.markdown("### Dépôt")
        st.markdown(f"[{T.DEPOT}]({T.DEPOT})")
    st.markdown(avertissement(), unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------ assemblage
st.session_state.setdefault("page", PAGES[0])
injecter_css()
with st.sidebar:
    for i, nom_page in enumerate(PAGES):
        st.button(nom_page, key=f"nav_{i}", on_click=aller, args=(nom_page,), width="stretch")
    st.markdown(f'<div class="barre-pied">{html.escape(T.PIED_BARRE_LATERALE)}<br>{html.escape(T.AVERTISSEMENT)}</div>',
                unsafe_allow_html=True)

page = st.session_state["page"]
actif = PAGES.index(page)
st.html(f"<style>.st-key-nav_{actif} button {{ border-left-color: var(--accent) !important; background: var(--encadre) !important; }}"
        f" .st-key-nav_{actif} button p {{ color: var(--accent) !important; font-weight: 700 !important; }}</style>")   # menu actif

{"Analyser un texte": page_analyser, "Catégories reconnues": page_categories, "À propos": page_a_propos}[page]()
