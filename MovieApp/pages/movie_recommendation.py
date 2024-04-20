import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Function to interact with the Flask backend
def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    try:
        # Try to return JSON if possible
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
        return {}  # Return an empty dict if there's an HTTP error
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")  # Problems parsing JSON
        return {}  # Return an empty dict if the JSON is invalid


# Initialize session state for selected movies and movie IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'selected_movie_ids' not in st.session_state:
    st.session_state['selected_movie_ids'] = []

# Fetch the user matrix (ratings data) from the backend for cosine similarity calculation
def fetch_user_matrix():
    ratings = fetch_data('/ratings')
    df = pd.DataFrame(ratings)
    return df.pivot(index='userId', columns='movieId', values='rating').fillna(0)

# Calculate cosine similarity and find the top 3 similar users
def find_similar_users(user_profile, user_matrix):
    similarity = cosine_similarity(user_profile, user_matrix)
    top_indices = similarity.argsort()[0][-4:-1]  # Exclude the last one because it's the user itself
    return user_matrix.index[top_indices].tolist()

# Generate movie recommendations using the backend
def generate_recommendations(similar_user_ids):
    ids = ','.join(map(str, similar_user_ids))
    recommendations = fetch_data(f'/recommendations/{ids}')
    return pd.DataFrame(recommendations)

# Convert movie IDs to titles
def convert_ids_to_titles(movie_ids):
    titles = []
    for mid in movie_ids:
        title = fetch_data(f'/title_from_movie_id/{mid}')
        if title:
            titles.append(title['title'][0])
    return titles

# Page for Recommendations
st.set_page_config(page_title="Movie Recommendations", layout='wide')
st.title("🎬 Movie Recommendations")

# Display recommendations if there are selected movies
if 'selected_movies' in st.session_state and st.session_state['selected_movies']:
    # Get movie IDs from titles
    movie_ids = [fetch_data(f"/movie_id_from_title/{movie}")['movieId'][0] for movie in st.session_state['selected_movies']]
    st.session_state['selected_movie_ids'] = movie_ids
    
    user_matrix = fetch_user_matrix()
    new_user_row = pd.DataFrame(0, index=['new_user'], columns=user_matrix.columns)
    for movie_id in movie_ids:
        if movie_id in new_user_row.columns:
            new_user_row.at['new_user', movie_id] = 1.0  # Assume max rating for selected movies

    similar_users = find_similar_users(new_user_row, user_matrix)
    recommendations_df = generate_recommendations(similar_users)
    
    recommended_movie_ids = recommendations_df['movieId'].tolist()
    recommended_titles = convert_ids_to_titles(recommended_movie_ids)
    
    st.write("We recommend the following movies based on your preferences:")
    for title in recommended_titles:
        st.write(title)
else:
    st.write("Please select some movies first.")

# Ensure that this entire setup is correctly retrieving data from the backend, and each function handles possible errors or missing data.
