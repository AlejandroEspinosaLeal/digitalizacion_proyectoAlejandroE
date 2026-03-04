"""
MÓDULO DE CONFIGURACIÓN (config.py)
-----------------------------------
Este archivo actúa como el "diccionario central" de la aplicación.
Separar estas extensiones del código principal (main.py o file_manager.py) 
sigue el principio de diseño "Separation of Concerns" (Separación de responsabilidades).
Si en el futuro se añade un nuevo formato de archivo, solo se toca este texto,
sin riesgo de romper la lógica de programación.
"""

LOG_FILE = "log.txt" # Nombre del archivo donde se guardará la auditoría/registro de movimientos.

# Diccionario principal: La clave es el nombre de la carpeta destino, 
# el valor es una lista de extensiones de archivo asociadas a esa categoría.
DIRECTORIES = {
    "Documentos": [
        ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".ods", ".odp", 
        ".xlsx", ".xls", ".xlsm", ".csv", ".pptx", ".ppt", ".wps", ".dotx", 
        ".docm", ".dotm", ".potx", ".potm", ".ppam", ".pptm", ".sldx", ".sldm",
        ".epub", ".mobi", ".azw", ".azw3", ".ibooks", ".cbr", ".cbz",
        ".md", ".markdown", ".tex", ".bib", ".cls",
        ".pages", ".numbers", ".key",
        ".msg", ".eml", ".vcf", ".ics"
    ],
    "Imagenes": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".tif", 
        ".webp", ".ico", ".heic", ".heif",
        ".psd", ".ai", ".eps", ".indd", ".raw", ".cdr",
        ".cr2", ".nef", ".orf", ".sr2", ".arw", ".dng", ".rw2", ".raf", ".pef"
    ],
    "Audio_Video": [
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".vob", 
        ".ogv", ".m4v", ".3gp", ".mpeg", ".mpg", ".m2ts", ".mts", ".ts",
        ".srt", ".sub", ".ass", ".ssa", ".vtt",
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", 
        ".alac", ".mid", ".midi", ".amr", ".opus", ".pcm",
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
        ".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", 
        ".php", ".asp", ".aspx", ".scss", ".less", ".sass",
        ".py", ".java", ".c", ".cpp", ".cs", ".h", ".rb", ".swift", ".go", 
        ".kt", ".pl", ".lua", ".r", ".m", ".rs", ".dart", ".groovy",
        ".sql", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".env", 
        ".properties", ".dockerfile", ".config",
        ".ipynb"
    ],
    "Fuentes": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot", ".pfb", ".pfm", ".fon"
    ],
    "Diseño_3D_CAD": [
        ".stl", ".obj", ".fbx", ".blend", ".3ds", ".dae", ".ply", ".gcode",
        ".dwg", ".dxf", ".rvt", ".skp", ".ifc"
    ],
    "Base_de_Datos": [
        ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".dbf", ".sav", ".dat"
    ],
    "Sistema_Backups": [
        ".bak", ".old", ".tmp", ".log", ".swp", ".dump", ".cfg", ".reg"
    ],
    "Otros": [] # Carpeta por defecto si un archivo tiene extensión pero no está en la lista.
}