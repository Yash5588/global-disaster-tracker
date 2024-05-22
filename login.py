from flask import Flask,render_template,jsonify,redirect,request,url_for
from flask import Blueprint,current_app
import mysql.connector
import math
import smtplib
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

#function to send gmail
def send_email(subject, body, sender, recipients, password):
    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients

    msg.attach(MIMEText(body,'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       #smtp_server.starttls()
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender,recipients,msg.as_string())
    print("Message sent!")


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
        distance = round(distance)
        # print('country name =',data['country_names'][i])
        # print("user latitude =",user_latitude)
        # print("user longitude =",user_longitude)
        # print("disaster latitude =",disaster_latitudes[i])
        # print("disaster longitude =",disaster_longitudes[i])
        # print("distance =",distance)
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

    # print(data)
    # print(len(data['latitude']))
    # print(len(data['user_disaster_distance']['data_index']))
    # print(len(data['latitude']))

    email = email[0][0]
    #data to send to gmail
    gmail_subject = 'The Disasters Which Are In 10km Radius Around You'

    
    distances = data['user_disaster_distance']['distance']
    indices = data['user_disaster_distance']['data_index']

    under_10km_indices = []
    
    for i in range(len(distances)):
        if distances[i] > 10:
            break
        under_10km_indices.append(indices[i])
    
    gmail_body = '''<html>
                    <head>
                    <style>
                        .space {
                            white-space: pre;
                          }
                    </style>
                    </head>
                    <body>'''
    
    genai.configure(api_key='AIzaSyA7HgBym8amisAYJxm6FgitUJKCnvwdLnc')

    model = genai.GenerativeModel('gemini-pro')

    if len(under_10km_indices) == 0:
        gmail_body = '<h1> SAFE\n\n There are no disasters currently around you within 10km radius </h1>'
    
    else:
        if len(under_10km_indices) == 1:
            gmail_body += f'<h1> !!!ALERT!!! <br> There is a disaster in your 10km radius </h1>'
        else:
            gmail_body += f'<h1> !!!ALERT!!! <br> There are a total of {len(under_10km_indices)} disasters in your 10km radius </h1>'

        for i in range(len(under_10km_indices)):
            
            j = under_10km_indices[i]

            response = model.generate_content(f'Generate the city whose coordinates are latitude : {str(data['latitude'][j])}  longitude : {str(data['longitude'][j])}')
            city = response.text
            city = city.replace('*','')

            if i == 0:
                response = model.generate_content(f'''There is a {data['disaster_names'][j]} whose coordinates are Latitude : {str(data['latitude'][j])} and longitude : {str(data['longitude'][j])}
                and it is at a distance of {distances[i]}km from my current location and the severity of the disaster is {data['severity_text'][j]}
                and a {data['alert_level'][j]} is issued
                Now generate 5 best suited survival precautions for me so that i can escape from this disaster
                suggest places where i can evacuate near me along with the distance of that place which is less than the distance of the disaster so that
                i can be safe also generate contact numbers so that i can contact for help near me in case of emergency''')

                precaution = response.text

                precaution = precaution.replace('*','')

                print(precaution)

            gmail_body += f'''<div class = "gmail_content">
                                <h2> {i+1}) {data['disaster_names'][j]}({city}) </h2>
                                <h3 class = "space"> CITY : {city} </h3>
                                <h3 class = "space"> DISTANCE FROM YOUR LOCATION :    {distances[i]}km  </h3>
                                <h3 class = "space"> SEVERITY :    {data['severity_text'][j]} </h3>
                                <h3 class = "space"> ALERT LEVEL :    {data['alert_level'][j]} </h3>
                                <h3 class = "space"> {data['exact_description'][j]} </h3>
                                <br>'''
            if i==0:
                    gmail_body += f'''<h3 class = "space"> {precaution} </h3>'''

            gmail_body += '''<br>
                             <br>
                             </div>'''
        
        gmail_body += '''
        </body>
        </html>'''

    gmail_sender = "disastertracker777@gmail.com"
    gmail_recipient = email
    gmail_password = "orhd ubgo vxhy pewi"

    send_email(gmail_subject,gmail_body,gmail_sender,gmail_recipient,gmail_password)

    return redirect(url_for('nearest_disasters'))