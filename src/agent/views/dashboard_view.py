import customtkinter as ctk
from src.agent.models.theme import Theme

class DashboardView(ctk.CTkScrollableFrame):
    """
    Statistical metrics view displaying real-time feedback on organized files
    and sorting volumes separated by system-recognized categories.
    """
    def __init__(self, master, file_manager):
        super().__init__(master, fg_color="transparent")
        self.manager = file_manager
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(header, text="System Metrics", font=ctk.CTkFont(size=28, weight="bold"), text_color=Theme.TEXT).pack(side="left")
        
        self.lbl_t_archivos = ctk.CTkLabel(self, text="0 Organized Files", font=ctk.CTkFont(size=38, weight="bold"), text_color=Theme.PRIMARY)
        self.lbl_t_archivos.pack(pady=40)
        
        self.dash_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.dash_grid.pack(fill="both", expand=True, padx=40)

    def actualizar(self):
        h = self.manager.historial
        total = h.get("total_archivos", 0)
        self.lbl_t_archivos.configure(text=f"{total:,} Automated Files".replace(",", "."))
        
        for w in self.dash_grid.winfo_children(): w.destroy()
        
        import os
        cats = sorted(h.get("por_categoria", {}).items(), key=lambda x: -x[1])
        for i, (cat, qty) in enumerate(cats):
            card = ctk.CTkFrame(self.dash_grid, fg_color=Theme.CARD, corner_radius=16, border_color=Theme.BORDER, border_width=1)
            card.pack(fill="x", pady=5)
            
            header = ctk.CTkFrame(card, fg_color="transparent", height=45, cursor="hand2")
            header.pack(fill="x")
            
            lbl_cat = ctk.CTkLabel(header, text=f"📂 {cat}", font=ctk.CTkFont(size=15), cursor="hand2")
            lbl_cat.pack(side="left", padx=20, pady=10)
            
            lbl_qty = ctk.CTkLabel(header, text=f"{qty:,}".replace(",", "."), font=ctk.CTkFont(size=15, weight="bold"), text_color=Theme.SUCCESS, cursor="hand2")
            lbl_qty.pack(side="right", padx=20, pady=10)
            
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            
            archivos_cat = []
            for m in self.manager.ultimo_movimiento:
                path_parts = m.get("destino_real", "").replace("\\", "/").split("/")
                if cat in path_parts:
                    archivos_cat.append(m["file"])
                elif self.manager.obtener_carpeta_destino(os.path.splitext(m["file"])[1]) == cat:
                    archivos_cat.append(m["file"])
                    
            archivos_cat = list(dict.fromkeys(archivos_cat))
            
            if archivos_cat:
                for arch in archivos_cat:
                    ctk.CTkLabel(details_frame, text=f"📄 {arch}", font=ctk.CTkFont(size=12), text_color=Theme.MUTED).pack(anchor="w", padx=40, pady=2)
            else:
                ctk.CTkLabel(details_frame, text="No recent files from this session", font=ctk.CTkFont(size=12, slant="italic"), text_color=Theme.MUTED).pack(anchor="w", padx=40, pady=2)
                
            def toggle_details(event, df=details_frame):
                if df.winfo_ismapped():
                    df.pack_forget()
                else:
                    df.pack(fill="x", pady=(0, 10))
                    
            header.bind("<Button-1>", toggle_details)
            lbl_cat.bind("<Button-1>", toggle_details)
            lbl_qty.bind("<Button-1>", toggle_details)
