import subprocess
import time
import sys
import os

def start_services():
    backend_log = open("backend.log", "w")
    frontend_log = open("frontend.log", "w")
    
    try:
        print("Starting Backend (Port 8000)...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "debug"],
            cwd=os.getcwd(),
            stdout=backend_log,
            stderr=backend_log,
            text=True
        )
        
        print("Starting Frontend (Port 3000)...")
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=frontend_log,
            stderr=frontend_log,
            text=True,
            shell=True
        )
        
        print("\n🚀 Services started. Logs: backend.log, frontend.log")
        print("Backend: http://127.0.0.1:8000")
        print("Frontend: http://localhost:3000")
        
        while True:
            if backend_proc.poll() is not None:
                print("❌ Backend stopped.")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend stopped.")
                break
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_log.close()
        frontend_log.close()

if __name__ == "__main__":
    start_services()
