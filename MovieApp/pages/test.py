import streamlit as st
import requests

def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass203-gev3pcymxa-uc.a.run.app"
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    full_url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()  # This will raise an exception for HTTP errors.
        # Check if the content type is JSON before decoding
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else:
            st.error("Invalid response format received. Expected JSON.")
            return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e.response.status_code} - {e.response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None
    except ValueError:
        st.error("Failed to decode JSON.")
        return None

def get_movie_id(movie_title):
    # Replace spaces with URL encoded '%20' for the API call
    movie_id_response = fetch_data(f"movie_id_from_title/{movie_title.replace(' ', '%20')}")
    if movie_id_response:
        # Assuming the response format is {'movieId': {'0': actual_id}}
        return movie_id_response.get('movieId', {}).get('0')
    return None

def get_poster_url(movie_id):
    if movie_id:
        poster_response = fetch_data(f"tmdb_id/{movie_id}")
        if poster_response:
            # Assuming poster_response directly gives you the URL or the path
            return poster_response
    return None

# Initialize session state for selected movies
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []

# Configure Streamlit page properties
st.set_page_config(page_title="Movie Selector", layout='wide')
st.title("🎬 Movie Selector Interface")

# Movie search and selection
search_term = st.text_input("Type to search for movies:", placeholder="Start typing...")
if search_term:
    search_results = fetch_data(f"elastic_search/{search_term}")
    if search_results:
        cols = st.columns(len(search_results))  # Adjust based on number of results
        for idx, movie in enumerate(search_results):
            with cols[idx]:
                movie_id = get_movie_id(movie)
                poster_url = get_poster_url(movie_id)
                if poster_url:
                    st.image(poster_url, caption=movie, width=150)  # Adjust width as necessary
                if st.button("Select", key=f"select_{movie}"):
                    if movie not in st.session_state['selected_movies']:
                        st.session_state['selected_movies'].append(movie)
                        st.experimental_rerun()
                        
# Sidebar for managing selected movies
if st.session_state['selected_movies']:
    st.sidebar.header("Selected Movies")
    for movie in st.session_state['selected_movies']:
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            st.session_state['selected_movies'].remove(movie)
            st.experimental_rerun()
    if st.sidebar.button("Get Recommendations"):
        # Assuming you have a page or method to display recommendations
        st.switch_page('pages/movie_recommendation.py')
