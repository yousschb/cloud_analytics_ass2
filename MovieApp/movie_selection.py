import streamlit as st
import requests
import pandas as pd

# API Constants
API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
MOVIE = "https://api.themoviedb.org/3/movie/"

# Page Configuration
st.set_page_config(page_title="Movie Recommendation", layout="wide", initial_sidebar_state="expanded")

# Function to fetch data from Flask backend
def fetch_flask_data(url_path):
    url = "https://cloud-analytics-ass213-gev3pcymxa-uc.a.run.app/" + url_path
    response = requests.get(url)
    return response.json()

# Check for selected movies in session state
if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

# Main Page Header
st.markdown("<h1 style='text-align: center; font-size: 3rem; color: #FF0000;'>Movie Recommender </h1>", unsafe_allow_html=True)
st.write("## Movie Selection")
st.write("Search for a movie title below and select from the autocomplete suggestions to add to your watchlist.")

# Movie Search Input
movies_query = st.text_input("", placeholder="Type to search for movies...")
if movies_query:
    st.write("### Results (Click To Select):")
    autocomplete_results = fetch_flask_data(f"elastic_search/{movies_query}")
    for movie in autocomplete_results:
        button_key = f"select_{movie}"
        if st.button(movie, key=button_key):
            if movie not in st.session_state.get('movie_title_selected', []):
                st.session_state['movie_title_selected'].append(movie)

# Sidebar: Selected Movies Display
if st.session_state.get("movie_title_selected"):
    st.sidebar.header("Selected Movies")
    for movie in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f"{movie}", key=f"remove_{movie}"):
            st.session_state["movie_title_selected"].remove(movie)
            st.rerun()

# Sidebar: Recommendations Button
if st.sidebar.button("Get Recommendations", help="Click to get movie recommendations based on your selection"):
    st.switch_page('pages/movie_recommendation.py')

# Styles
st.markdown("""
<style>
    h1 { text-align: center; }
    .stTextInput, .stButton > button {
        width: 70%; 
        margin: auto;
        display: block;
        padding: 10px 25px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        background: transparent;
        color: grey;
        border: 2px solid rgb(220, 220, 220);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: black;
        color: white;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)
