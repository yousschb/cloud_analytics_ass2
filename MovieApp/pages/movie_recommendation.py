import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Constants
BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"

def fetch_data(endpoint):
    """ Fetch data from the Flask backend """
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()  # Will raise HTTPError for bad requests (400 or 500)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None

def get_user_matrix_and_profile(selected_movie_ids):
    ratings_json = fetch_data("ratings")
    if ratings_json:
        ratings_df = pd.DataFrame(ratings_json)
        user_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        new_user_row = pd.DataFrame(0, index=['new_user'], columns=user_matrix.columns)
        # Ensure only valid movie IDs are used
        valid_movie_ids = set(user_matrix.columns) & set(selected_movie_ids)
        for movie_id in valid_movie_ids:
            new_user_row.at['new_user', movie_id] = 1.0
        return user_matrix, new_user_row
    return None, None

def get_recommendations(user_matrix, new_user_profile):
    similarity = cosine_similarity(new_user_profile, user_matrix)
    top_indices = similarity.argsort()[0][-4:-1]  # Top 3 similar users, excluding the last one (new user itself)
    if top_indices.size > 0:
        user_ids = user_matrix.index[top_indices].tolist()
        recommendations_json = fetch_data(f"recommendations/{','.join(map(str, user_ids))}")
        if recommendations_json:
            return pd.DataFrame(recommendations_json)
    return pd.DataFrame()

# Streamlit page configuration
st.set_page_config(page_title="Movie Recommendations")
st.title("🎬 Movie Recommendations")

# Assuming the movie IDs are stored in the session state
if not st.session_state.get('selected_movie_ids', []):
    st.write("No movies selected for recommendations. Please select movies first.")
else:
    user_matrix, new_user_profile = get_user_matrix_and_profile(st.session_state['selected_movie_ids'])
    if user_matrix is not None and not new_user_profile.empty:
        recommendations_df = get_recommendations(user_matrix, new_user_profile)
        if not recommendations_df.empty:
            st.write("We recommend the following movies based on your preferences:")
            for idx, row in recommendations_df.iterrows():
                st.write(f"{row['movieId']} - {row['title']}")
        else:
            st.write("No recommendations found.")
    else:
        st.error("Failed to fetch ratings data or construct user profile.")
