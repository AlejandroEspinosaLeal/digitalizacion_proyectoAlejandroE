# Enterprise Cloud API Guide

This documentation specifies the endpoints available on the FastAPI backend for interacting with User Authentication, Device synchronization, Telemetry WebSocket metrics, and Logging.

---

## 1. Authentication Endpoints

### 1.1 Login & 2FA Dispatch
- **Method:** `POST`
- **Route:** `/auth/token`
- **Description:** Validates user credentials. Upon success, instead of dispatching the JWT instantly, it shoots a 2FA Code to the user's email inbox using SMTP. 
- **Body Example:**
  ```json
  { "email": "admin@nexmedia.com", "hashed_password": "supersecretpassword123" }
  ```
- **Success Response:**
  ```json
  { "status": "pending_verification", "message": "Verification code sent to email" }
  ```
- **Errors:**
  - `401 Unauthorized`: "Invalid credentials"

### 1.2 Access Token Verification
- **Method:** `POST`
- **Route:** `/auth/verify`
- **Description:** Verifies the 6-digit confirmation code previously sent to the email to unlock the API.
- **Body Example:**
  ```json
  { "email": "admin@nexmedia.com", "code": "849201" }
  ```
- **Success Response:**
  ```json
  { "access_token": "eyJhbGciOiJIUzI...", "token_type": "bearer" }
  ```
- **Errors:**
  - `401 Unauthorized`: "Invalid code"

---

## 2. Telemetry and Analytics

### 2.1 Public File Statistics
- **Method:** `GET`
- **Route:** `/stats/public`
- **Description:** Fetches aggregated privacy-safe metadata highlighting the total sum of files correctly classified worldwide across the company.
- **Parameters:** None. No JWT token required.
- **Success Response:**
  ```json
  {
      "total": 12891,
      "categories": { "Documents": 402, "Images": 8900, "Audio Video": 120 },
      "last_updated": "2026-04-24T18:00:20"
  }
  ```

### 2.2 Live Action Websockets
- **Method:** `WS (WebSocket)`
- **Route:** `/ws/events/{device_id}`
- **Description:** Continuous reverse-connection socket allowing physical Workstations running Python to push telemetry objects to the web dashboard interface dynamically in real-time.
- **Payload Broadcasted:**
  ```json
  {
      "type": "file_event",
      "category": "Documents",
      "filename": "Q3_Invoice_NexMedia.pdf",
      "device_id": "409f87c2b",
      "timestamp": "2026-04-24T18:02:11"
  }
  ```

---

## 3. Operations Reporting

### 3.1 Upload Background Sorting Logs
- **Method:** `POST`
- **Route:** `/devices/log/report`
- **Description:** Submits a massive array detailing hundreds of file-movements locally occurred inside a Workstation. Triggers a background process that generates and sends an HTML audit report back to the user via Email.
- **Authorization:** Requires JSON Web Token (`Bearer ey...`).
- **Body Example:**
  ```json
  {
      "device_id": "848da1-b92d-41",
      "folder": "C:/Downloads",
      "logs": [
          {"file": "receipt_02.png", "status": "Sorted", "destino_real": "Images/receipt_02.png"}
      ]
  }
  ```
- **Success Response:**
  ```json
  { "status": "success", "message": "Report sent to admin@nexmedia.com" }
  ```
- **Errors:** 
  - `401 Unauthorized`: "Invalid token" or "User not found"
