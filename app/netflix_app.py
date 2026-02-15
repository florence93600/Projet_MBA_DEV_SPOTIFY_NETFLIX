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

# =========================================================
# 3. CONSTRUCTION DE LA REQUÊTE SQL DYNAMIQUE
# =========================================================

# Cette section traduit les choix de l'utilisateur en langage SQL
conditions = [f"release_year BETWEEN {year_range[0]} AND {year_range[1]}"]

if selected_types:
    formatted_types = ",".join([f"'{t}'" for t in selected_types])
    conditions.append(f"type IN ({formatted_types})")

if selected_country != "Tous les pays":
    # On utilise LIKE pour trouver le pays même s'il est dans une liste (ex: "France, Spain")
    conditions.append(f"country LIKE '%{selected_country}%'")

where_sql = "WHERE " + " AND ".join(conditions)

# =========================================================
# 4. SECTION DES INDICATEURS CLÉS (KPI)
# =========================================================

st.markdown("---")
# Récupération des volumes totaux
kpi_data = con.execute(f"SELECT type, COUNT(*) as total FROM {TABLE_NAME} {where_sql} GROUP BY type").df()
total_titles = kpi_data['total'].sum()

# Affichage des métriques sur une ligne
m1, m2, m3 = st.columns(3)
m1.metric("Total Catalogue", f"{total_titles:,}")
m2.metric("Movie", kpi_data[kpi_data['type']=='Movie']['total'].sum())
m3.metric("TV Show", kpi_data[kpi_data['type']=='TV Show']['total'].sum())

# =========================================================
# 5. ANALYSE FORMAT ET RÉTENTION (DEUX COLONNES)
# =========================================================

st.markdown("---")
col_format, col_retention = st.columns(2)

with col_format:
    st.subheader("⏳ Format Culturel")
    # Calcul de la durée moyenne uniquement pour les films
    q_dur = f"SELECT AVG(CAST(regexp_extract(duration, '(\\d+)', 1) AS INTEGER)) as moy FROM {TABLE_NAME} {where_sql} AND type = 'Movie'"
    avg_dur = con.execute(q_dur).df()['moy'].iloc[0]
    
    if avg_dur:
        st.markdown(f"<h1 style='text-align: center; color: #E50914;'>{avg_dur:.0f} min</h1>", unsafe_allow_html=True)
        st.caption("<p style='text-align: center;'>Durée moyenne d'un long-métrage</p>", unsafe_allow_html=True)
    else:
        st.write("Données insuffisantes")

with col_retention:
    st.subheader("🔄 Taux de Rétention (Séries)")
    # Analyse du succès des séries (plus d'une saison)
    q_ret = f"SELECT duration FROM {TABLE_NAME} {where_sql} AND type = 'TV Show'"
    df_ret = con.execute(q_ret).df()

    if not df_ret.empty:
        # Transformation : on extrait le chiffre et on catégorise
        counts = df_ret['duration'].str.extract('(\d+)').astype(int)[0].gt(1).value_counts()
        counts.index = ['Succès (2+ Saisons)', 'Saison Unique']
        
        fig_pie = px.pie(values=counts.values, names=counts.index, hole=.6, color_discrete_sequence=['#E50914', '#564d4d'])
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("Aucune série trouvée")

        
