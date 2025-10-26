#!/bin/bash

# Install Python dependencies using uv
uv sync

# Start the server
uv run uvicorn mem0_api:app --host 0.0.0.0 --port $PORT