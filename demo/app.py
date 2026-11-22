"""Application « NER Djibouti » (Streamlit) : démonstration pour des utilisateurs non techniques.

Lancer, depuis la racine du dépôt :   streamlit run demo/app.py
Fonctionne SANS internet : aucune police, image ou script en ligne. Les couleurs et les textes sont dans demo/theme.py.
Aucun score n'est affiché : c'est un prototype qui peut se tromper.
"""
import csv
import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).resolve().parent
RACINE = DOSSIER.parent
sys.path.insert(0, str(DOSSIER))
import analyse  # noqa: E402
import theme as T  # noqa: E402

st.set_page_config(page_title=T.TITRE, layout="wide", initial_sidebar_state="expanded")

C = T.COULEURS
PAGES = ["Analyser un texte", "Catégories reconnues", "À propos"]
NOM_COMPLET = {code: f"{v['nom']} ({code})" for code, v in T.TYPES.items()}


# ------------------------------------------------------------------------------------------------ apparence
def injecter_css():
    css_types = "\n".join(f".ent-{code} {{ background: {v['fond']}; }}" for code, v in T.TYPES.items())
    st.markdown(f"""<style>
    .stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp textarea, .stApp button,
    .stApp .stMarkdown, .stApp [data-testid="stCaptionContainer"] {{ font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif; }}
    .stApp {{ background: {C['fond_page']}; color: {C['texte']}; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] > div:first-child {{ background: linear-gradient(180deg, {C['barre_haut']} 0%, {C['barre_bas']} 100%); }}
    [data-testid="stSidebar"] * {{ color: {C['barre_texte']}; }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{ padding: .55rem .8rem; border-radius: .6rem; margin-bottom: .25rem; }}
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background: {C['menu_actif']}; }}
    .barre-titre {{ font-size: 1.9rem; font-weight: 700; line-height: 1.1; margin: .2rem 0 .4rem 0; }}
    .barre-sous-titre {{ font-size: .95rem; opacity: .95; margin-bottom: 1.2rem; }}
    .barre-pied {{ font-size: .85rem; opacity: .95; margin-top: 2rem; padding-top: .8rem; border-top: 1px solid rgba(255,255,255,.35); }}
    .drapeau {{ width: 78px; height: 52px; border-radius: 4px; margin-bottom: .8rem; background-size: cover;
                background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 90 60'%3E%3Crect width='90' height='30' fill='%236AB2E7'/%3E%3Crect y='30' width='90' height='30' fill='%2312AD2B'/%3E%3Cpolygon points='0,0 45,30 0,60' fill='%23FFFFFF'/%3E%3Cpolygon points='15.00,21.50 16.91,27.37 23.08,27.37 18.09,31.00 20.00,36.88 15.00,33.25 10.00,36.88 11.91,31.00 6.92,27.37 13.09,27.37' fill='%23D7141A'/%3E%3C/svg%3E"); }}
    .bandeau {{ background: linear-gradient(120deg, {C['bandeau_debut']}, {C['bandeau_fin']}); border-radius: 16px;
                padding: 1.6rem 2rem; margin-bottom: 1.1rem; color: {C['texte']}; }}
    .bandeau h1 {{ color: {C['titre']}; font-size: 2rem; margin: 0 0 .4rem 0; padding: 0; }}
    .bandeau p {{ font-size: 1.1rem; margin: 0; max-width: 46rem; }}
    .st-key-carte_texte, .st-key-carte_resultats, .st-key-carte_simple {{ border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: 1rem; }}
    .st-key-carte_texte, .st-key-carte_simple {{ background: {C['carte_fond']}; border: 1px solid {C['carte_bord']}; }}
    .st-key-carte_resultats {{ background: {C['resultats_fond']}; border: 1px solid {C['resultats_bord']}; }}
    .titre-carte {{ font-size: 1.25rem; font-weight: 700; color: {C['titre']}; margin-bottom: .5rem; }}
    .pastille {{ display: inline-block; width: 1.7rem; height: 1.7rem; line-height: 1.7rem; text-align: center; border-radius: 50%;
                 background: {C['bouton']}; color: {C['bouton_texte']}; font-size: .95rem; margin-right: .5rem; }}
    .stButton > button[kind="primary"] {{ background: linear-gradient(120deg, {C['bouton']}, {C['bouton_fin']}); color: {C['bouton_texte']};
                 border: none; border-radius: 12px; padding: .7rem 1.2rem; font-weight: 700; font-size: 1.05rem; width: 100%; }}
    .stButton > button[kind="secondary"] {{ border-radius: 10px; border: 1px solid {C['carte_bord']}; background: #FFFFFF; color: {C['texte']}; }}
    .texte-surligne {{ background: #FFFFFF; border: 1px solid {C['carte_bord']}; border-radius: 12px; padding: .9rem 1.1rem;
                       font-size: 1.1rem; line-height: 2.1; white-space: pre-wrap; color: {C['texte']}; }}
    .ent {{ padding: .12rem .4rem; border-radius: .45rem; color: {C['texte']}; font-weight: 600; }}
    .ent small {{ font-size: .62rem; font-weight: 800; margin-left: .3rem; opacity: .85; letter-spacing: .03em; }}
    {css_types}
    .legende {{ margin-top: .8rem; color: {C['texte']}; }}
    .legende span {{ display: inline-block; margin-right: 1.2rem; font-size: .95rem; }}
    .point {{ display: inline-block; width: .75rem; height: .75rem; border-radius: 50%; margin-right: .4rem; }}
    .resume {{ background: #FFFFFF; border: 1px solid {C['carte_bord']}; border-radius: 12px; padding: .9rem 1.1rem; color: {C['texte']}; }}
    .resume h4 {{ margin: 0 0 .6rem 0; color: {C['titre']}; font-size: 1.15rem; }}
    .resume .total {{ font-size: 1.05rem; font-weight: 700; margin-bottom: .4rem; }}
    .resume .ligne {{ margin: .15rem 0; font-size: 1rem; }}
    .avertissement {{ margin-top: .9rem; padding: .6rem .9rem; border-radius: 10px; background: #E7F1FC; color: {C['texte']}; font-size: .95rem; }}
    .carte-type {{ background: #FFFFFF; border: 1px solid {C['carte_bord']}; border-radius: 12px; padding: .9rem 1.1rem; margin-bottom: .8rem; color: {C['texte']}; }}
    .carte-type h4 {{ margin: 0 0 .3rem 0; color: {C['titre']}; }}
    .carte-type .source {{ font-size: .85rem; opacity: .8; }}
    </style>""", unsafe_allow_html=True)


def titre_carte(numero, texte):
    pastille = f'<span class="pastille">{numero}</span>' if numero else ""
    return f'<div class="titre-carte">{pastille}{html.escape(texte)}</div>'


# ------------------------------------------------------------------------------------------------ composants
def surligner(texte, entites):
    """Le texte avec les entités surlignées. Tout le texte est « échappé » : aucun code HTML saisi n'est exécuté."""
    morceaux, position = [], 0
    for e in sorted(entites, key=lambda x: x.debut):
        if e.debut < position:
            continue
        morceaux.append(html.escape(texte[position:e.debut]))
        morceaux.append(f'<mark class="ent ent-{e.type}" title="{html.escape(NOM_COMPLET[e.type])}">'
                        f'{html.escape(texte[e.debut:e.fin])}<small>{e.type}</small></mark>')
        position = e.fin
    morceaux.append(html.escape(texte[position:]))
    return "".join(morceaux)


def legende(systeme):
    """Légende : SEULEMENT les types que ce système peut réellement produire (lus dans son pipeline)."""
    items = "".join(f'<span><i class="point" style="background:{T.TYPES[t]["point"]}"></i>{html.escape(NOM_COMPLET[t])}</span>'
                    for t in analyse.types_possibles(systeme))
    return f'<div class="legende">{items}</div>'


def pluriel(n, singulier, plur):
    return f"{n} {singulier if n == 1 else plur}"


def resume(entites):
    total = len(entites)
    lignes = []
    for code in analyse.ORDRE_TYPES:
        n = sum(1 for e in entites if e.type == code)
        if n:
            nom = T.TYPES[code]["nom"].lower()
            lignes.append(f'<div class="ligne">{pluriel(n, nom, T.TYPES[code]["pluriel"])}</div>')
    entete = f'<div class="total">{pluriel(total, "entité détectée", "entités détectées")}</div>'
    return f'<div class="resume"><h4>Résumé</h4>{entete}{"".join(lignes)}</div>'


def avertissement():
    return f'<div class="avertissement">{html.escape(T.AVERTISSEMENT)}</div>'


def preparer_systeme(cle):
    """Charge le système choisi (une seule fois par lancement). Message d'attente clair pour D au premier lancement."""
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
    st.session_state["resultat"] = None
    st.session_state.pop("avertissement", None)


# ------------------------------------------------------------------------------------------------ pages
def page_analyser():
    st.markdown(f'<div class="bandeau"><h1>{html.escape(T.BANDEAU_TITRE)}</h1><p>{html.escape(T.PHRASE_ACCUEIL)}</p></div>',
                unsafe_allow_html=True)
    systeme = st.session_state.get("systeme", analyse.SYSTEME_PAR_DEFAUT)
    if not preparer_systeme(systeme):
        st.stop()

    with st.container(key="carte_texte"):
        st.markdown(titre_carte("1", "Votre texte"), unsafe_allow_html=True)
        colonne_texte, colonne_bouton = st.columns([4, 1.2], vertical_alignment="bottom")
        with colonne_texte:
            st.text_area("Saisissez ou collez un texte en français :", key="texte", height=170,
                         placeholder="Exemple : une actualité, un article ou un document…")
        with colonne_bouton:
            clic = st.button("Analyser le texte", type="primary", key="analyser")
        st.caption("Ou essayez avec un vrai extrait du journal La Nation :")
        colonnes = st.columns(len(T.EXEMPLES))
        for colonne, (id_segment, libelle) in zip(colonnes, T.EXEMPLES):
            colonne.button(libelle, key=f"exemple_{id_segment}", on_click=choisir_exemple, args=(id_segment,))
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

    with st.container(key="carte_resultats"):
        st.markdown(titre_carte("2", "Résultats de l'analyse"), unsafe_allow_html=True)
        res = st.session_state.get("resultat")
        if not res:
            st.write("Les résultats s'afficheront ici après l'analyse.")
        else:
            gauche, droite = st.columns([3, 2])
            with gauche:
                st.markdown(f'<div class="texte-surligne">{surligner(res["texte"], res["entites"])}</div>', unsafe_allow_html=True)
                st.markdown(legende(res["systeme"]), unsafe_allow_html=True)
            with droite:
                st.markdown(resume(res["entites"]), unsafe_allow_html=True)
            st.caption(f"Système utilisé : {analyse.SYSTEMES[res['systeme']]}")
            if res["entites"]:
                st.dataframe(pd.DataFrame({"Entité": [e.texte for e in res["entites"]],
                                           "Type": [NOM_COMPLET[e.type] for e in res["entites"]]}), hide_index=True)
            else:
                st.info("Aucune entité n'a été trouvée dans ce texte par ce système.")
            st.markdown(avertissement(), unsafe_allow_html=True)


def lire_phrase_kadiga(id_phrase):
    with open(RACINE / "kadiga" / "data" / "corpus" / "sentences.csv", encoding="utf-8", newline="") as f:
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
    st.markdown(f'<div class="bandeau"><h1>Catégories reconnues</h1><p>Les cinq types d\'informations que l\'application peut chercher '
                f'dans un texte, avec un exemple réel de chacun.</p></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="carte-type"><h4><i class="point" style="background:{T.TYPES[code]["point"]}"></i>'
                    f'{html.escape(NOM_COMPLET[code])}</h4><div>C\'est {html.escape(T.DEFINITIONS[code])}.</div>'
                    f'<div class="texte-surligne" style="margin-top:.5rem">{extrait}</div>'
                    f'<div class="source">{html.escape(origine)}</div></div>', unsafe_allow_html=True)

    st.subheader("Ce que chaque système sait reconnaître")
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
                  key="ajouter_d", on_click=ajouter_d_au_tableau)
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
    st.markdown(f'<div class="bandeau"><h1>À propos</h1><p>{html.escape(T.AVERTISSEMENT)}</p></div>', unsafe_allow_html=True)
    with st.container(key="carte_simple"):
        for cle, valeur in T.A_PROPOS.items():
            st.markdown(f"**{cle}** : {valeur}")
    st.markdown(avertissement(), unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------ assemblage
injecter_css()
with st.sidebar:
    st.markdown('<div class="drapeau"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="barre-titre">{html.escape(T.TITRE)}</div><div class="barre-sous-titre">{html.escape(T.SOUS_TITRE)}</div>',
                unsafe_allow_html=True)
    page = st.radio("Navigation", PAGES, label_visibility="collapsed", key="page")
    st.markdown(f'<div class="barre-pied">{html.escape(T.FORMATION_PIED)}<br>{html.escape(T.PIED_BARRE_LATERALE)}</div>',
                unsafe_allow_html=True)

{"Analyser un texte": page_analyser, "Catégories reconnues": page_categories, "À propos": page_a_propos}[page]()
