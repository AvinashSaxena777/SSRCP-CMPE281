document.addEventListener('DOMContentLoaded', function() {
    let map;
    let markers = [];

    // Initialize Map
    function initMap() {
        map = L.map('analyticsMap').setView([37.3352, -121.8811], 13);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add markers from Django template context
        {% for analytic in analytics %}
        {% if analytic.latitude and analytic.longitude %}
        const marker = L.marker([{{ analytic.latitude }}, {{ analytic.longitude }}], {
            icon: L.icon({
                iconUrl: '{% if analytic.resolved %}/static/assets/img/marker-green.png{% else %}/static/assets/img/marker-red.png{% endif %}',
                iconSize: [32, 41],
                iconAnchor: [16, 41]
            }),
            detectionType: '{{ analytic.detection_type }}',
            severity: '{{ analytic.severity }}',
            resolved: {{ analytic.resolved|yesno:"true,false" }},
            image: '{{ analytic.image.url }}',
            timestamp: '{{ analytic.created_at|date:"M d, Y H:i" }}'
        }).addTo(map);
        
        marker.on('click', function(e) {
            showDetails(e.target.options, e.latlng);
        });
        
        markers.push(marker);
        {% endif %}
        {% endfor %}
    }

    // Show Details Modal
    function showDetails(data, coords) {
        const statusHtml = data.resolved ? 
            '<span class="text-success">Resolved</span>' : 
            '<span class="text-danger">Unresolved</span>';
        
        document.getElementById('detailImage').src = data.image;
        document.getElementById('detailType').textContent = data.detectionType.charAt(0).toUpperCase() + data.detectionType.slice(1);
        document.getElementById('detailSeverity').textContent = data.severity;
        document.getElementById('detailStatus').innerHTML = statusHtml;
        document.getElementById('detailTimestamp').textContent = data.timestamp;
        document.getElementById('detailCoords').textContent = 
            `${coords.lat.toFixed(4)}, ${coords.lng.toFixed(4)}`;
        
        $('#detailModal').modal('show');
    }

    // Filter Markers
    function filterMarkers() {
        const typeFilter = document.getElementById('filterType').value;
        const severityFilter = document.getElementById('filterSeverity').value;
        const resolvedFilter = document.getElementById('filterResolved').value;

        markers.forEach(marker => {
            const matchType = typeFilter === 'all' || marker.options.detectionType === typeFilter;
            const matchSeverity = severityFilter === 'all' || marker.options.severity === severityFilter;
            const matchResolved = resolvedFilter === 'all' || 
                (resolvedFilter === 'true' && marker.options.resolved) ||
                (resolvedFilter === 'false' && !marker.options.resolved);

            if (matchType && matchSeverity && matchResolved) {
                if (!map.hasLayer(marker)) marker.addTo(map);
            } else {
                if (map.hasLayer(marker)) map.removeLayer(marker);
            }
        });
    }

    // Initialize
    initMap();
    
    // Add filter event listeners
    document.getElementById('filterType').addEventListener('change', filterMarkers);
    document.getElementById('filterSeverity').addEventListener('change', filterMarkers);
    document.getElementById('filterResolved').addEventListener('change', filterMarkers);
    
    // Handle window resize
    window.addEventListener('resize', () => map.invalidateSize());
});
