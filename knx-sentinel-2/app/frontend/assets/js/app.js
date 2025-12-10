// --- Config & State ---
const MAX_ROWS = 500;
const CHART_HISTORY_POINTS = 30; // 30 seconds of live data on chart

const state = {
    connected: false,
    paused: false,
    msgCount: 0,
    startTime: new Date(),
    chartData: Array(CHART_HISTORY_POINTS).fill(0),
    telegrams: [] // Not strictly needed to store all if we just append to DOM, but good for pause logic if we wanted filtering
};

// --- DOM Elements ---
const dom = {
    statusBadge: document.getElementById('status-badge'),
    statusText: document.getElementById('status-text'),
    tableBody: document.getElementById('log-table-body'),
    totalDisplay: document.getElementById('stat-total'),
    rateDisplay: document.getElementById('stat-rate'),
    btnPause: document.getElementById('btn-pause'),
    btnClear: document.getElementById('btn-clear')
};

// --- Chart Setup (Requires Chart.js loaded globally) ---
let trafficChart;

function initChart() {
    const ctx = document.getElementById('trafficChart').getContext('2d');

    // Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(0, 229, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(0, 229, 255, 0.0)');

    trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(CHART_HISTORY_POINTS).fill(''),
            datasets: [{
                label: 'Telegrams',
                data: state.chartData,
                borderColor: '#00e5ff',
                backgroundColor: gradient,
                borderWidth: 2,
                pointRadius: 0,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: {
                    display: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    suggestedMax: 10
                }
            },
            animation: { duration: 0 }
        }
    });

    // Update Chart Interval (Every 1s push current rate and reset)
    setInterval(() => {
        // Shift data
        trafficChart.data.datasets[0].data.shift();
        trafficChart.data.datasets[0].data.push(currentSecondCount);
        trafficChart.update();

        // Update Rate Display
        dom.rateDisplay.innerText = `${currentSecondCount} /s`;

        // Reset counter
        currentSecondCount = 0;
    }, 1000);
}

let currentSecondCount = 0;

// --- WebSocket ---
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/telegrams`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        state.connected = true;
        updateStatusUI();
        console.log('WS Connected');
    };

    socket.onmessage = (event) => {
        if (state.paused) return;
        const data = JSON.parse(event.data);
        processTelegram(data);
    };

    socket.onclose = () => {
        state.connected = false;
        updateStatusUI();
        setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = (e) => console.error("WS Error", e);
}

// --- Logic ---
function processTelegram(data) {
    state.msgCount++;
    currentSecondCount++;
    dom.totalDisplay.innerText = state.msgCount.toLocaleString();

    addTableRow(data);
}

function addTableRow(data) {
    const row = document.createElement('tr');

    // Formatting
    const time = new Date(data.timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const dirClass = data.direction === 'Incoming' ? 'dir-in' : 'dir-out';
    const arrow = data.direction === 'Incoming' ? '↓' : '↑';

    row.innerHTML = `
        <td style="color: var(--text-secondary); font-family: monospace;">${time}</td>
        <td class="${dirClass}" style="font-weight: bold;">${arrow} ${data.direction || 'Unknown'}</td>
        <td style="font-family: monospace;">${data.source}</td>
        <td style="font-family: monospace;">${data.destination}</td>
        <td><span class="type-badge">${data.type}</span></td>
        <td class="payload-text">${data.payload || '-'}</td>
    `;

    // Prepend
    dom.tableBody.insertBefore(row, dom.tableBody.firstChild);

    // Limit
    if (dom.tableBody.children.length > MAX_ROWS) {
        dom.tableBody.removeChild(dom.tableBody.lastChild);
    }
}

function updateStatusUI() {
    if (state.connected) {
        dom.statusBadge.className = 'status-badge connected';
        dom.statusText.innerText = 'Connected';
    } else {
        dom.statusBadge.className = 'status-badge disconnected';
        dom.statusText.innerText = 'Disconnected';
    }
}

// --- Fetch History ---
async function fetchHistory() {
    try {
        const res = await fetch('/api/history');
        const history = await res.json();
        // Reverse needed because we prepend
        for (let i = history.length - 1; i >= 0; i--) {
            processTelegram(history[i]);
        }
    } catch (e) {
        console.error("Fetch history failed", e);
    }
}

// --- Listeners ---
dom.btnPause.addEventListener('click', () => {
    state.paused = !state.paused;
    dom.btnPause.classList.toggle('active');
    dom.btnPause.innerHTML = state.paused
        ? `<svg style="width:16px;height:16px;fill:currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Resume`
        : `<svg style="width:16px;height:16px;fill:currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> Pause`;
});

dom.btnClear.addEventListener('click', () => {
    dom.tableBody.innerHTML = '';
    // Optional: Reset stats?
    // state.msgCount = 0;
    // dom.totalDisplay.innerText = '0';
});

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    fetchHistory();
    connectWebSocket();
});
