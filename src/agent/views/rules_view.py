import customtkinter as ctk
from src.agent.models.theme import Theme
from src.agent.views.apple_components import AppleHeading, AppleCard, AppleInput, AppleButton, AppleSubText

class RulesView(ctk.CTkScrollableFrame):
    """
    Configuration panel enabling users to attach custom logic keywords to file extensions.
    Rules defined here overwrite automatic general categorical sorting behavior.
    """
    def __init__(self, master, file_manager):
        super().__init__(master, fg_color="transparent")
        self.manager = file_manager
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        AppleHeading(header, text="Automata and Local Rules", size=28).pack(side="left")
        
        creator = AppleCard(self)
        creator.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(creator, text="Add Logic", font=ctk.CTkFont(family="Helvetica", size=15, weight="bold")).pack(anchor="w", padx=25, pady=(20, 10))
        row = ctk.CTkFrame(creator, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=(0, 25))
        
        self.r_ext = AppleInput(row, placeholder_text=".pdf", width=80)
        self.r_ext.pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text="  +  ").pack(side="left")
        self.r_kw = AppleInput(row, placeholder_text="Keyword", width=150)
        self.r_kw.pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text="  🡆  ").pack(side="left")
        self.r_cat = AppleInput(row, placeholder_text="Destination Folder", width=150)
        self.r_cat.pack(side="left", padx=5)
        
        AppleButton(row, text="Save Rule", variant="success", command=self.add_rule, height=45).pack(side="right", padx=5)
        
        self.rules_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.rules_grid.pack(fill="both", expand=True, padx=40, pady=20)

    def actualizar(self):
        for w in self.rules_grid.winfo_children(): w.destroy()
        for i, r in enumerate(self.manager.custom_rules):
            c = ctk.CTkFrame(self.rules_grid, fg_color=Theme.INPUT, height=45, corner_radius=12)
            c.pack(fill="x", pady=4)
            t = f"📄 {r['ext']}   |   Contains: '{r['key']}'   🡆   📂 {r['cat']}"
            ctk.CTkLabel(c, text=t, text_color=Theme.TEXT, font=ctk.CTkFont(family="Helvetica", size=13)).pack(side="left", padx=15, pady=8)
            AppleButton(c, text="X", width=35, height=35, corner_radius=8, variant="danger", command=lambda idx=i: self.del_rule(idx)).pack(side="right", padx=10, pady=8)

    def add_rule(self):
        ext = self.r_ext.get().strip()
        kw = self.r_kw.get().strip()
        cat = self.r_cat.get().strip()
        if ext and cat:
            self.manager.guardar_regla_custom(ext, kw, cat)
            self.r_ext.delete(0, "end"); self.r_kw.delete(0, "end"); self.r_cat.delete(0, "end")
            self.actualizar()

    def del_rule(self, idx):
        self.manager.borrar_regla_custom(idx)
        self.actualizar()
