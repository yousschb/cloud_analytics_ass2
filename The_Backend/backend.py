from flask import Flask, jsonify, request
import pandas as pd
from google.cloud import bigquery
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)

# Initialize BigQuery and Elasticsearch clients
PROJECT_ID = "caaych2"
GOOGLE_CLOUD_KEY_PATH = 'caaych2-1324a5d22551.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_KEY_PATH
bigquery_client = bigquery.Client(project=PROJECT_ID)
ELASTIC_ENDPOINT = "https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"
ELASTIC_API_KEY = "ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="
elastic_client = Elasticsearch([ELASTIC_ENDPOINT], headers={"Authorization": f"ApiKey {ELASTIC_API_KEY}"})
INDEX_NAME = "index_of_movies"

def execute_bigquery(query):
    try:
        return bigquery_client.query(query).to_dataframe()
    except Exception as e:
        return pd.DataFrame()  # Return an empty DataFrame on error

@app.route('/movie_titles')
def list_movie_titles():
    query = "SELECT DISTINCT(title) FROM `caaych2.mo.movies`"
    query_job = bigquery_client.query(query)
    results = query_job.to_dataframe() 
    return results.to_json()

@app.route('/movie_ids')
def list_movie_ids():
    query = "SELECT DISTINCT(movieId) FROM `caaych2.mo.movies`"
    query_job = bigquery_client.query(query)
    results = query_job.to_dataframe() 
    return results.to_json()

@app.route('/ratings')
def list_ratings():
    query = "SELECT userId, movieId, rating_im FROM `caaych2.mo.ratings`"
    query_job = bigquery_client.query(query)
    results = query_job.to_dataframe() 
    return results.to_json()

@app.route('/recommendations/<user_ids>')
def generate_recommendations(user_ids):
    user_ids_list = [int(uid) for uid in user_ids.split(',')]
    user_condition = " OR ".join(f"userId = {uid}" for uid in user_ids_list)
    query = f"""
        SELECT * FROM ML.RECOMMEND(MODEL `caaych2.mo.first-MF-model`,
        (SELECT DISTINCT userId FROM `caaych2.mo.ratings` WHERE {user_condition}))
        ORDER BY -(predicted_rating_im_confidence)
    """
    query_job = bigquery_client.query(query)
    results = query_job.to_dataframe() 
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
    suggestions = [hit['_source']['title'] for hit in response['hits']['hits']]
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
