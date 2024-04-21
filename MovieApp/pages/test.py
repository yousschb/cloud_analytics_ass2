import streamlit as st
import requests

# Define a function to fetch data from the Flask backend
def fetch_data(endpoint):
    base_url = "https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app"
    url = f"{base_url}/{endpoint}"
    response = requests.get(url)
    return response.json()

# Initialize session state for managing selected movies
if 'selected_movies' not in st.session_state:
    st.session_state['selected_movies'] = []

# Set page configuration and title
st.set_page_config(page_title="Movie Recommendation System", layout="wide")
st.title("🎬 Movie Recommendation System")

# Movie search and selection
search_query = st.text_input("Search for a movie title here:")
if search_query:
    results = fetch_data(f"elastic_search/{search_query}")
    if results:
        st.subheader("Select from the following results:")
        for movie in results:
            if st.button(movie, key=f"select_{movie}"):
                if movie not in st.session_state['selected_movies']:
                    st.session_state['selected_movies'].append(movie)

# Sidebar for managing selected movies
if st.session_state['selected_movies']:
    st.sidebar.header("Selected Movies:")
    for movie in st.session_state['selected_movies']:
        if st.sidebar.button(f"Remove {movie}", key=f"remove_{movie}"):
            st.session_state['selected_movies'].remove(movie)

    # Button to get recommendations
    if st.sidebar.button("Get Recommendations"):
        # Create a string of selected movie IDs for the API call
        selected_movie_ids = ','.join([str(fetch_data(f"movie_id_from_title/{movie}")['movieId']) for movie in st.session_state['selected_movies']])
        recommendations = fetch_data(f"recommendations/{selected_movie_ids}")
        
        # Display recommended movies
        st.sidebar.header("Movie Recommendations:")
        for rec in recommendations:
            st.sidebar.write(rec)

# CSS for buttons and layout adjustments
st.markdown("""
    <style>
    .stButton>button {
        font-size: 16px;
        border: 2px solid #4CAF50;
        line-height: 1.5;
        border-radius: 5px;
        padding: 5px 20px;
        background-color: transparent;
        color: #4CAF50;
    }
    .stButton>button:hover {
        border-color: #45a049;
        color: white;
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
