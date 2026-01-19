import os
import shutil
import datetime
import sys

# Configuración de carpetas y extensiones
DIRECTORIES = {
    "Documentos": [
        # Microsoft / OpenOffice
        ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".ods", ".odp", 
        ".xlsx", ".xls", ".xlsm", ".csv", ".pptx", ".ppt", ".wps", ".dotx", 
        ".docm", ".dotm", ".potx", ".potm", ".ppam", ".pptm", ".sldx", ".sldm",
        # Ebooks / Publicaciones
        ".epub", ".mobi", ".azw", ".azw3", ".ibooks", ".cbr", ".cbz",
        # Markdown / LaTeX / Otros
        ".md", ".markdown", ".tex", ".bib", ".cls",
        # Mac iWork
        ".pages", ".numbers", ".key",
        # Correo / Organizers
        ".msg", ".eml", ".vcf", ".ics"
    ],
    
    "Imagenes": [
        # Web / Comunes
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".tif", 
        ".webp", ".ico", ".heic", ".heif",
        # Adobe / Diseño Vectorial
        ".psd", ".ai", ".eps", ".indd", ".raw", ".cdr",
        # RAW de Cámaras
        ".cr2", ".nef", ".orf", ".sr2", ".arw", ".dng", ".rw2", ".raf", ".pef"
    ],
    
    "Audio_Video": [
        # Video
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".vob", 
        ".ogv", ".m4v", ".3gp", ".mpeg", ".mpg", ".m2ts", ".mts", ".ts",
        # Subtítulos (a menudo van con el video)
        ".srt", ".sub", ".ass", ".ssa", ".vtt",
        # Audio
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", 
        ".alac", ".mid", ".midi", ".amr", ".opus", ".pcm",
        # Proyectos Audio (DAW)
        ".aup3", ".flp", ".logicx", ".als"
    ],
    
    "Comprimidos": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", 
        ".tgz", ".dmg", ".pkg", ".deb", ".rpm", ".z", ".lz", ".lzma", ".cab"
    ],
    
    "Ejecutables_Instaladores": [
        ".exe", ".msi", ".bat", ".sh", ".cmd", ".apk", ".app", ".bin", 
        ".jar", ".com", ".gadget", ".vbs", ".wsf", ".ps1", ".run", ".vb"
    ],
    
    "Codigo_Web_Dev": [
        # Web
        ".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", 
        ".php", ".asp", ".aspx", ".scss", ".less", ".sass",
        # Backend / Scripting
        ".py", ".java", ".c", ".cpp", ".cs", ".h", ".rb", ".swift", ".go", 
        ".kt", ".pl", ".lua", ".r", ".m", ".rs", ".dart", ".groovy",
        # Datos / Configuración
        ".sql", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".env", 
        ".properties", ".dockerfile", ".config",
        # Data Science
        ".ipynb"
    ],
    
    "Fuentes": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot", ".pfb", ".pfm", ".fon"
    ],
    
    "Diseño_3D_CAD": [
        # Modelado 3D / Impresión 3D
        ".stl", ".obj", ".fbx", ".blend", ".3ds", ".dae", ".ply", ".gcode",
        # CAD / Arquitectura
        ".dwg", ".dxf", ".rvt", ".skp", ".ifc"
    ],
    
    "Base_de_Datos": [
        ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".dbf", ".sav", ".dat"
    ],
    
    "Sistema_Backups": [
        ".bak", ".old", ".tmp", ".log", ".swp", ".dump", ".cfg", ".reg"
    ],
    
    "Otros": [] # Archivos sin extensión o no reconocidos
}
LOG_FILE = "log.txt"

def write_log(message):
    """
    Escribe una entrada en el archivo de registro con marca de tiempo.
    Garantiza la trazabilidad del dato.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def get_target_folder(extension):
    """
    Determina la carpeta destino basada en la extensión del archivo.
    """
    ext = extension.lower()
    for folder, extensions in DIRECTORIES.items():
        if ext in extensions:
            return folder
    return "Otros"

def organize_files(base_path):
    """
    Función principal que recorre el directorio y clasifica los archivos.
    """
    if not os.path.exists(base_path):
        print(f"Error: La ruta '{base_path}' no existe.")
        return

    # Contador para estadísticas
    moved_count = 0
    
    print(f"Iniciando organización en: {base_path}...")
    write_log(f"--- INICIO DE PROCESO DE ORGANIZACIÓN EN: {base_path} ---")

    files = [f for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f))]

    for file in files:
        # Evitar mover el propio script y el archivo de log
        if file in ["main.py", LOG_FILE]:
            continue

        filename, extension = os.path.splitext(file)
        
        # Si el archivo no tiene extensión, va a Otros
        if not extension:
            target_folder = "Otros"
        else:
            target_folder = get_target_folder(extension)

        target_path = os.path.join(base_path, target_folder)

        # Crear carpeta si no existe (Idempotencia)
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            write_log(f"Carpeta creada: {target_folder}")

        source_file = os.path.join(base_path, file)
        destination_file = os.path.join(target_path, file)

        # Manejo de conflictos: Si el archivo ya existe, renombramos
        if os.path.exists(destination_file):
            timestamp_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = f"{filename}_{timestamp_suffix}{extension}"
            destination_file = os.path.join(target_path, new_filename)
            write_log(f"CONFLICTO: {file} ya existía en {target_folder}. Renombrado a {new_filename}")

        try:
            shutil.move(source_file, destination_file)
            write_log(f"MOVIMIENTO: '{file}' -> '{target_folder}'")
            moved_count += 1
        except Exception as e:
            error_msg = f"ERROR: No se pudo mover '{file}'. Razón: {e}"
            print(error_msg)
            write_log(error_msg)

    print(f"Proceso completado. Se han movido {moved_count} archivos.")
    print(f"Consulta '{LOG_FILE}' para ver el historial detallado.")
    write_log(f"--- FIN DE PROCESO. Archivos movidos: {moved_count} ---")

if __name__ == "__main__":
    # Solicitamos la ruta al usuario, por defecto usa el directorio actual (.)
    target_dir = input("Introduce la ruta de la carpeta a organizar (deja vacío para usar la carpeta actual): ").strip()
    
    if not target_dir:
        target_dir = "."
    
    organize_files(target_dir)