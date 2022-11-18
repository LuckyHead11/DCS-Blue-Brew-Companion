# Made Happily with Github Copilot
# For the Blue Brew Coffee Shop
# Made by: Joshua Kirby
# Date of creation 11/2/2022

from os import path
import os
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request, flash, session
import datetime
import time
import base64


exe_file = False
if exe_file:
    print("Welcome to Blue Brew Companion!")
    print("You have 2 options")
    print("1. Run the program as usual")
    print("2. Change admin password")

    while True:
        option = int(input("Enter option: "))
        if option == 1:
            exe_file = False
            break
        elif option == 2:
            # Read from secret/password.txt
            with open("secret/password.txt", "rb") as f:
                password = f.read()
            current_password = str(base64.b64decode(password).decode("utf-8"))
            current_password_check = input("Please enter your old password: ")
            if current_password_check == current_password:
                new_password = input("Please enter your new password: ")
                new_password_check = input(
                    "Please re-enter your new password: ")
                if new_password == new_password_check:
                    # Write to secret/password.txt
                    with open("secret/password.txt", "wb") as f:
                        f.write(base64.b64encode(new_password.encode("utf-8")))
                    print("Successfully changed password!")
                    break
                else:
                    print("Passwords do not match!")
            else:
                print("Password is incorrect!")


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


admin_password = ""

with open("secret/password.txt", "rb") as f:
    password = f.read()
admin_password = str(base64.b64decode(password).decode("utf-8"))


def get_item_image(name, company):
    try:
        query = f"A photograph of {company} {name}"
        """Search a query on google"""
        import requests
        from bs4 import BeautifulSoup

        url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"}
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

        # Pick a random image from the folder and only save that image
        import random

        random_image = random.choice(os.listdir(f"static/{name}"))
        os.rename(f"static/{name}/{random_image}", f"static/{name}/choose.png")

    except:
        pass


app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "The Blue brew is better than any other Coffee Shop in the world"


db = SQLAlchemy(app)
current_items = []
cost = 0


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    item_price = db.Column(db.String(100), nullable=False)
    item_food = db.Column(db.Boolean, nullable=False, default=False)


class LogData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_name = db.Column(db.String(100), nullable=False)
    log_description = db.Column(db.String(255), nullable=False)
    log_severity = db.Column(db.String(100), nullable=False)
    log_date = db.Column(db.String(100), nullable=False)


class ItemOrdered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_price = db.Column(db.String(100), nullable=False)
    item_day = db.Column(db.Integer)
    item_month = db.Column(db.Integer)
    item_year = db.Column(db.Integer)
    item_week = db.Column(db.Integer)


def check_admin():
    is_admin = session.get("admin")
    if is_admin:

        print("Successfully logged in as admin!")
        return True
    else:
        flash("You are not logged in as an admin!", category="error")

        return False


def create_log_data(name, description, severity):

    if severity == 0:
        severity = "Low"
    elif severity == 1:
        severity = "Medium"
    elif severity == 2:
        severity = "Severe"
    # Only have the year, month, day, and week
    date = datetime.datetime.now()
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    log = LogData(log_name=name, log_description=description,
                  log_severity=severity, log_date=f"{month}/{day}/{year} at {hour}:{minute}")
    print("Successfully created log data! (NOTE ONLY FOR ADMINS!)")
    db.session.add(log)
    db.session.commit()


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


@app.route("/checkout")
def checkout():

    total_cost = 0
    for item in current_items:
        total_cost += float(str(item.item_price).replace("$", ""))

    total_cost = '{:,.2f}'.format(total_cost)
    return render_template("checkout.html", current_items=current_items, cost=str(total_cost))


@app.route('/order')
def order():
    cost = 0
    items = Item.query.all()
    # remove all the items fro mthe items list

    for item in current_items:
        item.item_price = item.item_price.replace("$", "").replace(",", "")
        cost += float(str(item.item_price).replace("$", ""))

    cost = '{:,.2f}'.format(cost)
    return render_template('order.html', items=items, current_items=current_items, cost=cost)


@app.route("/new-database")
def new_database():
    db.drop_all()
    db.create_all()
    return redirect("/")


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


@app.route('/clear-admin')
def clear_admin():
    # Remove all the LogData items from the database
    LogData.query.delete()
    db.session.commit()


@app.route('/confirm-edit', methods=['POST'])
def confirm_edit():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price').replace("$", "")

    if item_price != "":

        item_price = '{:,.2f}'.format(float(item_price))
    else:
        flash("Cannot have an empty price! So we put it as $0.00", category="error")
        item_price = float("0.00")

    item = Item.query.filter_by(item_name=item_name).first()
    item.item_description = item_description
    item.item_price = item_price
    item.item_name = item_name
    flash("Successfully edited the item!")
    db.session.commit()

    print(
        f"Successfully edited item! Item Name: {item_name} Item Description: {item_description} Item Price: {item_price}")
    create_log_data(f"Edited Item: {item_name}",
                    f"Successfully edited item!", 1)
    return redirect('/admin_food')


@app.errorhandler(404)
def page_not_found(e):
    flash("Page not found!", category="error")
    return render_template("404.html"), 404


@app.route("/admin-login", methods=['GET', 'POST'])
def admin_login():
    return render_template("admin_login.html")


@app.route('/admin')
def admin():

    if check_admin():
        return render_template('admin.html')
    else:
        return redirect("/admin-login")


@app.route('/add', methods=['POST'])
def add():
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')

    try:
        if request.form.get('item_price') != "":
            item_price = str('{:,.2f}'.format(
                float(request.form.get('item_price').replace("$", ""))))
            item_food = request.form.get('item_food')

            if item_price != None or item_name != "" or item_description != "":
                if item_food == "on":
                    item_food = True
                else:
                    item_food = False
                item = Item(item_name=item_name, item_description=item_description,
                            item_price=item_price, item_food=item_food)

                print(
                    f"Item Name: {item_name} Item Description: {item_description} Item Price: {item_price}")

                if item_food:
                    item_food = "snack"
                else:
                    item_food = "drink"
                create_log_data(name="Created Item: " + item_name,
                                description=f"This is a {item_food}", severity=0)
                db.session.add(item)
                db.session.commit()

                flash("Successfully added the item!")
                return redirect('/')
            else:
                flash("Please fill in all the fields!", category="error")
                return redirect('/new_item')
        else:
            flash("Make sure to fill in the price!", category="error")
            return redirect('/new_item')
    except:
        flash("Critical Error!", category="error")
        return redirect('/new_item')


@app.route("/clear_order")
def clear_order():
    current_items.clear()
    flash("Successfully cleared the order!", category="success")
    return redirect("/order")


@app.route('/add_order/<id>')
def add_order(id):
    item = Item.query.filter_by(id=id).first()
    current_items.append(item)
    return redirect('/order')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == "jreynolds@decaturchristian.net":
        if password == admin_password:
            print("Successfully logged in as admin!")

            session["admin"] = True
            flash("Successfully authenticated user as an admin!")
            create_log_data(
                "Admin Login", "Somebody has logged in under admin", 2)
            return redirect("/admin")
        else:
            flash("Incorrect password!", category="error")
            return redirect("/admin-login")
    else:
        flash("Incorrect email!", category="error")
        return redirect("/admin-login")


@app.route("/tendered")
def tendered():
    total_cost = 0
    for item in current_items:
        total_cost += float(str(item.item_price).replace("$", ""))

    total_cost = '{:,.2f}'.format(total_cost)
    return render_template("tendered.html", total_cost=total_cost)


@app.route("/confirm_tender", methods=['POST'])
def confirm_tender():
    try:
        tendered = str(request.form.get('tendered'))
        o_tendered = tendered
        tendered = tendered.replace("$", "")
        tendered = float(tendered)
        cost = 0
        for item in current_items:
            cost += float(item.item_price.replace("$", ""))

        change = tendered - cost
        
        cost = '{:,.2f}'.format(cost)
        o_tendered = '{:,.2f}'.format(float(o_tendered.replace("$", "")))

        total_cost = 0
        if change < 0:
            flash("Not enough money tendered! Must be higher than: $" +
                    str(cost), category="error")
            return redirect("/tendered")
        else:
            change = '{:,.2f}'.format(change)
            for item in current_items:
                total_cost += float(str(item.item_price).replace("$", ""))

                # Create item ordred data
                item_ordered = ItemOrdered(item_price=item.item_price, item_day=datetime.datetime.now().day, item_month=datetime.datetime.now().month, item_year=datetime.datetime.now().year,
                                            item_week=datetime.datetime.now().isocalendar()[1])
                db.session.add(item_ordered)
                db.session.commit()
            return render_template("confirm_tender.html", change=change, tendered=o_tendered, total=str(cost))
    except:
        flash("Wrong Input!", category="error")
        return redirect("/tendered")


@app.route('/remove_item/<id>')
def delete(id):
    flash("Successfully removed the item!")
    item = Item.query.filter_by(id=id).first()

    # remove the folder
    print(f"SUCCESSFULLY REMOVED {item.item_name}")

    create_log_data("Removed: " + item.item_name,
                    "Successfully removed item!", 2)
    db.session.delete(item)
    db.session.commit()
    return redirect('/admin_food')


@app.route("/admin_food")
def admin_food():
    items = Item.query.all()
    if check_admin():
        return render_template("admin_food.html", items=items)
    else:
        return redirect("/admin-login")


@app.route('/admin_earnings')
def admin_earnings():
    monthly_earnings = 0
    daily_earnings = 0
    yearly_earings = 0
    weekly_earnings = 0
    items = ItemOrdered.query.all()
    for item in items:
        if item.item_month == datetime.datetime.now().month:
            monthly_earnings += float(item.item_price)
        if item.item_day == datetime.datetime.now().day:
            daily_earnings += float(item.item_price)
        if item.item_year == datetime.datetime.now().year:
            yearly_earings += float(item.item_price)
        if item.item_week == datetime.datetime.now().isocalendar()[1]:
            weekly_earnings += float(item.item_price)

    # Make all the earnings into formatted money strings
    monthly_earnings = str('{:,.2f}'.format(monthly_earnings))
    daily_earnings = str('{:,.2f}'.format(daily_earnings))
    yearly_earings = str('{:,.2f}'.format(yearly_earings))
    weekly_earnings = str('{:,.2f}'.format(weekly_earnings))
    if check_admin():
        return render_template("admin_earnings.html", me=monthly_earnings, de=daily_earnings, ye=yearly_earings, we=weekly_earnings)
    else:
        return redirect("/admin-login")


@app.route("/admin_logdata")
def admin_logdata():
    log_data = LogData.query.all()
    # Make log_data into a list
    log_data = list(log_data)
    # Reverse the list so that the newest logs are at the top
    log_data.reverse()
    if check_admin():
        return render_template("admin_logdata.html", log_data=log_data)
    else:
        return render_template("admin_login.html")


if __name__ == '__main__':
    create_database(app)
    app.run(host="0.0.0.0", port=5000)


# pyinstaller -F --add-data "templates;templates" --add-data "static;static" --name BlueBrewCompanion main.py
