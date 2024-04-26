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

var row_col_50km = document.getElementById('row_col_50km');
var row_col_100km = document.getElementById('row_col_100km');
var row_col_200km = document.getElementById('row_col_200km');
var row_col_500km = document.getElementById('row_col_500km');

var flag_50km = false;
var flag_100km = false;
var flag_200km = false;
var flag_500km = false;

for(let i=0;i<latitude.length;i++){
    var j = data_indices[i];
    content =
        '<div class="col-md-6">' +
            '<div class="card mb-3 shadow-lg">' + 
                '<ul class = "card-body list-group list-group-flush">' + 
                    '<li class = "list-group-item"><h3 class="card-title">' + disaster_names[j] + '<img class = "icons" src="' + icon[j] +'" alt=""> </h3> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Latitude: ' + latitude[j] + '<br>Longitude: ' + longitude[j] + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Distance from Your Location: ' + Math.round(distances[i]) + 'km</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Severity: ' + severity_text[j]  + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Alert Level: ' + alert_level[j] + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">' + exact_description[j] + '</h6> </li>' + 
                '</ul>' +
            '</div>' + 
        '</div>';
    if(distances[i] <= 50){
        row_col_50km.innerHTML += content;
        flag_50km = true;
    }
    else if(distances[i] > 50 && distances[i] <= 100){
        row_col_100km.innerHTML += content;
        flag_100km = true;
    }
    else if(distances[i] > 100 && distances[i] <= 200){
        row_col_200km.innerHTML += content;
        flag_200km = true;
    }
    else if(distances[i] > 200 && distances[i] <= 500){
        row_col_500km.innerHTML += content;
        flag_500km = true;
    }
}

if(!flag_50km){
    document.getElementById('empty_50km').innerHTML += 'There are no Disasters Currently in your 50km Radius'
}
if(!flag_100km){
    document.getElementById('empty_100km').innerHTML += 'There are no Disasters Currently in your 100km Radius'
}
if(!flag_200km){
    document.getElementById('empty_200km').innerHTML += 'There are no Disasters Currently in your 200km Radius'
}
if(!flag_500km){
    document.getElementById('empty_500km').innerHTML += 'There are no Disasters Currently in your 500km Radius'
}