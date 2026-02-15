from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 1. CONFIGURATION ET CONNEXION
# =========================================================


st.set_page_config(page_title="Music Tracks Dashboard", layout="wide")


st.title("🎵 Business Intelligence Music")
st.markdown("Analyse stratégique du catalogue de titres (Tracks)")
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


# Gestion des chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ma_base_globale.db"
TABLE_TRACKS = "table_tracks"


# Connexion à DuckDB
con = duckdb.connect(database=str(DB_PATH), read_only=True)

# =========================================================
# 2. PIPELINE DE TRAITEMENT (NETTOYAGE & DÉDOUBLONNAGE)
# =========================================================


con.execute(f"""
    CREATE OR REPLACE TEMP TABLE tracks_clean AS
   
    WITH normalized_tracks AS (
        SELECT *,
            -- Normalisation du nom (retrait parenthèses/crochets)
            TRIM(regexp_replace(CAST(name AS VARCHAR), '\\s*[\\(\\[][^\\)\\]]*[\\)\\]]', '', 'g')) as pure_name,
            -- Nettoyage de la liste des artistes
            regexp_replace(artists, '[\[\]\'']', '', 'g') as clean_artists,
            -- Extraction de l'année
            SUBSTR(TRIM(CAST(release_date AS VARCHAR)), 1, 4) as clean_year
        FROM {TABLE_TRACKS}
    ),


    dedup_logic AS (
        SELECT *,
            -- Définition de l'unicité par Nom Pur, Durée et Année
            ROW_NUMBER() OVER(
                PARTITION BY LOWER(pure_name), ROUND(duration_ms / 60000.0, 1), clean_year
                ORDER BY popularity DESC
            ) as rn
        FROM normalized_tracks
    )


    SELECT
        id,
        pure_name || ' (' || clean_artists || ')' as full_title,
        popularity,
        explicit,
        (duration_ms / 60000.0) as duration_min,
        CAST(clean_year AS INTEGER) as release_year
    FROM dedup_logic
    WHERE rn = 1
""")

# =========================================================
# 3. FILTRES (SIDEBAR)
# =========================================================


st.sidebar.header("🎯 Filtres Stratégiques")


# --- A) Période d'analyse ---
max_db = int(con.execute("SELECT MAX(release_year) FROM tracks_clean").fetchone()[0])


scope = st.sidebar.radio(
    "Amplitude de l'analyse :",
    options=["10 dernières années", "25 dernières années"],
    index=0
)


min_analysis = max_db - 10 if scope == "10 dernières années" else max_db - 25


year_range = st.sidebar.slider(
    "Ajuster la fenêtre d'observation",
    min_value=min_analysis,
    max_value=max_db,
    value=(min_analysis, max_db)
)


# --- B) Type de contenu ---
explicit_opt = st.sidebar.radio("Contenu Explicite", options=["Tous", "Oui", "Non"])
