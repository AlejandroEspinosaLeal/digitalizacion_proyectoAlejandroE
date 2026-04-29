import customtkinter as ctk
from src.agent.models.theme import Theme
from src.agent.services.api_client import APIClient
from src.agent.models.state import AppState
from src.agent.views.apple_components import AppleCard, AppleHeading, AppleInput, AppleButton, AppleSubText

class AuthView(ctk.CTkFrame):
    """
    Component view responsible for handling User Authentication (Login, Register, and Password Recovery).
    Communicates with the central API and dispatches events upon completion.
    """
    def __init__(self, master, on_authenticated):
        super().__init__(master, fg_color="transparent")
        self.api = APIClient()
        self.app_state = AppState()
        self.on_authenticated = on_authenticated
        
        self.auth_container = AppleCard(self, width=400, height=520)
        self.auth_container.pack(expand=True)
        self.auth_container.pack_propagate(False)
        self.draw_auth_form("login")

    def show_msg(self, text, color):
        if color == "red": color = Theme.DANGER
        elif color == "green": color = Theme.SUCCESS
        elif color == "yellow": color = "#F59E0B"
        else: color = Theme.MUTED
        self.lbl_msg.configure(text=text, text_color=color)

    def create_password_field(self, parent, placeholder, width=300, height=45):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        entry = AppleInput(frame, placeholder_text=placeholder, width=width-50)
        entry.pack(side="left")
        
        btn_show = ctk.CTkButton(frame, text="👁", width=40, height=height, fg_color=Theme.INPUT, hover_color=Theme.BG, text_color=Theme.TEXT)
        btn_show.pack(side="left", padx=(5, 0))
        
        def toggle_pwd():
            if entry.cget("show") == "•":
                entry.configure(show="")
                btn_show.configure(text="🔒")
            else:
                entry.configure(show="•")
                btn_show.configure(text="👁")
                
        btn_show.configure(command=toggle_pwd)
        return frame, entry

    def draw_auth_form(self, mode="login"):
        for widget in self.auth_container.winfo_children(): widget.destroy()
        
        AppleHeading(self.auth_container, text="File Governance System").pack(pady=(40, 5))
        self.lbl_msg = AppleSubText(self.auth_container, text=f"{'Login' if mode=='login' else ('Register' if mode=='register' else 'Recover your account')}", size=14)
        self.lbl_msg.pack(pady=(0, 25))
        
        if mode in ["login", "register"]:
            tab_frame = ctk.CTkFrame(self.auth_container, fg_color="transparent")
            tab_frame.pack(pady=5)
            c1 = Theme.PRIMARY if mode=="login" else "transparent"
            c2 = Theme.PRIMARY if mode=="register" else "transparent"
            
            ctk.CTkButton(tab_frame, text="Sign In", fg_color=c1, hover_color=Theme.PRIMARY_HOVER, text_color=Theme.TEXT, width=130, height=35, corner_radius=10, command=lambda: self.draw_auth_form("login")).pack(side="left", padx=5)
            ctk.CTkButton(tab_frame, text="Sign Up", fg_color=c2, hover_color=Theme.PRIMARY_HOVER, text_color=Theme.TEXT, width=130, height=35, corner_radius=10, command=lambda: self.draw_auth_form("register")).pack(side="left", padx=5)

        if mode == "reset":
            self.draw_reset_fields()
            return
            
        self.auth_email = AppleInput(self.auth_container, placeholder_text="Email Address", width=300)
        self.auth_email.pack(pady=(20, 10))
        
        self.pwd_frame, self.auth_password = self.create_password_field(self.auth_container, "Password", width=300, height=45)
        self.pwd_frame.pack(pady=10)
        
        if mode == "login":
            self.btn_action = AppleButton(self.auth_container, text="Enter", width=300, command=self.do_login)
            self.btn_action.pack(pady=(25, 15))
            ctk.CTkButton(self.auth_container, text="Forgot your password?", fg_color="transparent", text_color=Theme.MUTED, hover_color=Theme.BG, command=lambda: self.draw_auth_form("reset")).pack()
        else:
            self.btn_action = AppleButton(self.auth_container, text="Create Account", variant="success", width=300, command=self.do_register)
            self.btn_action.pack(pady=(25, 15))

    def draw_reset_fields(self):
        self.auth_email = AppleInput(self.auth_container, placeholder_text="Email Address", width=300)
        self.auth_email.pack(pady=(15, 10))
        
        self.btn_send_reset = AppleButton(self.auth_container, text="Send Code", width=300, command=self.do_send_reset)
        self.btn_send_reset.pack(pady=5)
        
        self.reset_box = ctk.CTkFrame(self.auth_container, fg_color="transparent")
        
        self.reset_code = AppleInput(self.reset_box, placeholder_text="6-digit Code", width=300)
        self.reset_code.pack(pady=5)
        self.reset_pwd1_frame, self.reset_pwd1 = self.create_password_field(self.reset_box, "New Password", width=300, height=40)
        self.reset_pwd1_frame.pack(pady=5)
        self.reset_pwd2_frame, self.reset_pwd2 = self.create_password_field(self.reset_box, "Confirm", width=300, height=40)
        self.reset_pwd2_frame.pack(pady=5)
        self.btn_reset_confirm = AppleButton(self.reset_box, text="Change Password", variant="success", width=300, command=self.do_confirm_reset)
        self.btn_reset_confirm.pack(pady=15)
        
        ctk.CTkButton(self.auth_container, text="Back to Login", fg_color="transparent", text_color=Theme.MUTED, hover_color=Theme.BG, command=lambda: self.draw_auth_form("login")).pack(side="bottom", pady=20)

    def do_login(self):
        email, pwd = self.auth_email.get(), self.auth_password.get()
        self.show_msg("Connecting...", "white")
        try:
            data, status_code = self.api.login(email, pwd)
            if status_code == 200:
                if data.get("status") == "pending_verification":
                    self.show_msg(data.get("message"), "yellow")
                    self.pwd_frame.pack_forget()
                    self.btn_action.pack_forget()
                    self.login_code = AppleInput(self.auth_container, placeholder_text="Verification code via email", width=300)
                    self.login_code.pack(pady=10)
                    btn_v = AppleButton(self.auth_container, text="Verify", variant="success", width=300, command=self.verify_code)
                    btn_v.pack(pady=15)
                elif data.get("status") == "requires_reset":
                    self.show_msg(data.get("message"), "yellow")
                    self.draw_auth_form("reset")
                    self.auth_email.insert(0, email)
                    self.btn_send_reset.pack_forget()
                    self.reset_box.pack(fill="both", expand=True)
                else:
                    self.finish_auth(data.get("access_token"), email)
            else: self.show_msg(data.get("detail", "Error"), "red")
        except Exception as e: self.show_msg(f"Connection failed: {e}", "red")

    def verify_code(self):
        email, code = self.auth_email.get(), self.login_code.get()
        self.show_msg("Verifying...", "white")
        try:
            data, status = self.api.verify_code(email, code)
            if status == 200: self.finish_auth(data.get("access_token"), email)
            else: self.show_msg(data.get("detail", "Incorrect code."), "red")
        except Exception as e: self.show_msg(f"Connection failed: {e}", "red")

    def do_register(self):
        email, pwd = self.auth_email.get(), self.auth_password.get()
        self.show_msg("Registering...", "white")
        try:
            data, status = self.api.register(email, pwd)
            if status == 201:
                self.draw_auth_form("login")
                self.auth_email.insert(0, email)
                self.show_msg("Account created! Check your email when logging in.", "green")
            else:
                e = data.get("detail", "Error")
                self.show_msg(str(e[0] if isinstance(e, list) else e), "red")
        except Exception as e: self.show_msg(f"Connection failed: {e}", "red")

    def do_send_reset(self):
        email = self.auth_email.get()
        self.show_msg("Requesting code...", "white")
        try:
            self.api.forgot_password(email)
            self.show_msg("Check your email.", "yellow")
            self.btn_send_reset.pack_forget()
            self.reset_box.pack(fill="both", expand=True, pady=10)
        except Exception as e: self.show_msg(f"Connection failed: {e}", "red")

    def do_confirm_reset(self):
        email, code = self.auth_email.get(), self.reset_code.get()
        pwd1, pwd2 = self.reset_pwd1.get(), self.reset_pwd2.get()
        if pwd1 != pwd2:
            self.show_msg("Passwords do not match.", "red")
            return
        self.show_msg("Resetting...", "white")
        try:
            data, status = self.api.reset_password(email, code, pwd1)
            if status == 200: self.finish_auth(data.get("access_token"), email)
            else: self.show_msg(data.get("detail", "Error"), "red")
        except Exception as e: self.show_msg(f"Connection failed: {e}", "red")
        
    def finish_auth(self, token, email):
        self.app_state.token = token
        self.app_state.user_email = email
        self.on_authenticated()
