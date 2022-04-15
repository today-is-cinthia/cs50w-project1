
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
import json

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
            flash("Username already exists. Try again")
            return render_template("register.html")

        flash('Welcome to Search Books!')
        return redirect("/")

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
            flash('Invalid username and/or password')
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]
        flash('Welcome to Search Books!')
        return redirect("/")
    else:
        return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def salir():
    session.clear()
    flash('You succesfully logged out')
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
        if not busqueda:
            flash('No matches found')
        return render_template("search.html", busqueda=busqueda)
    else:
        return render_template("search.html")


@app.route("/libros/<isbn>",methods=['GET','POST'])
def libros(isbn):
    if request.method == "POST":
        rating = int(request.form.get("rating"))
        comentario = request.form.get("comentario")

        query = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if query is not None:
            query = query[0]

        validate = db.execute("SELECT * FROM reviews WHERE \
        id_user = :id_user AND id_book = :id_book", {"id_user": session["user_id"], "id_book": query})
        if validate.rowcount == 1:
            flash('You can only publish one review per book')
        else:
        
            db.execute("INSERT INTO reviews (comentario, rating, id_book, id_user) VALUES (:comentario, :rating, :id_book, :id)",
            { "comentario": comentario, "rating": rating, "id_book": query, "id": session["user_id"]})
            db.commit()
        return redirect("/libros/" + isbn)
  
    if request.method == "GET":
        resultado = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn", {"isbn":isbn})
        resultado = resultado.fetchall()

        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()

        formato = response['items'][0]
        count = formato['volumeInfo']['ratingsCount']
        rating = formato['volumeInfo']['averageRating']

        resultado.append(formato)
        query = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if query is not None:
            query = query[0]

        ayuda = db.execute("SELECT users.usuario, comentario, rating FROM users \
         INNER JOIN reviews ON users.id = reviews.id_user WHERE id_book = :id_book", {"id_book": query})
        ya_duermanme_como_a_los_perritos = ayuda.fetchall()
    return render_template("libros.html", resultados=resultado, ayudas = ya_duermanme_como_a_los_perritos, count = count, rating = rating, isbn=isbn)

@app.route("/api/<isbn>",methods=['GET','POST'])
def api(isbn):
    a = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    if a == None:
        return jsonify({"Error": "invalid/incorrect isbn"})
    
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn)

    if response.status_code != 200:
        raise Exception("Failed to request api")
    
    response = response.json()
    formato = response['items'][0]
    count = formato['volumeInfo']['ratingsCount']
    rating = formato['volumeInfo']['averageRating']

    return jsonify({
        "title": a.title,
        "author": a.author,
        "year": a.year,
        "isbn": a.isbn,
        "rating_count": count,
        "average_rating": rating 
    })


