"""Tests automatiques du corpus (style TP2 : tests de non-regression).

Lancer depuis la racine du projet :  python -m pytest -q
Pre-requis : avoir lance  python src/build_dataset.py
"""
from pathlib import Path

import pandas as pd
import pytest

CORPUS = Path(__file__).resolve().parents[1] / "data" / "corpus"
LABELS = {"ORG", "LOC", "PER", "DATE", "FORM"}
SPLITS = {"train", "val", "test"}


@pytest.fixture(scope="module")
def sent():
    return pd.read_csv(CORPUS / "sentences.csv", encoding="utf-8")


@pytest.fixture(scope="module")
def ents():
    return pd.read_csv(CORPUS / "entities.csv", encoding="utf-8")


def test_trois_splits_non_vides(sent):
    assert set(sent["split"]) == SPLITS


def test_proportions_proches_de_60_20_20(sent):
    part = sent["split"].value_counts(normalize=True)
    assert 0.50 <= part["train"] <= 0.70
    assert 0.12 <= part["val"] <= 0.28
    assert 0.12 <= part["test"] <= 0.28


def test_etiquettes_valides(ents):
    assert set(ents["label"]) <= LABELS


def test_offsets_coherents(sent, ents):
    texte = dict(zip(sent["id"], sent["text"]))
    for r in ents.itertuples():
        assert texte[r.id][r.start:r.end] == r.text, (r.id, r.text)


def test_pas_de_chevauchement(ents):
    for i, g in ents.sort_values("start").groupby("id"):
        fin = -1
        for r in g.itertuples():
            assert r.start >= fin, (i, r.text)
            fin = r.end


def test_split_coherent_entre_les_deux_fichiers(sent, ents):
    split = dict(zip(sent["id"], sent["split"]))
    assert all(split[r.id] == r.split for r in ents.itertuples())


def test_pas_de_fuite_phrases_ni_blocs(sent):
    """Une phrase n'est que dans un split, et un bloc (source+section) n'est jamais coupe entre splits."""
    assert sent["id"].is_unique and sent["text"].is_unique
    par_bloc = sent.groupby("bloc")["split"].nunique()
    assert (par_bloc == 1).all(), par_bloc[par_bloc > 1].to_dict()


@pytest.mark.parametrize("label", ["ORG", "LOC", "PER", "DATE", "FORM"])
def test_classes_principales_presentes_partout(ents, label):
    for s in SPLITS:
        assert ((ents["split"] == s) & (ents["label"] == label)).sum() >= 3, (s, label)
