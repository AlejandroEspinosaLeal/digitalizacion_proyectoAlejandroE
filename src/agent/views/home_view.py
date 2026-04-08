import os
import threading
from tkinter import filedialog
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.agent.models.theme import Theme
from src.agent.models.state import AppState
from src.agent.services.api_client import APIClient

class HomeView(ctk.CTkScrollableFrame):
    """
    Main operations view. Exposes the Drag & Drop mechanics to process directories,
    set exclusion filters, rules, background watching, and dispatching API file sync events.
    """
    def __init__(self, master, file_manager):
        super().__init__(master, fg_color="transparent")
        self.manager = file_manager
        self.app_state = AppState()
        self.api = APIClient()
        self.last_log_time = 0
        self.log_queue_str = ""
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(header, text="Drag & Drop Processing", font=ctk.CTkFont(size=28, weight="bold"), text_color=Theme.TEXT).pack(side="left")
        
        f1 = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=16, border_width=1, border_color=Theme.BORDER)
        f1.pack(fill="x", padx=40, pady=(0, 20))
        ctk.CTkLabel(f1, text="Source Directory (Drag folder or click)", font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.TEXT).pack(anchor="w", padx=25, pady=(20, 5))
        
        self.lbl_origen = ctk.CTkLabel(f1, text="📁 Drag files here...", font=ctk.CTkFont(size=15), text_color=Theme.MUTED, fg_color=Theme.INPUT, corner_radius=12, cursor="hand2")
        self.lbl_origen.pack(fill="x", padx=25, pady=(5, 25), ipady=25)
        self.lbl_origen.bind("<Button-1>", self.select_origen_manual)
        
        self.lbl_origen.drop_target_register(DND_FILES)
        self.lbl_origen.dnd_bind('<<Drop>>', self.drop_origen)

        f2 = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=16, border_width=1, border_color=Theme.BORDER)
        f2.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(f2, text="Category Filters", font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.TEXT).pack(anchor="w", padx=25, pady=(20, 10))
        
        grid_cats = ctk.CTkFrame(f2, fg_color="transparent")
        grid_cats.pack(fill="x", padx=25, pady=(0, 25))
        
        categorias = ["Documents", "Images", "Audio Video", "Compressed", "Executables Installers", "Web Dev Code", "Fonts", "3D CAD Design", "Databases", "System Backups", "Others", ""]
        self.chk_cats = {}
        for i, cat in enumerate(categorias):
            if cat:
                var = ctk.BooleanVar(value=True)
                chk = ctk.CTkCheckBox(grid_cats, text=cat, variable=var, font=ctk.CTkFont(size=13), text_color=Theme.MUTED, fg_color=Theme.PRIMARY, hover_color=Theme.PRIMARY_HOVER, border_color=Theme.BORDER)
                chk.grid(row=i//3, column=i%3, sticky="w", pady=12, padx=10)
                grid_cats.grid_columnconfigure(i%3, weight=1)
                self.chk_cats[cat] = var

        f3 = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=16, border_width=1, border_color=Theme.BORDER)
        f3.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(f3, text="Organization Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.TEXT).pack(anchor="w", padx=25, pady=(20, 10))
        
        self.entry_ignore = ctk.CTkEntry(f3, placeholder_text="Exclusiones separated by comma (e.g., draft, private)", height=45, fg_color=Theme.INPUT, border_color=Theme.BORDER, text_color=Theme.TEXT)
        self.entry_ignore.pack(fill="x", padx=25, pady=(0, 20))
        
        opts_grid = ctk.CTkFrame(f3, fg_color="transparent")
        opts_grid.pack(fill="x", padx=25, pady=(0, 25))
        
        self.sw_simulacro = ctk.CTkSwitch(opts_grid, text="Dry Run Mode", progress_color=Theme.PRIMARY, text_color=Theme.TEXT)
        self.sw_simulacro.grid(row=0, column=0, sticky="w", pady=15)
        self.sw_subcarpetas = ctk.CTkSwitch(opts_grid, text="Deep Scan Subfolders", progress_color=Theme.PRIMARY, text_color=Theme.TEXT)
        self.sw_subcarpetas.grid(row=0, column=1, sticky="w", pady=15)
        self.sw_year_month = ctk.CTkSwitch(opts_grid, text="Create Year/Month folders", progress_color=Theme.PRIMARY, text_color=Theme.TEXT)
        self.sw_year_month.grid(row=1, column=0, sticky="w", pady=15)
        self.sw_vigia = ctk.CTkSwitch(opts_grid, text="Continuous Watcher (Background)", command=self.toggle_vigia, progress_color=Theme.PRIMARY, text_color=Theme.TEXT)
        self.sw_vigia.grid(row=1, column=1, sticky="w", pady=15)
        opts_grid.grid_columnconfigure((0,1), weight=1)

        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(fill="x", padx=40, pady=30, side="bottom")
        
        self.btn_run = ctk.CTkButton(self.actions, text="🚀 Start Organization", font=ctk.CTkFont(size=16, weight="bold"), fg_color=Theme.SUCCESS, hover_color=Theme.SUCCESS_HOVER, text_color="white", height=60, corner_radius=15, command=self.ejecutar_organizacion)
        self.btn_run.pack(side="left", expand=True, fill="x", padx=(0, 15))
        
        self.progress_bar = ctk.CTkProgressBar(self.actions, width=150, progress_color=Theme.PRIMARY, mode="indeterminate")
        self.progress_bar.set(0)
        
        self.btn_undo = ctk.CTkButton(self.actions, text="⏪ Undo Batch", font=ctk.CTkFont(size=14, weight="bold"), fg_color=Theme.DANGER, hover_color="#B91C1C", text_color="white", height=60, corner_radius=15, width=150, command=self.ejecutar_deshacer)
        self.btn_undo.pack(side="left", padx=15)
        
        self.status_bar = ctk.CTkLabel(self.actions, text="Inactive.", text_color=Theme.MUTED, font=ctk.CTkFont(size=14))
        self.status_bar.pack(side="right", padx=10)

    def select_origen_manual(self, event=None):
        folder = filedialog.askdirectory()
        if folder:
            self.app_state.monitor_folder = folder
            self.lbl_origen.configure(text=f"📁 {folder}")

    def drop_origen(self, event):
        folder = event.data.strip('{}')
        if os.path.exists(folder):
            self.app_state.monitor_folder = folder
            self.lbl_origen.configure(text=f"📁 {folder}")

    def toggle_vigia(self):
        if self.sw_vigia.get():
            if not self.app_state.monitor_folder:
                self.status_bar.configure(text="Select source first.", text_color=Theme.DANGER)
                self.sw_vigia.deselect()
                return
            class Handler(FileSystemEventHandler):
                def __init__(self, view): self.view = view
                def on_modified(self, event):
                    if not event.is_directory:
                        cats, ops = self.view.get_opciones()
                        ops["dry_run"] = False
                        self.view.manager.procesar_lote(self.view.state.monitor_folder, cats, ops, self.view.log_message)
                def on_created(self, event):
                    if not event.is_directory:
                        cats, ops = self.view.get_opciones()
                        ops["dry_run"] = False
                        self.view.manager.procesar_lote(self.view.state.monitor_folder, cats, ops, self.view.log_message)

            self.observer = Observer()
            self.observer.schedule(Handler(self), self.app_state.monitor_folder, recursive=False)
            self.observer.start()
            self.status_bar.configure(text=f"Watching in background...", text_color=Theme.PRIMARY)
        else:
            if hasattr(self, 'observer'):
                self.observer.stop()
                self.observer.join()
                self.status_bar.configure(text="Watcher mode disabled.", text_color=Theme.MUTED)

    def log_message(self, msg):
        import time
        now = time.time()
        self.log_queue_str = msg[:60]
        if now - self.last_log_time > 0.1:
            self.last_log_time = now
            self.after(0, lambda m=self.log_queue_str: self.status_bar.configure(text=m, text_color=Theme.MUTED))

    def get_opciones(self):
        cats = [cat for cat, var in self.chk_cats.items() if var.get()]
        ops = {"dry_run": self.sw_simulacro.get() == 1, "escanear_subcarpetas": self.sw_subcarpetas.get() == 1, "crear_carpetas_fecha": self.sw_year_month.get() == 1, "exclusiones": self.entry_ignore.get()}
        return cats, ops

    def ejecutar_organizacion(self):
        if not self.app_state.monitor_folder:
            self.status_bar.configure(text="Warning: Select folder.", text_color=Theme.DANGER)
            return
            
        self.btn_run.configure(state="disabled", text="Organizing...", fg_color=Theme.PRIMARY)
        self.btn_undo.pack_forget()
        self.progress_bar.pack(side="left", padx=15)
        self.progress_bar.start()
        
        threading.Thread(target=self._task_organizacion, daemon=True).start()

    def _task_organizacion(self):
        folder = self.app_state.monitor_folder
        cats, ops = self.get_opciones()
        try:
            m_log = self.manager.procesar_lote(folder, cats, ops, self.log_message)
            self.api.send_log_report(m_log)
            self.status_bar.configure(text=f"Success! Operation synchronized.", text_color=Theme.SUCCESS)
        except Exception as e:
            msg = str(e)
            if "Backend offine" in msg:
                self.status_bar.configure(text="Disconnected. Offline report successful.", text_color=Theme.SUCCESS)
            else:
                self.status_bar.configure(text=f"Local error: {msg}", text_color=Theme.DANGER)
        finally:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.btn_run.configure(state="normal", text="🚀 Start Organization", fg_color=Theme.SUCCESS)
            self.btn_undo.pack(side="left", padx=15)

    def ejecutar_deshacer(self):
        self.btn_undo.configure(state="disabled", text="Undoing...")
        def rollback():
            try:
                exito = self.manager.deshacer_ultimo(self.log_message)
                if exito: self.status_bar.configure(text="Successful Rollback", text_color=Theme.SUCCESS)
                self.btn_undo.configure(state="normal", text="⏪ Undo Batch")
            except Exception as e:
                self.log_message(f"Undo Error: {e}")
                self.btn_undo.configure(state="normal", text="⏪ Undo Batch")
        threading.Thread(target=rollback, daemon=True).start()
