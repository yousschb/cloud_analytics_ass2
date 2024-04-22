import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import time
from urllib.parse import quote

# Function to interact with the Flask backend
def get_data_from_flask(url_path):
    url = "https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app/" + url_path
    response = requests.get(url)
    return response.json()

# Initialize session state for movie selection
if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

# Initialize session state for movie IDs
if "movie_id" not in st.session_state:
    st.session_state['movie_id'] = list()

# Set Streamlit page configuration
st.set_page_config(page_title="Movie Recommendation")
st.markdown("<h1 style='text-align: center;'>Movie Recommendation</h1>", unsafe_allow_html=True)
st.title("Movie Selection")

# Movie search and selection functionality
movies_query = st.text_input("Search for a movie title here")
if movies_query:
    st.write("Results  (Click To Select):")
    autocomplete_results = get_data_from_flask(f"elastic_search/{quote(movies_query)}")
    if autocomplete_results:
        for i in autocomplete_results:
            button_key = f"select_{i}"
            if st.button(f"{i}", key=button_key, type="primary"):
                if i not in st.session_state['movie_title_selected']:
                    st.session_state['movie_title_selected'].append(i)

# Display selected movies in sidebar and allow removal
if st.session_state["movie_title_selected"]:
    st.sidebar.write("You have selected these movies (Click to remove):")
    for i in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f"{i}", key=f"remove_{i}", type="secondary"):
            st.session_state["movie_title_selected"].remove(i)
            st.experimental_rerun()

# Button to get recommendations
if st.sidebar.button("Get Recommendations", type="primary"):
    # Processing to generate recommendations
    for movie_title in st.session_state['movie_title_selected']:
        df = pd.DataFrame(get_data_from_flask("movie_id_from_title/" + quote(movie_title)), columns=["movieId"])
        for movie_id in df['movieId']:
            if movie_id not in st.session_state['movie_id']:
                st.session_state['movie_id'].append(movie_id)

    # Generate recommendations based on selected movies
    if 'ratings' not in st.session_state:
        ratings = pd.DataFrame(get_data_from_flask("ratings"), 
                                columns=['userId', 'movieId', 'rating_im'])
        st.session_state['ratings'] = ratings

    user_matrix = st.session_state['ratings'].pivot_table(index='userId', 
                                                          columns='movieId', values='rating_im')
    user_matrix = user_matrix.fillna(0)
    
    new_user_row = pd.DataFrame(0, index=[user_matrix.index[-1] + 1], columns=user_matrix.columns)
    new_user_row[st.session_state['movie_id']] = 1
    similarity = cosine_similarity(new_user_row, user_matrix)
    
    most_5_similar_users = [index + 1 for index in similarity.argsort()[0][-5:][::-1]]
    df = pd.DataFrame(get_data_from_flask("recommendations/" + ",".join(map(str, most_5_similar_users))),
                      columns=['userId', 'movieId', 'predicted_rating_im_confidence'])
    
    df_filtered = df[~df['movieId'].isin(st.session_state['movie_id'])]
    df2 = df_filtered.drop_duplicates(subset=['movieId'], keep="first")
    five_movies = df2.head(8)

    st.write("Based on the movies you selected, we recommend you to watch these movies:")
    for movie_id in five_movies['movieId']:
        tmdb_id = get_data_from_flask("tmdb_id/" + str(movie_id))
        movie_details = get_data_from_flask("title_from_movie_id/" + str(movie_id))
        with st.expander(f"{movie_details['title']['0']}"):
            display_info(tmdb_id["tmdbId"]["0"])

def display_info(tmdb_id):
    API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
    MOVIE = "https://api.themoviedb.org/3/movie/"
    response = requests.get(MOVIE + str(tmdb_id) + API_KEY)
    data = response.json()
    st.write(data['tagline'])
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://image.tmdb.org/t/p/original/" + data['poster_path'], width=320)
    with col2:
        genres = ""
        for genre in data['genres']:
            genres += genre['name'] + ", "
        st.write("Genres: " + genres[:-2])
        st.write(f"Overview: {data['overview']}")
        st.write(f"Language: {data['original_language']}")
        st.write(f"Release Date: {data['release_date']}")
        st.write(f"Vote Average: {data['vote_average']}")

# Clear Selection Button
if st.button("Clear Selection", on_click=lambda: st.session_state.pop("movie_title_selected", None)):
    st.experimental_rerun()

# Styling for buttons (remains unchanged as per your request)
st.markdown(
    """
    <style>
    button[kind="primary"] {
        padding: 10px 25px;
        font-family: "Roboto", sans-serif;
        font-weight: 500;
        background: transparent;
        outline: none !important;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        display: inline-block;
        border: 2px solid rgb(220, 220, 220);
        z-index: 1;
        color: grey;
    }
    button[kind="primary"]:hover {
        text-decoration: none;
        outline: none !important;
        color: black !important;
    }
    button[kind="primary"]:after {
        position: absolute;
        content: "";
        width: 0;
        outline: none !important;
        height: 100%;
        top: 0;
        left: 0;
        direction: rtl;
        z-index: -1;
        background: rgb(255, 255, 255);
        transition: all 0.5s ease;
    }
    button[kind="primary"]:hover:after {
        left: auto;
        right: 0;
        outline: none !important;
        width: 100%;
    }
    button[kind="primary"]:hover span {
        background: black;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
