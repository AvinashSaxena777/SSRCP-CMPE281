let speedChart;
let eventSource;

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    setupEventListeners();
    connectTelemetry();
});

function initChart() {
    const ctx = document.getElementById('speedChart').getContext('2d');
    speedChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Speed (km/h)',
                data: [],
                borderColor: '#4e73df',
                tension: 0.4
            }]
        }
    });
}



function setupEventListeners() {
    document.getElementById('spawnBtn').addEventListener('click', spawnVehicle);
    document.getElementById('destroyBtn').addEventListener('click', destroyVehicle);
    document.getElementById('startDriveBtn').addEventListener('click', startDrive);
    document.getElementById('stopDriveBtn').addEventListener('click', stopDrive);
    document.getElementById('attachCameraBtn').addEventListener('click', attachCamera);
    document.getElementById('detachCameraBtn').addEventListener('click', detachCamera);
}

let telemetrySource = null;
let videoStreamElement = null;

function connectTelemetry() {
    telemetrySource = new EventSource(`${API_BASE}/robots/${ROBOT_ID}/stream_data`);
    
    telemetrySource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateMetrics(data);
        updateChart(data.speed);
        updateLogs(data);
    };
}

function connectVideoStream() {
    videoStreamElement = document.getElementById('videoStream');
    videoStreamElement.src = `${API_BASE}/robots/${ROBOT_ID}/video_feed`;
}

function disconnectStreams() {
    if (telemetrySource) {
        telemetrySource.close();
        telemetrySource = null;
    }
    if (videoStreamElement) {
        videoStreamElement.src = '';
    }
}

// Initialize connections
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    connectTelemetry();
    connectVideoStream();
});

// Handle tab changes
document.querySelectorAll('[data-toggle="tab"]').forEach(tab => {
    tab.addEventListener('shown.bs.tab', (e) => {
        if (e.target.getAttribute('href') === '#stream') {
            connectVideoStream();
        }
    });
});
document.getElementById('stream-tab').addEventListener('shown.bs.tab', function() {
    document.getElementById('videoStream').style.display = 'block';
});

document.getElementById('logs-tab').addEventListener('shown.bs.tab', function() {
    document.getElementById('videoStream').style.display = 'none';
});

function updateMetrics(data) {
    document.getElementById('speed-value').textContent = `${data.speed.toFixed(1)} km/h`;
    document.getElementById('throttle-value').textContent = `${(data.throttle * 100).toFixed(0)}%`;
    document.getElementById('steering-value').textContent = `${(data.steering * 70).toFixed(0)}°`;
    document.getElementById('brake-value').textContent = `${(data.brake * 100).toFixed(0)}%`;
}

function updateChart(speed) {
    const labels = speedChart.data.labels;
    const dataset = speedChart.data.datasets[0];
    
    labels.push(new Date().toLocaleTimeString());
    dataset.data.push(speed);
    
    if (labels.length > 20) {
        labels.shift();
        dataset.data.shift();
    }
    
    speedChart.update();
}

function updateLogs(data) {
    const logElement = document.getElementById('telemetryLogs');
    const entry = `[${new Date().toLocaleTimeString()}] ` +
                  `Speed: ${data.speed.toFixed(1)}km/h ` +
                  `Throttle: ${(data.throttle * 100).toFixed(0)}% ` +
                  `Steering: ${(data.steering * 70).toFixed(0)}°`;
    
    logElement.innerHTML = entry + '<br>' + logElement.innerHTML;
}

async function spawnVehicle() {
    const x = document.getElementById('spawnX').value;
    const y = document.getElementById('spawnY').value;
    const z = document.getElementById('spawnZ').value;
    
    try {
        const response = await fetch(
            `${API_BASE}/robots/${ROBOT_ID}/spawn?x=${x}&y=${y}&z=${z}`,
            { method: 'POST' }
        );
        showAlert('Vehicle spawned successfully', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

async function destroyVehicle() {
    try {
        const response = await fetch(
            `${API_BASE}/robots/${ROBOT_ID}/destroy_vehicle`,
            { method: 'POST' }
        );
        showAlert('Vehicle destroyed', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

async function startDrive() {
    const x = document.getElementById('targetX').value;
    const y = document.getElementById('targetY').value;
    const z = document.getElementById('targetZ').value;
    
    try {
        const response = await fetch(
            `${API_BASE}/robots/${ROBOT_ID}/start_drive?x=${x}&y=${y}&z=${z}`,
            { method: 'POST' }
        );
        showAlert('Drive started', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

async function stopDrive() {
    try {
        const response = await fetch(
            `${API_BASE}/robots/${ROBOT_ID}/stop_drive`,
            { method: 'POST' }
        );
        showAlert('Drive stopped', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

async function attachCamera() {
    try {
        await fetch(`${API_BASE}/robots/${ROBOT_ID}/attach_camera`, { method: 'POST' });
        document.getElementById('videoStream').src = 
            `${API_BASE}/robots/${ROBOT_ID}/video_feed?t=${Date.now()}`;
        showAlert('Camera attached', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

async function detachCamera() {
    try {
        await fetch(`${API_BASE}/robots/${ROBOT_ID}/detach_camera`, { method: 'POST' });
        document.getElementById('videoStream').src = '';
        showAlert('Camera detached', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    document.body.prepend(alert);
    setTimeout(() => alert.remove(), 3000);
}
