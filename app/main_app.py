import streamlit as st
import netflix_app  
import artists_app  
import tracks_app  


# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Cross-Platform Intelligence | Netflix & Spotify",
    page_icon="📊",
    layout="wide"
)


# --- CSS PERSONNALISÉ POUR LE MENU ---
st.markdown("""
    <style>
    .main-title { font-size: 35px; font-weight: bold; color: #E50914; }
    .stRadio > label { font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)


# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/1024px-Spotify_logo_without_text.svg.png", width=50) # Optionnel
st.sidebar.title("🧭 Navigation BI")


# Choix de la page
page = st.sidebar.radio(
    "Sélectionnez un Dashboard :",
    ["🏠 Accueil", "🎬 Analyse Netflix", "👤 Analyse Artistes", "🎵 Analyse Tracks"]
)


st.sidebar.markdown("---")
st.sidebar.info(f"**Équipe :** Florence, Missaël, Carole, Marie-Paule")


# --- LOGIQUE DE NAVIGATION ---
if page == "🏠 Accueil":
    st.write("### Bienvenue dans l'outil d'aide à la décision stratégique.")
   
    col1, col2 = st.columns(2)
    with col1:
        st.info("#### 🎬 Secteur Cinéma\nAnalyse du catalogue Netflix, du Star Power et de la rétention des séries.")
    with col2:
        st.success("#### 🎧 Secteur Musique\nAnalyse du marché Spotify, segmentation des genres et performance des titres.")
   
    # Dans main.py, remplacez la ligne st.image par :
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop", caption="Dashboard de Business Intelligence", use_container_width=True)


elif page == "🎬 Analyse Netflix":
    netflix_app.show_netflix()  # ON APPELLE LA FONCTION


elif page == "👤 Analyse Artistes":
    artists_app.show_artists()  # ON APPELLE LA FONCTION


elif page == "🎵 Analyse Tracks":
    tracks_app.show_tracks()    # ON APPELLE LA FONCTION

