from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 1. CONFIGURATION ET CONNEXION
# =========================================================


def show_tracks():


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

    # =========================================================
    # 4. FILTRAGE DES DONNÉES
    # =========================================================


    conditions = [f"release_year BETWEEN {year_range[0]} AND {year_range[1]}"]
    if explicit_opt == "Oui":
        conditions.append("explicit = 1")
    elif explicit_opt == "Non":
        conditions.append("explicit = 0")


    df_filtered = con.execute(f"SELECT * FROM tracks_clean WHERE {' AND '.join(conditions)}").df()

    # =========================================================
    # 5. DASHBOARD - SECTION 1 : INDICATEURS CLÉS (KPI)
    # =========================================================


    st.markdown("---")
    # Calcul des métriques
    total_tracks = len(df_filtered)
    avg_pop = df_filtered['popularity'].mean() if not df_filtered.empty else 0
    explicit_rate = (df_filtered['explicit'].mean() * 100) if not df_filtered.empty else 0


    # Affichage des métriques côte à côte
    m1, m2, m3 = st.columns(3)
    m1.metric("💿 Répertoire", f"{total_tracks:,}")
    m2.metric("🔥 Popularité Moyenne", f"{avg_pop:.1f} / 100")
    m3.metric("📢 Taux d'Explicité", f"{explicit_rate:.1f}%")

    # =========================================================
    # 6. DASHBOARD - SECTION 2 : PERFORMANCE & FORMAT
    # =========================================================


    st.markdown("---")
    col_left, col_right = st.columns([1, 2])


    with col_left:
        st.subheader("⏳ Format temporel")
        avg_dur = df_filtered['duration_min'].mean() if not df_filtered.empty else 0
    
        # Affichage "Netflix Style" pour la durée
        st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #1DB954; text-align: center;">
                <h1 style="color: #1DB954; margin: 0;">{avg_dur:.2f} min</h1>
                <p style="color: #ffffff; font-size: 0.9em;">Durée moyenne par titre</p>
            </div>
        """, unsafe_allow_html=True)
    
        st.caption("Une durée stable entre 3 et 4 min indique un catalogue calibré pour la radio et le streaming.")


    with col_right:
        st.subheader("🔥 Top 5 des morceaux les plus populaires")
        df_top5 = df_filtered.sort_values('popularity', ascending=False).head(5)


        if not df_top5.empty:
            for _, row in df_top5.iterrows():
                c_title, c_score = st.columns([3, 1])
                with c_title:
                    st.write(f"**{row['full_title']}**")
                    st.progress(int(row['popularity']))
                with c_score:
                    st.write(f"Score : **{row['popularity']}**")
                    st.caption(f"Année : {row['release_year']}")
        else:
            st.info("Aucun titre ne correspond aux filtres.")

    # =========================================================
    # 7. ANALYSE DU DYNAMISME (VOLUME & TENDANCE)
    # =========================================================
    st.markdown("---")
    st.subheader("📊 Dynamisme de Production")


    if not df_filtered.empty:
        # 1. Préparation des données (on groupe par année)
        df_trend = df_filtered.groupby('release_year').size().reset_index(name='nb')
    
        # 2. Création du graphique (On s'assure qu'il n'y a qu'UN SEUL appel à px.bar)
        fig = px.bar(df_trend,
                    x='release_year',
                    y='nb',
                    color_discrete_sequence=['#1DB954'],
                    opacity=0.4)


        # 3. Ajout de la ligne de tendance
        fig.add_scatter(x=df_trend['release_year'],
                        y=df_trend['nb'],
                        line=dict(color='#00D1FF', width=3, shape='spline'),
                        name="Tendance")


        # 4. Mise en forme
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified"
        )


        # 5. L'UNIQUE affichage du graphique
        st.plotly_chart(fig, use_container_width=True, key="graphique_unique_dynamisme")


    else:
        st.info("Données insuffisantes pour cette période.")


    # =========================================================
    # FIN DU SCRIPT (Vérifie qu'il n'y a rien après con.close())
    # =========================================================
    con.close()        