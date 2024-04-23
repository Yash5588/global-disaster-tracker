
from flask import Flask,render_template,jsonify,redirect,request,url_for
from flask import Blueprint
import mysql.connector

login_bp = Blueprint('login',__name__)

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
    user_latitude = str(login_user_location['user_latitude'])
    user_longitude = str(login_user_location['user_longitude'])

    cursor = connection.cursor()

    retrive_query = "select email from login_details where username = %s and password = %s"

    cursor.execute(retrive_query,(username,password))

    email = cursor.fetchall()

    
    if(len(email) == 0):
        return render_template('login.html',error = "Invalid Username Or Password Sign Up before Login")
    
    print(login_user_location)
    
    update_location_query = "update login_details set latitude = %s,longitude = %s  where username = %s and password = %s"
    
    cursor.execute(update_location_query,(user_latitude,user_longitude,username,password))

    connection.commit()
    cursor.close()
    connection.close()
    
    email = email[0][0]
    

    return redirect(url_for('home_page'))