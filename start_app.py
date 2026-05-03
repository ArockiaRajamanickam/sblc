import subprocess
import time
import sys
import os
import signal

def start_services():
    processes = []
    
    try:
        # 1. Start Backend
        print("Starting Backend (Port 8000)...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        processes.append(backend_proc)
        
        # 2. Start Frontend
        print("Starting Frontend (Port 3000)...")
        frontend_dir = os.path.join(os.getcwd(), "frontend")
        frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True # Needed for npm on Windows
        )
        processes.append(frontend_proc)
        
        print("\n" + "="*40)
        print("🚀 Application is starting!")
        print(f"Backend: http://127.0.0.1:8000")
        print(f"Frontend: http://localhost:3000")
        print("="*40)
        print("\nPress Ctrl+C to stop all services.\n")

        # Monitor processes
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"\n❌ Process {p.pid} terminated unexpectedly.")
                    return
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down services...")
    finally:
        for p in processes:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()

if __name__ == "__main__":
    start_services()
