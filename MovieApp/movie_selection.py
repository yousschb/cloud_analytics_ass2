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

# Improved Page Configuration
st.set_page_config(page_title="Cinematic Explorer", layout="wide", initial_sidebar_state="expanded")

# Updated Custom Styles
st.markdown("""
<style>
    h1 { text-align: center; color: #0083B8; }
    .stTextInput { width: 70%; margin: 10px auto; }
    .stButton > button { width: 90%; margin: 10px auto; background-color: #0083B8; color: white; }
    .css-18e3th9 { padding: 1.5rem; }
    .stButton > button:hover { background-color: #005f73; }
</style>
""", unsafe_allow_html=True)

# Elegant Title Display
st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>Cinematic Explorer</h1>", unsafe_allow_html=True)

# Centralized Movie Search Bar
st.write("## Explore and Select Movies")
st.write("Discover your next favorite movie. Start by typing below:")

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
