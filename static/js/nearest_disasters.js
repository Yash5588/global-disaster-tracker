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

var row_col_10km = document.getElementById('row_col_10km')
var row_col_50km = document.getElementById('row_col_50km');
var row_col_100km = document.getElementById('row_col_100km');
var row_col_200km = document.getElementById('row_col_200km');
var row_col_500km = document.getElementById('row_col_500km');

var flag_10km = false;
var flag_50km = false;
var flag_100km = false;
var flag_200km = false;
var flag_500km = false;


for(let i=0;i<latitude.length;i++){
    var j = data_indices[i];
    var event_info = '<button class = "btn btn-success" onclick = "fetch_event_details({eventid},{letter1},{letter2})"> Get More Info </button>';

    event_info = event_info.replace('{eventid}',event_id[j]);
    event_info = event_info.replace('{letter1}',event_type[j].charCodeAt(0));
    event_info = event_info.replace('{letter2}',event_type[j].charCodeAt(1));

    content =
        '<div class="col-md-6">' +
            '<div class="card mb-3 shadow-lg">' + 
                '<ul class = "card-body list-group list-group-flush">' + 
                    '<li class = "list-group-item"><h3 class="card-title">' + disaster_names[j] + '<img class = "icons" src="' + icon[j] +'" alt=""> </h3> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Latitude: ' + latitude[j] + '<br>Longitude: ' + longitude[j] + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Distance from Your Location: ' + distances[i] + 'km</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Severity: ' + severity_text[j]  + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">Alert Level: ' + alert_level[j] + '</h6> </li>' + 
                    '<li class = "list-group-item"><h6 class="card-text">' + exact_description[j] + '</h6> </li>' + 
                    '<li class = "list-group-item">' + event_info + '</li>' + 
                '</ul>' +
            '</div>' + 
        '</div>';

    if(distances[i] <= 10){
        row_col_10km.innerHTML += content;
        flag_10km = true;
    }
    else if(distances[i] > 10 && distances[i] <= 50){
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

    event_info = event_info.replace(event_id[j],'{eventid}');
    event_info = event_info.replace(event_type[j].charCodeAt(0),'{letter1}');
    event_info = event_info.replace(event_type[j].charCodeAt(1),'{letter2}');
}

if(!flag_10km){
    document.getElementById('empty_10km').innerHTML += 'There are no Disasters Currently in your 10km Radius'
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
            //here new path is created in success attribute
        },
        error: function(error) {
            console.log('Error:', error);
        }
    });
}