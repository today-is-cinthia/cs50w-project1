
#from crypt import methods
import os
from turtle import title

from flask import Flask, session, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from loginrequired import login_required
import requests

app = Flask(__name__)

#Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if confirmation != password:
            flash("passwords dont match")
            return render_template("register.html")

        rows = db.execute(
            "SELECT usuario FROM users WHERE usuario=:username", {"username": user}).fetchall()

        if not rows:
            db.execute("INSERT INTO users (usuario, contraseña) VALUES (:username, :password)",
                       {"username": user, "password": generate_password_hash(password)})
            db.commit()
        elif rows:
            flash("username already exists")
            return render_template("register.html")

        return redirect("/search")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()

    if request.method == "POST":
        rows = db.execute(
            "SELECT * FROM users WHERE usuario = :usuario",
                          {"usuario": request.form.get("username")}).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["contraseña"], request.form.get("password")):
            flash('invalid username and/or password')
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]

        return redirect("/search")
    else:
        return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def salir():
    session.clear()
    return redirect("/")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        search= request.form.get("search").capitalize()
        search = ("%"+ search +"%")
        busqueda = db.execute(
            "SELECT * FROM books WHERE isbn LIKE :search OR title LIKE :search OR author LIKE :search OR year LIKE :search", 
            {"search":search}).fetchall()
        return render_template("search.html", busqueda=busqueda)
    else:
        return render_template("search.html")


@app.route("/libros/<isbn>",methods=['GET','POST'])
def libros(isbn):
    book_id = request.form.get('book_id')
    global goodreads
    global count
    global rating

    if request.method == "POST":
        count = 0
        rating = request.form.get("rating")
        comentario = request.form.get("comentario")
        #if rating or comentario == "":
            #return render_template("error.html")
        db.execute("INSERT INTO reviews (usuario, comentario, rating, id_book) VALUES (:usuario, :comentario, :rating, :id_book)", {"usuario": session["user_id"], "comentario": comentario, "rating": rating, "id_book": book_id})
        db.commit()
            
    resultado = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchall()

    if resultado is None:
        return render_template("libros.html")
    
    reviews = db.execute("SELECT * FROM reviews WHERE id_book = :id;",{"id":book_id}).fetchall()
    if request.method == "GET":
        try:
            validation = db.execute("SELECT usuario FROM reviews WHERE id_book = :id AND usuario = :usuario", {"id": book_id, "usuario": session["user_id"]}).fetchone()
            if validation != None:
                return render_template("error.html")
        except:
            pass
        if "AIzaSyCPNyAngETN9xr7U7XAU_gDALxG3Tttbi4":
            response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"access_key":'AIzaSyCPNyAngETN9xr7U7XAU_gDALxG3Tttbi4', "isbns": isbn})
            if response.status_code != 200:
                raise Exception("Request to goodreads was unsuccessful")
            goodreads = response.json().get('books')[0]
            count = goodreads.get('work_ratings_count')
            rating = goodreads.get('average_rating')
    return render_template("libros.html", resultado=resultado, count=count, rating=rating, reviews=reviews)

