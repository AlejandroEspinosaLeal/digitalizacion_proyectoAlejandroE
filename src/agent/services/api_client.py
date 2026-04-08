import requests
import json
from src.agent.models.state import AppState
from src.agent.services.offline_queue import OfflineQueue

class APIClient:
    """Unified HTTP Client for interfacing with the FastAPI backend."""
    
    def __init__(self):
        self.app_state = AppState()
        self.offline_queue = OfflineQueue()
        
    def login(self, email, password):
        resp = requests.post(f"{self.app_state.api_url}/auth/token", json={"email": email, "hashed_password": password})
        return resp.json(), resp.status_code

    def verify_code(self, email, code):
        resp = requests.post(f"{self.app_state.api_url}/auth/verify", json={"email": email, "code": code})
        return resp.json(), resp.status_code

    def register(self, email, password):
        resp = requests.post(f"{self.app_state.api_url}/auth/register", json={"email": email, "hashed_password": password})
        return resp.json(), resp.status_code

    def forgot_password(self, email):
        resp = requests.post(f"{self.app_state.api_url}/auth/forgot-password", json={"email": email})
        return resp.json(), resp.status_code

    def reset_password(self, email, code, new_password):
        resp = requests.post(f"{self.app_state.api_url}/auth/reset-password", json={"email": email, "code": code, "new_password": new_password})
        return resp.json(), resp.status_code

    def send_log_report(self, logs_payload):
        if not self.app_state.token:
            return None
            
        headers = {"Authorization": f"Bearer {self.app_state.token}"}
        req_data = {
            "device_id": self.app_state.device_id, 
            "logs": logs_payload, 
            "folder": self.app_state.monitor_folder
        }
        
        try:
            resp = requests.post(f"{self.app_state.api_url}/devices/log/report", json=req_data, headers=headers, timeout=5)
            resp.raise_for_status()
            self.sync_offline_logs()
            return resp
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            self.offline_queue.push(req_data)
            raise ConnectionError("Backend offline. Saved in local resolution queue.")

    def sync_offline_logs(self):
        """Called automatically when a network request is successful."""
        pending = self.offline_queue.get_pending()
        if not pending: 
            return
            
        headers = {"Authorization": f"Bearer {self.app_state.token}"}
        for log_id, payload_str in pending:
            payload = json.loads(payload_str)
            try:
                resp = requests.post(f"{self.app_state.api_url}/devices/log/report", json=payload, headers=headers, timeout=5)
                if resp.status_code in [200, 201]:
                    self.offline_queue.remove(log_id)
            except:
                break # Network dropped back down
