import streamlit as st
import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity

# Assuming this function fetches your ratings data correctly
def fetch_ratings():
    # Replace this URL with the actual endpoint that returns ratings
    response = requests.get("https://cloud-analytics-ass20-gev3pcymxa-uc.a.run.app/ratings")
    if response.status_code == 200:
        return pd.read_json(response.text)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if something goes wrong

# Assuming selected_movie_ids is fetched or defined earlier in your code
selected_movie_ids = st.session_state.get('selected_movies', [])

# Load ratings data
ratings_df = fetch_ratings()
if ratings_df.empty:
    st.error("Failed to fetch ratings data or data is empty.")
else:
    user_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0)

    # Check if the user matrix is empty
    if user_matrix.empty or user_matrix.index.empty:
        st.error("User matrix is empty. Unable to proceed with recommendations.")
    else:
        # Assuming a new user profile needs to be created
        new_user_index = max(user_matrix.index) + 1
        new_user_row = pd.DataFrame(0, index=[new_user_index], columns=user_matrix.columns)
        
        # Setting high ratings for selected movies
        for movie_id in selected_movie_ids:
            if movie_id in new_user_row.columns:
                new_user_row.loc[new_user_index, movie_id] = 5  # Assuming 5 is a high rating

        # Calculate cosine similarity between the new user and existing users
        similarity = cosine_similarity(new_user_row, user_matrix)
        most_similar_users = similarity.argsort()[0][-3:]  # Get the top 3 similar users

        # Example logic to display something based on the most similar users
        if most_similar_users.size > 0:
            st.write("Most similar users IDs:", most_similar_users)
        else:
            st.error("No similar users found.")
