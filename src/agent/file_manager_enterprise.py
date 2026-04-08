import os
import shutil
import datetime
import json
import requests
import threading

# Core categories defining file classifications based on extensions
MESES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

DIRECTORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".ods", ".odp", ".xlsx", ".xls", ".xlsm", ".csv", ".pptx", ".ppt", ".wps", ".epub", ".mobi", ".md", ".pages", ".numbers", ".key", ".ibooks", ".cbr", ".cbz", ".tex", ".bib", ".cls", ".msg", ".eml", ".vcf", ".ics"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".tif", ".webp", ".ico", ".heic", ".heif", ".psd", ".ai", ".eps", ".indd", ".raw", ".cdr", ".cr2", ".nef", ".orf", ".sr2", ".arw", ".dng", ".rw2", ".raf", ".pef"],
    "Audio Video": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".vob", ".ogv", ".m4v", ".3gp", ".mpeg", ".mpg", ".m2ts", ".mts", ".ts", ".srt", ".sub", ".ass", ".ssa", ".vtt", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".alac", ".mid", ".midi", ".amr", ".opus", ".pcm", ".aup3", ".flp", ".logicx", ".als"],
    "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".tgz", ".dmg", ".pkg", ".deb", ".rpm", ".z", ".lz", ".lzma", ".cab"],
    "Executables Installers": [".exe", ".msi", ".bat", ".sh", ".cmd", ".apk", ".app", ".bin", ".jar", ".com", ".gadget", ".vbs", ".wsf", ".ps1", ".run", ".vb"],
    "Web Dev Code": [".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", ".php", ".asp", ".aspx", ".scss", ".less", ".sass", ".py", ".java", ".c", ".cpp", ".cs", ".h", ".rb", ".swift", ".go", ".kt", ".pl", ".lua", ".r", ".m", ".rs", ".dart", ".groovy", ".sql", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".env", ".properties", ".dockerfile", ".config", ".ipynb"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot", ".pfb", ".pfm", ".fon"],
    "3D CAD Design": [".stl", ".obj", ".fbx", ".blend", ".3ds", ".dae", ".ply", ".gcode", ".dwg", ".dxf", ".rvt", ".skp", ".ifc"],
    "Databases": [".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".dbf", ".sav", ".dat"],
    "System Backups": [".bak", ".old", ".tmp", ".log", ".swp", ".dump", ".cfg", ".reg"],
    "Others": [] 
}

class EnterpriseFileManager:
    """
    Core engine handling local file operations, metadata extraction,
    and automatic rule-based sorting with cloud synchronization.
    """
    def __init__(self, device_id, api_url, token, user_email, ws_client=None):
        self.device_id = device_id
        self.api_url = api_url
        self.token = token
        self.user_email = user_email
        self.ws = ws_client
        self.cloud_rules = self._descargar_reglas()
        self.custom_rules = self._cargar_reglas_locales()
        
        self.historial_file = f"historial_{self.user_email}.json" if self.user_email else "historial.json"
        self.movimiento_file = f"ultimo_movimiento_{self.user_email}.json" if self.user_email else "ultimo_movimiento.json"
        
        self.historial = self._cargar_json(self.historial_file, {"total_archivos": 0, "por_categoria": {}})
        self.ultimo_movimiento = self._cargar_json(self.movimiento_file, [])

    def _cargar_json(self, file_path, default):
        """Loads a JSON file returning its content or the default value if it fails."""
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception: pass
        return default

    def _guardar_json(self, file_path, data):
        """Saves data into a local JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception: pass

    def _cargar_reglas_locales(self):
        return self._cargar_json("custom_rules.json", [])

    def guardar_reglas_locales(self, reglas):
        self.custom_rules = reglas
        self._guardar_json("custom_rules.json", reglas)

    def guardar_regla_custom(self, ext, kw, cat):
        """Stores a new user-defined sorting rule manually created from the GUI."""
        self.custom_rules.append({"ext": ext, "key": kw, "cat": cat})
        self.guardar_reglas_locales(self.custom_rules)

    def borrar_regla_custom(self, idx):
        """Deletes a local rule by index."""
        if 0 <= idx < len(self.custom_rules):
            del self.custom_rules[idx]
            self.guardar_reglas_locales(self.custom_rules)

    def _descargar_reglas(self):
        """Fetches dynamic sorting rules established by the Admins via the Enterprise Cloud."""
        try:
            r = requests.get(f"{self.api_url}/devices/sync/{self.device_id}")
            return r.json()
        except: return []

    def obtener_carpeta_destino(self, extension):
        """Maps a file extension to its primary parent category."""
        ext = extension.lower()
        for folder, extensions in DIRECTORIES.items():
            if ext in extensions:
                return folder
        return "Others"
        
    def obtener_ruta_fecha(self, stat_result):
        """Formats the file modification timestamp into a Year/Month structure."""
        timestamp = stat_result.st_mtime
        fecha = datetime.datetime.fromtimestamp(timestamp)
        return str(fecha.year), MESES[fecha.month - 1]

    def _escanear_profundo(self, base_path):
        """
        Recursively maps subdirectories relying on the high-performance 'os.scandir' 
        system call in C, bypassing expensive stat lookups compared to os.walk.
        """
        archivos = []
        try:
            with os.scandir(base_path) as it:
                for entry in it:
                    if entry.name in DIRECTORIES.keys() or entry.name == "Others":
                        continue
                    if entry.is_file(follow_symlinks=False):
                        archivos.append((entry.path, entry.name, entry.stat(follow_symlinks=False)))
                    elif entry.is_dir(follow_symlinks=False):
                        archivos.extend(self._escanear_profundo(entry.path))
        except Exception:
            pass
        return archivos

    def procesar_lote(self, base_path, categorias_activas, opciones, callback_log):
        """
        The principal orchestrator that processes a folder sorting request.
        Translates file metadata, validates rules, moves paths, caches history,
        and dispatches real-time Live Sync events to the background network server.
        """
        dry_run = opciones.get("dry_run", False)
        por_fecha = opciones.get("crear_carpetas_fecha", False)
        escanear_sub = opciones.get("escanear_subcarpetas", False)
        
        texto_exclusiones = opciones.get("exclusiones", "").lower()
        exclusiones = set([ex.strip() for ex in texto_exclusiones.split(",") if ex.strip()])

        archivos_a_procesar = []

        if escanear_sub:
            archivos_a_procesar = self._escanear_profundo(base_path)
        else:
            try:
                with os.scandir(base_path) as it:
                    for entry in it:
                        if entry.is_file(follow_symlinks=False):
                            archivos_a_procesar.append((entry.path, entry.name, entry.stat(follow_symlinks=False)))
            except Exception as e:
                callback_log(f"ERROR reading the folder: {e}")
                return []

        movimientos_log = []
        nombre_carpeta_base = os.path.basename(os.path.normpath(base_path))
        
        c_rules = self.custom_rules + [{"ext": r['extension'].lower(), "key": r['keyword'].lower(), "cat": r['category']} for r in self.cloud_rules]

        for ruta_origen, archivo, stat_info in archivos_a_procesar:
            archivo_lower = archivo.lower()
            
            if any(palabra in archivo_lower for palabra in exclusiones):
                movimientos_log.append({"file": archivo, "status": "Omitted (Excluded)"})
                continue

            nombre, extension = os.path.splitext(archivo)
            ext_lower = extension.lower()
            
            target_folder_base = None
            for rule in c_rules:
                if ext_lower.endswith(rule['ext']) and rule['key'] in archivo_lower:
                    target_folder_base = rule['cat']
                    break
            
            if not target_folder_base:
                target_folder_base = "Others" if not extension else self.obtener_carpeta_destino(ext_lower)

            if target_folder_base not in categorias_activas and not any(r['cat'] == target_folder_base for r in c_rules): 
                movimientos_log.append({"file": archivo, "status": "Omitted (Category)"})
                continue

            estamos_en_categoria = (nombre_carpeta_base == target_folder_base)
            target_folder = ""
            
            if por_fecha:
                año, mes = self.obtener_ruta_fecha(stat_info)
                if estamos_en_categoria: target_folder = os.path.join(año, mes)
                else: target_folder = os.path.join(target_folder_base, año, mes)
            else:
                if estamos_en_categoria: target_folder = ""
                else: target_folder = target_folder_base

            if not target_folder: 
                movimientos_log.append({"file": archivo, "status": "Ignored (Already in place)"})
                continue

            target_path = os.path.join(base_path, target_folder)

            if not os.path.exists(target_path) and not dry_run:
                try: os.makedirs(target_path)
                except Exception as e:
                    movimientos_log.append({"file": archivo, "status": f"Error mkDir: {e}"})
                    continue

            destino = os.path.join(target_path, archivo)
            if ruta_origen == destino: continue

            if os.path.exists(destino):
                contador = 1
                while True:
                    nuevo_nombre = f"{nombre}({contador}){extension}"
                    destino = os.path.join(target_path, nuevo_nombre)
                    if not os.path.exists(destino): break
                    contador += 1
            
            if dry_run:
                callback_log(f"DRY RUN: {archivo} -> {target_folder}")
                movimientos_log.append({"file": archivo, "status": "Simulated"})
            else:
                try:
                    shutil.move(ruta_origen, destino)
                    callback_log(f"MOVED: {archivo} -> {target_folder}")
                    movimientos_log.append({"file": archivo, "status": "Sorted", "origen_real": ruta_origen, "destino_real": destino})
                    
                    self.historial["total_archivos"] += 1
                    self.historial["por_categoria"][target_folder_base] = self.historial["por_categoria"].get(target_folder_base, 0) + 1
                    
                    if self.ws:
                        evento = {"filename": archivo,"source_path": base_path,"dest_path": target_folder}
                        self.ws.send(json.dumps(evento))

                except Exception as e:
                    movimientos_log.append({"file": archivo, "status": f"Error moving: {e}"})

        if not dry_run and movimientos_log:
            validos = [m for m in movimientos_log if m["status"] == "Sorted"]
            if validos:
                self.ultimo_movimiento = validos
                self._guardar_json(self.movimiento_file, validos)
                self._guardar_json(self.historial_file, self.historial)

        return movimientos_log

    def deshacer_ultimo(self, callback_log):
        """Reverses the last batch of sorted files back to their original locations."""
        if not self.ultimo_movimiento:
            callback_log("Nothing to undo (Empty rollback cache).")
            return False
        
        exito_count = 0
        for m in reversed(self.ultimo_movimiento):
            origen = m.get("origen_real")
            destino = m.get("destino_real")
            if origen and destino and os.path.exists(destino):
                try:
                    shutil.move(destino, origen)
                    callback_log(f"RESTORED: {m['file']}")
                    exito_count += 1
                except Exception as e:
                    callback_log(f"Error restoring {m['file']}: {e}")
                    
        if exito_count > 0:
            # Revert Dashboard metrics globally if rollback succeeds
            self.historial["total_archivos"] = max(0, self.historial["total_archivos"] - exito_count)
            self._guardar_json(self.historial_file, self.historial)
            
        self.ultimo_movimiento = []
        self._guardar_json(self.movimiento_file, [])
        return True