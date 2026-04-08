import sys

class AppState:
    """Centralized State Manager for the Enterprise Agent."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        self.token = None
        self.user_email = None
        self.device_id = "PC-LOCAL-01"
        self.api_url = "http://127.0.0.1:8000"
        self.monitor_folder = ""
        self.backend_pid = None
        
        # Try finding backend PID from sys args
        if "--backend-pid" in sys.argv:
            try:
                idx = sys.argv.index("--backend-pid")
                self.backend_pid = int(sys.argv[idx + 1])
            except (ValueError, IndexError):
                pass
