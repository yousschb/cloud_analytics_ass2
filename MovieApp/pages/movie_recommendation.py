"""
import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote  # Import the quote function

def fetch_data(url_path):
    url = "https://cloud-analytics-ass203-gev3pcymxa-uc.a.run.app" + url_path
    response = requests.get(url)
    return response.json()

# Initialize session state keys with default values if they don't exist.
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []

if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = []  # Initialize as an empty list.

st.title("🎬 Movie Recommendations")

# Sidebar for movie selection and management
st.sidebar.title("Movie Selector")
search_term = st.sidebar.text_input("Search for movies:", "")
if search_term:
    st.subheader("Select from the following results:")
    search_results = fetch_data(f"elastic_search/{search_term}")
    for movie in search_results:
        if st.button(movie, key=f"btn_{movie}"):
            if movie not in st.session_state['selected_movies']:
                st.session_state['selected_movies'].append(movie)
                st.experimental_rerun()

# Display selected movies
selected_movies = st.session_state.get('selected_movies', [])  # Use .get with default empty list
if selected_movies:
    st.sidebar.header("Selected Movies")
    for movie in selected_movies:
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            selected_movies.remove(movie)
            st.experimental_rerun()


# Button to get recommendations
if st.sidebar.button("Get Recommendations"):
    if selected_movies:
        # Fetch movie IDs for selected movies
        movie_ids = []
        for movie in selected_movies:
            encoded_movie_title = quote(movie)  # URL encode the movie title
            movie_data = fetch_data(f"movie_id_from_title/{encoded_movie_title}")
            if movie_data and 'movieId' in movie_data:
                movie_ids.append(movie_data['movieId'])
"""

import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote  # Import the quote function

def fetch_data(url_path):
    url = "https://cloud-analytics-ass203-gev3pcymxa-uc.a.run.app" + url_path
    response = requests.get(url)
    return response.json()

def get_movie_details(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key=your_api_key"
    response = requests.get(url)
    return response.json()

# Initialize session state keys with default values if they don't exist.
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []
if 'movie_ids' not in st.session_state:
    st.session_state['movie_ids'] = []

st.title("🎬 Movie Recommendations")

# Sidebar for movie selection and management
st.sidebar.title("Movie Selector")
search_term = st.sidebar.text_input("Search for movies:", "")
if search_term:
    st.subheader("Select from the following results:")
    search_results = fetch_data(f"elastic_search/{search_term}")
    for movie in search_results['results']:  # Assume search_results contains results
        movie_title = movie['title']
        tmdb_id = movie['id']  # Assume each result has an 'id' that is the TMDB ID
        if st.sidebar.button(movie_title, key=f"btn_{tmdb_id}"):
            if tmdb_id not in st.session_state['movie_ids']:
                st.session_state['movie_ids'].append(tmdb_id)
                st.experimental_rerun()

# Display selected movies
if st.session_state['movie_ids']:
    st.sidebar.header("Selected Movies")
    for tmdb_id in st.session_state['movie_ids']:
        movie_details = get_movie_details(tmdb_id)
        if movie_details:
            col1, col2 = st.columns([1, 3])  # Dividing the page into two columns
            # Display movie poster in the first column
            if movie_details.get('poster_path'):
                col1.image(f"https://image.tmdb.org/t/p/w500/{movie_details['poster_path']}")
            # Display movie information in the second column
            col2.write(f"**Title:** {movie_details['title']}")
            col2.write(f"**Overview:** {movie_details['overview']}")
            col2.write(f"**Release Date:** {movie_details['release_date']}")
            col2.write(f"**Language:** {movie_details['original_language']}")
            col2.write(f"**Genres:** {', '.join(genre['name'] for genre in movie_details['genres'])}")

        # Remove button for each movie
        if st.sidebar.button(f"Remove {movie_details['title']}", key=f"remove_{tmdb_id}"):
            st.session_state['movie_ids'].remove(tmdb_id)
            st.experimental_rerun()

# This can be used in your recommendation fetching code
if st.sidebar.button("Get Recommendations"):
    if st.session_state['selected_movies']:
        movie_ids = []
        for movie in st.session_state['selected_movies']:
            encoded_movie_title = quote(movie)  # Properly encode the movie title to handle special characters
            movie_data = fetch_data(f"movie_id_from_title/{encoded_movie_title}")
            if movie_data and 'movieId' in movie_data:
                movie_ids.append(movie_data['movieId'])
            else:
                st.error(f"Failed to fetch ID for {movie}. Ensure the title is correct and try again.")

        if movie_ids:
            # Fetch user ratings matrix
            ratings = fetch_data("ratings")
            if ratings:
                df = pd.DataFrame(ratings)
                user_matrix = df.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)
            else:
                st.error("Failed to fetch ratings data. Check the backend service for issues.")

                new_user_profile = pd.DataFrame(0, index=['new_user'], columns=user_matrix.columns)
                for movie_id in movie_ids:
                    if movie_id in new_user_profile.columns:
                        new_user_profile.at['new_user', movie_id] = 1.0  # Assume max rating
                
                similarity = cosine_similarity(new_user_profile, user_matrix)
                similar_users = similarity.argsort()[0][-4:-1]  # Top 3 similar users
                recommendations = fetch_data(f"recommendations/{','.join(map(str, similar_users))}")

                if recommendations:
                    st.header("Recommended Movies:")
                    for rec in recommendations:
                        movie_details = fetch_data(f"title_from_movie_id/{rec['movieId']}")
                        if movie_details:
                            st.write(movie_details['title'])
                else:
                    st.error("No recommendations found. There might be an issue with the recommendation engine.")

                else:
                    st.error("No recommendations found.")
            else:
                st.error("Failed to fetch ratings data.")
        else:
            st.sidebar.error("Failed to fetch movie IDs for selected movies.")
    else:
        st.sidebar.warning("Please select at least one movie for recommendations.")
