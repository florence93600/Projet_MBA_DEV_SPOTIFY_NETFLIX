from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 1. CONFIGURATION ET CONNEXION
# =========================================================

# Configuration de l'interface Streamlit (doit être la première instruction)
st.set_page_config(page_title="Netflix BI Dashboard", layout="wide")

# Titre principal avec style
st.title("🎬 Business Intelligence Netflix")
st.markdown("Cartographie mondiale de l'offre : Arbitrage entre volume de production, Star Power et formats culturels.")

st.markdown("""
    <style>
    /* Taille du chiffre principal */
    [data-testid="stMetricValue"] {
        font-size: 25px !important;
    }
    /* Taille du label (le titre au-dessus) */
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Gestion des chemins de fichiers (robuste pour tout ordinateur)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ma_base_globale.db"
TABLE_NAME = "table_netflix"

# Connexion à DuckDB en mode lecture seule (plus rapide et sécurisé)
con = duckdb.connect(database=str(DB_PATH), read_only=True)

# =========================================================
# 2. PRÉPARATION DES FILTRES (SIDEBAR)
# =========================================================

st.sidebar.header("🎯 Filtres Stratégiques")

# --- A) Extraction des types (Movie/TV Show) ---
types_list = con.execute(f"SELECT DISTINCT type FROM {TABLE_NAME} WHERE type IS NOT NULL").df()["type"].tolist()
selected_types = st.sidebar.multiselect("Catégorie de produit", options=types_list, default=types_list)

# --- B) Nettoyage et Extraction des Pays ---
# On récupère les données brutes pour nettoyer les virgules traînantes
raw_countries = con.execute(f"SELECT DISTINCT country FROM {TABLE_NAME} WHERE country IS NOT NULL").df()
unique_countries = set()
for row in raw_countries['country']:
    for p in row.split(','):
        clean_p = p.strip(" ,") # Supprime espaces et virgules aux extrémités
        if clean_p: unique_countries.add(clean_p)

sorted_countries = sorted(list(unique_countries))
selected_country = st.sidebar.selectbox("Zone Géographique", options=["Tous les pays"] + sorted_countries)

# --- C) Sélection de la Période ---
year_range = st.sidebar.slider("Période de sortie", 1940, 2024, (1940, 2024))