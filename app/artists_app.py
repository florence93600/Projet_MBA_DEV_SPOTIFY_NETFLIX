from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 1. CONFIGURATION
# =========================================================
def show_artists():
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

    # =========================================================
    # 4. ANALYSE ET AFFICHAGE (UN SEUL BLOC VERTICAL)
    # =========================================================
    if not df_art.empty:
        # --- KPIs ---
        # st.markdown("---")
        # k1, k2, k3, k4 = st.columns(4)
        # k1.metric("👤 Pool Artistes", f"{len(df_art):,}")
        # k2.metric("📢 Portée Totale", f"{df_art['followers'].sum()/1e6:.1f}M folls")
        # k3.metric("🔥 Popularité Moyenne", f"{df_art['popularity'].mean():.1f}/100")
        # k4.metric("🚀 Indice Modernité", f"{(len(df_art[df_art['segment_modernite']=='Modern/Fusion'])/len(df_art)*100):.1f}%")


        st.markdown("---")
    
        # --- SECTION KPIs (AVEC FIX POUR LES CHIFFRES COUPÉS) ---
        # On utilise des st.columns mais on force l'affichage via du CSS si besoin
        k1, k2, k3, k4 = st.columns(4)
    
        with k1:
            st.metric("👤 Pool Artistes", f"{len(df_art):,}")
        with k2:
            portee_m = df_art['followers'].sum() / 1_000_000
            st.metric("📢 Portée Totale", f"{portee_m:,.1f}M")
        with k3:
            st.metric("🔥 Popularité Moyenne", f"{df_art['popularity'].mean():.1f}/100")
        with k4:
            mod_rate = (len(df_art[df_art['segment_modernite']=='Modern/Fusion'])/len(df_art)*100)
            st.metric("🚀 Indice Modernité", f"{mod_rate:.1f}%")

            # --- GRAPHIQUE 1 : BARS ---
        st.markdown("---")
        st.subheader("🔥 Top Genres Bruts (Spotify Data)")
        df_raw_genres = df_art.groupby('main_genre_raw')['followers'].sum().sort_values(ascending=False).head(15).reset_index()
        fig_raw = px.bar(df_raw_genres, x='followers', y='main_genre_raw', orientation='h',
                        color='followers', color_continuous_scale='Greens', text_auto='.2s')
        fig_raw.update_layout(yaxis={'autorange': 'reversed'}, plot_bgcolor='rgba(0,0,0,0)', yaxis_title=None, height=500)
        st.plotly_chart(fig_raw, use_container_width=True)

    # --- GRAPHIQUE 2 : SCATTER ---
        # --- GRAPHIQUE 2 : INDICE DE DYNAMISME (Lollipop Chart) ---
        st.markdown("---")
        st.subheader("🚀 Indice de Dynamisme : Quels genres dominent l'actualité ?")
    
        # 1. Préparation des données : Moyenne de popularité par Genre
        df_dyn = df_art.groupby('main_genre_raw').agg({
            'popularity': 'mean',
            'followers': 'sum'
        }).reset_index()

    # 2. On filtre les 15 genres qui ont la plus haute popularité (les plus "chauds")
        # Condition : on ne prend que ceux qui ont un minimum de poids (ex: > 100k followers)
        df_dyn = df_dyn[df_dyn['followers'] > 100000].sort_values('popularity', ascending=False).head(15)

        # 3. Création du Lollipop Chart
        fig_dyn = px.scatter(df_dyn, x='popularity', y='main_genre_raw',
                            size='popularity', color='popularity',
                            color_continuous_scale='Viridis',
                            labels={'popularity': 'Score de Popularité (0-100)', 'main_genre_raw': 'Genre'})

    # Ajout des lignes pour l'effet "Lollipop"
        for i in range(len(df_dyn)):
            fig_dyn.add_shape(
                type='line', x0=0, y0=i, x1=df_dyn.iloc[i]['popularity'], y1=i,
                line=dict(color='gray', width=1, dash='dot')
            )


        fig_dyn.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis={'autorange': 'reversed'},
            xaxis_range=[0, 105],
            height=600,
            showlegend=False
        )
    
        st.plotly_chart(fig_dyn, use_container_width=True)
    
        st.info("""
            **Indicateur de Momentum :** Il permet d'isoler les genres bénéficiant d'un engagement actif immédiat (flux), par opposition à une base de fans passive (stock).
        """)

        # --- TABLEAU FINAL ---
        st.markdown("---")
        st.subheader("🏆 Leaders du Marché (Top 10 par Followers)")
        st.dataframe(
            df_art.sort_values('followers', ascending=False).head(10)[['artist_name', 'main_genre_raw', 'genre_famille', 'followers']],
            use_container_width=True, hide_index=True
        )


    else:
        st.warning("⚠️ Aucun résultat. Essayez d'élargir les filtres.")


    con.close()