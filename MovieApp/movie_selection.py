import streamlit as st
import requests
import pandas as pd
API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
MOVIE = "https://api.themoviedb.org/3/movie/"

st.set_page_config(page_title="Movie Recommendation", layout="wide", initial_sidebar_state="expanded")


def fetch_flask_data(url_path):
    url = "https://cloud-analytics-ass213-gev3pcymxa-uc.a.run.app/" + url_path
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

# Champ de recherche centré avec autocomplete
movies_query = st.text_input("", placeholder="Type to search for movies...")
if movies_query:
    st.write("### Results (Click To Select):")
    autocomplete_results = fetch_flask_data(f"elastic_search/{movies_query}")
    if autocomplete_results:
        for i in autocomplete_results:
            button_key = f"select_{i}"
            if st.button(i, key=button_key):
                if i not in st.session_state.get('movie_title_selected', []):
                    st.session_state['movie_title_selected'].append(i)


# Affichage esthétique des films sélectionnés dans la barre latérale
if st.session_state.get("movie_title_selected"):
    st.sidebar.header("Selected Movies")
    for i in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f" {i}", key=f"remove_{i}"):
            st.session_state["movie_title_selected"].remove(i)
            st.rerun()
    if st.sidebar.button("Get Recommendations", help="Click to get movie recommendations based on your selection"):
        st.switch_page('pages/movie_recommendation.py')
        
st.markdown("""
<style>
    .stTextInput, .stButton > button {
        transition: all 0.3s ease-in-out;
        border-radius: 10px;
    }
    .stTextInput:hover, .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

