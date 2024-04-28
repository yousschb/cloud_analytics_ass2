import streamlit as st
import pandas as pd
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote

# Set page configuration
st.set_page_config(page_title="Movie Reco")

# Page Header
st.markdown("<h1 style='text-align: center;'>Recommendations</h1>", unsafe_allow_html=True)

# Check session state for selected and movie IDs
if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

if "movie_id" not in st.session_state:
    st.session_state['movie_id'] = list()

# Function to fetch data from Flask backend
def fetch_flask_data(url_path):
    base_url = "https://cloud-analytics-ass213-gev3pcymxa-uc.a.run.app"
    url = f"{base_url}{url_path if url_path.startswith('/') else '/' + url_path}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Invalid JSON response")
            return None
    else:
        st.error(f"Failed to fetch data: HTTP status code {response.status_code}")
        return None

# Display selected movies in sidebar
if st.session_state["movie_title_selected"]:
    st.sidebar.write("You have selected these movies:")
    for movie in st.session_state["movie_title_selected"]:
        st.sidebar.write(movie)
else:
    st.write("You have not selected any movies yet.")

# Fetch movie IDs from titles
for title in st.session_state['movie_title_selected']:
    df = pd.DataFrame(fetch_flask_data(f"/movie_id_from_title/{title}"), columns=["movieId"])
    for movie_id in df['movieId']:
        if movie_id not in st.session_state['movie_id']:
            st.session_state['movie_id'].append(movie_id)

# Create user vector and calculate similarity
if st.session_state['movie_id']:
    new_user_movie_id_list = [movie_id for movie_id in st.session_state['movie_id']]
    if 'ratings' not in st.session_state:
        ratings = pd.DataFrame(fetch_flask_data("/ratings"), columns=['userId', 'movieId', 'rating_im'])
        st.session_state['ratings'] = ratings

    user_matrix = st.session_state['ratings'].pivot(index='userId', columns='movieId', values='rating_im').fillna(0)
    new_user_row = pd.DataFrame(0, index=[user_matrix.index[-1] + 1], columns=user_matrix.columns)
    new_user_row.loc[:, new_user_movie_id_list] = 1
    similarity = cosine_similarity(new_user_row, user_matrix)

    # Fetch recommendations for similar users
    most_similar_users = [index + 1 for index in similarity.argsort()[0][-5:][::-1]]
    recommendations = pd.DataFrame(fetch_flask_data(f"/recommendations/{','.join(map(str, most_similar_users))}"),
                                   columns=['userId', 'movieId', 'predicted_rating_im_confidence'])
    recommendations_filtered = recommendations[~recommendations['movieId'].isin(st.session_state['movie_id'])]
    top_recommendations = recommendations_filtered.drop_duplicates(subset=['movieId'], keep="first").head(8)

    # Display recommended movies
    st.write("Based on the movies you selected, we recommend you to watch these movies:")
    for movie_id in top_recommendations['movieId']:
        if movie_id not in st.session_state['movie_title_selected']:
            tmdb_id = fetch_flask_data(f"/tmdb_id/{movie_id}")
            with st.expander(f"{get_title_from_id(movie_id)['title'][0]}"):
                display_info(tmdb_id["tmdbId"]["0"])

# Buttons for additional actions
if st.button("Add to Selection"):
    st.switch_page('movie_selection.py')

if st.button("Clear Selection", on_click=lambda: st.session_state.pop("movie_title_selected", None)):
    st.switch_page('movie_selection.py')
