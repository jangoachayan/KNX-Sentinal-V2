#!/usr/bin/with-contenv bashio

echo "Starting KNX Sentinel V2..."

# Retrieve config options using bashio and export as env vars
export KNX_HOST=$(bashio::config 'knx_host')
export KNX_PORT=$(bashio::config 'knx_port')
export KNX_TYPE=$(bashio::config 'knx_type')


# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
