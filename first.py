from flask import Flask, request, url_for, session, redirect
import pymongo
import bcrypt
import datetime
import requests, json
#from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
from flask import render_template

app = Flask(__name__)
app.config["MONGO_URI"] ="mongodb+srv://bhawna28:gargpass@cluster0-jte0f.mongodb.net/test?retryWrites=true&w=majority"
app.config['RECAPTCHA_PUBLIC_KEY'] = ''
app.config['RECAPTCHA_PRIVATE_KEY'] = ''
mongo = PyMongo(app)


@app.route('/', methods=['POST','GET'])
def hello_world():
    sitekey = ""
    if request.method == 'POST':
        client = pymongo.MongoClient("mongodb+srv://bhawna28:gargpass@cluster0-jte0f.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test_regis
        col= db.user_details        
        existing_user = col.find_one({'name' : request.form['name']}) or col.find_one({'email' : request.form['email']})
        #print(users)
        if existing_user:
            return "Record already exists !!!"
        try:
            pre_records = col.find({"client_ip": request.remote_addr, "created": datetime.datetime.utcnow().strftime("%Y%m%d")})
            if len(list(pre_records)) >= 3:
                print("yes ..............")

                render_template('user_captcha.html')
                user_data  = {"name": request.form["name"], "email": request.form["email"], "password": request.form["psw"], "created": datetime.datetime.utcnow().strftime("%Y%m%d"), "client_ip": request.remote_addr}
                captcha_response = request.form['g-recaptcha-response']    
                print(captcha_response)         
       
                if is_human(captcha_response):
                # Process request here
                    col.insert_one(user_data)
                    return "Detail submitted successfully."
                else:
                # Log invalid attempts
                    return "Sorry ! Bots are not allowed."
            user_data1  = {"name": request.form["name"], "email": request.form["email"], "password": request.form["psw"], "created": datetime.datetime.utcnow().strftime("%Y%m%d"), "client_ip": request.remote_addr}
            col.insert_one(user_data1)
            records = col.find()
            to_send_rec = ''
            for rec in records:
                to_send_rec += str(rec)
            return "Record added and records are : {}".format(str(to_send_rec))
        except Exception as e:
            print(str(e))
            return 'Exception Occurred'

    return render_template('user.html')


def is_human(captcha_response):

    secret = ""
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']



if __name__ == '__main__':
    app.run()
