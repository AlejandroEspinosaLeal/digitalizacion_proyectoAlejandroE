import requests
import json
from pathlib import Path
from src.agent.models.state import AppState
from src.agent.services.offline_queue import OfflineQueue

def _get_env_vars():
    env_path = Path(".env")
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()
    return env_vars

class APIClient:
    """Unified HTTP Client connecting directly to Supabase Auth and Data."""
    
    def __init__(self):
        self.app_state = AppState()
        self.offline_queue = OfflineQueue()
        env_vars = _get_env_vars()
        url = env_vars.get("SUPABASE_URL", "https://TU_SUPABASE_URL_AQUI")
        if url and not url.startswith("http"):
            url = f"https://{url}"
        self.supabase_url = url
        self.anon_key = env_vars.get("SUPABASE_ANON_KEY", "TU_ANON_KEY_AQUI")
        
    def login(self, email, password):
        headers = {"apikey": self.anon_key, "Content-Type": "application/json"}
        resp = requests.post(f"{self.supabase_url}/auth/v1/token?grant_type=password", json={"email": email, "password": password}, headers=headers)
        data = resp.json()
        if resp.status_code == 200:
            user_id = data.get("user", {}).get("id")
            access_token = data.get("access_token")
            # Register device in Supabase so the web dashboard can track it
            if user_id:
                headers["Authorization"] = f"Bearer {access_token}"
                headers["Prefer"] = "resolution=merge-duplicates"
                device_payload = {
                    "id": self.app_state.device_id,
                    "name": f"Agent-{self.app_state.device_id[:4]}",
                    "user_id": user_id,
                    "is_online": True
                }
                requests.post(f"{self.supabase_url}/rest/v1/device", json=device_payload, headers=headers)
            return {"access_token": access_token}, 200
        return {"detail": data.get("error_description", "Error logging in")}, resp.status_code

    def verify_code(self, email, code):
        return {"access_token": "shim_not_used"}, 200

    def register(self, email, password):
        headers = {"apikey": self.anon_key, "Content-Type": "application/json"}
        resp = requests.post(f"{self.supabase_url}/auth/v1/signup", json={"email": email, "password": password}, headers=headers)
        data = resp.json()
        if resp.status_code in [200, 201]:
            return {"status": "ok"}, 201
        return {"detail": data.get("error_description", "Error registering")}, resp.status_code

    def forgot_password(self, email):
        headers = {"apikey": self.anon_key, "Content-Type": "application/json"}
        requests.post(f"{self.supabase_url}/auth/v1/recover", json={"email": email}, headers=headers)
        return {"status": "ok"}, 200

    def reset_password(self, email, code, new_password):
        return {"detail": "Check your email for the secure Supabase reset link."}, 400

    def send_log_report(self, logs_payload):
        if not self.app_state.token:
            return None
            
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.app_state.token}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Translate to Supabase schema:
        # device_id, filename, source_path, dest_path
        supabase_payload = []
        for log in logs_payload:
            supabase_payload.append({
                "device_id": self.app_state.device_id,
                "filename": log.get("filename", "unknown"),
                "source_path": log.get("source_path", ""),
                "dest_path": log.get("dest_path", "")
            })
        
        try:
            resp = requests.post(f"{self.supabase_url}/rest/v1/fileevent", json=supabase_payload, headers=headers, timeout=5)
            resp.raise_for_status()
            self.sync_offline_logs()
            return resp
        except requests.HTTPError as e:
            print("SUPABASE HTTP ERROR:", e.response.text)
            self.offline_queue.push(supabase_payload)
            raise ConnectionError(f"Backend offline. Saved in local resolution queue.")
        except (requests.ConnectionError, requests.Timeout) as e:
            self.offline_queue.push(supabase_payload)
            raise ConnectionError(f"Backend offline. Saved in local resolution queue.")

    def sync_offline_logs(self):
        """Called automatically when a network request is successful."""
        pending = self.offline_queue.get_pending()
        if not pending: 
            return
            
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.app_state.token}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        for log_id, payload_str in pending:
            payload = json.loads(payload_str)
            if isinstance(payload, dict) and "logs" in payload:
                # Up-translate legacy queued logs if they exist
                legacy_logs = payload.get("logs", [])
                payload = []
                for log in legacy_logs:
                    payload.append({
                        "device_id": self.app_state.device_id,
                        "filename": log.get("filename", "unknown"),
                        "source_path": log.get("source_path", ""),
                        "dest_path": log.get("dest_path", "")
                    })
            if not payload:
                self.offline_queue.remove(log_id)
                continue
                
            try:
                resp = requests.post(f"{self.supabase_url}/rest/v1/fileevent", json=payload, headers=headers, timeout=5)
                if resp.status_code in [200, 201]:
                    self.offline_queue.remove(log_id)
            except:
                break # Network dropped back down
