
let eventSource;
let speedChart = null;
let telemetrySource = null;
let videoStreamElement = null;
let isStreaming = false;
let spawnMarker = null;
let destMarker = null;
let currentMode = 'spawn'; // 'spawn' or 'destination'
let map; // Global map reference

function initMap() {
    if (map) map.remove();
    
    map = L.map('controlMap', {
        center: [37.3352, -121.8811],
        zoom: 15
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Initialize markers
    spawnMarker = null;
    destMarker = null;

    map.on('click', function(e) {
        const coords = e.latlng;
        if(currentMode === 'spawn') {
            if(spawnMarker) map.removeLayer(spawnMarker);
            spawnMarker = L.marker(coords, {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            }).addTo(map);
            document.getElementById('spawnCoords').textContent = 
                `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}`;
        } else {
            if(destMarker) map.removeLayer(destMarker);
            destMarker = L.marker(coords, {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            }).addTo(map);
            document.getElementById('destCoords').textContent = 
                `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}`;
        }
    });
}

Chart.register(ChartStreaming);


function initChart() {
    if (speedChart) {
        speedChart.destroy();
    }
    
    Chart.register(ChartStreaming);
    
    const ctx = document.getElementById('speedChart').getContext('2d');
    speedChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Speed (km/h)',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'realtime',
                    realtime: {
                        duration: 20000,
                        refresh: 1000
                    }
                },
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                streaming: {
                    duration: 20000
                }
            }
        }
    });
}


function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    // Get or create alert container
    let container = document.querySelector('.alert-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'alert-container';
        document.body.prepend(container);
    }
    
    container.prepend(alert);
    setTimeout(() => alert.remove(), 3000);
}


async function spawnVehicle() {
    if(!spawnMarker) {
        showAlert('Please set a spawn point on the map first!', 'danger');
        return;
      }
      
    const coords = spawnMarker.getLatLng();
    
    // const x = document.getElementById('spawnX').value;
    // const y = document.getElementById('spawnY').value;
    // const z = document.getElementById('spawnZ').value;
    const x = coords.lng;
    const y = coords.lat;
    const z = 0; // Assuming a flat surface for simplicity
    
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
    if(!destMarker) {
        showAlert('Please set a destination on the map first!', 'danger');
        return;
      }
    
    const coords = destMarker.getLatLng();
    // const x = document.getElementById('targetX').value;
    // const y = document.getElementById('targetY').value;
    // const z = document.getElementById('targetZ').value;
    
    const x = coords.lng;
    const y = coords.lat; 
    const z = 0; // Assuming a flat surface for simplicity        
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

// function setupEventListeners() {
//     document.getElementById('spawnBtn').addEventListener('click', spawnVehicle);
//     document.getElementById('destroyBtn').addEventListener('click', destroyVehicle);
//     document.getElementById('startDriveBtn').addEventListener('click', startDrive);
//     document.getElementById('stopDriveBtn').addEventListener('click', stopDrive);
//     document.getElementById('attachCameraBtn').addEventListener('click', attachCamera);
//     document.getElementById('detachCameraBtn').addEventListener('click', detachCamera);
// }

function updateMetrics(data) {
    document.getElementById('speed-value').textContent = `${data.speed.toFixed(1)} km/h`;
    document.getElementById('throttle-value').textContent = `${(data.throttle * 100).toFixed(0)}%`;
    document.getElementById('steering-value').textContent = `${(data.steering * 70).toFixed(0)}°`;
    document.getElementById('brake-value').textContent = `${(data.brake * 100).toFixed(0)}%`;
}
function updateChart(speed) {
    const now = Date.now();
    speedChart.data.datasets[0].data.push({
        x: now,
        y: speed
    });
    
    // Keep only visible data points
    const firstTimestamp = speedChart.data.datasets[0].data[0]?.x;
    if (firstTimestamp && now - firstTimestamp > 20000) {
        speedChart.data.datasets[0].data.shift();
    }
    
    speedChart.update('quiet');
}


function updateLogs(data) {
    const logElement = document.getElementById('telemetryLogs');
    const entry = `[${new Date().toLocaleTimeString()}] ` +
                  `Speed: ${data.speed.toFixed(1)}km/h ` +
                  `Throttle: ${(data.throttle * 100).toFixed(0)}% ` +
                  `Steering: ${(data.steering * 70).toFixed(0)}°`;
    
    logElement.innerHTML = entry + '<br>' + logElement.innerHTML;
}
function connectTelemetry() {
    telemetrySource = new EventSource(`${API_BASE}/robots/${ROBOT_ID}/stream_data`);
    
    telemetrySource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateMetrics(data);
        updateChart(data.speed);
        updateLogs(data);
    };
}

// document.addEventListener('DOMContentLoaded', () => {
//     initChart();
//     setupEventListeners();
//     connectTelemetry();
// });

// Enhanced Alert System

async function startVideo() {
    try {
        // 1. Attach camera if not already attached
        await attachCamera();
        
        // 2. Start streaming through API
        const response = await fetch(`${API_BASE}/robots/${ROBOT_ID}/start_streaming`, { 
            method: 'POST' 
        });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.message || "Stream start failed");
        
        // 3. Start displaying video feed
        videoStreamElement = document.getElementById('videoStream');
        videoStreamElement.src = `${API_BASE}/robots/${ROBOT_ID}/video_feed?t=${Date.now()}`;
        isStreaming = true;
        
        showAlert("Video streaming started", "success");
    } catch (error) {
        showAlert(`Video Error: ${error.message}`, "danger");
    }
}

async function stopVideo() {
    try {
        // 1. Stop through API
        const response = await fetch(`${API_BASE}/robots/${ROBOT_ID}/stop_streaming`, { 
            method: 'POST' 
        });
        const data = await response.json();
        
        // 2. Clear video element
        if (videoStreamElement) {
            videoStreamElement.src = '';
        }
        isStreaming = false;
        
        showAlert("Video streaming stopped", "success");
    } catch (error) {
        showAlert(`Stop Video Error: ${error.message}`, "danger");
    }
}


function connectVideoStream() {
    videoStreamElement = document.getElementById('videoStream');
    videoStreamElement.src = `${API_BASE}/robots/${ROBOT_ID}/video_feed`;
}

// function disconnectStreams() {
//     if (telemetrySource) {
//         telemetrySource.close();
//         telemetrySource = null;
//     }
//     if (videoStreamElement) {
//         videoStreamElement.src = '';
//     }
// }
// Initialize without auto-connecting
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initChart();
    connectTelemetry();
    // setupEventListeners();
    videoStreamElement = document.getElementById('videoStream');
    // Mode button handlers
    document.getElementById('setSpawnBtn').addEventListener('click', function() {
        currentMode = 'spawn';
        this.classList.add('active');
        document.getElementById('setDestinationBtn').classList.remove('active');
    });

    document.getElementById('setDestinationBtn').addEventListener('click', function() {
        currentMode = 'destination';
        this.classList.add('active');
        document.getElementById('setSpawnBtn').classList.remove('active');
    });
});

function toggleVideoStream() {
    const btn = document.getElementById('startVideoBtn');
    if (btn.dataset.streaming === "false") {
        startVideo();
        btn.dataset.streaming = "true";
        btn.textContent = "Stop Video";
    } else {
        stopVideo();
        btn.dataset.streaming = "false";
        btn.textContent = "Start Video";
    }
}


// Handle tab changes
document.querySelectorAll('[data-toggle="tab"]').forEach(tab => {
    tab.addEventListener('shown.bs.tab', (e) => {
        if (e.target.getAttribute('href') === '#stream') {
            connectVideoStream();
        }
    });
});

// document.getElementById('stream-tab').addEventListener('shown.bs.tab', function() {
//     document.getElementById('videoStream').style.display = 'block';
// });

// document.getElementById('logs-tab').addEventListener('shown.bs.tab', function() {
//     document.getElementById('videoStream').style.display = 'none';
// });




