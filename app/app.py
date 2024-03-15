from base64 import b64encode
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, Response
from pymongo import MongoClient
import os
from bson import ObjectId
import dotenv
import random
import requests
import smtplib, ssl

dotenv.load_dotenv()

app = Flask(__name__)

client = MongoClient(os.environ.get('MONGO_URI'))
db = client["medical-simplify"]
app.config['SECRET_KEY'] = "MEDICAL_SIMPLIFY_KEY"
hospital_users_collection = db["hospital-data"]

auto_increment_collection = db["auto-increment-id-info"]
patient_collection = db["patient-datas"]
access_collection = db["access"]
patient_ehr = db["patient-ehr"]
conv_summary = db["conv-summaries"]




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

def send_mail(receiver_email, flag, hospital_name=None, otp=None):
    port = 465  
    smtp_server = "smtp.gmail.com"
    sender_email = "vignesh1234can@gmail.com"  
    # receiver_email = "your@gmail.com"  
    password = "nhcy nbkt teag fnos"
    if flag:
        message = """
        Subject: Medical Simplify - Verification Successful.

        Hospital Verification is successful and you can now login with your registered mail id and password.
        Thank you.
        """
    else:
        message = f"""
        Subject: Medical Simplify - OTP.

        Your OTP to allow {hospital_name} to access your Medical records is {otp}
        Thank you.
        """


    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print(f"Mail sent to {receiver_email}")
    return True

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


@app.route('/approve', methods=['GET','POST'])
def admin_approve():
    if request.method == 'POST':
        try:
            _id = int(request.form['hospitalId'].strip())
            print(_id)
            print(hospital_users_collection.count_documents({"hospitalId": _id}))
            # result = hospital_users_collection.update_one({"hospitalId": _id}, {"$set": {"approved": True}})

            document = hospital_users_collection.find_one({"hospitalId": _id})
            print(document["email"])
            result = hospital_users_collection.update_one({"hospitalId": _id}, {"$set": {"approved": True}})
            print(document)
            if document and result.matched_count > 0:
                send_mail(receiver_email=document["email"], flag=True)
                print("Mail sent successfully")

            print("updated")
            if result.modified_count == 1:
                print("Approved successfully.")
                flash("Approved successfully.")
            else:
                print("Hospital ID not found.")
                flash("Hospital ID not found.")
        except Exception as e:
            print("An error occurred")
            flash("An error occurred while updating the approval status.")
            print(e)
            
        return redirect(url_for('admin_approve'))

    to_be_approved = hospital_users_collection.find({"approved": False})
    return render_template('admin_approve.html', users=to_be_approved)

@app.route('/profiles', methods=['GET', 'POST'])
def profiles():
    if request.method == 'POST':
        ph_no = request.form.get('phno').strip()
        if not ph_no:
            flash("Please enter a valid phone number")
            return redirect(url_for('profiles'))
        ph_no = int(ph_no)
        print(ph_no)
        doc = patient_collection.find({"phone": ph_no})
        print(doc)
        return render_template('profiles.html', profiles=doc)

    return render_template('profiles.html')
   

@app.route('/display/<int:patientId>', methods=['GET', 'POST'])
def display(patientId):
    session["patientId"] = patientId
    session["patientName"] = patient_collection.find_one({'patientId': patientId}).get('patientName')
    print(f"Patient ID: {patientId} {session['patientName']}")
    return render_template('display.html')

@app.route('/add_profile', methods=['POST'])
def add_profile():
    phone = int(request.form.get('phone').strip())
    name = request.form.get('patientName').strip()
    email = request.form.get('email').strip()
    patient_id = get_next_version_id(auto_increment_collection, "patient-datas")
    patient_data = {"phone": phone, "patientName": name, "email": email, "patientId": patient_id}
    result = patient_collection.insert_one(patient_data)
    
    # patient_id = patient_data.get('patientId')
    print("Yay!!!!!!!1")
    print(name, phone)
    return redirect(url_for('display', patientId=int(patient_id)))

@app.route('/handle_submit', methods=['POST'])
def handle_submit():
    print(request.form)
    # if 'add_document' in request.form:
    doctor_name = request.form['doctor_name']
    file = request.files['file']

    content = file.read()
    file_type = None
    file_name_splitted = file.filename.split('.')
    if len(file_name_splitted)>1:
        file_type = file_name_splitted[1]

    if not file_type=='pdf':
        file_type = 'image'
    patient_ehr.insert_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"], "doctorName": doctor_name, "fileName": file.filename, "fileType": file_type ,"content": content})
    print("Inserted ehr")
    flash("File uploaded successfully")

    # time.sleep(5)

    return "File uploaded successfully"

@app.route("/getdata", methods=["GET"])
def getdata():
    # access_doc = access_collection.find_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"]})
    # print(access_doc.get('access'))
    # if access_doc and access_doc.get('access'):
    profile_summary_doc = patient_collection.find_one({"patientId": session["patientId"]})
    prof_summary = profile_summary_doc.get('profileSummary')
    suggestions = profile_summary_doc.get('suggestions')
    # print(prof_summary)
    patient_details = patient_ehr.find({"patientId": session["patientId"]})
    # if patient_details:
    print(patient_details)

    summaries = conv_summary.find({"patientId": session["patientId"]})

    return render_template('patient_details.html', patient_details=patient_details, summaries=summaries, profile_summary=prof_summary, name=session['patientName'], patient_id = session["patientId"], suggestions=suggestions)


@app.route('/generate_otp', methods = ['POST'])
def generate_otp():
    access_doc = access_collection.find_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"]})

    if access_doc and access_doc.get('access'):
        return {"res": "success"}

    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    print(otp)
    document = hospital_users_collection.find_one({"hospitalId": session["hospitalId"]})
    hospital_name = document.get('hospitalName')

    patient = patient_collection.find_one({"patientId": session["patientId"]})
    access_collection.insert_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"], "otp": otp, "access": False})
    print(document)
    if document:
            send_mail(receiver_email=patient["email"], flag=False, hospital_name=hospital_name, otp=otp)
            print("Mail sent successfully")
    return {"res":"sent", "data": "OTP Sent successfully"}

@app.route('/request_access', methods=['POST'])
def request_access():
    if request.method == 'POST':
        print(request.form.items)
        input_otp = request.form.get('otp').strip()
        access_doc = access_collection.find_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"]})
        print(access_doc.get('otp'))
        if input_otp == access_doc.get('otp'):
            access_collection.update_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"]}, {"$set": {"access": True}})
            patient_details = patient_ehr.find({"patientId": session["patientId"]})
            if patient_details:
                print(patient_details)
                summaries = conv_summary.find({"patientId": session["patientId"]})
                profile_summary_doc = patient_collection.find_one({"patientId": session["patientId"]})
                prof_summary = profile_summary_doc.get('profileSummary')
               
                suggestions = profile_summary_doc.get('suggestions')
                # return render_template('patient_details.html', patient_details=patient_details, summaries=summaries, profile_summary=prof_summary, suggestions=suggestions, name=session['patientName'])
                return render_template('patient_details.html', patient_details=patient_details, summaries=summaries, profile_summary=prof_summary, suggestions=suggestions, name=session['patientName'])
            else:
                return "Patient details not found. No docs available for the patient"
        else:
            # access_collection.insert_one({"hospitalId": session["hospitalId"], "patientId": session["patientId"], "access": False})
            flash("Invalid OTP. Try again")
            return "Invalid OTP. Try again"


@app.route('/get_document/<string:_id>')
def get_document(_id):
    try:
        doc_id = ObjectId(_id)
        doc = patient_ehr.find_one({"_id": doc_id})
        if doc:
            content_base64 = b64encode(doc["content"]).decode("utf-8")
            content_type = "image/png" 
            data_uri = f"data:;base64,{content_base64}"

            html_content = f'<html><body><img src="{data_uri}" /></body></html>'

            return Response(html_content, status=200)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=5052, host='0.0.0.0')
