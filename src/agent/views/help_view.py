import customtkinter as ctk
from src.agent.models.theme import Theme
from src.agent.views.apple_components import AppleCard, AppleHeading, AppleSubText

class HelpView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", bg_color="transparent", **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.language = "Español"
        
        # Header Area
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = AppleHeading(header_frame, text="Manual de Usuario - Enterprise")
        self.lbl_title.grid(row=0, column=0, sticky="w")
        
        self.seg_lang = ctk.CTkSegmentedButton(
            header_frame, 
            values=["Español", "English"], 
            command=self.cambiar_idioma, 
            selected_color=Theme.PRIMARY, 
            selected_hover_color=Theme.PRIMARY_HOVER, 
            unselected_color=Theme.CARD, 
            unselected_hover_color=Theme.BORDER
        )
        self.seg_lang.grid(row=0, column=1, sticky="e")
        self.seg_lang.set("Español")
        
        # Content Areas inside Cards
        self.card_1 = AppleCard(self)
        self.card_1.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.lbl_h1 = AppleHeading(self.card_1, text="1. Panel de Organización", size=20)
        self.lbl_h1.pack(anchor="w", padx=20, pady=(20, 10))
        self.txt_1 = AppleSubText(self.card_1, text="- Arrastra (Drag & Drop) cualquier carpeta a la zona principal.\n- Desmarca cualquier categoría en los filtros si no deseas procesarla.\n- Pulsa 'Start Organization' para clasificar los archivos en nuevas subcarpetas.")
        self.txt_1.pack(anchor="w", padx=20, pady=(0, 20))
        
        self.card_2 = AppleCard(self)
        self.card_2.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.lbl_h2 = AppleHeading(self.card_2, text="2. Configuraciones Avanzadas", size=20)
        self.lbl_h2.pack(anchor="w", padx=20, pady=(20, 10))
        self.txt_2 = AppleSubText(self.card_2, text="- Simulacro (Dry-Run): Evalúa posibles movimientos sin tocar el disco duro.\n- Vigilancia (Watchdog): Daemon oculto que ordena automáticamente en tiempo real.\n- Undo Batch: Botón rojo para revertir la última iteración con 100% de fiabilidad.\n- Exclusiones: Prohíbe mover archivos que contengan sintaxis (ej. 'borrador').")
        self.txt_2.pack(anchor="w", padx=20, pady=(0, 20))

        self.card_3 = AppleCard(self)
        self.card_3.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.lbl_h3 = AppleHeading(self.card_3, text="3. Motor de Reglas (Automata)", size=20)
        self.lbl_h3.pack(anchor="w", padx=20, pady=(20, 10))
        self.txt_3 = AppleSubText(self.card_3, text="Navega a 'Rules Engine' para forzar rutas personalizadas excepcionales.\n\nEjemplo: Si extensión = '.pdf' y nombre contiene = 'factura' \n-> Redirigir hacia 'Finanzas' en vez del subdirectorio general.")
        self.txt_3.pack(anchor="w", padx=20, pady=(0, 20))
        
    def cambiar_idioma(self, lang):
        if lang == "Español":
            self.lbl_title.configure(text="Manual de Usuario - Enterprise")
            self.lbl_h1.configure(text="1. Panel de Organización")
            self.txt_1.configure(text="- Arrastra (Drag & Drop) cualquier carpeta caótica a la zona principal.\n- Desmarca cualquier categoría en los filtros inferiores si no deseas procesarla.\n- Pulsa el botón verde 'Start Organization' para auto-clasificar los archivos.")
            self.lbl_h2.configure(text="2. Configuraciones Avanzadas")
            self.txt_2.configure(text="- Simulacro (Dry-Run): Evalúa posibles movimientos sin tocar en absoluto el disco.\n- Vigilancia (Watchdog): Se ancla de fondo ordenando automáticamente lo que entra.\n- Undo: Botón rojo 'Undo Batch' para revertir el último traslado masivo de manera segura.\n- Exclusiones: Separa por coma atributos que la máquina nunca debe tocar ('temp, test').")
            self.lbl_h3.configure(text="3. Motor de Reglas (Automata)")
            self.txt_3.configure(text="Navega al 'Rules Engine' para forzar enrutamientos ignorando rutas naturales.\n\nEjemplo de Algoritmo: Si la extensión es '.pdf' y nombre contiene 'factura' \n-> Redirigir el archivo a la carpeta 'Finanzas_Logs'.")
        else:
            self.lbl_title.configure(text="Enterprise User Guide")
            self.lbl_h1.configure(text="1. Welcome to the Home Page")
            self.txt_1.configure(text="- Drag & Drop any chaotic folder directly into the main dropping zone.\n- Uncheck categories in the bottom parameters if you want them to be ignored.\n- Click 'Start Organization' to let the AI route files to rigid subdirectories.")
            self.lbl_h2.configure(text="2. Advanced Operations Settings")
            self.txt_2.configure(text="- Dry-Run Mode: Test the algorithm securely without moving bytes physically on disk.\n- Watchdog Daemon: Runs perpetually in the background mapping downloads instantly.\n- Undo Batch: Massive red button to safely revert and rollback the latest batch.\n- Overrides: Pass comma-separated strings to safely blindside fragile files or caches.")
            self.lbl_h3.configure(text="3. Automata & Custom Route Rules")
            self.txt_3.configure(text="Navigate to 'Rules Engine' tab to intercept file strings overriding default mappings.\n\nAlgorithm Code logic: IF Ext = '.pdf' AND Name includes 'invoice' \n-> Dispatch strictly into absolute folder '/Finance Logs'.")
