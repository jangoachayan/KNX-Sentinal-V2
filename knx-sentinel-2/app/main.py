from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.connection import KNXConnectionManager
from app.monitor import BusMonitor
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knx-sentinel")

app = FastAPI(title="KNX Sentinel 2", version="0.1.5")

# Managers
connection_manager = KNXConnectionManager()
bus_monitor = BusMonitor()

# Serve frontend static files
# Ensure the directory exists or this will fail. We will create it next.
static_dir = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting KNX Sentinel 2...")
    await connection_manager.start()
    
    # Start the monitor if connection succeeded (or even if not, to be ready)
    xknx = connection_manager.get_xknx()
    if xknx:
        await bus_monitor.start(xknx)

@app.on_event("shutdown")
async def shutdown_event():
    await connection_manager.stop()

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "knx_connected": connection_manager.connected
    }

@app.get("/api/history")
async def get_history():
    return bus_monitor.get_history()

@app.websocket("/ws/telegrams")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = await bus_monitor.subscribe()
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        bus_monitor.unsubscribe(queue)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        bus_monitor.unsubscribe(queue)
