# Guía Global de la API Corporativa

Esta documentación expone todos los Endpoints REST y WebSockets integrados en el servicio backend hecho en FastAPI. Sirve como puente entre los Agentes de escritorio locales y el Panel Web de Telemetría.

---

## 1. Endpoints de Autenticación

### 1.1 Iniciar sesión & Disparador MFA
- **Método:** `POST`
- **Ruta:** `/auth/token`
- **Descripción:** Valida las credenciales. Al tener éxito, obliga al dispositivo a realizar la Autenticación de Múltiples Factores disparando por correo SMTP un código de 6 dígitos.
- **Ejemplo del Body:**
  ```json
  { "email": "admin@nexmedia.com", "hashed_password": "miclave_supersegura1" }
  ```
- **Respuesta Exitosa:**
  ```json
  { "status": "pending_verification", "message": "Verification code sent to email" }
  ```
- **Errores Previstos:**
  - `401 Unauthorized`: "Invalid credentials"

### 1.2 Validación de Código de Acceso
- **Método:** `POST`
- **Ruta:** `/auth/verify`
- **Descripción:** Valida la respuesta del correo. De ser correcta, entrega por fin el `access_token` JWT para la sesión.
- **Ejemplo del Body:**
  ```json
  { "email": "admin@nexmedia.com", "code": "849201" }
  ```
- **Respuesta Exitosa:**
  ```json
  { "access_token": "eyJhbGciOiJIUzI...", "token_type": "bearer" }
  ```
- **Errores Previstos:**
  - `401 Unauthorized`: "Invalid code"

---

## 2. Telemetría y Analíticas

### 2.1 Estadísticas Globales
- **Método:** `GET`
- **Ruta:** `/stats/public`
- **Descripción:** Obtiene los metadatos agregados de eficacia que destacan el volumen masivo de la empresa entera en archivos desplazados. (Sin exponer los nombres de archivos reales).
- **Parámetros:** Ninguno. No requiere JWT Token (Acceso Público para el Panel Web).
- **Respuesta Exitosa:**
  ```json
  {
      "total": 12891,
      "categories": { "Documents": 402, "Images": 8900, "Audio Video": 120 },
      "last_updated": "2026-04-24T18:00:20"
  }
  ```

### 2.2 Sockets de Acción en Vivo
- **Método:** `WS (WebSocket)`
- **Ruta:** `/ws/events/{device_id}`
- **Descripción:** Un túnel bidireccional donde los PC de los empleados en todo el edificio avisan con latencia casi nula cada vez que un archivo se mueve localmente, rebotando la señal para animar la Landing Page corporativa.
- **Broadcast Recibido en Dashboard:**
  ```json
  {
      "type": "file_event",
      "category": "Documents",
      "filename": "Factura_Q3_NexMedia.pdf",
      "device_id": "409f87c2b",
      "timestamp": "2026-04-24T18:02:11"
  }
  ```

---

## 3. Reportes Generenciales

### 3.1 Enviar Registros (Logs) de Clasificación
- **Método:** `POST`
- **Ruta:** `/devices/log/report`
- **Descripción:** Envía la información detallada de una limpieza profunda de una carpeta, forzando a la nube de Python a construir y enviar un Reporte HTML de Auditoría directo al correo del jefe usando SMTP en segundo plano (`BackgroundTasks`).
- **Autorización:** Obligatorio poseer un Token Válido (`Bearer ey...`).
- **Ejemplo del Body:**
  ```json
  {
      "device_id": "848da1-b92d-41",
      "folder": "C:/Downloads",
      "logs": [
          {"file": "comprobante_02.png", "status": "Sorted", "destino_real": "Images/comprobante_02.png"}
      ]
  }
  ```
- **Respuesta Exitosa:**
  ```json
  { "status": "success", "message": "Report sent to admin@nexmedia.com" }
  ```
- **Errores:** 
  - `401 Unauthorized`: "Invalid token" (Cuando la sesión ha caducado)
