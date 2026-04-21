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
  const files = [
    { icon: '🖼️', name: 'image_' + Math.floor(Math.random() * 100) + '.png', tag: 'Images', cls: 'tag-img' },
    { icon: '📄', name: 'report_' + Math.floor(Math.random() * 100) + '.pdf', tag: 'Docs', cls: 'tag-doc' },
    { icon: '🎬', name: 'clip_' + Math.floor(Math.random() * 100) + '.mp4', tag: 'Video', cls: 'tag-vid' },
    { icon: '💻', name: 'script_' + Math.floor(Math.random() * 100) + '.js', tag: 'Code', cls: 'tag-code' }
  ];
  const f = files[Math.floor(Math.random() * files.length)];

  const container = document.getElementById("demo-card-container");
  if (!container) return;

  const card = document.createElement('div');
  card.className = 'file-card';
  card.innerHTML = `
    <div class="fc-left">
      <span class="fc-icon">${f.icon}</span>
      <span class="fc-name">${f.name}</span>
    </div>
    <span class="fc-tag ${f.cls}" data-i18n="demo.rules.${f.tag.toLowerCase()}">
      ${getTranslation(`demo.rules.${f.tag.toLowerCase()}`) || f.tag}
    </span>
  `;

  container.prepend(card);
  if (container.children.length > 4) {
    container.removeChild(container.lastChild);
  }

  showToast(`${getTranslation('toast.sort_sim')} ${f.tag}`, "info");
}

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
