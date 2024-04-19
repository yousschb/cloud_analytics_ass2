import streamlit as st
import requests

def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    return response.json()

# Initialize session state for selected movies and movie IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

st.set_page_config(page_title="Movie Selector", layout='wide')
st.title("🎬 Movie Selector Interface")

search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
if search_term:
    search_results = fetch_data(f"elastic_search/{search_term}")
    for movie in search_results:
        if st.button(movie, key=f"btn_{movie}"):
            if movie not in st.session_state['selected_movies']:
                st.session_state['selected_movies'].append(movie)
                movie_id = fetch_data(f"movie_id/{movie}")  # Assuming this returns an ID
                st.session_state['movie_ids'].append(movie_id)
                st.experimental_rerun()

st.sidebar.header("Selected Movies")
for idx, movie in enumerate(st.session_state.get('selected_movies', [])):
    if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
        st.session_state.selected_movies.pop(idx)
        st.session_state.movie_ids.pop(idx)  # Remove corresponding ID
        st.experimental_rerun()

st.write("Debug: Selected IDs", st.session_state['movie_ids'])  # Debug output
