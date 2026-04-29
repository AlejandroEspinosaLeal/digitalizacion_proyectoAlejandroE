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
  const userEmailEl = document.getElementById("user-email");
  if (userEmailEl) userEmailEl.textContent = session.user.email;

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
  const c = 'w-4 h-4 opacity-70';
  if (/image/i.test(cat)) return `<svg class="text-blue-500 ${c}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>`;
  if (/doc/i.test(cat)) return `<svg class="text-emerald-500 ${c}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>`;
  if (/code|script/i.test(cat)) return `<svg class="text-purple-500 ${c}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;
  if (/video/i.test(cat)) return `<svg class="text-amber-500 ${c}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect width="15" height="14" x="1" y="5" rx="2" ry="2"/></svg>`;
  return `<svg class="text-zinc-500 ${c}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" x2="12" y1="22.08" y2="12"/></svg>`;
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
    '#3b82f6', // accent-primary
    '#10b981', // success
    '#f59e0b', // warning
    '#8b5cf6', // info
    '#ef4444', // danger
    '#0ea5e9', // sky
    '#f43f5e', // rose
    '#14b8a6'  // teal
  ];
  
  // Adaptable al modo oscuro
  const isDark = document.documentElement.classList.contains('dark');
  const borderColors = Array(backgroundColors.length).fill(isDark ? '#18181b' : '#ffffff');

  for (const [ext, count] of Object.entries(counts)) {
    const percentage = ((count / total) * 100).toFixed(1);
    labels.push(`${ext.toUpperCase()} (${percentage}%)`);
    data.push(count);
  }

  if (extensionChartInstance) {
    extensionChartInstance.destroy();
  }

  // Use global defaults for better aesthetic
  const isDarkChart = document.documentElement.classList.contains('dark');
  Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
  Chart.defaults.color = isDarkChart ? '#a1a1aa' : '#52525b';

  extensionChartInstance = new Chart(ctx, {
    type: 'doughnut', // doughnut looks more modern
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: backgroundColors.slice(0, data.length),
        borderColor: borderColors.slice(0, data.length),
        borderWidth: 4,
        borderRadius: 4,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      cutout: '65%', // makes it a thin ring
      plugins: {
        legend: {
          position: 'bottom',
          labels: { 
            color: '#94a3b8',
            padding: 24,
            usePointStyle: true,
            pointStyle: 'circle',
            font: { size: 13 }
          }
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
      tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-8 text-center text-zinc-500 dark:text-zinc-400" data-i18n="dash.table.empty">No file movement events detected yet.</td></tr>`;
      document.getElementById("kpi-files").textContent = "0";
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
        <td class="px-6 py-4 border-t border-zinc-100 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 font-medium flex items-center gap-3">
          ${icon}
          ${ev.filename || 'Unknown File'}
        </td>
        <td class="px-6 py-4 border-t border-zinc-100 dark:border-zinc-800">
          <span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-zinc-100 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700">${cat}</span>
        </td>
        <td class="px-6 py-4 border-t border-zinc-100 dark:border-zinc-800 text-zinc-500 dark:text-zinc-400 font-mono text-xs max-w-[200px] sm:max-w-xs truncate" title="${ev.dest_path || 'Unknown'}">${ev.dest_path || 'Unknown'}</td>
        <td class="px-6 py-4 border-t border-zinc-100 dark:border-zinc-800 text-zinc-500 dark:text-zinc-400 text-right text-xs whitespace-nowrap">${dateString}</td>
      </tr>`;
    }).join("");

    document.getElementById("kpi-files").textContent = events.length;
    document.getElementById("kpi-cats").textContent = categoriesUsed.size;

    renderChart(extensionCounts, totalFilesForChart);

  } catch (error) {
    console.error("Dashboard DB fetch error:", error);
    tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-8 text-center text-red-500">Error loading data.</td></tr>`;
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
    "dash.table.empty": "No file movement events detected yet.",
    "dash.chart.title": "Distribution by Extension",
    "dash.chart.subtitle": "Visual breakdown of your sorted files"
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
    "dash.table.empty": "Aún no se han detectado movimientos de archivos.",
    "dash.chart.title": "Distribución por Extensión",
    "dash.chart.subtitle": "Desglose visual de los archivos organizados"
  };

  updateTranslations();
}

window.addEventListener("DOMContentLoaded", initDashboard);
