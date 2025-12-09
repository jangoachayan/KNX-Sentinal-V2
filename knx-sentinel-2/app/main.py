from fastapi import FastAPI
from xknx import XKNX
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knx-sentinel")

app = FastAPI(title="KNX Sentinel V2", version="0.1.0")

xknx = None

@app.on_event("startup")
async def startup_event():
    global xknx
    logger.info("Starting KNX Sentinel V2...")
    try:
        # Initialize XKNX (by default reads xknx.yaml or tries auto-discovery)
        # In an Add-on, we might want to pass parameters explicitly from config later.
        xknx = XKNX()
        await xknx.start()
        logger.info("XKNX started successfully.")
    except Exception as e:
        logger.error(f"Failed to start XKNX: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global xknx
    if xknx:
        await xknx.stop()
        logger.info("XKNX stopped.")

@app.get("/")
async def read_root():
    return {"status": "online", "service": "KNX Sentinel V2"}

@app.get("/health")
async def health_check():
    if xknx and xknx.started:
        return {"status": "healthy", "knx_connected": True}
    return {"status": "unhealthy", "knx_connected": False}
