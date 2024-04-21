import streamlit as st
import requests
import pandas as pd

def get_data_from_flask(url_path):
    """Envoyer une requête GET et retourner la réponse JSON."""
    url = f"https://cloud-analytics-ass207-gev3pcymxa-uc.a.run.app/{url_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to get data from {url}: {response.status_code}")
        return None

def extract_single_value(json_response, key):
    """Extraire une valeur unique à partir d'une réponse JSON structurée."""
    if json_response and key in json_response:
        return json_response[key]['0']
    else:
        st.error(f"Key '{key}' not found in the response")
        return None

def search_movies_by_keyword(keyword):
    movies = get_data_from_flask(f"elastic_search/{keyword}")
    if movies:
        st.write("Search Results:", movies)
    else:
        st.write("No results found.")

search_movies_by_keyword("Harry")
