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
                st.session_state['selected_movies'].append(movie)
                st.experimental_rerun()

# Sidebar for managing selected movies
selected_movies = st.session_state.get('selected_movies', [])  # Use .get with default empty list
if selected_movies:
    st.sidebar.header("Selected Movies")
    for movie in selected_movies:
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            selected_movies.remove(movie)
            st.experimental_rerun()
    if st.sidebar.button("Get Recommendations", type= "primary"):
        st.switch_page('pages/movie_recommendation.py')

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
