from flask import Flask, request, url_for, session, redirect
import pymongo
import bcrypt
import datetime
import requests, json
#from flask.ext.pymongo import PyMongo

from flask import render_template

app = Flask(__name__)



@app.route('/', methods=['POST','GET'])
def hello_world():

    client = pymongo.MongoClient("mongodb+srv://bhawna28:gargpass@cluster0-jte0f.mongodb.net/test?retryWrites=true&w=majority")
    db = client.test_regis
    col= db.user_details        
    pre_records = col.find({"client_ip": request.remote_addr, "created": datetime.datetime.utcnow().strftime("%Y%m%d")})
   
    if len(list(pre_records)) >= 3:
       if request.method == 'POST':
           user_data  = {"name": request.form["name1"], "email": request.form["email1"], "password": request.form["psw1"], "created": datetime.datetime.utcnow().strftime("%Y%m%d"), "client_ip": request.remote_addr}
           captcha_response = request.form.get('g-recaptcha-response')
           existing_users = col.find_one({'name' : request.form['name1']}) or col.find_one({'email' : request.form['email1']})
           if existing_users:
               return "Record already exists !!!"
           print(captcha_response)
           if is_human(captcha_response):
               col.insert(user_data)
               return "Successfully Registered!!!"
           else :
               return "You are a bot!!"
       return render_template('user_captcha.html')
    else:
        if request.method == 'POST':
            user_data  = {"name": request.form["name"], "email": request.form["email"], "password": request.form["psw"], "created": datetime.datetime.utcnow().strftime("%Y%m%d"), "client_ip": request.remote_addr}
            existing_users = col.find_one({'name' : request.form['name']}) or col.find_one({'email' : request.form['email']})
            if existing_users:
               return "Record already exists !!!"
            col.insert(user_data)
            return "Successfully Registered!!!"
       #col.insert(user_data)
    return render_template('user.html')


def is_human(captcha_response):

    secret = "6LcBD-MUAAAAABA6qizuw12lhxM14YqfZXcDitPr"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']



if __name__ == '__main__':
    app.run()
