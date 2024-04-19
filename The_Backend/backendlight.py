from flask import Flask, jsonify, request
import pandas as pd
from google.cloud import bigquery
from elasticsearch import Elasticsearch
import os

# Configuration des chemins et des clés
PROJECT_ID = "caaych2"
GOOGLE_CLOUD_KEY_PATH = 'caaych2-1324a5d22551.json'
ELASTIC_ENDPOINT = "https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"
ELASTIC_API_KEY = "ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="
INDEX_NAME = "index_of_movies"

# Configuration de l'environnement pour Google Cloud BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_KEY_PATH
bigquery_client = bigquery.Client(project=PROJECT_ID)  # Utilisez une seule instance du client correctement configurée

# Configuration du client Elasticsearch
elastic_client = Elasticsearch(
    [ELASTIC_ENDPOINT],
    headers={"Authorization": ELASTIC_API_KEY}
)

app = Flask(__name__)

# Fonctions utilitaires
def execute_query(query):
    query_job = bigquery_client.query(query)
    return query_job.to_dataframe()

# Definitions de la route
@app.route('/')
def home():
    return jsonify({
        "routes": [
            "/movie_titles", "/movie_ids", "/movie_ids/<movie_title>",
            "/movie_titles/<movie_id>", "/ratings", "/recommendations/<user_ids>",
            "/search/<query>"
        ]
    })

@app.route('/movie_titles')
def movie_titles():
    query = "SELECT DISTINCT(title) FROM `caaych2.mo.movies`"
    return execute_query(query).to_json()

@app.route('/movie_ids')
def movie_ids():
    query = "SELECT DISTINCT(movieId) FROM `caaych2.mo.movies`"
    return execute_query(query).to_json()

@app.route('/movie_ids/<movie_title>')
def movie_id_from_title(movie_title):
    query = f"""
        SELECT movieId FROM `caaych2.mo.movies`
        WHERE title = @title
    """
    return execute_query(query.replace("@title", f'"{movie_title}"')).to_json()

@app.route('/movie_titles/<movie_id>')
def title_from_id(movie_id):
    query = f"""
        SELECT title FROM `caaych2.mo.movies`
        WHERE movieId = @movie_id
    """
    return execute_query(query.replace("@movie_id", movie_id)).to_json()

@app.route('/ratings')
def ratings():
    query = "SELECT userId, movieId, rating_im FROM `caaych2.mo.ratings`"
    return execute_query(query).to_json()

@app.route('/recommendations/<user_ids>')
def recommendations(user_ids):
    user_ids_list = user_ids.split(',')
    user_ids_query = " OR ".join(f"userId = {uid}" for uid in user_ids_list)
    query = f"""
        SELECT * FROM ML.RECOMMEND(MODEL `caaych2.mo.first-MF-model`, 
        (SELECT DISTINCT userId FROM `caaych2.mo.ratings` WHERE {user_ids_query}))
        ORDER BY -predicted_rating_im_confidence
    """
    return execute_query(query).to_json()

@app.route('/search/<query>')
def search(query):
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
    return jsonify([hit['_source']['title'] for hit in response['hits']['hits']])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
