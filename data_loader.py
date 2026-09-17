"""Chargement et préparation des données, partagés entre toutes les pages du dashboard."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# Copie locale du CSV, livrée avec le script (aucun téléchargement en ligne).
# Chemin basé sur l'emplacement de ce fichier, indépendant du dossier de lancement.
DATA_PATH = Path(__file__).parent / "data" / "youtube.csv"

# Mapping des identifiants de catégorie vers leur nom (repris du notebook d'analyse)
CATEGORY_MAP = {
    1: "Film & Animation", 2: "Autos & Vehicles", 10: "Music",
    15: "Pets & Animals", 17: "Sports", 20: "Gaming",
    22: "People & Blogs", 23: "Comedy", 24: "Entertainment",
    25: "News & Politics", 26: "Howto & Style", 27: "Education",
    28: "Science & Tech", 29: "Nonprofits",
}

COLS = [
    "video_id", "trending_date", "title", "channel_title", "category_id",
    "publish_date", "views", "likes", "dislikes", "comment_count",
]


@st.cache_data
def charger_donnees():
    """Charge le CSV local (aucun téléchargement en ligne) et prépare les colonnes dérivées."""
    df = pd.read_csv(DATA_PATH, encoding="latin-1", usecols=COLS)

    df["category"] = df["category_id"].map(CATEGORY_MAP)

    # Taux de like : proportion de likes par vue
    df["like_rate"] = np.where(df["views"] > 0, df["likes"] / df["views"], np.nan)

    # Délai entre publication et entrée en tendance
    df["publish_date"] = pd.to_datetime(df["publish_date"], format="%d/%m/%Y")
    df["trending_date"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")
    df["days_to_trending"] = (df["trending_date"] - df["publish_date"]).dt.days

    # Une vidéo est "virale" si elle est dans le top 1 % des vues
    seuil_viral = df["views"].quantile(0.99)
    df["viral"] = df["views"] >= seuil_viral

    return df.dropna(subset=["category"])
