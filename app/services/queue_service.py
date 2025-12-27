import os
import json
import redis.asyncio as redis
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Build URL from individual components in your .env
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_USER = os.getenv("REDIS_USER", "default")

# Constructing a valid URL scheme: redis://user:password@host:port
REDIS_URL = f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

# Global client used by both Jobs and Realtime routers
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def push_job_to_queue(job_data: dict):
    """Pushes a task to the Redis Cloud queue for the worker."""
    await redis_client.rpush("job_queue", json.dumps(job_data))
    return True