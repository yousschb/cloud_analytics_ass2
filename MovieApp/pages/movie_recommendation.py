import streamlit as st
import pandas as pd
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote

# Constants for TMDB API access
API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
MOVIE = "https://api.themoviedb.org/3/movie/"

# Initialize session state for storing user-selected movies
if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()
if "movie_id" not in st.session_state:
    st.session_state['movie_id'] = list()

# Configure page properties
st.set_page_config(page_title="Cinematic Insights")
st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>Cinematic Recommendations</h1>", unsafe_allow_html=True)

# Display the user's selected movies in the sidebar
if st.session_state["movie_title_selected"]:
    st.sidebar.header("Your Watchlist")
    for i in st.session_state["movie_title_selected"]:
        st.sidebar.write(f"🎬 {i}")
else:
    st.sidebar.write("No movies selected yet. Please add some to see recommendations.")

# Function to fetch data from the Flask backend server
def fetch_flask_data(url_path):
    """Fetch data from Flask backend using the given URL path."""
    url = "https://cloud-analytics-ass213-gev3pcymxa-uc.a.run.app" + url_path
    response = requests.get(url)
    return response.json()

# Function to retrieve the title of a movie by its ID
def retrieve_movie_title_by_id(id):
    """Retrieve the title of a movie by its ID from the TMDB database."""
    df = pd.DataFrame(fetch_flask_data(f"/title_from_movie_id/{id}"), columns=["title"])
    return df

# Function to present detailed information about a movie
def present_movie_details(movie_id):
    """Fetch and display detailed information for a specific movie ID from TMDB."""
    response = requests.get(MOVIE + str(movie_id) + API_KEY)
    data = response.json()
    st.write(data['tagline'])
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://image.tmdb.org/t/p/original/" + data['poster_path'], width=320)
    with col2:
        genres = ", ".join([genre['name'] for genre in data['genres']])
        st.write(f"Genres: {genres}")
        st.write(f"Overview: {data['overview']}")
        st.write(f"Language: {data['original_language']}")
        st.write(f"Release Date: {data['release_date']}")
        st.write(f"Vote Average: {data['vote_average']}")

# Processing movie selections for recommendations
if st.session_state['movie_title_selected']:
    # Fetch movie IDs based on selected titles
    for movie_title in st.session_state['movie_title_selected']:
        df = pd.DataFrame(fetch_flask_data(f"/movie_id_from_title/{movie_title}"), columns=["movieId"])
        for movie_id in df['movieId']:
            if movie_id not in st.session_state['movie_id']:
                st.session_state['movie_id'].append(movie_id)

    # Prepare a list of movie IDs chosen by the user
    new_user_movie_id_list = [id for id in st.session_state['movie_id']]

    # Load user ratings from the backend
    if 'ratings' not in st.session_state:
        ratings = pd.DataFrame(fetch_flask_data("/ratings"), columns=['userId', 'movieId', 'rating_im'])
        st.session_state['ratings'] = ratings

    # Create a matrix of user ratings
    user_matrix = st.session_state['ratings'].pivot(index='userId', columns='movieId', values='rating_im').fillna(0)

    # Generate a new user row for similarity comparison
    new_user_row = pd.DataFrame(0, index=[user_matrix.index[-1] + 1], columns=user_matrix.columns)
    new_user_row.loc[:, new_user_movie_id_list] = 1

    # Compute cosine similarity between the new user and all existing users
    similarity = cosine_similarity(new_user_row, user_matrix)
    most_similar_users = [index + 1 for index in similarity.argsort()[0][-5:][::-1]]

    # Fetch recommendations based on the most similar users
    recommendations = pd.DataFrame(fetch_flask_data(f"/recommendations/{','.join(map(str, most_similar_users))}"),
                                   columns=['userId', 'movieId', 'predicted_rating_im_confidence'])
    recommended_movies = recommendations[~recommendations['movieId'].isin(st.session_state['movie_id'])]
    top_movies = recommended_movies.drop_duplicates(subset=['movieId'], keep="first").head(8)

    # Show recommendations
    progress_text = "Compiling your personalized recommendations..."
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.05)
        my_bar.progress(percent_complete + 1)
    time.sleep(1)
    my_bar.empty()
    st.write("Based on your selections, we suggest the following movies:")

    # Display each recommended movie and allow details to be expanded on click
    for movie_id in top_movies['movieId']:
        if movie_id not in st.session_state['movie_title_selected']:
            tmdb_id = fetch_flask_data(f"/tmdb_id/{movie_id}")
            with st.expander(f"{retrieve_movie_title_by_id(movie_id)['title'][0]}"):
                present_movie_details(tmdb_id["tmdbId"]["0"])

# Interaction buttons for the user
if st.button("Clear Selection", on_click=lambda: st.session_state.pop("movie_title_selected", None)):
    st.switch_page('movie_selection.py')
