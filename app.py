from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from download_image import get_item_image
app = Flask(__name__)
from os import path

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"


db= SQLAlchemy(app)
current_items = []
cost = 0



class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    item_price = db.Column(db.String(100), nullable=False)
    item_food = db.Column(db.Boolean, nullable=False, default=False)




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
    cost = 0
    items = Item.query.all()
    for item in current_items:
        cost += float(str(item.item_price).replace("$", ""))
    print(cost)
    return render_template('order.html', items=items, current_items=current_items,cost=cost)

@app.route('/new_item')
def new_item():
    return render_template('new_item.html')
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



@app.route('/add',methods=['POST'])
def add():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price')
    item_food = request.form.get('item_food')
    if item_food == "on":
        item_food = True
    else:
        item_food = False
    item = Item(item_name=item_name, item_description=item_description, item_price=item_price, item_food=item_food)

    print(f"Item Name: {item_name} Item Description: {item_description} Item Price: {item_price}")

    get_item_image(item_name, item_description)
    db.session.add(item)
    db.session.commit()
    return redirect('/')

@app.route('/add_order/<id>')
def add_order(id):
    item = Item.query.filter_by(id=id).first()
    current_items.append(item)
    return redirect('/order')

if __name__ == '__main__':
    create_database(app)
    app.run(host="0.0.0.0", port=5000)