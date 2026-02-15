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

# =========================================================
# 2. PIPELINE : NETTOYAGE & CLASSIFICATION
# =========================================================
con.execute(f"""
    CREATE OR REPLACE TEMP TABLE artists_clean AS
    WITH raw_prep AS (
        SELECT
            id, name as artist_name, followers, popularity,
            LOWER(genres) as g,
            TRIM(string_split(regexp_replace(genres, '[\[\]\'']', '', 'g'), ',')[1]) as main_genre_raw
        FROM {TABLE_ARTISTS}
        WHERE genres IS NOT NULL AND genres != '[]'
    )
    SELECT
        *,
        CASE
            WHEN g LIKE '%pop%' OR g LIKE '%opm%' THEN 'WORLD POP'
            WHEN g LIKE '%folk%' OR g LIKE '%flamenco%' OR g LIKE '%traditional%' THEN 'FOLK / TRADITIONAL'
            WHEN g LIKE '%hip hop%' OR g LIKE '%rap%' OR g LIKE '%trap%' THEN 'REGIONAL HIP-HOP'
            WHEN g LIKE '%amapiano%' OR g LIKE '%house%' OR g LIKE '%dance%' THEN 'ELECTRONIC / DANCE'
            WHEN g LIKE '%bollywood%' OR g LIKE '%filmi%' THEN 'FILM MUSIC'
            WHEN g LIKE '%sufi%' OR g LIKE '%qawwali%' OR g LIKE '%nasheed%' THEN 'DEVOTIONAL / SPIRITUAL'
            WHEN g LIKE '%fusion%' OR g LIKE '%hybrid%' THEN 'FUSION / GLOBAL HYBRID'
            WHEN g LIKE '%ambient%' OR g LIKE '%meditation%' THEN 'AMBIENT / WELLNESS'
            ELSE 'OTHER'
        END as genre_famille,
        CASE
            WHEN g LIKE '%pop%' OR g LIKE '%hip hop%' OR g LIKE '%trap%' OR g LIKE '%electronic%' THEN 'Modern/Fusion'
            ELSE 'Traditional/Heritage'
        END as segment_modernite
    FROM raw_prep
""")

# =========================================================
# 3. FILTRES DYNAMIQUES (SIDEBAR)
# =========================================================
st.sidebar.header("🎯 Filtres de Sélection")


familles = con.execute("SELECT DISTINCT genre_famille FROM artists_clean ORDER BY genre_famille").df()['genre_famille'].tolist()
sel_familles = st.sidebar.multiselect("Sélectionner des Familles", options=familles, default=familles[0:3])


max_foll = int(con.execute("SELECT MAX(followers) FROM artists_clean").fetchone()[0])
foll_range = st.sidebar.slider("Tranche de Followers", 0, max_foll, (0, max_foll))


sel_segment = st.sidebar.multiselect("Segment Culturel", options=['Modern/Fusion', 'Traditional/Heritage'], default=['Modern/Fusion', 'Traditional/Heritage'])


query = "SELECT * FROM artists_clean WHERE followers BETWEEN ? AND ?"
params = [foll_range[0], foll_range[1]]


if sel_familles:
    query += f" AND genre_famille IN ({','.join(['?' for _ in sel_familles])})"
    params.extend(sel_familles)


if sel_segment:
    query += f" AND segment_modernite IN ({','.join(['?' for _ in sel_segment])})"
    params.extend(sel_segment)


df_art = con.execute(query, params).df()