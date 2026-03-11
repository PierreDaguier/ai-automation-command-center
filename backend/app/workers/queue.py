from redis import Redis
from rq import Queue

from app.core.config import settings

QUEUE_NAME = "workflow-runs"


def get_queue() -> Queue | None:
    try:
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=1)
        redis.ping()
        return Queue(name=QUEUE_NAME, connection=redis)
    except Exception:
        return None
