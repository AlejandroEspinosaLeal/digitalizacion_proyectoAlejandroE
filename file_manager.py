"""
MÓDULO DE GESTIÓN DE ARCHIVOS (file_manager.py)
-----------------------------------------------
Este es el "Cerebro" de la aplicación (Backend). No sabe nada de botones ni de interfaces,
su único trabajo es leer el disco duro, evaluar las reglas lógicas y mover archivos.
Maneja exclusiones, reglas personalizadas, creación de carpetas por fecha y el sistema de Rollback (JSON).
"""

import os
import shutil
import datetime
import json
from config import DIRECTORIES, LOG_FILE

# Constantes de configuración interna
HISTORY_FILE = "history.json"      # Base de datos en texto plano para el sistema de Deshacer
RULES_FILE = "custom_rules.json"   # Base de datos de reglas inteligentes del usuario
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def obtener_carpeta_destino(extension):
    """Busca a qué categoría pertenece una extensión cruzándola con el diccionario de config.py."""
    ext = extension.lower()
    for folder, extensions in DIRECTORIES.items():
        if ext in extensions:
            return folder
    return "Otros"

def obtener_ruta_fecha(archivo_path, tipo_fecha):
    """
    Extrae la fecha de un archivo basándose en la configuración elegida por el usuario
    (Creación, Modificación o Último Acceso) y devuelve una tupla con el (Año, Mes en texto).
    """
    if tipo_fecha == "Creación": timestamp = os.path.getctime(archivo_path)
    elif tipo_fecha == "Último Acceso": timestamp = os.path.getatime(archivo_path)
    else: timestamp = os.path.getmtime(archivo_path) # Por defecto: Modificación
        
    fecha = datetime.datetime.fromtimestamp(timestamp)
    año = str(fecha.year)
    mes = MESES[fecha.month - 1] # Traduce el mes número (1-12) a texto (Enero-Diciembre)
    return año, mes

def cargar_reglas_custom():
    """Lee el archivo JSON de reglas inteligentes y devuelve la lista de diccionarios."""
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def procesar_archivos(base_path, categorias_activas, opciones, callback_log):
    """
    Motor principal de la aplicación. Recorre el directorio y mueve los archivos aplicando:
    1. Filtros de exclusión (Listas negras).
    2. Reglas Inteligentes personalizadas.
    3. Organización clásica por extensión.
    4. Sub-carpetas por Fechas.
    """
    moved_count = 0
    historial_movimientos = {} # Diccionario temporal para guardar {Destino: Origen}
    
    # Extraemos la configuración enviada desde la interfaz (main.py)
    dry_run = opciones.get("dry_run", False)
    por_fecha = opciones.get("crear_carpetas_fecha", False)
    tipo_fecha = opciones.get("tipo_fecha", "Modificación")
    escanear_sub = opciones.get("escanear_subcarpetas", False)
    
    # Procesamos el texto de exclusiones convirtiéndolo en una lista limpia
    texto_exclusiones = opciones.get("exclusiones", "").lower()
    exclusiones = [ex.strip() for ex in texto_exclusiones.split(",") if ex.strip()]

    reglas_custom = cargar_reglas_custom()

    callback_log(f"--- INICIO DE PROCESO EN: {base_path} ---")
    if dry_run: callback_log("⚠️ MODO SIMULACRO: No se moverá ningún archivo.")
    if exclusiones: callback_log(f"🛑 Excluyendo archivos que contengan: {', '.join(exclusiones)}")

    archivos_a_procesar = []

    # PASO 1: RECOPILACIÓN DE ARCHIVOS
    if escanear_sub:
        # os.walk entra en todas las subcarpetas. 
        # Modificamos 'dirs' para evitar entrar en las carpetas que nosotros mismos creamos
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in DIRECTORIES.keys() and d != "Otros"]
            for f in files: archivos_a_procesar.append(os.path.join(root, f))
    else:
        # Escaneo simple: solo la carpeta raíz
        try:
            items = os.listdir(base_path)
            for item in items:
                ruta_item = os.path.join(base_path, item)
                if os.path.isfile(ruta_item): archivos_a_procesar.append(ruta_item)
        except Exception as e:
            callback_log(f"ERROR al leer la carpeta: {e}")
            return 0

    # Evitamos que el sistema se modifique a sí mismo o mueva sus configuraciones
    archivos_ignorados = ["main.py", "file_manager.py", "config.py", LOG_FILE, "main.exe", HISTORY_FILE, RULES_FILE]
    
    # Extrae el nombre de la carpeta base (ej. "Descargas") para evitar anidación redundante
    nombre_carpeta_base = os.path.basename(os.path.normpath(base_path))

    # PASO 2: EVALUACIÓN DE REGLAS POR ARCHIVO
    for ruta_origen in archivos_a_procesar:
        archivo = os.path.basename(ruta_origen)
        if archivo in archivos_ignorados: continue

        archivo_lower = archivo.lower()
        
        # Filtro de Exclusión: Si coincide, saltamos a la siguiente iteración (continue)
        if any(palabra in archivo_lower for palabra in exclusiones):
            callback_log(f"⏭️ Omitido por regla de exclusión: '{archivo}'")
            continue

        nombre, extension = os.path.splitext(archivo)
        ext_lower = extension.lower()
        
        # Jerarquía de reglas: Primero verificamos reglas Custom
        target_folder_base = None
        for regla in reglas_custom:
            if regla["ext"].lower() == ext_lower and regla["keyword"].lower() in archivo_lower:
                target_folder_base = regla["categoria"]
                break 
        
        # Si no encaja en reglas custom, aplicamos regla por defecto del diccionario
        if not target_folder_base:
            target_folder_base = "Otros" if not extension else obtener_carpeta_destino(extension)

        # Si el usuario desmarcó esta categoría en la interfaz, ignoramos el archivo
        if target_folder_base not in categorias_activas and not any(r["categoria"] == target_folder_base for r in reglas_custom): 
            continue

        # Evitamos crear la ruta "Documentos/Documentos/..." si ya estamos dentro de ella
        estamos_en_categoria = (nombre_carpeta_base == target_folder_base)
        
        target_folder = ""
        if por_fecha:
            año, mes = obtener_ruta_fecha(ruta_origen, tipo_fecha)
            if estamos_en_categoria: target_folder = os.path.join(año, mes)
            else: target_folder = os.path.join(target_folder_base, año, mes)
        else:
            if estamos_en_categoria: target_folder = ""
            else: target_folder = target_folder_base

        if not target_folder: continue

        target_path = os.path.join(base_path, target_folder)

        # Crear estructura de directorios físicos si no existe
        if not os.path.exists(target_path) and not dry_run:
            try: os.makedirs(target_path)
            except Exception as e:
                callback_log(f"Error creando carpeta {target_folder}: {e}")
                continue

        destino = os.path.join(target_path, archivo)
        if ruta_origen == destino: continue

        # Gestión de Conflictos (Archivos Duplicados): Añade sufijos incrementales (1), (2)...
        if os.path.exists(destino):
            contador = 1
            while True:
                nuevo_nombre = f"{nombre}({contador}){extension}"
                destino = os.path.join(target_path, nuevo_nombre)
                if not os.path.exists(destino): break
                contador += 1
            if not dry_run: callback_log(f"CONFLICTO evitado: Renombrado a '{os.path.basename(destino)}'")

        # PASO 3: EJECUCIÓN DEL MOVIMIENTO
        if dry_run:
            callback_log(f"[SIMULACRO] Movería: '{archivo}' -> '{target_folder}'")
            moved_count += 1
        else:
            try:
                shutil.move(ruta_origen, destino)
                historial_movimientos[destino] = ruta_origen # Guardar trazabilidad para Deshacer
                callback_log(f"MOVIMIENTO: '{archivo}' -> '{target_folder}'")
                moved_count += 1
            except Exception as e:
                callback_log(f"ERROR: No se pudo mover '{archivo}'. Razón: {e}")

    # PASO 4: ALMACENAMIENTO DE AUDITORÍA Y ROLLBACK (JSON)
    if not dry_run and historial_movimientos:
        historial_previo = {}
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    historial_previo = json.load(f)
            except: pass
        historial_previo.update(historial_movimientos) # Fusionamos historial viejo con movimientos nuevos
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(historial_previo, f, indent=4)

    if dry_run: callback_log(f"--- FIN DE SIMULACRO. {moved_count} archivos ---")
    else: callback_log(f"--- FIN DE PROCESO. Archivos movidos: {moved_count} ---")
        
    return moved_count

# --- SISTEMA DE ROLLBACK (DESHACER) ---

def obtener_historial_completo():
    """Recupera el archivo JSON parseado como diccionario de Python."""
    if not os.path.exists(HISTORY_FILE): return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def deshacer_seleccion(rutas_a_restaurar, callback_log):
    """
    Toma una lista de rutas (suministrada por el panel visual de la UI) 
    y devuelve específicamente esos archivos a su ubicación original (Rollback).
    """
    historial = obtener_historial_completo()
    if not historial or not rutas_a_restaurar: return 0

    archivos_devueltos = 0
    callback_log("⏪ INICIANDO ROLLBACK SELECTIVO...")

    for ruta_actual in rutas_a_restaurar:
        if ruta_actual in historial:
            ruta_original = historial[ruta_actual] # Recuperamos de dónde vino el archivo
            
            if os.path.exists(ruta_actual):
                dir_origen = os.path.dirname(ruta_original)
                if not os.path.exists(dir_origen): os.makedirs(dir_origen)

                # Si ya existe un archivo con ese nombre en el origen, lo protegemos renombrando
                destino_seguro = ruta_original
                if os.path.exists(destino_seguro):
                    nombre, ext = os.path.splitext(os.path.basename(ruta_original))
                    contador = 1
                    while os.path.exists(destino_seguro):
                        destino_seguro = os.path.join(dir_origen, f"{nombre}_recuperado({contador}){ext}")
                        contador += 1
                try:
                    shutil.move(ruta_actual, destino_seguro)
                    callback_log(f"↩️ RESTAURADO: '{os.path.basename(ruta_actual)}'")
                    archivos_devueltos += 1
                    del historial[ruta_actual] # Borramos del registro al restaurarse
                except Exception as e: callback_log(f"❌ ERROR al restaurar '{ruta_actual}': {e}")
            else:
                callback_log(f"⚠️ No se encontró '{os.path.basename(ruta_actual)}'.")
                del historial[ruta_actual] # Limpiamos basura del JSON si el archivo ya no existe

    # Guardamos el JSON actualizado (sin los archivos que acabamos de restaurar)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f: json.dump(historial, f, indent=4)
    callback_log(f"✅ FIN DEL ROLLBACK. {archivos_devueltos} archivos devueltos a su origen.")
    return archivos_devueltos