"""
Dashboard : Les vidéos qui explosent en vues sur YouTube
Point d'entrée : définit la navigation entre les 2 pages, avec des noms clairs.
"""

import streamlit as st

st.set_page_config(page_title="YouTube : viral ne veut pas dire engageant", page_icon="▶️", layout="wide")

pages = st.navigation([
    st.Page("vue_synthese.py", title="Vue synthèse", icon="🏠", default=True),
    st.Page("pages/1_Vue_detail.py", title="Vue détail", icon="🔍"),
])
pages.run()
