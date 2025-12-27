import redis.asyncio as redis
from app.core.config import settings
import json

# Initialize Async Redis with your Cloud credentials
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=settings.REDIS_USER,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

async def publish_event(channel: str, message: dict):
    """Broadcasts to WebSockets via Pub/Sub"""
    await redis_client.publish(channel, json.dumps(message))

async def push_job_to_queue(job_data: dict):
    """Pushes jobs to the background worker"""
    await redis_client.rpush("job_queue", json.dumps(job_data))