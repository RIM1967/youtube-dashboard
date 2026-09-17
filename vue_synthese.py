"""
Dashboard : Les vidéos qui explosent en vues sur YouTube — Vue synthèse
Dataset : YouTube Trending Videos (US, nov. 2017 - juin 2018)
"""

import streamlit as st

from data_loader import charger_donnees

# Style des cartes KPI : fond blanc, bordure fine, ombre légère, hauteur uniforme,
# avec un "kicker" numéroté en rouge au-dessus d'un titre de section en gras.
st.markdown(
    """
    <style>
    .card {
        background-color: #FFFFFF;
        border: 1px solid #ECEDF1;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 14px rgba(17,17,17,0.04);
        min-height: 260px;
        display: flex;
        flex-direction: column;
    }
    .card .kicker {
        color: #E63946;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
    }
    .card .titre-section {
        font-size: 17px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df = charger_donnees()

st.markdown(
    """<div style="display:flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
        <svg width="28" height="20" viewBox="0 0 48 34" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
            <path d="M47 5.3c-.5-2-2.1-3.6-4.1-4.1C39.1 0 24 0 24 0S8.9 0 5.1 1.2C3.1 1.7 1.5 3.3 1 5.3 0 9.1 0 17 0 17s0 7.9 1 11.7c.5 2 2.1 3.6 4.1 4.1C8.9 34 24 34 24 34s15.1 0 18.9-1.2c2-.5 3.6-2.1 4.1-4.1C48 24.9 48 17 48 17s0-7.9-1-11.7z" fill="#E62117"/>
            <path d="M19 24V10l13 7-13 7z" fill="#FFFFFF"/>
        </svg>
        <span style="font-size:2.25rem; font-weight:700; line-height:1.2; color:#111111;">Les vidéos qui explosent en vues sont surtout musicales — mais moins engageantes</span>
    </div>""",
    unsafe_allow_html=True,
)
st.caption(
    "Dataset : YouTube Trending Videos (US, nov. 2017 – juin 2018) · "
    "Vidéo « virale » = top 1 % des vues du dataset (seuil ajustable dans Vue détail)."
)
st.markdown(
    "Vue synthèse : les 3 chiffres clés à retenir, sur l'ensemble du dataset. "
    "Direction **Vue détail** (menu à gauche) pour filtrer et explorer les graphiques."
)

# ------------------------------------------------------------------
# ZONE KPIs — comparaison vidéos virales vs reste, sur tout le dataset
# Chaque KPI est affiché sous forme de barre remplie, façon infographie.
# ------------------------------------------------------------------
viral = df[df["viral"]]
reste = df[~df["viral"]]


def barre_html(label, valeur_texte, largeur_pourcent, couleur="#1f77b4"):
    """Construit une barre horizontale remplie à `largeur_pourcent` %, avec un label et une valeur."""
    largeur = max(0, min(100, largeur_pourcent))
    # .strip() retire l'indentation/retour à la ligne de tête : sans ça, Markdown
    # interprète les 4 espaces d'indentation comme un bloc de code brut, pas du HTML.
    return f"""<div style="margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:3px;">
            <span>{label}</span><span style="font-weight:bold;">{valeur_texte}</span>
        </div>
        <div style="background:#EDEDED; border-radius:6px; height:16px; overflow:hidden;">
            <div style="width:{largeur}%; background:{couleur}; height:100%; border-radius:6px;"></div>
        </div>
    </div>""".strip()


def carte_html(numero, titre, barres, note):
    """Assemble un KPI complet (kicker + titre + barres + note) en une seule carte HTML."""
    return f"""<div class="card">
        <div class="kicker">{numero}</div>
        <div class="titre-section">{titre}</div>
        {barres}
        <div style="font-size:12px; color:#6B7280; margin-top:auto; padding-top:6px;">{note}</div>
    </div>""".strip()


col1, col2, col3 = st.columns(3)

# KPI 1 — Like rate médian : deux barres comparées entre elles (pas un % d'un tout,
# donc leur longueur est relative l'une à l'autre, pas à 100 %).
with col1:
    like_viral = viral["like_rate"].median()
    like_reste = reste["like_rate"].median()
    max_like = max(like_viral, like_reste)
    barres = (
        barre_html("Top 1 % (virales)", f"{like_viral:.2%}", like_viral / max_like * 100)
        + barre_html("Reste", f"{like_reste:.2%}", like_reste / max_like * 100, couleur="#B5B5B5")
    )
    note = f"{(like_viral - like_reste):+.2%} vs reste"
    st.markdown(carte_html("01", "Like rate médian", barres, note), unsafe_allow_html=True)

# KPI 2 — Délai médian avant trending : même principe, deux barres comparées entre elles.
with col2:
    delai_viral = viral["days_to_trending"].median()
    delai_reste = reste["days_to_trending"].median()
    max_delai = max(delai_viral, delai_reste)
    barres = (
        barre_html("Top 1 % (virales)", f"{delai_viral:.0f} j", delai_viral / max_delai * 100)
        + barre_html("Reste", f"{delai_reste:.0f} j", delai_reste / max_delai * 100, couleur="#B5B5B5")
    )
    note = f"{(delai_viral - delai_reste):+.0f} j vs reste"
    st.markdown(carte_html("02", "Délai médian avant trending", barres, note), unsafe_allow_html=True)

# KPI 3 — Part de la catégorie dominante : un vrai pourcentage d'un tout, donc une
# jauge classique 0-100 % a du sens ici.
with col3:
    part_dominante = viral["category"].value_counts(normalize=True)
    categorie_dominante = part_dominante.idxmax()
    part = part_dominante.max()
    part_dans_dataset = (df["category"] == categorie_dominante).mean()
    barres = barre_html(f"{categorie_dominante} dans le Top 1 %", f"{part:.0%}", part * 100, couleur="#E00000")
    note = f"{(part - part_dans_dataset):+.0%} vs sa part globale dans le dataset"
    st.markdown(carte_html("03", f"Catégorie dominante : {categorie_dominante}", barres, note), unsafe_allow_html=True)

st.divider()
st.caption(f"{len(df):,} vidéos au total dans le dataset, dont {len(viral):,} virales (top 1 % des vues).")

# ------------------------------------------------------------------
# BANDEAU D'INVITATION — vers la page "Vue détail"
# ------------------------------------------------------------------
st.markdown(
    """<div style="background-color:#FBEAEC; border-radius:14px; padding:22px 26px; margin-top:28px;">
        <div style="font-size:17px; font-weight:700; color:#1A1A1A; margin-bottom:6px;">
            Envie d'explorer plus en détail ?
        </div>
        <div style="font-size:14px; color:#333333;">
            Direction la page <strong>Vue détail</strong> (menu à gauche) pour filtrer par
            catégorie, par période et par seuil de viralité, et explorer les graphiques
            en fonction de votre sélection.
        </div>
    </div>""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# PIED DE PAGE — source des données
# ------------------------------------------------------------------
st.markdown(
    """<div style="text-align:right; font-size:12px; color:#8A8A8A; margin-top:32px;">
        Source : YouTube Trending Videos Dataset (Kaggle) · Période couverte : nov. 2017 – juin 2018 · Analyse personnelle
    </div>""",
    unsafe_allow_html=True,
)
