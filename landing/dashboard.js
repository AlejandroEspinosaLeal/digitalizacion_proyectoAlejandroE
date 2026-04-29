/* =========================================
   DASHBOARD.JS | Logged User Area
   ========================================= */

const SUPABASE_URL = 'https://dnbsgjmscuycjwrnknyj.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuYnNnam1zY3V5Y2p3cm5rbnlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1MTY5MDYsImV4cCI6MjA5MjA5MjkwNn0.M9bQLJRlbEzFQb39q3r8gTbktgMdOTlxX9nw9cy5NxU';

let supabaseClient = null;

try {
  if (window.supabase) supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} catch (e) {
  console.warn("Supabase CDN blocked.");
}

// Ensure the user is logged in
async function initDashboard() {
  if (!supabaseClient) return redirectToIndex();

  const { data: { session }, error } = await supabaseClient.auth.getSession();

  if (error || !session) {
    return redirectToIndex();
  }

  // Display user email
  document.getElementById("user-email").textContent = session.user.email;

  // Bind logout
  document.getElementById("logout-btn").addEventListener("click", async () => {
    await supabaseClient.auth.signOut();
    redirectToIndex();
  });

  // Load activity
  loadActivityData(session.user);

  // Extra i18n injections for dashboard
  injectDashboardTranslations();
}

function redirectToIndex() {
  window.location.href = "index.html";
}

function getDerivedCategory(destPath) {
  if (!destPath) return 'Other';
  const parts = destPath.replace(/\\/g, '/').replace(/\/$/, '').split('/');
  return parts.length > 1 ? parts[parts.length - 2] : 'Other';
}

function iconForCat(cat) {
  if (/image/i.test(cat)) return '🖼️';
  if (/doc/i.test(cat)) return '📄';
  if (/code|script/i.test(cat)) return '💻';
  if (/video/i.test(cat)) return '🎬';
  return '📦';
}

function getExtension(filename) {
  if (!filename) return 'other';
  const parts = filename.split('.');
  if (parts.length > 1) {
    return parts.pop().toLowerCase();
  }
  return 'other';
}

let extensionChartInstance = null;

function renderChart(counts, total) {
  if (!window.Chart) return;
  const ctx = document.getElementById('extensionChart');
  if (!ctx) return;

  const labels = [];
  const data = [];
  const backgroundColors = [
    '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', 
    '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
  ];

  for (const [ext, count] of Object.entries(counts)) {
    const percentage = ((count / total) * 100).toFixed(1);
    labels.push(`${ext.toUpperCase()} (${percentage}%)`);
    data.push(count);
  }

  if (extensionChartInstance) {
    extensionChartInstance.destroy();
  }

  extensionChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: backgroundColors.slice(0, data.length),
        borderWidth: 1,
        borderColor: '#1e1e1e'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#a0a0a0' }
        },
        title: {
          display: true,
          text: 'File Extensions',
          color: '#ffffff'
        }
      }
    }
  });
}

async function loadActivityData(user) {
  const tbody = document.getElementById("activity-tbody");

  try {
    // 1. Get user's devices
    const { data: devices } = await supabaseClient.from('device').select('id').eq('user_id', user.id);
    const deviceIds = (devices || []).map(d => d.id);
    document.getElementById("kpi-devices").textContent = Math.max(deviceIds.length, 1); // fallback to 1

    let events = [];
    if (deviceIds.length > 0) {
      const { data } = await supabaseClient.from('fileevent')
        .select('*')
        .in('device_id', deviceIds)
        .order('timestamp', { ascending: false })
        .limit(50);
      if (data) events = data;
    }

    // fallback mock data if completely empty DB architecture
    if (events.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty-msg" data-i18n="dash.table.empty">No file movement events detected yet.</td></tr>`;
      document.getElementById("kpi-total").textContent = "0";
      return;
    }

    const categoriesUsed = new Set();
    const extensionCounts = {};
    let totalFilesForChart = 0;

    // Render Rows
    tbody.innerHTML = events.map(ev => {
      const cat = getDerivedCategory(ev.dest_path);
      categoriesUsed.add(cat);
      const icon = iconForCat(cat);

      const ext = getExtension(ev.filename);
      extensionCounts[ext] = (extensionCounts[ext] || 0) + 1;
      totalFilesForChart++;

      let dateString = "Unknown";
      if (ev.timestamp) {
        // ensure UTC appended for accurate browser conversion
        const tObj = new Date(ev.timestamp.endsWith('Z') ? ev.timestamp : ev.timestamp + 'Z');
        dateString = tObj.toLocaleString();
      }

      return `<tr>
        <td style="color:var(--text-primary); font-weight: 500;">
          <span style="margin-right:8px">${icon}</span> ${ev.filename || 'Unknown File'}
        </td>
        <td><span class="fc-tag" style="background:rgba(255,255,255,0.05); color:var(--text-secondary)">${cat}</span></td>
        <td style="color:var(--text-secondary); font-family: monospace; font-size: 0.85em; word-break: break-all; max-width: 250px; white-space: normal;">${ev.dest_path || 'Unknown'}</td>
        <td style="color:var(--text-secondary)">${dateString}</td>
      </tr>`;
    }).join("");

    document.getElementById("kpi-total").textContent = events.length;
    document.getElementById("kpi-cats").textContent = categoriesUsed.size;

    renderChart(extensionCounts, totalFilesForChart);

  } catch (error) {
    console.error("Dashboard DB fetch error:", error);
    tbody.innerHTML = `<tr><td colspan="4" class="empty-msg" style="color:var(--danger)">Error loading data.</td></tr>`;
  }
}

// Expanding translations dynamically
function injectDashboardTranslations() {
  translations.en = {
    ...translations.en,
    "dash.title": "Activity Dashboard",
    "dash.subtitle": "Live tracking of your enterprise file movements.",
    "dash.kpi.total": "Total Files Sorted",
    "dash.kpi.cats": "Categories Created",
    "dash.kpi.devices": "Active Agents",
    "dash.table.file": "File Name",
    "dash.table.category": "Target Category",
    "dash.table.path": "Destination Path",
    "dash.table.time": "Timestamp",
    "dash.table.loading": "Loading records...",
    "dash.table.empty": "No file movement events detected yet."
  };

  translations.es = {
    ...translations.es,
    "dash.title": "Panel de Actividad",
    "dash.subtitle": "Seguimiento en vivo de los movimientos de tus archivos.",
    "dash.kpi.total": "Archivos Organizados",
    "dash.kpi.cats": "Categorías Creadas",
    "dash.kpi.devices": "Dispositivos Activos",
    "dash.table.file": "Nombre del Archivo",
    "dash.table.category": "Categoría Destino",
    "dash.table.path": "Ruta de Destino",
    "dash.table.time": "Fecha / Hora",
    "dash.table.loading": "Cargando registros...",
    "dash.table.empty": "Aún no se han detectado movimientos de archivos."
  };

  updateTranslations();
}

window.addEventListener("DOMContentLoaded", initDashboard);
