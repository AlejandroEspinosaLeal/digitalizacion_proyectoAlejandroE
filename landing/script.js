/* =========================================
   SCRIPT.JS | File Sorter Enterprise
   ========================================= */

const SUPABASE_URL = 'https://dnbsgjmscuycjwrnknyj.supabase.co';
// WARNING: Exposed anon key for demo purposes.
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuYnNnam1zY3V5Y2p3cm5rbnlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1MTY5MDYsImV4cCI6MjA5MjA5MjkwNn0.M9bQLJRlbEzFQb39q3r8gTbktgMdOTlxX9nw9cy5NxU';

let supabaseClient = null;

try {
  if (window.supabase) {
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }
} catch (e) {
  console.warn("Supabase CDN blocked or unavailable.");
}

let authMode = "login"; // "login" or "register"

// Show Toast Notification
function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = msg;
  toast.style.borderLeft = `4px solid var(--${type})`;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

// Authentication Logic
async function handleAuth(e) {
  e.preventDefault();
  const email = document.getElementById("auth-email").value.trim();
  const password = document.getElementById("auth-password").value;
  const msgEl = document.getElementById("auth-msg");

  if (!email || !password) {
    msgEl.className = "auth-msg msg-error";
    msgEl.textContent = "Please fill in all fields.";
    return;
  }

  msgEl.className = "auth-msg msg-info";
  msgEl.textContent = "Working...";

  try {
    if (authMode === "login") {
      const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
      if (error) throw error;
      showToast(getTranslation("toast.auth_success"), "success");
      // Redirect to dashboard
      window.location.href = "dashboard.html";
    } else {
      const { data, error } = await supabaseClient.auth.signUp({ email, password });
      if (error) throw error;
      showToast("Account created successfully!", "success");
      msgEl.className = "auth-msg msg-success";
      msgEl.textContent = "Registration successful. You can now log in.";
      setAuthMode("login");
    }
  } catch (error) {
    msgEl.className = "auth-msg msg-error";
    msgEl.textContent = error.message;
    showToast(getTranslation("toast.auth_err"), "danger");
  }
}

function setAuthMode(mode) {
  authMode = mode;
  const tabLogin = document.getElementById("tab-login");
  const tabRegister = document.getElementById("tab-register");
  const btnSubmit = document.getElementById("auth-submit");
  const msgEl = document.getElementById("auth-msg");

  if (msgEl) msgEl.textContent = "";

  if (mode === "login") {
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
    btnSubmit.setAttribute("data-i18n", "auth.submit_log");
    btnSubmit.textContent = getTranslation("auth.submit_log");
  } else {
    tabRegister.classList.add("active");
    tabLogin.classList.remove("active");
    btnSubmit.setAttribute("data-i18n", "auth.submit_reg");
    btnSubmit.textContent = getTranslation("auth.submit_reg");
  }
}

// Check auth state on load
async function checkAuth() {
  if (!supabaseClient) return;
  const { data: { session } } = await supabaseClient.auth.getSession();

  if (session) {
    // If logged in on index, switch "Log in" button to "Dashboard"
    const navLogin = document.getElementById("nav-login-btn");
    if (navLogin) {
      navLogin.setAttribute("data-i18n", "nav.dashboard");
      navLogin.textContent = getTranslation("nav.dashboard");
      navLogin.href = "dashboard.html";
    }
  }
}

// File Sorting Simulation
function simulateSort() {
  const svgs = {
    img: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-500"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>`,
    doc: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>`,
    vid: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-500"><polygon points="23 7 16 12 23 17 23 7"/><rect width="15" height="14" x="1" y="5" rx="2" ry="2"/></svg>`,
    code: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-purple-500"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`
  };

  const files = [
    { icon: svgs.img, name: 'image_' + Math.floor(Math.random() * 100) + '.png', tag: 'Images', cls: 'bg-blue-50 text-blue-700 ring-1 ring-blue-700/10' },
    { icon: svgs.doc, name: 'report_' + Math.floor(Math.random() * 100) + '.pdf', tag: 'Docs', cls: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-700/10' },
    { icon: svgs.vid, name: 'clip_' + Math.floor(Math.random() * 100) + '.mp4', tag: 'Video', cls: 'bg-amber-50 text-amber-700 ring-1 ring-amber-700/10' },
    { icon: svgs.code, name: 'script_' + Math.floor(Math.random() * 100) + '.js', tag: 'Code', cls: 'bg-purple-50 text-purple-700 ring-1 ring-purple-700/10' }
  ];
  const f = files[Math.floor(Math.random() * files.length)];

  const container = document.getElementById("demo-card-container");
  if (!container) return;

  const card = document.createElement('div');
  card.className = 'flex items-center justify-between p-3 bg-white border border-zinc-100 rounded-xl shadow-sm transition-all duration-300 transform origin-left animate-[slideIn_0.3s_ease-out]';
  card.innerHTML = `
    <div class="flex items-center gap-3">
      <div class="flex items-center justify-center p-1.5 rounded-md bg-zinc-50 border border-zinc-100">
        ${f.icon}
      </div>
      <span class="text-sm font-medium text-zinc-700">${f.name}</span>
    </div>
    <span class="text-[11px] font-bold px-2.5 py-1 rounded-full ${f.cls}" data-i18n="demo.rules.${f.tag.toLowerCase()}">
      ${getTranslation(`demo.rules.${f.tag.toLowerCase()}`) || f.tag}
    </span>
  `;

  container.prepend(card);
  if (container.children.length > 4) {
    container.removeChild(container.lastChild);
  }

  showToast(`${getTranslation('toast.sort_sim')} ${f.tag}`, "info");
}

// Add a simple keyframe for slideIn
const styleObj = document.createElement('style');
styleObj.textContent = `@keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }`;
document.head.appendChild(styleObj);

window.addEventListener("DOMContentLoaded", () => {
  checkAuth();

  const authForm = document.getElementById("auth-form");
  if (authForm) {
    authForm.addEventListener("submit", handleAuth);
  }

  const tLogin = document.getElementById("tab-login");
  const tReg = document.getElementById("tab-register");
  if (tLogin) tLogin.addEventListener("click", () => setAuthMode("login"));
  if (tReg) tReg.addEventListener("click", () => setAuthMode("register"));
});
