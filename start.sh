#!/bin/bash
uvicorn mem0_api:app --host 0.0.0.0 --port $PORT
