
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

var earthquake = document.getElementById('earthquake_body');
var flood = document.getElementById('flood_body');
var drought = document.getElementById('drought_body');
var tropical = document.getElementById('tropical_body');
var forest = document.getElementById('forest_body');
var eruption = document.getElementById('eruption_body');
var tsunami = document.getElementById('tsunami_body');

let earthquake_flag = 0;
let flood_flag = 0;
let drought_flag = 0;
let tropical_flag = 0;
let forest_flag = 0;
let eruption_flag = 0;
let tsunami_flag = 0;

for(i=0;i<latitude.length;i++)
{
    var event_info = '<button class = "btn btn-success" onclick = "fetch_event_details({eventid},{letter1},{letter2})"> get more info </button>';
    
    event_info = event_info.replace('{eventid}',event_id[i]);
    event_info = event_info.replace('{letter1}',event_type[i].charCodeAt(0));
    event_info = event_info.replace('{letter2}',event_type[i].charCodeAt(1));
    
    let table_row =  
        '<td>' + country_names[i] + '</td>' + 
        '<td>' + latitude[i] + '</td>' + 
        '<td>' + longitude[i] + '</td>' +
        "<td class = 'alert_level'>" + alert_level[i] +"</td>" + 
        '<td>' + from_date[i] + '</td>' + 
        '<td>' + time[i] + '</td>'+ 
        '<td>' + severity_text[i] + '</td>'+
        '<td>' + ((is_current[i] == 'true') ? 'an ongoing crisis' : 'stable situation') + '</td>' +
        '<td>' + event_info + '</td>' +
    '</tr>';



    if(disaster_type[i] == 'Earthquake'){
        earthquake.innerHTML += '<tr>'  + '<td>' + (++earthquake_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Flood'){
        flood.innerHTML += '<tr>' + '<td>' + (++flood_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Drought'){
        drought.innerHTML += '<tr>' + '<td>' + (++drought_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Tropical'){
        tropical.innerHTML += '<tr>' + '<td>' + (++tropical_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Forest'){
        forest.innerHTML += '<tr>' + '<td>' + (++forest_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Eruption'){
        eruption.innerHTML += '<tr>' + '<td>' + (++eruption_flag) + '</td>' + table_row;
    }
    else if(disaster_type[i] == 'Tsunami'){
        tsunami.innerHTML += '<tr>' + '<td>' + (++tsunami_flag) + '</td>' + table_row;
    }

    event_info = event_info.replace(event_id[i],'{eventid}');
    event_info = event_info.replace(event_type[i].charCodeAt(0),'{letter1}');
    event_info = event_info.replace(event_type[i].charCodeAt(1),'{letter2}');
}

if(!earthquake_flag){
    document.getElementById('earthquake_table').style.display = 'none';
    document.getElementById('earthquake_empty').innerHTML = "There Are No Earthquakes Currently Across The World";
}
if(!flood_flag){
    document.getElementById('flood_table').style.display = 'none';
    document.getElementById('flood_empty').innerHTML = "There Are No Floods Currently Across The World";
}
if(!drought_flag){
    document.getElementById('drought_table').style.display = 'none';
    document.getElementById('drought_empty').innerHTML = "There Are No Droughts Currently Across The World";
}
if(!tropical_flag){
    document.getElementById('tropical_table').style.display = 'none';
    document.getElementById('tropical_empty').innerHTML = "There Are No Tropical Cyclones Currently Across Across The World";
}
if(!forest_flag){
    document.getElementById('forest_table').style.display = 'none';
    document.getElementById('forest_empty').innerHTML = "There Are No Forest Fires Currently Across The World";
}
if(!eruption_flag){
    document.getElementById('eruption_table').style.display = 'none';
    document.getElementById('eruption_empty').innerHTML = "There Are No Volcanic Eruptions Currently Across The World";
}
if(!tsunami_flag){
    document.getElementById('tsunami_table').style.display = 'none';
    document.getElementById('tsunami_empty').innerHTML = "There Are No Tsunamis Currently Across The World";
}

var alert = document.getElementsByClassName('alert_level');

for(let i=0;i<alert.length;i++){
    alert[i].style.color = alert[i].textContent;
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