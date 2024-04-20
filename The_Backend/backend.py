from flask import Flask, jsonify, request
import pandas as pd
from google.cloud import bigquery
from elasticsearch import Elasticsearch
import os

# Configurations for project and keys
PROJECT_ID = "caaych2"
GOOGLE_CLOUD_KEY_PATH = 'caaych2-1324a5d22551.json'
ELASTIC_ENDPOINT = "https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"
ELASTIC_API_KEY = "ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="
INDEX_NAME = "index_of_movies"

# Setting environment variables for Google Cloud and Elasticsearch
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_KEY_PATH
bigquery_client = bigquery.Client(project=PROJECT_ID)
elastic_client = Elasticsearch([ELASTIC_ENDPOINT], headers={"Authorization": f"ApiKey {ELASTIC_API_KEY}"})

app = Flask(__name__)

def execute_bigquery(query):
    return bigquery_client.query(query).to_dataframe()

@app.route('/')
def api_root():
    # Generating dynamic endpoints using the base URL from the request
    endpoints = {
        "movie_titles": "Retrieve a list of all movie titles available.",
        "movie_ids": "Fetch all unique movie IDs.",
        "ratings": "Get ratings from users.",
        "recommendations/<user_ids>": "Generate recommendations for provided user IDs.",
        "elastic_search/<query>": "Perform a search for movie titles using Elasticsearch."
    }
    
    base_url = request.base_url.rstrip('/')
    
    # Construct an HTML list of endpoints
    html = "<h1>API Endpoint List</h1>"
    html += "<ul>"
    for path, desc in endpoints.items():
        url = f"{base_url}/{path}"
        html += f"<li><a href='{url}'>{path}</a>: {desc}</li>"
    html += "</ul>"
    return html

# Additional routes defined here

@app.route('/movie_titles')
def list_movie_titles():
    query = "SELECT DISTINCT(title) FROM `caaych2.mo.movies`"
    results = execute_bigquery(query)
    return results.to_json()

@app.route('/movie_ids')
def list_movie_ids():
    query = "SELECT DISTINCT(movieId) FROM `caaych2.mo.movies`"
    results = execute_bigquery(query)
    return results.to_json()

@app.route('/ratings')
def list_ratings():
    query = "SELECT userId, movieId, rating_im FROM `caaych2.mo.ratings`"
    results = execute_bigquery(query)
    return results.to_json()

@app.route('/recommendations/<user_ids>')
def generate_recommendations(user_ids):
    user_ids_list = [int(uid) for uid in user_ids.split(',')]
    user_condition = " OR ".join(f"userId = {uid}" for uid in user_ids_list)
    query = f"""
        SELECT * FROM ML.RECOMMEND(MODEL `caaych2.mo.first-MF-model`,
        (
        SELECT DISTINCT userId
        FROM `caaych2.mo.ratings`
        WHERE {user_condition}))
        ORDER BY -(predicted_rating_im_confidence)
    """
    results = execute_bigquery(query)
    return results.to_json()


@app.route('/elastic_search/<query>')
def search_elastic(query):
    body = {
        "query": {
            "match_phrase_prefix": {
                "title": {
                    "query": query,
                    "max_expansions": 10
                }
            }
        }
    }
    response = elastic_client.search(index=INDEX_NAME, body=body)
    titles = [hit['_source']['title'] for hit in response['hits']['hits']]
    return jsonify(titles)
    
@app.route('/tmdb_id/<movie_id>')
def tmdb_id(movie_id):
    query = f"SELECT tmdbId FROM `caaych2.mo.links` WHERE movieId = {movie_id}"
    results = execute_bigquery(query)
    return results.to_json()

@app.route('/movie_id_from_title/<movie_title>')
def movie_id_from_title(movie_title):
    query = f"SELECT movieId FROM `caaych2.mo.movies` WHERE title = '{movie_title}'"
    results = execute_bigquery(query)
    return results.to_json()


@app.route('/title_from_movie_id/<movie_id>')
def title_from_movie_id(movie_id):
    query = f"SELECT title FROM `caaych2.mo.movies` WHERE movieId = {movie_id}"
    results = execute_bigquery(query)
    return results.to_json()
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
