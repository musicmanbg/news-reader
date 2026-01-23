import subprocess
import time
import requests
import pytest
import os

def test_cloud_function_emulator():
    """
    Integration test that starts the functions-framework emulator and verifies
    that the scrape_news_http function responds with a 200 OK and a JSON list.
    """
    port = "8081"
    # Start the emulator in a background process
    # Using 'python -m' to ensure we use the correct environment
    process = subprocess.Popen(
        ["poetry", "run", "functions-framework", "--target=scrape_news_http", "--source=src/news_reader/main.py", "--port", port],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    try:
        # Give the server some time to start
        time.sleep(5)
        
        # Make a request to the local emulator
        response = requests.get(f"http://localhost:{port}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"\nIntegration test passed! Received {len(data)} articles.")
        
    finally:
        # Ensure the process is killed
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            process.terminate()
