"""Application « Repère Djibouti » (Streamlit) : démonstration pour des utilisateurs non techniques.

Lancer, depuis la racine du dépôt :   streamlit run demo/app.py
Fonctionne SANS internet : aucune police, image ou script en ligne.
  - les COULEURS et les TEXTES sont dans demo/theme.py ;
  - la MISE EN FORME (tailles, espaces, formes) est dans demo/style.css.
Aucun score n'est affiché : c'est un prototype qui peut se tromper.
"""
import base64
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

PAGES = ["Analyser un texte", "Catégories reconnues", "À propos"]
NOM_COMPLET = {code: f"{v['nom']} ({code})" for code, v in T.TYPES.items()}
IMAGE_BANDEAU = DOSSIER / "assets" / "bandeau.jpg"


# ------------------------------------------------------------------------------------------------ apparence
def variables_css():
    """Les couleurs de theme.py, sous forme de variables CSS (--nom) utilisables dans style.css."""
    morceaux = [f"--{cle.replace('_', '-')}: {valeur};" for cle, valeur in T.COULEURS.items()]
    for code, v in T.TYPES.items():
        morceaux.append(f"--{code.lower()}-fond: {v['fond']}; --{code.lower()}-point: {v['point']};")
    b = T.BANDEAU
    morceaux.append(f"--bandeau-debut: {b['debut']}; --bandeau-fin: {b['fin']}; "
                    f"--bandeau-arret: {b['arret_pct']}%; --bandeau-largeur-texte: {b['largeur_texte_pct']}%;")
    return ":root { " + " ".join(morceaux) + " }"


def css_image_bandeau():
    """Si demo/assets/bandeau.jpg existe : l'image, avec le dégradé par-dessus (sinon, rien)."""
    if not IMAGE_BANDEAU.exists():
        return ""
    donnees = base64.b64encode(IMAGE_BANDEAU.read_bytes()).decode("ascii")
    return (".bandeau { background-image: linear-gradient(90deg, rgba(29,78,216,0.95) 0%, rgba(29,78,216,0.95) var(--bandeau-arret), "
            f"rgba(14,165,233,0.80) 100%), url(data:image/jpeg;base64,{donnees}); background-size: cover; background-position: center; }}"
            " .bandeau .deco { display: none; }")


def injecter_css():
    style = (DOSSIER / "style.css").read_text(encoding="utf-8")
    st.html(f"<style>{variables_css()}\n{style}\n{css_image_bandeau()}</style>")


def titre_carte(numero, texte, coche=False):
    marque = '<span class="coche">✓</span>' if coche else f'<span class="pastille">{numero}</span>'
    return f'<div class="titre-carte">{marque}{html.escape(texte)}</div>'


def bandeau(titre, sous_titre):
    st.markdown(f'<div class="bandeau"><div class="deco"></div><div class="texte"><h1>{html.escape(titre)}</h1>'
                f'<p>{html.escape(sous_titre)}</p></div></div>', unsafe_allow_html=True)


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
    items = "".join(f'<span><i class="point pastille-{t}"></i>{html.escape(NOM_COMPLET[t])}</span>'
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
            lignes.append(f'<div class="ligne"><i class="pastille-type pastille-{code}"></i>{pluriel(n, nom, T.TYPES[code]["pluriel"])}</div>')
    entete = f'<div class="total">{pluriel(total, "entité détectée", "entités détectées")}</div>'
    return f'<div class="resume"><h4>Résumé</h4>{entete}{"".join(lignes)}</div>'


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
    st.session_state["resultat"] = None
    st.session_state.pop("avertissement", None)


def aller(page):
    st.session_state["page"] = page


# ------------------------------------------------------------------------------------------------ pages
def page_analyser():
    bandeau(T.BANDEAU_TITRE, T.SOUS_TITRE)
    systeme = st.session_state.get("systeme", analyse.SYSTEME_PAR_DEFAUT)
    if not preparer_systeme(systeme):
        st.stop()

    with st.container(key="carte_texte"):
        st.markdown(titre_carte("1", "Votre texte"), unsafe_allow_html=True)
        st.markdown('<div class="etiquette">Saisissez ou collez un texte en français :</div>', unsafe_allow_html=True)
        st.text_area("Texte à analyser", key="texte", height=170, label_visibility="collapsed",
                     placeholder="Exemple : une actualité, un article ou un document…")
        st.caption("Ou essayez avec un vrai extrait du journal La Nation :")
        colonnes = st.columns(len(T.EXEMPLES))
        for colonne, (id_segment, libelle) in zip(colonnes, T.EXEMPLES):
            colonne.button(libelle, key=f"exemple_{id_segment}", on_click=choisir_exemple, args=(id_segment,), width="stretch")
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

    with st.container(key="carte_resultats"):
        st.markdown(titre_carte("", "Résultats de l'analyse", coche=True), unsafe_allow_html=True)
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
    bandeau("Catégories reconnues", "Les cinq types d'informations que l'application peut chercher dans un texte, avec un exemple réel de chacun.")
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
        st.markdown(f'<div class="carte-type"><h4><i class="point pastille-{code}"></i>'
                    f'{html.escape(NOM_COMPLET[code])}</h4><div>C\'est {html.escape(T.DEFINITIONS[code])}.</div>'
                    f'<div class="texte-surligne" style="margin-top:.6rem">{extrait}</div>'
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
    bandeau("À propos", T.AVERTISSEMENT)
    with st.container(key="carte_simple"):
        for cle, valeur in T.A_PROPOS.items():
            st.markdown(f"**{cle}** : {valeur}")
        if IMAGE_BANDEAU.exists():
            st.markdown(f"**Image** : {T.CREDIT_BANDEAU}")
    st.markdown(avertissement(), unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------ assemblage
st.session_state.setdefault("page", PAGES[0])
injecter_css()
with st.sidebar:
    st.markdown('<div class="drapeau"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="barre-titre">{html.escape(T.TITRE)}</div><div class="barre-sous-titre">{html.escape(T.SOUS_TITRE)}</div>',
                unsafe_allow_html=True)
    for i, nom_page in enumerate(PAGES):
        st.button(nom_page, key=f"nav_{i}", on_click=aller, args=(nom_page,), width="stretch")
    st.markdown(f'<div class="barre-pied">{html.escape(T.FORMATION_PIED)}<br>{html.escape(T.PIED_BARRE_LATERALE)}</div>',
                unsafe_allow_html=True)

page = st.session_state["page"]
st.html(f"<style>.st-key-nav_{PAGES.index(page)} button {{ background: var(--bouton-couleur) !important; }}</style>")   # menu actif

{"Analyser un texte": page_analyser, "Catégories reconnues": page_categories, "À propos": page_a_propos}[page]()
