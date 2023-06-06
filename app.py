from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from sqlalchemy import text
from db import db
from User import User
import pymysql

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
pymysql.install_as_MySQLdb()

# Konfiguracja połączenia z bazą danych MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/socialize'

db.init_app(app)


@app.route("/register", methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    print(data)
    email = data['email']
    username = data['username']
    password = data['password']

    if not email:
        return {"response": "email cannot be empty"}, 400
    if not username:
        return {"response": "username cannot be empty"}, 400
    if not password:
        return {"response": "password cannot be empty"}, 400

    existing_email_user = User.query.filter_by(email=email).first()
    if existing_email_user:
        return {"response": "this email is already taken"}, 400

    existing_username_user = User.query.filter_by(username=username).first()
    if existing_username_user:
        return {"response": "this username is already taken"}, 400

    new_user = User(email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {"response": "Registration Completed. User created successfully"}


@app.route("/login", methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()


    email = data['email']
    password = data['password']

    user_exists = User.query.filter_by(email=email).first()
    if not user_exists:
        return {"response": "User doesn't exist"}, 400

    query = text("""
       SELECT password
       FROM socialize.users
       WHERE email = :email
       """)
    result = db.session.execute(query, {"email": email})
    password_from_query = result.fetchone()[0] if result.rowcount > 0 else None

    if password == password_from_query:
        query = text("""
           SELECT username
           FROM socialize.users
           WHERE email = :email
           """)
        result = db.session.execute(query, {"email": email})
        username = result.fetchone()[0] if result.rowcount > 0 else None
        print({"response": "logging in successful I guess", "username": username})
        return jsonify({"response": "logging in successful I guess", "username": username}), 200
    return {"response": "Wrong password"}, 400


if __name__ == "__main__":
    app.run(debug=True)
