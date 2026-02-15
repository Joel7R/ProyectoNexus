import requests
import time
import subprocess
import sys
import os

def run_server():
    """Starts the server in a subprocess."""
    print("Starting server...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() # Ensure root is in pythonpath
    
    process = subprocess.Popen(
        [sys.executable, "server/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    return process

def check_health():
    """Checks the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("Health Check: PASSED")
            print(response.json())
            return True
        else:
            print(f"Health Check: FAILED (Status {response.status_code})")
            return False
    except Exception as e:
        print(f"Health Check: FAILED ({e})")
        return False

def check_llm():
    """Checks the LLM chat endpoint (mock or real)."""
    try:
        payload = {"message": "Hola, esto es una prueba."}
        # Note: The stream endpoint returns an event stream, so we just check connection
        # For simplicity in this script, we'll just check if it accepts the connection
        # or use a non-streaming check if available.
        # Since we only implemented stream, we can try to connect and read the first chunk.
        
        with requests.post("http://localhost:8000/api/chat/stream", json=payload, stream=True) as r:
            if r.status_code == 200:
                 print("Chat Stream: CONNECTION PASSED")
                 for line in r.iter_lines():
                     if line:
                         print(f"Chat Stream Output: {line.decode('utf-8')[:100]}...")
                         break
                 return True
            else:
                 print(f"Chat Stream: FAILED (Status {r.status_code})")
                 return False
    except Exception as e:
        print(f"Chat Stream: FAILED ({e})")
        return False

def main():
    # Start server
    server_process = run_server()
    
    # Wait for startup
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Run checks
    print("\n--- RUNNING CHECKS ---")
    health_passed = check_health()
    llm_passed = check_llm()
    
    print("\n--- RESULTS ---")
    if health_passed and llm_passed:
        print("VERIFICATION SUCCESSFUL: Server is running and endpoints are accessible.")
    else:
        print("VERIFICATION FAILED: Issues detected.")
    
    # Kill server
    print("\nStopping server...")
    server_process.terminate()
    try:
        outs, errs = server_process.communicate(timeout=5)
        print("Server Output:\n", outs)
        print("Server Errors:\n", errs)
    except:
        server_process.kill()

if __name__ == "__main__":
    main()
