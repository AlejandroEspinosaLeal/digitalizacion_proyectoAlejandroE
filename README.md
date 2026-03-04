# digitalizacion_proyectoAlejandroE

# Propuesta: Automatización y Organización de tus Archivos

**De:** Tu Consultor de Desarrollo  
**Fecha:** 02 de Febrero de 2026  
**Asunto:** Solución para el desorden digital y gestión de documentos  

---
# 🤖 File Sorter RPA - Sistema Avanzado de Gobernanza de Archivos

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/Licencia-Open%20Source-green)
![UI](https://img.shields.io/badge/UI-CustomTkinter-purple)
![Estado](https://img.shields.io/badge/Estado-Producción-success)

## 📖 Descripción del Proyecto

**File Sorter RPA** es una aplicación de escritorio desarrollada en Python orientada a la **Automatización Robótica de Procesos (RPA)** y el **Gobierno del Dato**. Su objetivo principal es resolver el problema del desorden digital en entornos corporativos y personales, automatizando la clasificación, el enrutamiento y la auditoría de miles de archivos en segundos.

A diferencia de los scripts tradicionales, esta herramienta no solo clasifica por extensión, sino que permite definir **Reglas de Negocio Inteligentes** (clasificación por contexto/palabras clave), operar de forma invisible en segundo plano y garantizar la integridad de los datos mediante un sistema avanzado de **Rollback (Deshacer)** en tiempo real. Todo ello envuelto en una interfaz gráfica moderna inspirada en las *Human Interface Guidelines* de Apple (macOS/iOS Dark Mode).

---

## ✨ Características Principales

* 🎯 **Interfaz Gráfica Moderna (UI/UX):** Diseño minimalista en Modo Oscuro con animaciones fluidas, barras de progreso y sistema de arrastrar y soltar (*Drag & Drop*) para una experiencia de usuario inmejorable.
* 🧠 **Reglas Inteligentes (Custom Rules):** Crea reglas lógicas personalizadas. Ej: *"Mover todos los archivos .pdf que contengan la palabra 'Factura' a la carpeta 'Contabilidad'"*.
* 🛡️ **Modo Vigía (Background Monitor):** La aplicación puede ocultarse de la pantalla y alojarse en la bandeja del sistema (System Tray). Vigilará la carpeta seleccionada 24/7 y organizará automáticamente cualquier archivo nuevo que entre en ella.
* ⏪ **Rollback Selectivo (Deshacer):** Sistema de memoria basado en archivos JSON. Si te equivocas, abre el Panel de Deshacer, busca el archivo exacto con el buscador en tiempo real y devuélvelo a su origen con un clic.
* 📅 **Clasificación Temporal:** Capacidad de generar subcarpetas dinámicas basadas en el Año y Mes de Creación o Modificación del archivo.
* 🔍 **Modo Simulacro (Dry Run):** Permite testear el impacto de las reglas de negocio sin realizar ninguna modificación real en el disco duro.
* ⛔ **Listas Negras (Exclusiones):** Protege archivos críticos indicando palabras clave que el algoritmo debe ignorar por completo.
* 📝 **Trazabilidad y Logs:** Generación de archivos de auditoría (`log.txt`) con el registro exacto de cada movimiento para garantizar el cumplimiento normativo.

---

## 🏗️ Arquitectura del Software

El código ha sido diseñado siguiendo principios de modularidad y responsabilidad única (*Separation of Concerns*):

* `main.py`: Actúa como el **Front-end**. Gestiona la interfaz con CustomTkinter, los eventos del usuario, el Drag & Drop y lanza hilos de ejecución (*Threading*) para evitar que la UI se congele durante el procesamiento.
* `file_manager.py`: Es el **Back-end** (Motor Lógico). Contiene los algoritmos de enrutamiento, la gestión del sistema de archivos (`shutil`, `os`), la lectura/escritura de los historiales JSON y la prevención de sobreescritura de datos.
* `config.py`: Archivo de **Configuración**. Almacena los diccionarios base de categorías y extensiones, permitiendo escalar el software fácilmente sin alterar la lógica central.

---

## 🚀 Instalación y Uso

### Prerrequisitos
* Python 3.8 o superior instalado en el sistema.

### Instalación Automática (Recomendado)
El software cuenta con un script de auto-resolución de dependencias. 
1. Clona este repositorio o descarga los archivos en una carpeta.
2. Ejecuta el archivo principal:
   ```bash
   python main.py
