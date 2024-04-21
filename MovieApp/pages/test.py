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

# Function to fetch detailed information about a movie
def get_movie_details(movie_id):
    return fetch_data(f"movie_details/{movie_id}")

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
        movie_title = movie['title']
        tmdb_id = movie['id']
        if st.button(movie_title, key=f"btn_{tmdb_id}"):
            if tmdb_id not in st.session_state['movie_ids']:
                st.session_state['selected_movies'].append(movie_title)
                st.session_state['movie_ids'].append(tmdb_id)
                st.experimental_rerun()

# Sidebar for managing selected movies
selected_movies = st.session_state.get('selected_movies', [])
movie_ids = st.session_state.get('movie_ids', [])
if selected_movies:
    st.sidebar.header("Selected Movies")
    for i, movie_title in enumerate(selected_movies):
        if st.sidebar.button(f"Remove {movie_title}", key=f"remove_{movie_title}"):
            selected_movies.pop(i)
            movie_ids.pop(i)
            st.experimental_rerun()

        # Display movie details in the main area
        if st.sidebar.button(f"Show Details for {movie_title}", key=f"details_{movie_title}"):
            movie_details = get_movie_details(movie_ids[i])
            st.write(f"**Title:** {movie_details['title']}")
            st.write(f"**Overview:** {movie_details['overview']}")
            st.write(f"**Release Date:** {movie_details['release_date']}")
            st.write(f"**Genres:** {', '.join(genre['name'] for genre in movie_details['genres'])}")
            if 'poster_path' in movie_details:
                st.image(f"https://image.tmdb.org/t/p/w500/{movie_details['poster_path']}")

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

