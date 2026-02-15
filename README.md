# Projet_MBA_DEV_SPOTIFY_NETFLIX


## 📊 Cross-Platform Data Intelligence : Netflix & Spotify
### 📝 Présentation du Projet
Ce projet de Business Intelligence, réalisé pour le MBA ESG, propose une plateforme analytique interactive permettant de décrypter les stratégies de contenus de Netflix et Spotify.
L'application utilise une architecture performante basée sur DuckDB pour traiter plus d'un million de lignes, offrant des insights stratégiques sur la production cinématographique et les dynamiques du marché musical.


<h2>Tableau des Membres de l'Équipe</h2>

<table>
    <thead>
        <tr>
            <th>Membre</th>
            <th>Rôle</th>
            <th>Responsabilités Clés</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Florence</td>
            <td>Data Engineer (Lead)</td>
            <td>Architecture DuckDB (init_db.py), menu de navigation (main.py) et gestion GitHub.</td>
        </tr>
        <tr>
            <td>Missaël</td>
            <td>Product Owner Netflix</td>
            <td>Dashboard Cinéma, Analyse du Star Power et optimisation de l'interface (CSS).</td>
        </tr>
        <tr>
            <td>Carole</td>
            <td>Market Analyst</td>
            <td>Dashboard Artistes, segmentation "Modernité vs Heritage" et momentum Spotify.</td>
        </tr>
        <tr>
            <td>Marie-Paule</td>
            <td>Data Analyst</td>
            <td>Dashboard Tracks, analyse des formats (durée) et tendances de production.</td>
        </tr>
    </tbody>
</table>

</body>
</html>

### 🚀 Installation et Lancement
Pour exécuter ce projet localement, suivez ces étapes :
1. Préparation de l'environnement
Bash
* Clonage du projet
git clone https://github.com/florence93600/Projet_MBA_DEV_SPOTIFY_NETFLIX.git
cd Projet_MBA_DEV_SPOTIFY_NETFLIX

* Création de l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate

* Installation des bibliothèques
pip install -r requirements.txt


2. Initialisation des données
Les fichiers CSV originaux sont dans le dossier data_csv/.
Bash
python init_db.py


3. Exécution de l'application
Bash
streamlit run main_app.py


### 🛠️ Stack Technique
Backend : Python 3.10+, DuckDB (Moteur SQL analytique).
Frontend : Streamlit, Plotly Express (Visualisations dynamiques).
Collaboration : Git/GitHub (Workflow par branches et Pull Requests).
### 📂 Sources des Données
Les analyses s'appuient sur des datasets open-source de référence :
Netflix : https://www.kaggle.com/datasets/abhinavrongala/netflix-datasets-evaluation?select=Netflix+Datasets+Evaluation+MS+Excel.csv
Spotify :https://www.kaggle.com/datasets/nimishasen27/spotify-dataset


