import streamlit as st

# Setup page configuration
st.set_page_config(page_title="Movie App", layout="wide")

# Initialize session state variables if they don't exist
if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = []
if 'movie_ids' not in st.session_state:
    st.session_state.movie_ids = []
if 'page' not in st.session_state:
    st.session_state.page = 'selection'

# Navigation
page = st.radio("Choose a page:", ['Selection', 'Recommendation'])

if page == 'Selection':
    st.session_state.page = 'selection'
elif page == 'Recommendation':
    st.session_state.page = 'recommendation'

