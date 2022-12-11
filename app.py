from flask import Flask, jsonify, request, render_template
import mysql.connector
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
import os
import bcrypt
import jwt
import datetime

app=Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = MySQL()

api = Api(app)

SECRET_KEY = os.environ('SECRET_KEY') or 'secretxxXx'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MYSQL_DATABASE_USER'] = 'usertst'
app.config['MYSQL_DATABASE_PASSWORD'] = 'passwordtst'
app.config['MYSQL_DATABASE_DB'] = 'tst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)

def token_required(f) :
    @wraps(f)
    def decorated(*args, **kwargs) :
        token = request.args.get('token')
        if not token :
            return jsonify({'message' : 'Token is missing!'}), 403
        try :
            user = jwt.decode(token, app.config['SECRET_KEY'])
            if (user is None) :
                return jsonify({'message' : 'Token is invalid!'}), 403
        except Exception as e :
            return jsonify({'message' : 'Token is invalid!', 'error' : str(e)}), 403
        return f(user, *args, **kwargs)
    return decorated

#Get All
class MainPage(Resource):
    @token_required
    def get(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MATERNAL_RISK LIMIT 10")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

class View(Resource):
    @token_required
    def get(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MATERNAL_RISK")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

class ViewRisk(Resource):
    @token_required
    def get(self, get_risk):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            get_risk = get_risk.replace("-", " ")
            cursor.execute(f"""SELECT * FROM MATERNAL_RISK WHERE RiskLevel = '{get_risk}'""")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

class Insert(Resource):
    @token_required
    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            _age = int(request.form['Age'])
            # print(_age)
            _systolicbp = int(request.form['SystolicBP'])
            # print(_systolicbp)
            _diastolicbp = int(request.form['DiastolicBP'])
            # print(_diastolicbp)
            _bs = float(request.form['BS'])
            # print(_bs)
            _bodytemp = float(request.form['BodyTemp'])
            # print(_bodytemp)
            _heartrate = int(request.form['HeartRate'])
            # print(_heartrate)
            _risk = request.form['RiskLevel']
            # print(_risk)
            insertval = f"""INSERT INTO MATERNAL_RISK VALUES({_age}, {_systolicbp}, {_diastolicbp}, {_bs}, {_bodytemp}, {_heartrate}, {_risk})"""
            # print(insertval)
            cursor.execute(insertval)
            # print(1)
            conn.commit()
            response = jsonify(message='Data added to the dataset successfully.', id=cursor.lastrowid)
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify('Failed to add data to the dataset.')
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return(response)

class Update(Resource):
    @token_required
    def put(self, up_age, up_risk):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            up_risk = up_risk.replace("-", " ")
            # _age = request.form['Age']
            _systolicbp = int(request.form['SystolicBP'])
            _diastolicbp = int(request.form['DiastolicBP'])
            _bs = float(request.form['BS'])
            _bodytemp = float(request.form['BodyTemp'])
            _heartrate = request.form['HeartRate']
            # _risk = request.form['RiskLevel']
            # updateval = """UPDATE MATERNAL_RISK SET Age = %d, SystolicBP = %d, DiastolicBP = %d, BS = %d, BodyTemp = %d, HeartRate = %d, RiskLevel = %s WHERE age ="""      
            updateval = f"""UPDATE MATERNAL_RISK SET SystolicBP = {_systolicbp}, DiastolicBP = {_diastolicbp}, BS = {_bs}, BodyTemp = {_bodytemp}, HeartRate = {_heartrate} WHERE `﻿Age` = {up_age} and RiskLevel = '{up_risk}'"""      
            cursor.execute(updateval)
            conn.commit()
            response = jsonify(message='Data in the dataset updated successfully.', id=cursor.lastrowid)
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify('Failed to update data in the dataset.')
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return(response)

class Erase(Resource):
    @token_required
    def delete(self, del_age, del_risk):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            del_risk = del_risk.replace("-", " ")
            print(del_risk)
            delval = f"""DELETE FROM MATERNAL_RISK WHERE `﻿Age` = {del_age} and RiskLevel = '{del_risk}'"""
            cursor.execute(delval)
            conn.commit()
            print(1)
            response = jsonify(message='Data in the dataset deleted successfully.', id=cursor.lastrowid)
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify('Failed to delete data in the dataset.')
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return(response)

class Register(Resource) :
    def check_password(password) :
        if len(password) >= 6 and len(password) <= 20 and any(char.isdigit() for char in password) \
            and any(char.isupper() for char in password) and any(char.islower() for char in password):
            return True
        else:
            return False

    def post(self):
        try :
            username = request.form['username']
            password = request.form['password']
            if (username is None or password is None):
                response = jsonify('Please provide both username and password.')
                response.status_code = 400
                return response

            # check password validation
            if not self.check_password(password):
                response = jsonify('Password must be between 6 and 20 characters, and must contain at least one digit, one uppercase letter, and one lowercase letter.')
                response.status_code = 400
                return response
            
            # check if username is unique by querying into db
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(f"""SELECT * FROM USERS WHERE username = '{username}'""")
            rows = cursor.fetchall()
            if len(rows) > 0:
                response = jsonify('Username already exists.')
                response.status_code = 400
                return response

            # insert new user into db
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            cursor.execute(f"""INSERT INTO USERS (username, password) VALUES ('{username}', '{hashed_password}')""")
            conn.commit()
            response = jsonify('User registered successfully.')
            response.status_code = 201
            return response
        except Exception as e:
            print(e)
            response = jsonify('Failed to add data to the dataset.')
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return(response)

class Login(Resource):
    def post(self):
        try:
            username = request.form['username']
            password = request.form['password']
            if (username is None or password is None):
                response = jsonify('Please provide both username and password.')
                response.status_code = 400
                return response

            # check if username is in db
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(f"""SELECT * FROM USERS WHERE username = '{username}'""")
            rows = cursor.fetchall()
            if len(rows) == 0:
                response = jsonify('Username does not exist.')
                response.status_code = 400
                return response

            # check if password is correct
            if bcrypt.checkpw(password.encode('utf-8'), rows[0][2].encode('utf-8')):
                token = jwt.encode({'username': username, 'exp' : datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
                response = jsonify({'message' : 'User logged in successfully.', 'token': token.decode('UTF-8')})
                # create token for user
                response.status_code = 200
                return response
            else:
                response = jsonify('Incorrect password.')
                response.status_code = 400
                return response
        except Exception as e:
            print(e)
            response = jsonify('Failed to add data to the dataset.')
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return(response)

# API Resource Routes
api.add_resource(Login, '/login')
api.add_resource(Register, '/register')
api.add_resource(MainPage, '/')
api.add_resource(View, '/maternalrisk')
api.add_resource(ViewRisk, '/maternalrisk/<string:get_risk>')
api.add_resource(Insert, '/maternalrisk/insert')
api.add_resource(Update, '/maternalrisk/update/<int:up_age>/<string:up_risk>')
api.add_resource(Erase, '/maternalrisk/delete/<int:del_age>/<string:del_risk>')

if __name__=="__main__":
    app.run(debug=True)