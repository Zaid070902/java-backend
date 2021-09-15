# imports

import hmac
import sqlite3
from datetime import timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
# from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail, Message


class User(object):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


class Product(object):
    def __init__(self, prod_name, prod_price, amount):
        self.prod_name = prod_name
        self.prod_price = prod_price
        self.amount = amount

# creating user table


def user_table():
    conn = sqlite3.connect('blog.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


user_table()

# fetching users from table


def fetch_users():
    with sqlite3.connect('blog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4], data[5]))
    return new_data


users = fetch_users()

# product table


def post_table():
    with sqlite3.connect('blog.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "prod_name TEXT NOT NULL,"
                     "prod_price INTEGER NOT NULL,"
                     "amount INTEGER NOT NULL)")
    print("blog table created successfully.")


post_table()

# fetching product from table


def fetch_users():
    with sqlite3.connect('blog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()

        new_data = []

        for data in products:
            new_data.append(Product(data[0], data[1], data[2]))
    return new_data


products = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# def authenticate(username, password):
#     user = username_table.get(username, None)
#     if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
#         return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)

CORS(app)

app.debug = True
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)
app.config['SECRET_KEY'] = 'super-secret'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'zaidflandorp4@gmail.com'
app.config['MAIL_PASSWORD'] = 'xxxtentacion_17'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# jwt = JWT(app, authenticate, identity)


# @app.route('/protected')
# # @jwt_required()
# def protected():
#     return '%s' % current_identity

# register route


@app.route('/registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        with sqlite3.connect("blog.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password,"
                           "email) VALUES(?, ?, ?, ?, ?)", (first_name, last_name, username, password, email))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

        msg = Message('Hello Message', sender='zaidflandorp4@gamil.com', recipients=[email])
        msg.body = "My email using Flask"
        mail.send(msg)
        return "Message send"
    return response

# adding products route


@app.route('/create-blog/', methods=["POST"])
# @jwt_required()
def create_blog():
    response = {}

    if request.method == "POST":
        prod_name = request.json['prod_name']
        prod_price = request.json['prod_price']
        amount = request.json['amount']

        with sqlite3.connect('blog.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product("
                           "prod_name,"
                           "prod_price,"
                           "amount) VALUES(?, ?, ?)", (prod_name, prod_price, amount))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Blog post added successfully"
        return response

# fetching users route


@app.route('/get-user/', methods=["GET"])
def get_users():
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response

# fetching products route


@app.route('/get-blogs/', methods=["GET"])
def get_blogs():
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return jsonify(response)

# delete products route


@app.route("/delete-post/<int:id>")
# @jwt_required()
def delete_post(id):
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "blog post deleted successfully."
        return response


@app.route('/edit-post/<int:id>/', methods=["PUT"])
# @jwt_required()
def edit_post(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('blog.db') as conn:
            prod_name = request.form['prod_name']
            prod_price = request.form['prod_price']
            amount = request.form['amount']
            put_data = {}

            if prod_name is not None:
                put_data["prod_name"] = prod_name
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET prod_name =? WHERE id=?", (put_data["prod_name"], id))
                conn.commit()
                response['message'] = "Update was successfully"
                response['status_code'] = 200
            if prod_price is not None:
                put_data['prod_price'] = prod_price
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET prod_price =? WHERE id=?", (put_data["prod_price"], id))
                conn.commit()
                response["prod_price"] = "Content updated successfully"
                response["status_code"] = 200
            if amount is not None:
                put_data['amount'] = amount
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET amount =? WHERE id=?", (put_data["amount"], id))
                conn.commit()
                response["amount"] = "Content updated successfully"
                response["status_code"] = 200
    return response


@app.route('/get-post/<int:post_id>/', methods=["GET"])
def get_post(id):
    response = {}

    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=" + str(id))

        response["status_code"] = 200
        response["description"] = "Blog post retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
