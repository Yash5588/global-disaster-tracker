 // Initialize and add the map
 function initMap() {
    var map;
    var bounds = new google.maps.LatLngBounds();
    var mapOptions = {
        mapTypeId: 'hybrid',
        center: {lat: -34.397, lng: 150.644},
        zoom: 8
    };
                    
    // Display a map on the web page
    map = new google.maps.Map(document.getElementById("mapCanvas"), mapOptions);
    map.setTilt(45);

    var latitude = flaskData.latitude;
    var longitude = flaskData.longitude;
    var country_names = flaskData.country_names;
    var disaster_names = flaskData.disaster_names;
    var exact_description = flaskData.exact_description;
    var alert_level = flaskData.alert_level;
    var from_date = flaskData.from_date;
    var time = flaskData.time;
    var severity_text = flaskData.severity_text;
    var icon = flaskData.icon;
    var alert_color = flaskData.alert_color;
    var legend_icon_names = flaskData.legend_icon_names;
    var legend_icon_pics = flaskData.legend_icon_pics;
    var event_type = flaskData.event_type;
    var event_id = flaskData.event_id;
    
    // Multiple markers location, latitude, and longitude
    var markers = []
    for(i = 0;i<latitude.length;i++)
    {
        markers.push([country_names[i],latitude[i],longitude[i]]);
    }
    
    var event_info = '<button class = "btn btn-success" onclick = "fetch_event_details({eventid},{letter1},{letter2})"> Get More Info </button>';
    // Info window content
    var infoWindowContent = [];
    for(i = 0;i<latitude.length;i++){
        
        event_info = event_info.replace('{eventid}',event_id[i]);
        event_info = event_info.replace('{letter1}',event_type[i].charCodeAt(0));
        event_info = event_info.replace('{letter2}',event_type[i].charCodeAt(1));
        var content = '<div class="info_content">'+
            '<h3>' + country_names[i] + '</h3>'+
            '<h4>' + disaster_names[i] + '</h4>' +
            '<h6>' + exact_description[i] + '</h6>' +
            '<h5>Alert Level : ' + alert_level[i] + '</h5>' +
            '<div class="progress" style="width: 100">' +
                '<div class="progress-bar ' + alert_color[i] + '" style="width: 100%"></div>' + 
            '</div>' +
            '<h5>Occured Date : ' + from_date[i] + '</h5>' +
            '<h5>Occured Time : ' + time[i] + '</h5>' +
            '<h5>Severity : ' + severity_text[i] + '</h5>' +
            event_info +
            '</div>';
        infoWindowContent.push(content);
        event_info = event_info.replace(event_id[i],'{eventid}');
        event_info = event_info.replace(event_type[i].charCodeAt(0),'{letter1}');
        event_info = event_info.replace(event_type[i].charCodeAt(1),'{letter2}');
    }
        
    // Add multiple markers to map
    var infoWindow = new google.maps.InfoWindow(), marker, i;
    
    // Place each marker on the map  
    for( i = 0; i < markers.length; i++ ) {
        var position = new google.maps.LatLng(markers[i][1], markers[i][2]);
        bounds.extend(position);
        marker = new google.maps.Marker({
            position: position,
            map: map,
            icon : icon[i],
            title: markers[i][0]
        });
        // Add info window to 
        marker    
        google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
                infoWindow.setContent(infoWindowContent[i]);
                infoWindow.open(map, marker);
            }
        })(marker, i));

        // Center the map to fit all markers on the screen
        map.fitBounds(bounds);
    }

    // Set zoom level
    var boundsListener = google.maps.event.addListener((map), 'bounds_changed', function(event) {
        this.setZoom(3);
        google.maps.event.removeListener(boundsListener);
    });

    const legend = document.getElementById("legend");
    for(i = 0;i < legend_icon_names.length;i++)
    {
        const div = document.createElement("div");
        div.innerHTML = '<img src="' + legend_icon_pics[i] + '"> ' + '<h5>' + legend_icon_names[i] + '</h5>';
        legend.appendChild(div)
    }
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(legend);
}

    window.initMap = initMap;

    function fetch_event_details(id,ascii1,ascii2){
            
            var eventdata = {
                id: id,
                type: String.fromCharCode(ascii1) + String.fromCharCode(ascii2),
            };
            
            //ajax is used here to send data from js to python flask
            $.ajax({
                url: "/processing", 
                type: 'POST',       
                contentType: 'application/json', 
                data: JSON.stringify(eventdata), 
                //response is sent from python as a response by jsonify
                success: function(response) {
                    console.log('Data sent successfully:', response);
                    window.location.href = '/more_info';
                    //here new path os created in success attribute
                },
                error: function(error) {
                    console.log('Error:', error);
                }
            });
        }
