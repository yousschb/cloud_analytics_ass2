import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Setup page configuration
st.set_page_config(page_title="Movie App", layout="wide")

# Initialize session state variables if they don't exist
if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = []
if 'movie_ids' not in st.session_state:
    st.session_state.movie_ids = []
if 'page' not in st.session_state:
    st.session_state.page = 'selection'

def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    # Ensure the endpoint string starts with a '/'
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    return response.json()

# Navigation
page = st.radio("Choose a page:", ['Selection', 'Recommendation'])

# Movie selection logic
if page == 'Selection':
    st.title("🎬 Movie Selector Interface")
    search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
    if search_term:
        st.subheader("Select from the following results:")
        search_results = fetch_data(f"elastic_search/{search_term}")
        for movie in search_results:
            if st.button(movie, key=f"btn_{movie}"):
                if movie not in st.session_state['selected_movies']:
                    st.session_state['selected_movies'].append(movie)
                    # Fetch the movie ID for later use in recommendations
                    movie_id = fetch_data(f"movie_id/{movie}")[0]['movieId']
                    st.session_state.movie_ids.append(movie_id)
                    st.experimental_rerun()

    # Sidebar for managing selected movies
    selected_movies = st.session_state.get('selected_movies', [])
    if selected_movies:
        st.sidebar.header("Selected Movies")
        for movie in selected_movies:
            if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
                idx = st.session_state.selected_movies.index(movie)
                st.session_state.selected_movies.remove(movie)
                st.session_state.movie_ids.pop(idx)  # Also remove corresponding movie ID
                st.experimental_rerun()

# Movie recommendation logic
if page == 'Recommendation':
    st.title("🎥 Movie Recommendations")
    if st.session_state.selected_movies:
        st.write("Selected Movies:", st.session_state.selected_movies)
        if st.button("Get Recommendations"):
            # Assuming maximum preference for selected movies
            new_user_ratings = pd.Series(5, index=st.session_state.movie_ids)
            all_ratings = pd.DataFrame(fetch_data("rating_df"), columns=['userId', 'movieId', 'rating_im'])
            matrix = all_ratings.pivot_table(index='userId', columns='movieId', values='rating_im').fillna(0)
            
            # Compute cosine similarity
            user_similarity = cosine_similarity([new_user_ratings], matrix)
            similar_users = user_similarity.argsort()[0][-3:]  # Top 3 similar users

            # Fetch and display recommendations
            recommended_ids = fetch_data(f"reco/{'/'.join(map(str, similar_users))}")
            recommended_movies = pd.DataFrame(recommended_ids, columns=['movieId', 'predicted_rating_im_confidence']).head(5)
            
            for mid in recommended_movies['movieId']:
                movie_details = fetch_data(f"title_from_id/{mid}")
                with st.expander(movie_details['title']):
                    movie_info = requests.get(f"https://api.themoviedb.org/3/movie/{mid}?api_key=c1cf246019092e64d25ae5e3f25a3933").json()
                    st.image(f"https://image.tmdb.org/t/p/original{movie_info['poster_path']}")
                    st.write(f"Overview: {movie_info['overview']}")

    # Reset button
    if st.button("Reset Selection"):
        st.session_state.selected_movies = []
        st.session_state.movie_ids = []
