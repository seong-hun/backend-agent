import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, event: dict):
        event["timestamp"] = datetime.utcnow().isoformat()
        await self.queue.put(event)

    def subscribe(self):
        return self.queue


event_bus = EventBus()
