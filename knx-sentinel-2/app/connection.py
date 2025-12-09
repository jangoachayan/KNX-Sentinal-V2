import logging
import asyncio
import os
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
            # Parse configuration from environment variables
            knx_host = os.getenv("KNX_HOST")
            knx_port = int(os.getenv("KNX_PORT", 3671))
            knx_type_str = os.getenv("KNX_TYPE", "AUTOMATIC").upper()

            connection_config = None
            if knx_host:
                logger.info(f"Manual KNX config detected: Host={knx_host}, Port={knx_port}, Type={knx_type_str}")
                
                # Determine connection type
                conn_type = ConnectionType.TUNNELING
                if knx_type_str == "ROUTING":
                    conn_type = ConnectionType.ROUTING
                elif knx_type_str == "AUTOMATIC":
                     # If host is provided but type is auto, default to tunneling as it's most common for specific IP
                     conn_type = ConnectionType.TUNNELING

                connection_config = ConnectionConfig(
                    gateway_ip=knx_host,
                    gateway_port=knx_port,
                    connection_type=conn_type
                )
            else:
                 logger.info("No manual host configured. Using Auto-Discovery.")

            # Initialize XKNX with or without specific config
            if connection_config:
                self.xknx = XKNX(connection_config=connection_config)
            else:
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
