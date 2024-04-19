import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Define the base URLs
MOVIE_SELECTION_BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
MOVIE_RECOMMENDATION_BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
API_KEY = "c1cf246019092e64d25ae5e3f25a3933"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"

# Set up page configuration
st.set_page_config(page_title="Movie App", layout="wide")

# Initialize session state for selected movies and movie IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []
if 'page' not in st.session_state:
    st.session_state['page'] = 'selection'

# Function to interact with the Flask backend
def fetch_data(base_url, endpoint):
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    return response.json()

# Navigation
page = st.sidebar.radio("Navigate to:", ['Selection', 'Recommendation'])

# Movie selection logic
if page == 'Selection':
    st.title("🎬 Movie Selector Interface")
    search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
    if search_term:
        st.subheader("Select from the following results:")
        search_results = fetch_data(MOVIE_SELECTION_BASE_URL, f"elastic_search/{search_term}")
        for movie in search_results:
            if st.button(movie, key=f"btn_{movie}"):
                if movie not in st.session_state['selected_movies']:
                    st.session_state['selected_movies'].append(movie)
                    # Assuming movie IDs are fetched here for use in recommendations
                    movie_id = fetch_data(MOVIE_SELECTION_BASE_URL, f"movie_id/{movie}")[0]['movieId']
                    st.session_state.movie_ids.append(movie_id)
                    st.experimental_rerun()

    # Sidebar for managing selected movies
    if st.session_state['selected_movies']:
        st.sidebar.header("Selected Movies")
        for movie in st.session_state['selected_movies']:
            if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
                idx = st.session_state['selected_movies'].index(movie)
                st.session_state['selected_movies'].pop(idx)
                st.session_state.movie_ids.pop(idx)  # Also remove the movie ID
                st.experimental_rerun()

# Movie recommendation logic
elif page == 'Recommendation':
    st.title("🎥 Movie Recommendations")
    if st.session_state.selected_movies:
        st.write("Selected Movies:", st.session_state.selected_movies)
        if st.button("Get Recommendations"):
            # Construct a new user preference matrix
            all_ratings = pd.DataFrame(fetch_data(MOVIE_RECOMMENDATION_BASE_URL, "rating_df"), columns=['userId', 'movieId', 'rating_im'])
            matrix = all_ratings.pivot_table(index='userId', columns='movieId', values='rating_im').fillna(0)
            
            new_user_ratings = pd.Series(0, index=matrix.columns)
            for mid in st.session_state.movie_ids:
                new_user_ratings[mid] = 5  # Assuming maximum preference for selected movies

            # Compute cosine similarity
            user_similarity = cosine_similarity([new_user_ratings], matrix)
            similar_users = user_similarity.argsort()[0][-3:]  # Top 3 similar users

            # Fetch and display recommendations
            recommended_ids = fetch_data(MOVIE_RECOMMENDATION_BASE_URL, f"reco/{'/'.join(map(str, similar_users))}")
            recommended_movies = pd.DataFrame(recommended_ids, columns=['movieId', 'predicted_rating_im_confidence']).head(5)
            
            for mid in recommended_movies['movieId']:
                movie_details = fetch_data(MOVIE_RECOMMENDATION_BASE_URL, f"title_from_id/{mid}")
                with st.expander(movie_details['title']):
                    movie_info = requests.get(f"{TMDB_BASE_URL}{mid}?api_key={API_KEY}").json()
                    st.image(f"https://image.tmdb.org/t/p/original{movie_info['poster_path']}")
                    st.write(f"Overview: {movie_info['overview']}")

    # Reset button for recommendations
    if st.button("Reset Selection"):
        st.session_state.selected_movies = []
        st.session_state.movie_ids = []

