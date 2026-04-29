"""
Enterprise App Main Module.

This module initializes the Main App Orchestrator. Bootstraps AppState, views, and layout routing
using CustomTkinter and TkinterDnD for drag and drop features.
"""
import sys
import os
import threading
import subprocess
import requests
import websocket
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.agent.file_manager_enterprise import EnterpriseFileManager
from src.agent.models.state import AppState
from src.agent.models.theme import Theme
from src.agent.views.auth_view import AuthView
from src.agent.views.home_view import HomeView
from src.agent.views.dashboard_view import DashboardView
from src.agent.views.rules_view import RulesView
from src.agent.views.help_view import HelpView

class EnterpriseApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main App Orchestrator. Bootstraps AppState, views, and layout routing."""
    
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("File Governance System")
        self.geometry("1100x850")
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Theme.BG)
        
        self.app_state = AppState()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Load Initial Authorization View
        self.auth_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_wrapper.pack(expand=True, fill="both")
        self.auth_view = AuthView(self.auth_wrapper, self.load_main_dashboard)
        self.auth_view.pack(expand=True, fill="both")

    def load_main_dashboard(self):
        """Cleanly destroys auth wrapper and bootstraps Main Layout"""
        self.auth_wrapper.destroy()
        
        self.manager = EnterpriseFileManager(self.app_state.device_id, self.app_state.api_url, self.app_state.token, self.app_state.user_email)
        self.conectar_websocket()
        
        # Layout Configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.sidebar_expanded = True
        self.sidebar_width = 240
        self.sidebar_min_width = 75
        self.is_animating = False
        
        # Transparent placeholder to reserve space in the layout engine
        self.sidebar_placeholder = ctk.CTkFrame(self, width=self.sidebar_width, fg_color="transparent", corner_radius=0)
        self.sidebar_placeholder.grid(row=0, column=0, sticky="nsew")
        
        # The content frame sits in column 1, shaped by the placeholder
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        # The actual sidebar absolute-places over the placeholder bounds
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0, fg_color=Theme.CARD)
        self.sidebar.place(x=0, y=0, relheight=1)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        self.sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_header.grid(row=0, column=0, sticky="ew", pady=(25, 30))
        self.sidebar_header.grid_columnconfigure(0, weight=1)
        
        try:
            # Replicating original behavior with an image wrapper
            logo_img = ctk.CTkImage(light_image=Image.open("assets/logo.png"), dark_image=Image.open("assets/logo.png"), size=(24, 24))
            self.lbl_logo = ctk.CTkLabel(self.sidebar_header, text=" File Sorter", image=logo_img, compound="left", font=ctk.CTkFont(size=20, weight="bold"), text_color=Theme.PRIMARY)
        except Exception:
            self.lbl_logo = ctk.CTkLabel(self.sidebar_header, text=" File Sorter", font=ctk.CTkFont(size=20, weight="bold"), text_color=Theme.PRIMARY)
        self.lbl_logo.grid(row=0, column=0, sticky="w", padx=(15, 0))
        
        self.btn_toggle = ctk.CTkButton(self.sidebar_header, text="☰", width=35, height=35, fg_color="transparent", hover_color=Theme.BORDER, text_color=Theme.TEXT, font=ctk.CTkFont(size=18), command=self.toggle_sidebar)
        self.btn_toggle.grid(row=0, column=1, sticky="e", padx=(0, 10))
        
        self.btn_nav_home = ctk.CTkButton(self.sidebar, text="  🏠  Home / Organize", font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=Theme.TEXT, hover_color=Theme.BORDER, anchor="w", height=45, corner_radius=12, command=lambda: self.select_page("home"))
        self.btn_nav_home.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        
        self.btn_nav_dash = ctk.CTkButton(self.sidebar, text="  📊  Metrics Dashboard", font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=Theme.TEXT, hover_color=Theme.BORDER, anchor="w", height=45, corner_radius=12, command=lambda: self.select_page("dash"))
        self.btn_nav_dash.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        
        self.btn_nav_rules = ctk.CTkButton(self.sidebar, text="  ⚙️  Rules Engine", font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=Theme.TEXT, hover_color=Theme.BORDER, anchor="w", height=45, corner_radius=12, command=lambda: self.select_page("rules"))
        self.btn_nav_rules.grid(row=3, column=0, padx=15, pady=10, sticky="ew")
        
        self.btn_nav_help = ctk.CTkButton(self.sidebar, text="  ❔  Documentation", font=ctk.CTkFont(size=13), fg_color="transparent", text_color=Theme.MUTED, hover_color=Theme.BORDER, anchor="w", height=45, corner_radius=12, command=lambda: self.select_page("help"))
        self.btn_nav_help.grid(row=5, column=0, padx=15, pady=20, sticky="sew")

        # Init Views directly into the layout content zone with Fall-back Protection
        try: self.page_home = HomeView(self.content_frame, self.manager)
        except Exception as e: self.page_home = ctk.CTkLabel(self.content_frame, text=f"Error rendering Home module:\n{e}", text_color=Theme.DANGER)
            
        try: self.page_dash = DashboardView(self.content_frame, self.manager)
        except Exception as e: self.page_dash = ctk.CTkLabel(self.content_frame, text=f"Error rendering Metrics module:\n{e}", text_color=Theme.DANGER)
            
        try: self.page_rules = RulesView(self.content_frame, self.manager)
        except Exception as e: self.page_rules = ctk.CTkLabel(self.content_frame, text=f"Error rendering Rules Engine module:\n{e}", text_color=Theme.DANGER)
            
        try: self.page_help = HelpView(self.content_frame)
        except Exception as e: self.page_help = ctk.CTkLabel(self.content_frame, text=f"Error rendering Documentation module:\n{e}", text_color=Theme.DANGER)
        
        self.select_page("home")

    def toggle_sidebar(self):
        if getattr(self, "is_animating", False): return
        self.is_animating = True
        
        step = 25
        if self.sidebar_expanded:
            self.sidebar_expanded = False
            self.lbl_logo.grid_forget()
            self.btn_nav_home.configure(text="  🏠  ")
            self.btn_nav_dash.configure(text="  📊  ")
            self.btn_nav_rules.configure(text="  ⚙️  ")
            self.btn_nav_help.configure(text="  ❔  ")
            
            self.sidebar_placeholder.configure(width=self.sidebar_min_width)
            self.update_idletasks()
            self._animate_sidebar_place(self.sidebar_width, self.sidebar_min_width, -step)
        else:
            self.sidebar_expanded = True
            self.lbl_logo.grid(row=0, column=0, sticky="w", padx=(15, 0))
            self._animate_sidebar_place(self.sidebar_min_width, self.sidebar_width, step)

    def _animate_sidebar_place(self, start_w, end_w, step):
        current_w = start_w
        while (step < 0 and current_w > end_w) or (step > 0 and current_w < end_w):
            current_w += step
            if step < 0 and current_w < end_w: current_w = end_w
            if step > 0 and current_w > end_w: current_w = end_w
            
            self.sidebar.configure(width=current_w)
            self.update()
            
        if self.sidebar_expanded:
            self.sidebar_placeholder.configure(width=self.sidebar_width)
            self.btn_nav_home.configure(text="  🏠  Home / Organize")
            self.btn_nav_dash.configure(text="  📊  Metrics Dashboard")
            self.btn_nav_rules.configure(text="  ⚙️  Rules Engine")
            self.btn_nav_help.configure(text="  ❔  Documentation")
            
        self.is_animating = False

    def select_page(self, name):
        """Routing multiplexer to switch active visual views"""
        self.btn_nav_home.configure(fg_color=Theme.PRIMARY if name=="home" else "transparent")
        self.btn_nav_dash.configure(fg_color=Theme.PRIMARY if name=="dash" else "transparent")
        self.btn_nav_rules.configure(fg_color=Theme.PRIMARY if name=="rules" else "transparent")
        self.btn_nav_help.configure(fg_color=Theme.PRIMARY if name=="help" else "transparent")

        self.page_home.pack_forget()
        self.page_dash.pack_forget()
        self.page_rules.pack_forget()
        self.page_help.pack_forget()

        if name == "home": self.page_home.pack(fill="both", expand=True)
        elif name == "dash":
            if hasattr(self.page_dash, 'actualizar'): self.page_dash.actualizar()
            self.page_dash.pack(fill="both", expand=True)
        elif name == "rules":
            if hasattr(self.page_rules, 'actualizar'): self.page_rules.actualizar()
            self.page_rules.pack(fill="both", expand=True)
        elif name == "help": self.page_help.pack(fill="both", expand=True)


    def conectar_websocket(self):
        def run():
            ws_url = self.app_state.api_url.replace("http://", "ws://").replace("https://", "wss://") + f"/ws/events/{self.app_state.device_id}"
            try:
                self.ws = websocket.WebSocketApp(ws_url, on_message=lambda ws, m: print(f"Cloud: {m}"))
                self.manager.ws = self.ws
                self.ws.run_forever()
            except Exception as e: print(e)
        threading.Thread(target=run, daemon=True).start()

    def on_close(self):
        """Graciously shuts down background hooks before native exit."""
        if hasattr(self, 'page_home') and hasattr(self.page_home, 'observer'):
            try:
                self.page_home.observer.stop()
                self.page_home.observer.join()
            except: pass
            
        if self.app_state.backend_pid:
            try:
                subprocess.run(f"taskkill /PID {self.app_state.backend_pid} /T /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
            
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = EnterpriseApp()
    app.mainloop()