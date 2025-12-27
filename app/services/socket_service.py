from app.services.queue_service import redis_client
import json

async def publish_event(channel: str, message: dict):
    """
    Publishes an event to a Redis Channel.
    [cite_start]Satisfies 'Event distribution using Redis Pub/Sub'[cite: 61].
    """
    await redis_client.publish(channel, json.dumps(message))