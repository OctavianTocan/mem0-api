#!/bin/bash

# Build the web app first
echo "Building Mem0 web app..."
cd mem0-webapp
npm install
npm run build
cd ..

# Install Python dependencies
pip install --upgrade mem0ai[graph]

# Start the server
uvicorn mem0_api:app --host 0.0.0.0 --port $PORT