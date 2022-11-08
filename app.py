import time





from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

import os
from os import path
def get_item_image(name, company):
    try:
        query = f"A photograph of {company} {name}"
        """Search a query on google"""
        import requests
        from bs4 import BeautifulSoup

        url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"
        headers = {"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        images = soup.find_all("img", class_="rg_i")
        count = 0

        os.mkdir("static/" + name)
        for image in images:
            
            
            image_url = image.get("data-src")
            if image_url is not None:
                count += 1
                r = requests.get(image_url)

                with open(f"static/{name}/{count}.png", "wb") as f:
                    f.write(r.content)

                if count >= 5:
                    break

        #Pick a random image from the folder and only save that image
        import random

        random_image = random.choice(os.listdir(f"static/{name}"))
        os.rename(f"static/{name}/{random_image}", f"static/{name}/choose.png")
        
    except:
        pass


app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "The Blue brew is better than any other Coffee Shop in the world"


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
    items = Item.query.all()
    return render_template('index.html', items=items)

def create_database(app):
    if not path.exists("instance/" + "site.db"):
        with app.app_context():
            db.create_all()
        print("Created Database!")
    else:
        print("Database already created!")
@app.route("/checkout")
def checkout():
    cost = 0
    items = Item.query.all()
    for item in current_items:
        cost += float(str(item.item_price).replace("$", ""))
    return render_template("checkout.html", current_items=current_items, cost=str(cost))

@app.route('/order')
def order():
    cost = 0
    items = Item.query.all()
    for item in current_items:
        cost += float(str(item.item_price).replace("$", ""))
    print(cost)
    return render_template('order.html', items=items, current_items=current_items,cost=cost)
@app.route('/new-order')
def new_order():
    current_items.clear()
    return redirect('/order')
@app.route('/new_item')
def new_item():
    return render_template('new_item.html')

@app.route('/edit_item/<id>')
def edit_item(id):
    item = Item.query.filter_by(id=id).first()
    return render_template('new_item.html', item=item)

@app.route('/confirm-edit', methods=['POST'])
def confirm_edit():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price').replace("$", "")
    item = Item.query.filter_by(item_name=item_name).first()
    item.item_description = item_description
    item.item_price = item_price
    flash("Successfully edited the item!")
    db.session.commit()

    print(f"Successfully edited item! Item Name: {item_name} Item Description: {item_description} Item Price: {item_price}")
    return redirect('/')
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



@app.route('/add',methods=['POST'])
def add():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price').replace("$", "")
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


    flash("Successfully added the item!")
    return redirect('/')

@app.route('/add_order/<id>')
def add_order(id):
    item = Item.query.filter_by(id=id).first()
    current_items.append(item)
    return redirect('/order')



@app.route('/remove_item/<id>')
def delete(id):
    flash("Successfully removed the item!")
    item = Item.query.filter_by(id=id).first()
    


    #remove the folder

    import shutil
    shutil.rmtree(f"static/{item.item_name}")
    print(f"SUCCESSFULLY REMOVED {item.item_name}")
    db.session.delete(item)
    db.session.commit()
    return redirect('/')
if __name__ == '__main__':
    create_database(app)
    app.run(host="0.0.0.0", port=5000)





#pyinstaller -F --add-data "templates;templates" --add-data "static;static" --name BlueBrewCompanion app.py