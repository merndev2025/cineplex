import subprocess
import sys
import os
import time
import signal
import platform
import webbrowser

def is_windows():
    return platform.system().lower() == "windows"

def run_servers():
    try:
        # Change working directory to project root
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("Starting Movie Recommendation System Servers...")
        
        # Configure commands based on OS
        if is_windows():
            backend_cmd = "python -m uvicorn app.main:app --reload --port 8000"
            frontend_cmd = "python -m http.server 8080"
            shell = True
            flags = subprocess.CREATE_NEW_CONSOLE
        else:
            backend_cmd = ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
            frontend_cmd = ["python3", "-m", "http.server", "8080"]
            shell = False
            flags = 0
            # Create new terminal windows for Linux
            if os.environ.get('DISPLAY'):  # Check if running in GUI mode
                terminal = os.environ.get('TERMINAL', 'xterm')
                backend_cmd = ["xterm", "-e", f"cd backend && {' '.join(' '.join(backend_cmd))}; bash"]
                frontend_cmd = ["xterm", "-e", f"cd frontend && {' '.join(' '.join(frontend_cmd))}; bash"]
        
        # Start Backend Server
        backend_process = subprocess.Popen(
            backend_cmd, 
            cwd="backend",
            shell=shell,
            creationflags=flags if is_windows() else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to initialize
        print("Waiting for backend to initialize...")
        time.sleep(5)
        
        # Check if backend process has crashed
        if backend_process.poll() is not None:
            stdout, stderr = backend_process.communicate()
            print(f"Backend server failed to start. Error:\n{stderr.decode()}")
            return
        
        # Start Frontend Server
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd="frontend",
            shell=shell,
            creationflags=flags if is_windows() else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("\nServers started successfully!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:8080")
        
        # Open browsers automatically
        if os.environ.get('DISPLAY') or is_windows():  # Only open if in GUI mode
            print("\nOpening browsers...")
            webbrowser.open('http://localhost:8080')
            webbrowser.open('http://localhost:8000/docs')  # Open API docs
        
        print("\nPress Ctrl+C to stop both servers...")
        
        # Keep the script running and monitor processes
        while True:
            if backend_process.poll() is not None:
                print("\nBackend server crashed! Shutting down...")
                break
            if frontend_process.poll() is not None:
                print("\nFrontend server crashed! Shutting down...")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        # Cleanup
        if not is_windows():
            try:
                os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
            except ProcessLookupError:
                print("Backend process not found.")
            try:
                os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)
            except ProcessLookupError:
                print("Frontend process not found.")
        else:
            subprocess.run("taskkill /F /T /PID %d" % backend_process.pid, shell=True)
            subprocess.run("taskkill /F /T /PID %d" % frontend_process.pid, shell=True)
        print("Servers stopped.")
        sys.exit(0)

if __name__ == "__main__":
    import platform
    if not is_windows() and os.getenv('DISPLAY') is None:
        print("Warning: Running in non-GUI mode. Servers will run in current terminal.")
    run_servers()