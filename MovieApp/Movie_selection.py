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

# Main Page Header with added spacing via HTML
st.markdown("""
<h1 style='text-align: center; font-size: 3rem; color: #FF0000;'>Movie Recommender</h1>
<br>  
""", unsafe_allow_html=True)

# Additional space before the introductory text
st.markdown("""
<p style='text-align: center; margin-top: 20px;'>
    Search for a movie title below and select from the autocomplete suggestions to add to your watchlist.
</p>
""", unsafe_allow_html=True)

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
    st.sidebar.header("Selected Movies (click to remove) ")
    for movie in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f"{movie}", key=f"remove_{movie}"):
            st.session_state["movie_title_selected"].remove(movie)
            st.rerun()

# Sidebar: Recommendations Button
if st.sidebar.button("Get Recommendations", help="Click to get movie recommendations based on your selection"):
    st.switch_page('pages/Movie_recommendation.py')

# Styles
st.markdown("""
<style>
    body {
        background-color: #f0f2f6;
    }

    h1 { text-align: center; }

    /* Improved styling for text inputs */
    .stTextInput > div > div > input {
        width: 70%; 
        margin: 20px auto;
        padding: 10px 25px;
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        border-radius: 20px;
        border: 2px solid rgb(220, 220, 220);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    /* Specific styles for result buttons under the search bar */
    .stButton > button {
        width: 70%;
        margin: 10px auto;
        display: block;
        padding: 10px 25px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        background-color: black; /* Fond noir */
        color: white; /* Texte blanc */
        border: 2px solid #FF0000; /* Bordure rouge */
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    /* Hover effects for result buttons under the search bar */
    .stButton > button:hover {
        background-color: #333; /* Fond plus sombre au survol */
        color: white;
        border-color: #FF0000; /* Bordure rouge maintenue */
    }

    /* Styles for the sidebar */
    .stSidebar .stButton > button {
        background-color: #FF0000; /* Fond rouge */
        color: white; /* Texte blanc */
        border-color: #FF0000; /* Bordure rouge */
    }

    .stSidebar .stButton > button:hover {
        background-color: #C80000; /* Rouge plus sombre au survol */
        border-color: #C80000; /* Bordure rouge plus sombre */
    }
</style>
""", unsafe_allow_html=True)

