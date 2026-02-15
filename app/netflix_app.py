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