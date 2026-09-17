"""
Dashboard : Les vidéos qui explosent en vues sur YouTube — Vue détail
Filtres interactifs + 3 onglets de visualisations, réactifs aux filtres.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

from data_loader import charger_donnees

# Même style de "kicker" (petit label rouge numéroté) que sur la page Vue synthèse.
# Les styles CSS ne persistent pas d'une page à l'autre dans Streamlit, d'où la redéfinition.
st.markdown(
    """<style>
    .kicker {
        color: #E63946;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 2px;
    }
    .kicker + .titre-section {
        font-size: 15px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 10px;
    }
    </style>""",
    unsafe_allow_html=True,
)

df = charger_donnees()

st.title("🔍 Vue détail — Explorer vues et engagement")
st.caption(
    "Filtrez par catégorie, plage de vues, période et seuil de viralité "
    "pour explorer la relation entre popularité et engagement."
)

# ------------------------------------------------------------------
# SIDEBAR — FILTRES
# ------------------------------------------------------------------
st.sidebar.header("Filtres")

categories = sorted(df["category"].unique())

with st.sidebar.popover("📁 Catégories", use_container_width=True):
    col_a, col_b = st.columns(2)
    if col_a.button("Tout cocher", use_container_width=True):
        for cat in categories:
            st.session_state[f"cat_{cat}"] = True
    if col_b.button("Tout décocher", use_container_width=True):
        for cat in categories:
            st.session_state[f"cat_{cat}"] = False

    # Hauteur fixe avec défilement interne, pour que le panneau ne déborde
    # jamais en haut de l'écran quel que soit le nombre de catégories.
    with st.container(height=250):
        categories_choisies = [
            cat for cat in categories if st.checkbox(cat, value=True, key=f"cat_{cat}")
        ]

vues_min, vues_max = int(df["views"].min()), int(df["views"].max())
plage_vues = st.sidebar.slider(
    "Plage de vues",
    min_value=vues_min,
    max_value=vues_max,
    value=(vues_min, vues_max),
)

date_min, date_max = df["trending_date"].min().date(), df["trending_date"].max().date()
periode = st.sidebar.slider(
    "Période (date de tendance)",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max),
)

seuil_pourcentage = st.sidebar.slider(
    "Seuil de viralité",
    min_value=0.5,
    max_value=10.0,
    value=1.0,
    step=0.5,
    format="Top %.1f %%",
    help="Définit quelles vidéos sont considérées comme « virales » : les X % avec le plus de vues, dans la sélection actuelle.",
)

df_filtre = df[
    df["category"].isin(categories_choisies)
    & df["views"].between(*plage_vues)
    & df["trending_date"].between(pd.Timestamp(periode[0]), pd.Timestamp(periode[1]))
]

# Le seuil de viralité est recalculé sur la sélection filtrée : "Top X %"
# désigne les X % de vidéos les plus vues parmi celles actuellement affichées.
if len(df_filtre) > 0:
    seuil_dynamique = df_filtre["views"].quantile(1 - seuil_pourcentage / 100)
    viral = df_filtre[df_filtre["views"] >= seuil_dynamique]
    reste = df_filtre[df_filtre["views"] < seuil_dynamique]
else:
    viral = df_filtre
    reste = df_filtre

# ------------------------------------------------------------------
# ZONE DÉTAIL — un onglet par visualisation, réactifs aux filtres
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Vues vs engagement", "🏷️ Par catégorie", "🔥 Profil des vidéos virales", "📋 Vidéos",
])

PLOT_LAYOUT = dict(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font_color="#111111")
GRID_COLOR = "#E1E0D9"
BLEU = "#1f77b4"   # popularité (vues)
ROUGE = "#E63946"  # engagement (like rate) — même rouge que le reste du dashboard

with tab1:
    st.subheader("Vues vs taux de like, par catégorie")

    df_plot = df_filtre.copy()
    df_plot["log_views"] = np.log10(df_plot["views"].clip(lower=1))

    fig1 = px.scatter(
        df_plot,
        x="log_views",
        y="like_rate",
        color="category",
        hover_data=["title", "channel_title", "views"],
        labels={"log_views": "Vues (échelle log10)", "like_rate": "Taux de like"},
        opacity=0.6,
    )
    fig1.update_layout(**PLOT_LAYOUT, legend_title_text="Catégorie")
    fig1.update_xaxes(gridcolor=GRID_COLOR)
    fig1.update_yaxes(gridcolor=GRID_COLOR)
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Vues médianes par catégorie")

    vues_par_categorie = (
        df_filtre.groupby("category")["views"].median().sort_values(ascending=True)
    )
    fig2 = px.bar(
        vues_par_categorie,
        orientation="h",
        labels={"value": "Vues médianes", "category": "Catégorie"},
        text=vues_par_categorie.apply(lambda v: f"{v:,.0f}"),
        color=vues_par_categorie.values,
        color_continuous_scale="Blues",
    )
    fig2.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="outside",
        textfont=dict(color="#111111", size=12),
        cliponaxis=False,
        marker_line_width=0,
    )
    fig2.update_layout(**PLOT_LAYOUT, showlegend=False, coloraxis_showscale=False, margin=dict(r=70))
    fig2.update_xaxes(gridcolor=GRID_COLOR)
    fig2.update_yaxes(gridcolor="#FFFFFF")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Taux de like médian par catégorie")

    like_rate_par_categorie = (
        df_filtre.groupby("category")["like_rate"].median().sort_values(ascending=True)
    )
    fig2b = px.bar(
        like_rate_par_categorie,
        orientation="h",
        labels={"value": "Taux de like médian", "category": "Catégorie"},
        text=like_rate_par_categorie.apply(lambda v: f"{v:.2%}"),
        color=like_rate_par_categorie.values,
        color_continuous_scale="Reds",
    )
    fig2b.update_traces(
        texttemplate="<b>%{text}</b>",
        textposition="outside",
        textfont=dict(color="#111111", size=12),
        cliponaxis=False,
        marker_line_width=0,
    )
    fig2b.update_layout(**PLOT_LAYOUT, showlegend=False, coloraxis_showscale=False, margin=dict(r=70))
    fig2b.update_xaxes(gridcolor=GRID_COLOR)
    fig2b.update_yaxes(gridcolor="#FFFFFF")
    st.plotly_chart(fig2b, use_container_width=True)

    # Phrase de synthèse : la catégorie la plus vue n'est pas forcément la plus engageante.
    if len(vues_par_categorie) > 0 and len(like_rate_par_categorie) > 0:
        categorie_plus_vue = vues_par_categorie.idxmax()
        categorie_plus_engageante = like_rate_par_categorie.idxmax()
        if categorie_plus_vue == categorie_plus_engageante:
            st.markdown(
                f"**{categorie_plus_vue}** domine à la fois en vues et en engagement dans cette sélection."
            )
        else:
            st.markdown(
                f"**{categorie_plus_vue}** est la catégorie la plus vue, mais "
                f"**{categorie_plus_engageante}** engage proportionnellement le plus : "
                f"viser les vues et viser l'engagement ne mènent pas à la même catégorie."
            )

with tab3:
    st.subheader(f"Profil des vidéos virales (Top {seuil_pourcentage:.1f} % des vues)")
    st.caption("Reprise des graphiques du notebook (Q4), recalculés dynamiquement selon les filtres.")

    if len(viral) > 0 and len(reste) > 0:
        like_viral = viral["like_rate"].median()
        like_reste = reste["like_rate"].median()
        delai_viral = viral["days_to_trending"].median()
        delai_reste = reste["days_to_trending"].median()
        part_dominante = viral["category"].value_counts(normalize=True)
        categorie_dominante = part_dominante.idxmax()
        part = part_dominante.max()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(
                '<div class="kicker">01</div><div class="titre-section">Catégorie dominante</div>',
                unsafe_allow_html=True,
            )
            fig_donut, ax_donut = plt.subplots(figsize=(4, 4))
            fig_donut.patch.set_facecolor("#FFFFFF")
            ax_donut.pie(
                [part, 1 - part],
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.28, edgecolor="#FFFFFF"),
                colors=["#E63946", "#E1E3E6"],
            )
            ax_donut.text(0, 0.04, f"{part:.0%}", ha="center", va="center", fontsize=26, fontweight="bold")
            ax_donut.text(0, -0.16, categorie_dominante.upper(), ha="center", va="center", fontsize=11, fontweight="bold", color="#555555")
            ax_donut.axis("off")
            st.pyplot(fig_donut)
            st.caption(f"{part:.0%} des vidéos virales sont « {categorie_dominante} ».")

        with c2:
            st.markdown(
                '<div class="kicker">02</div><div class="titre-section">L\'engagement</div>',
                unsafe_allow_html=True,
            )
            fig_bar1, ax1 = plt.subplots(figsize=(4, 4))
            fig_bar1.patch.set_facecolor("#FFFFFF")
            valeurs = [like_viral * 100, like_reste * 100]
            barres = ax1.bar([f"Top {seuil_pourcentage:.1f} %", "Reste"], valeurs, width=0.52, color=ROUGE)
            ax1.set_ylabel("Like rate médian (%)")
            for barre, valeur in zip(barres, valeurs):
                ax1.text(barre.get_x() + barre.get_width() / 2, valeur, f"{valeur:.2f} %",
                          ha="center", va="bottom", fontweight="bold")
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            ax1.grid(axis="y", alpha=0.2)
            st.pyplot(fig_bar1)

        with c3:
            st.markdown(
                '<div class="kicker">03</div><div class="titre-section">Délai avant trending</div>',
                unsafe_allow_html=True,
            )
            fig_bar2, ax2 = plt.subplots(figsize=(4, 4))
            fig_bar2.patch.set_facecolor("#FFFFFF")
            valeurs2 = [delai_viral, delai_reste]
            barres2 = ax2.bar([f"Top {seuil_pourcentage:.1f} %", "Reste"], valeurs2, width=0.52, color=BLEU)
            ax2.set_ylabel("Délai médian (jours)")
            for barre, valeur in zip(barres2, valeurs2):
                ax2.text(barre.get_x() + barre.get_width() / 2, valeur, f"{valeur:.0f} j",
                          ha="center", va="bottom", fontweight="bold")
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            ax2.grid(axis="y", alpha=0.2)
            st.pyplot(fig_bar2)

        st.markdown(
            f"**{categorie_dominante} domine le Top {seuil_pourcentage:.1f} % ({part:.0%})**, mais ces vidéos "
            f"ont un like rate plus faible ({like_viral:.2%} contre {like_reste:.2%}) et "
            f"mettent plus de temps à apparaître en tendance "
            f"({delai_viral:.0f} j contre {delai_reste:.0f} j)."
        )
    else:
        st.info("Pas assez de données dans cette sélection pour ce comparatif.")

with tab4:
    st.subheader("Liste des vidéos (sélection filtrée)")
    st.caption("Cliquez sur un titre pour ouvrir la vidéo sur YouTube.")

    tableau = df_filtre[
        ["title", "channel_title", "category", "views", "likes", "like_rate", "video_id"]
    ].sort_values("views", ascending=False).copy()

    # L'URL n'est pas dans le dataset : on la reconstruit à partir du video_id,
    # un identifiant YouTube standard (youtube.com/watch?v=ID).
    tableau["url"] = "https://www.youtube.com/watch?v=" + tableau["video_id"]
    tableau["like_rate_pct"] = tableau["like_rate"] * 100

    st.dataframe(
        tableau[["title", "url", "channel_title", "category", "views", "likes", "like_rate_pct"]],
        column_config={
            "title": st.column_config.TextColumn("Titre"),
            "url": st.column_config.LinkColumn("Lien", display_text="Voir sur YouTube"),
            "channel_title": st.column_config.TextColumn("Chaîne"),
            "category": st.column_config.TextColumn("Catégorie"),
            "views": st.column_config.NumberColumn("Vues", format="%d"),
            "likes": st.column_config.NumberColumn("Likes", format="%d"),
            "like_rate_pct": st.column_config.NumberColumn("Taux de like", format="%.2f %%"),
        },
        hide_index=True,
        use_container_width=True,
    )

st.caption(
    f"{len(df_filtre):,} vidéos affichées sur {len(df):,} au total ({len(viral):,} virales dans la sélection)."
)
