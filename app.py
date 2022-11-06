from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from os import path

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"


db= SQLAlchemy(app)

class Item(db.Model):
    id = id.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    item_price = db.Column(db.String(100), nullable=False)




@app.route('/')
def index():
    return render_template('index.html')

def create_database(app):
    if not path.exists("instance/" + "site.db"):
        with app.app_context():
            db.create_all()
        print("Created Database!")
    else:
        print("Database already created!")

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/new_item')
def new_item():
    return render_template('new_item.html')
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
if __name__ == '__main__':
    create_database(app)
    app.run(host="0.0.0.0", port=5000)