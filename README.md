# mem0-railway-git Utilities

This directory contains utility scripts for testing and interacting with the mem0 memory server.

## Script: `check_mem0_server.py`

A command-line tool to test, reset, search, and save memories for a specified user on the mem0 server.

### Requirements
- Python 3.7+
- `requests` library (install with `pip install requests`)
- `python-dotenv` library (install with `pip install python-dotenv`) if you want to use a `.env` file for the API key

### Usage

Run the script with one of the following commands. The `--user` argument is required for all commands. The `--api-key` argument is optional: if not provided, the script will load the API key from the `.env` file (`MEMORY_API_KEY`).

```sh
python check_mem0_server.py <command> --user <user_id> [--api-key <your_api_key>] [--query "search term"]
```

Alternatively, set your API key in a `.env` file in the same directory:

```
MEMORY_API_KEY=sk-...yourkey...
```

#### Commands

- `reset`  
  Delete (reset) all memories for the specified user.
  
  Example with API key as argument:
  ```sh
  python check_mem0_server.py reset --user alice --api-key sk-...yourkey...
  ```
  Example with API key in `.env`:
  ```sh
  python check_mem0_server.py reset --user alice
  ```

- `save`  
  Fetch all memories for the specified user and save them to `memories/all_memories.json`.
  
  Example:
  ```sh
  python check_mem0_server.py save --user alice --api-key sk-...yourkey...
  # or
  python check_mem0_server.py save --user alice
  ```

- `search`  
  Search for a specific query string in all memories for the specified user. Requires `--query` argument.
  
  Example:
  ```sh
  python check_mem0_server.py search --user alice --api-key sk-...yourkey... --query "hello"
  # or
  python check_mem0_server.py search --user alice --query "hello"
  ```

- `add`  
  Add a test memory ("Hello, world!") for the specified user and then clean it up.
  
  Example:
  ```sh
  python check_mem0_server.py add --user alice --api-key sk-...yourkey...
  # or
  python check_mem0_server.py add --user alice
  ```

- `getall`  
  Fetch and print all memories for the specified user, and save them to `memories/all_memories.json`.
  
  Example:
  ```sh
  python check_mem0_server.py getall --user alice --api-key sk-...yourkey...
  # or
  python check_mem0_server.py getall --user alice
  ```

### Notes
- The script interacts with the remote mem0 server at `https://databases.memory.octaviantocan.com`.
- Saved memories are stored in the `memories/` directory as `all_memories.json`.
- If neither `--api-key` nor a `.env` file with `MEMORY_API_KEY` is provided, the script will exit with an error.

---

Feel free to modify or extend the script for your own testing needs. 