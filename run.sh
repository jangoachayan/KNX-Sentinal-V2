#!/usr/bin/with-contenv bashio

echo "Starting KNX Sentinel V2..."

# Retrieve config options if needed in the future using bashio
# LOG_LEVEL=$(bashio::config 'log_level')

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000
