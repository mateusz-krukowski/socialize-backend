from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import pymysql


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
pymysql.install_as_MySQLdb()

# Konfiguracja połączenia z bazą danych MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/socialize'
db = SQLAlchemy(app)

@app.route("/")
@cross_origin()
def index():
    return {
        "Status": "True"
    }


if __name__ == "__main__":
    app.run(debug=True)
