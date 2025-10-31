# redis_client.py
import redis
import os
from django.conf import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_URL,
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)