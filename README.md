# Mem0 API

This project provides a production-ready API for `mem0`, a tool for AI-powered semantic memory management. It allows you to store, search, and manage memories for AI agents using a simple, robust interface.

This API is designed for developers who need to give their AI agents a reliable long-term memory. It handles the complexities of vector embeddings and LLM integration, so you can focus on building your agent's logic.

## The Problem It Solves

AI agents are often stateless. They forget everything after an interaction. This makes building sophisticated, context-aware agents difficult.

`mem0` solves this by providing a memory layer. This API exposes that layer through a clean, secure, and scalable service. It's built for real-world use, not just as a demo.

## Getting Started

You need Python 3.9+ and access to a Redis instance. You will also need an API key from an LLM provider like Google Gemini or OpenAI.

1.  **Clone the repository and install dependencies:**

    ```bash
    git clone https://github.com/OctavianTocan/mem0-api.git
    cd mem0-api
    pip install -r requirements.txt
    ```

2.  **Configure your environment.** Copy the example `.env.example` file to `.env` and fill in the required values. At a minimum, you need to set `MEMORY_API_KEY`.

    ```bash
    cp .env.example .env
    ```

3.  **Run the server.**
    ```bash
    ./start.sh
    ```
    The API will be available at `http://localhost:8000`.

## How to Use It

All endpoints require an `X-API-Key` header for authentication. This key should match the `MEMORY_API_KEY` you set in your `.env` file.

### Adding a Memory

To store information, send a `POST` request to `/add_memory`. The `messages` field contains the content to be stored.

```http
POST /add_memory
Content-Type: application/json
X-API-Key: your-secret-key

{
  "messages": [
    {"role": "user", "content": "The user's favorite food is pasta."}
  ],
  "user_id": "user-123"
}
```

The `infer` parameter, which is on by default, uses the LLM to extract and store the core facts from the content.

### Searching Memories

To retrieve information, send a `POST` request to `/search_memory`. The API performs a semantic search, so you can ask questions in natural language.

```http
POST /search_memory
Content-Type: application/json
X-API-Key: your-secret-key

{
  "query": "What is the user's favorite food?",
  "user_id": "user-123"
}
```

The API will return the most relevant memories it has stored for that user.

## Limitations

This API is a starting point. It provides core memory functions but is not a complete agent framework. It manages memory, not agent state or decision-making.

The quality of the semantic search depends heavily on the underlying embedding model. The default models are a good starting point, but you may need to experiment to find the best fit for your use case.

## Project Roadmap

This project is under active development. Future plans include:

- Support for more vector database backends.
- More sophisticated memory analysis and summarization features.
- Integration with popular agent frameworks.

Contributions are welcome.

## Project Information

This project is licensed under the MIT License. See the `LICENSE` file for details.

All contributors are expected to follow our `CODE_OF_CONDUCT.md`. Please read it before participating. Our `docs/CODING_GUIDELINES.md` outlines the standards for code contributions.
