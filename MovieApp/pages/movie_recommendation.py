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
        st.error(f"Failed to fetch data from {endpoint}")
        return None

def get_recommendations(similar_users):
    """ Fetch recommendations based on similar user IDs """
    if not similar_users:
        return pd.DataFrame()
    user_ids = ",".join(map(str, similar_users))
    recommendations_json = fetch_data(f"recommendations/{user_ids}")
    if recommendations_json:
        return pd.read_json(recommendations_json)
    else:
        return pd.DataFrame()

# Streamlit page configuration
st.set_page_config(page_title="Movie Recommendations")
st.title("🎬 Movie Recommendations")

if 'selected_movies' not in st.session_state or not st.session_state['selected_movies']:
    st.write("No movies selected for recommendations. Please select movies first.")
else:
    st.write("You have selected the following movies:")
    for movie in st.session_state['selected_movies']:
        st.write(movie)

    selected_movie_ids = [fetch_data(f"movie_ids/{movie}") for movie in st.session_state['selected_movies']]
    st.write("Fetched Movie IDs:", selected_movie_ids)  # Debugging output

    if any(x is None for x in selected_movie_ids):
        st.error("Some movie IDs could not be fetched. Please check the movie titles.")
    else:
        ratings_data = fetch_data("ratings")
        if ratings_data is None:
            st.error("Failed to fetch ratings data.")
        else:
            ratings_df = pd.DataFrame(ratings_data, columns=['userId', 'movieId', 'rating'])
            if ratings_df.empty:
                st.error("Ratings data is empty.")
            else:
                st.write("Ratings DataFrame:", ratings_df.head())  # Debugging output
                user_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0)
                if user_matrix.empty or user_matrix.index.empty:
                    st.error("User matrix is empty.")
                else:
                    new_user_index = max(user_matrix.index) + 1
                    new_user_row = pd.DataFrame(0, index=[new_user_index], columns=user_matrix.columns)
                    for movie_id in selected_movie_ids:
                        if movie_id in new_user_row.columns:
                            new_user_row.loc[new_user_index, movie_id] = 5

                    similarity = cosine_similarity(new_user_row, user_matrix)
                    similar_users = similarity.argsort()[0][-3:]

                    recommendations_df = get_recommendations(similar_users)
                    if not recommendations_df.empty:
                        st.write("We recommend the following movies based on your preferences:")
                        for idx, row in recommendations_df.iterrows():
                            st.write(f"{row['movieId']} - {row['title']}")
                    else:
                        st.write("No recommendations found.")
