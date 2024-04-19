import streamlit as st
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

# Constants
BASE_URL = "https://cloud-analytics-caa2-gev3pcymxa-uc.a.run.app"

def fetch_data(endpoint):
    """ Fetch data from the Flask backend """
    response = requests.get(f"{BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_recommendations(similar_users):
    """ Fetch recommendations based on similar user IDs """
    user_ids = ",".join(map(str, similar_users))
    recommendations_json = fetch_data(f"recommendations/{user_ids}")
    if recommendations_json:
        return pd.read_json(recommendations_json)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no recommendations

# Streamlit page configuration
st.set_page_config(page_title="Movie Recommendations")
st.title("🎬 Movie Recommendations")

# Check if there are selected movies in session state
if 'selected_movies' not in st.session_state or not st.session_state['selected_movies']:
    st.write("No movies selected for recommendations. Please select movies first.")
else:
    # Display selected movies
    st.write("You have selected the following movies:")
    for movie in st.session_state['selected_movies']:
        st.write(movie)

    # Assuming each movie title maps to a unique movieId as a simplification
    selected_movie_ids = [fetch_data(f"movie_ids/{movie}") for movie in st.session_state['selected_movies']]

    # Fetch ratings data and construct user matrix
    ratings_df = pd.DataFrame(fetch_data("ratings"), columns=['userId', 'movieId', 'rating'])
    user_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0)

    # Create a new user profile based on selected movies
    new_user_row = pd.DataFrame(0, index=[max(user_matrix.index) + 1], columns=user_matrix.columns)
    for movie_id in selected_movie_ids:
        new_user_row.loc[:, movie_id] = 5  # Assuming 5 is a high rating

    # Calculate cosine similarity between the new user and existing users
    similarity = cosine_similarity(new_user_row, user_matrix)
    similar_users = similarity.argsort()[0][-3:]  # Top 3 similar users

    # Fetch recommendations for similar users
    recommendations_df = get_recommendations(similar_users)
    if not recommendations_df.empty:
        st.write("We recommend the following movies based on your preferences:")
        for idx, row in recommendations_df.iterrows():
            st.write(f"{row['movieId']} - {row['title']}")
    else:
        st.write("No recommendations found.")
