# File Sorter Enterprise

File Sorter Enterprise es un sistema de gobernanza de archivos automatizado (asistido por IA) que rescata discos duros no estructurados del caos digital. Monitorea, categoriza y organiza los archivos entrantes (documentos, media, instaladores) hacia estructuras de directorios rígidas mientras transmite las métricas en tiempo real a tu dashboard en la nube.

## Demo Online
Puedes probar la versión web del Dashboard estilo SaaS directamente aquí:
🌐 **[Demo en Vercel](https://filesorterv1.vercel.app/index.html)**

## Requisitos Previos
- Python 3.10+
- SQLite (Integrado en Python)
- Windows, macOS o Linux

## Instalación Paso a Paso

```bash
# 1. Clona el repositorio
git clone https://github.com/NexMediaSolutions/file_sorter.git
cd file_sorter

# 2. Crea y activa tu entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura tus variables de entorno
cp .env.example .env

# 5. Lanza el servidor Backend y la Interfaz de Escritorio simultáneamente
python setup_and_run.py
```

## Ejemplo de uso rápido

1. Abre la interfaz gráfica del Agente de Escritorio (File Governance System).
2. Haz clic en **Login** o **Crear Cuenta** para sincronizarte de forma segura.
3. En el panel principal, arrastra y suelta (Drag & Drop) cualquier carpeta desorganizada (ej: `Descargas`).
4. Pulsa **Start Organization**. El programa extraerá los archivos dividiéndolos en subcarpetas como `Images`, `Documents` y `Videos`.
5. Abre `<TU_IP>:8000` en tu navegador para visualizar tu panel de administración corporativo.

## Estructura del proyecto

```text
file_sorter/
├── src/
│   ├── agent/             # Código fuente del Cliente Desktop (CustomTkinter)
│   │   ├── models/        # Estados locales de la sesión y Temas UI
│   │   ├── services/      # Cliente HTTP para acceder a la API remota
│   │   └── views/         # Interfaces Gráficas con diseño Apple HIG
│   └── backend/           # Código fuente del Servidor Web (FastAPI)
│       ├── api/           # Endpoints divididos por Router
│       └── core/          # Criptografía Bcrypt y seguridad JWT
├── tests/                 # Asserts de validación de lógica Pytest
├── landing/               # Código Frontend (HTML/JS/CSS) corporativo
├── setup_and_run.py       # Script principal que ejecuta ambos hilos simultáneos
└── verify_script.py       # Validaciones automatizadas de integridad
```

## Variables de Entorno (.env) necesarias

| Nombre | Descripción | Ejemplo | Obligatoria |
| --- | --- | --- | --- |
| `SECRET_KEY` | Firma para firmar los Tokens de JWT | `0x9abcd123...` | **Sí** |
| `ALGORITHM` | Algoritmo criptográfico para los tokens | `HS256` | Sí |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Vida útil máxima de una sesión | `30` | No |
| `DATABASE_URL` | URI de la base de datos central | `sqlite:///./enterprise.db`| No |
| `SMTP_USER` | Correo utilizado para enviar códigos 2FA | `auth@midominio.com`| No |
| `SMTP_PASSWORD`| Contraseña de Aplicación de SMTP | `ejem ploa cont rase` | No |

## Cómo ejecutar los tests

Usamos `pytest` para todo el QA del sistema. Para asegurar un despliegue libre de errores corre:

```bash
# Asegúrate de tener el entorno virtual activado
pytest -v tests/
```
Para ver un reporte de cobertura detallado:
```bash
coverage run -m pytest
coverage report -m
```

## Cómo contribuir
1. Haz un Fork del proyecto ("Bifurcar")
2. Crea una rama para tu feature (`git checkout -b feature/CaracteristicaIncreible`)
3. Haz Commit a tus cambios (`git commit -m 'Agregar nueva caracteristica increible'`)
4. Súbela a la nube (`git push origin feature/CaracteristicaIncreible`)
5. Haz un Pull Request
