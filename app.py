from flask import Flask, jsonify, request, render_template
import mysql.connector
from flask_restful import Resource, Api
from flaskext.mysql import MySQL

app=Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = MySQL()

api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'usertst'
app.config['MYSQL_DATABASE_PASSWORD'] = 'passwordtst'
app.config['MYSQL_DATABASE_DB'] = 'tst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)

#Get All
class MainPage(Resource):
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

# API Resource Routes
api.add_resource(MainPage, '/')
api.add_resource(View, '/maternalrisk')
api.add_resource(ViewRisk, '/maternalrisk/<string:get_risk>')
api.add_resource(Insert, '/maternalrisk/insert')
api.add_resource(Update, '/maternalrisk/update/<int:up_age>/<string:up_risk>')
api.add_resource(Erase, '/maternalrisk/delete/<int:del_age>/<string:del_risk>')

if __name__=="__main__":
    app.run(debug=True)