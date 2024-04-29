import streamlit as st
import pandas as pd
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote

# Constants for TMDB
API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
MOVIE = "https://api.themoviedb.org/3/movie/"

# Initialize session state
if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()
if "movie_id" not in st.session_state:
    st.session_state['movie_id'] = list()

# Page setup
st.set_page_config(page_title="Cinematic Insights")
st.markdown("<h1 style='text-align: center; color: #4A4A4A;'>Cinematic Recommendations</h1>", unsafe_allow_html=True)

# Sidebar: Display selected movies
if st.session_state["movie_title_selected"]:
    st.sidebar.header("Your Watchlist")
    for i in st.session_state["movie_title_selected"]:
        st.sidebar.write(f"🎬 {i}")
else:
    st.sidebar.write("No movies selected yet. Please add some to see recommendations.")

# Fetch data from Flask backend
def fetch_flask_data(url_path):
    """ Fetch data from the Flask backend """
    url = "https://cloud-analytics-ass213-gev3pcymxa-uc.a.run.app" + url_path
    response = requests.get(url)
    return response.json()

# Present movie information
def retrieve_movie_title_by_id(id):
    """ Retrieve and display the movie title by ID """
    df = pd.DataFrame(fetch_flask_data(f"/title_from_movie_id/{id}"), columns=["title"])
    return df

def present_movie_details(movie_id):
    """Display information for a specific movie ID."""
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

# Process movie selections for recommendations
if st.session_state['movie_title_selected']:
    for movie_title in st.session_state['movie_title_selected']:
        df = pd.DataFrame(fetch_flask_data(f"/movie_id_from_title/{movie_title}"), columns=["movieId"])
        for movie_id in df['movieId']:
            if movie_id not in st.session_state['movie_id']:
                st.session_state['movie_id'].append(movie_id)

    new_user_movie_id_list = [id for id in st.session_state['movie_id']]

    if 'ratings' not in st.session_state:
        ratings = pd.DataFrame(fetch_flask_data("/ratings"), columns=['userId', 'movieId', 'rating_im'])
        st.session_state['ratings'] = ratings

    user_matrix = st.session_state['ratings'].pivot(index='userId', columns='movieId', values='rating_im').fillna(0)
    new_user_row = pd.DataFrame(0, index=[user_matrix.index[-1] + 1], columns=user_matrix.columns)
    new_user_row.loc[:, new_user_movie_id_list] = 1
    similarity = cosine_similarity(new_user_row, user_matrix)

    most_similar_users = [index + 1 for index in similarity.argsort()[0][-5:][::-1]]
    recommendations = pd.DataFrame(fetch_flask_data(f"/recommendations/{','.join(map(str, most_similar_users))}"),
                                   columns=['userId', 'movieId', 'predicted_rating_im_confidence'])
    recommended_movies = recommendations[~recommendations['movieId'].isin(st.session_state['movie_id'])]
    top_movies = recommended_movies.drop_duplicates(subset=['movieId'], keep="first").head(8)

    # Show progress and recommendations
    progress_text = "Compiling your personalized recommendations..."
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.05)
        my_bar.progress(percent_complete + 1)
    time.sleep(1)
    my_bar.empty()
    st.write("Based on your selections, we suggest the following movies:")

    for movie_id in top_movies['movieId']:
        if movie_id not in st.session_state['movie_title_selected']:
            tmdb_id = fetch_flask_data(f"/tmdb_id/{movie_id}")
            with st.expander(f"{retrieve_movie_title_by_id(movie_id)['title'][0]}"):
                present_movie_details(tmdb_id["tmdbId"]["0"])

# Interaction buttons
if st.button("Add to Selection"):
    st.switch_page('movie_selection.py')

if st.button("Clear Selection", on_click=lambda: st.session_state.pop("movie_title_selected", None)):
    st.switch_page('movie_selection.py')
