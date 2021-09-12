import pymysql
from app import app
from config import mysql
from flask import jsonify
import json
from flask import flash, request
from password_strength import PasswordPolicy
import uuid

@app.before_request
def validate_token():
    path = request.path
    authentication_not_required = {"login": "/api/login", "signup": "/api/signup"}
    if path != authentication_not_required['login'] or path != authentication_not_required['signup']:
        token = request.headers["Authorization"]
        setattr(request, 'token', token)
        if token == '':
            return {"Error": "Unauthorized user!"}, 401

@app.before_request
def validate_userId():
    path = request.path
    excluded_paths = {"login": "/api/login", "signup": "/api/signup"}
    if(path != excluded_paths['login'] and path != excluded_paths['signup']):
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = "Select userId from users where token = %s"
        token = request.token
        # print(token)
        values = (token)
        status = cursor.execute(sql, values)
        results = cursor.fetchone()
        print(results)
        # print(status)
        if status == 1:
            userId = results[0]
            # print(userId)
            setattr(request, "userId", userId)
        else:
            return {"Error": "Unauthorized user!"}, 401

@app.route('/api/signup', methods = ['POST'])
def signup():
    username = request.json['username']
    password = request.json['password']
    policy = PasswordPolicy.from_names(
        length = 6,
        special = 1,
    )
    token = str(uuid.uuid4())
    print(policy.test(password))
    if policy.test(str(password)) == []:
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = 'insert into users(username, password, token) values(%s, %s, %s)'
        values = (username, password, token)
        cursor.execute(sql, values)
        connection.commit()
        return {"Success": "You have signed up successfully!"}, 201
    else:
        return {"Error": "Please check your password; It must contain atleast 6 characters and 1 special character!"}, 400

@app.route('/api/login', methods = ['POST'])
def login():
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        username = request.json['username']
        password = request.json['password']
        sql = 'select token from users where username = %s and password = %s'
        values = (username, password)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        print(result)
        response = result[0]
        print(response)
        return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

@app.route('/api/course', methods = ['GET'])
def get_all_items():
    try:
        sql = 'select itemId, title, description from items'
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        row_headers = [x[0] for x in cursor.description]
        json_data = []
        for result in results:
            json_data.append(dict(zip(row_headers,result)))
        return json.dumps(json_data)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

def validate_items(data):
    error_messages = {}
    is_valid = True
    if data["title"] == "" or data["title"] == None:
        error_messages["name"] = "Title is required!"
        is_valid = False
    if data['description'] == "":
        error_messages["description"] = "Description is required!"
        is_valid = False
    if not is_valid:
        error_messages["isFormValid"] = False
    else:
        error_messages["isFormValid"] = True
    return error_messages

@app.route('/api/course', methods = ['POST'])
def insert_item():
    userId = request.userId
    data = request.json
    try:
        errors = validate_items(data)
        if errors['isFormValid']:
            title = data['title']
            description = data['description']
            connection = mysql.connect()
            cursor = connection.cursor()
            sql = "insert into items(title, description, userId, status) Values(%s, %s, %s, 1)"
            values = (title, description, userId)
            cursor.execute(sql, values)
            connection.commit()
            return {"Message": "Syllabus item inserted successfully!"}
        else:
            del errors['isFormValid']
            return not_found(), 400
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route('/api/course/<id>', methods = ['PUT'])
def update_item(id):
    try:
        userId = request.userId
        data = request.json
        errors = validate_items(data)
        if errors['isFormValid']:
            title = data['title']
            description = data['description']
            connection = mysql.connect()
            cursor = connection.cursor()
            sql = "update items set name = %s, description = %s where itemId = %s and userId = %s"
            values = (title, description, id, userId)
            cursor.execute(sql, values)
            connection.commit()
            return {"Message": "Syllabus item updated successfully!"}
        else:
            del errors["isFormValid"]
            return errors, 400
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

@app.route('/api/course/<id>', methods=['DELETE'])
def delete_item(id):
    try:
        userId = request.userId
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = "update items set status = 0 where itemId = %s and userId = %s"
        itemId = id
        values = (itemId, userId)
        status = cursor.execute(sql, values)
        connection.commit()
        if (status == 1):
            return {"Message": "Syllabus item deleted successfully!"}, 200
    except Exception as e:
        print(e)    
    finally:
        cursor.close() 
        connection.close()

@app.route('/api/course/<id>', methods=['GET'])
def search_item(id):
    try:
        itemId = id
        userId = request.userId
        connection = mysql.connect()
        cursor = connection.cursor()
        sql = "select itemId, title, description from items where itemId = %s and userId = %s and status = 1"
        values = (itemId, userId)
        status = cursor.execute(sql, values)
        results = cursor.fetchall()
        if status == 1:
            row_headers = [x[0] for x in cursor.description]
            json_data = []
            for result in results:
                json_data.append(dict(zip(row_headers,result)))
        return json.dumps(json_data)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

@app.errorhandler(404)
def not_found(error = None):
    message = {
        'status': 404,
        'message': 'Not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response

if(__name__) == '__main__':
    app.run(debug=True)
