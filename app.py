from flask import Flask, jsonify, request, render_template, redirect, session, make_response, url_for
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from functools import wraps
import os
import bcrypt
import jwt
import datetime

app=Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = MySQL()

api = Api(app)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretxxXx'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MYSQL_DATABASE_USER'] = 'usertst'
app.config['MYSQL_DATABASE_PASSWORD'] = 'passwordtst'
app.config['MYSQL_DATABASE_DB'] = 'tst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)

def token_required(f) :
    @wraps(f)
    def decorated(*args, **kwargs) :
        # token = None
        # if 'x-access-tokens' in request.headers:
        #    token = request.headers['x-access-tokens']
        token = session['token']
        if not token :
            response = jsonify('Token is missing!.')
            response.status_code = 403
            return response
        try :
            user = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if (user is None) :
                response = jsonify('Token is invalid!.')
                response.status_code = 403
                return response
        except Exception as e :
            response = jsonify(message = 'Token is invalid!.', error = str(e))
            response.status_code = 403
            return response
        return f(*args, **kwargs)
    return decorated

# Home
class MainPage(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('home.html'), 200, headers)

# Dashboard
class Dashboard(Resource):
    @token_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('dashboard.html'), 200, headers)

# Menu to different types of View
class ViewMenu(Resource):
    @token_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('viewmenu.html'), 200, headers)

# View all data
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

# View data by ID
class ViewbyID(Resource):
    @token_required
    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            get_idmr = request.form['id']
            cursor.execute(f"""SELECT * FROM MATERNAL_RISK WHERE idmr = {get_idmr}""")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

#View data by Risk
class ViewRisk(Resource):
    @token_required
    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            get_risk = request.form['Risk']
            cursor.execute(f"""SELECT * FROM MATERNAL_RISK WHERE RiskLevel = '{get_risk}'""")
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# INsert data to DB
class Insert(Resource):
    @token_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('insert.html'), 200, headers)

    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            _womanage = int(request.form['Age'])
            _systolicbp = int(request.form['SystolicBP'])
            _diastolicbp = int(request.form['DiastolicBP'])
            _bs = float(request.form['BS'])
            _bodytemp = float(request.form['BodyTemp'])
            _heartrate = int(request.form['HeartRate'])
            _risk = request.form['RiskLevel']
            insertval = f"""INSERT INTO maternal_risk(WomenAge, SystolicBP, DiastolicBP, BS, BodyTemp, HeartRate, RiskLevel) VALUES({_womanage}, {_systolicbp}, {_diastolicbp}, {_bs}, {_bodytemp}, {_heartrate}, '{_risk}')"""
            cursor.execute(insertval)
            conn.commit()
            response = jsonify(message='Data added to the dataset successfully.', id=cursor.lastrowid)
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify(message = 'Failed to add data to the dataset.', error = str(e))
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()
            return response

# Update data to DB
class Update(Resource):
    @token_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('update.html'), 200, headers)

    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            up_idmr = int(request.form['id'])
            _womenage = request.form['Age']
            _systolicbp = int(request.form['SystolicBP'])
            _diastolicbp = int(request.form['DiastolicBP'])
            _bs = float(request.form['BS'])
            _bodytemp = float(request.form['BodyTemp'])
            _heartrate = request.form['HeartRate']
            _risk = request.form['RiskLevel']
            updateval = f"""UPDATE MATERNAL_RISK SET WomenAge = {_womenage}, SystolicBP = {_systolicbp}, DiastolicBP = {_diastolicbp}, BS = {_bs}, BodyTemp = {_bodytemp}, HeartRate = {_heartrate}, RiskLevel = '{_risk}' WHERE IDMR = {up_idmr}"""      
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

# Delete data from DB
class Delete(Resource):
    @token_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('delete.html'), 200, headers)

    def post(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()
            del_idmr = int(request.form['id'])
            delval = f"""DELETE FROM MATERNAL_RISK WHERE IDMR = {del_idmr}"""
            cursor.execute(delval)
            conn.commit()
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

# Register Account
class Register(Resource) :
    def check_password(self, password) :
        if len(password) >= 6 and len(password) <= 20 and any(char.isdigit() for char in password) \
            and any(char.isupper() for char in password) and any(char.islower() for char in password):
            return True
        else:
            return False

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html'), 200, headers)

    def post(self):
        conn = db.connect()
        cursor = conn.cursor()
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
            cursor.execute(f"""SELECT * FROM USERS WHERE username = '{username}'""")
            rows = cursor.fetchall()
            if len(rows) > 0:
                response = jsonify('Username already exists.')
                response.status_code = 400
                return response

            # insert new user into db
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            cursor.execute("INSERT INTO USERS (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            response = jsonify('User registered successfully.')
            response.status_code = 201
            # headers = {'Content-Type': 'text/html'}
            return redirect(url_for("mainpage"))
        except Exception as e:
            print(e)
            response = jsonify(message = 'Failed to add data to the dataset.', error = str(e))
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()

# Login Account
class Login(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'), 200, headers)

    def post(self):
        conn = db.connect()
        cursor = conn.cursor()
        try:
            username = request.form['username']
            password = request.form['password']
            if (username is None or password is None):
                response = jsonify('Please provide both username and password.')
                response.status_code = 400
                return response

            # check if username is in db
            cursor.execute(f"""SELECT * FROM USERS WHERE username = '{username}'""")
            rows = cursor.fetchall()
            if len(rows) == 0:
                response = jsonify('Username does not exist.')
                response.status_code = 400
                return response

            # check if password is correct
            if bcrypt.checkpw(password.encode('utf-8'), rows[0][2].encode('utf-8')):
                token = jwt.encode({'username': username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                response = jsonify(message = 'User logged in successfully.', token = token)
                session['name'] = username
                session['token'] = token
                # create token for user
                response.status_code = 200
                return redirect(url_for("dashboard"))         
            else:
                response = jsonify('Incorrect password.')
                response.status_code = 400
                return response
        except Exception as e:
            print(e)
            response = jsonify(message = 'Failed to add data to the dataset.', error = str(e))
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()

# Logout
class Logout(Resource):
    def get(self):
        session.clear()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('home.html'), 200, headers)

# API Resource Routes
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Register, '/register')
api.add_resource(MainPage, '/')
api.add_resource(Dashboard, '/dashboard')
api.add_resource(ViewMenu, '/view-menu')
api.add_resource(View, '/view-all')
api.add_resource(ViewRisk, '/view-risk')
api.add_resource(ViewbyID, '/view-id')
api.add_resource(Insert, '/insert')
api.add_resource(Update, '/update') 
api.add_resource(Delete, '/delete')

if __name__=="__main__":
    app.run(debug=True)