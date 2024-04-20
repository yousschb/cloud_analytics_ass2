import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Base URL for backend API calls
BASE_URL = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"

def fetch_data(endpoint):
    """Fetch data from backend API and handle errors."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None

# Initialize session state for selected movies and IDs
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

st.title("🎬 Movie Recommendations")

# Sidebar for movie selection and management
st.sidebar.title("Movie Selector")
search_term = st.sidebar.text_input("Search for movies:", "")
if search_term:
    search_results = fetch_data(f"elastic_search/{search_term}")
    if search_results:
        for movie in search_results:
            if st.sidebar.button(movie):
                if movie not in st.session_state['selected_movies']:
                    movie_data = fetch_data(f"movie_id_from_title/{movie}")
                    if movie_data and 'movieId' in movie_data:
                        st.session_state['selected_movies'].append(movie)
                        st.session_state['movie_ids'].append(movie_data['movieId'])
                        st.experimental_rerun()
                    else:
                        st.sidebar.error("Movie ID not found for the selected movie.")

# Display selected movies
if st.session_state['selected_movies']:
    st.sidebar.write("Selected Movies:")
    for movie in st.session_state['selected_movies']:
        st.sidebar.write(movie)

# Button to get recommendations
if st.sidebar.button("Get Recommendations"):
    if st.session_state['movie_ids']:
        # Fetch user ratings matrix
        ratings = fetch_data("ratings")
        if ratings:
            df = pd.DataFrame(ratings)
            user_matrix = df.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)

            # Create a new user profile based on selected movies
            new_user_profile = pd.DataFrame(0, index=['new_user'], columns=user_matrix.columns)
            for movie_id in st.session_state['movie_ids']:
                if movie_id in new_user_profile.columns:
                    new_user_profile.at['new_user', movie_id] = 1.0  # Max rating

            # Calculate cosine similarity and find top 3 similar users
            similarity = cosine_similarity(new_user_profile, user_matrix)
            similar_users = similarity.argsort()[0][-4:-1]  # Top 3 similar users
            recommendations = fetch_data(f"recommendations/{','.join(map(str, similar_users))}")

            if recommendations:
                st.header("We recommend these movies based on your preferences:")
                for rec in recommendations:
                    movie_details = fetch_data(f"title_from_movie_id/{rec['movieId']}")
                    if movie_details:
                        st.write(movie_details['title'])
            else:
                st.error("No recommendations found.")
    else:
        st.sidebar.warning("Please select at least one movie for recommendations.")

