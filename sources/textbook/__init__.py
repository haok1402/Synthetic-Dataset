import os

from google.cloud import storage
from sources.queue import Queue

queue = Queue(topic="textbook")
store = storage.Client().bucket(os.environ["GCP_BUCKET"])
