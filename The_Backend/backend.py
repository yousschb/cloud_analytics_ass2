from flask import Flask, jsonify, request
import pandas as pd
from google.cloud import bigquery
from elasticsearch import Elasticsearch
import os

# Configuration of paths and keys
PROJECT_ID = "caaych2"
GOOGLE_CLOUD_KEY_PATH = 'caaych2-1324a5d22551.json'
ELASTIC_ENDPOINT = "https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"
ELASTIC_API_KEY = "ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="
INDEX_NAME = "index_of_movies"

# Environment setup for Google Cloud BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_KEY_PATH
bigquery_client = bigquery.Client(project=PROJECT_ID)

elastic_client = Elasticsearch(
    [ELASTIC_ENDPOINT],
    headers={"Authorization": f"ApiKey {ELASTIC_API_KEY}"}
)

app = Flask(__name__)

def execute_query(query):
    query_job = bigquery_client.query(query)
    return query_job.to_dataframe()

@app.route('/')
def home():
    # Define the routes and their descriptions
    routes = {
        "/movie_titles": "Display movie titles",
        "/movie_ids": "Display movie IDs",
        "/ratings": "Display ratings",
        "/recommendations/<user_ids>": "Display recommendations for users",
        "/elastic_search/<query>": "Search for movies by title"
    }

    # Construct HTML for the links
    html = "<h1>Welcome to the Movie API</h1>"
    html += "<ul>"
    for path, description in routes.items():
        # Use request.base_url to dynamically generate full URLs
        full_path = request.base_url.rstrip('/') + path
        html += f'<li><a href="{full_path}">{path}</a> - {description}</li>'
    html += "</ul>"
    
    return html

# Continue with other routes as previously defined without changes

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
