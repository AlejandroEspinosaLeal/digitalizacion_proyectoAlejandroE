# Fase 2: Análisis de Utilidad y Aplicación

A continuación, se presenta el análisis de viabilidad, impacto y utilidad de **File Sorter Enterprise**, aplicado a las necesidades de una empresa orientada a la gestión documental (ficticia o real).

---

### Criterio 6a) Objetivos estratégicos

**¿Qué objetivos estratégicos específicos de la empresa aborda tu software?**
File Sorter Enterprise aborda el objetivo estratégico de la **automatización de procesos repetitivos** (RPA). Las empresas desperdician miles de horas anuales ordenando archivos, buscando documentos mal ubicados y categorizando descargas. Nuestro software asume esa carga de trabajo, organizando automáticamente el ecosistema de archivos de los empleados de forma silenciosa.

**¿Cómo se alinea el software con la estrategia general de digitalización?**
Se alinea impulsando la transición hacia el "Cero Papel" y un entorno de trabajo estrictamente digital. Al garantizar que todos los documentos digitales (PDFs de facturas, imágenes, código, etc.) queden perfectamente catalogados en sus directorios correspondientes desde el minuto uno, se estandariza la estructura de la información a nivel corporativo, un paso previo e indispensable para cualquier futura implementación de Inteligencia Artificial o analítica de Big Data dentro de la empresa.

---

### Criterio 6b) Áreas de negocio y comunicaciones

**¿Qué áreas de la empresa (producción, negocio, comunicaciones) se ven más beneficiadas con tu software?**
Se beneficia principalmente el **área de producción/operaciones** y la de **administración**. Al manejar grandes volúmenes de contratos, facturas y recursos multimedia, estas áreas suelen sufrir cuellos de botella buscando archivos. 

**¿Qué impacto operativo esperas en las operaciones diarias?**
El impacto esperado es una reducción del 90% en el tiempo empleado para organizar bandejas de entrada o carpetas de descargas compartidas. Las operaciones ganarán fluidez, minimizando el extravío de archivos clave y reduciendo la frustración de los empleados, lo que impacta indirectamente en un aumento global de la productividad diaria.

---

### Criterio 6c) Áreas susceptibles de digitalización

**¿Qué áreas de la empresa son más susceptibles de ser digitalizadas con tu software?**
Las áreas de Recursos Humanos (recepción de CVs masivos), Contabilidad (facturas y recibos) y Marketing (recepción de recursos multimedia brutos como vídeos, fotos o audios).

**¿Cómo mejorará la digitalización las operaciones en esas áreas?**
Actualmente, los recepcionistas o administrativos deben arrastrar manualmente y renombrar los archivos que llegan a sus equipos. Con File Sorter Enterprise, el departamento de Contabilidad simplemente deposita todos los archivos recibidos en la carpeta "Input", y el motor automatizado los segmentará por formatos (ej. enviando todos los `.pdf` y `.xlsx` a carpetas financieras protegidas), reduciendo el error humano a cero.

---

### Criterio 6d) Encaje de áreas digitalizadas (AD)

**¿Cómo interactúan las áreas digitalizadas con las no digitalizadas?**
Los departamentos que usen el clasificador (AD) generarán un sistema de carpetas limpio y predecible. Los departamentos que todavía dependan del papel o tengan procesos manuales (áreas no digitalizadas) podrían tener fricciones si necesitan introducir documentos físicos en el flujo de los departamentos digitalizados.

**¿Qué soluciones o mejoras propondrías para integrar estas áreas?**
Integrar en la empresa escáneres con tecnología OCR conectados a un servidor central. Todo el papel escaneado pasaría a ser PDF digital que sería inyectado automáticamente en la carpeta de entrada de File Sorter Enterprise, logrando que el departamento digitalizado absorba y ordene el trabajo del área no digitalizada sin fricciones.

---

### Criterio 6e) Necesidades presentes y futuras

**¿Qué necesidades actuales de la empresa resuelve tu software?**
Resuelve el caos organizativo crónico en los discos duros locales de los empleados y en los servidores compartidos. Elimina la "basura digital" y asegura un versionado y organización predecible. Además, satisface la necesidad de los administradores de monitorizar (vía el Dashboard de actividad) cómo y cuántos archivos se gestionan en tiempo real.

---

### Criterio 6f) Relación con tecnologías

**¿Qué tecnologías habilitadoras has empleado y cómo impactan en las áreas de la empresa?**
- **Python (Watchdog):** Para la motorización del sistema de archivos a bajo nivel y automatización (impacta quitando la carga mecánica al trabajador).
- **FastAPI / Supabase:** Para centralizar la telemetría y generar una base de datos en la nube (impacta a la dirección tecnológica, ofreciendo métricas precisas de uso).
- **Web Analytics (Chart.js + Tailwind):** Para el Dashboard en tiempo real que consumen los gestores del sistema.

**¿Qué beneficios específicos aporta la implantación de estas tecnologías?**
Estabilidad, escalabilidad (el stack web de Supabase/Vercel aguanta alta concurrencia) y bajo consumo de recursos (el motor Python se ejecuta en segundo plano ocupando muy poca memoria).

---

### Criterio 6g) Brechas de seguridad

**¿Qué posibles brechas de seguridad podrían surgir al implementar tu software?**
1. **Acceso indebido a archivos confidenciales:** Dado que el programa tiene permisos de lectura/escritura y mueve archivos a gran velocidad, si se corrompen las rutas de destino, facturas confidenciales podrían acabar en carpetas públicas.
2. **Inyección de código / Ejecución de Malware:** Si se configura mal, el sistema podría mover un archivo malicioso (como un `.exe` camuflado) a zonas críticas del sistema operativo corporativo.
3. **Exposición de credenciales:** El uso de API Keys de Supabase en el lado cliente (Dashboard) podría exponer la base de datos de eventos a terceros malintencionados.

**¿Qué medidas concretas propondrías para mitigarlas?**
- Restringir la ejecución del script bajo un usuario del Sistema Operativo con privilegios muy limitados.
- Añadir validación del *Magic Number* del archivo, y no fiarse solamente de la extensión.
- Esconder las claves de Supabase usando variables de entorno (`.env`) en el backend (FastAPI) y crear un proxy para que el Dashboard consulte los datos a través del propio backend, en lugar de conectar directamente con el cliente.

---

### Criterio 6h) Tratamiento de datos y análisis

**¿Cómo se gestionan los datos en tu software y qué metodologías utilizas?**
El software utiliza un flujo *Event-Driven* (guiado por eventos). Cuando el servicio local detecta un archivo nuevo (evento), registra las metadatos del archivo (nombre, tamaño, timestamp, extensión, y path destino) y envía un JSON a través de la API hacia la base de datos de Supabase (PostgreSQL). Todo se almacena en tablas relacionales asegurando integridad.

**¿Qué haces para garantizar la calidad y consistencia de los datos?**
- Tipado estricto a través de validadores como **Pydantic** en el backend.
- Colas *offline*: si la aplicación local de Python pierde conectividad a internet, los eventos de ordenación se guardan temporalmente en SQLite local y se sincronizan con Supabase cuando regresa la conexión, garantizando que jamás se pierdan datos estadísticos de la actividad empresarial.
