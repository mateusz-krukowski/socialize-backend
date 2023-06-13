import logging
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
from sqlalchemy import text, select
from db import db
from User import User
from Message import Message
import pymysql

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
pymysql.install_as_MySQLdb()

# Konfiguracja połączenia z bazą danych MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://mateuszkrukowski:password2137@db4free.net/socialize'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/socialize'

db.init_app(app)

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@app.route("/", methods=["GET"])
def index():
    return "API is working"


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

        query = text("""
                   SELECT is_admin
                   FROM socialize.users
                   WHERE email = :email
                   """)
        result = db.session.execute(query, {"email": email})
        is_admin = result.fetchone()[0] if result.rowcount > 0 else None
        is_admin = True if is_admin == 1 else False if is_admin == 0 else None

        print({"response": "logging in successful I guess", "username": username, "isAdmin": is_admin})
        return jsonify({"response": "logging in successful I guess", "username": username, "isAdmin": is_admin}), 200

    return {"response": "Wrong password"}, 400


@app.route("/api/getmessages", methods=['GET'])
@cross_origin()
def get_messages():
    messages = Message.query.order_by(Message.date.asc()).all()
    result = []
    for message in messages:
        date_str = message.date.strftime('%a, %d %b %Y %H:%M:%S')
        formatted_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
        result.append({
            'user': message.user.username,
            'text': message.text,
            'date': formatted_date
        })
    print(result)
    return jsonify(result)


@app.route("/api/sendmessage", methods=["POST"])
@cross_origin()
def send_message():
    data = request.get_json()
    username = data.get('user')
    text = data.get('text')
    date_str = data.get('date')
    user = User.query.filter_by(username=username).first()
    new_message = Message(user_id=user.id, text=text, date=datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S'))
    db.session.add(new_message)
    db.session.commit()
    print(data)
    return "Message sent correctly", 200


@app.route("/api/getusers", methods=["GET"])
@cross_origin()
def get_users():
    users_list = User.query.all()
    result = []
    for user in users_list:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'is_admin': bool(user.is_admin)
        })
    # print(result)
    return jsonify(result), 200


@app.route("/api/edituser", methods=["POST"])
@cross_origin()
def edit_user():
    user_data = request.get_json()
    user_id = user_data.get('id')
    print(request.get_json())
    try:
        user = User.query.get(user_id)
        if user:
            user.username = user_data.get('username')
            user.email = user_data.get('email')
            user.is_admin = user_data.get('is_admin')
            user.password = user_data.get('password')
            db.session.commit()
            return jsonify({'message': 'User data updated successfully'})
        else:
            new_user = User(

                username=user_data.get('username'),
                email=user_data.get('email'),
                is_admin=user_data.get('is_admin'),
                password=user_data.get('password')
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'New user created successfully'})

    except Exception as e:
        return jsonify({'message': 'Error occurred while updating user data', 'error': str(e)})


@app.route("/api/deleteuser", methods=["DELETE", "POST"])
@cross_origin()
def delete_user():
    user_id = request.get_json()
    print(user_id)
    if user_id == 1:
        return jsonify({'message': 'This user cannot be deleted'})

    try:
        user = User.query.get(user_id)
        # Usuń powiązane rekordy z tabeli messages
        db.session.query(Message).filter_by(user_id=user_id).delete()
        if user:
            db.session.delete(user)
            db.session.commit()
            query = text("""ALTER TABLE socialize.users AUTO_INCREMENT = 1;""")
            db.session.execute(query)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        else:
            return jsonify({'message': 'User not found'})
    except Exception as e:
        return jsonify({'message': 'Error occurred while deleting user', 'error': str(e)})
    return 200


@app.route('/api/showservertime', methods=['GET'])
@cross_origin()
def show_server_time():
    def generate_server_time():
        while True:
            time = datetime.now().strftime("%H:%M:%S")
            yield f"data: {time}\n\n"

    return Response(generate_server_time(), mimetype='text/event-stream')


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
