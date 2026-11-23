"""Analyse d'un texte avec l'un des systèmes du projet (sans interface : l'application et les tests l'utilisent).

Les systèmes ne sont NI copiés NI modifiés : on importe
  - A      : spaCy fr_core_news_sm seul                              (src/regles_locales.py, construire(groupes=[]))
  - 3a+3b  : nos règles locales + filtres, version GELÉE 087deb3     (src/regles_locales.py)
  - D      : le modèle ré-entraîné de Kadiga                         (src/systemes_kadiga.py, entrainer_D)

D n'est enregistré nulle part dans Git (un modèle spaCy est trop gros). La PREMIÈRE fois qu'on l'utilise, on le ré-entraîne
(environ 30 secondes), puis on le garde dans demo/.cache/ (dossier ignoré par Git) : les utilisations suivantes sont plus rapides.
Le système par défaut de la démo est 3a+3b : il ne demande aucun entraînement.
"""
import hashlib
import shutil
import sys
import time
from pathlib import Path
from typing import NamedTuple

import spacy

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))
import regles_locales as R       # noqa: E402  (nos règles, gelées)
import systemes_kadiga as K      # noqa: E402  (systèmes de Kadiga, repris à l'identique)

MODELE_SPACY = "fr_core_news_sm"
DOSSIER_CACHE = Path(__file__).resolve().parent / ".cache" / "modele_D"
MAX_CARACTERES = 3000            # limite choisie pour une démo (environ 500 mots)

# clé interne -> nom affiché
SYSTEMES = {          # le premier est le système par défaut (menu « Options avancées »)
    "3a+3b": "3a+3b – nos règles locales (version gelée)",
    "D": "D – modèle ré-entraîné",
    "A": "A – spaCy seul",
}
SYSTEME_PAR_DEFAUT = "3a+3b"

# étiquettes des modèles -> nos types. MISC (« divers ») n'existe pas dans notre guide : on l'ignore.
ETIQUETTE_VERS_TYPE = {"PER": "PER", "ORG": "ORG", "LOC": "LOC", "DATE": "DATE", "FORM": "FORMATION"}
ORDRE_TYPES = ["ORG", "LOC", "DATE", "PER", "FORMATION"]


class Entite(NamedTuple):
    debut: int
    fin: int
    type: str
    texte: str


class ErreurDemo(Exception):
    """Erreur dont le message est destiné à l'utilisateur (clair, sans jargon)."""


class ModeleManquant(ErreurDemo):
    pass


class TexteInvalide(ErreurDemo):
    pass


# ------------------------------------------------------------------------------------ construction des systèmes
def _spacy_ou_erreur(construire):
    try:
        return construire()
    except OSError as e:
        if "E050" in str(e) or MODELE_SPACY in str(e):
            raise ModeleManquant(
                f"Le modèle de langue « {MODELE_SPACY} » n'est pas installé sur cet ordinateur. "
                f"Installez-le avec la commande : python -m spacy download {MODELE_SPACY}") from e
        raise


def _empreinte_D():
    """Résumé de tout ce dont dépend D : si l'un change, le cache est périmé."""
    h = hashlib.sha256()
    for chemin in [RACINE / "data" / "corpus_kadiga" / "sentences.csv",
                   RACINE / "data" / "corpus_kadiga" / "entities.csv",
                   RACINE / "src" / "systemes_kadiga.py"]:
        h.update(chemin.read_bytes())
    h.update(f"spacy {spacy.__version__}|{spacy.util.get_package_version(MODELE_SPACY)}|"
             f"{K.SEED},{K.MAX_EPOCHS},{K.PATIENCE},{K.BATCH},{K.DROPOUT}".encode())
    return h.hexdigest()


def d_en_cache_disque():
    """Vrai si D est déjà enregistré sur cet ordinateur et à jour."""
    try:
        return (DOSSIER_CACHE / "empreinte.txt").read_text(encoding="utf-8").strip() == _empreinte_D()
    except Exception:                      # fichier absent, illisible, ou corpus de Kadiga introuvable
        return False


def _construire_D():
    """Retourne (nlp, source). source = « cache disque » ou « entraîné »."""
    try:
        if d_en_cache_disque():
            return spacy.load(DOSSIER_CACHE), "cache disque"
        train, val = K.charger("train"), K.charger("val")
    except FileNotFoundError as e:
        raise ErreurDemo("Les fichiers du corpus de Kadiga sont introuvables (dossier data/corpus_kadiga). "
                         "Vérifiez que le dépôt est complet.") from e
    nlp, _courbe = _spacy_ou_erreur(lambda: K.entrainer_D(train, val, verbeux=False))
    source = "entraîné"
    try:                                           # on garde D pour les prochains lancements
        DOSSIER_CACHE.parent.mkdir(parents=True, exist_ok=True)     # spaCy ne crée pas les dossiers parents
        temporaire = DOSSIER_CACHE.parent / "modele_D_en_cours"
        shutil.rmtree(temporaire, ignore_errors=True)
        nlp.to_disk(temporaire)
        (temporaire / "empreinte.txt").write_text(_empreinte_D(), encoding="utf-8")
        shutil.rmtree(DOSSIER_CACHE, ignore_errors=True)
        temporaire.rename(DOSSIER_CACHE)
    except OSError:
        source = "entraîné (cache non enregistré)"
    return nlp, source


def _construire(cle):
    if cle == "A":
        return _spacy_ou_erreur(lambda: R.construire(groupes=[])), "règles : aucune"
    if cle == "3a+3b":
        return _spacy_ou_erreur(lambda: R.construire(groupes=list(R.GROUPES), filtres=list(R.FILTRES_3B_FINAL))), "règles locales"
    if cle == "D":
        return _construire_D()
    raise ErreurDemo(f"Système inconnu : {cle}")


_MEMOIRE = {}    # cle -> (nlp, secondes, source) : chaque système n'est chargé qu'UNE fois par lancement


def est_charge(cle):
    return cle in _MEMOIRE


def charger_systeme(cle):
    """Retourne (nlp, secondes_de_chargement, source). Le chargement n'a lieu qu'une fois."""
    if cle not in _MEMOIRE:
        debut = time.perf_counter()
        nlp, source = _construire(cle)
        _MEMOIRE[cle] = (nlp, time.perf_counter() - debut, source)
    return _MEMOIRE[cle]


def temps_de_chargement():
    return {cle: (round(s, 1), src) for cle, (_, s, src) in _MEMOIRE.items()}


# ------------------------------------------------------------------------------------ ce que fait un système
def types_possibles(cle):
    """Les types que ce système peut RÉELLEMENT produire, lus dans le pipeline chargé (pas supposés) :
    étiquettes du NER + étiquettes des règles (EntityRuler)."""
    nlp = charger_systeme(cle)[0]
    etiquettes = set(nlp.get_pipe("ner").labels)
    if "entity_ruler" in nlp.pipe_names:
        etiquettes |= set(nlp.get_pipe("entity_ruler").labels)
    types = {ETIQUETTE_VERS_TYPE[e] for e in etiquettes if e in ETIQUETTE_VERS_TYPE}
    return [t for t in ORDRE_TYPES if t in types]


def analyser(texte, systeme=SYSTEME_PAR_DEFAUT):
    """Retourne la liste des entités trouvées : Entite(debut, fin, type, texte), dans l'ordre du texte.
    debut/fin sont des positions en caractères dans le texte reçu (fin exclue)."""
    if texte is None or not texte.strip():
        raise TexteInvalide("Le texte est vide. Écrivez ou collez un texte en français, puis cliquez sur « Analyser le texte ».")
    if len(texte) > MAX_CARACTERES:
        raise TexteInvalide(f"Le texte est trop long ({len(texte)} caractères). "
                            f"La limite de cette démonstration est de {MAX_CARACTERES} caractères : raccourcissez le texte.")
    nlp = charger_systeme(systeme)[0]
    doc = nlp(texte)
    return [Entite(e.start_char, e.end_char, ETIQUETTE_VERS_TYPE[e.label_], e.text)
            for e in doc.ents if e.label_ in ETIQUETTE_VERS_TYPE]



def entites_en_csv(entites):
    """Le contenu du fichier CSV téléchargeable (colonnes texte, type, debut, fin ; encodage lisible par Excel)."""
    import csv
    import io
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, lineterminator="\n")
    ecrivain.writerow(["texte", "type", "debut", "fin"])
    for e in entites:
        ecrivain.writerow([e.texte, e.type, e.debut, e.fin])
    return sortie.getvalue().encode("utf-8-sig")


# ------------------------------------------------------------------------------------ données de la démo
def lire_segment(id_segment):
    """Retourne le texte réel d'un segment de La Nation (corpus du dépôt). Rien n'est inventé."""
    import csv
    for fichier in ["corpus_ner.csv", "corpus_test2.csv", "corpus_test3.csv"]:
        with open(RACINE / "data" / fichier, encoding="utf-8", newline="") as f:
            for ligne in csv.DictReader(f):
                if ligne["id"] == id_segment:
                    return ligne["fr"]
    raise ErreurDemo(f"Segment introuvable dans le corpus : {id_segment}")
