import streamlit as st
import requests


def get_data_from_flask(url_path):
    url = "https://backenda2-mjz535d2kq-oa.a.run.app/" + url_path
    response = requests.get(url)
    return response.json()

if 'movie_title_selected' not in st.session_state:
    st.session_state['movie_title_selected'] = list()

st.set_page_config(page_title="Movie Recommendation")
st.markdown("<h1 style='text-align: center;'>Movie Recomendation</h1>", unsafe_allow_html=True)

st.title("Movie Selection")

# Could not deploy elastic search backend on cloud run i had a previous version
# running without the elastic search and i could not deploy the new version with elastic search
# The function are in the backend.py file

# in this version it works

# elastic search autocomplete search
movies_query = st.text_input("Search for a movie title here")
if movies_query:
    st.write("Results  (Click To Select):")
    autocomplete_results = get_data_from_flask(f"elastic_search/{movies_query}")
    if autocomplete_results:
        for i in autocomplete_results:
            button_key = f"select_{i}"
            if st.button(f"{i}", key=button_key, type="primary"):
                if i not in st.session_state['movie_title_selected']:
                    st.session_state['movie_title_selected'].append(i)


# display selected movies in sidebar and a button to remove them 
if st.session_state["movie_title_selected"]:
    st.sidebar.write("You have selected these movies (Click to remove):")
    for i in st.session_state["movie_title_selected"]:
        if st.sidebar.button(f"{i}", key=f"remove_{i}", type="secondary"):
            st.session_state["movie_title_selected"].remove(i)
            st.experimental_rerun()
    if st.sidebar.button("Get Recommendations", type= "primary"):
        st.switch_page('pages/test1.py')
        

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
