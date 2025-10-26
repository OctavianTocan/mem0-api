# Docker Deployment Guide

This guide explains how to deploy the Mem0 Memory API using Docker and Docker Compose.

## Architecture

The Docker setup includes three services:

- **mem0-api**: FastAPI application (port 8000)
- **redis**: Vector database for memory storage (port 6379)
- **ollama**: Local LLM inference service (port 11434)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB+ RAM (4GB for Ollama, rest for other services)
- Google Gemini API key

## Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your preferred editor
```

Required environment variables:
- `MEMORY_API_KEY`: Your API authentication key
- `GOOGLE_API_KEY`: Google Gemini API key

### 2. Start Services

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### 3. Verify Deployment

```bash
# Check API health
curl http://localhost:8000/

# Check Redis
docker exec mem0-redis redis-cli ping

# Check Ollama
curl http://localhost:11434/
```

### 4. Pull Ollama Models (Optional)

If you want to use Ollama for local LLM inference:

```bash
# Pull a model (example: llama2)
docker exec -it mem0-ollama ollama pull llama2

# List available models
docker exec -it mem0-ollama ollama list

# Test model
docker exec -it mem0-ollama ollama run llama2 "Hello"
```

## Configuration

### Using Ollama Instead of Gemini

To use Ollama for LLM inference, update your `.env`:

```bash
LLM_PROVIDER=ollama
LLM_MODEL=llama2  # or any model you've pulled
OLLAMA_BASE_URL=http://ollama:11434
```

### GPU Support (NVIDIA)

To enable GPU acceleration for Ollama:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Uncomment GPU section in `docker-compose.yml`:
```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

3. Restart services:
```bash
docker compose down
docker compose up -d
```

### Resource Limits

Default resource limits (adjust in `docker-compose.yml`):

- **Redis**: 512MB max, 256MB reserved
- **Ollama**: 8GB max, 4GB reserved
- **API**: No limits (adjust as needed)

## Usage

### Test API

```bash
# Add memory
curl -X POST http://localhost:8000/add_memory \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "I love pizza"}],
    "user_id": "user123"
  }'

# Search memory
curl -X POST http://localhost:8000/search_memory \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What food does the user like?",
    "user_id": "user123"
  }'
```

### API Documentation

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/redoc

## Management

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f mem0-api
docker compose logs -f redis
docker compose logs -f ollama
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart mem0-api
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (deletes data!)
docker compose down -v
```

### Update Services

```bash
# Rebuild API after code changes
docker compose up -d --build mem0-api

# Pull latest Ollama image
docker compose pull ollama
docker compose up -d ollama
```

## Data Persistence

Data is persisted using Docker volumes:

- `redis-data`: Memory embeddings and vector data
- `ollama-data`: Downloaded LLM models

To backup data:

```bash
# Backup Redis data
docker run --rm -v mem0-api_redis-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz -C /data .

# Backup Ollama models
docker run --rm -v mem0-api_ollama-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama-backup.tar.gz -C /data .
```

To restore:

```bash
# Restore Redis data
docker run --rm -v mem0-api_redis-data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/redis-backup.tar.gz"
```

## Troubleshooting

### API Won't Start

Check logs:
```bash
docker compose logs mem0-api
```

Common issues:
- Missing `GOOGLE_API_KEY` or `MEMORY_API_KEY` in `.env`
- Redis not healthy (check `docker compose ps`)

### Redis Connection Failed

```bash
# Check Redis health
docker exec mem0-redis redis-cli ping

# Check Redis logs
docker compose logs redis
```

### Ollama Out of Memory

Reduce model size or increase Docker memory:

```bash
# Use smaller model
docker exec -it mem0-ollama ollama pull llama2:7b

# Or adjust docker-compose.yml memory limits
```

### Port Already in Use

Change port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

## Production Deployment

### Security Checklist

- [ ] Use strong `MEMORY_API_KEY`
- [ ] Configure `CORS_ORIGINS` to restrict access
- [ ] Set `ENVIRONMENT=production`
- [ ] Use secrets management for API keys
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Regular backups of volumes
- [ ] Monitor resource usage

### Reverse Proxy Example (nginx)

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Best Practices

1. **Version Pinning**: Docker images use pinned versions (redis:7.2-alpine, ollama:0.5.4)
2. **Health Checks**: All services have health checks for reliability
3. **Resource Limits**: Memory limits prevent resource exhaustion
4. **Non-Root User**: API runs as non-root user (mem0user)
5. **Multi-Stage Build**: Smaller image size (builder pattern)
6. **Named Volumes**: Proper data persistence

## Support

For issues:
- Check logs: `docker compose logs`
- Verify environment: `docker compose config`
- Test connectivity: `docker compose exec mem0-api ping redis`
- Review [Mem0 docs](https://docs.mem0.ai)
- Review [Ollama docs](https://ollama.ai/docs)
