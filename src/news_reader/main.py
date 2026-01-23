# /functions/news-crawler/main.py

import base64
import os
import json
from datetime import datetime

import functions_framework
import requests
from bs4 import BeautifulSoup
from google.cloud import pubsub_v1, storage
from google.api_core import exceptions

# --- Configuration ---
# Environment variables are set in docker-compose.yml for local development
PROJECT_ID = os.environ.get("GCP_PROJECT", "local-dev-project")
TARGET_URL = "https://www.bta.bg/en/news"
NEXT_TOPIC_ID = "articles-topic"
STATE_BUCKET_NAME = os.environ.get("STATE_BUCKET_NAME", "local-state-bucket")
STATE_BLOB_NAME = "last_article_url.txt"

# --- Clients (initialized globally) ---
# When PUBSUB_EMULATOR_HOST is set, this client connects to the emulator
publisher = pubsub_v1.PublisherClient()
# When STORAGE_EMULATOR_HOST is set, this client connects to the emulator
storage_client = storage.Client()

topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC_ID)

def _get_last_processed_url(bucket_name: str, blob_name: str) -> str | None:
    """Fetches the last processed article URL from GCS."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if blob.exists():
            return blob.download_as_text()
        return None
    except exceptions.NotFound:
        print(f"Bucket '{bucket_name}' or blob '{blob_name}' not found. Will proceed as first run.")
        return None
    except Exception as e:
        print(f"Error getting last processed URL: {e}")
        return None

def _set_last_processed_url(url: str, bucket_name: str, blob_name: str):
    """Saves the last processed article URL to GCS."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(url)
    except Exception as e:
        print(f"Error setting last processed URL: {e}")

@functions_framework.cloud_event
def crawl_news(cloud_event):
    """
    Cloud Function to crawl a news website, find new articles,
    and publish them to a Pub/Sub topic.
    """
    print(f"Crawl function triggered by event: {cloud_event.id}")

    # In a real scenario, you would crawl the website here.
    # For this example, we'll simulate finding a few articles.
    print(f"Simulating crawl of {TARGET_URL}")
    
    last_processed_url = _get_last_processed_url(STATE_BUCKET_NAME, STATE_BLOB_NAME)
    print(f"Last processed URL from GCS emulator: {last_processed_url}")

    # Simulate finding 3 new articles
    new_articles_to_publish = [
        {
            "url": "https://example.com/article/3",
            "title": "Third New Article",
            "content": "Content of the third article.",
            "crawled_at": datetime.utcnow().isoformat()
        },
        {
            "url": "https://example.com/article/2",
            "title": "Second New Article",
            "content": "Content of the second article.",
            "crawled_at": datetime.utcnow().isoformat()
        },
        {
            "url": "https://example.com/article/1",
            "title": "First New Article",
            "content": "Content of the first article.",
            "crawled_at": datetime.utcnow().isoformat()
        },
    ]

    if not new_articles_to_publish:
        print("No new articles to publish.")
        return

    # Publish new articles
    for article_data in reversed(new_articles_to_publish):
        # Don't re-publish what we've already seen
        if article_data['url'] == last_processed_url:
            break
        try:
            message_data = json.dumps(article_data).encode("utf-8")
            future = publisher.publish(topic_path, data=message_data)
            future.result() # Wait for publish to complete
            print(f"Published to Pub/Sub emulator: {article_data['url']}")
        except Exception as e:
            print(f"Error publishing article {article_data['url']}: {e}")

    # After successfully publishing, update the state with the newest article's URL
    newest_article_url = new_articles_to_publish[0]['url']
    _set_last_processed_url(newest_article_url, STATE_BUCKET_NAME, STATE_BLOB_NAME)
    print(f"Updated last processed URL in GCS emulator to: {newest_article_url}")