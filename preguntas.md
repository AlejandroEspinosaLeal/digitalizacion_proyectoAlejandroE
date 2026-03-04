Proyecto: File Sorter RPA (Sistema de Gobernanza de Archivos)
1. Ciclo de vida del dato (Criterio 5b)
¿Cómo se gestionan los datos desde su generación hasta su eliminación en tu proyecto?
En este RPA, el dato (los archivos y documentos) entra en el ciclo de vida cuando es generado por un usuario o una máquina en un directorio de origen (ej. Descargas). El software actúa en la fase de Procesamiento y Almacenamiento: captura el dato, evalúa su tipología (extensión) y su contexto (palabras clave / reglas personalizadas), y lo enruta hacia su repositorio estructurado definitivo. El software no se encarga de la eliminación por motivos de seguridad (evitar pérdida de datos), delegando la destrucción final a las políticas de retención de la empresa. Además, genera "metadatos" de auditoría mediante logs y un archivo JSON de trazabilidad.

¿Qué estrategia sigues para garantizar la consistencia e integridad de los datos?
La integridad está garantizada mediante tres capas de seguridad implementadas en el código:

Gestión de colisiones: Si un archivo con el mismo nombre ya existe en el destino, el sistema no lo sobrescribe, sino que le asigna un sufijo incremental (archivo(1).txt), evitando la corrupción o pérdida de datos.

Modo Simulacro (Dry Run): Permite auditar el proceso de enrutamiento sin ejecutar operaciones físicas en el disco.

Rollback (Deshacer): Se mantiene un historial en tiempo real (history.json). Si hay una categorización errónea, el sistema puede leer este JSON y devolver los datos exactos a su estado y ubicación original manteniendo su integridad.

2. Almacenamiento en la nube (Criterio 5f)
Si tu software utiliza almacenamiento en la nube, ¿cómo garantizas la seguridad y disponibilidad de los datos? / Si no usas la nube, ¿cómo podrías integrarla en futuras versiones?
Actualmente, el software opera en un entorno local (On-Premise) para garantizar la máxima privacidad de los archivos procesados. Sin embargo, su arquitectura es totalmente compatible con la nube de forma indirecta: si la ruta de destino es una carpeta sincronizada (como OneDrive, SharePoint o Google Drive Desktop), el RPA automatiza la subida a la nube al organizar los archivos allí.
Integración futura: En futuras versiones, se podría integrar la librería boto3 para conectar directamente con AWS S3 o el SDK de Azure Blob Storage. Esto permitiría que el "Modo Vigía" capte archivos locales y los suba directamente a buckets en la nube, eliminando la dependencia del almacenamiento físico y aumentando la disponibilidad del dato (Alta Disponibilidad).

¿Qué alternativas consideraste para almacenar datos y por qué elegiste tu solución actual?
Se evaluó usar bases de datos SQL para registrar el historial de movimientos (history.json) y las reglas inteligentes (custom_rules.json). Se descartó en favor de archivos JSON locales porque el JSON no requiere instalar motores de bases de datos de terceros, mantiene el software ligero, portable (Open Source) y facilita al usuario la exportación e inspección manual de las reglas de negocio.

3. Seguridad y regulación (Criterio 5i)
¿Qué medidas de seguridad implementaste para proteger los datos o procesos en tu proyecto?

Aislamiento de procesos: El "Modo Vigía" utiliza la librería watchdog para operar en segundo plano sin exponer puertos a la red, mitigando riesgos de ataques externos.

Filtro de Exclusiones: Se implementó una "Lista Negra" donde el usuario puede definir palabras clave (ej: "privado", "nomina"). El algoritmo ignora estos archivos, protegiendo información crítica de ser movida accidentalmente a carpetas públicas o compartidas.

Trazabilidad: Generación de un log.txt que cumple con los estándares de auditoría de seguridad (quién movió qué, cuándo y a dónde).

¿Qué normativas (e.g., GDPR) podrían afectar el uso de tu software y cómo las has tenido en cuenta?
El GDPR (RGPD en España) afecta directamente si el software clasifica archivos que contienen PII (Información de Identificación Personal), como currículums o nóminas. La herramienta facilita el cumplimiento del GDPR gracias a las "Reglas Inteligentes": permite configurar el sistema para que todos los archivos .pdf con la palabra "CV" se envíen automáticamente a una carpeta cifrada o con acceso restringido exclusivo para el departamento de RRHH, aplicando el principio de Privacidad por Diseño.

4. Implicación de las THD en negocio y planta (Criterio 2e)
¿Qué impacto tendría tu software en un entorno de negocio o en una planta industrial? / ¿Cómo crees que tu solución podría mejorar procesos operativos?

En Negocio (Back-office): Departamentos como Contabilidad pueden ahorrar cientos de horas anuales automatizando el enrutamiento de facturas y albaranes. El RPA clasifica automáticamente los archivos por año/mes y proveedor.

En Planta (Industrial): La maquinaria industrial y los sistemas SCADA generan continuamente archivos de registro (Logs) y reportes de producción (CSV). Implementando el "Modo Vigía" en el servidor de la planta, el software puede capturar estos reportes en tiempo real y organizarlos por fecha y tipo de máquina, facilitando enormemente el trabajo de los analistas de mantenimiento predictivo.

5. Mejoras en IT y OT (Criterio 2f)
¿Cómo puede tu software facilitar la integración entre entornos IT y OT?
El software actúa como un puente de datos. El entorno OT (Tecnologías de la Operación, como los PLCs en fábrica) genera datos crudos a nivel local. Nuestro RPA puede monitorizar las carpetas locales de OT y trasladar automáticamente esa información estructurada hacia los servidores del entorno IT (Tecnologías de la Información), permitiendo que los sistemas de gestión (ERP) o los analistas de datos consuman la información de planta sin intervención humana.

¿Qué procesos específicos podrían beneficiarse de tu solución en términos de automatización o eficiencia?
La recolección de Data Dumps (volcados de datos) diarios. En lugar de que un operario de OT tenga que sacar los archivos CSV de una máquina manualmente mediante un USB o moviéndolos por red, el RPA vigila la ruta de salida de la máquina y enruta los datos a la infraestructura IT de forma transparente, eliminando el cuello de botella manual.

6. Tecnologías Habilitadoras Digitales (Criterio 2g)
¿Qué tecnologías habilitadoras digitales (THD) has utilizado o podrías integrar en tu proyecto?
El proyecto en sí mismo es una implementación de RPA (Robotic Process Automation), una THD fundamental para la automatización de tareas repetitivas basadas en reglas lógicas.
Para enriquecer la solución en el futuro, se podrían integrar las siguientes THD:

Inteligencia Artificial (Procesamiento de Lenguaje Natural - NLP): En lugar de depender de la extensión o el nombre del archivo, integrar una IA permitiría "leer" el contenido interno de un PDF escaneado (OCR) para saber si es un contrato o una factura, y clasificarlo de forma autónoma.

Big Data / Analítica Avanzada: Conectar la salida del history.json a un dashboard de PowerBI para analizar volúmenes de generación de datos en la empresa (ej: ver picos de creación de archivos por departamentos).
