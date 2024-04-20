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

# Initialize session state for selected movies and movie IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

# Configure Streamlit page properties
st.set_page_config(page_title="Movie Selector", layout='wide')
st.title("🎬 Movie Selector Interface")

# Movie search and selection
search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
if search_term:
    st.subheader("Select from the following results:")
    search_results = fetch_data(f"elastic_search/{search_term}")
    for movie in search_results:
        if st.button(movie, key=f"btn_{movie}"):
            if movie not in st.session_state['selected_movies']:
                # Fetch the movie ID when a movie is selected
                movie_id_response = fetch_data(f"movie_ids/{movie.replace(' ', '%20')}")  # Encode space as URL encoded
                if movie_id_response:
                    movie_id = movie_id_response['movieId'][0]  # Assuming the first entry is the correct ID
                    st.session_state['selected_movies'].append(movie)
                    st.session_state['movie_ids'].append(movie_id)
                st.experimental_rerun()

# Sidebar for managing selected movies
if st.session_state['selected_movies']:
    st.sidebar.header("Selected Movies")
    for i, movie in enumerate(st.session_state['selected_movies']):
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            # Remove movie and its ID
            st.session_state['selected_movies'].pop(i)
            st.session_state['movie_ids'].pop(i)
            st.experimental_rerun()

# Custom CSS for button aesthetics
st.markdown("""
    <style>
    .stButton>button {
        border: 2px solid #4CAF50;
        color: #FFFFFF;
        background-color: #4CAF50;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 12px;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
        border: 2px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
