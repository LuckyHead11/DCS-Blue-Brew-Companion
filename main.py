# Made Happily with Github Copilot
# For the Blue Brew Coffee Shop
# Made by: Joshua Kirby
# Date of creation 11/2/2022

#mport jsonify
from flask import jsonify
from os import path
import os
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request, flash, session
import datetime
import base64
import paramiko
import random
import re
import SamsScraper
import time

sams = SamsScraper.SamsScraper()
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
            if (current_password_check.lower() == "help!"):
                print("Help has been granted! Your old password is: " + current_password)
                exit()
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
inspirational_quotes = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "The best way to predict the future is to invent it. - Alan Kay",
    "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
    "The only way to achieve the impossible is to believe it is possible. - Charles Kingsleigh",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "Dream big and dare to fail. - Norman Vaughan",
    "Don't be pushed around by the fears in your mind. Be led by the dreams in your heart. - Roy T. Bennett",
    "Act as if what you do makes a difference. It does. - William James",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "What you get by achieving your goals is not as important as what you become by achieving your goals. - Zig Ziglar",
    "The only place where success comes before work is in the dictionary. - Vidal Sassoon",
    "Don't be afraid to give up the good to go for the great. - John D. Rockefeller",
    "I find that the harder I work, the more luck I seem to have. - Thomas Jefferson",
    "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau",
    "Opportunities don't happen. You create them. - Chris Grosser",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "The best revenge is massive success. - Frank Sinatra",
    "Don't be afraid to give up the good to go for the great. - John D. Rockefeller"
]

def get_qod():
    return random.choice(inspirational_quotes)


app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "The Blue brew is better than any other Coffee Shop in the world"

db = SQLAlchemy(app)
current_items = []
cost = 0

sams_list = []

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
    item_name = db.Column(db.String(100), nullable=False)

    item_day = db.Column(db.Integer)
    item_month = db.Column(db.Integer)
    item_year = db.Column(db.Integer)
    item_week = db.Column(db.Integer)

class GroceryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grocery_name = db.Column(db.String(100), nullable=False)
    sams_name = db.Column(db.String(100), nullable=False)
    grocery_amount = db.Column(db.String(100), nullable=False)
    grocery_description = db.Column(db.String(255), nullable=False)
    grocery_price = db.Column(db.String(100), nullable=False)



sams_groceries = []
def upload_database_to_server():

    sftp_username = 'root'
    
    with open('secret/server_access.txt', 'r') as f:
        things = f.readlines()
    sftp_host = things[0].strip()
    sftp_password = things[1].strip()
    print("Connecting to the server...")
    print(sftp_host, sftp_username, sftp_password)
    remote_directory = '/root/BBC/database-backups/'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect(sftp_host, username=sftp_username, password=sftp_password)
    print("Connection successfully established ... ")

    # Create an SFTP session
    sftp = ssh.open_sftp()

    sftp.chdir(remote_directory)
    print(f"Changed to remote directory: {remote_directory}")

    print("Uploading file to the server... this may take a while depending on the size of the database.")
    local_file_path = os.path.join(os.getcwd(), 'instance/site.db')
    sftp.put(local_file_path, os.path.join(remote_directory, 'site.db'))
    print(f"File {local_file_path} uploaded successfully to {remote_directory}")

    remote_filename = f'Backup-{datetime.datetime.now().strftime("%Y-%m-%d")}.db'
    try:
        sftp.rename(os.path.join(remote_directory, 'site.db'), os.path.join(remote_directory, remote_filename))
    except IOError:
        print("File already exists!")
    print(f"File renamed to {remote_filename}")

    sftp.close()
    print("Redirecting...")
    return redirect("/admin")


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
    #Get the time in the right format

    now = datetime.datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    minute = now.strftime("%M")


    #Does datetime.datetime.now() account for the time zone?

    log = LogData(log_name=name, log_description=description,
                  log_severity=severity, log_date=f"{month}/{day}/{year} at {hour}:{minute}")
    print("Successfully created log data! (NOTE ONLY FOR ADMINS!)")
    db.session.add(log)
    db.session.commit()


@app.route('/')
def index():
    qod = get_qod()
    return render_template('index.html',qod=qod)


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

@app.route('/game')
def game():
    return render_template('game.html')
@app.route('/order')
def order():
    items = Item.query.all()
    
    #Sort all the items by alphabetical order
    items = sorted(items, key=lambda x: x.item_name)
            
    
    cost = '{:,.2f}'.format(sum(float(item.item_price.replace("$", "").replace(",", "")) for item in current_items))
    return render_template('order.html', items=items, current_items=current_items, cost=cost)

@app.route('/add_order/<int:id>', methods=['POST'])
def add_order(id):
    item = Item.query.get(id)
    if item:
        current_items.append(item)
        cost = sum(float(item.item_price.replace("$", "").replace(",", "")) for item in current_items)
        cost = '{:,.2f}'.format(cost)
        return jsonify({'current_items': [{'item_name': item.item_name, 'item_price': item.item_price, 'item_description': item.item_description} for item in current_items], 'total_cost': cost})
    return jsonify({'error': 'Item not found'}), 404

@app.route('/clear_order', methods=['POST'])
def clear_order():
    current_items.clear()
    return jsonify({'current_items': [], 'total_cost': '0.00'})


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

@app.route('/edit_grocery/<id>')
def edit_grocery(id):
    item = GroceryItem.query.filter_by(id=id).first()
    return render_template('groceries/add_custom_grocery.html', item=item)

@app.route('/confirm-edit-grocery', methods=['POST'])
def confirm_edit_grocery():
    old_grocery_name = request.form['old_grocery_name']
    grocery = GroceryItem.query.filter_by(grocery_name=old_grocery_name).first()
    if request.form['grocery_name'] == "" or request.form['grocery_description'] == "" or request.form['grocery_price'] == "":
        flash("Please fill out all fields!", category="error")
    grocery_price = request.form['grocery_price']
    grocery_price = grocery_price.replace("$", "").replace(",", "")
    grocery_price = "{:,.2f}".format(float(grocery_price))
    grocery.grocery_name = request.form['grocery_name']
    grocery.grocery_description = request.form['grocery_description']
    grocery.grocery_price = str(grocery_price)
    grocery.grocery_amount = request.form['grocery_amount']
    db.session.commit()
    # Removed unreachable code
@app.route('/review_item/<id>')
def review_item(id):
    item = Item.query.filter_by(id=id).first()
    item_ordered = ItemOrdered.query.all()
    #Get the item name, description, and price
    name = item.item_name
    description = item.item_description
    price = item.item_price
    #Get the yearly, monthly, weekly, and daily earnings for that specific item
    ye = 0
    me = 0
    we = 0
    de = 0

    amount_bought = 0
    for item_ordered in item_ordered:
        if item_ordered.item_name == name:
            if item_ordered.item_day == datetime.datetime.now().day:
                de += float(str(item_ordered.item_price).replace("$", "").replace(",", ""))
            if item_ordered.item_week == datetime.datetime.now().isocalendar()[1]:
                we += float(str(item_ordered.item_price).replace("$", "").replace(",", ""))
            if item_ordered.item_month == datetime.datetime.now().month:
                me += float(str(item_ordered.item_price).replace("$", "").replace(",", ""))
            if item_ordered.item_year == datetime.datetime.now().year:
                ye += float(str(item_ordered.item_price).replace("$", "").replace(",", ""))

            amount_bought += 1
    me = str('{:,.2f}'.format(me))
    de = str('{:,.2f}'.format(de))
    ye = str('{:,.2f}'.format(ye))
    we = str('{:,.2f}'.format(we))


    profit = amount_bought * float(str(price).replace("$", "").replace(",", ""))
    profit = '{:,.2f}'.format(profit)
    return render_template('review_item.html', name=name, description=description,
                           price=price, ye=ye, me=me, we=we, de=de, profit=profit, amount_bought=amount_bought)

@app.route('/cl2ear-admin')
def clear_admin():
    # Remove all the LogData items from the database
    LogData.query.delete()
    db.session.commit()


@app.route('/confirm-edit', methods=['POST'])
def confirm_edit():
    item_name = request.form.get('item_name')
    old_item_name = request.form.get('old_item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price').replace("$", "").replace(",", "")

    if item_price != "":

        item_price = '{:,.2f}'.format(float(item_price))
    else:
        flash("Cannot have an empty price! So we put it as $0.00", category="error")
        item_price = float("0.00")

    item = Item.query.filter_by(item_name=old_item_name).first()
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
def page_not_found(error):
    app.logger.error(f"Page not found: {error}")
    flash("Page not found!", category="error")
    return render_template("404.html"), 404


@app.route('/grocery_list')
def grocery_list():
    groceries = GroceryItem.query.all()
    total_price = 0.00
    for grocery in groceries:
        total_price += float(grocery.grocery_price.replace("$", "").replace(",", ""))

    total_price = "{:,.2f}".format(total_price)
    return render_template('groceries/grocery_list.html', groceries=groceries, total_price=total_price)

@app.route('/add_custom_grocery')
def add_custom_grocery():
    return render_template('groceries/add_custom_grocery.html')
@app.route('/add_grocery', methods=['POST'])
def add_grocery():
    grocery_name = request.form.get('grocery_name')
    grocery_description = request.form.get('grocery_description')
    grocery_amount = request.form.get('grocery_amount')

    try:
        if request.form.get('item_price') != "":
            grocery_price = str('{:,.2f}'.format(
                float(request.form.get('grocery_price').replace("$", ""))))
            grocery_description += " (Custom)"
            if grocery_name != "" or grocery_name != "":

                item = GroceryItem(grocery_name=grocery_name, grocery_description=grocery_description,
                            grocery_price=grocery_price, sams_name=grocery_name, grocery_amount=grocery_amount)

                db.session.add(item)
                db.session.commit()

                flash("Successfully added the item!")
                return redirect('/grocery_list')
            else:
                flash("Please fill in all the fields!", category="error")
                return redirect('/add_custom_grocery')
        else:
            flash("Make sure to fill in the price!", category="error")
            return redirect('/add_custom_grocery')
    except Exception as e:
        print(e.with_traceback(e.__traceback__))
        flash("Critical Error!", category="error")
        return redirect('/add_custom_grocery')


    return redirect('/grocery_list')

@app.route('/add_sams_grocery')
def add_sams_grocery():
    return render_template('groceries/add_sams_grocery.html', sams_list=sams_list)
def extract_price(text):
    # Use regular expression to find the price in the format $xx.xx
    match = re.search(r'\$\d+\.\d{2}', text)
    if match:
        return match.group()
    else:
        return None


def extract_quantity(text):
    # Use regular expression to find the quantity in the format xx pk, xx ct, or xx oz
    match_pk_ct = re.search(r'\b\d+\s(?:pk|ct|lbs|pcs|rolls|pks|pc)\b', text)
    match_oz = re.search(r'\b\d+\s(?:oz)\b', text)

    if match_pk_ct:
        return match_pk_ct.group()
    elif match_oz:
        return match_oz.group()
    else:
        return '0'
def extract_number(text):
    # Use regular expression to find numbers, including decimals
    match = re.search(r'\b\d+(\.\d+)?\b', text)
    if match:
        return match.group()
    else:
        return None
@app.route('/search_sams', methods=['GET', 'POST'])
def search_sams():
    #Delete all the files in static/images/groceries
    for f in os.listdir('static/images/groceries'):
        os.remove(os.path.join('static/images/groceries', f))
    #get item_name from post
    item_name = request.form.get('sams_name')
    sams_list = sams.full_scrape(item_name, download_image_check=True)
    for sams_lis in sams_list:
        print(sams_lis)
    sams_price = []
    sams_quantity = []
    sams_number = []

    sams_img_path = []
    if sams_list[0] == "No results":
        sams_list.clear()
        return render_template('groceries/add_sams_grocery.html', search_query=item_name, sams_list=sams_list,
                               sams_price=sams_price, sams_quantity=sams_quantity, sams_number=sams_number,sams_img_path=sams_img_path)

    for sams_item in sams_list:
        #Extract everything past the $
        price = extract_price(sams_item)
        if price == "$0.00":
            price = "Couldn't load, check sams website"
        sams_price.append(price)
        sams_quantity.append(extract_quantity(sams_item))
        sams_number.append(extract_number(sams_item))


        new_sams_item = sams_item.replace(extract_number(sams_item) + ". ", '')
        new_sams_item = new_sams_item.replace(extract_price(sams_item), '')
        new_title = new_sams_item.replace(" ", "").replace('.', '').replace("\"", '').replace("\\",'').replace('/','')
        new_sams_item = new_sams_item.replace(extract_quantity(sams_item), '')
        new_sams_item = new_sams_item.replace(".", '').replace(",", '')
        sams_list[sams_list.index(sams_item)] = new_sams_item



        sams_img_path.append("\static\images\groceries\\" + new_title + ".png")
        print(sams_img_path)
    time.sleep(2)
    return render_template('groceries/add_sams_grocery.html', search_query=item_name, sams_list=sams_list, sams_price=sams_price, sams_quantity=sams_quantity, sams_number=sams_number,
                           sams_img_path=sams_img_path)

@app.route("/add_sams/<int:item_id>/<string:item_name>")
def add_sams(item_id, item_name):
    info = sams.get_certain_order(item_name, item_id-1)
    quantity = extract_quantity(info[0])
    item_name = info[0]
    new_sams_item = item_name.replace(extract_number(item_name) + ". ", '')
    new_sams_item = new_sams_item.replace(extract_quantity(item_name), '')
    new_sams_item = new_sams_item.replace(".", '').replace(",", '')
    item = GroceryItem(grocery_name=new_sams_item, grocery_description="(Auto Generated)", grocery_price=info[1], sams_name=info[0], grocery_amount=quantity)

    db.session.add(item)
    db.session.commit()
    return redirect('/grocery_list')
@app.route('/remove_grocery/<int:item_id>')
def remove_grocery(item_id):
    item = GroceryItem.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/grocery_list')

@app.route('/duplicate_grocery/<int:item_id>')
def duplicate_grocery(item_id):
    item = GroceryItem.query.get(item_id)
    new_item = GroceryItem(grocery_name=item.grocery_name, grocery_description=item.grocery_description, grocery_price=item.grocery_price, grocery_amount=item.grocery_amount, sams_name=item.sams_name)
    db.session.add(new_item)
    db.session.commit()
    return redirect('/grocery_list')

@app.route("/admin-login", methods=['GET', 'POST'])
def admin_login():
    return render_template("admin_login.html")



@app.route('/admin')
def admin():
    if check_admin():
        return render_template('admin.html')
    else:
        return redirect("/admin-login")

def redirect_from_thread(url):
    return redirect(url)
@app.route('/database_backup')
def database_backup():
    upload_database_to_server()

    flash("Database backup finished!", category="success")
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


# @app.route("/clear_order")
# def clear_order():
#     current_items.clear()
#     return redirect("/order")


# @app.route('/add_order/<id>')
# def add_order(id):
#     item = Item.query.filter_by(id=id).first()

#     current_items.append(item)
#     return redirect('/order')


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

        tendered = tendered.replace("$", "").replace(",", "")
        tendered = float(tendered.replace(",", ""))

        cost = 0
        for item in current_items:
            cost += float(item.item_price.replace("$", ""))

        change = tendered - cost

        cost = '{:,.2f}'.format(cost)
        o_tendered = str(tendered)
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
                item_ordered = ItemOrdered(item_price=item.item_price, item_day=datetime.datetime.now().day,
                                           item_month=datetime.datetime.now().month,
                                           item_year=datetime.datetime.now().year,
                                           item_week=datetime.datetime.now().isocalendar()[1],
                                           item_name=item.item_name)
                db.session.add(item_ordered)
                db.session.commit()
            return render_template("confirm_tender.html", change=change, tendered=o_tendered, total=str(cost))
    except Exception as e:
        print(e.with_traceback(e.__traceback__))
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


@app.route("/items_profit")
def items_profit():
    items = ItemOrdered.query.all()
    #Sort all the items by amount bought, you would do this by going through every item bought and then counting how many times it was bought
    items_profit = {}
    for item in items:
        if item.item_name not in items_profit:
            items_profit[item.item_name] = float(item.item_price)
        else:
            items_profit[item.item_name] += float(item.item_price)

    for item in items_profit:
        items_profit[item] = float('{:,.2f}'.format(items_profit[item]))
    items_profit = sorted(items_profit.items(), key=lambda x: x[1], reverse=True)


    if check_admin():
        return render_template("items_profit.html", items=items_profit)
    else:
        return redirect("/admin-login")


@app.route("/items_profit_reverse")
def items_profit_reverse():
    items = ItemOrdered.query.all()
    #Sort all the items by amount bought, you would do this by going through every item bought and then counting how many times it was bought
    items_profit = {}
    for item in items:
        if item.item_name not in items_profit:
            items_profit[item.item_name] = float(item.item_price)
        else:
            items_profit[item.item_name] += float(item.item_price)

    items_profit = sorted(items_profit.items(), key=lambda x: x[1], reverse=False)
    if check_admin():
        return render_template("items_profit_reverse.html", items=items_profit)
    else:
        return redirect("/admin-login")


@app.route("/items_ordered")
def items_ordered():
    items = ItemOrdered.query.all()
    #Sort all the items by amount bought, you would do this by going through every item bought and then counting how many times it was bought
    items_bought = {}
    for item in items:
        if item.item_name not in items_bought:
            items_bought[item.item_name] = 1
        else:
            items_bought[item.item_name] += 1

    items_sorted_by_amount_bought = sorted(items_bought.items(), key=lambda x: x[1], reverse=True)

    if check_admin():
        return render_template("items_ordered.html", items=items_sorted_by_amount_bought)
    else:
        return redirect("/admin-login")


@app.route("/items_ordered_reverse")
def items_ordered_reverse():
    items = ItemOrdered.query.all()
    #Sort all the items by amount bought, you would do this by going through every item bought and then counting how many times it was bought
    items_bought = {}
    for item in items:
        if item.item_name not in items_bought:
            items_bought[item.item_name] = 1
        else:
            items_bought[item.item_name] += 1

    items_sorted_by_amount_bought = sorted(items_bought.items(), key=lambda x: x[1])

    if check_admin():
        return render_template("items_ordered_reverse.html", items=items_sorted_by_amount_bought)
    else:
        return redirect("/admin-login")


@app.route('/admin_earnings')
def admin_earnings():
    monthly_earnings = 0
    daily_earnings = 0
    yearly_earings = 0
    weekly_earnings = 0

    items_bought = []
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

        items_bought.append(item.item_name)

    #Find the one that sold the most by counting the amount of times it was in the list
    most_bought_name = max(items_bought, key=items_bought.count)
    most_bought = items_bought.count(most_bought_name)

    #Find the one that sold the least by counting the amount of times it was in the list
    least_bought_name = min(items_bought, key=items_bought.count)
    least_bought = items_bought.count(least_bought_name)

    most_bought_profit = 0
    least_bought_profit = 0
    for item in items:
        if item.item_name == most_bought_name:
            most_bought_profit += float(item.item_price)
        if item.item_name == least_bought_name:
            least_bought_profit += float(item.item_price)

    # Make all the earnings into formatted money strings
    monthly_earnings = str('{:,.2f}'.format(monthly_earnings))
    daily_earnings = str('{:,.2f}'.format(daily_earnings))
    yearly_earings = str('{:,.2f}'.format(yearly_earings))
    weekly_earnings = str('{:,.2f}'.format(weekly_earnings))

    most_bought_profit = str('{:,.2f}'.format(most_bought_profit))
    least_bought_profit = str('{:,.2f}'.format(least_bought_profit))
    if check_admin():
        return render_template("admin_earnings.html", me=monthly_earnings, de=daily_earnings, ye=yearly_earings,
                               we=weekly_earnings,
                               best_item=most_bought_name, best_amount=most_bought, best_profit=most_bought_profit,
                               worst_item=least_bought_name, worst_amount=least_bought,
                               worst_profit=least_bought_profit)
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

    
@app.route("/weekly_overview")
def weekly_overview():

    #Make a weekly overview, by seeing what the diffrence is from the last week
    #Get the current week
    current_week = datetime.datetime.now().isocalendar()[1]
    current_year = datetime.datetime.now().year
    #Get the last week
    last_week = current_week - 1
    last_year = current_year
    
    #Get all the items bought
    items = ItemOrdered.query.all()
    last_week_items = []
    current_week_items = []
    for item in items:
        if item.item_week == last_week and item.item_year == last_year:
            last_week_items.append(item)
        if item.item_week == current_week and item.item_year == current_year:
            current_week_items.append(item)
    last_week_earnings = 0
    current_week_earnings = 0
    for item in last_week_items:
        last_week_earnings += float(item.item_price)
    for item in current_week_items:
        current_week_earnings += float(item.item_price)
        
    earnings_diffrence = current_week_earnings - last_week_earnings
    if abs(earnings_diffrence) == earnings_diffrence:
        positive = True
    else:
        positive = False
    last_week_earnings = '{:,.2f}'.format(last_week_earnings)
    current_week_earnings = '{:,.2f}'.format(current_week_earnings)
    
    earnings_diffrence = '{:,.2f}'.format(earnings_diffrence)
    
    
    #Now get most popular item for last week and current week
    last_week_items_bought = []
    current_week_items_bought = []
    for item in last_week_items:
        last_week_items_bought.append(item.item_name)
    for item in current_week_items:
        current_week_items_bought.append(item.item_name)
    most_popular_last_week = max(last_week_items_bought, key=last_week_items_bought.count)
    most_popular_current_week = max(current_week_items_bought, key=current_week_items_bought.count)
    most_popular_last_week_amount = last_week_items_bought.count(most_popular_last_week)
    most_popular_current_week_amount = current_week_items_bought.count(most_popular_current_week)
    most_popular_last_week_profit = 0
    most_popular_current_week_profit = 0
    for item in last_week_items:
        if item.item_name == most_popular_last_week:
            most_popular_last_week_profit += float(item.item_price)
    for item in current_week_items:
        if item.item_name == most_popular_current_week:
            most_popular_current_week_profit += float(item.item_price)
    most_popular_last_week_profit = '{:,.2f}'.format(most_popular_last_week_profit)
    most_popular_current_week_profit = '{:,.2f}'.format(most_popular_current_week_profit)
    
    #Worst items
    least_popular_last_week = min(last_week_items_bought, key=last_week_items_bought.count)
    least_popular_current_week = min(current_week_items_bought, key=current_week_items_bought.count)
    least_popular_last_week_amount = last_week_items_bought.count(least_popular_last_week)
    least_popular_current_week_amount = current_week_items_bought.count(least_popular_current_week)
    least_popular_last_week_profit = 0
    least_popular_current_week_profit = 0
    for item in last_week_items:
        if item.item_name == least_popular_last_week:
            least_popular_last_week_profit += float(item.item_price)
    for item in current_week_items:
        if item.item_name == least_popular_current_week:
            least_popular_current_week_profit += float(item.item_price)
    least_popular_last_week_profit = '{:,.2f}'.format(least_popular_last_week_profit)
    least_popular_current_week_profit = '{:,.2f}'.format(least_popular_current_week_profit)
    
    if check_admin():
        return render_template("weekly_overview.html", last_week_earnings=last_week_earnings, current_week_earnings=current_week_earnings, earnings_diffrence=earnings_diffrence, positive=positive,
                               most_popular_last_week=most_popular_last_week, most_popular_current_week=most_popular_current_week, most_popular_last_week_amount=most_popular_last_week_amount, most_popular_current_week_amount=most_popular_current_week_amount,
                               most_popular_last_week_profit=most_popular_last_week_profit, most_popular_current_week_profit=most_popular_current_week_profit,
                               least_popular_last_week=least_popular_last_week, least_popular_current_week=least_popular_current_week, least_popular_last_week_amount=least_popular_last_week_amount, least_popular_current_week_amount=least_popular_current_week_amount,
                               least_popular_last_week_profit=least_popular_last_week_profit, least_popular_current_week_profit=least_popular_current_week_profit)
    else:
        return redirect("/admin-login")
    


if __name__ == '__main__':
    
    create_database(app)
    app.run(host="0.0.0.0", port=8761)

# pyinstaller -F --add-data "templates;templates" --add-data "static;static" --name BlueBrewCompanion main.py
