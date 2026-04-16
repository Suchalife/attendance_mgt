/**
 * Operations Dashboard JavaScript
 * Fetches real-time data from backend API and updates KPIs, chart, and activity feed
 */

const POLL_INTERVAL = 5000;
let pollIntervalId;

document.addEventListener('DOMContentLoaded', () => {
    if (typeof router !== 'undefined' && router.setupNavigation) {
        router.setupNavigation();
    }

    fetchDashboardData();
    startPolling();
});

async function fetchDashboardData() {
    try {
        const data = await (typeof apiClient !== 'undefined'
            ? apiClient.getAttendanceStats()
            : fetch('/api/attendance/stats').then(r => r.json()));

        if (!data.success) return;

        updateKPIs(data.stats);
        updateChart(data.weekly_trend, data.stats.total_employees);
        updateActivityFeed(data.recent_activity);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

function updateKPIs(stats) {
    const el = (id) => document.getElementById(id);

    el('kpi-total-employees').textContent = stats.total_employees.toLocaleString();
    el('kpi-present-today').textContent = stats.present_today.toLocaleString();
    el('kpi-absent-today').textContent = stats.absent_today.toLocaleString();
    el('kpi-avg-attendance').textContent = stats.avg_attendance_pct + '%';

    const bar = el('kpi-avg-bar');
    if (bar) {
        bar.style.width = Math.min(stats.avg_attendance_pct, 100) + '%';
    }
}

function updateChart(trend, totalEmployees) {
    const container = document.getElementById('attendance-chart');
    if (!container || !trend || trend.length === 0) return;

    const maxCount = Math.max(...trend.map(d => d.count), 1);
    const isToday = (dateStr) => dateStr === new Date().toISOString().slice(0, 10);

    // Keep the grid lines, remove old bars
    const gridLines = container.querySelector('.absolute');
    container.innerHTML = '';
    if (gridLines) container.appendChild(gridLines);

    trend.forEach(day => {
        const heightPct = Math.max((day.count / maxCount) * 90, 2);
        const today = isToday(day.date);

        const col = document.createElement('div');
        col.className = 'flex flex-col items-center group w-full h-full justify-end';

        const label = document.createElement('span');
        label.className = `text-[9px] font-bold mb-1 ${today ? 'text-primary' : 'text-on-surface-variant'}`;
        label.textContent = day.count;

        const bar = document.createElement('div');
        bar.className = `w-8 rounded-t-sm transition-colors ${today ? 'bg-primary' : 'bg-surface-container-high group-hover:bg-primary'}`;
        bar.style.height = heightPct + '%';

        const dayLabel = document.createElement('span');
        dayLabel.className = 'text-[10px] font-bold text-on-surface-variant mt-2 uppercase tracking-tighter';
        dayLabel.textContent = day.day;

        col.appendChild(label);
        col.appendChild(bar);
        col.appendChild(dayLabel);
        container.appendChild(col);
    });
}

function updateActivityFeed(records) {
    const feed = document.getElementById('activity-feed');
    const lastUpdated = document.getElementById('activity-last-updated');
    if (!feed) return;

    if (!records || records.length === 0) {
        feed.innerHTML = '<div class="p-4 text-center text-sm text-on-surface-variant">No recent activity</div>';
        if (lastUpdated) lastUpdated.textContent = 'No records yet';
        return;
    }

    if (lastUpdated) {
        lastUpdated.textContent = 'Last updated just now';
    }

    feed.innerHTML = records.map(record => {
        const timestamp = record.timestamp || '';
        const time = timestamp.includes(' ') ? timestamp.split(' ')[1].slice(0, 5) : '--:--';
        const name = record.employeeName || 'Unknown';
        const empId = record.employeeId || '--';
        const status = record.status || 'Present';

        const statusClass = status === 'Present'
            ? 'bg-tertiary-container/10 text-tertiary-fixed-dim'
            : 'bg-error-container/20 text-error';
        const statusLabel = status === 'Present' ? 'In-Time' : 'Out-Time';

        return `
        <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex items-center space-x-4">
            <div class="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center">
                <span class="material-symbols-outlined text-on-surface-variant">person</span>
            </div>
            <div class="flex-1">
                <div class="flex justify-between">
                    <span class="text-xs font-bold text-on-surface">${escapeHtml(name)}</span>
                    <span class="text-[10px] font-mono text-on-surface-variant">${escapeHtml(time)}</span>
                </div>
                <div class="flex justify-between items-center mt-1">
                    <span class="text-[10px] font-mono text-on-surface-variant">${escapeHtml(empId)}</span>
                    <span class="px-1.5 py-0.5 ${statusClass} text-[9px] font-bold rounded-sm uppercase tracking-wide">${statusLabel}</span>
                </div>
            </div>
        </div>`;
    }).join('');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function startPolling() {
    if (pollIntervalId) clearInterval(pollIntervalId);
    pollIntervalId = setInterval(fetchDashboardData, POLL_INTERVAL);
}

window.addEventListener('beforeunload', () => {
    if (pollIntervalId) clearInterval(pollIntervalId);
});
