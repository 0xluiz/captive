from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
mail = Mail(app)

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
