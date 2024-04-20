import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    full_url = f"{base_url}/{endpoint}"
    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Will raise an exception for HTTP errors
        return response.json()  # This will raise an exception if response is not JSON
    except requests.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")  # Provide feedback on HTTP errors
    except requests.RequestException as err:
        st.error(f"Request error occurred: {err}")  # General request exceptions (network issues, etc.)
    except ValueError as json_err:
        st.error(f"JSON decoding error: {json_err}")  # JSON decoding issues
    return None  # Return None or an empty dict if you want to handle missing data elsewhere
"""
# Function to interact with the Flask backend
def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass2-gev3pcymxa-uc.a.run.app"
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    response = requests.get(full_url)
    return response.json()
"""
        
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
            movie_data = fetch_data(f"movie_id_from_title/{movie.replace(' ', '%20')}")
            if movie_data and 'movieId' in movie_data:
                movie_ids.append(movie_data['movieId'])

        if movie_ids:
            # Fetch user ratings matrix
            ratings = fetch_data("ratings")
            if ratings:
                df = pd.DataFrame(ratings)
                user_matrix = df.pivot(index='userId', columns='movieId', values='rating_im').fillna(0)

                # Create new user profile
                new_user_profile = pd.DataFrame(0, index=['new_user'], columns=user_matrix.columns)
                for movie_id in movie_ids:
                    if movie_id in new_user_profile.columns:
                        new_user_profile.at['new_user', movie_id] = 1.0  # Assume max rating

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
                st.error("Failed to fetch ratings data.")
        else:
            st.sidebar.error("Failed to fetch movie IDs for selected movies.")
    else:
        st.sidebar.warning("Please select at least one movie for recommendations.")
