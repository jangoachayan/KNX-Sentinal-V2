import logging
import asyncio
from collections import deque
from xknx.telegram import Telegram
from datetime import datetime

logger = logging.getLogger("knx-sentinel.monitor")

class BusMonitor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BusMonitor, cls).__new__(cls)
            # Store last 1000 telegrams
            cls._instance.history = deque(maxlen=1000)
            cls._instance.subscribers = set()
        return cls._instance

    async def start(self, xknx):
        """Starts monitoring the bus."""
        if not xknx:
            logger.error("Cannot start monitor: XKNX instance is missing.")
            return
        
        # Register callback for all telegrams
        xknx.telegram_queue.register_telegram_received_cb(self._telegram_received_cb)
        logger.info("Bus Monitor started and listening for telegrams.")

    def _telegram_received_cb(self, telegram: Telegram):
        """Synchronous callback wrapper for XKNX."""
        asyncio.create_task(self.process_telegram(telegram))

    async def process_telegram(self, telegram: Telegram):
        """Callback when a telegram is received."""
        try:
            processed_data = self._parse_telegram(telegram)
            self.history.appendleft(processed_data)
            
            # Broadcast to real-time subscribers (WebSockets)
            for queue in list(self.subscribers):
                await queue.put(processed_data)
                
        except Exception as e:
            logger.error(f"Error processing telegram: {e}")

    def _parse_telegram(self, telegram: Telegram):
        """Converts an XKNX telegram to a JSON-friendly dict."""
        payload_data = None
        if telegram.payload:
             payload_data = str(telegram.payload)

        return {
            "timestamp": datetime.now().isoformat(),
            "direction": telegram.direction.value,
            "source": str(telegram.source_address),
            "destination": str(telegram.destination_address),
            "payload": payload_data,
            "type": telegram.payload.__class__.__name__ if telegram.payload else "Unknown"
        }

    async def subscribe(self):
        """Subscribes to the real-time feed."""
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue):
        """Unsubscribes from the real-time feed."""
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    def get_history(self):
        """Returns the current history buffer."""
        return list(self.history)
