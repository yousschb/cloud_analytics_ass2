import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests
import time
from urllib.parse import quote



if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

if "movie_id" not in st.session_state:
    st.session_state['movie_id'] = list()

"""
def get_data_from_flask(url_path):
    base_url = "https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app"
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    url = base_url + url_path
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
"""

def get_data_from_flask(title):
    base_url = "https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app/"
    # Encode le titre pour l'usage dans l'URL
    encoded_title = quote(title)
    url_path = f"/movie_id_from_title/{encoded_title}"
    url = base_url + url_path
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



def get_title_from_id(id):
    df = pd.DataFrame(get_data_from_flask("title_from_movie_id/" + str(id)), columns = ["title"])
    return df


def display_info(movie_id):
    if movie_id:
        response = requests.get(MOVIE + str(movie_id) + API_KEY)
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
    



st.set_page_config(page_title="Movie Reco")
st.markdown("<h1 style='text-align: center;'>Recommendations</h1>", unsafe_allow_html=True)

# display selected movies in sidebar    
if st.session_state["movie_title_selected"]:
    st.sidebar.write("You have selected these movies :")
    for i in st.session_state["movie_title_selected"]:
        st.sidebar.write(i)
else:
    st.write("You have not selected any movies yet.")



if st.session_state['movie_title_selected']:
    for movie_title in st.session_state['movie_title_selected']:
        df = pd.DataFrame(get_data_from_flask("movie_id_from_title/" + movie_title), columns = ["movieId"])
        for movie_id in df['movieId']:
            if movie_id not in st.session_state['movie_id']:
                st.session_state['movie_id'].append(movie_id)


# Creation of new user :
    new_user_movie_id_list = list()

    if st.session_state['movie_id']:
        for i in st.session_state['movie_id']:
            new_user_movie_id_list.append(i)



# rating df
    if 'ratings' not in st.session_state:
        ratings = pd.DataFrame(get_data_from_flask("ratings"), 
                                columns=['userId', 'movieId', 'rating_im'])
        st.session_state['ratings'] = ratings

    user_matrix = st.session_state['ratings'].pivot_table(index = 'userId', 
                                                            columns = 'movieId', values = 'rating_im')
    user_matrix = user_matrix.fillna(0)
    #  (610, 9724)

    new_user_row = pd.DataFrame(0, index=[user_matrix.index[-1] + 1], columns=user_matrix.columns)
    new_user_row[new_user_movie_id_list] = 1
    similarity = cosine_similarity(new_user_row, user_matrix)

# Most 3 Similar Users
    most_5_similar_users = [index + 1 for index in similarity.argsort()[0][-5:][::-1]]

# Recommendations
    df = pd.DataFrame(get_data_from_flask("recommendations/" + str(most_5_similar_users[0]) + "," + 
                        str(most_5_similar_users[1]) + "," + str(most_5_similar_users[2]) + 
                        "," + str(most_5_similar_users[3]) + "," + str(most_5_similar_users[4])), 
                        columns = ['userId', 'movieId', 'predicted_rating_im_confidence'])
    
    df_filtered = df[~df['movieId'].isin(st.session_state['movie_id'])]
    df2 = df_filtered.drop_duplicates(subset=['movieId'], keep="first")
    five_movies = df2.head(8)

    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.05)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    st.write("Based on the movies you selected, we recommend you to watch these movies :")


#  DISPLAY INFO OF RECOMMENDED MOVIES

    API_KEY = "?api_key=c1cf246019092e64d25ae5e3f25a3933"
    MOVIE = "https://api.themoviedb.org/3/movie/"

    for movie_id in five_movies['movieId']:
        if movie_id not in st.session_state['movie_title_selected']:
            tmdb_id = get_data_from_flask("tmdb_id/" + str(movie_id))
            with st.expander(f"{get_title_from_id(movie_id)['title'][0]}"):
                display_info(tmdb_id["tmdbId"]["0"])



# Add to selection
if st.button("Add to Selection"):
    st.switch_page('test.py')

# Clear Selection
if st.button("Clear Selection", on_click=lambda: st.session_state.pop("movie_title_selected", None)):
    st.switch_page('test.py')
