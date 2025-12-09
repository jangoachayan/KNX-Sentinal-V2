import logging
import asyncio
from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType

logger = logging.getLogger("knx-sentinel.connection")

class KNXConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KNXConnectionManager, cls).__new__(cls)
            cls._instance.xknx = None
            cls._instance.connected = False
        return cls._instance

    async def start(self):
        """Starts the XKNX connection."""
        if self.xknx is not None:
             logger.warning("XKNX is already initialized.")
             return

        logger.info("Initializing XKNX connection...")
        try:
            # In a real add-on, we would parse config options here.
            # For now, we rely on xknx auto-discovery or default config.
            # If a knx.yaml exists in /config, xknx might pick it up if configured.
            # Ideally, we construct ConnectionConfig from Add-on options.
            
            self.xknx = XKNX()
            await self.xknx.start()
            self.connected = True
            logger.info("XKNX connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to KNX: {e}")
            self.connected = False
            # In a real scenario, implement a retry loop here

    async def stop(self):
        """Stops the XKNX connection."""
        if self.xknx:
            await self.xknx.stop()
            self.xknx = None
            self.connected = False
            logger.info("XKNX connection stopped.")
    
    def get_xknx(self):
        return self.xknx
