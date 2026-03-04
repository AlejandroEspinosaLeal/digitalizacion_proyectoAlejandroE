"""
MÓDULO DE INTERFAZ GRÁFICA (main.py)
------------------------------------
Front-end de la aplicación. Responsable de:
- Dibujar la interfaz estilo Apple macOS con CustomTkinter.
- Manejar eventos del usuario (Drag & Drop, Clics, Buscador).
- Ejecutar el backend (file_manager) en Hilos (Threads) separados para que la UI no se congele.
- Gestionar el 'Modo Vigía' (Watchdog y Pystray) para funcionar en segundo plano.
- Mostrar la Guía de Usuario y gestionar Reglas Inteligentes.
"""

import sys
import subprocess
import datetime
import threading
import os
import time
import json

# --- AUTO-INSTALADOR DE DEPENDENCIAS ---
def instalar_dependencias():
    dependencias = ["customtkinter", "watchdog", "pystray", "pillow", "tkinterdnd2"]
    faltan = False
    for dep in dependencias:
        try: __import__(dep)
        except ImportError:
            faltan = True
            break
    if faltan:
        print("Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencias)

instalar_dependencias()

import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES 
from config import DIRECTORIES, LOG_FILE
import file_manager

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# Configuramos la paleta de colores base
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VigiaHandler(FileSystemEventHandler):
    """Manejador de eventos para Watchdog en Modo Vigía."""
    def __init__(self, app_ref, categorias, opciones):
        self.app = app_ref
        self.categorias = categorias
        self.opciones = opciones

    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1) 
            self.app.registrar_evento(f"👀 VIGÍA DETECTÓ: {os.path.basename(event.src_path)}")
            file_manager.procesar_archivos(self.app.ruta_seleccionada, self.categorias, self.opciones, self.app.registrar_evento)

class FileSorterApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self) 
        
        self.title("Sistema de Gobernanza de Archivos")
        self.geometry("850x900")
        self.configure(fg_color="#1C1C1E") 
        
        self.ruta_seleccionada = ""
        self.observer = None
        self.icono_tray = None
        self.construir_interfaz()

    def construir_interfaz(self):
        """Crea y renderiza todos los elementos visuales en pantalla."""
        fuente_titulo_app = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        fuente_tarjeta = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        fuente_normal = ctk.CTkFont(family="Segoe UI", size=13)
        fuente_botones = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")

        # --- CABECERA ---
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cabecera.pack(pady=(25, 10), padx=30, fill="x")
        
        self.label_titulo = ctk.CTkLabel(self.frame_cabecera, text="File Sorter", font=fuente_titulo_app)
        self.label_titulo.pack(side="left")

        self.btn_reglas = ctk.CTkButton(self.frame_cabecera, text="🧠 Reglas", width=100, fg_color="#5E5CE6", hover_color="#4B49B8", corner_radius=15, command=self.abrir_panel_reglas, font=fuente_botones)
        self.btn_reglas.pack(side="right", padx=(10, 0))

        self.btn_info = ctk.CTkButton(self.frame_cabecera, text="ℹ️ Guía", width=80, fg_color="#64D2FF", text_color="black", hover_color="#50A8CC", corner_radius=15, command=self.mostrar_guia_uso, font=fuente_botones)
        self.btn_info.pack(side="right")

        # --- ZONA DRAG & DROP ---
        self.frame_top = ctk.CTkFrame(self, fg_color="#2C2C2E", corner_radius=15)
        self.frame_top.pack(pady=10, padx=30, fill="x")
        
        self.label_paso1 = ctk.CTkLabel(self.frame_top, text="Origen de Datos", font=fuente_tarjeta)
        self.label_paso1.pack(pady=(15, 5), anchor="w", padx=20)
        
        self.frame_drop = ctk.CTkFrame(self.frame_top, fg_color="#3A3A3C", corner_radius=12, height=90)
        self.frame_drop.pack(pady=(5, 15), padx=20, fill="x")
        self.frame_drop.pack_propagate(False) 
        
        self.label_drop = ctk.CTkLabel(self.frame_drop, text="📁 Arrastra tu carpeta aquí o haz clic para buscar", text_color="#8E8E93", font=fuente_botones)
        self.label_drop.pack(expand=True)

        self.frame_drop.bind("<Button-1>", lambda e: self.seleccionar_carpeta())
        self.label_drop.bind("<Button-1>", lambda e: self.seleccionar_carpeta())
        self.frame_drop.drop_target_register(DND_FILES)
        self.frame_drop.dnd_bind('<<Drop>>', self.al_soltar_carpeta)

        # --- CATEGORÍAS ---
        self.frame_center = ctk.CTkFrame(self, fg_color="#2C2C2E", corner_radius=15)
        self.frame_center.pack(pady=10, padx=30, fill="x")
        
        self.label_paso2 = ctk.CTkLabel(self.frame_center, text="Categorías a organizar", font=fuente_tarjeta)
        self.label_paso2.pack(pady=(15, 10), anchor="w", padx=20)
        
        self.grid_container = ctk.CTkFrame(self.frame_center, fg_color="transparent")
        self.grid_container.pack(pady=(0, 15), padx=20, expand=True)

        emojis = {
            "Documentos": "📄", "Imagenes": "🖼️", "Audio_Video": "🎵", 
            "Comprimidos": "📦", "Ejecutables_Instaladores": "⚙️", 
            "Codigo_Web_Dev": "💻", "Fuentes": "🔤", "Diseño_3D_CAD": "🧊", 
            "Base_de_Datos": "🗄️", "Sistema_Backups": "🛡️", "Otros": "📁"
        }

        self.checkbox_vars = {}
        fila, columna = 0, 0
        for categoria in DIRECTORIES.keys():
            var = ctk.IntVar(value=1)
            icono = emojis.get(categoria, "📁")
            nombre_limpio = f"{icono} {categoria.replace('_', ' ')}"
            chk = ctk.CTkCheckBox(self.grid_container, text=nombre_limpio, variable=var, font=fuente_normal, fg_color="#0A84FF", hover_color="#007AFF")
            chk.grid(row=fila, column=columna, padx=15, pady=8, sticky="w")
            self.checkbox_vars[categoria] = var
            columna += 1
            if columna > 2: columna = 0; fila += 1

        # --- OPCIONES AVANZADAS ---
        self.frame_opciones = ctk.CTkFrame(self, fg_color="#2C2C2E", corner_radius=15)
        self.frame_opciones.pack(pady=10, padx=30, fill="x")
        
        self.label_paso3 = ctk.CTkLabel(self.frame_opciones, text="Opciones Avanzadas", font=fuente_tarjeta)
        self.label_paso3.pack(pady=(15, 5), anchor="w", padx=20)
        
        self.entry_exclusiones = ctk.CTkEntry(self.frame_opciones, placeholder_text="⛔ Ignorar si contiene... (ej: importante, draft)", width=600, fg_color="#1C1C1E", border_color="#3A3A3C", corner_radius=8)
        self.entry_exclusiones.pack(pady=(5, 15), padx=20)

        self.grid_switches = ctk.CTkFrame(self.frame_opciones, fg_color="transparent")
        self.grid_switches.pack(pady=(0, 15), padx=20, expand=True)

        self.var_dry_run = ctk.BooleanVar(value=False)
        self.var_subcarpetas = ctk.BooleanVar(value=False)
        self.var_fechas = ctk.BooleanVar(value=False)
        self.var_vigia = ctk.BooleanVar(value=False)

        self.sw_dry_run = ctk.CTkSwitch(self.grid_switches, text="Modo Simulacro", variable=self.var_dry_run, progress_color="#0A84FF", font=fuente_normal)
        self.sw_dry_run.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.sw_subcarpetas = ctk.CTkSwitch(self.grid_switches, text="Escanear subcarpetas", variable=self.var_subcarpetas, progress_color="#0A84FF", font=fuente_normal)
        self.sw_subcarpetas.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        self.sw_fechas = ctk.CTkSwitch(self.grid_switches, text="Subcarpetas Año/Mes", variable=self.var_fechas, command=self.activar_menu_fechas, progress_color="#0A84FF", font=fuente_normal)
        self.sw_fechas.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.var_tipo_fecha = ctk.StringVar(value="Modificación")
        self.combo_fechas = ctk.CTkOptionMenu(self.grid_switches, values=["Modificación", "Creación", "Último Acceso"], variable=self.var_tipo_fecha, state="disabled", fg_color="#3A3A3C", button_color="#48484A", corner_radius=8)
        self.combo_fechas.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        self.sw_vigia = ctk.CTkSwitch(self.grid_switches, text="Modo Vigía (2do Plano)", variable=self.var_vigia, progress_color="#0A84FF", font=fuente_normal)
        self.sw_vigia.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        # --- ZONA DE ACCIÓN Y AUDITORÍA ---
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent") 
        self.frame_bottom.pack(pady=10, padx=30, fill="both", expand=True)
        
        self.frame_botones = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        self.frame_botones.pack(pady=(10, 15), fill="x")

        self.btn_organizar = ctk.CTkButton(self.frame_botones, text="Ejecutar Organización", command=self.iniciar_ejecucion, fg_color="#32D74B", text_color="black", hover_color="#28CD41", corner_radius=12, height=45, font=fuente_botones)
        self.btn_organizar.pack(side="left", expand=True, padx=5, fill="x")
        
        self.btn_deshacer = ctk.CTkButton(self.frame_botones, text="Deshacer...", command=self.abrir_panel_deshacer, fg_color="transparent", text_color="#FF453A", hover_color="#3A0A0A", corner_radius=12, height=45, font=fuente_botones)
        self.btn_deshacer.pack(side="left", padx=5)
        
        self.btn_exportar = ctk.CTkButton(self.frame_botones, text="Exportar Log", command=self.accion_exportar, fg_color="transparent", text_color="#0A84FF", hover_color="#001A33", corner_radius=12, height=45, font=fuente_botones)
        self.btn_exportar.pack(side="left", padx=5)

        self.progressbar = ctk.CTkProgressBar(self.frame_bottom, mode="indeterminate", progress_color="#32D74B", fg_color="#2C2C2E", height=8)
        self.progressbar.pack(pady=(5, 10), fill="x")
        self.progressbar.set(0)

        self.label_estado = ctk.CTkLabel(self.frame_bottom, text="Estado: Listo y esperando...", text_color="#8E8E93", font=fuente_normal)
        self.label_estado.pack(anchor="w")

    # ==========================================
    # LÓGICA: EVENTOS DE INTERFAZ Y DRAG & DROP
    # ==========================================
    def al_soltar_carpeta(self, event):
        ruta = event.data.strip('{}')
        if os.path.isdir(ruta):
            self.ruta_seleccionada = ruta
            self.label_drop.configure(text=f"📁 {ruta}", text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", weight="bold"))
        else:
            messagebox.showwarning("Error", "Por favor, arrastra una CARPETA válida, no un archivo.")

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_seleccionada = ruta
            self.label_drop.configure(text=f"📁 {ruta}", text_color="#FFFFFF", font=ctk.CTkFont(family="Segoe UI", weight="bold"))

    # ==========================================
    # LÓGICA: ACTUALIZACIONES DE UI "THREAD-SAFE"
    # ==========================================
    def registrar_evento(self, mensaje):
        self.after(0, self._actualizar_estado_ui, mensaje)
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(f"[{timestamp}] {mensaje}\n")
        except: pass

    def _actualizar_estado_ui(self, mensaje):
        if len(mensaje) > 80: mensaje = mensaje[:77] + "..."
        self.label_estado.configure(text=f"Estado: {mensaje}")

    # ==========================================
    # LÓGICA: GUÍA DE USO Y REGLAS INTELIGENTES
    # ==========================================
    def mostrar_guia_uso(self):
        """Abre una ventana modal con el manual de usuario completo y exhaustivo."""
        ventana_info = ctk.CTkToplevel(self)
        ventana_info.title("Manual del Usuario - File Sorter RPA")
        ventana_info.geometry("800x750") 
        ventana_info.configure(fg_color="#1C1C1E")
        ventana_info.transient(self)
        ventana_info.grab_set()

        lbl_titulo = ctk.CTkLabel(ventana_info, text="📖 Manual de Usuario Completo", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"))
        lbl_titulo.pack(pady=(25, 15))

        txt_info = ctk.CTkTextbox(ventana_info, wrap="word", font=ctk.CTkFont(family="Segoe UI", size=14), fg_color="#2C2C2E", text_color="#E5E5EA", corner_radius=12)
        txt_info.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        guia_texto = """¡Bienvenido a File Sorter RPA! 
Esta aplicación es un "Robot" diseñado para acabar con el desorden de tus carpetas de forma totalmente automática. Si tienes una carpeta de Descargas llena de miles de archivos mezclados, estás en el lugar correcto.

A continuación, te explicamos cómo usar cada función paso a paso:

1️⃣ PASO 1: SELECCIONAR EL ORIGEN DE DATOS
Lo primero es decirle al programa qué carpeta quieres limpiar. Tienes dos formas de hacerlo:
• Haz clic en el recuadro gris que dice "Arrastra tu carpeta aquí..." y busca la carpeta en tu ordenador (por ejemplo, tu carpeta de 'Descargas').
• O, simplemente, abre tu explorador de archivos, pincha una carpeta y arrástrala directamente sobre ese recuadro gris.

2️⃣ PASO 2: CATEGORÍAS (¿Qué quieres organizar?)
Aquí verás una lista con interruptores (Documentos, Imágenes, Audio, etc.). 
• Si están marcados (en azul), el programa cogerá esos archivos y los meterá en sus carpetas correspondientes.
• Si desmarcas "Imágenes", el programa ignorará todos los archivos .jpg o .png y los dejará tirados donde estaban. Úsalo si solo quieres limpiar un tipo de archivo en concreto.

3️⃣ 🧠 REGLAS INTELIGENTES (El botón morado de arriba)
¡Esta es la función más potente! Imagina que no quieres que tus facturas se mezclen con el resto de "Documentos".
Haz clic en el botón morado de "Reglas Inteligentes" y añade una regla así:
• Carpeta: "Facturas_2026"
• Ext (Extensión): ".pdf"
• Palabra: "factura"
Al darle a Añadir, el programa sabrá que cualquier PDF que tenga la palabra "factura" en su nombre NO debe ir a Documentos, sino a tu nueva carpeta especial. ¡Estas reglas mandan sobre todo lo demás!

4️⃣ ⛔ EXCLUSIONES (La lista negra)
Justo debajo de las categorías hay una barra para escribir. Si tienes archivos que NO quieres que el programa toque por nada del mundo, escribe palabras clave separadas por comas.
Ejemplo: escribe "importante, borrador, privado". Si un archivo se llama "contrato_importante.docx", el programa lo saltará y no lo moverá.

5️⃣ ⚙️ OPCIONES AVANZADAS (Los 4 interruptores)
• Modo Simulacro: ¿Tienes miedo de liarla? Activa esto y dale a Ejecutar. El programa no moverá NINGÚN archivo real, solo te escribirá en la pantalla negra de abajo qué es lo que haría. Perfecto para probar.
• Escanear subcarpetas: Normalmente, el programa solo limpia los archivos sueltos. Si activas esto, entrará dentro de las carpetitas que tengas en tus Descargas para sacar la basura de ahí también.
• Subcarpetas Año/Mes: En vez de meter 5.000 fotos en la carpeta "Imágenes", el programa creará carpetas por fechas (Ej: Imágenes/2026/Febrero/). Puedes elegir en el desplegable si prefieres usar la fecha de Creación del archivo o la de Modificación.

6️⃣ 🛡️ MODO VIGÍA (El Piloto Automático)
Si activas "Modo Vigía" y le das a Ejecutar, ¡la ventana de la aplicación desaparecerá! No te asustes.
El robot se ha quedado trabajando en "modo fantasma" gastando muy poca batería. Estará vigilando la carpeta que elegiste. Si en ese momento te descargas un archivo de internet, verás que aparece en tu carpeta de descargas e instantáneamente desaparece porque el robot lo ha ordenado solo.
Para apagarlo: Busca un icono verde cuadradito abajo a la derecha en tu pantalla de Windows (junto a la hora y el volumen). Haz clic derecho sobre él y dale a "Mostrar Panel Principal".

7️⃣ ⏪ DESHACER (Panel de Rollback)
¿Le diste a organizar y te arrepentiste? No pasa nada, el programa tiene memoria.
Haz clic en el botón "Deshacer... (Panel)". Se abrirá una ventana con la lista de todos los archivos que se han movido. 
Usa la barra de búsqueda para encontrar ese archivo que no querías mover, márcalo en la lista y dale a Confirmar. El robot lo sacará de su nueva carpeta y lo devolverá exactamente al sitio donde estaba antes de que tocaras nada.

¡Ya estás listo para organizar miles de archivos en segundos!
"""
        
        txt_info.insert("0.0", guia_texto)
        txt_info.configure(state="disabled") 

        btn_cerrar = ctk.CTkButton(ventana_info, text="¡Entendido! Cerrar manual", fg_color="#3A3A3C", hover_color="#48484A", corner_radius=10, height=40, font=ctk.CTkFont(family="Segoe UI", weight="bold"), command=ventana_info.destroy)
        btn_cerrar.pack(pady=(0, 25))

    def abrir_panel_reglas(self):
        """Abre un modal para configurar Reglas Inteligentes JSON."""
        self.panel_reglas = ctk.CTkToplevel(self)
        self.panel_reglas.title("🧠 Reglas Inteligentes")
        self.panel_reglas.geometry("600x500")
        self.panel_reglas.configure(fg_color="#1C1C1E")
        self.panel_reglas.transient(self)
        self.panel_reglas.grab_set() 

        ctk.CTkLabel(self.panel_reglas, text="Nueva Regla", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(pady=(20, 10))
        
        frame_inputs = ctk.CTkFrame(self.panel_reglas, fg_color="transparent")
        frame_inputs.pack(pady=10, padx=20)

        self.entry_cat = ctk.CTkEntry(frame_inputs, placeholder_text="Carpeta", width=170, fg_color="#2C2C2E", border_color="#3A3A3C")
        self.entry_cat.grid(row=0, column=0, padx=5)
        self.entry_ext = ctk.CTkEntry(frame_inputs, placeholder_text="Ext (ej: .pdf)", width=120, fg_color="#2C2C2E", border_color="#3A3A3C")
        self.entry_ext.grid(row=0, column=1, padx=5)
        self.entry_key = ctk.CTkEntry(frame_inputs, placeholder_text="Palabra", width=160, fg_color="#2C2C2E", border_color="#3A3A3C")
        self.entry_key.grid(row=0, column=2, padx=5)

        ctk.CTkButton(self.panel_reglas, text="➕ Añadir", width=80, fg_color="#32D74B", text_color="black", hover_color="#28CD41", corner_radius=10, command=self.guardar_regla).grid(row=0, column=3, padx=5)

        self.scroll_reglas = ctk.CTkScrollableFrame(self.panel_reglas, width=500, height=200, fg_color="#2C2C2E")
        self.scroll_reglas.pack(pady=15, padx=20, fill="both", expand=True)
        self.refrescar_lista_reglas()

    def guardar_regla(self):
        cat, ext, key = self.entry_cat.get().strip(), self.entry_ext.get().strip(), self.entry_key.get().strip()
        if not cat or not ext or not key: return messagebox.showwarning("Atención", "Rellena los 3 campos.")
        if not ext.startswith("."): ext = "." + ext

        reglas = []
        if os.path.exists("custom_rules.json"):
            try:
                with open("custom_rules.json", "r", encoding="utf-8") as f: reglas = json.load(f)
            except: pass
        
        reglas.append({"categoria": cat, "ext": ext, "keyword": key})
        with open("custom_rules.json", "w", encoding="utf-8") as f: json.dump(reglas, f, indent=4)
        
        self.entry_cat.delete(0, 'end'); self.entry_ext.delete(0, 'end'); self.entry_key.delete(0, 'end')
        self.refrescar_lista_reglas()

    def borrar_regla(self, indice):
        try:
            with open("custom_rules.json", "r", encoding="utf-8") as f: reglas = json.load(f)
            del reglas[indice]
            with open("custom_rules.json", "w", encoding="utf-8") as f: json.dump(reglas, f, indent=4)
            self.refrescar_lista_reglas()
        except: pass

    def refrescar_lista_reglas(self):
        for widget in self.scroll_reglas.winfo_children(): widget.destroy()
        reglas = []
        if os.path.exists("custom_rules.json"):
            try:
                with open("custom_rules.json", "r", encoding="utf-8") as f: reglas = json.load(f)
            except: pass

        if not reglas:
            ctk.CTkLabel(self.scroll_reglas, text="No hay reglas personalizadas.", text_color="#8E8E93").pack(pady=20)
            return

        for i, regla in enumerate(reglas):
            frame_regla = ctk.CTkFrame(self.scroll_reglas, fg_color="#1C1C1E", corner_radius=8)
            frame_regla.pack(fill="x", pady=2, padx=5)
            texto = f"📂 {regla['categoria']} | {regla['ext']} que contengan '{regla['keyword']}'"
            ctk.CTkLabel(frame_regla, text=texto, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side="left", padx=10, pady=5)
            ctk.CTkButton(frame_regla, text="❌", width=30, fg_color="transparent", text_color="#FF453A", hover_color="#3A0A0A", command=lambda idx=i: self.borrar_regla(idx)).pack(side="right", padx=5)

    def activar_menu_fechas(self):
        if self.var_fechas.get(): self.combo_fechas.configure(state="normal")
        else: self.combo_fechas.configure(state="disabled")

    def accion_exportar(self):
        messagebox.showinfo("Exportar", f"Log guardado en: {os.path.abspath(LOG_FILE)}")

    # ==========================================
    # LÓGICA: ROLLBACK SELECTIVO OPTIMIZADO
    # ==========================================
    def abrir_panel_deshacer(self):
        historial = file_manager.obtener_historial_completo()
        if not historial: return messagebox.showinfo("Deshacer", "El historial está vacío.")

        self.panel_rollback = ctk.CTkToplevel(self)
        self.panel_rollback.title("Rollback Selectivo")
        self.panel_rollback.geometry("700x600")
        self.panel_rollback.configure(fg_color="#1C1C1E")
        self.panel_rollback.transient(self)
        self.panel_rollback.grab_set()

        ctk.CTkLabel(self.panel_rollback, text="Archivos a restaurar:", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")).pack(pady=(20, 10))

        self.entry_busqueda = ctk.CTkEntry(self.panel_rollback, placeholder_text="🔍 Buscar...", width=400, fg_color="#2C2C2E", border_color="#3A3A3C")
        self.entry_busqueda.pack(pady=5)
        self.entry_busqueda.bind("<KeyRelease>", self.filtrar_lista_archivos)

        self.scroll_frame = ctk.CTkScrollableFrame(self.panel_rollback, width=600, height=350, fg_color="#2C2C2E", corner_radius=10)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.estado_archivos = {}
        self.checkbox_widgets = {}

        for fila, (ruta_actual, ruta_original) in enumerate(historial.items()):
            self.estado_archivos[ruta_actual] = ctk.BooleanVar(value=True)
            nombre_archivo = os.path.basename(ruta_actual)
            chk = ctk.CTkCheckBox(self.scroll_frame, text=f"📄 {nombre_archivo}", variable=self.estado_archivos[ruta_actual], fg_color="#0A84FF", hover_color="#007AFF")
            chk.grid(row=fila, column=0, sticky="w", pady=5, padx=10)
            self.checkbox_widgets[ruta_actual] = (chk, nombre_archivo.lower(), fila)

        ctk.CTkButton(self.panel_rollback, text="Confirmar Restauración", fg_color="transparent", text_color="#FF453A", border_color="#FF453A", border_width=1.5, hover_color="#3A0A0A", corner_radius=10, height=40, command=self.ejecutar_rollback_selectivo).pack(pady=15)

    def filtrar_lista_archivos(self, event=None):
        texto = self.entry_busqueda.get().lower()
        for ruta_actual, (chk, nombre, fila) in self.checkbox_widgets.items():
            if texto in nombre: chk.grid(row=fila, column=0, sticky="w", pady=5, padx=10)
            else: chk.grid_forget()

    def ejecutar_rollback_selectivo(self):
        rutas = [ruta for ruta, var in self.estado_archivos.items() if var.get()]
        if not rutas: return messagebox.showinfo("Atención", "Selecciona algún archivo.")

        self.panel_rollback.destroy()
        self.btn_deshacer.configure(state="disabled")
        self.btn_organizar.configure(state="disabled")
        self.progressbar.start()

        threading.Thread(target=lambda: self._hilo_rollback_selectivo(rutas)).start()

    def _hilo_rollback_selectivo(self, rutas):
        archivos_recuperados = file_manager.deshacer_seleccion(rutas, self.registrar_evento)
        self.after(0, self._fin_rollback, archivos_recuperados)

    def _fin_rollback(self, archivos_recuperados):
        self.progressbar.stop()
        self.progressbar.set(1)
        self.btn_deshacer.configure(state="normal")
        self.btn_organizar.configure(state="normal")
        messagebox.showinfo("Rollback Completado", f"Se han devuelto {archivos_recuperados} archivos a su origen.")

    # ==========================================
    # LÓGICA: EJECUCIÓN PRINCIPAL (THREADS)
    # ==========================================
    def iniciar_ejecucion(self):
        if not self.ruta_seleccionada: return messagebox.showwarning("Atención", "Selecciona o arrastra una carpeta de origen.")

        categorias_activas = [cat for cat, var in self.checkbox_vars.items() if var.get() == 1]
        if not categorias_activas: return

        opciones = {
            "dry_run": self.var_dry_run.get(),
            "escanear_subcarpetas": self.var_subcarpetas.get(),
            "crear_carpetas_fecha": self.var_fechas.get(),
            "tipo_fecha": self.var_tipo_fecha.get(),
            "exclusiones": self.entry_exclusiones.get()
        }

        if self.var_vigia.get():
            self.iniciar_modo_vigia(categorias_activas, opciones)
            return

        self.btn_organizar.configure(state="disabled", text="Trabajando...")
        self.btn_deshacer.configure(state="disabled")
        self.progressbar.start()
        
        threading.Thread(target=self.ejecutar_backend, args=(categorias_activas, opciones)).start()

    def ejecutar_backend(self, categorias_activas, opciones):
        archivos_movidos = file_manager.procesar_archivos(self.ruta_seleccionada, categorias_activas, opciones, self.registrar_evento)
        self.after(0, self._fin_ejecucion, archivos_movidos)

    def _fin_ejecucion(self, archivos_movidos):
        self.progressbar.stop()
        self.progressbar.set(1)
        self.btn_organizar.configure(state="normal", text="Ejecutar Organización")
        self.btn_deshacer.configure(state="normal")
        self.label_estado.configure(text=f"Estado: Proceso finalizado. {archivos_movidos} archivos movidos.")
        messagebox.showinfo("¡Organización Completada! 🎉", f"Se han procesado y movido {archivos_movidos} archivos con éxito.")

    # ==========================================
    # LÓGICA: MODO VIGÍA Y SYSTEM TRAY
    # ==========================================
    def crear_icono_imagen(self):
        imagen = Image.new('RGB', (64, 64), color=(50, 215, 75))
        dibujo = ImageDraw.Draw(imagen)
        dibujo.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
        return imagen

    def iniciar_modo_vigia(self, categorias, opciones):
        self.registrar_evento("🛡️ Iniciando Modo Vigía...")
        event_handler = VigiaHandler(self, categorias, opciones)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.ruta_seleccionada, recursive=opciones["escanear_subcarpetas"])
        self.observer.start()
        
        self.withdraw()
        menu = pystray.Menu(
            item('Mostrar Panel Principal', self.detener_vigia_y_mostrar),
            item('Salir Completamente', self.salir_completamente)
        )
        self.icono_tray = pystray.Icon("FileSorterVigia", self.crear_icono_imagen(), "RPA Vigía Activo", menu)
        threading.Thread(target=self.icono_tray.run, daemon=True).start()
        
        file_manager.procesar_archivos(self.ruta_seleccionada, categorias, opciones, self.registrar_evento)

    def detener_vigia_y_mostrar(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.icono_tray: self.icono_tray.stop()
        
        self.deiconify() 
        self.registrar_evento("Modo Vigía detenido. Panel restaurado.")
        self.sw_vigia.deselect()

    def salir_completamente(self):
        if self.observer: self.observer.stop()
        if self.icono_tray: self.icono_tray.stop()
        self.quit()

if __name__ == "__main__":
    app = FileSorterApp()
    app.mainloop()
