import os
import sys
import time
import subprocess
import secrets
from pathlib import Path

# Core dependencies explicitly required if the user wishes to run the application securely
DEPENDENCIES = [
    "fastapi", "uvicorn[standard]", "sqlmodel", "pydantic-settings",
    "passlib[bcrypt]", "bcrypt", "python-jose[cryptography]", "python-multipart",
    "psycopg2-binary", "redis", "requests", "websocket-client",
    "customtkinter", "watchdog", "pystray", "pillow", "tkinterdnd2", "jinja2",
    "pytest", "pytest-asyncio", "httpx"
]

def setup_environment():
    """Bootstraps a local .env configuration script preserving user keys and network port pointers."""
    env_path = Path(".env")
    
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
                
    if "SECRET_KEY" not in env_vars:
        env_vars["SECRET_KEY"] = secrets.token_hex(32)
        
    env_vars["PROJECT_NAME"] = '"File Sorter Enterprise"'
    env_vars["ALGORITHM"] = "HS256"
    
    # Supabase Native Configuration
    if "SUPABASE_URL" not in env_vars:
        env_vars["SUPABASE_URL"] = "PON_TU_SUPABASE_URL_AQUI"
    if "SUPABASE_ANON_KEY" not in env_vars:
        env_vars["SUPABASE_ANON_KEY"] = "PON_TU_ANON_KEY_AQUI"
    
    # If the user has not injected DATABASE_URL, defaults to local SQLite.
    # User is expected to put their Supabase URL directly into .env
    if "DATABASE_URL" not in env_vars:
        env_vars["DATABASE_URL"] = "sqlite:///./enterprise.db"
        
    if "REDIS_HOST" not in env_vars: env_vars["REDIS_HOST"] = "localhost"
    if "REDIS_PORT" not in env_vars: env_vars["REDIS_PORT"] = "6379"

    env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()]) + "\n"
    env_path.write_text(env_content)
    return env_vars

def main():
    setup_environment()
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    print("--------------------------------------------------")
    print("[INFO] Booting FastAPI Backend Server...")
    # Hide the backend uvicorn console window via 0x08000000 creation flag so it stays stealthy
    p1 = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.backend.main:app", "--port", "8000"],
                          env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    
    # Wait for socket to properly open before agent initialization
    time.sleep(2)
    
    print("[INFO] Booting File Governance System GUI...")
    # Boot the frontend login screen (Native desktop application)
    p2 = subprocess.Popen([sys.executable, "src/agent/main_enterprise.py", "--backend-pid", str(p1.pid)],
                          env=env, creationflags=0x08000000)
    
    try:
        # Prevent the runner script from evaluating termination logic until physical app window is closed
        p2.wait()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            p1.terminate()
            p1.wait(timeout=2)
            print("Server shut down.")
        except Exception:
            pass

if __name__ == "__main__":
    main()