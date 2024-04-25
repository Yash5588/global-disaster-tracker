
from flask import Flask,render_template,jsonify,redirect,request,url_for
from flask import Blueprint,current_app
import mysql.connector
import math

login_bp = Blueprint('login',__name__)

min_distance_indices = []
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    d_lat = math.radians(lat2 - lat1)  # Convert degrees to radians
    d_lon = math.radians(lon2 - lon1)  # Convert degrees to radians
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in kilometers
    return distance

@login_bp.route('/login')
def login():
    return render_template('login.html')

@login_bp.route('/login_get_location',methods = ['GET','POST'])
def login_get_location():
    global login_user_location
    login_user_location = request.json
    return jsonify(login_user_location)


@login_bp.route('/login_check',methods = ['POST'])
def login_check():
    connection = mysql.connector.connect(
        host = "localhost",
        user = "yash559",
        password = "1234",
        database = "disaster"
    )

    username = request.form['username']
    password = request.form['password']
    user_latitude = login_user_location['user_latitude']
    user_longitude = login_user_location['user_longitude']

    cursor = connection.cursor()

    retrive_query = "select email from login_details where username = %s and password = %s"

    cursor.execute(retrive_query,(username,password))

    email = cursor.fetchall()

    
    if(len(email) == 0):
        return render_template('login.html',error = "Invalid Username Or Password Sign Up before Login")
    
    print(login_user_location)
    
    update_location_query = "update login_details set latitude = %s,longitude = %s  where username = %s and password = %s"
    
    cursor.execute(update_location_query,(str(user_latitude),str(user_longitude),username,password))

    connection.commit()
    cursor.close()
    connection.close()

    data = current_app.config['data']
    
    disaster_latitudes = data['latitude']
    disaster_longitudes = data['longitude']
    
    data['user_disaster_distance']['distance'] = []
    data['user_disaster_distance']['data_index'] = []

    for i in range(len(disaster_longitudes)):
        distance = calculate_distance(user_latitude,user_longitude,disaster_latitudes[i],disaster_longitudes[i])
        print('country name =',data['country_names'][i])
        print("user latitude =",user_latitude)
        print("user longitude =",user_longitude)
        print("disaster latitude =",disaster_latitudes[i])
        print("disaster longitude =",disaster_longitudes[i])
        print("distance =",distance)
        data['user_disaster_distance']['data_index'].append(i)
        data['user_disaster_distance']['distance'].append(distance)
        print()
    
    data_indices = data['user_disaster_distance']['data_index']
    disaster_distances = data['user_disaster_distance']['distance']

    #this zip generated tuples by combining elements in each index
    zipped_list = sorted(zip(data_indices,disaster_distances),key = lambda x : x[1])

    #unzipping
    data['user_disaster_distance']['data_index'],data['user_disaster_distance']['distance'] = zip(*zipped_list)
    data['user_disaster_distance']['data_index'] = list(data['user_disaster_distance']['data_index'])
    data['user_disaster_distance']['distance'] = list(data['user_disaster_distance']['distance'])

    print(data)
    print(len(data['latitude']))
    print(len(data['user_disaster_distance']['data_index']))

    email = email[0][0]
    
    return redirect(url_for('nearest_disasters'))