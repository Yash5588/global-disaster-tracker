function getCurrentLocation() {

    //checks whether the browser can access geolocation
    if(navigator.geolocation){
        /*getCurrentPostion method of geolocation takes a call back function as input
        in this case it took getCoordinates function as input*/
        navigator.geolocation.getCurrentPosition(getCoordinates);
    }

    //if browser cannot access geolocation then error msg is generated

    else{
        alert('This Browser Cannot Fetch the Your location Try In another browser');
    }
}

function getCoordinates(position){
    //above when getCoordinates activates which takes postition as input 
    //postion.coords.latitude provides latitude of the user and vice versa for longitude
    console.log('latitude : ' + position.coords.latitude);
    console.log('longitude : ' + position.coords.longitude); 

    var user_latitude = position.coords.latitude;
    var user_longitude = position.coords.longitude;
    //this ajax request sends the location object to '/get_location' path
    $.ajax({
            url: "/login_get_location", 
            type: 'POST',       
            contentType: 'application/json', 
            //this is location object which is converted to string using json.stringify
            data: JSON.stringify({user_latitude: user_latitude,user_longitude: user_longitude}), 
            //response is sent from python as a response by jsonify
            success: function(response) {
                console.log('Location is sent successfully:', response);
            },
            error: function(error) {
                console.log('Error:', error);
            }
    });
}
function validate(){
    var username = document.getElementById('username');
    var password = document.getElementById('password');
    if(password.value.length == 0 || username.value.length == 0){
        alert("One Or More Fields are Empty Please Fill All the Fields");
        return false;
    }
    else{
        var form = document.getElementById('form_id');
        form.action = "/login_check";
        form.method = "post";
        return true;
    }
}

//to hide display of error block when the page is loaded initially
var currentpath = window.location.pathname;
if(currentpath == '/login'){

    var error = document.getElementById('error');
    error.style.display = "none";
    //when current path is /sign_up then getCurrentLocation() function activates which fetches the current location of user
    getCurrentLocation();
}
