# Mem0 Memory

## Overview

This repository contains utilities and an API to interact with the **mem0** memory server. The system provides endpoints and scripts for saving, searching, resetting, and managing "memories" (structured data/messages) for specific users. It is built with FastAPI and supports integration with LLMs (Large Language Models) and vector databases for semantic memory operations.

## Features

- **REST API (`mem0_api.py`):**
  - Add, search, and fetch all memories for a user
  - Delete all memories (reset)
  - Ping and debug endpoints
  - API key authentication (via header or `.env`)
  - Configurable vector database, LLM, and embedder backends

- **Utility Script (`check_mem0_server.py`):**
  - Command-line tool for testing memory server endpoints
  - Supports saving, searching, adding, and resetting memories
  - Saves all user memories to a local JSON file
  - Loads API key from `.env` or command-line argument

## Requirements

- Python 3.7+
- `requests` (`pip install requests`)
- `python-dotenv` (`pip install python-dotenv`) for environment variable management

## Usage

### API

Start the FastAPI server using `mem0_api.py`. Endpoints include:

- `POST /add_memory` – Add new memories
- `POST /delete_all_memories` – Reset all memories for a user
- `GET /get_all_memories` – Fetch all memories
- `GET /debug_memory_stats` – Get memory stats and preview
- `POST /search` – Search for memories (if implemented)
- `GET /ping` – Health check

All endpoints require an API key supplied via the `X-API-Key` header.

### Command-Line Utility

`check_mem0_server.py` supports the following commands:

- `reset` – Deletes all memories for the specified user
- `save` – Saves all user memories to `memories/all_memories.json`
- `search` – Searches memories for a query string
- `add` – Adds a test memory for the user and cleans it up
- `getall` – Fetches and prints all memories for the user

#### Example

```sh
python check_mem0_server.py <command> --user <user_id> [--api-key <your_api_key>] [--query "search term"]
```

Alternatively, set your API key in a `.env` file:

```
MEMORY_API_KEY=sk-...yourkey...
```

## Configuration

Environment variables (in `.env`) control API keys, LLM and embedder models, database providers, and more.

## License

_No license specified. Please add a license if you intend to share or open source this code._
