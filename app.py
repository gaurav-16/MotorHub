from crypt import methods
import re
from flask import Flask,render_template,request,redirect, session
import jsonify
import requests
import pickle
import numpy as np
import sklearn
import pymysql
from sklearn.preprocessing import StandardScaler
from flask_session import Session

app=Flask(__name__)
conn = pymysql.connect(user='root', password='kalilinux', db='motorhub', host='localhost')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
model = pickle.load(open('/home/rnarwade/Videos/MotorHub/random_forest_regression_model.pkl', 'rb'))
username = 'admin@mail.com'
password = 'admin@123'

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if((request.form['login_username']) == 'admin@mail.com'):
            session["username"] = request.form['login_username']
            session["password"] = request.form['login_password']
            return redirect('/admin_newsletter')
        else:
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session["username"] = None
    session["password"] = None
    return redirect('/login')

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/admin_newsletter',methods=['GET'])
def admin_newsletter():
    if not session.get("username"):
        return redirect('/login')
    cur = conn.cursor()
    cur.execute("SELECT * FROM newsletter")
    data = cur.fetchall()
    return render_template('admin_newsletter.html', data=data)

@app.route('/admin_contacts',methods=['GET'])
def admin_contacts():
    if not session.get("username"):
        return redirect('/login')
    cur = conn.cursor()
    cur.execute("SELECT * FROM contact")
    data = cur.fetchall()
    return render_template('admin_contacts.html', data=data)

@app.route('/admin_sell',methods=['GET'])
def admin_sell():
    if not session.get("username"):
        return redirect('/login')
    cur = conn.cursor()
    cur.execute("SELECT * FROM sell_form")
    data = cur.fetchall()
    return render_template('admin_sell.html', data=data)

@app.route('/wanna-buy',methods=['GET'])
def wanna_buy():
    return render_template('grid.html')

@app.route('/wanna-sell',methods=['GET'])
def wanna_sell():
    return render_template('wanna-sell.html')

@app.route('/contact',methods=['GET'])
def contact():
    return render_template('contact-us.html')
    
@app.route('/about',methods=['GET'])
def about():
    return render_template('about-us.html')

@app.route('/blog',methods=['GET'])
def blog():
    return render_template('blog.html')

@app.route('/success-2',methods=['GET'])
def success_2():
    return render_template('success.html')

@app.route('/blog-detail',methods=['GET'])
def blog_detail():
    return render_template('blog-detail.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
    name = request.form['name']
    email = request.form['email']
    telephone = request.form['telephone']
    manufacturer_name = request.form['manufacturer_name']
    vehicle_name = request.form['vehicle_name']
    demand = request.form['demand']
    comment = request.form['comment']

    cur = conn.cursor()
    sql = "INSERT INTO `sell_form` (`name`, `email`, `telephone`, `manufacturer_name`, `vehicle_name`, `demand`, `comment`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (name, email, telephone, manufacturer_name, vehicle_name, demand, comment))
    conn.commit()
    return render_template('success.html')

@app.route('/success-newsletter', methods=['GET', 'POST'])
def success_newsletter():
    email = request.form['email']

    cur = conn.cursor()
    sql = "INSERT INTO `newsletter` (`email`) VALUES (%s)"
    cur.execute(sql, (email))
    conn.commit()
    return render_template('success.html')

@app.route('/success-contact', methods=['GET', 'POST'])
def success_contact():
    name = request.form['name']
    email = request.form['email']
    telephone = request.form['telephone']
    comment = request.form['comment']

    cur = conn.cursor()
    
    sql = "INSERT INTO `contact` (`name`, `email`, `telephone`, `comment`) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (name, email, telephone, comment))
    conn.commit()
    return render_template('success.html')

standard_to = StandardScaler()
@app.route('/',methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
       Year = int(request.form['Year'])
       Present_Price=float(request.form['Present_Price'])
       Kms_Driven=int(request.form['Kms_Driven'])
       Kms_Driven2=np.log(Kms_Driven)
       Owner=int(request.form['Owner'])
       Fuel_Type=request.form['Fuel_Type']
       seller_type = request.form['seller_type']
       if(Fuel_Type=='Petrol'):
                Fuel_Type_Petrol=1
                Fuel_Type_Diesel=0
       elif(Fuel_Type == 'Diesel'):
                Fuel_Type_Petrol = 0
                Fuel_Type_Diesel = 1
       else:
            Fuel_Type_Petrol=0
            Fuel_Type_Diesel=0
       Year=2020-Year
       if(seller_type=='Individual'):
            seller_type=1
       else:
            seller_type=0	
    #    Transmission_Mannual=request.form['Transmission_Mannual']
       Transmission_Mannual = 1
    #    if(Transmission_Mannual=='Manual'):
    #         Transmission_Mannual=1
    #    else:
    #         Transmission_Mannual=0
       prediction=model.predict([[Present_Price, Kms_Driven,Owner,Year,Fuel_Type_Diesel, Fuel_Type_Petrol,seller_type,Transmission_Mannual]])
       output=round(prediction[0],2)
       if output<0:
            return render_template('index.html',prediction_texts="Sorry you cannot sell this car")
       else:
            return render_template('index.html',prediction_text="You Can Sell The Car at {}".format(output)+" Lakhs")
    else:
        return render_template("form.html")

# @app.route('/blog-detail',methods=['GET'])
# def blog_detail():
#     return render_template('blog-detail.html')

# standard_to = StandardScaler()
# @app.route("/predict", methods=['POST'])
# def predict():
#     Fuel_Type_Diesel=0
#     if request.method == 'POST':
#         Year = int(request.form['Year'])
#         Present_Price=float(request.form['Present_Price'])
#         Kms_Driven=int(request.form['Kms_Driven'])
#         Kms_Driven2=np.log(Kms_Driven)
#         Owner=int(request.form['Owner'])
#         Fuel_Type_Petrol=request.form['Fuel_Type_Petrol']
#         if(Fuel_Type_Petrol=='Petrol'):
#                 Fuel_Type_Petrol=1
#                 Fuel_Type_Diesel=0
#         else:
#             Fuel_Type_Petrol=0
#             Fuel_Type_Diesel=1
#         Year=2020-Year
#         Seller_Type_Individual=request.form['Seller_Type_Individual']
#         if(Seller_Type_Individual=='Individual'):
#             Seller_Type_Individual=1
#         else:
#             Seller_Type_Individual=0	
#         Transmission_Mannual=request.form['Transmission_Mannual']
#         if(Transmission_Mannual=='Mannual'):
#             Transmission_Mannual=1
#         else:
#             Transmission_Mannual=0
#         prediction=model.predict([[Present_Price,Kms_Driven2,Owner,Year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Mannual]])
#         output=round(prediction[0],2)
#         if output<0:
#             return render_template('index.html',prediction_texts="Sorry you cannot sell this car")
#         else:
#             return render_template('index.html',prediction_text="You Can Sell The Car at {}".format(output))
#     else:
#         return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)