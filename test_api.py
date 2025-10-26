import asyncio
import os
import requests
import subprocess
import time

API_KEY = "test-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY}

def start_server():
    """Starts the uvicorn server as a subprocess."""
    env = os.environ.copy()
    env["MEMORY_API_KEY"] = API_KEY
    env["PORT"] = "8000"
    env["GOOGLE_API_KEY"] = "test-key"
    return subprocess.Popen(["uvicorn", "mem0_api:app", "--host", "0.0.0.0", "--port", "8000"], env=env)

def wait_for_server(url, timeout=20):
    """Waits for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is ready.")
                return True
        except requests.ConnectionError:
            time.sleep(0.5)
    print("Server failed to start.")
    return False

def test_endpoint(endpoint, method="post", json=None):
    """Tests a single endpoint."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "post":
            response = requests.post(url, headers=HEADERS, json=json)
        else:
            response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        print(f"SUCCESS: {method.upper()} {endpoint} - {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"FAILURE: {method.upper()} {endpoint} - {e}")
        return None

def main():
    """Main function to run the tests."""
    server_process = start_server()

    if not wait_for_server(f"{BASE_URL}/"):
        server_process.terminate()
        return

    # Test endpoints
    test_endpoint("/", method="get")
    test_endpoint("/ping")
    add_memory_data = {
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "user_id": "test_user"
    }
    test_endpoint("/add_memory", json=add_memory_data)
    search_data = {"query": "Hello", "user_id": "test_user"}
    test_endpoint("/search_memory", json=search_data)
    get_all_data = {"user_id": "test_user"}
    test_endpoint("/get_all_memories", json=get_all_data)
    test_endpoint("/delete_all_memories")

    # Stop the server
    server_process.terminate()
    server_process.wait()

if __name__ == "__main__":
    main()
