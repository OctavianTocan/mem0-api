# Mem0 Memory API

A clean, production-ready FastAPI service for semantic memory management using [Mem0](https://mem0.ai). Store, search, and manage AI agent memories with vector embeddings and LLM-powered inference.

## Features

- **Semantic Memory Storage** - Store conversations and information with AI-powered inference
- **Vector Search** - Find relevant memories using semantic similarity
- **Multiple Backends** - Support for Redis and Chroma vector databases
- **LLM Integration** - Uses Google Gemini for memory inference and embeddings
- **API Key Authentication** - Secure access with header-based authentication
- **CORS Support** - Pre-configured for local development and Railway deployment

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager
- Redis (for vector storage) or Chroma
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Mem0-Memory
```

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Configure your environment variables (see Configuration section)

5. Start the server:
```bash
uv run uvicorn mem0_api:app --host 0.0.0.0 --port 8000
```

Or use the included startup script:
```bash
./start.sh
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/api/v1/docs`

## API Endpoints

All endpoints require an `X-API-Key` header for authentication.

### Health Check
```http
GET /
```
Returns: `{"status": "ok"}`

### Ping
```http
POST /ping
```
Returns: `{"status": "pong"}`

### Add Memory
```http
POST /add_memory
Content-Type: application/json
X-API-Key: your-api-key

{
  "messages": [
    {"role": "user", "content": "I love pizza"},
    {"role": "assistant", "content": "I'll remember that!"}
  ],
  "user_id": "user123",
  "agent_id": "agent456",
  "infer": true,
  "metadata": {"source": "conversation"},
  "prompt": "Extract key facts about user preferences"
}
```

**Parameters:**
- `messages` (required): List of message objects with `role` and `content`
- `user_id` (optional): User identifier
- `agent_id` (optional): Agent identifier
- `infer` (optional, default: true): Whether to use LLM to infer additional memories
- `metadata` (optional): Custom metadata dictionary
- `prompt` (optional): Custom prompt to guide memory inference

**Returns:**
```json
{
  "status": "memory added",
  "result": {
    "results": [
      {"id": "mem_abc123", "memory": "User loves pizza", ...}
    ]
  }
}
```

### Search Memory
```http
POST /search_memory
Content-Type: application/json
X-API-Key: your-api-key

{
  "query": "What food does the user like?",
  "user_id": "user123",
  "agent_id": "agent456"
}
```

**Parameters:**
- `query` (required): Search query string
- `user_id` (optional): Filter by user ID
- `agent_id` (optional): Filter by agent ID

**Returns:**
```json
{
  "results": [
    {
      "id": "mem_abc123",
      "memory": "User loves pizza",
      "score": 0.95,
      ...
    }
  ]
}
```

### Get All Memories
```http
POST /get_all_memories
Content-Type: application/json
X-API-Key: your-api-key

{
  "user_id": "user123"
}
```

**Parameters:**
- `user_id` (required): User identifier

**Returns:**
```json
{
  "status": "success",
  "memories": [...],
  "count": 42
}
```

### Delete All Memories
```http
POST /delete_all_memories
X-API-Key: your-api-key
```

**Returns:**
```json
{
  "status": "memory deleted"
}
```

## Configuration

Configure the API using environment variables in `.env`:

### Required

```bash
# API Authentication
MEMORY_API_KEY=your-secret-api-key
```

### Optional

```bash
# LLM Configuration
LLM_PROVIDER=gemini                          # Default: gemini
LLM_MODEL=models/gemini-2.5-flash           # Default: models/gemini-2.5-flash
LLM_MAX_TOKENS=2000                          # Default: 2000

# Embedder Configuration
EMBEDDER_PROVIDER=gemini                     # Default: gemini
EMBEDDER_MODEL=models/text-embedding-004     # Default: models/text-embedding-004
EMBEDDER_DIMENSIONS=768                      # Default: 768

# Database Configuration
DATABASE_PROVIDER=redis                      # Options: redis, chroma (default: redis)
REDIS_URL=redis://localhost:6379             # Required if using Redis
DB_COLLECTION_NAME=mem0                      # Default: mem0

# Search Configuration
MEMORY_SEARCH_LIMIT=100                      # Default: 100

# CORS Configuration
ENVIRONMENT=development                      # Set to 'production' to disable localhost CORS
CORS_ORIGINS=https://example.com             # Comma-separated list of allowed origins

# Railway Deployment (automatically detected)
RAILWAY_STATIC_URL=your-app.railway.app
RAILWAY_PUBLIC_DOMAIN=your-domain.com
```

## Example Usage

### Python Client

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY}

# Add a memory
response = requests.post(
    f"{API_URL}/add_memory",
    json={
        "messages": [
            {"role": "user", "content": "My favorite color is blue"}
        ],
        "user_id": "user123",
        "infer": True
    },
    headers=headers
)
print(response.json())

# Search memories
response = requests.post(
    f"{API_URL}/search_memory",
    json={
        "query": "What is the user's favorite color?",
        "user_id": "user123"
    },
    headers=headers
)
print(response.json())

# Get all memories
response = requests.post(
    f"{API_URL}/get_all_memories",
    json={"user_id": "user123"},
    headers=headers
)
print(response.json())
```

### cURL

```bash
# Add memory
curl -X POST "http://localhost:8000/add_memory" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "I work as a software engineer"}],
    "user_id": "user123",
    "infer": true
  }'

# Search memories
curl -X POST "http://localhost:8000/search_memory" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the user do for work?",
    "user_id": "user123"
  }'
```

## Architecture

```
FastAPI Application
    ↓
Mem0 Framework (v1.0.0)
    ↓
├─ Google Gemini (LLM & Embeddings)
└─ Vector Database (Redis/Chroma)
```

## Deployment

### Railway

The API is pre-configured for Railway deployment:

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy - Railway will automatically use `start.sh`

### Docker

```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY .python-version .

# Install dependencies
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "mem0_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mem0-api .
docker run -p 8000:8000 --env-file .env mem0-api
```

## Development

### Project Structure

```
.
├── mem0_api.py        # FastAPI application and endpoints
├── models.py          # Pydantic request/response models
├── pyproject.toml     # Project configuration and dependencies (uv)
├── .python-version    # Python version specification
├── start.sh          # Startup script
└── README.md         # This file
```

### Testing

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/redoc`

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Mem0** (v1.0.0) - Memory management framework
- **Google Gemini** - LLM and embeddings provider
- **Redis/Chroma** - Vector database backends
- **Pydantic** - Data validation

## Troubleshooting

### Redis Connection Issues
Ensure Redis is running:
```bash
redis-cli ping  # Should return PONG
```

### Authentication Errors
Verify your `X-API-Key` header matches `MEMORY_API_KEY` in `.env`

### Memory Inference Not Working
Check that your Google Gemini API key is properly configured and has quota

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions:
- Open a GitHub issue
- Check [Mem0 documentation](https://docs.mem0.ai)
