from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 1. CONFIGURATION
# =========================================================
st.set_page_config(page_title="Music Data Intelligence", layout="wide")
st.title("👤 Artists Market Analysis")
st.markdown("Analyse structurelle de l'offre musicale : Arbitrage stratégique entre courants Heritage et dynamiques Modern/Fusion.")


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


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ma_base_globale.db"
TABLE_ARTISTS = "table_artists"


con = duckdb.connect(database=str(DB_PATH), read_only=True)
