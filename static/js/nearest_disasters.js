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
var disaster_type = flaskData.disaster_type;
var is_current = flaskData.is_current;
var event_type = flaskData.event_type;
var event_id = flaskData.event_id;
var data_indices = flaskData.user_disaster_distance.data_index;
var distances = flaskData.user_disaster_distance.distance;

var row_col_100km = document.getElementById('row_col_100km');
row_col_100km.innerHTML = '';
var content_100km = '';

for(let i=0;i<latitude.length && distances[i] <= 100;i++){
    var j = data_indices[i];
    content_100km += 
        '<div class="col-md-6">' +
            '<div class="card mb-3">' +
                '<div class="card-body">' + 
                    '<h5 class="card-title">' + disaster_names[j] + '</h5>' + 
                    '<p class="card-text">Latitude: ' + latitude[j] + '   Longitude: ' + longitude[j] + '</p>' + 
                    '<p class="card-text">Distance from Your Location: ' + Math.round(distances[i]) + 'kilometers</p>' + 
                    '<p class="card-text">Severity: ' + severity_text[j]  + '</p>' + 
                    '<p class="card-text">Alert Level: ' + alert_level[i] + '</p>' + 
                    '<p class="card-text">' + exact_description[j] + '</p>' + 
                '</div>' + 
            '</div>' + 
        '</div>';
}

row_col_100km.innerHTML = content_100km;