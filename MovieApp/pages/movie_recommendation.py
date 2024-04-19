import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Define API URL and Key
API_KEY = "81eb26f048683218d8f96f9fab8e8c52"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"
BACKEND_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app/"

# Setup Streamlit page
st.set_page_config(page_title="Movie Recommendations", layout="wide")
st.title("🎥 Movie Recommendations")

# Display selected movies in sidebar    
if st.session_state.get("selected_movies"):
    st.sidebar.write("You have selected these movies:")
    for movie in st.session_state["selected_movies"]:
        st.sidebar.write(movie)
else:
    st.write("You have not selected any movies yet.")

# Generate recommendations
if st.session_state.get('movie_ids'):
    # Construct a new user preference matrix
    user_ratings = pd.DataFrame(get_data_from_flask("rating_df"), columns=['userId', 'movieId', 'rating_im'])
    user_matrix = user_ratings.pivot_table(index='userId', columns='movieId', values='rating_im').fillna(0)

    new_user_ratings = pd.Series(0, index=user_matrix.columns)
    for mid in st.session_state['movie_ids']:
        if mid in new_user_ratings.index:
            new_user_ratings[mid] = 5  # Assuming maximum preference

    # Compute cosine similarity
    user_similarity = cosine_similarity([new_user_ratings], user_matrix)
    similar_users = user_similarity.argsort()[0][-3:]  # Top 3 similar users

    # Fetch and display recommendations
    recommended_ids = fetch_data(f"reco/{'/'.join(map(str, similar_users))}")
    recommended_movies = pd.DataFrame(recommended_ids, columns=['movieId', 'predicted_rating_im_confidence']).head(5)

    for mid in recommended_movies['movieId']:
        movie_details = fetch_data(f"title_from_id/{mid}")
        with st.expander(movie_details['title']):
            movie_info = requests.get(f"{TMDB_BASE_URL}{mid}?api_key={API_KEY}").json()
            st.image(f"https://image.tmdb.org/t/p/original{movie_info['poster_path']}")
            st.write(f"Overview: {movie_info['overview']}")

# Reset button
if st.button("Reset Selection"):
    st.session_state['selected_movies'] = []
    st.session_state['movie_ids'] = []

def fetch_data(endpoint):
    response = requests.get(BACKEND_URL + endpoint)
    if response.ok:
        return response.json()
    else:
        st.error("Failed to fetch data")
        return {}

