import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests

API_KEY = "81eb26f048683218d8f96f9fab8e8c52"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"
BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"

def fetch_data(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.ok:
        return response.json()
    st.error("Failed to fetch data from the backend.")
    return []

st.set_page_config(page_title="Movie Recommendations", layout='wide')
st.title("🎥 Movie Recommendations")

# Display selected movies
if 'selected_movies' in st.session_state and st.session_state['selected_movies']:
    st.sidebar.write("Selected Movies:")
    for movie in st.session_state['selected_movies']:
        st.sidebar.write(movie)
else:
    st.sidebar.write("You have not selected any movies yet.")

# Generate and display recommendations
if st.button("Get Recommendations"):
    if 'movie_ids' in st.session_state and st.session_state['movie_ids']:
        ratings = fetch_data("rating_df")
        user_ratings = pd.DataFrame(ratings, columns=['userId', 'movieId', 'rating_im'])
        user_matrix = user_ratings.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)

        user_prefs = pd.Series(0, index=user_matrix.columns)
        for movie_id in st.session_state['movie_ids']:
            if movie_id in user_prefs.index:
                user_prefs[movie_id] = 5

        similarity = cosine_similarity([user_prefs], user_matrix)
        top_users = similarity.argsort()[0][-3:]  # get indices of top 3 similar users

        reco_data = fetch_data(f"reco/{'/'.join(map(str, top_users))}")
        recommended_movies = pd.DataFrame(reco_data, columns=['movieId', 'predicted_rating_im_confidence']).head(5)

        st.write("We recommend the following movies based on your selections:")
        for movie_id in recommended_movies['movieId']:
            details = fetch_data(f"title_from_id/{movie_id}")
            if details:
                movie_info = requests.get(f"{TMDB_BASE_URL}{movie_id}{API_KEY}").json()
                with st.expander(details['title']):
                    st.image(f"{TMDB_BASE_URL}original{movie_info['poster_path']}", width=320)
                    st.write(f"Overview: {movie_info['overview']}")
    else:
        st.error("Please select some movies first.")

# Reset selection
if st.button("Reset Selection"):
    st.session_state['selected_movies'] = []
    st.session_state['movie_ids'] = []
