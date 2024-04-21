import streamlit as st
import requests

# Function to interact with the Flask backend
def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    return response.json()

# Fetch movie data including posters
def fetch_movie_data_with_posters(movie_title):
    movie_id = fetch_data(f"movie_id_from_title/{movie_title.replace(' ', '_')}")
    if movie_id:
        poster_url = fetch_data(f"tmdb_id/{movie_id[0]}")  # Assuming tmdb_id endpoint returns the URL
        return poster_url

# Initialize session state for selected movies
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []

# Configure Streamlit page properties
st.set_page_config(page_title="Movie Selector", layout='wide')
st.title("🎬 Movie Selector Interface")

# Movie search and selection
search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
if search_term:
    search_results = fetch_data(f"elastic_search/{search_term}")
    cols = st.columns(3)  # Adjust the number of columns based on your layout preference
    for idx, movie in enumerate(search_results):
        with cols[idx % 3]:  # Looping through columns
            poster_url = fetch_movie_data_with_posters(movie)
            if poster_url:
                if st.button("Select", key=f"select_{movie}"):
                    if movie not in st.session_state['selected_movies']:
                        st.session_state['selected_movies'].append(movie)
                        st.experimental_rerun()
                st.image(poster_url, caption=movie, width=150)  # Adjust width as necessary

# Sidebar for managing selected movies
if st.session_state['selected_movies']:
    st.sidebar.header("Selected Movies")
    for movie in st.session_state['selected_movies']:
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            st.session_state['selected_movies'].remove(movie)
            st.experimental_rerun()
    if st.sidebar.button("Get Recommendations"):
        # Assuming you have a page or method to display recommendations
        st.switch_page('pages/movie_recommendation.py')
