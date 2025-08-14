from rq import Queue

from app.services.clients import redis_client

# rq to process pdf indexing offloaded from server
q = Queue(connection=redis_client)