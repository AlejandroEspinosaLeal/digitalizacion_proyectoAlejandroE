/* =========================================
   I18N.JS | Internationalization Logic
   ========================================= */

const translations = {
  en: {
    "nav.features": "Features",
    "nav.demo": "App Demo",
    "nav.login": "Log In",
    "nav.dashboard": "Dashboard",
    "nav.logout": "Log Out",
    "hero.badge": "Enterprise Automation",
    "hero.title": "Organize Your Files. Automatically.",
    "hero.subtitle": "File Sorter Enterprise is the automated digital organization system designed to maintain order across your entire company.",
    "hero.cta": "Create Account",
    "auth.signup_title": "Create Account",
    "auth.login_title": "Sign In",
    "auth.email_label": "Email Address",
    "auth.pass_label": "Password",
    "auth.submit_reg": "Register →",
    "auth.submit_log": "Log In →",
    "demo.tag": "How It Works",
    "demo.title": "See It In Action",
    "demo.desc": "Drop files into your monitored folder and the Rules Engine handles the rest seamlessly.",
    "demo.drop_title": "Drop Zone Simulation",
    "demo.drop_desc": "Click here to simulate sorting a new file.",
    "demo.rules_title": "Active Rules Engine",
    "demo.rules.doc": "Documents",
    "demo.rules.doc_ext": ".pdf, .docx, .xlsx",
    "demo.rules.img": "Images",
    "demo.rules.img_ext": ".png, .jpg, .svg",
    "demo.rules.vid": "Videos",
    "demo.rules.vid_ext": ".mp4, .mov, .avi",
    "toast.auth_success": "Authentication successful!",
    "toast.auth_err": "Authentication failed. Check your details.",
    "toast.sort_sim": "Organized into"
  },
  es: {
    "nav.features": "Características",
    "nav.demo": "Demo App",
    "nav.login": "Entrar",
    "nav.dashboard": "Panel de Control",
    "nav.logout": "Salir",
    "hero.badge": "Automatización Empresarial",
    "hero.title": "Organiza Tus Archivos. Automáticamente.",
    "hero.subtitle": "File Sorter Enterprise es el sistema automatizado de organización digital diseñado para mantener el orden en toda tu empresa.",
    "hero.cta": "Crear Cuenta",
    "auth.signup_title": "Crear Cuenta",
    "auth.login_title": "Iniciar Sesión",
    "auth.email_label": "Correo Electrónico",
    "auth.pass_label": "Contraseña",
    "auth.submit_reg": "Registrarse →",
    "auth.submit_log": "Entrar →",
    "demo.tag": "Cómo Funciona",
    "demo.title": "Míralo En Acción",
    "demo.desc": "Suelta los archivos en tu carpeta supervisada y el Motor de Reglas hace el resto sin complicaciones.",
    "demo.drop_title": "Simulación: Copiar Archivo",
    "demo.drop_desc": "Haz clic aquí para simular la organización de un archivo.",
    "demo.rules_title": "Motor de Reglas Activo",
    "demo.rules.doc": "Documentos",
    "demo.rules.doc_ext": ".pdf, .docx, .xlsx",
    "demo.rules.img": "Imágenes",
    "demo.rules.img_ext": ".png, .jpg, .svg",
    "demo.rules.vid": "Videos",
    "demo.rules.vid_ext": ".mp4, .mov, .avi",
    "toast.auth_success": "¡Autenticación exitosa!",
    "toast.auth_err": "Fallo en la autenticación. Revisa tus datos.",
    "toast.sort_sim": "Organizado en"
  }
};

let currentLang = localStorage.getItem("fse_lang") || "en";

function setLanguage(lang) {
  if (!translations[lang]) lang = "en";
  currentLang = lang;
  localStorage.setItem("fse_lang", lang);

  const langSelect = document.getElementById("lang-select");
  if (langSelect) langSelect.value = lang;
  
  updateTranslations();
}

function updateTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (translations[currentLang][key]) {
      el.textContent = translations[currentLang][key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (translations[currentLang][key]) {
      el.setAttribute("placeholder", translations[currentLang][key]);
    }
  });
}

function getTranslation(key) {
  return translations[currentLang][key] || key;
}

window.addEventListener("DOMContentLoaded", () => {
  setLanguage(currentLang);
  
  const select = document.getElementById("lang-select");
  if (select) {
    select.addEventListener("change", (e) => {
      setLanguage(e.target.value);
    });
  }
});
