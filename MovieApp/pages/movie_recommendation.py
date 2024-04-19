import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests
import time

# Constants
BACKEND_URL = "https://backenda2-mjz535d2kq-oa.a.run.app/"
API_KEY = "?api_key=81eb26f048683218d8f96f9fab8e8c52"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"

# Initialize session state
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

def get_data_from_flask(endpoint):
    response = requests.get(BACKEND_URL + endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from backend")
        return None

def get_movie_details(movie_id):
    response = requests.get(f"{TMDB_BASE_URL}{movie_id}{API_KEY}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch movie details")
        return None

def fetch_recommendations(similar_users):
    # Construct the endpoint URL to fetch recommendations for similar users
    users_str = "/".join(map(str, similar_users))
    return get_data_from_flask(f"reco/{users_str}")

st.title("Movie Recommendations")
st.markdown("<h2 style='text-align: center;'>Based on your movie selections, here are some recommendations:</h2>", unsafe_allow_html=True)

# If movies have been selected previously
if st.session_state['movie_ids']:
    # Fetch recommendations based on similar users
    user_ratings = pd.DataFrame(get_data_from_flask("rating_df"), columns=['userId', 'movieId', 'rating_im'])
    user_matrix = user_ratings.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)
    
    # Creating a new user row based on selected movies
    new_user_row = pd.Series(0, index=user_matrix.columns)
    for movie_id in st.session_state['movie_ids']:
        if movie_id in new_user_row.index:
            new_user_row[movie_id] = 5  # Assuming maximum interest
    
    # Calculating cosine similarity
    similarity = cosine_similarity([new_user_row], user_matrix)
    top_users = similarity.argsort()[0][-3:]  # Get top 3 similar users
    
    recommendations = fetch_recommendations(top_users)
    recommended_movies = pd.DataFrame(recommendations, columns=['movieId', 'predicted_rating_im_confidence']).sort_values(by='predicted_rating_im_confidence', ascending=False).head(5)
    
    for idx, row in recommended_movies.iterrows():
        movie_details = get_movie_details(row['movieId'])
        if movie_details:
            col1, col2 = st.columns(2)
            with col1:
                st.image(movie_details['poster_path'], width=320)
            with col2:
                st.write(f"**{movie_details['title']}**")
                st.write(f"Overview: {movie_details['overview']}")
                st.write(f"Genres: {', '.join([genre['name'] for genre in movie_details['genres']])}")
                st.write(f"Release Date: {movie_details['release_date']}")
                st.write(f"Rating: {movie_details['vote_average']}/10")
else:
    st.write("No movies selected for recommendations. Please go back and select some movies first.")
