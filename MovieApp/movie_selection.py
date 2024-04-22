import streamlit as st
import requests

API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
MOVIE = "https://api.themoviedb.org/3/movie/"

st.set_page_config(page_title="Movie Recommendation", layout="wide", initial_sidebar_state="expanded")


def get_data_from_flask(url_path):
    url = "https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app/" + url_path
    response = requests.get(url)
    return response.json()

if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

# Style personnalisé pour améliorer l'esthétique de la page
st.markdown("""
<style>
    h1 { text-align: center; }
    .stTextInput { width: 50%; margin-left: auto; margin-right: auto; }
    .stButton>button { width: 100%; margin: 5px 0; }
    .css-18e3th9 { padding: 1rem; }
</style>
""", unsafe_allow_html=True)

# Beau titre avec une meilleure typographie
st.markdown("<h1 style='text-align: center; font-size: 3rem; color: #FF0000;'>Movie Recommender </h1>", unsafe_allow_html=True)

st.write("## Movie Selection")
st.write("Search for a movie title below and select from the autocomplete suggestions to add to your watchlist.")

def fetch_movie_id(title):
    data = get_data_from_flask(f"movie_id_from_title/{title}")
    if data:
        return pd.DataFrame(data, columns=["movieId"]).iloc[0]['movieId']
    return None

def display_movie_poster(movie_id):
    if movie_id:
        response = requests.get(f"{MOVIE}{movie_id}?api_key={API_KEY}")
        data = response.json()
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://image.tmdb.org/t/p/original/" + data['poster_path'], width=150)
        with col2:
            st.write(data['title'])
            if st.button("Select", key=f"select_{data['id']}"):
                if data['title'] not in st.session_state.get('movie_title_selected', []):
                    st.session_state['movie_title_selected'].append(data['title'])


# Champ de recherche centré avec autocomplete
movies_query = st.text_input("", placeholder="Type to search for movies...")
if movies_query:
    autocomplete_results = get_data_from_flask(f"elastic_search/{movies_query}")
    if autocomplete_results:
        for movie_title in autocomplete_results:
            movie_id = fetch_movie_id(movie_title)
            display_movie_poster(movie_id)
"""
# Champ de recherche centré avec autocomplete
movies_query = st.text_input("", placeholder="Type to search for movies...")
if movies_query:
    st.write("### Results (Click To Select):")
    autocomplete_results = get_data_from_flask(f"elastic_search/{movies_query}")
    if autocomplete_results:
        for i in autocomplete_results:
            button_key = f"select_{i}"
            if st.button(i, key=button_key):
                if i not in st.session_state.get('movie_title_selected', []):
                    st.session_state['movie_title_selected'].append(i)
"""

# Affichage esthétique des films sélectionnés dans la barre latérale
if st.session_state.get("movie_title_selected"):
    st.sidebar.header("Selected Movies")
    for i in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f" {i}", key=f"remove_{i}"):
            st.session_state["movie_title_selected"].remove(i)
            st.rerun()
    if st.sidebar.button("Get Recommendations", help="Click to get movie recommendations based on your selection"):
        st.switch_page('pages/movie_recommendation.py')
        
st.markdown(
    """
    <style>
    button[kind="primary"] {
        padding: 10px 25px;
        font-family: "Roboto", sans-serif;
        font-weight: 500;
        background: transparent;
        outline: none !important;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        display: inline-block;
        border: 2px solid rgb(220, 220, 220);
        z-index: 1;
        color: grey;
    }
    button[kind="primary"]:hover {
        text-decoration: none;
        outline: none !important;
        color: black !important;
    }
    button[kind="primary"]:after {
        position: absolute;
        content: "";
        width: 0;
        outline: none !important;
        height: 100%;
        top: 0;
        left: 0;
        direction: rtl;
        z-index: -1;
        background: rgb(255, 255, 255);
        transition: all 0.5s ease;
    }
    button[kind="primary"]:hover:after {
    left: auto;
    right: 0;
    outline: none !important;
    width: 100%;
    }
    button[kind="primary"]:hover span {
        background: black;
        outline: none !important;
    }
</style>


    """,
    unsafe_allow_html=True,
)
