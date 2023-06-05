from flask import Flask, request
from flask_cors import CORS, cross_origin
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

@app.route("/")
@cross_origin()
def index():
    return {
        "Status": "True"
    }


@app.route("/register", methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    print(data)
    email = data['email']
    username = data['username']
    password = data['password']

    existing_email_user = User.query.filter_by(email=email).first()
    if existing_email_user:
        return {"response": "this email is already taken"}

    existing_username_user = User.query.filter_by(username=username).first()
    if existing_username_user:
        return {"response": "this username is already taken"}

    new_user = User(email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {"response": "Registration Completed. User created successfully"}


if __name__ == "__main__":
    app.run(debug=True)
