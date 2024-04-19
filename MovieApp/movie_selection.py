import streamlit as st
import requests

# Define the base URL for the backend API
BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"

# Helper function to fetch data from the backend
def fetch_data(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.ok:
        return response.json()
    st.error("Failed to fetch data from the backend.")
    return []

# Initialize session state for storing selected movies and their IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

st.set_page_config(page_title="Movie Selector", layout='wide')
st.title("🎬 Movie Selector Interface")

# Search and select movies
search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
if search_term:
    results = fetch_data(f"elastic_search/{search_term}")
    st.subheader("Select from the following results:")
    for movie in results:
        if st.button(movie, key=f"btn_{movie}"):
            if movie not in st.session_state['selected_movies']:
                st.session_state['selected_movies'].append(movie)
                # Assuming each movie name fetches a unique ID correctly
                movie_id = fetch_data(f"movie_id/{movie}")[0]['movieId']
                st.session_state['movie_ids'].append(movie_id)

# Sidebar for managing selected movies
st.sidebar.header("Selected Movies")
for idx, movie in enumerate(st.session_state['selected_movies']):
    if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
        st.session_state['selected_movies'].pop(idx)
        st.session_state['movie_ids'].pop(idx)

