
from flask import Flask,render_template,jsonify,redirect,request,url_for
from flask import Blueprint
import mysql.connector

sign_up_bp = Blueprint('sign_up',__name__)

@sign_up_bp.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

#this is ajax request request.json we are returing again to ajax as success which is taken as response in ajax
@sign_up_bp.route('/sign_up_get_location',methods = ['GET','POST'])
def sign_up_get_location():
    #signup_user_location is taken globally
    global signup_user_location
    signup_user_location = request.json
    return jsonify(signup_user_location)

@sign_up_bp.route('/sign_up_validate',methods = ['POST'])
def sign_up_validate():
    try:
        connection = mysql.connector.connect(
            host = "localhost",
            user = "yash559",
            password = "1234",
            database = "disaster"
        ) 
        
        #request.from takes names of attributes not ids
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        contact = request.form['contact']
        user_latitude = str(signup_user_location['user_latitude'])
        user_longitude = str(signup_user_location['user_longitude'])

        cursor = connection.cursor()

        insert_query = "INSERT INTO login_details (username,password,email,contact,latitude,longitude) VALUES (%s,%s,%s,%s,%s,%s)"

        cursor.execute(insert_query,(username,password,email,contact,user_latitude,user_longitude))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('home_page'))
    
    except:

        return render_template('sign_up.html',error = "The User Already Exists Login To Get The Latest Details")