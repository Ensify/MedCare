from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, Response
import time
from pymongo import MongoClient
import os
from bson.json_util import dumps
from bson import ObjectId
import dotenv
import random


dotenv.load_dotenv()

app = Flask(__name__)


client = MongoClient(os.environ.get('MONGO_URI'))
db = client["medical-simplify"]
app.config['SECRET_KEY'] = "MEDICAL_SIMPLIFY_KEY"
hospital_users_collection = db["hospital-data"]

auto_increment_collection = db["auto-increment-id-info"]


def get_next_version_id(collection_auto_increment, coll_name, scan=None):
    counter_doc = collection_auto_increment.find_one(
        {"versionId": "versionId", "collName": coll_name}
    )

    if counter_doc is None:
        collection_auto_increment.insert_one(
            {"versionId": "versionId", "collName": coll_name, "seq": 0}
        )
    result = collection_auto_increment.find_one_and_update(
        {"versionId": "versionId", "collName": coll_name},
        {"$inc": {"seq": 1}},
        return_document=True,
    )

    return 1 if not result else result["seq"]


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email=="admin@gmail.com" and password=="admin":
            return redirect(url_for('admin_approve'))
        
        user = hospital_users_collection.find_one({"email": email})
        if user:
            if user.get('password') == password and user.get('approved')==True:
                session['email'] = email
                session['hospitalId'] = user.get('hospitalId')
                
                flash("Logged in successfully")
                return redirect(url_for('profiles'))
            elif user.get('approved')==False:
                flash("Your request is being proccessed.  We'll send you mail once we accept your registration. Thank you.")
            else:
                flash("Invalid password")
                
        else:
            flash("Invalid Credentials")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hospital_name = request.form['hospital_name']
        hospital_address = request.form['hospital_address']
        phone_number = request.form['phone']

        existing_user = hospital_users_collection.find_one({"email": email})

        if existing_user:
            flash("User with this email already exists. Try logging in. Redirecting in 5 secs..")
            # time.sleep(5)
            return render_template('login.html')
        else:
            version_id = get_next_version_id(auto_increment_collection, "hospital-data")
            user = hospital_users_collection.insert_one({"hospitalId": version_id,"email": email, "password": password, "hospitalName": hospital_name, "hospitalAddress": hospital_address,"phone_number" : phone_number ,"approved": False})
            flash("Submitted for Registration. We'll send you mail once we accept your registration. Thank you.")


    return render_template('register.html')


@app.route('/profiles', methods=['GET', 'POST'])
def profiles():
    return {'message': 'success'}
   



if __name__ == "__main__":
    app.run(debug=True, port=5050, host='0.0.0.0')
