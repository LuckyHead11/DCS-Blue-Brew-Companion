from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from os import path

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"


db= SQLAlchemy(app)

@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

def create_database(app):
    if not path.exists("instance/" + "site.db"):
        with app.app_context():
            db.create_all()
        print("Created Database!")
    else:
        print("Database already created!")
if __name__ == '__main__':
    create_database(app)
    app.run(host="0.0.0.0", port=5000)