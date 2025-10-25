#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Start the server
uvicorn mem0_api:app --host 0.0.0.0 --port $PORT