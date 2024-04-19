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

elastic_client = Elasticsearch(
    ["https://6f8402e9b7ae48f6ad05fb7037960f8a.europe-west9.gcp.elastic-cloud.com:443"],
    headers={"Authorization": "ApiKey ODhqUDJJNEJFZjlFU080SWh3VFA6YlQyLUM3WENSbk9CSHJTTnBCRW1RZw=="}
)

app = Flask(__name__)

# Fonctions utilitaires
def execute_query(query):
    query_job = bigquery_client.query(query)
    return query_job.to_dataframe()

@app.route('/')
def home():
    # Définir les routes et leurs descriptions
    routes = {
        "/movie_titles": "Afficher les titres de films",
        "/movie_ids": "Afficher les IDs de films",
        "/movie_ids/<movie_title>": "Afficher l'ID d'un film spécifique par titre",
        "/movie_titles/<movie_id>": "Afficher le titre d'un film par ID",
        "/ratings": "Afficher les évaluations",
        "/recommendations/<user_ids>": "Afficher les recommandations pour les utilisateurs",
        "/search/<query>": "Rechercher des films par titre"
    }

    # Construire le HTML pour les liens
    html = "<h1>Bienvenue à l'API de films</h1>"
    html += "<ul>"
    for path, description in routes.items():
        link = f'http://127.0.0.1:8080{path}'
        html += f'<li><a href="{link}">{path}</a> - {description}</li>'
    html += "</ul>"
    
    return html


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
    user_ids_list = [int(uid) for uid in user_ids.split(',')]  # Convertit la chaîne en liste d'entiers
    user_ids_condition = " OR ".join(f"userId = {uid}" for uid in user_ids_list)  # Crée la condition pour la requête SQL

    query = f"""
        SELECT * FROM ML.RECOMMEND(MODEL `caaych2.mo.first-MF-model`,
        (
        SELECT DISTINCT userId
        FROM `caaych2.mo.ratings`
        WHERE {user_ids_condition}))
        ORDER BY -(predicted_rating_im_confidence)
    """
    query_job = bigquery_client.query(query)  # Exécute la requête
    results = query_job.to_dataframe()  # Convertit les résultats en DataFrame
    return results.to_json()


@app.route('/title_from_id/<movie_id>')
def title_from_id(movie_id):
    """Return the title of a movie based on its ID."""
    query = f"""
            SELECT m.title
            FROM `{PROJECT_NAME}.{DATASET}.movies` m
            WHERE m.movieId = {movie_id}
            """
    result = execute_query(query)
    return result.to_json()

@app.route('/tmdb_id/<movie_id>')
def tmdb_id(movie_id):
    """Return the TMDB ID of a movie based on its movie ID."""
    query = f"""
            SELECT l.tmdbId
            FROM `{PROJECT_NAME}.{DATASET}.links` l
            WHERE l.movieId = {movie_id}
            """
    result = execute_query(query)
    return result.to_json()

@app.route('/elastic_search/<query>')
def elastic_search(query):
    """Perform an elastic search for a given query."""
    body = {
        "query": {
            "match_phrase_prefix": {
                "title": {
                    "query": query,
                    "max_expansions": 10
                }
            }
        },
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
