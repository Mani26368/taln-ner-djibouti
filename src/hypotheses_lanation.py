"""Ajoute les hypothèses de cause (écrites à la main) dans results/erreurs_lanation.csv.

Ce sont des HYPOTHÈSES, pas des causes vérifiées. Elles ne changent aucun score.
Clé : (id_segment, entité prédite, entité réelle). Lancer : python src/hypotheses_lanation.py
"""
import sys
from pathlib import Path

import pandas as pd

CSV = Path(__file__).resolve().parent.parent / "results" / "erreurs_lanation.csv"

H = {
    # --- DATE : manquées
    ("A01_S002", "", "lundi"):
        "Certain, pas une hypothèse : le NER de spaCy n'a pas d'étiquette DATE (seulement LOC, MISC, ORG, PER). Toutes les DATE du gold sont donc manquées.",
    ("A12_S001", "", "30 et 31 août 2026"):
        "Même cause : A ne produit jamais DATE.",
    # --- mauvaise frontière : convention d'annotation différente
    ("A01_S001", "Secrétaire générale de l'OIF", "OIF"):
        "Écart de convention : spaCy prend fonction + organisation comme un seul ORG ; notre guide exclut la fonction et garde le sigle seul.",
    ("A01_S004", "aéroport international de Djibouti", "Djibouti"):
        "Écart de convention : notre guide n'annote pas le nom commun (« aéroport international ») ; spaCy garde tout le groupe nominal.",
    ("A02_S001", "ministre de l'Agriculture", ""):
        "Écart de convention : une fonction n'est pas une entité dans notre guide. spaCy prend « ministre de l'Agriculture » pour une ORG.",
    # --- fausse détection
    ("A01_S002", "Secrétaire générale", ""):
        "Le titre « Secrétaire générale » est écrit avec des majuscules ; spaCy le prend pour un nom d'organisation. Fonction = pas d'entité chez nous.",
    ("A01_S008", "Mission économique de la Francophonie", ""):
        "Événement : notre guide exclut les événements. spaCy voit un nom propre (majuscules + « Francophonie ») et prédit une ORG.",
    ("A02_S001", "Eau", ""):
        "Énumération de domaines d'un ministre (« de l'Eau, de la Pêche, de l'Élevage ») : mots à majuscule après « de l' », que spaCy range en LOC.",
    ("A08_S025", "Organisation", ""):
        "Mention courte (« l'Organisation » pour l'OMS) : exclue par notre guide ; spaCy reconnaît le mot avec majuscule comme ORG.",
    ("A08_S049", "Diabète", ""):
        "Mot commun en début de phrase : la majuscule initiale suffit à tromper le modèle (signal « nom propre » trop fort).",
    ("A08_S067", "Détecter", ""):
        "Verbe à l'infinitif en début de phrase pris pour un nom de personne : même cause que « Diabète » (majuscule initiale).",
    ("A14_S001", "Challenge", ""):
        "Mot anglais écrit avec une majuscule, hors du vocabulaire français courant : pris pour un lieu. C'est aussi le début d'un nom d'événement.",
    ("A03_S002", "Fédération", ""):
        "Mention courte (« la Fédération ») non annotée chez nous ; en plus l'étiquette change selon la phrase (LOC ici, ORG ailleurs), ce qui montre que le modèle devine à partir du contexte.",
    ("A15_S001", "Activités Estivales 2026", ""):
        "Événement : exclu par notre guide ; spaCy le voit comme un nom propre d'organisation (majuscules, année).",
    ("A11_S004", "Encadrée", ""):
        "Participe passé en début de phrase, pris pour un lieu : même cause que « Diabète » et « Détecter » (majuscule initiale).",
    # --- mauvaise frontière : nom propre local
    ("A01_S004", "Mariam Hamadou", "Mariam Hamadou Ali"):
        "Nom djiboutien peu fréquent dans les données d'entraînement : le modèle s'arrête avant le dernier élément « Ali ».",
    ("A10_S029", "Mohamed", "Mohamed Houmed Abass"):
        "Plusieurs noms arabes/somali à la suite dans une phrase longue : le modèle coupe en morceaux (« Mohamed », « Abass ») au lieu d'un seul nom complet.",
    ("A12_S001", "Djibouti", "Djibouti-ville"):
        "Nom composé avec trait d'union : spaCy découpe en 3 tokens (Djibouti, -, ville) et ne garde que « Djibouti ».",
    ("A10_S011", "Zone", "Zone portuaire Sud"):
        "Nom de lieu qui contient un mot en minuscule (« portuaire ») : le modèle s'arrête au premier mot à majuscule et coupe l'entité.",
    ("A03_S008", "Secrétariat d'État", "Secrétariat d'État chargé des Sports"):
        "Intitulé long avec « chargé des » : le modèle s'arrête après « d'État » ; seul « Sports » est repris à part en ORG.",
    ("A03_S014", "Comité", "Comité ad hoc"):
        "L'expression latine « ad hoc » (minuscules) n'est pas rattachée à « Comité ».",
    # --- mauvais type / type + frontière
    ("A02_S002", "Douda Tazwid Industries", "Douda Tazwid Industries"):
        "Nom d'entreprise local, inconnu du modèle : trois mots à majuscule qui ressemblent à un nom de personne, donc PER au lieu d'ORG.",
    ("A14_S001", "Ardo Bankoualé", "Ardo Bankoualé"):
        "Nom de localité afar/somali absent des données d'entraînement : ressemble à un nom de personne, donc PER au lieu de LOC. Un lexique de lieux locaux aiderait.",
    ("A14_S006", "Ardo", "Coopérative artisanale des femmes d'Ardo"):
        "Organisation locale dont le nom commence par un nom commun en minuscules (« Coopérative artisanale des femmes ») : le modèle ne repère que le nom propre « Ardo ».",
    # --- manquées : noms locaux
    ("A11_S002", "", "Ali-Sabieh"):
        "Nom de région djiboutienne avec trait d'union, absent du modèle (français général) : le modèle ne le reconnaît pas du tout.",
    ("A03_S007", "", "Abeyazide"):
        "Nom rare derrière la civilité « Me » : le modèle voit « Me Abeyazide » comme MISC (étiquette ignorée par le mapping de Kadiga), pas comme PER.",
}


def main():
    df = pd.read_csv(CSV, encoding="utf-8-sig", keep_default_na=False)
    cle = list(zip(df["id_segment"], df["entité_prédite"], df["entité_réelle"]))
    manquantes = [k for k in H if k not in set(cle)]
    if manquantes:
        sys.exit(f"Clés absentes du CSV : {manquantes}")
    df["hypothèse_cause"] = [H.get(k, "") for k in cle]
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    print(f"{(df['hypothèse_cause'] != '').sum()} erreurs avec hypothèse sur {len(df)}")
    print(df[df["hypothèse_cause"] != ""]["type_erreur"].value_counts().to_string())


if __name__ == "__main__":
    main()
