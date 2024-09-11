
let map = L.map('map').setView([28.7041, 77.1025], 13); 

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let userMarker;


function addSaferZoneMarkers(shops) {
 
    map.eachLayer(function(layer) {
        if (layer.options && layer.options.pane === "markerPane" && layer !== userMarker) {
            map.removeLayer(layer);
        }
    });

    shops.forEach(shop => {
        const marker = L.marker([shop.lat, shop.lon], {
            icon: L.icon({
                iconUrl: shop.predicted_safe_zone === 1 ? 'https://maps.google.com/mapfiles/ms/icons/green-dot.png' : 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32],
            })
        }).addTo(map);
        marker.bindPopup(`<b>${shop.name}</b><br>Safe Zone: ${shop.predicted_safe_zone === 1 ? 'Yes' : 'No'}`);
    });
}


document.getElementById('findLocationBtn').addEventListener('click', () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendLocation, handleLocationError);
    } else {
        alert("Geolocation is not supported by your browser.");
    }
});


function sendLocation(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    map.setView([lat, lon], 15);


    if (userMarker) {
        userMarker.setLatLng([lat, lon]);
    } else {
        userMarker = L.marker([lat, lon]).addTo(map)
            .bindPopup("You are here")
            .openPopup();
    }

    L.circle([lat, lon], {
        color: 'blue',
        fillColor: '#f03',
        fillOpacity: 0.2,
        radius: 1000 
    }).addTo(map);

    axios.get('http://127.0.0.1:5000/safer_zone', {
        params: {
            lat: lat,
            lon: lon
        }
    })
    .then(response => {
        const data = response.data;
        if (data.nearby_shops.length > 0) {
            addSaferZoneMarkers(data.nearby_shops);
        } else {
            alert("No nearby shops found within 1 km radius.");
        }
    })
    .catch(error => {
        console.error(error);
        alert("An error occurred while fetching safer zones.");
    });
}


function handleLocationError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}
