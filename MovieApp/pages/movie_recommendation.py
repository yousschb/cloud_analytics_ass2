import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Define API URL and Key
API_KEY = "?api_key=81eb26f048683218d8f96f9fab8e8c52"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"
BACKEND_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app/"

# Setup Streamlit page
st.set_page_config(page_title="Movie Recommendations", layout="wide")
st.title("🎥 Movie Recommendations")

# Function to fetch data from backend
def fetch_data(endpoint):
    response = requests.get(BACKEND_URL + endpoint)
    if response.ok:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.text}")
        return None

# Display selected movies in sidebar    
if st.session_state.get("selected_movies"):
    st.sidebar.write("You have selected these movies:")
    for movie in st.session_state["selected_movies"]:
        st.sidebar.write(movie)
else:
    st.write("You have not selected any movies yet.")

# Button to generate recommendations
if st.button("Get Recommendations"):
    if st.session_state.get('movie_ids'):
        # Construct a new user preference matrix
        ratings_data = fetch_data("rating_df")
        if ratings_data:
            user_ratings = pd.DataFrame(ratings_data, columns=['userId', 'movieId', 'rating_im'])
            user_matrix = user_ratings.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)

            new_user_ratings = pd.Series(0, index=user_matrix.columns)
            for mid in st.session_state['movie_ids']:
                if mid in new_user_ratings.index:
                    new_user_ratings[mid] = 5  # Assuming maximum preference

            # Compute cosine similarity
            user_similarity = cosine_similarity([new_user_ratings], user_matrix)
            similar_users = user_similarity.argsort()[0][-3:]  # Top 3 similar users

            # Fetch and display recommendations
            recommended_ids = fetch_data(f"reco/{'/'.join(map(str, similar_users))}")
            if recommended_ids:
                recommended_movies = pd.DataFrame(recommended_ids, columns=['movieId', 'predicted_rating_im_confidence']).head(5)

                st.write("Based on the movies you selected, we recommend you to watch these movies:")
                for mid in recommended_movies['movieId']:
                    movie_details = fetch_data(f"title_from_id/{mid}")
                    if movie_details:
                        with st.expander(movie_details['title']):
                            movie_info = requests.get(f"{TMDB_BASE_URL}{mid}{API_KEY}").json()
                            if 'poster_path' in movie_info and 'overview' in movie_info:
                                st.image(f"https://image.tmdb.org/t/p/original{movie_info['poster_path']}")
                                st.write(f"Overview: {movie_info['overview']}")
                    else:
                        st.error("Failed to fetch movie details.")
    else:
        st.error("No movies selected for recommendations. Please select some movies first.")

# Reset button
if st.button("Reset Selection"):
    st.session_state['selected_movies'] = []
    st.session_state['movie_ids'] = []
