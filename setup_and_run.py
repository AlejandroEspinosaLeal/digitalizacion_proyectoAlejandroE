import os
import sys
import time
import subprocess
import secrets
from pathlib import Path
import customtkinter as ctk
from PIL import Image

# Core dependencies explicitly required if the user wishes to run the application securely
DEPENDENCIES = [
    "fastapi", "uvicorn[standard]", "sqlmodel", "pydantic-settings",
    "passlib[bcrypt]", "bcrypt", "python-jose[cryptography]", "python-multipart",
    "psycopg2-binary", "redis", "requests", "websocket-client",
    "customtkinter", "watchdog", "pystray", "pillow", "tkinterdnd2", "jinja2",
    "pytest", "pytest-asyncio", "httpx"
]

def get_current_db_type():
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "postgresql" in content:
            return "docker"
    return "sqlite"

def setup_environment(db_type="sqlite"):
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
    env_vars["DATABASE_URL"] = "postgresql://postgres:admin@localhost:5432/filesorter_db" if db_type == "docker" else "sqlite:///./enterprise.db"
    if "REDIS_HOST" not in env_vars: env_vars["REDIS_HOST"] = "localhost"
    if "REDIS_PORT" not in env_vars: env_vars["REDIS_PORT"] = "6379"

    env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()]) + "\n"
    env_path.write_text(env_content)

class EnterpriseLauncher(ctk.CTk):
    """
    Main entrypoint GUI orchestration class ensuring that the Python environment
    contains identical absolute paths and correctly traps the standard output streams
    of child subprocesses to prevent invisible blocking crashes.
    """
    def __init__(self):
        super().__init__()
        self.title("Enterprise Launcher")
        self.geometry("380x520")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#09090B")
        self.c_card = "#121215"
        self.c_border = "#27272A"
        self.c_primary = "#E03131"
        self.c_hover = "#C92A2A"
        self.c_success = "#2F9E44"
        self.c_text = "#F8F9FA"
        
        self.db_var = ctk.StringVar(value=get_current_db_type())
        setup_environment(self.db_var.get())
        
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = os.getcwd()
        
        self.procesos = []
        
        self.crear_interfaz()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_todo)

    def crear_interfaz(self):
        """Builds the actual interactive graphical overlay displaying the deployment toggles."""
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("assets/logo.png"), dark_image=Image.open("assets/logo.png"), size=(40, 40))
            ctk.CTkLabel(self, text=" File Sorter", image=logo_img, compound="left", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.c_text).pack(pady=(30, 5))
        except Exception:
            ctk.CTkLabel(self, text="File Sorter", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.c_text).pack(pady=(30, 5))
        ctk.CTkLabel(self, text="Control Center", font=ctk.CTkFont(size=14), text_color="#9CA3AF").pack(pady=(0, 20))
        
        # DB Configuration
        db_frame = ctk.CTkFrame(self, fg_color="transparent")
        db_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(db_frame, text="Backend Env:", text_color=self.c_text, font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        def on_db_change():
            setup_environment(self.db_var.get())
            if self.db_var.get() == "docker":
                self.btn_docker.pack(fill="x", padx=20, pady=(20, 0))
            else:
                self.btn_docker.pack_forget()
                
        ctk.CTkRadioButton(db_frame, text="Local (SQLite)", variable=self.db_var, value="sqlite", command=on_db_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(db_frame, text="Docker (PG)", variable=self.db_var, value="docker", command=on_db_change).pack(side="left")

        wrapper = ctk.CTkFrame(self, fg_color=self.c_card, corner_radius=16, border_width=1, border_color=self.c_border)
        wrapper.pack(padx=30, fill="both", expand=True, pady=(0, 30))
        
        self.btn_docker = ctk.CTkButton(wrapper, text="Deploy Database (Docker)", height=40, corner_radius=12, fg_color="#F59E0B", hover_color="#D97706", command=self.lanzar_docker)
        
        self.btn_1 = ctk.CTkButton(wrapper, text="Deploy Uvicorn Server", height=40, corner_radius=12, fg_color="transparent", border_width=1, border_color=self.c_border, hover_color=self.c_border, command=self.lanzar_servidor)
        self.btn_1.pack(fill="x", padx=20, pady=(20, 10))
        
        self.btn_2 = ctk.CTkButton(wrapper, text="Deploy Standalone UI", height=40, corner_radius=12, fg_color="transparent", border_width=1, border_color=self.c_border, hover_color=self.c_border, command=self.lanzar_agente)
        self.btn_2.pack(fill="x", padx=20, pady=10)
        
        self.btn_3 = ctk.CTkButton(wrapper, text="Launch Full System Node", height=50, corner_radius=12, fg_color=self.c_primary, hover_color=self.c_hover, font=ctk.CTkFont(weight="bold"), command=self.lanzar_ambos)
        self.btn_3.pack(fill="x", padx=20, pady=(10, 20))
        
        self.status = ctk.CTkLabel(self, text="", text_color=self.c_success, font=ctk.CTkFont(size=12))
        self.status.pack(side="bottom", pady=10)
        
        on_db_change()

    def lanzar_docker(self):
        self.status.configure(text="Booting Docker containers...")
        self.update()
        subprocess.Popen(["docker-compose", "up", "-d"], env=self.env, creationflags=0x08000000)
        self.status.configure(text="Containers running in the background.")

    def lanzar_servidor(self):
        self._bloquear_botones()
        self.status.configure(text="Starting Server...")
        self.update()
        subprocess.Popen([sys.executable, "-m", "uvicorn", "src.backend.main:app", "--port", "8000"], env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        self.after(1000, self.destroy)

    def lanzar_agente(self):
        self._bloquear_botones()
        self.status.configure(text="Starting Frontend Agent...")
        self.update()
        subprocess.Popen([sys.executable, "src/agent/main_enterprise.py"], env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        self.after(1000, self.destroy)

    def lanzar_ambos(self):
        self._bloquear_botones()
        self.status.configure(text="🚀 Initiating Full System...")
        self.update()
        
        p1 = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.backend.main:app", "--port", "8000"], env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        
        def spawn_frontend():
            subprocess.Popen([sys.executable, "src/agent/main_enterprise.py", "--backend-pid", str(p1.pid)], env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            self.after(1000, self.destroy)
            
        self.after(1500, spawn_frontend)

    def _bloquear_botones(self):
        self.btn_1.configure(state="disabled")
        self.btn_2.configure(state="disabled")
        self.btn_3.configure(state="disabled")
        if hasattr(self, "btn_docker"):
            self.btn_docker.configure(state="disabled")

    def cerrar_todo(self):
        for p in self.procesos:
            try:
                p.terminate()
                p.wait(timeout=2)
            except: pass
        self.destroy()

if __name__ == "__main__":
    app = EnterpriseLauncher()
    app.mainloop()