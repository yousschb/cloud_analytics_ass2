from flask import Flask, jsonify, request
import pandas as pd
from google.cloud import bigquery
from elasticsearch import Elasticsearch
import os

# Configuration setup
class Config:
    PROJECT_NAME = "assignment2ych"
    GOOGLE_CLOUD_KEY_PATH = 'assignment2ych-696f83052e7e.json'
    ELASTIC_ENDPOINT = "https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"
    ELASTIC_API_KEY = "ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="
    INDEX_NAME = "index_of_movies"

# App initialization
app = Flask(__name__)
app.config.from_object(Config())

# Google Cloud BigQuery client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = app.config['GOOGLE_CLOUD_KEY_PATH']
bigquery_client = bigquery.Client()

# Elasticsearch client setup
elastic_client = Elasticsearch(
    [app.config['ELASTIC_ENDPOINT']],
    headers={"Authorization": app.config['ELASTIC_API_KEY']}
)

# Utility functions
def execute_query(query):
    query_job = bigquery_client.query(query)
    return query_job.to_dataframe()

# Route definitions
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
    query = f"SELECT DISTINCT(title) FROM `{app.config['PROJECT_NAME']}.a2.movies`"
    return execute_query(query).to_json()

@app.route('/movie_ids')
def movie_ids():
    query = f"SELECT DISTINCT(movieId) FROM `{app.config['PROJECT_NAME']}.a2.movies`"
    return execute_query(query).to_json()

@app.route('/movie_ids/<movie_title>')
def movie_id_from_title(movie_title):
    query = f"""
        SELECT movieId FROM `{app.config['PROJECT_NAME']}.a2.movies`
        WHERE title = @title
    """
    return execute_query(query.replace("@title", f'"{movie_title}"')).to_json()

@app.route('/movie_titles/<movie_id>')
def title_from_id(movie_id):
    query = f"""
        SELECT title FROM `{app.config['PROJECT_NAME']}.a2.movies`
        WHERE movieId = @movie_id
    """
    return execute_query(query.replace("@movie_id", movie_id)).to_json()

@app.route('/ratings')
def ratings():
    query = f"SELECT userId, movieId, rating_im FROM `{app.config['PROJECT_NAME']}.a2.ratings`"
    return execute_query(query).to_json()

@app.route('/recommendations/<user_ids>')
def recommendations(user_ids):
    user_ids_list = user_ids.split(',')
    user_ids_query = " OR ".join(f"userId = {uid}" for uid in user_ids_list)
    query = f"""
        SELECT * FROM ML.RECOMMEND(MODEL `{app.config['PROJECT_NAME']}.a2.first-MF-model`, 
        (SELECT DISTINCT userId FROM `{app.config['PROJECT_NAME']}.a2.ratings` WHERE {user_ids_query}))
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
    response = elastic_client.search(index=app.config['INDEX_NAME'], body=body)
    return jsonify([hit['_source']['title'] for hit in response['hits']['hits']])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
