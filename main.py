from flask import Flask, render_template, request, flash, redirect,abort
from flask_login import LoginManager, login_user,login_required,logout_user

import pymysql

from dynaconf import Dynaconf
import pymysql.cursors

app = Flask(__name__)

config = Dynaconf(settings_file= ["settings.toml"])

app.secret_key = config.secret_key

login_manager = LoginManager(app)

login_manager.login_view = '/login'


class User:
    is_authenticated = True
    is_active = True
    is_anonymous = False
    def  __init__(self,result):
        self.name = result['Name']
        self.email = result['Email']
        self.id = result['ID']
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `User` WHERE `ID` = %s",(user_id))
    result = cursor.fetchone()
    
    connection.close()
    
    if result is None:
        return None
    return User(result)

def connect_db():
    conn = pymysql.connect(
        host="db.steamcenter.tech",
        user="jeubanks",
        password=config.password,
        database="jeubanks_Predict_Understand_Sources",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

@app.route("/")
def index():
    return render_template("homepage.html.jinja")

@app.route("/browse")
def browse():
    connection = connect_db()
    
    cursor = connection.cursor()
    
    cursor.execute("SELECT * From `Product`")

    result = cursor.fetchall()

    connection.close()
    
    return render_template("browse.html.jinja", products=result)

@app.route("/product/<product_id>")
def product_page(product_id):
    connection = connect_db()
    
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM `Product` WHERE `ID` = %s", (product_id))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        abort(404)
    
    return render_template("product.html.jinja", product=result)

@app.route("/login", methods = ["POST" ,"GET"])
def login():
  if request.method== 'Post':
      email = request.form['email']
      password = request.form['password']
     
      connection = connect_db()

    
      cursor = connection.cursor()

      cursor.execute(" SELECT * FROM `User` WHERE `Email` = %s", (email))
      result = cursor.fetchone

      print(result)

      connection.close()

      if result is None:
          flash("No user found")
      elif password != result["password"]:
          flash("Incorrect password")
      else:
          login_user(User(result))
          return redirect('/browse')

     
  return render_template("login.html.jinja",)

@app.route("/register", methods =['POST', 'GET'])
def register():
       if request.method == 'POST':
           name = request.form["name"]
           email = request.form["email"]
           password = request.form["password"]
           confrim_password = request.form["confirm_password"]

           if password != confrim_password:
               flash("Password does not match")
           elif len (password) < 5:
               flash("Password is too short")
           else:
            connection = connect_db()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO `User` ( `Name`, `Password`, `Email`)
                    VALUES(%s, %s, %s)
                    """,(name, password, email))
            except pymysql.err.IntegrityError:
                flash("email already exists")
            else:
                return redirect ("/login")

       

       return render_template("register.html.jinja")


@app.route("/logout", methods= ["POST", "GET"])
@login_required
def logout():
       logout_user()
       return redirect("/")
